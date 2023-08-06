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

from abc import abstractmethod
import os
from collections import OrderedDict

import fastr
from fastr import exceptions
from fastr.core.baseplugin import BasePlugin

from fastr.core.pluginmanager import PluginManager
from fastr.core.interface import Interface, InterfaceResult, InputSpec, OutputSpec


class FlowPlugin(BasePlugin):
    @abstractmethod
    def execute(payload):
        result_data = None
        log_data = None
        return result_data, log_data


class FlowPluginManager(PluginManager):
    """
    Container holding all the CollectorPlugins
    """

    def __init__(self, path=None, recursive=False):
        """
        Create the Coll
        :param path:
        :param recursive:
        :return:
        """
        if path is None:
            path = fastr.config.flow_plugins_path

        super(FlowPluginManager, self).__init__(path, recursive)

    @property
    def plugin_class(self):
        """
        The class of the Plugins in the collection
        """
        return FlowPlugin

    @property
    def _instantiate(self):
        """
        Indicate that the plugins should instantiated before stored
        """
        return False


class FlowInterface(Interface):
    """
    The default Interface for fastr. For the command-line Tools as used by
    fastr.
    """

    __dataschemafile__ = 'FastrInterface.schema.json'

    flow_plugins = FlowPluginManager()

    def __init__(self, id_, document):
        super(FlowInterface, self).__init__()

        # Load from file if it is not a dict
        if not isinstance(document, dict):
            fastr.log.debug('Trying to load file: {}'.format(document))
            filename = os.path.expanduser(document)
            filename = os.path.abspath(filename)
            document = self._loadf(filename)
        else:
            document = self.get_serializer().instantiate(document)

        #: The ID of the interface
        self.id = id_

        # Create the inputs/outputs spec to expose to the rest of the system
        self._inputs = OrderedDict((v['id'], InputSpec(id=v['id'],
                                                       cardinality=v.get('cardinality', 1),
                                                       datatype=v['datatype'] if 'datatype' in v else fastr.typelist.create_enumtype('__{}__{}__Enum__'.format(self.id, v['id']),
                                                                                                                                     tuple(v['enum'])),
                                                       required=v.get('required', True),
                                                       description=v.get('description', ''),
                                                       default=v.get('default', None),
                                                       hidden=v.get('hidden', False))) for v in document['inputs'])

        self._outputs = OrderedDict((v['id'], OutputSpec(id=v['id'],
                                                         cardinality=v.get('cardinality', 1),
                                                         datatype=v['datatype'] if 'datatype' in v else fastr.typelist.create_enumtype('__{}__{}__Enum__'.format(self.id, v['id']),
                                                                                                                                       tuple(v['enum'])),
                                                         automatic=v.get('automatic', False),
                                                         required=v.get('required', True),
                                                         description=v.get('description', ''),
                                                         hidden=v.get('hidden', False))) for v in document['outputs'])

    def __eq__(self, other):
        if not isinstance(other, FlowInterface):
            return NotImplemented

        return vars(self) == vars(other)

    def __getstate__(self):
        """
        Get the state of the FastrInterface object.

        :return: state of interface
        :rtype: dict
        """
        state = {
            'id': self.id,
            'class': type(self).__name__,
            'inputs': self.inputs.values(),
            'outputs': self.outputs.values(),
        }

        return state

    def __setstate__(self, state):
        """
        Set the state of the Interface
        """
        self.id = state['id']

        self._inputs = OrderedDict((x['id'], x) for x in state['inputs'])
        self._outputs = OrderedDict((x['id'], x) for x in state['outputs'])

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    def expanding(self):
        return 1

    def execute(self, target, payload):
        try:
            flow_plugin = self.flow_plugins[target.binary]
        except KeyError:
            raise exceptions.FastrKeyError('Could not find {} in {} (options {})'.format(target.binary, self.flow_plugins, self.flow_plugins.keys()))
        result = InterfaceResult(result_data=None, log_data=None, payload=payload)
        result.result_data, result.log_data = flow_plugin.execute(payload)

        return result
