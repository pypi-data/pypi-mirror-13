import json
import logging
import os
import sys
import socket

import six
import semantic_version

from lymph.exceptions import RegistrationFailure, SocketNotCreated, NoSharedSockets, ConfigurationError
from lymph.core.components import Componentized
from lymph.core.events import Event
from lymph.core.monitoring import metrics
from lymph.core.monitoring.pusher import MonitorPusher
from lymph.core.monitoring.aggregator import Aggregator
from lymph.core.services import ServiceInstance, Service
from lymph.core.rpc import ZmqRPCServer
from lymph.core.interfaces import DefaultInterface
from lymph.core.plugins import Hook
from lymph.core import trace
from lymph.core.versioning import get_lymph_version, serialize_version
from lymph.utils import hash_id


logger = logging.getLogger(__name__)


def create_container(config, **kwargs):
    if 'registry' in config:
        logger.warning('global `registry` configuration is deprecated. '
                       'Please use `container` and define a `registry` entry '
                       'inside `container` instead.')
        config.set('container.registry', config.get_raw('registry'))

    if 'event_system' in config:
        logger.warning('global `event_system` configuration is deprecated. '
                       'Please use `container` and define an `events` '
                       'entry inside `container` instead.')
        config.set('container.events', config.get_raw('event_system'))

    container = config.create_instance(
        'container',
        default_class='lymph.core.container:ServiceContainer',
        events=config.create_instance('container.events'),
        **kwargs
    )
    return container


class InterfaceSkipped(Exception):
    pass


class InterfaceVersions(object):
    def __init__(self):
        self.versions = {}
        self.latest = None

    def add(self, interface):
        if interface.version in self.versions:
            raise ConfigurationError("Duplicate interface `%s`" % interface)
        if interface.version:
            if not self.latest or interface.version > self.latest.version:
                self.latest = interface
        self.versions[interface.version] = interface

    def __iter__(self):
        return six.itervalues(self.versions)

    def __str__(self):
        return ', '.join(str(v) for v in self.versions.keys())

    def __getitem__(self, version):
        try:
            return self.versions[version]
        except KeyError:
            if not version:
                return self.latest
            raise


class ServiceContainer(Componentized):
    def __init__(self, rpc=None, registry=None, events=None, log_endpoint=None, service_name=None, debug=False, pool=None, worker=False, metrics=None):
        if pool is None:
            pool = trace.Group()
        if metrics is None:
            metrics = Aggregator()
        super(ServiceContainer, self).__init__(error_hook=Hook('error_hook'), pool=pool, metrics=metrics)
        self.log_endpoint = log_endpoint
        self.backdoor_endpoint = None
        self.service_name = service_name
        self.fqdn = socket.getfqdn()
        self.worker = worker

        self.http_request_hook = Hook('http_request_hook')

        self.server = rpc
        self.service_registry = registry
        self.events = events

        self.installed_interfaces = {}
        self.installed_plugins = []

        self.debug = debug

        self.metrics.add_tags(service=self.service_name, host=self.fqdn)
        self.monitor = self.install(MonitorPusher, aggregator=self.metrics, endpoint=rpc.ip, interval=5)

        if self.service_registry:
            self.add_component(self.service_registry)

        if self.events:
            self.add_component(self.events)
            self.events.install(self)

        self.add_component(rpc)
        rpc.request_handler = self.handle_request

        self.install_interface(DefaultInterface, name='lymph', builtin=True, version=get_lymph_version())

    @classmethod
    def from_config(cls, config, **explicit_kwargs):
        kwargs = dict(config)
        kwargs.pop('class', None)
        kwargs.setdefault('service_name', os.environ.get('LYMPH_SERVICE_NAME', config.root.get('name')))
        kwargs['registry'] = config.create_instance('registry')

        kwargs['rpc'] = config.create_instance('rpc', default_class=ZmqRPCServer, ip=kwargs.pop('ip', None), port=kwargs.pop('port', None))
        kwargs['pool'] = config.create_instance('pool', default_class='lymph.core.trace:Group')
        kwargs['metrics'] = config.create_instance('metrics', default_class=Aggregator)

        for key, value in six.iteritems(explicit_kwargs):
            if value is not None:
                kwargs[key] = value
        return cls(**kwargs)

    def excepthook(self, type, value, traceback):
        logger.log(logging.CRITICAL, 'Uncaught exception', exc_info=(type, value, traceback))
        self.error_hook((type, value, traceback))

    @property
    def endpoint(self):
        return self.server.endpoint

    @property
    def identity(self):
        return hash_id(self.endpoint)

    def install_interface(self, cls, **kwargs):
        interface = cls(self, **kwargs)
        if not interface.should_install():
            raise InterfaceSkipped('not a worker interface')
        self.add_component(interface)
        versions = self.installed_interfaces.setdefault(interface.name, InterfaceVersions())
        versions.add(interface)
        for plugin in self.installed_plugins:
            plugin.on_interface_installation(interface)
        return interface

    def install_plugin(self, cls, **kwargs):
        logger.info('installing plugin %s:%s', cls.__module__, cls.__name__)
        plugin = self.install(cls, **kwargs)
        self.installed_plugins.append(plugin)
        return plugin

    def get_shared_socket_fd(self, port):
        try:
            fds = os.environ['LYMPH_SHARED_SOCKET_FDS']
        except KeyError:
            raise NoSharedSockets()
        fds = json.loads(fds)
        try:
            return fds[str(port)]
        except KeyError:
            raise SocketNotCreated()

    def iter_interfaces(self):
        for interfaces in six.itervalues(self.installed_interfaces):
            for interface in interfaces:
                yield interface

    @property
    def service_types(self):
        for interface in self.iter_interfaces():
            yield str(interface)

    def subscribe(self, handler, **kwargs):
        return self.events.subscribe(handler, **kwargs)

    def unsubscribe(self, handler):
        self.events.unsubscribe(handler)

    def get_instance_description(self, interface):
        description = interface.get_description()
        description.update({
            'id': interface.id,
            'endpoint': self.endpoint,
            'identity': self.identity,
            'log_endpoint': self.log_endpoint,
            'monitoring_endpoint': self.monitor.endpoint,
            'backdoor_endpoint': self.backdoor_endpoint,
            'fqdn': self.fqdn,
            'hostname': socket.gethostname(),
            'ip': self.server.ip,
            'type': self.worker,
            'version': serialize_version(interface.version),
        })
        return description

    def start(self, register=True):
        logger.info('starting %s (%s)', self.service_name, ', '.join(self.service_types))
        if all(i.builtin for i in self.iter_interfaces()):
            logger.warning('only builtin interfaces installed')

        self.on_start()
        self.metrics.add_tags(identity=self.identity)
        if register:
            self.register()
        self.metrics.add(metrics.Callable('greenlets.count', lambda: len(self.pool)))

    def register(self):
        for interface in self.iter_interfaces():
            if not interface.should_register():
                continue
            instance = ServiceInstance(**self.get_instance_description(interface))
            try:
                self.service_registry.register(interface.name, instance)
            except RegistrationFailure:
                logger.error("registration failed %s, %s", interface.name, interface)
                self.stop()

    def stop(self, **kwargs):
        self.on_stop()
        self.pool.kill()

    def join(self):
        self.pool.join()

    def lookup(self, address, version=None):
        if '://' not in address:
            service = self.service_registry.get(address)
        else:
            instance = ServiceInstance(address)
            service = Service(address, instances=[instance])
        if version:
            service = service.match_version(version)
        return service

    def discover(self):
        return self.service_registry.discover()

    def emit_event(self, event_type, payload, headers=None, **kwargs):
        headers = headers or {}
        headers.setdefault('trace_id', trace.get_id())
        event = Event(event_type, payload, source=self.identity, headers=headers)
        self.events.emit(event, **kwargs)

    def send_request(self, address, subject, body, headers=None, version=None):
        service = self.lookup(address, version=version)
        return self.server.send_request(service, subject, body, headers=headers)

    def handle_request(self, channel):
        interface_name, func_name = channel.request.subject.rsplit('.', 1)
        version = channel.request.version
        if version:
            version = semantic_version.Version(version)
        try:
            versions = self.installed_interfaces[interface_name]
        except KeyError:
            logger.warning('Unsupported interface: %s', interface_name)
            channel.nack(True)
            return
        try:
            interface = versions[version]
        except KeyError:
            logger.warning('Unsupported version: %s@%s', interface_name, version)
            channel.nack(True)
            return
        try:
            interface.handle_request(func_name, channel)
        except Exception:
            logger.exception('Request error:')
            exc_info = sys.exc_info()
            try:
                self.error_hook(exc_info, extra={
                    'service': self.service_name,
                    'interface': interface_name,
                    'func_name': func_name,
                    'trace_id': trace.get_id(),
                })
            finally:
                del exc_info
            try:
                channel.nack(True)
            except:
                logger.exception('failed to send automatic NACK')
