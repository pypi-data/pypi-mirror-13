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
Classes for arranging the input and output for nodes.

Exported classes:

Input -- An input for a node (holding datatype).
Output -- The output of a node (holding datatype and value).
ConstantOutput -- The output of a node (holding datatype and value).

.. warning::
   Don't mess with the Link, Input and Output internals from other places.
   There will be a huge chances of breaking the network functionality!
"""
import itertools
import re
from abc import abstractmethod, abstractproperty
from collections import OrderedDict

import sympy

import fastr
from fastr.core.datatypemanager import typelist
from fastr.core.samples import HasSamples, SampleItem, SampleId, SampleIndex, SampleValue, SampleCollection
from fastr.core.interface import InputSpec, OutputSpec
from fastr.core.updateable import Updateable
from fastr.core.serializable import Serializable
from fastr.datatypes import DataType
import fastr.exceptions as exceptions
from fastr.utils.dicteq import dicteq


class BaseInputOutput(HasSamples, Updateable, Serializable):

    """
    Base class for Input and Output classes. It mainly implements the
    properties to access the data from the underlying ParameterDescription.
    """

    def __init__(self, node, description):
        """Instantiate a BaseInputOutput

        :param node: the parent node the input/output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the input/output.
        :return: created BaseInputOutput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        super(BaseInputOutput, self).__init__()

        self._node = node

        # Get DataType
        if description.datatype in typelist:
            self._description = description
            self._datatype = typelist[description.datatype]

            # Create a validator for the cardinality
            self.cardinality_spec = self._create_cardinality_spec(description.cardinality)
        else:
            raise exceptions.FastrDataTypeNotAvailableError('DataType {} does not exist'.format(description.datatype))

    def __iter__(self):
        """
        This function is blocked to avoid support for iteration using a lecacy __getitem__ method.

        :return: None
        :raises FastrNotImplementedError: always
        """
        raise exceptions.FastrNotImplementedError('Not iterable, this function is to block legacy iteration using getitem')

    def __getstate__(self):
        """
        Retrieve the state of the BaseInputOutput

        :return: the state of the object
        :rtype dict:
        """
        state = super(BaseInputOutput, self).__getstate__()
        state['id'] = self.id
        state['datatype'] = self.datatype.id
        return state

    def __setstate__(self, state):
        """
        Set the state of the BaseInputOutput by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(BaseInputOutput, self).__setstate__(state)

        if 'datatype' in state:
            self._datatype = fastr.typelist[state['datatype']]

        self.cardinality_spec = self._create_cardinality_spec(self.description.cardinality)

    def __repr__(self):
        """
        Get a string representation for the Input/Output

        :return: the string representation
        :rtype: str
        """
        return '<{}: {}>'.format(type(self).__name__, self.fullid)


    @property
    def datatype(self):
        """
        The datatype of this Input/Output
        """
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        """
        The datatype of this Input/Output (setter)
        """
        self._datatype = value

    @property
    def description(self):
        """
        The description object of this input/output
        """
        return self._description

    def cardinality(self, key=None, job_data=None):
        """
        Determine the cardinality of this Input/Output. Optionally a key can be
        given to determine for a sample.

        :param key: key for a specific sample
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """

        # We need to key for the signature in subclasses, shut pylint up
        # pylint: disable=unused-argument,no-self-use

        raise exceptions.FastrNotImplementedError('Purposefully not implemented')

    @property
    def id(self):
        """
        Id of the Input/Output
        """
        return self._description.id

    @property
    def node(self):
        """
        The Node to which this Input/Output belongs
        """
        return self._node

    @property
    def numel(self):
        """
        The number of elements in this Input/Output
        """
        numel = 1
        for size_elem in self.size:
            numel *= size_elem
        return numel

    @property
    def required(self):
        """
        Flag indicating that the Input/Output is required
        """
        return self._description.required

    @abstractproperty
    def size(self):
        """
        The size of the Input/Output
        """
        raise exceptions.FastrNotImplementedError('Purposefully not implemented')

    @abstractproperty
    def fullid(self):
        """
        The fullid of the Input/Output, the fullid should be unnique and
        makes the object retrievable by the network.
        """
        raise exceptions.FastrNotImplementedError('Purposefully not implemented')

    def check_cardinality(self, key=None):
        """
        Check if the actual cardinality matches the cardinality specified in
        the ParameterDescription. Optionally you can use a key to test for a
        specific sample.

        :param key: sample_index (tuple of int) or
                    :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                    for desired sample
        :return: flag indicating that the cardinality is correct
        :rtype: bool
        :raises FastrCardinalityError: if the Input/Output has an incorrect
                cardinality description.
        """
        spec = self.cardinality_spec
        cardinality = self.cardinality(key)

        fastr.log.debug('Cardinality: {} (type {})'.format(cardinality, type(cardinality).__name__))
        if isinstance(cardinality, sympy.Symbol):
            fastr.log.debug('A symbol cardinality cannot be checked a priori!')
            return True

        if spec[0] == 'any':
            return True
        elif spec[0] == 'min':
            return cardinality >= spec[1]
        elif spec[0] == 'max':
            return cardinality <= spec[1]
        elif spec[0] == 'int':
            return cardinality == spec[1]
        elif spec[0] == 'range':
            return cardinality >= spec[1] and cardinality <= spec[2]
        elif spec[0] == 'as':
            return cardinality == self.node.inputs[spec[1]].cardinality(key)
        elif spec[0] == 'val':
            fastr.log.warning('Value cardinality specification cannot be checked a priori!')
            return True
        elif spec[0] == 'unknown':
            fastr.log.warning('Value cardinality specification cannot be checked a priori!')
            return True
        else:
            raise exceptions.FastrCardinalityError('Invalid cardinality specification ({})'.format(spec))

    @staticmethod
    def _create_cardinality_spec(desc):
        """
        Create simplified description of the cardinality. This changes the
        string representation to a tuple that is easier to check at a later
        time.

        :param str desc: the string version of the cardinality
        :return: the simplified cardinality description
        :rtype: tuple
        :raises FastrCardinalityError: if the Input/Output has an incorrect
                cardinality description.

        The translation works with the following table:

        ==================== ============================= ===============================================================
        cardinality string   cardinality spec              description
        ==================== ============================= ===============================================================
        ``"*"``              ``('any',)                    Any cardinality is allowed
        ``"N"``              ``('int', N)``                A cardinality of N is required
        ``"N-M"``            ``('range', N, M)``           A cardinality between N and M is required
        ``"*-M"``            ``('max', M)``                A cardinality of maximal M is required
        ``"N-*"``            ``('min', N)``                A cardinality of minimal N is required
        ``"[M,N,...,O,P]"``  ``('choice', [M,N,...,O,P])`` The cardinality should one of the given options
        ``"as:input_id"``    ``('as', 'input_id')``        The cardinality should match the cardinality of the given Input
        ``"val:input_id"``   ``('val', 'input_id')``       The cardinliaty should match the value of the given Input
        ==================== ============================= ===============================================================
        """

        if isinstance(desc, int) or re.match(r'^\d+$', desc) is not None:
            # N
            cardinality_spec = ('int', int(desc))
        elif desc == '*':
            # * (anything is okay)
            cardinality_spec = ('any',)
        elif re.match(r'^\[\d+(,\d+)*\]', desc) is not None:
            # [M,N,..,O,P]
            cardinality_spec = ('choice', tuple(int(x) for x in desc[1:-1].split(',')))
        elif '-' in desc:
            match = re.match(r'^(\d+|\*)-(\d+|\*)$', desc)
            if match is None:
                raise exceptions.FastrCardinalityError("Not a valid cardinality description string (" + desc + ")")

            lower, upper = match.groups()

            if lower == '*' and upper == '*':
                # *-* (anything is okay)
                cardinality_spec = ('any',)
            elif lower == '*' and upper != '*':
                # N-*
                cardinality_spec = ('max', int(upper))
            elif lower != '*' and upper == '*':
                # *-M
                cardinality_spec = ('min', int(lower))
            else:
                # N-M
                cardinality_spec = ('range', int(lower), int(upper))

        elif desc.startswith("as:"):
            # as:other
            field = desc[3:]
            cardinality_spec = ('as', field)
        elif desc.startswith("val:"):
            # val:other
            field = desc[5:]
            cardinality_spec = ('val', field)
        elif desc == 'unknown':
            cardinality_spec = ('unknown',)
        else:
            raise exceptions.FastrCardinalityError("Not a valid cardinality description string (" + desc + ")")

        return cardinality_spec


class BaseInput(BaseInputOutput):
    """
    Base class for all inputs.
    """

    def __init__(self, node, description):
        """
        Instantiate a BaseInput

        :param node: the parent node the input/output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
                            describing the input/output.
        :return: the created BaseInput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        if not isinstance(description, InputSpec):
            fastr.log.error('Description has type "{}" (must be ParameterDescription)'.format(type(description).__name__))
            raise exceptions.FastrTypeError('An input must be constructed based on an '
                                            'object of a class derived from Node and an '
                                            'object of class InputSpec')

        super(BaseInput, self).__init__(node, description)

    @abstractproperty
    def num_subinput(self):
        """
        The number of SubInputs in this Input
        """
        raise exceptions.FastrNotImplementedError('Purposefully not implemented')

    @abstractmethod
    def itersubinputs(self):
        """
        Iterator over the SubInputs

        :return: iterator

        example:

        .. code-block:: python

          >>> for subinput in input_a.itersubinputs():
                  print subinput

        """
        raise exceptions.FastrNotImplementedError('Purposefully not implemented')


class Input(BaseInput):
    """
    Class representing an input of a node. Such an input will be connected
    to the output of another node or the output of an constant node to provide
    the input value.
    """

    def __init__(self, node, description):
        """
        Instantiate an input.

        :param node: the parent node of this input.
        :type node: :py:class:`Node <fastr.core.node.Node>`
        :param ParameterDescription description: the ParameterDescription of the input.
        :return: the created Input
        """
        self._source = {}
        super(Input, self).__init__(node, description)
        self._input_group = 'default'

    def __eq__(self, other):
        """Compare two Input instances with each other. This function ignores
        the parent node and update status, but tests rest of the dict for equality.

        :param other: the other instances to compare to
        :type other: :py:class:`Input <fastr.core.inputoutput.Input>`
        :returns: True if equal, False otherwise
        :rtype: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['_node']
        del dict_self['_status']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['_node']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

    def __getstate__(self):
        """
        Retrieve the state of the Input

        :return: the state of the object
        :rtype dict:
        """
        state = super(Input, self).__getstate__()
        state['input_group'] = self.input_group

        return state

    def __setstate__(self, state):
        """
        Set the state of the Input by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(Input, self).__setstate__(state)
        self._input_group = state['input_group']

    def __getitem__(self, key):
        """
        Retrieve an item from this Input.

        :param key: the key of the requested item, can be a key str, sample
                    index tuple or a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :type key: str, :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` or tuple
        :return: the return value depends on the requested key. If the key was
                 an int the corresponding :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                 will be returned. If the key was a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                 or sample index tuple, the corresponding
                 :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned.
        :rtype: :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` or
                :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :raises FastrTypeError: if key is not of a valid type
        :raises FastrKeyError: if the key is not found
        """
        if not isinstance(key, (int, str, SampleId, SampleIndex)):
            raise exceptions.FastrTypeError('MappedInput indices must a int, str, SampleId or '
                                            'SampleIndex, not {}'.format(type(key).__name__))

        if isinstance(key, (SampleId, SampleIndex)):
            data = []
            # Create mapping items of key; value and combine those
            self_size = self.size
            for subindex_key, sub in self.source.items():
                # Allow the same mixing of parts of a mapped input as in input groups
                if sub.size == self_size:
                    value = sub[key]
                    value = SampleItem(value.index, value.id, value.data, value.jobs)
                elif sub.size == (1,):
                    value = sub[SampleIndex(0)]
                    value = SampleItem(value.index, value.id, value.data, value.jobs)
                elif sub.size == (0,) or sub.size == ():
                    value = SampleItem(SampleIndex(0), '__EMPTY__', SampleValue(), set())
                else:
                    raise exceptions.FastrSizeMismatchError('MappedInput has inconsistent size/dimension'
                                                            ' info for (sub)Input {}'.format(sub.fullid))
                data.append(SampleItem(value.index, value.id, {subindex_key: tuple(value.data.sequence_part())}, value.jobs))

            combination = SampleItem.combine(data)
            return combination

        if key not in self.source:
            # This is to allow for linking against inputs['key'][0]
            try:
                key = int(key)
            except ValueError:
                pass  # No problem, just go for the str
            sub_input = SubInput(self)
            self.source[key] = sub_input
            return sub_input
        else:
            return self.source[key]

    def __setitem__(self, key, value):
        """
        Create a link between a SubInput of this Inputs and an Output/Constant

        :param key: the key of the SubInput
        :type key: int, str
        :param value: the target to link, can be an output or a value to create a constant for
        :type value: BaseOutput, list, tuple, dict, OrderedDict
        :raises FastrTypeError: if key is not of a valid type
        """
        if not isinstance(key, (int, str)):
            raise exceptions.FastrTypeError('The key of an SubInput to set should be an '
                                            'int or str (found {})'.format(type(key).__name__))

        if key not in self.source:
            subin = Input(self.node, self.description)
            self.source[key] = subin

        if isinstance(value, BaseOutput):
            if self[key].node.parent is not value.node.parent:
                message = 'Cannot create links between members of different Network'
                fastr.log.warning(message)

            network = value.node.parent
            if network is None:
                message = 'Cannot create links between non-network-attached Nodes'
                fastr.log.warning(message)
            else:
                fastr.log.debug('Linking {} to {}'.format(value.fullid, self[key].fullid))
                network.create_link(value, self[key])
        elif isinstance(value, (list, tuple, dict, OrderedDict)):
            # This is data for a ConstantNode, so create one and set it
            # First make sure the stepid of the new ConstantNode will match the stepid of the current Node
            for k, i in self.node.parent.stepids.items():
                if self.node in i:
                    stepid = k
                    break
            else:
                stepid = None
            network = self.node.parent
            const_node = network.create_constant(datatype=self.datatype, data=value, id_='{}__{}__{}_const'.format(self.node.id, self.id, key), stepid=stepid)
            network.create_link(const_node.output, self[key])

        else:
            message = 'Cannot add object of type {} to MappedInput'.format(type(value).__name__)
            fastr.log.critical(message)
            raise exceptions.FastrTypeError(message)

    def __str__(self):
        """
        Get a string version for the Input

        :return: the string version
        :rtype: str
        """
        return '<Input: {} ({})>'.format(self.fullid, self.id)

    def cardinality(self, key=None, job_data=None):
        """
        Cardinality for an Input is the sum the cardinalities of the SubInputs,
        unless defined otherwise.

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """

        cardinality = 0

        for subinput in self.source.values():
            cardinality += subinput.cardinality(key, job_data)

        return cardinality

    def remove(self, value):
        """
        Remove a SubInput from the SubInputs list.

        :param value: the :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                      to removed from this Input
        :type value: :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        """
        for key, val in self.source.items():
            if value is val:
                self._source.pop(key)

    @property
    def datatype(self):
        """
        The datatype of this Input
        """
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        # This does not differ, as it is a property
        # pylint: disable=arguments-differ
        self._datatype = value
        for subinput in self.itersubinputs():
            subinput.datatype = value

    @property
    def dimnames(self):
        """
        The list names of the dimensions in this Input. This will be a list of str.
        """
        subinputs = [sub for sub in self.itersubinputs()]
        sizes = [sub.size for sub in subinputs]

        unique_sizes = set(sizes) - {(0,), (1,), ()}

        if len(unique_sizes) > 1:
            nr_non_symbolic_sizes = sum(not all(isinstance(x, sympy.Symbol) for x in size) for size in unique_sizes)

            if nr_non_symbolic_sizes == 0:
                return subinputs[sizes.index(unique_sizes.pop())].dimnames

            raise exceptions.FastrSizeMismatchError('Cannot determine dimnames: sizes of SubInputs do not match!')
        elif len(unique_sizes) == 1:
            return subinputs[sizes.index(unique_sizes.pop())].dimnames
        elif (1,) in sizes:
            return subinputs[sizes.index((1,))].dimnames
        elif (0,) in sizes:
            return subinputs[sizes.index((0,))].dimnames
        else:
            return []

    @property
    def fullid(self):
        """
        The full defining ID for the Input
        """
        if self.node is not None:
            return '{}/inputs/{}'.format(self.node.fullid, self.id)
        else:
            return 'fastr://ORPHANED/inputs/{}'.format(self.id)

    @property
    def input_group(self):
        """
        The id of the :py:class:`InputGroup <fastr.core.node.InputGroup>` this
        Input belongs to.
        """
        return self._input_group

    @input_group.setter
    def input_group(self, value):
        """
        The id of the :py:class:`InputGroup <fastr.core.node.InputGroup>` this
        Input belongs to. (setter)
        """
        self._input_group = value
        self.node.update_inputgroups()

    @property
    def num_subinput(self):
        """
        The number of SubInputs in this Input
        """
        return len(self._source)

    @property
    def size(self):
        """
        The size of the sample collections that can accessed via this Input.
        """
        sizes = set([subinput.size for subinput in self.itersubinputs()])
        unique_sizes = set(sizes) - set([(0,), (1,)])

        if len(unique_sizes) > 1:
            nr_non_symbolic_sizes = sum(not all(isinstance(x, sympy.Symbol) for x in size) for size in unique_sizes)

            if nr_non_symbolic_sizes == 0:
                return unique_sizes.pop()

            size_map = {x.source_output.id: x.size for x in self.itersubinputs()}
            message = 'Conflicting sizes of SubInputs ({})  {}, full size map: {}'.format(unique_sizes, nr_non_symbolic_sizes, size_map)
            fastr.log.error(message)
            raise exceptions.FastrSizeMismatchError(message)
        elif len(unique_sizes) == 1:
            return unique_sizes.pop()
        elif (1,) in sizes:
            return (1,)
        else:
            return ()

    @property
    def source(self):
        """
        The mapping of :py:class:`SubInputs <fastr.core.inputoutput.SubInput>`
        that are connected and have more than 0 elements.
        """
        return self._source

    @source.setter
    def source(self, value):
        """
        The list of :py:class:`SubInputs <fastr.core.inputoutput.SubInput>`
        that are connected and have more than 0 elements. (setter)
        """
        for src in self._source.values():
            src._source.destroy()

        self._source = {0: SubInput(self)}
        self._source[0].source = value

    def get_subinput(self, key):
        """
        Get a requested :py:class:`SubInput <fastr.core.inputoutput.SubInput>`

        :param int key: the index of the :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                        to retrieve
        :return: requested :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        """
        if not isinstance(key, int):
            raise exceptions.FastrTypeError('Input indices must be integers, not {}'.format(type(key).__name__))

        if key >= len(self.source) or key < 0:
            raise exceptions.FastrIndexError('Input index out of range')

        return self.source[key]

    def set_subinput(self, key, value):
        """
        Set a specified SubInput.

        :param int key: positive integer for position in _source list
        :param value: new :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                      to assign to the selected location
        """
        if not isinstance(key, int):
            raise exceptions.FastrTypeError('Input indices must be integers, not {}'.format(type(key).__name__))

        if key >= len(self.source) or key < 0:
            raise exceptions.FastrIndexError('Input index out of range')

        if not isinstance(value, SubInput):
            raise exceptions.FastrTypeError('Value should be a SubInput')

        self.source[key] = value

    def get_sourced_nodes(self):
        """
        Get a list of all :py:class:`Nodes <fastr.core.node.Node>` connected as sources to this Input

        :return: list of all connected :py:class:`Nodes <fastr.core.node.Node>`
        :rtype: list
        """
        return list(set(n for subinput in self.itersubinputs() for n in subinput.get_sourced_nodes()))

    def get_sourced_outputs(self):
        """
        Get a list of all :py:class:`Outputs <fastr.core.inputoutput.Output>` connected as sources to this Input

        :return: tuple of all connected :py:class:`Outputs <fastr.core.inputoutput.Output>`
        :rtype: tuple
        """
        return tuple(n for subinput in self.itersubinputs() for n in subinput.get_sourced_outputs())

    def index(self, value):
        """
        Find index of a SubInput

        :param value: the :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                      to find the index of
        :type value: :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :return: key
        :rtype: int, str
        """
        for key, val in self.source.items():
            if val is value:
                return key
        else:
            return None

    def remove(self, value):
        """
        Remove a SubInput from the SubInputs list based on the connected Link.

        :param value: the :py:class:`SubInput <fastr.core.link.Link>`
                      to removed from this Input
        :type value: :py:class:`SubInput <fastr.core.link.Link>`, <fastr.core.inputoutput.SubInput>`
        """
        for key in self.source.keys():
            subinput = self.get_subinput(key)
            if subinput is value:
                self.source.pop(key)

            subinput_source = subinput.source
            if len(subinput_source) == 1 and subinput_source[0] is value:
                self.source.pop(key)

    def insert(self, index):
        """
        Insert a new SubInput at index in the sources list

        :param int key: positive integer for position in _source list to insert to
        :return: newly inserted :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :rtype: :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        """
        newsub = SubInput(self)
        self.source[index] = newsub
        return newsub

    def append(self, value):
        """
        When you want to append a link to an Input, you can use the append
        property. This will automatically create a new SubInput to link to.

        example:

        .. code-block:: python

          >>> link = node2['input'].append(node1['output'])

        will create a new SubInput in node2['input'] and link to that.
        """
        new_sub = SubInput(self)
        # Get the next index-like key to use
        new_key = max([-1] + [x for x in self.source.keys() if isinstance(x, int)]) + 1
        self.source[new_key] = new_sub

        if isinstance(value, BaseOutput):
            if self.node.parent is not value.node.parent:
                message = 'Cannot create links between members of different Network'
                fastr.log.warning(message)
            elif value.node.parent is None:
                message = 'Cannot create links between non-network-attached Nodes'
                fastr.log.warning(message)
            else:
                fastr.log.debug('Linking {} to {}'.format(value.fullid, self[new_key].fullid))
                return self.node.parent.create_link(value, self[new_key])

        elif isinstance(value, (list, tuple, dict, OrderedDict)):
            # This is data for a ConstantNode, so create one and set it
            # First make sure the stepid of the new ConstantNode will match the stepid of the current Node
            inp = self[new_key]
            for k, i in self.node.parent.stepids.items():
                if inp.node in i:
                    stepid = k
                    break
            else:
                stepid = None
            network = inp.node.parent
            new_id = 'const_{}_{}'.format(inp.node.id, inp.id)
            const_node = network.create_constant(datatype=inp.datatype, data=value, id_=new_id, stepid=stepid)
            fastr.log.debug('Linking {} to {}'.format(const_node.output.fullid, self[new_key].fullid))
            return network.create_link(const_node.output, self[new_key])

    def itersubinputs(self):
        """
        Iterate over the :py:class:`SubInputs <fastr.core.inputoutput.SubInput>`
        in this Input.

        :return: iterator yielding  :py:class:`SubInput <fastr.core.inputoutput.SubInput>`


        example:

        .. code-block:: python

          >>> for subinput in input_a.itersubinputs():
                  print subinput

        """
        for subinput in self.source.values():
            yield subinput

    def prepare(self, sample_size=None):
        """
        This function makes sure the :py:class:`SampleIdList <fastr.core.sampleidlist.SampleIdList>`
        has the correct size.

        :param sample_size: the required size of the :py:class:`SampleIdList <fastr.core.sampleidlist.SampleIdList>`.
                            If no size is given, ``self.size`` will be used by default.
        :type sample_size: tuple of int
        """
        pass

    def _update(self, key, forward=True, backward=False):
        """Update the validity of the Input and propagate the update downstream.
        An Input is valid if:

        * All SubInputs are valid (see :py:meth:`SubInput.update <fastr.core.inputoutput.SubInput.update>`)
        * Cardinality is correct
        * If Input is required, it must have a size larger than (0,)

        An Input is ready if:

        * The Input is valid
        * All SubInputs are ready (see :py:meth:`SubInput.update <fastr.core.inputoutput.SubInput.update>`)

        """
        # fastr.log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))
        for subinput in self.itersubinputs():
            subinput.update(key, forward, backward)

        valid = True
        ready = True
        messages = []
        for subinput in self.itersubinputs():
            if not subinput.valid:
                valid = False
                for message in subinput.messages:
                    messages.append('SubInput {} is not valid: {}'.format(subinput.fullid, message))
            if not subinput.ready:
                ready = False

        if self.check_cardinality() is None or self:
            # If the cardinality is 0 and Input is not required, this is fine,
            # all other cases are not allowed
            if self.required and self.cardinality() == 0:
                valid = False
                messages.append(('Input "{}" cardinality ({}) is not valid (must'
                                 ' be {}, required is {})').format(self.id,
                                                                   self.cardinality(),
                                                                   self._description.cardinality,
                                                                   self.required))
        if self.size is None:
            valid = False
            messages.append('Cannot determine size of Input "{}"'.format(self.id))

        fastr.log.debug('Size: {}'.format(self.size))
        if self.required and (len([x for x in self.size if x != 0]) == 0):
            valid = False
            nodes = ', '.join([x.id for x in self.get_sourced_nodes()])
            messages.append(('Required Input "{}" cannot have size 0. Input obtained'
                             ' from nodes: {}').format(self.id, nodes))

        self._status['valid'] = valid
        self._status['messages'] = messages

        self._status['ready'] = (valid and ready)

        # Update downstream
        self.node.update(key, forward, backward)


class SubInput(BaseInput):
    """
    This class is used by :py:class:`Input <fastr.core.inputoutput.Input>` to
    allow for multiple links to an :py:class:`Input <fastr.core.inputoutput.Input>`.
    The SubInput class can hold only a single Link to a (Sub)Output, but behaves
    very similar to an :py:class:`Input <fastr.core.inputoutput.Input>` otherwise.
    """

    def __init__(self, input_):
        """
        Instantiate an SubInput.

        :param input_: the parent of this SubInput.
        :type input_: :py:class:`Input <fastr.core.inputoutput.Input>`
        :return: the created SubInput
        """
        self._source = None

        if not isinstance(input_, Input):
            raise exceptions.FastrTypeError('First argument for a SubInput constructor should be an Input')

        self.parent = input_
        super(SubInput, self).__init__(self.node, self.description)

        self.datatype = input_.datatype
        if self.parent.valid:
            self.update()

    def __getitem__(self, key):
        """
        Retrieve an item from this SubInput.

        :param key: the key of the requested item, can be a number, sample
                    index tuple or a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :type key: int, :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` or
                   :py:class:`SampleIndex <fastr.core.sampleidlist.SampleIndex>`
        :return: the return value depends on the requested key. If the key was
                 an int the corresponding :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                 will be returned. If the key was a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                 or sample index tuple, the corresponding
                 :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned.
        :rtype: :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` or
                :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :raises FastrTypeError: if key is not of a valid type

        .. note:: As a SubInput has only one SubInput, only requesting int key
                  0 or -1 is allowed, and it will return self
        """

        if not isinstance(key, (int, SampleIndex, SampleId)):
            raise exceptions.FastrTypeError('SubInput indices must be an int, SampleIndex, or SampleID, not {}'.format(type(key).__name__))

        if isinstance(key, (SampleIndex, SampleId)):
            return self.source[0][key]

        if not -1 <= key < 1:
            raise exceptions.FastrIndexError('SubInput index out of range (key: {})'.format(key))

        return self

    def __eq__(self, other):
        """Compare two SubInput instances with each other. This function ignores
        the parent, node, source and update status, but tests rest of the dict
        for equality.

        :param other: the other instances to compare to
        :type other: SubInput
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['_node']
        del dict_self['parent']
        del dict_self['_source']
        del dict_self['_status']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['_node']
        del dict_other['parent']
        del dict_other['_source']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

    def __getstate__(self):
        """
        Retrieve the state of the SubInput

        :return: the state of the object
        :rtype dict:
        """
        state = super(SubInput, self).__getstate__()
        return state

    def __setstate__(self, state):
        """
        Set the state of the SubInput by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(SubInput, self).__setstate__(state)

        if not hasattr(self, '_source'):
            self._source = None

    def __str__(self):
        """
        Get a string version for the SubInput

        :return: the string version
        :rtype: str
        """
        return '<SubInput: {} => {}>'.format(self.fullid, self.source_output.fullid)

    def cardinality(self, key=None, job_data=None):
        """
        Get the cardinality for this SubInput. The cardinality for a SubInputs
        is defined by the incoming link.

        :param key: key for a specific sample, can be sample index or id
        :type key: :py:class:`SampleIndex <fastr.core.sampleidlist.SampleIndex>` or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """
        if self.source is not None:
            return self.source[0].cardinality(index=key)
        else:
            return 0

    @property
    def description(self):
        return self.parent.description

    @property
    def dimnames(self):
        """
        List of dimension names for this SubInput
        """
        return self.source[0].dimnames

    @property
    def size(self):
        """
        The sample size of the SubInput
        """
        if self.source is None:
            return ()
        else:
            return self.source[0].size

    @property
    def fullid(self):
        """
        The full defining ID for the SubInput
        """
        return '{}/{}'.format(self.parent.fullid, self.parent.index(self))

    @property
    def input_group(self):
        """
        The id of the :py:class:`InputGroup <fastr.core.node.InputGroup>` this
        SubInputs parent belongs to.
        """
        return self.parent.input_group

    @property
    def node(self):
        """
        The Node to which this SubInputs parent belongs
        """
        return self.parent.node

    @property
    def num_subinput(self):
        """
        The number of SubInputs in this SubInput, this is always 1.
        """
        return 1

    @property
    def source_output(self):
        """
        The :py:class:`Output <fastr.core.inputoutput.Output>`
        linked to this SubInput
        """
        if self.source is not None:
            return self.source[0].source

    @property
    def source(self):
        """
        A list with the source :py:class:`Link <fastr.core.link.Link>`.
        The list is to be compatible with :py:class:`Input <fastr.core.inputoutput.Input>`
        """
        if self._source is None:
            self.parent.remove(self)
            return []

        return [self._source]

    @source.setter
    def source(self, value):
        """
        Set new source, make sure previous link to source is released
        """
        if value is self._source:
            return

        if self._source is not None:
            self._source.destroy()

        if value is None:
            self.parent.remove(self)

        self._source = value

    def get_sourced_nodes(self):
        """
        Get a list of all :py:class:`Nodes <fastr.core.node.Node>` connected as sources to this SubInput

        :return: list of all connected :py:class:`Nodes <fastr.core.node.Node>`
        :rtype: list
        """
        return [x.source.node for x in self.source]

    def get_sourced_outputs(self):
        """
        Get a list of all :py:class:`Outputs <fastr.core.inputoutput.Output>` connected as sources to this SubInput

        :return: list of all connected :py:class:`Outputs <fastr.core.inputoutput.Output>`
        :rtype: list
        """
        return [x.source for x in self.source]

    def remove(self, value):
        """
        Remove a SubInput from parent Input.

        :param value: the :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                      to removed from this Input
        :type value: :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        """
        # Pass on to the parent Input
        self.parent.remove(value)

    def _update(self, key, forward=True, backward=False):
        """Update the validity of the SubInput and propagate the update downstream.
        A SubInput is valid if:

        * the source Link is set and valid (see :py:meth:`Link.update <fastr.core.link.Link.update>`)

        A SubInput is ready if:

        * The SubInput is valid
        * The source Link is ready (see :py:meth:`Link.update <fastr.core.link.Link.update>`)

        """
        # fastr.log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))
        valid = True
        messages = []
        if len(self.source) == 0:
            self.parent.remove(self)
            valid = False
            messages.append('No source in this SubInput, removing!')
        elif not self.source[0].valid:
            valid = False
            messages.append('SubInput source ({}) is not valid'.format(self.source[0].id))
            messages.extend(self.source[0].messages)

        self._status['valid'] = valid
        self._status['messages'] = messages

        if valid and self.source[0].ready:
            self._status['ready'] = True
        else:
            self._status['ready'] = False

        # Update downstream
        self.parent.update(key, forward, backward)

    def iteritems(self):
        """
        Iterate over the :py:class:`SampleItems <fastr.core.sampleidlist.SampleItem>`
        that are in the SubInput.

        :return: iterator yielding :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` objects
        """
        for item in self.source.items():
            yield item

    def itersubinputs(self):
        """Iterate over SubInputs (for a SubInput it will yield self and stop iterating after that)

        :return: iterator yielding  :py:class:`SubInput <fastr.core.inputoutput.SubInput>`

        example:

        .. code-block:: python

          >>> for subinput in input_a.itersubinputs():
                  print subinput

        """
        yield self


class BaseOutput(BaseInputOutput):
    """
    Base class for all outputs.
    """

    def __init__(self, node, description):
        """Instantiate a BaseOutput

        :param node: the parent node the output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the output.
        :return: created BaseOutput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        if not isinstance(description, OutputSpec):
            fastr.log.error('Description has type "{}" (must be ParameterDescription)'.format(type(description).__name__))
            raise exceptions.FastrTypeError('An output must be constructed based on an '
                                            'object of a class derived from Node and an '
                                            'object of class OutputSpec')
        super(BaseOutput, self).__init__(node, description)

    @property
    def automatic(self):
        """
        Flag indicating that the Output is generated automatically
        without being specified on the command line
        """
        return self._description.automatic


class Output(BaseOutput):
    """
    Class representing an output of a node. It holds the output values of
    the tool ran. Output fields can be connected to inputs of other nodes.
    """

    def __init__(self, node, description):
        """Instantiate an Output

        :param node: the parent node the output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the output.
        :return: created Output
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        self._suboutputlist = {}
        self._samples = None
        super(Output, self).__init__(node, description)
        # Create the output_cardiality member function
        self._output_cardinality = self._create_output_cardinality(description.cardinality)
        self._listeners = []
        self._preferred_types = []

    def __str__(self):
        """
        Get a string version for the Output

        :return: the string version
        :rtype: str
        """
        return '<Output: {} ({})>'.format(self.fullid, self.name)

    def __eq__(self, other):
        """
        Compare two Output instances with each other. This function ignores
        the parent node, listeners and update status, but tests rest of the
        dict for equality.

        :param other: the other instances to compare to
        :type other: Output
        :returns: True if equal, False otherwise
        :rtype: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['_node']
        del dict_self['_listeners']
        del dict_self['_status']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['_node']
        del dict_other['_listeners']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

    def __getitem__(self, key):
        """
        Retrieve an item from this Output. The returned value depends on what type of key used:

        * Retrieving data using index tuple: [index_tuple]
        * Retrieving data sample_id str: [SampleId]
        * Retrieving a list of data using SampleId list: [sample_id1, ..., sample_idN]
        * Retrieving a :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>` using an int or slice: [n] or [n:m]

        :param key: the key of the requested item, can be a number, slice, sample
                    index tuple or a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :type key: int, slice, :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` or tuple
        :return: the return value depends on the requested key. If the key was
                 an int or slice the corresponding :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>`
                 will be returned (and created if needed). If the key was a
                 :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                 or sample index tuple, the corresponding
                 :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned. If the
                 key was a list of :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` a tuple
                 of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned.
        :rtype: :py:class:`SubInput <fastr.core.inputoutput.SubInput>` or
                :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` or
                list of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>`
        :raises FastrTypeError: if key is not of a valid type
        :raises FastrKeyError: if the parent Node has not been executed
        """
        if isinstance(key, (SampleId, SampleIndex, tuple, list)):
            # If the key is a index, then get the sample id
            if isinstance(key, (SampleId, SampleIndex)):
                return self.samples[key]
            else:
                # A list or tuple of SampleId/SampleIndex
                if not all(isinstance(k, (SampleId, SampleIndex)) for k in key):
                    message = ('If a list/tuple of keys is used, all elements should be of SampleId or SampleIndex type'
                               ' found key {}'.format(key))
                    fastr.log.error(message)
                    raise exceptions.FastrValueError(message)

                return tuple(self.samples[k] for k in key)
        elif isinstance(key, (int, slice)):
            # Get a string representation of the key
            if isinstance(key, slice):
                keystr = '{}:{}'.format(key.start, key.stop)
                keystr = keystr.replace('None', '')

                if key.step is not None and key.step != 1:
                    keystr = '{}:{}'.format(keystr, key.step)
            else:
                keystr = str(key)

            if keystr in self._suboutputlist:
                # Re-use the same SubOutput
                subout = self._suboutputlist[keystr]
            else:
                # Create the desired SubOutput object
                subout = SubOutput(self, key)
                self._suboutputlist[keystr] = subout

            return subout
        else:
            raise exceptions.FastrTypeError('Key should be an integer/slice (for getting a SubOutput) or an index tuple/sample_id str for getting value(s)')

    def __setitem__(self, key, value):
        """
        Store an item in the Output

        :param key: key of the value to store
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param value: the value to store
        :return: None
        :raises FastrTypeError: if key is not of correct type
        """

        if isinstance(value, SampleItem):
            self.samples[key] = value
        else:
            if not isinstance(value, (tuple, list)):
                value = (value,)

            self.samples[key] = tuple(self._cast_to_storetype(x) for x in value)

    def __getstate__(self):
        """
        Retrieve the state of the Output

        :return: the state of the object
        :rtype dict:
        """
        state = super(Output, self).__getstate__()

        # Add specific fields to the state
        state['suboutputs'] = [x.__getstate__() for x in self._suboutputlist.values()]
        state['preferred_types'] = [x.id for x in self._preferred_types]

        return state

    def __setstate__(self, state):
        """
        Set the state of the Output by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(Output, self).__setstate__(state)

        self._preferred_types = [fastr.typelist[x] for x in state['preferred_types']]

        suboutputlist = []
        for substate in state['suboutputs']:
            suboutput = SubOutput(self, slice(None))
            suboutput.__setstate__(substate)
            suboutputlist.append((suboutput.indexrep, suboutput))

        # Re-create the dict from the array
        self._suboutputlist = dict(suboutputlist)
        self._listeners = []

    def _cast_to_storetype(self, value):
        """
        Cast a given value to a DataType that matches this Outputs datatype.

        :param value: value to cast
        :return: cast value
        :rtype: DataType matching self.datatype
        """
        if isinstance(value, self.datatype):
            return value

        storetype = typelist.match_types(self.datatype, type(value))

        if storetype is None:
            storetype = typelist.match_types(self.datatype)

        if not isinstance(value, storetype):
            if isinstance(value, DataType):
                fastr.log.warning('Changing value type from {} to {}'.format(type(value), storetype))
            value = storetype(str(value))

        return value

    @property
    def blocking(self):
        """
        Flag indicating that this Output will cause blocking in the execution
        """
        return self._output_cardinality[0] in ('val', 'unknown')

    def cardinality(self, key=None, job_data=None):
        """
        Cardinality of this Output, may depend on the inputs of the parent Node.

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        :raises FastrCardinalityError: if cardinality references an invalid :py:class:`Input <fastr.core.inputoutput.Input>`
        :raises FastrTypeError: if the referenced cardinality values type cannot be case to int
        :raises FastrValueError: if the referenced cardinality value cannot be case to int
        """
        desc = self._output_cardinality

        if isinstance(key, SampleId):
            sample_index = self.samples[key].index if key in self.samples else None
        elif isinstance(key, SampleIndex):
            sample_index = key
        else:
            sample_index = None

        if desc[0] == 'int':
            return desc[1]
        elif desc[0] == 'as':
            if desc[1] in self.node.inputs:
                target = self.node.inputs[desc[1]]

                if key is None:
                    # No key is used, call target without key
                    cardinality = target.cardinality(None)
                elif all(x == 0 for x in target.size):
                    # Target is empty, cardinality can be set to 0
                    cardinality = 0
                elif target.size == (1,):
                    # Target has only sample, it will be repeated, use first sample
                    cardinality = target.cardinality((0,))
                elif key is None or len(self.node.inputgroups) == 1:
                    # The InputGroups are not mixed, we can request the sample_index
                    if len(key) == len(target.size):
                        cardinality = target.cardinality(sample_index)
                    else:
                        indexmap = dict(zip(self.dimnames, key))
                        lookup = {v: dimname for dimname in self.dimnames for value in self.node.parent.sourcegroups.values() if dimname in value for v in value}
                        lookup.update({x: x for x in self.dimnames})
                        if all(x in lookup for x in target.dimnames):
                            # Print there is broadcasting going on, we need to undo that here
                            matched_dimnames = [lookup[x] for x in target.dimnames]
                            matched_index = SampleIndex(indexmap[x] for x in matched_dimnames)
                            cardinality = target.cardinality(matched_index)
                        else:
                            raise exceptions.FastrSizeMismatchError('InputGroup has inconsistent size/dimension info for Input {}, cannot figure out broadcasting used!'.format(target.fullid))
                else:
                    fastr.log.debug('Unmixing key "{}" for cardinality retrieval'.format(key))
                    # The InputGroups are mixed, find the part of the ID relevant to this Input
                    test = self.node._input_group_combiner.unmerge(key)
                    index = test[target.input_group]

                    if len(index) == len(target.size):
                        cardinality = target.cardinality(index)
                    else:
                        raise exceptions.FastrSizeMismatchError('TODO: add broadcasting to this branch?')

                return cardinality
            else:
                raise exceptions.FastrCardinalityError('Cardinality references to invalid field ({} is not an Input in this Node)'.format(desc[1]))
        elif desc[0] == 'val':
            if desc[1] in self.node.inputs:
                if job_data is None:
                    # We cannot access to the jobs inputs it appears, so we
                    # check if the output has already been generated.
                    if self.samples is not None and key in self.samples:
                        value = self.samples[key].data
                        fastr.log.debug('Got val via output data result, got {}'.format(value))
                        return len(value)
                    else:
                        fastr.log.debug('Cannot get val: cardinality if there is not job_data supplied!')
                        return None

                value = job_data[desc[1]]
                fastr.log.debug('Extracted cardinality field {} from {} resulting in {}'.format(desc[1], job_data, value))

                if len(value) != 1:
                    message = 'Cardinality of Input {} with defining value for {} should have cardinality 1! Found {} (value {})'.format(self.node.inputs[desc[1]].fullid, self.fullid, len(value), value)
                    fastr.log.error(message)
                    raise exceptions.FastrCardinalityError(message)

                try:
                    cardinality = int(value[0].value)
                except TypeError:
                    raise exceptions.FastrTypeError('The value of the val: cardinality has an type that cannot be cast to an int ({})'.format(type(value[0].value).__name__))
                except ValueError:
                    raise exceptions.FastrValueError('The value of the val: cardinality has a value that cannot be cast to an int ({}, type: {})'.format(value[0].value, type(value[0].value).__name__))

                return cardinality
            elif desc[1] in self.node.outputs:
                # Get the value an output
                if key is None:
                    return None

                output = self.node.outputs[desc[1]]

                if output.samples is None:
                    return None

                # Try to cast via str to int (To make sure Int datatypes fares well)
                try:
                    #FIXME: need to open val:// url (create a helper function in utils?)
                    return int(str(output[key]))
                except exceptions.FastrKeyError:
                    return None
            else:
                raise exceptions.FastrCardinalityError('Cardinality references to invalid field ({} is not an Input or Output in this Node)'.format(desc[1]))
        elif desc[0] == 'unknown':
            if key is None:
                return None

            if key not in self.samples:
                return None

            value = self.samples[key].data
            return len(value)
        else:
            raise exceptions.FastrCardinalityError('Invalid output cardinality specification found! ({})'.format(desc))

    @property
    def datatype(self):
        """
        The datatype of this Output
        """
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        # This does not differ, as it is a property
        # pylint: disable=arguments-differ
        self._datatype = value

    @property
    def dimnames(self):
        """
        The list names of the dimensions in this Output. This will be a list of str.
        """
        if self.samples is not None:
            return self.samples.dimnames
        else:
            return self.node.dimnames

    @property
    def ndims(self):
        """
        The number of dimensions in this Output
        """
        return len(self.dimnames)

    @property
    def fullid(self):
        """
        The full defining ID for the Output
        """
        if self.node is not None:
            return '{}/outputs/{}'.format(self.node.fullid, self.id)
        else:
            return 'fastr://ORPHANED/outputs/{}'.format(self.id)

    @property
    def listeners(self):
        """
        The list of :py:class:`Links <fastr.core.link.Link>` connected to this Output.
        """
        return self._listeners

    @property
    def preferred_types(self):
        """
        The list of preferred :py:class:`DataTypes <fastr.core.datatypemanager.DataType>`
        for this Output.
        """
        return self._preferred_types

    @preferred_types.setter
    def preferred_types(self, value):
        """
        The list of preferred :py:class:`DataTypes <fastr.core.datatypemanager.DataType>`
        for this Output. (setter)
        """
        if isinstance(value, type) and issubclass(value, DataType):
            self._preferred_types = [value]
        elif isinstance(value, list) and all([isinstance(x, type) and issubclass(x, DataType) for x in value]):
            self._preferred_types = value
        else:
            fastr.log.warning('Invalid definition of preferred DataTypes, must be a DataType or list of DataTypes! Ignoring!')

    @property
    def samples(self):
        """
        The SampleCollection of the samples in this Output. None if the Node
        has not yet been executed. Otherwise a SampleCollection.
        """
        return self._samples

    @property
    def valid(self):
        """
        Check if the output is valid, i.e. has a valid cardinality
        """
        return self.check_cardinality()

    @property
    def resulting_datatype(self):
        """
        The :py:class:`DataType <fastr.core.datatypemanager.DataType>` that
        will the results of this Output will have.
        """
        requested_types = [l.target.datatype for l in self.listeners if l.target is not None]
        requested_types.append(self.datatype)

        if self.preferred_types is not None and len(self.preferred_types) > 0:
            return typelist.match_types(requested_types, preferred=self.preferred_types)
        elif self.node.parent is not None and self.node.parent.preferred_types is not None and len(self.node.parent.preferred_types) > 0:
            return typelist.match_types(requested_types, preferred=self.node.parent.preferred_types)
        else:
            return typelist.match_types(requested_types)

    @property
    def size(self):
        """
        The sample size of the Output
        """
        if self.samples is not None:
            return self.samples.size
        else:
            return self.node.outputsize

    def prepare(self):
        """
        This function makes sure that a value storage will be created
        """
        self._samples = SampleCollection(self.dimnames, self.resulting_datatype, self)

    def _update(self, key, forward=True, backward=False):
        """Update the status and validity of the Output and propagate the update the Node.
        An Output is valid if:

        * the parent Node is valid (see :py:meth:`Node.update <fastr.core.node.Node.update>`)

        A Output is ready if:

        * The Output is valid
        * The parent Node is is ready (see :py:meth:`Node.update <fastr.core.node.Node.update>`)
        * Output has been prepared

        """
        # fastr.log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))

        self.node.update(key, forward, backward)

        if self.node.valid:
            self._status['valid'] = True
        else:
            self._status['valid'] = False
            self._status['messages'] = ['Parent Node is not valid']

        self._status['ready'] = self._status['valid'] and self.node.ready

    @staticmethod
    def _create_output_cardinality(desc):
        """Create a lambda function that returns an integer value of the cardinality.

        :param str desc: The cardinality description string
        :return: output cardinality description
        :rtype tuple:

       The description string can be one of the following forms:

        * N: N number of values needed.
        * as:input_name: the same number of values as attached to input_name are needed.
        * val:input_name: the number of values needed is the value of input_name.
        * unknown: the output cardinality cannot be estimated a priori
        """
        try:
            int(desc)
            is_int = True
        except ValueError:
            is_int = False

        if is_int:
            # N
            output_cardinality = ('int', int(desc))
        elif desc[0:3] == "as:":
            # as:input_name
            output_cardinality = ('as', desc[3:])
        elif desc[0:4] == "val:":
            output_cardinality = ('val', desc[4:])
        elif desc == 'unknown':
            output_cardinality = ('unknown',)
        else:
            raise exceptions.FastrCardinalityError('Invalid cardinality specification "{}"!'.format(desc))

        return output_cardinality

    def iterconvergingindices(self, collapse_dims):
        """
        Iterate over all data, but collapse certain dimension to create lists
        of data.

        :param collapse_dims: dimension to collapse
        :type collapse_dims: iterable of int
        :return: iterator SampleIndex (possibly containing slices)
        """
        if all(-self.ndims <= x < self.ndims for x in collapse_dims):
            iter_dims = [xrange(s) for s in self.size]
            for idx in collapse_dims:
                iter_dims[idx] = slice(None),

            # It is just useful here :-)
            # pylint: disable=star-args
            for idx in itertools.product(*iter_dims):
                yield SampleIndex(idx)
        else:
            raise exceptions.FastrIndexError('Index of a converging dimension {} out out of range (number of dimensions {})'.format(collapse_dims, self.ndims))


class SubOutput(Output):
    """
    The SubOutput is an Output that represents a slice of another Output.
    """

    def __init__(self, output, index):
        """Instantiate a SubOutput

        :param output: the parent output the suboutput slices.
        :param index: the way to slice the parent output
        :type index: int or slice
        :return: created SubOutput
        :raises FastrTypeError: if the output argument is not an instance of :py:class:`Output <fastr.core.inputoutput.Output>`
        :raises FastrTypeError: if the index argument is not an ``int`` or ``slice``
        """
        if not isinstance(output, Output):
            raise exceptions.FastrTypeError('Second argument for a SubOutput init should be an Output')

        if not isinstance(index, (int, slice)):
            raise exceptions.FastrTypeError('SubOutput index should be an integer or a slice, found ({}, type {})'.format(index, type(index).__name__))

        super(SubOutput, self).__init__(output.node, output.description)
        self.parent = output
        self.index = index

    def __str__(self):
        """
        Get a string version for the SubOutput

        :return: the string version
        :rtype: str
        """
        return '<SubOutput {}>'.format(self.fullid)

    def __getitem__(self, key):
        """
        Retrieve an item from this SubOutput. The returned value depends on what type of key used:

        * Retrieving data using index tuple: [index_tuple]
        * Retrieving data sample_id str: [SampleId]
        * Retrieving a list of data using SampleId list: [sample_id1, ..., sample_idN]
        * Retrieving a :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>` using an int or slice: [n] or [n:m]

        :param key: the key of the requested item, can be a number, slice, sample
                    index tuple or a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :type key: int, slice, :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` or tuple
        :return: the return value depends on the requested key. If the key was
                 an int or slice the corresponding :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>`
                 will be returned (and created if needed). If the key was a
                 :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                 or sample index tuple, the corresponding
                 :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned. If the
                 key was a list of :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` a tuple
                 of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned.
        :rtype: :py:class:`SubInput <fastr.core.inputoutput.SubInput>` or
                :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` or
                list of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>`
        :raises FastrTypeError: if key is not of a valid type
        """

        if isinstance(key, (int, slice)):
            # Get a string representation of the key
            if isinstance(key, slice):
                keystr = '{}:{}'.format(key.start, key.stop)
                keystr = keystr.replace('None', '')

                if key.step is not None and key.step != 1:
                    keystr = '{}:{}'.format(keystr, key.step)
            else:
                keystr = str(key)

            if keystr in self._suboutputlist:
                # Re-use the same SubOutput
                subout = self._suboutputlist[keystr]
            else:
                # Create the desired SubOutput object
                subout = SubOutput(self, key)
                self._suboutputlist[keystr] = subout

            return subout

        item = self.parent[key]

        if isinstance(item, SampleItem):
            if isinstance(self.index, int):
                return SampleItem(item.index, item.id, {0: (item.data.sequence_part()[self.index],)}, item.jobs)
            else:
                return SampleItem(item.index, item.id, {0: item.data.sequence_part()[self.index]}, item.jobs)
        else:
            if isinstance(self.index, int):
                return tuple(SampleItem(x.index, x.id, (x.data[self.index],), x.jobs) for x in item)
            else:
                return tuple(SampleItem(x.index, x.id, x.data[self.index], x.jobs) for x in item)


    def __setitem__(self, key, value):
        """
        A function blocking the assignment operator. Values cannot be assigned to a SubOutput.

        :raises FastrNotImplementedError: if called
        """
        raise exceptions.FastrNotImplementedError('[{}] Cannot assign values to a SubOutput, assign to parent Output instead!'.format(self.fullid))

    def __getstate__(self):
        """
        Retrieve the state of the SubOutput

        :return: the state of the object
        :rtype dict:
        """
        state = super(SubOutput, self).__getstate__()
        state['index'] = self.indexrep
        return state

    def __setstate__(self, state):
        """
        Set the state of the SubOutput by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        if isinstance(state['index'], str):
            index = [int(x) if len(x) > 0 else None for x in state['index'].split(':')]
            # It is just useful here :-)
            # pylint: disable=star-args
            state['index'] = slice(*index)

        state['_preferred_types'] = []
        super(SubOutput, self).__setstate__(state)
        self._preferred_types = None

    def __eq__(self, other):
        """Compare two SubOutput instances with each other. This function ignores
        the parent, node and update status, but tests rest of the dict for equality.
        equality

        :param other: the other instances to compare to
        :type other: SubOutput
        :returns: True if equal, False otherwise
        :rtype: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['_node']
        del dict_self['_parent']
        del dict_self['_status']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['_node']
        del dict_other['_parent']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

    def __len__(self):
        """Return the length of the Output.

        .. note::

            In a SubOutput this is always 1.
        """
        return 1

    @property
    def indexrep(self):
        """
        Simple representation of the index.
        """
        if isinstance(self.index, slice):
            index = '{}:{}'.format(self.index.start, self.index.stop)
            index = index.replace('None', '')

            if self.index.step is not None and self.index.step != 1:
                index = '{}:{}'.format(index, self.index.step)
        else:
            index = self.index

        return index

    def cardinality(self, key=None, job_data=None):
        """
        Cardinality of this SubOutput depends on the parent Output and ``self.index``

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        :raises FastrCardinalityError: if cardinality references an invalid :py:class:`Input <fastr.core.inputoutput.Input>`
        :raises FastrTypeError: if the referenced cardinality values type cannot be case to int
        :raises FastrValueError: if the referenced cardinality value cannot be case to int
        """
        parent_cardinality = self.parent.cardinality(key)

        if parent_cardinality is not None:
            if isinstance(parent_cardinality, int):
                if isinstance(self.index, int):
                    if parent_cardinality >= 1:
                        return 1
                    else:
                        return 0
                else:
                    # Calculate the slice effect on a list of length parent cardinality
                    ind_range = self.index.indices(parent_cardinality)
                    return (ind_range[1] - ind_range[0]) // ind_range[2]
            else:
                return parent_cardinality
        else:
            return None

    @property
    def datatype(self):
        """
        The datatype of this SubOutput
        """
        return self.parent.datatype

    @property
    def fullid(self):
        """
        The full defining ID for the SubOutput
        """
        return '{}/{}'.format(self.parent.fullid, self.indexrep)

    @property
    def listeners(self):
        """
        The list of :py:class:`Links <fastr.core.link.Link>` connected to this Output.
        """
        return self.parent.listeners

    @property
    def node(self):
        """
        The Node to which this SubOutput belongs
        """
        return self.parent.node

    @property
    def preferred_types(self):
        """
        The list of preferred :py:class:`DataTypes <fastr.core.datatypemanager.DataType>`
        for this SubOutput.
        """
        return self.parent.preferred_types

    @preferred_types.setter
    def preferred_types(self, value):
        # We need to key for the signature in subclasses, shut pylint up
        # pylint: disable=unused-argument,no-self-use,arguments-differ
        raise exceptions.FastrNotImplementedError('Cannot set DataType of SubOutput, use the parent Output instead')

    @property
    def samples(self):
        """
        The :py:class:`SampleCollection <fastr.core.sampleidlist.SampleCollection>`
        for this SubOutput
        """
        return self.parent.samples

    @property
    def resulting_datatype(self):
        """
        The :py:class:`DataType <fastr.core.datatypemanager.DataType>` that
        will the results of this SubOutput will have.
        """
        return self.parent.resulting_datatype

    def _update(self, key, forward=True, backward=False):
        """Update the status and validity of the SubOutput and propagate the update downstream.
        An SubOutput is valid if:

        * the parent Node is valid (see :py:meth:`Node.update <fastr.core.node.Node.update>`)

        A SubOutput is ready if:

        * The SubOutput is valid
        * The parent Node is is ready (see :py:meth:`Node.update <fastr.core.node.Node.update>`)

        """
        # fastr.log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))
        self.parent.update(key, forward, backward)

        if self.node.valid:
            self._status['valid'] = True
        else:
            self._status['valid'] = False
            self._status['messages'] = ['Parent Node is not valid']

        if self._status['valid'] and self.node.ready:
            self._status['ready'] = True
        else:
            self._status['ready'] = False


class AdvancedFlowOutput(Output):
    @property
    def dimnames(self):
        """
        The dimnames of AdvancedFlowNodes have the output id appended, as the
        sizes per output can be different.
        """
        if self.samples is not None:
            return self.samples.dimnames
        else:
            parent_dimnames = super(AdvancedFlowOutput, self).dimnames
            return tuple('{}_{}'.format(x, self.id) for x in parent_dimnames[:-1]) + (parent_dimnames[-1],)


class SourceOutput(Output):
    """
    Output for a SourceNode, this type of Output determines the cardinality in
    a different way than a normal Node.
    """
    def __init__(self, node, description):
        """Instantiate a FlowOutput

        :param node: the parent node the output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the output.
        :return: created FlowOutput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        super(SourceOutput, self).__init__(node, description)

        self._linearized = None

    def __getitem__(self, item):
        """
        Retrieve an item from this Output. The returned value depends on what type of key used:

        * Retrieving data using index tuple: [index_tuple]
        * Retrieving data sample_id str: [SampleId]
        * Retrieving a list of data using SampleId list: [sample_id1, ..., sample_idN]
        * Retrieving a :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>` using an int or slice: [n] or [n:m]

        :param key: the key of the requested item, can be a number, slice, sample
                    index tuple or a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :type key: int, slice, :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` or tuple
        :return: the return value depends on the requested key. If the key was
                 an int or slice the corresponding :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>`
                 will be returned (and created if needed). If the key was a
                 :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                 or sample index tuple, the corresponding
                 :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned. If the
                 key was a list of :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` a tuple
                 of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned.
        :rtype: :py:class:`SubInput <fastr.core.inputoutput.SubInput>` or
                :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` or
                list of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>`
        :raises FastrTypeError: if key is not of a valid type
        :raises FastrKeyError: if the parent Node has not been executed
        """
        if len(item) != 1:
            fastr.log.debug('Non-linear access to SourceOutput attempted! (linearized data: {})'.format(self.linearized))
            raise exceptions.FastrIndexError('SourceOutput only allows for linear indices')

        fastr.log.debug('Retrieving {} ({}) from linear {}'.format(item, type(item).__name__, self.linearized))
        return self.linearized[item[0]]

    def __setitem__(self, key, value):
        """
        Store an item in the Output

        :param key: key of the value to store
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param value: the value to store
        :return: None
        :raises FastrTypeError: if key is not of correct type
        """
        super(SourceOutput, self).__setitem__(key, value)
        self._linearized = None

    @property
    def size(self):
        """
        The sample size of the SourceOutput
        """
        if self.samples is not None:
            return len(self.linearized),
        else:
            return (sympy.symbols('N_{}_{}'.format(self.node.id, self.id)),)

    @property
    def ndims(self):
        """
        The number of dimensions in this SourceOutput
        """
        return 1

    @property
    def linearized(self):
        """
        A linearized version of the sample data, this is lazily cached
        linearized version of the underlying SampleCollection.
        """
        if self._linearized is None:
            self._linearized = tuple(self.samples[x] for x in self.samples)

        return self._linearized

    def cardinality(self, key=None, job_data=None):
        """
        Cardinality of this SourceOutput, may depend on the inputs of the parent Node.

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """
        if key is None:
            return None

        if self.samples is None:
            return sympy.symbols('N_{}'.format(self.node.id.replace(' ', '_')))

        try:
            value = self[key]
        except (KeyError, IndexError):
            fastr.log.debug('Could not find sample {}, cardinality unknown!'.format(key))
            return None

        return len(value.data)
