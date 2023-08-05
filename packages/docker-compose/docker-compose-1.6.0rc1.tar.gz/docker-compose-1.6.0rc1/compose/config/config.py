from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
import functools
import logging
import operator
import os
import string
import sys
from collections import namedtuple

import six
import yaml
from cached_property import cached_property

from ..const import COMPOSEFILE_VERSIONS
from .errors import CircularReference
from .errors import ComposeFileNotFound
from .errors import ConfigurationError
from .interpolation import interpolate_environment_variables
from .sort_services import get_service_name_from_net
from .sort_services import sort_service_dicts
from .types import parse_extra_hosts
from .types import parse_restart_spec
from .types import VolumeFromSpec
from .types import VolumeSpec
from .validation import validate_against_fields_schema
from .validation import validate_against_service_schema
from .validation import validate_extends_file_path
from .validation import validate_top_level_object
from .validation import validate_top_level_service_objects


DOCKER_CONFIG_KEYS = [
    'cap_add',
    'cap_drop',
    'cgroup_parent',
    'command',
    'cpu_quota',
    'cpu_shares',
    'cpuset',
    'detach',
    'devices',
    'dns',
    'dns_search',
    'domainname',
    'entrypoint',
    'env_file',
    'environment',
    'extra_hosts',
    'hostname',
    'image',
    'ipc',
    'labels',
    'links',
    'mac_address',
    'mem_limit',
    'memswap_limit',
    'net',
    'pid',
    'ports',
    'privileged',
    'read_only',
    'restart',
    'security_opt',
    'stdin_open',
    'stop_signal',
    'tty',
    'user',
    'volume_driver',
    'volumes',
    'volumes_from',
    'working_dir',
]

ALLOWED_KEYS = DOCKER_CONFIG_KEYS + [
    'build',
    'container_name',
    'dockerfile',
    'expose',
    'external_links',
    'logging',
]

DOCKER_VALID_URL_PREFIXES = (
    'http://',
    'https://',
    'git://',
    'github.com/',
    'git@',
)

SUPPORTED_FILENAMES = [
    'docker-compose.yml',
    'docker-compose.yaml',
]

DEFAULT_OVERRIDE_FILENAME = 'docker-compose.override.yml'

log = logging.getLogger(__name__)


class ConfigDetails(namedtuple('_ConfigDetails', 'working_dir config_files')):
    """
    :param working_dir: the directory to use for relative paths in the config
    :type  working_dir: string
    :param config_files: list of configuration files to load
    :type  config_files: list of :class:`ConfigFile`
     """


class ConfigFile(namedtuple('_ConfigFile', 'filename config')):
    """
    :param filename: filename of the config file
    :type  filename: string
    :param config: contents of the config file
    :type  config: :class:`dict`
    """

    @classmethod
    def from_filename(cls, filename):
        return cls(filename, load_yaml(filename))

    @cached_property
    def version(self):
        if self.config is None:
            return 1
        version = self.config.get('version', 1)
        if isinstance(version, dict):
            log.warn("Unexpected type for field 'version', in file {} assuming "
                     "version is the name of a service, and defaulting to "
                     "Compose file version 1".format(self.filename))
            return 1
        return version

    def get_service_dicts(self):
        return self.config if self.version == 1 else self.config.get('services', {})

    def get_volumes(self):
        return {} if self.version == 1 else self.config.get('volumes', {})

    def get_networks(self):
        return {} if self.version == 1 else self.config.get('networks', {})


class Config(namedtuple('_Config', 'version services volumes networks')):
    """
    :param version: configuration version
    :type  version: int
    :param services: List of service description dictionaries
    :type  services: :class:`list`
    :param volumes: Dictionary mapping volume names to description dictionaries
    :type  volumes: :class:`dict`
    :param networks: Dictionary mapping network names to description dictionaries
    :type  networks: :class:`dict`
    """


class ServiceConfig(namedtuple('_ServiceConfig', 'working_dir filename name config')):

    @classmethod
    def with_abs_paths(cls, working_dir, filename, name, config):
        if not working_dir:
            raise ValueError("No working_dir for ServiceConfig.")

        return cls(
            os.path.abspath(working_dir),
            os.path.abspath(filename) if filename else filename,
            name,
            config)


def find(base_dir, filenames):
    if filenames == ['-']:
        return ConfigDetails(
            os.getcwd(),
            [ConfigFile(None, yaml.safe_load(sys.stdin))])

    if filenames:
        filenames = [os.path.join(base_dir, f) for f in filenames]
    else:
        filenames = get_default_config_files(base_dir)

    log.debug("Using configuration files: {}".format(",".join(filenames)))
    return ConfigDetails(
        os.path.dirname(filenames[0]),
        [ConfigFile.from_filename(f) for f in filenames])


def validate_config_version(config_files):
    main_file = config_files[0]
    validate_top_level_object(main_file)
    for next_file in config_files[1:]:
        validate_top_level_object(next_file)

        if main_file.version != next_file.version:
            raise ConfigurationError(
                "Version mismatch: file {0} specifies version {1} but "
                "extension file {2} uses version {3}".format(
                    main_file.filename,
                    main_file.version,
                    next_file.filename,
                    next_file.version))

    if main_file.version not in COMPOSEFILE_VERSIONS:
        raise ConfigurationError(
            'Invalid Compose file version: {0}'.format(main_file.version))


def get_default_config_files(base_dir):
    (candidates, path) = find_candidates_in_parent_dirs(SUPPORTED_FILENAMES, base_dir)

    if not candidates:
        raise ComposeFileNotFound(SUPPORTED_FILENAMES)

    winner = candidates[0]

    if len(candidates) > 1:
        log.warn("Found multiple config files with supported names: %s", ", ".join(candidates))
        log.warn("Using %s\n", winner)

    return [os.path.join(path, winner)] + get_default_override_file(path)


def get_default_override_file(path):
    override_filename = os.path.join(path, DEFAULT_OVERRIDE_FILENAME)
    return [override_filename] if os.path.exists(override_filename) else []


def find_candidates_in_parent_dirs(filenames, path):
    """
    Given a directory path to start, looks for filenames in the
    directory, and then each parent directory successively,
    until found.

    Returns tuple (candidates, path).
    """
    candidates = [filename for filename in filenames
                  if os.path.exists(os.path.join(path, filename))]

    if not candidates:
        parent_dir = os.path.join(path, '..')
        if os.path.abspath(parent_dir) != os.path.abspath(path):
            return find_candidates_in_parent_dirs(filenames, parent_dir)

    return (candidates, path)


def load(config_details):
    """Load the configuration from a working directory and a list of
    configuration files.  Files are loaded in order, and merged on top
    of each other to create the final configuration.

    Return a fully interpolated, extended and validated configuration.
    """
    validate_config_version(config_details.config_files)

    processed_files = [
        process_config_file(config_file)
        for config_file in config_details.config_files
    ]
    config_details = config_details._replace(config_files=processed_files)

    main_file = config_details.config_files[0]
    volumes = load_mapping(config_details.config_files, 'get_volumes', 'Volume')
    networks = load_mapping(config_details.config_files, 'get_networks', 'Network')
    service_dicts = load_services(
        config_details.working_dir,
        main_file,
        [file.get_service_dicts() for file in config_details.config_files])
    return Config(main_file.version, service_dicts, volumes, networks)


def load_mapping(config_files, get_func, entity_type):
    mapping = {}

    for config_file in config_files:
        for name, config in getattr(config_file, get_func)().items():
            mapping[name] = config or {}
            if not config:
                continue

            external = config.get('external')
            if external:
                if len(config.keys()) > 1:
                    raise ConfigurationError(
                        '{} {} declared as external but specifies'
                        ' additional attributes ({}). '.format(
                            entity_type,
                            name,
                            ', '.join([k for k in config.keys() if k != 'external'])
                        )
                    )
                if isinstance(external, dict):
                    config['external_name'] = external.get('name')
                else:
                    config['external_name'] = name

            mapping[name] = config

    return mapping


def load_services(working_dir, config_file, service_configs):
    def build_service(service_name, service_dict, service_names):
        service_config = ServiceConfig.with_abs_paths(
            working_dir,
            config_file.filename,
            service_name,
            service_dict)
        resolver = ServiceExtendsResolver(service_config, config_file)
        service_dict = process_service(resolver.run())

        validate_service(service_dict, service_config.name, config_file.version)
        service_dict = finalize_service(
            service_config._replace(config=service_dict),
            service_names,
            config_file.version)
        return service_dict

    def build_services(service_config):
        service_names = service_config.keys()
        return sort_service_dicts([
            build_service(name, service_dict, service_names)
            for name, service_dict in service_config.items()
        ])

    def merge_services(base, override):
        all_service_names = set(base) | set(override)
        return {
            name: merge_service_dicts_from_files(
                base.get(name, {}),
                override.get(name, {}),
                config_file.version)
            for name in all_service_names
        }

    service_config = service_configs[0]
    for next_config in service_configs[1:]:
        service_config = merge_services(service_config, next_config)

    return build_services(service_config)


def process_config_file(config_file, service_name=None):
    service_dicts = config_file.get_service_dicts()
    validate_top_level_service_objects(config_file.filename, service_dicts)

    interpolated_config = interpolate_environment_variables(service_dicts, 'service')

    if config_file.version == 2:
        processed_config = dict(config_file.config)
        processed_config['services'] = interpolated_config
        processed_config['volumes'] = interpolate_environment_variables(
            config_file.get_volumes(), 'volume')
        processed_config['networks'] = interpolate_environment_variables(
            config_file.get_networks(), 'network')

    if config_file.version == 1:
        processed_config = interpolated_config

    config_file = config_file._replace(config=processed_config)
    validate_against_fields_schema(config_file)

    if service_name and service_name not in processed_config:
        raise ConfigurationError(
            "Cannot extend service '{}' in {}: Service not found".format(
                service_name, config_file.filename))

    return config_file


class ServiceExtendsResolver(object):
    def __init__(self, service_config, config_file, already_seen=None):
        self.service_config = service_config
        self.working_dir = service_config.working_dir
        self.already_seen = already_seen or []
        self.config_file = config_file

    @property
    def signature(self):
        return self.service_config.filename, self.service_config.name

    def detect_cycle(self):
        if self.signature in self.already_seen:
            raise CircularReference(self.already_seen + [self.signature])

    def run(self):
        self.detect_cycle()

        if 'extends' in self.service_config.config:
            service_dict = self.resolve_extends(*self.validate_and_construct_extends())
            return self.service_config._replace(config=service_dict)

        return self.service_config

    def validate_and_construct_extends(self):
        extends = self.service_config.config['extends']
        if not isinstance(extends, dict):
            extends = {'service': extends}

        config_path = self.get_extended_config_path(extends)
        service_name = extends['service']

        extends_file = ConfigFile.from_filename(config_path)
        validate_config_version([self.config_file, extends_file])
        extended_file = process_config_file(
            extends_file,
            service_name=service_name)
        service_config = extended_file.config[service_name]
        return config_path, service_config, service_name

    def resolve_extends(self, extended_config_path, service_dict, service_name):
        resolver = ServiceExtendsResolver(
            ServiceConfig.with_abs_paths(
                os.path.dirname(extended_config_path),
                extended_config_path,
                service_name,
                service_dict),
            self.config_file,
            already_seen=self.already_seen + [self.signature])

        service_config = resolver.run()
        other_service_dict = process_service(service_config)
        validate_extended_service_dict(
            other_service_dict,
            extended_config_path,
            service_name)

        return merge_service_dicts(
            other_service_dict,
            self.service_config.config,
            self.config_file.version)

    def get_extended_config_path(self, extends_options):
        """Service we are extending either has a value for 'file' set, which we
        need to obtain a full path too or we are extending from a service
        defined in our own file.
        """
        filename = self.service_config.filename
        validate_extends_file_path(
            self.service_config.name,
            extends_options,
            filename)
        if 'file' in extends_options:
            return expand_path(self.working_dir, extends_options['file'])
        return filename


def resolve_environment(service_dict):
    """Unpack any environment variables from an env_file, if set.
    Interpolate environment values if set.
    """
    env = {}
    for env_file in service_dict.get('env_file', []):
        env.update(env_vars_from_file(env_file))

    env.update(parse_environment(service_dict.get('environment')))
    return dict(resolve_env_var(k, v) for k, v in six.iteritems(env))


def resolve_build_args(build):
    args = parse_build_arguments(build.get('args'))
    return dict(resolve_env_var(k, v) for k, v in six.iteritems(args))


def validate_extended_service_dict(service_dict, filename, service):
    error_prefix = "Cannot extend service '%s' in %s:" % (service, filename)

    if 'links' in service_dict:
        raise ConfigurationError(
            "%s services with 'links' cannot be extended" % error_prefix)

    if 'volumes_from' in service_dict:
        raise ConfigurationError(
            "%s services with 'volumes_from' cannot be extended" % error_prefix)

    if 'net' in service_dict:
        if get_service_name_from_net(service_dict['net']) is not None:
            raise ConfigurationError(
                "%s services with 'net: container' cannot be extended" % error_prefix)


def validate_ulimits(ulimit_config):
    for limit_name, soft_hard_values in six.iteritems(ulimit_config):
        if isinstance(soft_hard_values, dict):
            if not soft_hard_values['soft'] <= soft_hard_values['hard']:
                raise ConfigurationError(
                    "ulimit_config \"{}\" cannot contain a 'soft' value higher "
                    "than 'hard' value".format(ulimit_config))


def validate_service(service_dict, service_name, version):
    validate_against_service_schema(service_dict, service_name, version)
    validate_paths(service_dict)

    if 'ulimits' in service_dict:
        validate_ulimits(service_dict['ulimits'])

    if not service_dict.get('image') and has_uppercase(service_name):
        raise ConfigurationError(
            "Service '{name}' contains uppercase characters which are not valid "
            "as part of an image name. Either use a lowercase service name or "
            "use the `image` field to set a custom name for the service image."
            .format(name=service_name))


def process_service(service_config):
    working_dir = service_config.working_dir
    service_dict = dict(service_config.config)

    if 'env_file' in service_dict:
        service_dict['env_file'] = [
            expand_path(working_dir, path)
            for path in to_list(service_dict['env_file'])
        ]

    if 'build' in service_dict:
        if isinstance(service_dict['build'], six.string_types):
            service_dict['build'] = resolve_build_path(working_dir, service_dict['build'])
        elif isinstance(service_dict['build'], dict) and 'context' in service_dict['build']:
            path = service_dict['build']['context']
            service_dict['build']['context'] = resolve_build_path(working_dir, path)

    if 'volumes' in service_dict and service_dict.get('volume_driver') is None:
        service_dict['volumes'] = resolve_volume_paths(working_dir, service_dict)

    if 'labels' in service_dict:
        service_dict['labels'] = parse_labels(service_dict['labels'])

    if 'extra_hosts' in service_dict:
        service_dict['extra_hosts'] = parse_extra_hosts(service_dict['extra_hosts'])

    for field in ['dns', 'dns_search']:
        if field in service_dict:
            service_dict[field] = to_list(service_dict[field])

    return service_dict


def finalize_service(service_config, service_names, version):
    service_dict = dict(service_config.config)

    if 'environment' in service_dict or 'env_file' in service_dict:
        service_dict['environment'] = resolve_environment(service_dict)
        service_dict.pop('env_file', None)

    if 'volumes_from' in service_dict:
        service_dict['volumes_from'] = [
            VolumeFromSpec.parse(vf, service_names, version)
            for vf in service_dict['volumes_from']
        ]

    if 'volumes' in service_dict:
        service_dict['volumes'] = [
            VolumeSpec.parse(v) for v in service_dict['volumes']]

    if 'restart' in service_dict:
        service_dict['restart'] = parse_restart_spec(service_dict['restart'])

    normalize_build(service_dict, service_config.working_dir)

    service_dict['name'] = service_config.name
    return normalize_v1_service_format(service_dict)


def normalize_v1_service_format(service_dict):
    if 'log_driver' in service_dict or 'log_opt' in service_dict:
        if 'logging' not in service_dict:
            service_dict['logging'] = {}
        if 'log_driver' in service_dict:
            service_dict['logging']['driver'] = service_dict['log_driver']
            del service_dict['log_driver']
        if 'log_opt' in service_dict:
            service_dict['logging']['options'] = service_dict['log_opt']
            del service_dict['log_opt']

    if 'dockerfile' in service_dict:
        service_dict['build'] = service_dict.get('build', {})
        service_dict['build'].update({
            'dockerfile': service_dict.pop('dockerfile')
        })

    return service_dict


def merge_service_dicts_from_files(base, override, version):
    """When merging services from multiple files we need to merge the `extends`
    field. This is not handled by `merge_service_dicts()` which is used to
    perform the `extends`.
    """
    new_service = merge_service_dicts(base, override, version)
    if 'extends' in override:
        new_service['extends'] = override['extends']
    elif 'extends' in base:
        new_service['extends'] = base['extends']
    return new_service


def merge_service_dicts(base, override, version):
    d = {}

    def merge_field(field, merge_func, default=None):
        if field in base or field in override:
            d[field] = merge_func(
                base.get(field, default),
                override.get(field, default))

    def merge_mapping(mapping, parse_func):
        if mapping in base or mapping in override:
            merged = parse_func(base.get(mapping, None))
            merged.update(parse_func(override.get(mapping, None)))
            d[mapping] = merged

    merge_mapping('environment', parse_environment)
    merge_mapping('labels', parse_labels)
    merge_mapping('ulimits', parse_ulimits)

    for field in ['volumes', 'devices']:
        merge_field(field, merge_path_mappings)

    for field in ['ports', 'expose', 'external_links']:
        merge_field(field, operator.add, default=[])

    for field in ['dns', 'dns_search', 'env_file']:
        merge_field(field, merge_list_or_string)

    for field in set(ALLOWED_KEYS) - set(d):
        if field in base or field in override:
            d[field] = override.get(field, base.get(field))

    if version == 1:
        legacy_v1_merge_image_or_build(d, base, override)
    else:
        merge_build(d, base, override)

    return d


def merge_build(output, base, override):
    build = {}

    if 'build' in base:
        if isinstance(base['build'], six.string_types):
            build['context'] = base['build']
        else:
            build.update(base['build'])

    if 'build' in override:
        if isinstance(override['build'], six.string_types):
            build['context'] = override['build']
        else:
            build.update(override['build'])

    if build:
        output['build'] = build


def legacy_v1_merge_image_or_build(output, base, override):
    output.pop('image', None)
    output.pop('build', None)
    if 'image' in override:
        output['image'] = override['image']
    elif 'build' in override:
        output['build'] = override['build']
    elif 'image' in base:
        output['image'] = base['image']
    elif 'build' in base:
        output['build'] = base['build']


def merge_environment(base, override):
    env = parse_environment(base)
    env.update(parse_environment(override))
    return env


def split_env(env):
    if isinstance(env, six.binary_type):
        env = env.decode('utf-8', 'replace')
    if '=' in env:
        return env.split('=', 1)
    else:
        return env, None


def split_label(label):
    if '=' in label:
        return label.split('=', 1)
    else:
        return label, ''


def parse_dict_or_list(split_func, type_name, arguments):
    if not arguments:
        return {}

    if isinstance(arguments, list):
        return dict(split_func(e) for e in arguments)

    if isinstance(arguments, dict):
        return dict(arguments)

    raise ConfigurationError(
        "%s \"%s\" must be a list or mapping," %
        (type_name, arguments)
    )


parse_build_arguments = functools.partial(parse_dict_or_list, split_env, 'build arguments')
parse_environment = functools.partial(parse_dict_or_list, split_env, 'environment')
parse_labels = functools.partial(parse_dict_or_list, split_label, 'labels')


def parse_ulimits(ulimits):
    if not ulimits:
        return {}

    if isinstance(ulimits, dict):
        return dict(ulimits)


def resolve_env_var(key, val):
    if val is not None:
        return key, val
    elif key in os.environ:
        return key, os.environ[key]
    else:
        return key, ''


def env_vars_from_file(filename):
    """
    Read in a line delimited file of environment variables.
    """
    if not os.path.exists(filename):
        raise ConfigurationError("Couldn't find env file: %s" % filename)
    env = {}
    for line in codecs.open(filename, 'r', 'utf-8'):
        line = line.strip()
        if line and not line.startswith('#'):
            k, v = split_env(line)
            env[k] = v
    return env


def resolve_volume_paths(working_dir, service_dict):
    return [
        resolve_volume_path(working_dir, volume)
        for volume in service_dict['volumes']
    ]


def resolve_volume_path(working_dir, volume):
    container_path, host_path = split_path_mapping(volume)

    if host_path is not None:
        if host_path.startswith('.'):
            host_path = expand_path(working_dir, host_path)
        host_path = os.path.expanduser(host_path)
        return u"{}:{}".format(host_path, container_path)
    else:
        return container_path


def normalize_build(service_dict, working_dir):

    if 'build' in service_dict:
        build = {}
        # Shortcut where specifying a string is treated as the build context
        if isinstance(service_dict['build'], six.string_types):
            build['context'] = service_dict.pop('build')
        else:
            build.update(service_dict['build'])
            if 'args' in build:
                build['args'] = resolve_build_args(build)

        service_dict['build'] = build


def resolve_build_path(working_dir, build_path):
    if is_url(build_path):
        return build_path
    return expand_path(working_dir, build_path)


def is_url(build_path):
    return build_path.startswith(DOCKER_VALID_URL_PREFIXES)


def validate_paths(service_dict):
    if 'build' in service_dict:
        build = service_dict.get('build', {})

        if isinstance(build, six.string_types):
            build_path = build
        elif isinstance(build, dict) and 'context' in build:
            build_path = build['context']

        if (
            not is_url(build_path) and
            (not os.path.exists(build_path) or not os.access(build_path, os.R_OK))
        ):
            raise ConfigurationError(
                "build path %s either does not exist, is not accessible, "
                "or is not a valid URL." % build_path)


def merge_path_mappings(base, override):
    d = dict_from_path_mappings(base)
    d.update(dict_from_path_mappings(override))
    return path_mappings_from_dict(d)


def dict_from_path_mappings(path_mappings):
    if path_mappings:
        return dict(split_path_mapping(v) for v in path_mappings)
    else:
        return {}


def path_mappings_from_dict(d):
    return [join_path_mapping(v) for v in d.items()]


def split_path_mapping(volume_path):
    """
    Ascertain if the volume_path contains a host path as well as a container
    path. Using splitdrive so windows absolute paths won't cause issues with
    splitting on ':'.
    """
    # splitdrive has limitations when it comes to relative paths, so when it's
    # relative, handle special case to set the drive to ''
    if volume_path.startswith('.') or volume_path.startswith('~'):
        drive, volume_config = '', volume_path
    else:
        drive, volume_config = os.path.splitdrive(volume_path)

    if ':' in volume_config:
        (host, container) = volume_config.split(':', 1)
        return (container, drive + host)
    else:
        return (volume_path, None)


def join_path_mapping(pair):
    (container, host) = pair
    if host is None:
        return container
    else:
        return ":".join((host, container))


def expand_path(working_dir, path):
    return os.path.abspath(os.path.join(working_dir, os.path.expanduser(path)))


def merge_list_or_string(base, override):
    return to_list(base) + to_list(override)


def to_list(value):
    if value is None:
        return []
    elif isinstance(value, six.string_types):
        return [value]
    else:
        return value


def has_uppercase(name):
    return any(char in string.ascii_uppercase for char in name)


def load_yaml(filename):
    try:
        with open(filename, 'r') as fh:
            return yaml.safe_load(fh)
    except (IOError, yaml.YAMLError) as e:
        error_name = getattr(e, '__module__', '') + '.' + e.__class__.__name__
        raise ConfigurationError(u"{}: {}".format(error_name, e))
