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
This module contains the Manager class for Plugins in the fastr system
"""

import imp
import inspect
import os
import sys
import traceback
from abc import abstractproperty
import fastr
from fastr.core.basemanager import BaseManager
from fastr.core.baseplugin import BasePlugin
import fastr.exceptions as exceptions


class PluginManager(BaseManager):
    """
    Baseclass for PluginManagers, need to override the self._plugin_class
    """

    def __init__(self, path=None, recursive=False):
        """
        Create a PluginManager and scan the give path for matching plugins

        :param str path: path to scan
        :param bool recursive: flag to indicate a recursive search
        :return: newly created plugin manager
        :raises FastrTypeError: if self._plugin_class is set to a class not
                                 subclassing BasePlugin
        """
        super(PluginManager, self).__init__(path, recursive)

        if not issubclass(self.plugin_class, BasePlugin):
            raise exceptions.FastrTypeError('Plugin type to manage ({}) not a valid plugin! (needs to be subclass of BasePlugin)'.format(self.plugin_class.__name__))

    @abstractproperty
    def plugin_class(self):
        """
        The class from which the plugins must be subclassed
        """
        raise exceptions.FastrNotImplementedError

    @property
    def _item_extension(self):
        """
        Plugins should be loaded from files with a .py extension
        """
        return '.py'

    @property
    def _instantiate(self):
        """
        Flag indicating that the plugin should be instantiated prior to saving
        """
        return True

    def _print_value(self, val):
        """
        Function for printing values (plugins) in this manager

        :param BasePlugin val: value to print
        :return: print representation
        :rtype: str
        """
        if self._instantiate:
            val = type(val)

        print_out = ('<{}: {}>'.format(val.__bases__[0].__name__, val.__name__), '({})'.format(val.status))
        return print_out

    def _load_item(self, filepath):
        """
        Load a plugin

        :param str filepath: path of the plugin to load
        """
        # Since we cannot know what Plugins might throw, catch all
        # pylint: disable=broad-except
        try:
            filebase, _ = os.path.splitext(os.path.basename(filepath))
            temp_module = imp.load_source(filebase, filepath)
            for name, obj in inspect.getmembers(temp_module):
                if inspect.isclass(obj) and issubclass(obj, self.plugin_class):
                    if filebase.lower() != obj.__name__.lower():
                        fastr.log.debug('Plugin name and module do not match ({} vs {})'.format(obj.__name__, filebase))
                        continue
                    obj.filename = filepath
                    if not inspect.isabstract(obj):
                        if obj.status == 'Uninitialized':
                            # Since we cannot know what Plugins might throw, catch all
                            # pylint: disable=broad-except
                            try:
                                obj.set_status('Loaded', 'Set to Loaded to perform testing')  # Let the Plugin think it is loaded, or it will refuse to instantiate
                                obj.test()
                                obj.set_status('Loaded', 'Testing successful, loaded properly')  # Let the Plugin think it is loaded, or it will refuse to instantiate
                            except Exception as exception:
                                fastr.log.warning('Could not instantiate plugin file {}\n{}'.format(filepath, exception))
                                exc_type, _, _ = sys.exc_info()
                                exc_info = traceback.format_exc()
                                fastr.log.debug('Encountered exception ({}) during instantiation of the plugin:\n{}'.format(exc_type.__name__, exc_info))
                                obj.set_status('Failed', ('Encountered exception ({}) during'
                                                          ' instantiation of the plugin:\n{}').format(exc_type.__name__,
                                                                                                      exc_info))
                        elif obj.status not in ['Loaded', 'Failed']:
                            fastr.log.warning('Invalid Plugin status: {}!'.format(obj.status))

                        # Save the source in the obj
                        obj.set_code(inspect.getsource(obj))

                        if self._instantiate:
                            fastr.log.debug('Store instantiated plugin')
                            self._store_item(name, obj())
                        else:
                            fastr.log.debug('Store uninstantiated plugin')
                            self._store_item(name, obj)

                    else:
                        fastr.log.debug('Skipping abstract Plugin: {} ({})'.format(name, filepath))
                else:
                    if inspect.isclass(obj):
                        fastr.log.debug('{} is not a subclass of {}'.format(obj, self.plugin_class))
        except Exception as exception:
            fastr.log.warning('Could not load {} file {}\n{}'.format(self.plugin_class.__name__, filepath, exception))
            exc_type, _, _ = sys.exc_info()
            exc_info = traceback.format_exc()
            fastr.log.debug('Encountered exception ({}) during loading of the plugin:\n{}'.format(exc_type.__name__, exc_info))
