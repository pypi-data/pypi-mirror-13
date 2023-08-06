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
from collections import namedtuple, OrderedDict, Mapping
import os
import re

import fastr
from fastr import exceptions
from fastr.core.interface import Interface, InterfaceResult, InputSpec, OutputSpec
from fastr.core.baseplugin import BasePlugin
from fastr.core.pluginmanager import PluginManager
from fastr.core.serializable import Serializable
from fastr.datatypes import EnumType, TypeGroup, URLType


class CollectorPlugin(BasePlugin):
    """
    CollectorPlugins allow for Jobs to retrieve automatic outputs after
    execution. This can be via regexp matching, searching for files, or
    parsing the stdout of a job.
    """

    def __init__(self):
        """
        Constructor
        """
        super(CollectorPlugin, self).__init__()
        self.job = None

    @property
    def fullid(self):
        """
        The full id of the plugin
        """
        if self.job is not None:
            return 'fastr://plugins/collectorplugins/{}/{}'.format(self.id, self.job.jobid)
        else:
            return 'fastr://plugins/collectorplugins/{}'.format(self.id)

    def collect_results(self, interface, output, result):
        """
        Start the collection of the results. This method calls the actual
        implementation from the subclass (_collect_results) and wraps it
        with some convience functionality.

        :param interface: Job to collect data for
        :param output: Output to collect data for
        """
        self._collect_results(interface, output, result)

    @abstractmethod
    def _collect_results(self, job, output, result):
        """
        Placeholder method for the actual collection of the results. This
        method should implemented by subclasses.

        :param job: Job to collect data for
        :param output: Output to collect data for
        """
        pass

    def _regexp_path(self, path):
        """
        Helper function that searches for a regular expression in a path. There
        can be wildcards in any level of the path.

        :param path: path with regular expressions
        :return: list of paths that match the path pattern
        """
        # Get a clean, absolute path to work with
        path = os.path.expanduser(path)
        path = os.path.abspath(path)

        subpaths = self._full_split(path)
        if subpaths[0] != os.path.sep and not re.match(r'[a-zA-Z]:[/\\]', subpaths[0]):
            raise ValueError('path should always contain an absolute path (subpaths: {})'.format(subpaths))

        basepath = subpaths[0]

        pathlist = [basepath]
        fastr.log.debug('Basepath: {}'.format(basepath))
        for subpath in subpaths[1:]:
            subpath = '^' + subpath + '$'
            # Test the regexp and give a more understandable error if it fails
            try:
                re.compile(subpath)
            except Exception as detail:
                raise ValueError('Error parsing regexp "{}": {}'.format(subpath, detail))

            # Scan new level for matches
            newpathlist = []
            for curpath in pathlist:
                contents = os.listdir(curpath)
                for option in contents:
                    if re.match(subpath, option):
                        newpathlist.append(os.path.join(curpath, option))

            pathlist = newpathlist

        return pathlist

    @staticmethod
    def _full_split(urlpath):
        """
        Split an urls path completely into parts

        :param urlpath: path part of the url
        :return: a list of parts
        """
        parts = []
        while True:
            newpath, tail = os.path.split(urlpath)
            if newpath == urlpath:
                assert not tail
                if urlpath:
                    parts.append(urlpath)
                break
            parts.append(tail)
            urlpath = newpath
        parts.reverse()
        return parts


class CollectorPluginManager(PluginManager):
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
            path = fastr.config.collector_plugins_path

        super(CollectorPluginManager, self).__init__(path, recursive)

    @property
    def plugin_class(self):
        """
        The class of the Plugins in the collection
        """
        return CollectorPlugin

    @property
    def _instantiate(self):
        """
        Indicate that the plugins should instantiated before stored
        """
        return True

    def _store_item(self, name, value):
        """
        Store a CollectorPlugin in the CollectorPluginManager

        :param name: name of the CollectorPlugin
        :param value: the CollectorPlugin to store
        """
        self[value.id] = value


class HiddenFieldMap(Mapping):
    def __init__(self, *args, **kwargs):
        self._data = OrderedDict(*args, **kwargs)

    def __getitem__(self, item):
        return self._data[item]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for key, value in self._data.items():
            if not (hasattr(value, 'hidden') and value.hidden):
                yield key


class FastrInterface(Interface):
    """
    The default Interface for fastr. For the command-line Tools as used by
    fastr.
    """

    __dataschemafile__ = 'FastrInterface.schema.json'

    collectors = CollectorPluginManager()

    def __init__(self, id_, document):
        super(FastrInterface, self).__init__()

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

        #: List of input parameter descriptions
        self.input_map = OrderedDict()

        #: List of output parameter descriptions
        self.output_map = OrderedDict()

        # Parse input and output fields into parameter_description objects
        for n_order, input_ in enumerate(document['inputs']):
            self.input_map[input_['id']] = InputParameterDescription(self, input_, n_order)
        n_inputs = len(self.input_map)

        for n_order, output in enumerate(document['outputs']):
            self.output_map[output['id']] = OutputParameterDescription(self, output, n_order + n_inputs)

        # Create the inputs/outputs spec to expose to the rest of the system
        self._inputs = HiddenFieldMap((k, InputSpec(id=v.id,
                                                    cardinality=v.cardinality,
                                                    datatype=v.datatype,
                                                    required=v.required,
                                                    description=v.description,
                                                    default=v.default,
                                                    hidden=v.hidden)) for k, v in self.input_map.items())

        self._outputs = HiddenFieldMap((k, OutputSpec(id=v.id,
                                                      cardinality=v.cardinality,
                                                      datatype=v.datatype,
                                                      automatic=v.automatic,
                                                      required=v.required,
                                                      description=v.description,
                                                      hidden=v.hidden)) for k, v in self.output_map.items())

    def __eq__(self, other):
        if not isinstance(other, FastrInterface):
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
            'inputs': [x.__getstate__() for x in self.input_map.values()],
            'outputs': [x.__getstate__() for x in self.output_map.values()],
        }

        return state

    def __setstate__(self, state):
        """
        Set the state of the Interface
        """
        self.id = state['id']

        self.input_map = OrderedDict((x['id'], InputParameterDescription.createobj(x)) for x in state['inputs'])
        self.output_map = OrderedDict((x['id'], InputParameterDescription.createobj(x)) for x in state['outputs'])

        # Create the inputs/outputs spec to expose to the rest of the system
        self._inputs = HiddenFieldMap((k, InputSpec(id=v.id,
                                                    cardinality=v.cardinality,
                                                    datatype=v.datatype,
                                                    required=v.required,
                                                    description=v.description,
                                                    default=v.default,
                                                    hidden=v.hidden)) for k, v in self.input_map.items())

        self._outputs = HiddenFieldMap((k, OutputSpec(id=v.id,
                                                      cardinality=v.cardinality,
                                                      datatype=v.datatype,
                                                      automatic=v.automatic,
                                                      required=v.required,
                                                      description=v.description,
                                                      hidden=v.hidden)) for k, v in self.output_map.items())

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    def expanding(self):
        return 0

    def execute(self, target, payload):
        """
        Execute the interface using a specific target and payload (containing
        a set of values for the arguments)

        :param target: the target to use
        :type target: :py:class:`SampleId <fastr.core.target.Target>`
        :param dict payload: the values for the arguments
        :return: result of the execution
        :rtype: InterfaceResult
        """
        fastr.log.info('Execution payload: {}'.format(payload))
        command = [target.binary] + self.get_arguments(payload)
        log_data = target.run_command(command)

        result = InterfaceResult(result_data={}, log_data=log_data, payload=payload)
        # TODO: add the collection of results and log store here
        fastr.log.info('Collecting results')
        for output in self.outputs.values():
            if not output.automatic:
                result.result_data[output.id] = payload['outputs'][output.id]
        try:
            self.collect_results(result)
        except exceptions.FastrError:
            fastr.log.error('Encountered an error when collecting the results')
            raise

        return result

    def check_input_id(self, id_):
        """
        Check if an id for an object is valid and unused in the Tool. The
        method will always returns True if it does not raise an exception.

        :param str id_: the id to check
        :return: True
        :raises FastrValueError: if the id is not correctly formatted
        :raises FastrValueError: if the id is already in use
        """

        regex = r'^\w[\w\d_]*$'
        if re.match(regex, id_) is None:
            raise exceptions.FastrValueError('An id in Fastr should follow'
                                             ' the following pattern {}'
                                             ' (found {})'.format(regex, id_))

        if id_ in self.input_map:
            raise exceptions.FastrValueError('The id {} is already in use in {}!'.format(id_, self.id))

        return True

    def check_output_id(self, id_):
        """
        Check if an id for an object is valid and unused in the Tool. The
        method will always returns True if it does not raise an exception.

        :param str id_: the id to check
        :return: True
        :raises FastrValueError: if the id is not correctly formatted
        :raises FastrValueError: if the id is already in use
        """

        regex = r'^\w[\w\d_]*$'
        if re.match(regex, id_) is None:
            raise exceptions.FastrValueError('An id in Fastr should follow'
                                             ' the following pattern {}'
                                             ' (found {})'.format(regex, id_))

        if id_ in self.output_map:
            raise exceptions.FastrValueError('The id {} is already in use in {}!'.format(id_, self.id))

        return True

    def get_arguments(self, values):
        """
        Get the argument list for this interface

        :return: return list of arguments
        """
        # Get the argument list
        arguments = self.input_map.values() + self.output_map.values()
        arguments = sorted(arguments, key=lambda x: x.order)

        argument_list = []

        for argument in arguments:
            id_ = argument.id

            try:
                if isinstance(argument, InputParameterDescription):
                    value = values['inputs']
                    value = value[id_]
                else:
                    value = values['outputs']
                    value = value[id_]


                # TODO: check if this works!
                #if len(value) != argument.cardinality:
                #    raise exceptions.FastrValueError('Cardinality of argument {} has an incorrect cardinality (expected {} ({}), found {})'.format(argument.id,
                #                                                                                                                                   argument.cardinality,
                #                                                                                                                                   type(argument.cardinality).__name__,
                #                                                                                                                                   len(value)))
            except KeyError:
                if argument.default is not None:
                    value = argument.default
                elif argument.required:
                    raise exceptions.FastrValueError('Required argument "{}" has no value!'.format(argument.id))
                else:
                    value = None

            if value is not None:
                argument_list.extend(argument.get_commandline_argument(value))

        return argument_list

    def collect_results(self, result):
        """
        Collect all results of the interface
        """
        for output in self.output_map.values():
            if output.automatic:
                collector = self.collectors[output.method]
                collector.collect_results(self, output, result)

                fastr.log.debug('--= Collected automatic result for {} =--'.format(output.id))
                fastr.log.debug(result.result_data[output.id])

    def get_specials(self, payload, output, cardinality_nr):
        """
        Get special attributes. Returns tuples for specials, inputs and outputs
        that are used for formatting substitutions.

        :param output: Output for which to get the specials
        :param int cardinality_nr: the cardinality number
        """
        if output is not None:
            datatype = fastr.typelist[output.datatype]
            # Get extension match
            if issubclass(datatype, URLType):
                extension = datatype.extension
            elif issubclass(datatype, TypeGroup):
                extensions = set()
                for member in datatype.members:
                    extensions.add(member.extension if member.extension is not None else '')
                extension = '({})'.format('|'.join(extensions))
            else:
                extension = ''
        else:
            extension = ''

        specials_tuple_type = namedtuple('Specials', ['cardinality', 'extension'])
        specials = specials_tuple_type(cardinality_nr, extension)

        if len(self.input_map) > 0:
            inputs_tuple_type = namedtuple('Inputs', [x.id for x in self.input_map.values()])
            inputs = inputs_tuple_type(*[payload['inputs'][x.id] if x.id in payload['inputs'] else x.default for x in self.input_map.values()])
        else:
            inputs = ()

        output_arguments = [x for x in self.output_map.values() if not x.automatic]
        if len(output_arguments) > 0:
            outputs_tuple_type = namedtuple('Outputs', [x.id for x in self.output_map.values()])
            outputs = outputs_tuple_type(*[payload['outputs'][x.id] if x.id in payload['outputs'] else x.default for x in self.output_map.values()])
        else:
            outputs = ()

        return specials, inputs, outputs


class ParameterDescription(Serializable):
    """
    Description of an input or output parameter used by a Tool. This is the
    super class for both input and output, containing the shared parts.
    """
    _IS_INPUT = False

    def __init__(self, parent, element, order=0):
        """
        Instantiate a ParameterDescription

        :param Tool parent: parent tool
        :param dict element: description of the parameter
        :param order: the order in which the parameter was defined in the file
        """
        self.parent = parent

        if isinstance(element, dict):
            self.id = element['id']
            self.name = element['name']

            if 'datatype' in element:
                self.datatype = element['datatype']
            elif 'enum' in element:
                self.datatype = '__{}__{}__Enum__'.format(parent.id, self.id)
                fastr.typelist.create_enumtype(self.datatype, tuple(element['enum']), self.datatype)
            else:
                raise exceptions.FastrValueError('No valid datatype defined for {}'.format(self.id))

            self.prefix = element.get('prefix', None)
            self.repeat_prefix = element.get('repeat_prefix', False)
            self.cardinality = element.get('cardinality', 1)
            self.nospace = element.get('nospace', False)
            self.format = element.get('format', None)
            self.required = element.get('required', True)
            self.default = element.get('default', None)
            self.description = element.get('description', '')
            self.order = element.get('order', order)
            self.hidden = element.get('hidden', False)
        else:
            raise exceptions.FastrTypeError('element should be a dict')

    def __eq__(self, other):
        """
        Compare two ParameterDescription instance with eachother. This
        function helps ignores the parent, but once tests the values for
        equality

        :param other: the other instances to compare to

        :returns: True if equal, False otherwise
        """
        if not isinstance(other, ParameterDescription):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['parent']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['parent']

        return dict_self == dict_other

    def __getstate__(self):
        """
        Retrieve the state of the ParameterDescription

        :return: the state of the object
        :rtype dict:
        """
        state = {k: v for k, v in self.__dict__.items()}
        state['parent'] = self.parent.id

        datatype = fastr.typelist[self.datatype]
        if issubclass(datatype, EnumType):
            del state['datatype']
            state['enum'] = datatype.options

        return state

    def __setstate__(self, state):
        """
        Set the state of the ParameterDescription by the given state.

        :param dict state: The state to populate the object with
        """
        if 'datatype' not in state:
            if 'enum' in state:
                typename = '__{}__{}__Enum__'.format(state['parent'], state['id'])
                state['datatype'] = typename
                fastr.typelist.create_enumtype(typename, tuple(state['enum']), typename)
            else:
                raise exceptions.FastrValueError('No valid datatype defined for {} in {}'.format(state['id'], state))

        self.__dict__.update(state)

    def get_commandline_argument(self, value):
        """
        Get the commandline argument for this Parameter given the values
        assigned to it.

        :param value: the value(s) for this input
        :return: commandline arguments
        :rtype: list
        """
        argument = []
        if isinstance(value, tuple):
            for cardinality_nr, value in enumerate(value):
                value = self.format_argument_value(value)
                argument.extend(self.format_prefix(value, cardinality_nr))

        elif isinstance(value, OrderedDict):
            for cardinality_nr, (key, value) in enumerate(value.items()):
                value = ','.join(self.format_argument_value(x) for x in value if x is not None)
                argument.extend(self.format_prefix('{}={}'.format(key, value), cardinality_nr))
        else:
            raise exceptions.FastrTypeError('Argument should be tuple or OrderedDict!')

        return argument

    def format_prefix(self, value, cardinality_nr):
        extra_argument = []

        if cardinality_nr == 0 or self.repeat_prefix:
            if self.prefix is not None and self.prefix.strip() != '':
                prefix = self.prefix.replace('#', str(cardinality_nr))
                if not self.nospace or value is None:
                    extra_argument.append(prefix)

        if value is not None:
            if self.nospace:
                extra_argument.append('{}{}'.format(self.prefix, value))
            else:
                extra_argument.append(value)

        return extra_argument

    def format_argument_value(self, value):
        datatype = fastr.typelist[self.datatype]

        if not datatype.isinstance(value):
            fastr.log.info('CREATING DATATYPE {!r} for {!r}!'.format(datatype, value))
            value = datatype(value)

        # Format (and validate if required) the input value
        value.format = self.format
        if self._IS_INPUT and not value.valid:
            fastr.log.info('SELF TYPE: {}, ID {}'.format(type(self).__name__, self.id))
            raise exceptions.FastrDataTypeValueError('Value for input {} not a valid instance of type {} (value: {} ({} / {!r}) -> {})'.format(self.id, datatype.id, value, type(value).__name__, value.value, value.valid))

        value = str(value)

        # Filter out boolean flags
        if not value.startswith('__FASTR_FLAG__'):
            return value
        else:
            return None


class InputParameterDescription(ParameterDescription):
    """
    Description of an input parameter used by a Tool.
    """
    _IS_INPUT = True

    def __init__(self, parent, element, order=0):
        """
        Instantiate an InputParameterDescription

        :param Tool parent: parent tool
        :param dict element: description of the parameter
        :param order: the order in which the parameter was defined in the file
        """
        if isinstance(element, dict):
            super(InputParameterDescription, self).__init__(parent, element, order)
            self.parent.check_input_id(element['id'])
        else:
            raise exceptions.FastrTypeError('element should be a dict')


class OutputParameterDescription(ParameterDescription):
    """
    Description of a output parameter used by a Tool.
    """
    def __init__(self, parent, element, order=0):
        """
        Instantiate an OutputParameterDescription

        :param Tool parent: parent tool
        :param dict element: description of the parameter
        :param order: the order in which the parameter was defined in the file
        """
        if isinstance(element, dict):
            super(OutputParameterDescription, self).__init__(parent, element, order)
            self.parent.check_output_id(element['id'])
            self.automatic = element.get('automatic', False)
            self.action = element.get('action', None)
            self.location = element.get('location', None)
            self.separator = element.get('separator', None)
            if self.automatic:
                self.method = element.get('method', 'path')
            else:
                self.method = element.get('method', None)
        else:
            raise exceptions.FastrTypeError('element should be a dict')

    def __setstate__(self, state):
        """
        Set the state of the OutputParameterDescription by the given state.

        :param dict state: The state to populate the object with
        """
        if 'location' not in state:
            state['location'] = None

        if 'separator' not in state:
            state['separator'] = None

        if 'method' not in state:
            if 'automatic' not in state or not state['automatic']:
                state['method'] = None
            else:
                state['method'] = 'path'

        if 'action' not in state:
            state['action'] = None

    def get_commandline_argument(self, values):
        """
        Get the commandline argument for this Parameter given the values
        assigned to it.

        :param value: the value(s) for this input
        :return: commandline arguments
        :rtype: list
        """
        if self.action is not None:
            if self.action in self.ACTIONS:
                action_func = self.ACTIONS[self.action]
                for value in values:
                    fastr.log.info('Calling action {} for {}'.format(action_func, value))
                    action_func(self, value)

        if not self.automatic:
            return super(OutputParameterDescription, self).get_commandline_argument(values)
        else:
            return []

    def mkdirs(self, value):
        """
        Create the directory if it does not yet exist

        :param URLType value: the directory to create
        """
        value = str(value)
        if not os.path.exists(value):
            os.makedirs(value)

    ACTIONS = {'ensure': mkdirs,
               'mkdir': mkdirs}
