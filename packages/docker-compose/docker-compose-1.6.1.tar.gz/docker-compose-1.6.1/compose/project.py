from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import logging
from functools import reduce

from docker.errors import APIError

from . import parallel
from .config import ConfigurationError
from .config.config import V1
from .config.sort_services import get_container_name_from_network_mode
from .config.sort_services import get_service_name_from_network_mode
from .const import DEFAULT_TIMEOUT
from .const import IMAGE_EVENTS
from .const import LABEL_ONE_OFF
from .const import LABEL_PROJECT
from .const import LABEL_SERVICE
from .container import Container
from .network import build_networks
from .network import get_networks
from .network import ProjectNetworks
from .service import ContainerNetworkMode
from .service import ConvergenceStrategy
from .service import NetworkMode
from .service import Service
from .service import ServiceNetworkMode
from .utils import microseconds_from_time_nano
from .volume import ProjectVolumes


log = logging.getLogger(__name__)


class Project(object):
    """
    A collection of services.
    """
    def __init__(self, name, services, client, networks=None, volumes=None):
        self.name = name
        self.services = services
        self.client = client
        self.volumes = volumes or ProjectVolumes({})
        self.networks = networks or ProjectNetworks({}, False)

    def labels(self, one_off=False):
        return [
            '{0}={1}'.format(LABEL_PROJECT, self.name),
            '{0}={1}'.format(LABEL_ONE_OFF, "True" if one_off else "False"),
        ]

    @classmethod
    def from_config(cls, name, config_data, client):
        """
        Construct a Project from a config.Config object.
        """
        use_networking = (config_data.version and config_data.version != V1)
        networks = build_networks(name, config_data, client)
        project_networks = ProjectNetworks.from_services(
            config_data.services,
            networks,
            use_networking)
        volumes = ProjectVolumes.from_config(name, config_data, client)
        project = cls(name, [], client, project_networks, volumes)

        for service_dict in config_data.services:
            service_dict = dict(service_dict)
            if use_networking:
                service_networks = get_networks(service_dict, networks)
            else:
                service_networks = {}

            service_dict.pop('networks', None)
            links = project.get_links(service_dict)
            network_mode = project.get_network_mode(
                service_dict, list(service_networks.keys())
            )
            volumes_from = get_volumes_from(project, service_dict)

            if config_data.version != V1:
                service_dict['volumes'] = [
                    volumes.namespace_spec(volume_spec)
                    for volume_spec in service_dict.get('volumes', [])
                ]

            project.services.append(
                Service(
                    service_dict.pop('name'),
                    client=client,
                    project=name,
                    use_networking=use_networking,
                    networks=service_networks,
                    links=links,
                    network_mode=network_mode,
                    volumes_from=volumes_from,
                    **service_dict)
            )

        return project

    @property
    def service_names(self):
        return [service.name for service in self.services]

    def get_service(self, name):
        """
        Retrieve a service by name. Raises NoSuchService
        if the named service does not exist.
        """
        for service in self.services:
            if service.name == name:
                return service

        raise NoSuchService(name)

    def validate_service_names(self, service_names):
        """
        Validate that the given list of service names only contains valid
        services. Raises NoSuchService if one of the names is invalid.
        """
        valid_names = self.service_names
        for name in service_names:
            if name not in valid_names:
                raise NoSuchService(name)

    def get_services(self, service_names=None, include_deps=False):
        """
        Returns a list of this project's services filtered
        by the provided list of names, or all services if service_names is None
        or [].

        If include_deps is specified, returns a list including the dependencies for
        service_names, in order of dependency.

        Preserves the original order of self.services where possible,
        reordering as needed to resolve dependencies.

        Raises NoSuchService if any of the named services do not exist.
        """
        if service_names is None or len(service_names) == 0:
            service_names = self.service_names

        unsorted = [self.get_service(name) for name in service_names]
        services = [s for s in self.services if s in unsorted]

        if include_deps:
            services = reduce(self._inject_deps, services, [])

        uniques = []
        [uniques.append(s) for s in services if s not in uniques]

        return uniques

    def get_services_without_duplicate(self, service_names=None, include_deps=False):
        services = self.get_services(service_names, include_deps)
        for service in services:
            service.remove_duplicate_containers()
        return services

    def get_links(self, service_dict):
        links = []
        if 'links' in service_dict:
            for link in service_dict.get('links', []):
                if ':' in link:
                    service_name, link_name = link.split(':', 1)
                else:
                    service_name, link_name = link, None
                try:
                    links.append((self.get_service(service_name), link_name))
                except NoSuchService:
                    raise ConfigurationError(
                        'Service "%s" has a link to service "%s" which does not '
                        'exist.' % (service_dict['name'], service_name))
            del service_dict['links']
        return links

    def get_network_mode(self, service_dict, networks):
        network_mode = service_dict.pop('network_mode', None)
        if not network_mode:
            if self.networks.use_networking:
                return NetworkMode(networks[0]) if networks else NetworkMode('none')
            return NetworkMode(None)

        service_name = get_service_name_from_network_mode(network_mode)
        if service_name:
            return ServiceNetworkMode(self.get_service(service_name))

        container_name = get_container_name_from_network_mode(network_mode)
        if container_name:
            try:
                return ContainerNetworkMode(Container.from_id(self.client, container_name))
            except APIError:
                raise ConfigurationError(
                    "Service '{name}' uses the network stack of container '{dep}' which "
                    "does not exist.".format(name=service_dict['name'], dep=container_name))

        return NetworkMode(network_mode)

    def start(self, service_names=None, **options):
        containers = []
        for service in self.get_services(service_names):
            service_containers = service.start(**options)
            containers.extend(service_containers)
        return containers

    def stop(self, service_names=None, **options):
        parallel.parallel_stop(self.containers(service_names), options)

    def pause(self, service_names=None, **options):
        containers = self.containers(service_names)
        parallel.parallel_pause(reversed(containers), options)
        return containers

    def unpause(self, service_names=None, **options):
        containers = self.containers(service_names)
        parallel.parallel_unpause(containers, options)
        return containers

    def kill(self, service_names=None, **options):
        parallel.parallel_kill(self.containers(service_names), options)

    def remove_stopped(self, service_names=None, **options):
        parallel.parallel_remove(self.containers(service_names, stopped=True), options)

    def down(self, remove_image_type, include_volumes):
        self.stop()
        self.remove_stopped(v=include_volumes)
        self.networks.remove()

        if include_volumes:
            self.volumes.remove()

        self.remove_images(remove_image_type)

    def remove_images(self, remove_image_type):
        for service in self.get_services():
            service.remove_image(remove_image_type)

    def restart(self, service_names=None, **options):
        containers = self.containers(service_names, stopped=True)
        parallel.parallel_restart(containers, options)
        return containers

    def build(self, service_names=None, no_cache=False, pull=False, force_rm=False):
        for service in self.get_services(service_names):
            if service.can_be_built():
                service.build(no_cache, pull, force_rm)
            else:
                log.info('%s uses an image, skipping' % service.name)

    def create(self, service_names=None, strategy=ConvergenceStrategy.changed, do_build=True):
        services = self.get_services_without_duplicate(service_names, include_deps=True)

        plans = self._get_convergence_plans(services, strategy)

        for service in services:
            service.execute_convergence_plan(
                plans[service.name],
                do_build,
                detached=True,
                start=False)

    def events(self):
        def build_container_event(event, container):
            time = datetime.datetime.fromtimestamp(event['time'])
            time = time.replace(
                microsecond=microseconds_from_time_nano(event['timeNano']))
            return {
                'time': time,
                'type': 'container',
                'action': event['status'],
                'id': container.id,
                'service': container.service,
                'attributes': {
                    'name': container.name,
                    'image': event['from'],
                }
            }

        service_names = set(self.service_names)
        for event in self.client.events(
            filters={'label': self.labels()},
            decode=True
        ):
            if event['status'] in IMAGE_EVENTS:
                # We don't receive any image events because labels aren't applied
                # to images
                continue

            # TODO: get labels from the API v1.22 , see github issue 2618
            container = Container.from_id(self.client, event['id'])
            if container.service not in service_names:
                continue
            yield build_container_event(event, container)

    def up(self,
           service_names=None,
           start_deps=True,
           strategy=ConvergenceStrategy.changed,
           do_build=True,
           timeout=DEFAULT_TIMEOUT,
           detached=False):

        self.initialize()
        services = self.get_services_without_duplicate(
            service_names,
            include_deps=start_deps)

        plans = self._get_convergence_plans(services, strategy)
        return [
            container
            for service in services
            for container in service.execute_convergence_plan(
                plans[service.name],
                do_build=do_build,
                timeout=timeout,
                detached=detached
            )
        ]

    def initialize(self):
        self.networks.initialize()
        self.volumes.initialize()

    def _get_convergence_plans(self, services, strategy):
        plans = {}

        for service in services:
            updated_dependencies = [
                name
                for name in service.get_dependency_names()
                if name in plans and
                plans[name].action in ('recreate', 'create')
            ]

            if updated_dependencies and strategy.allows_recreate:
                log.debug('%s has upstream changes (%s)',
                          service.name,
                          ", ".join(updated_dependencies))
                plan = service.convergence_plan(ConvergenceStrategy.always)
            else:
                plan = service.convergence_plan(strategy)

            plans[service.name] = plan

        return plans

    def pull(self, service_names=None, ignore_pull_failures=False):
        for service in self.get_services(service_names, include_deps=False):
            service.pull(ignore_pull_failures)

    def containers(self, service_names=None, stopped=False, one_off=False):
        if service_names:
            self.validate_service_names(service_names)
        else:
            service_names = self.service_names

        containers = list(filter(None, [
            Container.from_ps(self.client, container)
            for container in self.client.containers(
                all=stopped,
                filters={'label': self.labels(one_off=one_off)})]))

        def matches_service_names(container):
            return container.labels.get(LABEL_SERVICE) in service_names

        return [c for c in containers if matches_service_names(c)]

    def _inject_deps(self, acc, service):
        dep_names = service.get_dependency_names()

        if len(dep_names) > 0:
            dep_services = self.get_services(
                service_names=list(set(dep_names)),
                include_deps=True
            )
        else:
            dep_services = []

        dep_services.append(service)
        return acc + dep_services


def get_volumes_from(project, service_dict):
    volumes_from = service_dict.pop('volumes_from', None)
    if not volumes_from:
        return []

    def build_volume_from(spec):
        if spec.type == 'service':
            try:
                return spec._replace(source=project.get_service(spec.source))
            except NoSuchService:
                pass

        if spec.type == 'container':
            try:
                container = Container.from_id(project.client, spec.source)
                return spec._replace(source=container)
            except APIError:
                pass

        raise ConfigurationError(
            "Service \"{}\" mounts volumes from \"{}\", which is not the name "
            "of a service or container.".format(
                service_dict['name'],
                spec.source))

    return [build_volume_from(vf) for vf in volumes_from]


class NoSuchService(Exception):
    def __init__(self, name):
        self.name = name
        self.msg = "No such service: %s" % self.name

    def __str__(self):
        return self.msg
