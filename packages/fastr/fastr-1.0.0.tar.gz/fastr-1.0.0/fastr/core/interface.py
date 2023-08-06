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
A module that describes the interface of a Tool. It specifies how a set of
 input values will be translated to commands to be executed. This creates
 a generic interface to different ways of executing underlying software.
"""

from abc import ABCMeta, abstractmethod, abstractproperty
from collections import namedtuple

import fastr
from fastr import exceptions
from fastr.core.baseplugin import BasePlugin
from fastr.core.pluginmanager import PluginManager
from fastr.core.serializable import Serializable


# Simple containers for minial fields for the input and output specification
InputSpec = namedtuple('InputSpec', ['id', 'cardinality', 'datatype', 'required', 'description', 'default', 'hidden'])
OutputSpec = namedtuple('OutputSpec', ['id', 'cardinality', 'datatype', 'automatic', 'required', 'description', 'hidden'])


class Interface(BasePlugin, Serializable):

    """
    Abstract base class of all Interfaces. Defines the minimal requirements for
    all Interface implementations.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, target, payload):
        """
        Execute the interface given the a target and payload. The payload
        should have the form {'input': {'input_id_a': (value, value), 'input_id_b': (value, value)}, 'output': {'output_id_a': (value, value), 'output_id_b': (value, value)}}

        :param target: the target to call
        :param payload: the payload to use
        :returns: the result of the execution
        :rtype: (tuple of) InterfaceResult
        """
        pass

    @abstractproperty
    def expanding(self):
        """
        Indicates whether or not this Interface will result in multiple samples
        per run. If the flow is unaffected, this will be zero, if it is nonzero
        it means that number of dimension will be added to the sample array.
        """
        pass

    @abstractproperty
    def inputs(self):
        """
        OrderedDict of Inputs connected to the Interface. The format should be
        {input_id: InputSpec}.
        """
        pass

    @abstractproperty
    def outputs(self):
        """
        OrderedDict of Output connected to the Interface. The format should be
        {output_id: OutputSpec}.
        """
        pass

    @abstractmethod
    def __getstate__(self):
        """
        Retrieve the state of the Interface

        :return: the state of the object
        :rtype dict:
        """
        raise NotImplementedError()

    @abstractmethod
    def __setstate__(self, state):
        """
        Set the state of the Interface
        """
        raise NotImplementedError()

    @classmethod
    def test(cls):
        """
        Test the plugin, interfaces do not need to be tested on import
        """
        pass


class InterfaceResult(object):
    """
    The class in which Interfaces should wrap their results to be picked up by fastr
    """
    def __init__(self, result_data, log_data, payload, sample_index=None, sample_id=None):
        if ((sample_index is None and sample_id is not None) or
           (sample_index is not None and sample_id is None)):
            raise exceptions.FastrValueError('An InterfaceResult needs both'
                                             ' sample_index and sample_id to'
                                             ' be set or neither of them set.')

        self.sample_index = sample_index
        self.sample_id = sample_id
        self.result_data = result_data
        self.log_data = log_data
        self.payload = payload


class InterfacePluginManager(PluginManager):
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
            path = fastr.config.interface_plugins_path

        super(InterfacePluginManager, self).__init__(path, recursive)

    @property
    def plugin_class(self):
        """
        The class of the Plugins in the collection
        """
        return Interface

    @property
    def _instantiate(self):
        """
        Indicate that the plugins should instantiated before stored
        """
        return False
