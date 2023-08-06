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
The module containing the classes describing the targets.
"""

from abc import ABCMeta, abstractmethod
import platform
import datetime
import os
import psutil
import subprocess
import time
import threading

import fastr
from fastr import exceptions
from fastr.data import url

# Check if docker is available
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    docker = None
    DOCKER_AVAILABLE = False

# Check if environment modules are available
try:
    from fastr.execution.environmentmodules import EnvironmentModules
    ENVIRONMENT_MODULES = EnvironmentModules(fastr.config.protected_modules)
    ENVIRONMENT_MODULES_LOADED = True
except exceptions.FastrValueError:
    ENVIRONMENT_MODULES = None
    ENVIRONMENT_MODULES_LOADED = False

try:
    from nipype.interfaces import base as nipypebase
    NIPYPE_AVAILABLE = True
except:
    NIPYPE_AVAILABLE = False

# Monitor interval for profiling
_MONITOR_INTERVAL = 1.0


class Target(object):
    """
    The abstract base class for all targets. Execution with a target should
    follow the following pattern:

    >>> with Target() as target:
    ...     target.run_commmand(['sleep', '10'])
    ...     target.run_commmand(['sleep', '10'])
    ...     target.run_commmand(['sleep', '10'])

    The Target context operator will set the correct paths/initialization.
    Within the context command can be ran and when leaving the context the
    target reverts the state before.
    """
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        pass

    if NIPYPE_AVAILABLE:
        _NIPYPE_RUN_COMMAND = nipypebase.run_command

        def nipype_run(self, runtime, output, timeout=None):
            """
            A command that has the same signature as the nipype.interfaces.base.run_command

            This adapts the call to the self.run_command that fastr uses for just dispatching
            without environment setting.
            """
            # It is safe to ignore the environmnet (as it is just a copy)
            # It is safe to ignore cwd (as it is just a copy)
            # See nipype.interfaces.base:974
            self.run_command(runtime.cmdline)
    else:
        _NIPYPE_RUN_COMMAND = None

    def __enter__(self):
        """
        Set the environment in such a way that the target will be on the path.
        """
        if NIPYPE_AVAILABLE:
            # Make sure nipype runs via the Target and not just spawn own subprocesses
            nipypebase.run_command = self.nipype_run
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleanup the environment where needed
        """
        if NIPYPE_AVAILABLE:
            # Reset nipype to work with own run_command
            nipypebase.run_command = self._NIPYPE_RUN_COMMAND
        pass

    @abstractmethod
    def run_command(self, command):
        pass


class LocalBinaryTarget(Target):
    """
    A tool target that is a local binary on the system. Can be found using
    environmentmodules or vfs-path on the executing machine
    """
    
    DYNAMIC_LIBRARY_PATH_DICT = {
        'windows': 'PATH',              #Not Tested
        'linux': 'LD_LIBRARY_PATH',     #tested
        'darwin': 'DYLD_LIBRARY_PATH',  #tested
    }

    _platform = platform.system().lower()
    if _platform not in DYNAMIC_LIBRARY_PATH_DICT:
        fastr.log.warning('"Dynamic library path not supported on platform: {}"'.format(_platform))
    

    def __init__(self, bin, paths=None, environment_variables=None, initscripts=None, modules=None, interpreter=None, **kwargs):
        """
        Define a new local binary target. Must be defined either using paths and optionally environment_variables
        and initscripts, or enviroment modules.
        """
        self.binary = bin
        if modules is None:
            if 'module' in kwargs and kwargs['module'] is not None:
                fastr.log.warning('Using deprecated module in target (modules is new way to do it)')
                self._modules = (kwargs['module'],)
            else:
                self._modules = None
        elif isinstance(modules, str):
            self._modules = (modules.strip(),)
        else:
            self._modules = tuple(x.strip() for x in modules)

        if isinstance(paths, str):
            self._paths = [{'type': 'bin', 'value': paths}]
        elif paths is None and 'location' in kwargs and kwargs['location'] is not None:
            fastr.log.warning('Using deprecated location in target (paths is the new way to do it)')
            self._paths = [{'type': 'bin', 'value': kwargs['location']}]
        else:
            self._paths = paths

        if paths is not None:
            for path_entry in self._paths:
                if not url.isurl(path_entry['value']):
                    path_entry['value'] = os.path.abspath(path_entry['value'])

        if environment_variables is None:
            environment_variables = {}
        self._envvar = environment_variables

        if initscripts is None:
            initscripts = []
        self._init_scripts = initscripts

        self.interpreter = interpreter

        self._roll_back = None

    def __enter__(self):
        """
        Set the environment in such a way that the target will be on the path.
        """
        super(LocalBinaryTarget, self).__enter__()

        #Create dictionary of possible platforms, to set dynamic labrary path
        #Add check to see if _platform is present in dictionary

                                     
        if self._platform in self.DYNAMIC_LIBRARY_PATH_DICT:
            dynamic_library_path = self.DYNAMIC_LIBRARY_PATH_DICT[self._platform]
        else:
            dynamic_library_path = None

        if ENVIRONMENT_MODULES_LOADED and self._modules is not None and len(self._modules) > 0:
            # Clear the enviroment modules and load all required modules
            ENVIRONMENT_MODULES.clear()
            for module_ in self._modules:
                if not ENVIRONMENT_MODULES.isloaded(module_):
                    ENVIRONMENT_MODULES.load(module_)
                    fastr.log.info('loaded module: {}'.format(module_))
            fastr.log.info('LoadedModules: {}'.format(ENVIRONMENT_MODULES.loaded_modules))
        elif self._paths is not None:
            # Prepend PATH and LD_LIBRARY_PATH as required
            self._roll_back = {'PATH': os.environ.get('PATH', None)}

            # Prepend extra paths to PATH
            bin_path = os.environ.get('PATH', None)
            bin_path = [bin_path] if bin_path else []
            extra_path = [x['value'] for x in self._paths if x['type'] == 'bin']
            extra_path = [fastr.vfs.url_to_path(x) if url.isurl(x) else x for x in extra_path]
            fastr.log.info('Adding extra PATH: {}'.format(extra_path))
            os.environ['PATH'] = os.pathsep.join(extra_path + bin_path)

            # Prepend extra paths to LB_LIBRARY_PATH
            extra_ld_library_path = [x['value'] for x in self._paths if x['type'] == 'lib']
            if len(extra_ld_library_path) > 0:
                if dynamic_library_path is None:
                    message = 'Cannot set dynamic library path on platform: {}'.format(self._platform)
                    fastr.log.critical(message)
                    raise exceptions.FastrNotImplementedError(message)
                
                self._roll_back[dynamic_library_path] = os.environ.get(dynamic_library_path, None)
                
                lib_path = os.environ.get(dynamic_library_path, None)
                lib_path = [lib_path] if lib_path else []
                extra_ld_library_path = [fastr.vfs.url_to_path(x) if url.isurl(x) else x for x in extra_ld_library_path]

                fastr.log.info('Adding extra LIB: {}'.format(extra_path))
                os.environ[dynamic_library_path] = os.pathsep.join(extra_ld_library_path + lib_path)
                    

            # Set other environment variables as indicated
            for var, value in self._envvar.items():
                if var in ['PATH', dynamic_library_path]:
                    continue

                self._roll_back[var] = os.environ.get(var, None)
                os.environ = value

            # Run init script(s) if required
            for script in self._init_scripts:
                if isinstance(script, str):
                    script = [script]

                subprocess.call(script)
        else:
            raise exceptions.FastrNotImplementedError('Binary targets must have either paths or modules set! (binary {})'.format(self.binary))

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleanup the environment
        """
        if ENVIRONMENT_MODULES_LOADED and self._modules is not None and len(self._modules) > 0:
            ENVIRONMENT_MODULES.clear()
        elif self._roll_back is not None:
            for var, value in self._roll_back.items():
                if value is not None:
                    os.environ[var] = value
                else:
                    del os.environ[var]

            self._roll_back = None

    def call_subprocess(self, command):
        """
        Call a subprocess with logging/timing/profiling

        :param list command: the command to execute
        :return: execution info
        :rtype: dict
        """
        sysuse = []
        start_time = time.time()
        fastr.log.info('Calling command: {}'.format(command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        monitor_thread = threading.Thread(target=self.monitor_process, name='SubprocessMonitor', args=(process, sysuse))
        monitor_thread.daemon = True  # Make sure this Thread does not block exiting the script
        monitor_thread.start()
        stdout, stderr = process.communicate()
        return_code = process.poll()
        end_time = time.time()

        if monitor_thread.is_alive():
            monitor_thread.join(2 * _MONITOR_INTERVAL)
            if monitor_thread.is_alive():
                fastr.log.warning('Ignoring unresponsive monitor thread!')

        return {'returncode': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'resource_usage': sysuse,
                'time_elapsed': end_time - start_time}

    def monitor_process(self, process, resources):
        """
        Monitor a process and profile the cpu, memory and io use. Register the
        resource use every _MONITOR_INTERVAL seconds.

        :param subproces.Popen process: process to monitor
        :param resources: list to append measurements to
        """
        psproc = psutil.Process(process.pid)

        while process.poll() is None:
            try:
                # First get 1.0 sec cpu, then moment of memory and io, then add the timestamp
                usage = (psproc.cpu_percent(_MONITOR_INTERVAL), psproc.memory_info(), psproc.io_counters())
                resources.append((datetime.datetime.now(),) + usage)
            except psutil.Error:
                # If the error occured because during the interval of meassuring the CPU use
                # the process stopped, we do not mind
                if process.poll() is None:
                    raise

    def run_command(self, command):
        if self.interpreter is not None:
            paths = [x['value'] for x in self._paths if x['type'] == 'bin']
            fastr.log.info('Options: {}'.format(paths))
            containing_path = next(x for x in paths if os.path.exists(os.path.join(x, command[0])))
            command = [self.interpreter, os.path.join(containing_path, command[0])] + command[1:]

        return self.call_subprocess(command)


class DockerTarget(Target):
    """
    A tool target that is located in a Docker images. Can be run using
    docker-py.
    """
    def __init__(self, docker_image, **kwargs):
        """
        Define a new docker target.

        :param str docker_image: Docker image to use
        """
        if not DOCKER_AVAILABLE:
            raise exceptions.FastrOptionalModuleNotAvailableError('Target cannot be used, module "docker" unavailable')

        self._docker_image = docker_image
        self._docker_client = docker.Client(fastr.config.docker_api)
        self._container = None

    def __enter__(self):
        super(DockerTarget, self).__enter__()
        mounts = fastr.config.mounts.values()
        docker_response = self._docker_client.create_container(image=self._docker_image,
                                                               volumes=mounts)
        if docker_response['Warnings'] is not None:
            fastr.log.warning('Creating the docker containers issued the following warnings: {}'.format(docker_response['Warnings']))
        self._container = docker_response['Id']

        # Bind all fastr mounts
        binds = {x: {'bind': x, 'ro': True} for x in mounts if os.path.exists(x)}
        binds['/tmp']['ro'] = False

        self._docker_client.start(self.container, binds=binds)

    def __exit__(self, exc_type, exc_value, traceback):
        self._docker_client.remove_container(self.container)
        self._container = None

    @property
    def container(self):
        return self._container

    def run_command(self, command):
        # TODO: figure out the stdout saving etc
        sysuse = []
        start_time = time.time()
        self._docker_client.exec_create(self.container, command)

        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_docker, name='DockerMonitor', args=(sysuse,))
        monitor_thread.daemon = True  # Make sure this Thread does not block exiting the script
        monitor_thread.start()

        return_code = self._docker_client.wait(self.container)
        end_time = time.time()
        stdout = self._docker_client.logs(self.container, stdout=True, stderr=False, stream=False, timestamps=True)
        stderr = self._docker_client.logs(self.container, stdout=False, stderr=True, stream=False, timestamps=True)

        if monitor_thread.is_alive():
            monitor_thread.join(2 * _MONITOR_INTERVAL)
            if monitor_thread.is_alive():
                fastr.log.warning('Ignoring unresponsive monitor thread!')

        return {'returncode': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'resource_usage': sysuse,
                'time_elapsed': end_time - start_time}

    def monitor_docker(self, resources):
        """
        Monitor a process and profile the cpu, memory and io use. Register the
        resource use every _MONITOR_INTERVAL seconds.

        :param subproces.Popen process: process to monitor
        :param resources: list to append measurements to
        """
        for stat in self._docker_client.stats(self.container, decode=True):
            # Get cpu, memory and io statistics
            usage = stat['cpu_stats'], stat['memory_stats'], stat['blkio_stats']
            resources.append((datetime.datetime.now(),) + usage)
