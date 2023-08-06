# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module defines the Fastr Config class for managing the configuration of
Fastr. The config object is stored directly in the fastr top-level module.
"""

import ConfigParser
import inspect
import logging
import logging.config
import multiprocessing
import os
import re
import tempfile
import json
from collections import deque
from urlparse import urlparse


logging.captureWarnings(True)


class Config(object):
    """
    Class contain the fastr configuration
    """
    # pylint: disable=too-many-instance-attributes
    # The config has many attributes, because its function is to hold
    # this data

    def __init__(self, *configfiles):
        #: Indicate if the fastr system is running in debug mode (default is False)
        self.debug = 'FASTRDEBUG' in os.environ

        #: Log type of fastr
        self.logtype = self._find_log_type()

        # Check .fastr directory in user folder (and create it if it does not exist)
        #: The user directory for fastr (typically ~/.fastr on Unix)
        self.userdir = os.path.expanduser(os.path.join('~', '.fastr'))
        if not os.path.exists(self.userdir):
            os.mkdir(self.userdir)

        #: Directory where the fastr logs will be placed
        self.logdir = os.path.join(self.userdir, 'logs')
        if not os.path.exists(self.logdir):
            os.mkdir(self.logdir)

        #: The logger used by fastr, set and updated by the Config object
        self.log = None
        self._update_logging()

        #: Trace of the config files read by this object
        self.read_config_files = []

        #: Placeholder dictionairy to be populated with the plugin config data
        self.plugin_config = {}

        #: Directory of the fastr installation
        self.systemdir = os.path.abspath(os.path.normpath(os.path.dirname(__file__)))

        #: Directory containing the fastr system resources
        self.resourcesdir = os.path.join(self.systemdir, 'resources')

        #: Directory containing the fastr examples
        self.examplesdir = os.path.join(self.systemdir, 'examples')

        #: Directory containing keypair.
        self.secretdir = os.path.join(self.resourcesdir, 'secret')

        #: Directory containing the fastr data schemas
        self.schemadir = os.path.join(self.resourcesdir, 'schemas')

        # Execution script location
        self.executionscript = os.path.join(self.systemdir, 'execution', 'executionscript.py')

        #: Directories used for looking up Type files
        self.types_path = deque()
        self.types_path.appendleft(os.path.join(self.resourcesdir, 'datatypes'))

        #: Directories used for looking up Tool files
        self.tools_path = deque()
        self.tools_path.appendleft(os.path.join(self.resourcesdir, 'tools'))

        #: Directories used for loading plugins for server types
        self.server_plugins_path = deque()
        self.server_plugins_path.appendleft(os.path.join(self.resourcesdir, 'serverplugins'))

        #: Directories used for loading plugins for source/sink i/o
        self.io_plugins_path = deque()
        self.io_plugins_path.appendleft(os.path.join(self.resourcesdir, 'ioplugins'))

        #: Directories used for loading plugins for collectors for the job results
        self.collector_plugins_path = deque()
        self.collector_plugins_path.appendleft(os.path.join(self.resourcesdir, 'collectorplugins'))

        #: Directories used for loading plugins for interfaces
        self.interface_plugins_path = deque()
        self.interface_plugins_path.appendleft(os.path.join(self.resourcesdir, 'interfaceplugins'))

        #: Directories used for loading plugins for interfaces
        self.flow_plugins_path = deque()
        self.flow_plugins_path.appendleft(os.path.join(self.resourcesdir, 'flowplugins'))

        self.local = {}
        self.executors = {}

        #: The server to use for execution of jobs
        self.server = {'name': 'localhost', 'port': 32787, 'autostart': 1, 'executor-plugin': 'ProcessPoolExecution'}

        #: A dictionary containing all mount points in the VFS system
        self.mounts = {'tmp': tempfile.gettempdir(), 'example_data': os.path.join(self.examplesdir, 'data'), 'home': os.path.expanduser('~/')}

        #:  A dict holding the authentication options.
        self.authentication = dict()
        self.authentication['allow_anonymous'] = True
        self.authentication['auth_schemes'] = 'fastr.services.auth.checkers.UNIX,fastr.services.auth.checkers.LDAP'
        self.authentication['request_timeout'] = 15 * 60
        self.authentication['ldap_host'] = 'localmaster'
        self.authentication['ldap_domain'] = 'dc=cm,dc=cluster'

        #: A dictionary with predefined kinds of resources, for the acl permission system.
        self.authentication['acl_structure'] = {
            'network': {'create', 'read', 'write', 'delete', 'execute'},
            'worker': {'start', 'stop', 'status', 'kill', 'list'},
            'server': {'start', 'stop', 'status', 'kill'},
            'usermanagement': {'create', 'read', 'write', 'delete'},
            'system_config': {'read', 'write'},
            'user_config': {'read', 'write'},
        }
        #: A list of users which should be admins.
        #FIXME: do this from the config file instead of here.
        self.authentication['acl_admin_users'] = ['mkoek', 'hachterberg']
        #: Predifined groups and permissions.
        self.authentication['acl_grants'] = {
            '@admin': {
                'network': {'create', 'read', 'write', 'delete', 'execute'},
                'worker': {'start', 'stop', 'status', 'kill', 'list'},
                'server': {'start', 'stop', 'status', 'kill'},
                'usermanagement': {'create', 'read', 'write', 'delete'},
                'system_config': {'read', 'write'},
                'user_config': {'read', 'write'},
            },
            '@super': {
                'network': {'create', 'read', 'write', 'delete', 'execute'},
                'worker': {'start', 'stop', 'status', 'kill', 'list'},
                'server': {'start', 'stop', 'status', 'kill'},
                'usermanagement': {'create', 'read', 'write', 'delete'},
                'system_config': {'read', 'write'},
                'user_config': {'read', 'write'},
            },
            '@user': {
                'network': {'create', 'read', 'write', 'delete', 'execute'},
                'worker': {'start', 'stop', 'status', 'kill', 'list'},
                'server': {},
                'usermanagement': {},
                'system_config': {},
                'user_config': {'read', 'write'},
            },
            'anonymous': {
                'network': {'create', 'read', 'write', 'delete', 'execute'},
                'worker': {'start', 'stop', 'status', 'kill', 'list'},
                'server': {},
                'usermanagement': {},
                'system_config': {},
                'user_config': {'read', 'write'},
            }
        }

        #: A list indicating the order of the preferred types to use. First item is more preferred, second a bit less,
        #: last is least preferred.
        self.preferred_types = []

        #: A list of modules which are protected from unloading
        self.protected_modules = []

        self.web = dict()
        #: secret key for flask sessions.
        self.web['secret_key'] = ''
        #: hostname for serving the web client
        self.web['hostname'] = 'localhost'
        #: port number for servering the web client
        self.web['port'] = 9000

        #: Docker api to use for docker target
        self.docker_api = 'unix://var/run/docker.sock'

        # User file location (tools, datatypes, plugins, etc)
        if os.path.exists(os.path.join(os.path.expanduser('~'), '.fastr')):
            if os.path.exists(os.path.join(self.userdir, 'datatypes')):
                self.types_path.appendleft(os.path.join(self.userdir, 'datatypes'))
            if os.path.exists(os.path.join(self.userdir, 'tools')):
                self.tools_path.appendleft(os.path.join(self.userdir, 'tools'))
            if os.path.exists(os.path.join(self.userdir, 'serverplugins')):
                self.server_plugins_path.appendleft(os.path.join(self.userdir, 'serverplugins'))
            if os.path.exists(os.path.join(self.userdir, 'ioplugins')):
                self.io_plugins_path.appendleft(os.path.join(self.userdir, 'ioplugins'))

        # Read default config files if found
        if os.environ.get('FASTRHOME'):
            if os.path.exists(os.path.join(os.environ['FASTRHOME'], 'conf', 'fastr.config')):
                self.read_config(os.path.join(os.environ['FASTRHOME'], 'conf', 'fastr.config'))

        if os.path.exists(os.path.join(self.userdir, 'fastr.config')):
            self.read_config(os.path.join(self.userdir, 'fastr.config'))

        # Read config files as parameters
        for filename in configfiles:
            if os.path.exists(filename):
                self.read_config(filename)
            else:
                self.log.error('Config file {} does not exist!'.format(filename))

    def __repr__(self):
        if len(self.mounts) > 0:
            maxlen = max(len(x) for x in self.mounts)
            mounts = '\n'.join('{x[0]: >{l}}:  {x[1]}'.format(x=x, l=maxlen) for x in self.mounts.items())
        else:
            mounts = ''
        representation = """
--- general config ---
       debug:  {self.debug}
   systemdir:  {self.systemdir}
resourcesdir:  {self.resourcesdir}
 examplesdir:  {self.examplesdir}
   schemadir:  {self.schemadir}
     userdir:  {self.userdir}
      logdir:  {self.logdir}
     logtype:  {self.logtype}

read from config files:
{configfiles}

------- mounts -------
{mounts}

------- paths --------
types_path:
{types}

tools_path:
{tools}

io_plugins_path:
{iops}

server_plugins_path:
{sps}

----- datatypes ------
preferred_types:
{preftypes}

-- protected modules -
{protmod}
""".format(self=self,
           mounts=mounts,
           types='\n'.join(self.types_path),
           tools='\n'.join(self.tools_path),
           iops='\n'.join(self.io_plugins_path),
           sps='\n'.join(self.server_plugins_path),
           preftypes='\n'.join(self.preferred_types),
           configfiles='\n'.join(self.read_config_files),
           protmod='\n'.join(self.protected_modules))

        maxlen = max(len(x)for x in representation.splitlines())
        maxlen = max(maxlen, 27)
        representation = '{h:=^{l}}\n{b}\n{f:=<{l}}'.format(l=maxlen, h=' fastr configuration ', b=representation, f='')

        return representation

    def read_config(self, filename):
        """
        Read a configuration and update the configuration object accordingly

        :param filename: the configuration file to read
        """
        config = ConfigParser.ConfigParser()
        config.read(filename)

        # Update the debug value
        if config.has_option(section='system', option='debug'):
            debug_config = config.getboolean('system', 'debug')
        else:
            debug_config = False

        self.debug = debug_config or 'FASTRDEBUG' in os.environ

        if config.has_option(section='resources', option='types'):
            extra_types_path = config.get('resources', 'types')
            extra_types_path = re.split('\n', extra_types_path.strip())
            extra_types_path = [os.path.abspath(os.path.expanduser(p.strip())) for p in extra_types_path]
            self.types_path.extendleft(extra_types_path)

        if config.has_option(section='resources', option='tools'):
            extra_tools_path = config.get('resources', 'tools')
            extra_tools_path = re.split('\n', extra_tools_path.strip())
            extra_tools_path = [os.path.abspath(os.path.expanduser(p.strip())) for p in extra_tools_path]
            self.tools_path.extendleft(extra_tools_path)

        if config.has_option(section='resources', option='serverplugins'):
            extra_server_plugins_path = config.get('resources', 'serverplugins')
            extra_server_plugins_path = re.split('\n', extra_server_plugins_path.strip())
            extra_server_plugins_path = [os.path.abspath(os.path.expanduser(p.strip())) for p in extra_server_plugins_path]
            self.server_plugins_path.extendleft(extra_server_plugins_path)

        if config.has_option(section='resources', option='ioplugins'):
            extra_io_plugins_path = config.get('resources', 'ioplugins')
            extra_io_plugins_path = re.split('\n', extra_io_plugins_path.strip())
            extra_io_plugins_path = [os.path.abspath(os.path.expanduser(p.strip())) for p in extra_io_plugins_path]
            self.io_plugins_path.extendleft(extra_io_plugins_path)

        if config.has_option(section='resources', option='collectorplugins'):
            extra_collector_plugins_path = config.get('resources', 'collectorplugins')
            extra_collector_plugins_path = re.split('\n', extra_collector_plugins_path.strip())
            extra_collector_plugins_path = [os.path.abspath(os.path.expanduser(p.strip())) for p in extra_collector_plugins_path]
            self.collector_plugins_path.extendleft(extra_collector_plugins_path)

        if config.has_option(section='resources', option='protected-modules'):
            new_protected_modules = config.get('resources', 'protected-modules')
            new_protected_modules = re.split('\n', new_protected_modules.strip())
            new_protected_modules = [t.strip() for t in new_protected_modules]
            # Do this last, so by here we are sure we found a new valid settings
            self.protected_modules[:] = new_protected_modules  # Slice to keep the reference intact

        if config.has_option(section='types', option='preferred-types'):
            new_preferred_types = config.get('types', 'preferred-types')
            new_preferred_types = re.split('\n', new_preferred_types.strip())
            new_preferred_types = [t.strip() for t in new_preferred_types]
            # Do this last, so by here we are sure we found a new valid settings
            self.preferred_types[:] = new_preferred_types  # Slice to keep the reference intact

        # Read server settings from config file
        if config.has_option('server', 'name'):
            self.server['name'] = config.get('server', 'name')
        if config.has_option('server', 'port'):
            self.server['port'] = config.getint('server', 'port')
        if config.has_option('server', 'autostart'):
            self.server['autostart'] = config.getint('server', 'autostart')
        if config.has_option('server', 'executor-plugin'):
            self.server['executor-plugin'] = config.get('server', 'executor-plugin')

        #: Try to read the authentication section of the config file.
        if config.has_option('authentication', 'allow_anonymous'):
            self.authentication['allow_anonymous'] = config.getboolean('authentication', 'allow_anonymous')
        if config.has_option('authentication', 'auth_schemes'):
            self.authentication['auth_schemes'] = config.get('authentication', 'auth_schemes')
        if config.has_option('authentication', 'request_timeout'):
            self.authentication['request_timeout'] = config.getfloat('authentication', 'request_timeout')
        if config.has_option('authentication', 'ldap_host'):
            self.authentication['ldap_host'] = config.get('authentication', 'ldap_host')
        if config.has_option('authentication', 'ldap_domain'):
            self.authentication['ldap_domain'] = config.get('authentication', 'ldap_domain')
        if config.has_option('authentication', 'acl_structure'):
            self.authentication['acl_structure'] = json.loads(config.get('authentication', 'acl_structure'))
        if config.has_option('authentication', 'acl_admin_users'):
            self.authentication['acl_admin_users'] = json.loads(config.get('authentication', 'acl_structure'))
        if config.has_option('authentication', 'acl_grants'):
            self.authentication['acl_grants'] = json.loads(config.get('authentication', 'acl_grants'))

        # Read the mount points from the config file.
        if config.has_section('mounts'):
            for name, mountpoint in config.items('mounts'):
                self.mounts[name] = os.path.normpath(mountpoint)
        else:
            self.log.warning('mount points [mounts] section does not exist in {}!'.format(filename))

        if config.has_section('web'):
            if config.has_option('web', 'hostname'):
                self.web['hostname'] = config.get('web', 'hostname')
                parsed_hostname = urlparse(self.web['hostname'])
                if parsed_hostname.netloc != '':
                    self.web['hostname'] = parsed_hostname.netloc
            if config.has_option('web', 'port'):
                self.web['port'] = config.getint('web', 'port')
            if config.has_option('web', 'secret_key'):
                self.web['secret_key'] = config.get('web', 'secret_key')
            else:
                raise ValueError("There is no secret set. Please set 'secret_key' in the config under the [web] section.")

        self._update_logging()
        self._read_plugin_sections(config)
        self.read_config_files.append(filename)

    def web_url(self):
        """ Construct a fqdn from the web['hostname'] and web['port'] settings.
        :return: FQDN
        :rtype: str
        """
        if self.web['port'] == 80:
            return 'http://{}' .format(self.web['hostname'])
        elif self.web['port'] == 443:
            return 'https://{}' .format(self.web['hostname'])
        else:
            return 'http://{}:{}'.format(self.web['hostname'], self.web['port'])

    def _read_plugin_sections(self, config):
        """
        Read sections for plugins, these can contain variable data which
        should be used/parsed by the pluings themselves.

        :param config: config object to parse
        """
        for section in config.sections():
            if section.lower().endswith('plugin'):
                if section in self.plugin_config:
                    self.plugin_config[section].update(dict(config.items(section)))
                else:
                    self.plugin_config[section] = dict(config.items(section))

    def _find_log_type(self):
        """
        Figure out the logtype to use for this fastr session

        :return: log type to us
        :rtype: str
        """
        # Use multiprocessing to check if we are actually in the MainProcess
        # Subprocesses should not log in a standard way
        current_process = multiprocessing.current_process()

        # Hack setting non-standard log methods/destinations before fastr is imported
        _stack = inspect.stack()
        for frame in _stack[1:]:
            if 'FASTR_LOG_TYPE' in frame[0].f_globals:
                fastr_log_type = frame[0].f_globals['FASTR_LOG_TYPE']

                # We only want to last definition of fastr_log_type
                break
        else:
            if current_process.name != 'MainProcess':
                #fastr_log_type = 'childprocess'
                fastr_log_type = 'default'
            else:
                fastr_log_type = 'default'

        return fastr_log_type

    def _update_logging(self):
        """
        Update the logging using the current config settings.
        """
        logging_definition = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {
                    'format': '%(levelname)s: %(asctime)s: %(module)s:%(lineno)d: %(process)d: %(threadName)s >> %(message)s'
                },
                'console_simple': {
                    'format': '[%(processName)s::%(threadName)s] %(levelname)s: %(module)s:%(lineno)d >> %(message)s'
                },
                'console_minimal': {
                    'format': '%(levelname)s >> %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'console_simple',
                    'stream': 'ext://sys.stdout',
                },
                'childprocess': {
                    'level': 'CRITICAL',
                    'class': 'logging.NullHandler',
                },
                'error_file': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'verbose',
                    'filename': os.path.join(self.logdir, 'error.log'),
                    'maxBytes': 10 * 1024 * 1024,
                    'backupCount': 20,
                },
                'info_file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'verbose',
                    'filename': os.path.join(self.logdir, 'info.log'),
                    'maxBytes': 10 * 1024 * 1024,
                    'backupCount': 20,
                },
                'server_file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'verbose',
                    'filename': os.path.join(self.logdir, 'server.log'),
                    'maxBytes': 10 * 1024 * 1024,
                    'backupCount': 20,
                },
                'null_handler': {
                    'level': 'CRITICAL',
                    'class': 'logging.NullHandler',
                }
            },
            'loggers': {
                'fastr': {
                    'handlers': ['console', 'info_file', 'error_file'],
                    'propagate': True,
                    'level': 'DEBUG',
                },
                'py:warnings': {
                    'handlers': ['console', 'info_file', 'error_file'],
                    'propagate': True,
                }
            },
            'root': {
                'handlers': ['null_handler'],
                'level': 'DEBUG'
            }
        }

        fastr_log_type_options = {
            'default': ['console', 'info_file', 'error_file'],
            'server': ['server_file', 'console'],
            'daemon': ['server_file'],
            'console': ['console'],
            'childprocess': ['childprocess'],
            'worker': ['worker'],
            'none': ['null_handler']
        }

        logging_definition['loggers']['fastr']['handlers'] = fastr_log_type_options[self.logtype]

        if self.debug:
            logging_definition['handlers']['console']['level'] = 'DEBUG'
            logging_definition['handlers']['server_file']['level'] = 'DEBUG'
            logging_definition['handlers']['debug_file'] = {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': os.path.join(self.logdir, 'debug.log'),
                'maxBytes': 10 * 1024 * 1024,
                'backupCount': 20,
                }
            logging_definition['handlers']['childprocess'] = {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'console_simple',
                'stream': 'ext://sys.stdout',
                }
            logging_definition['loggers']['fastr']['handlers'].append('debug_file')
        else:
            logging_definition['handlers']['console']['level'] = 'INFO'
            logging_definition['handlers']['server_file']['level'] = 'INFO'
            try:
                del logging_definition['handlers']['debug_file']
            except KeyError:
                pass
            try:
                logging_definition['loggers']['fastr']['handlers'].remove('debug_file')
            except ValueError:
                pass
            logging_definition['loggers']['fastr']['level'] = 'INFO'

        logging.config.dictConfig(logging_definition)
        if self.log is None:
            self.log = logging.getLogger('fastr')
            self.log.info('Setting up the FASTR environment')
        else:
            self.log.debug('Updated fastr logging')
        self.log.debug('Log directory: {}'.format(self.logdir))
        self.log.debug('Using log type: {} (debug: {})'.format(self.logtype, self.debug))
