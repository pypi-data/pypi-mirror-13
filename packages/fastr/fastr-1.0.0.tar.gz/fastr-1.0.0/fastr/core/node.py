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
A module to maintain a network node.

Exported classes:

Node -- A class encapsulating a tool.
ConstantNode -- A node encapsulating an Output to set scalar values.
SourceNode -- A class providing a handle to a file.
"""
from abc import ABCMeta
import itertools
from collections import OrderedDict
import os
import re
import urlparse


#For dynamically importing/loading of files(MacroNodes)
import sys, imp

import sympy
from sympy.core.symbol import Symbol

import fastr
from fastr.datatypes import DataType
import fastr.exceptions as exceptions
from fastr.core.inputoutput import BaseInput, Input, BaseOutput, Output, AdvancedFlowOutput, SourceOutput
from fastr.core.samples import SampleId, SampleItem, SampleIndex, SampleValue, SamplePayload
from fastr.core.serializable import Serializable
from fastr.core.tool import Tool
from fastr.core.updateable import Updateable, UpdateableMeta
from fastr.data import url
from fastr.execution.job import Job, SinkJob, SourceJob


class InputDict(OrderedDict):
    """
    The container containing the Inputs of Node. Implements helper functions
    for the easy linking syntax.
    """

    # We know this class is not really for public interaction, however it has
    # an important function linking of nodes.
    # pylint: disable=too-few-public-methods

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        """
        Set an item in the input dictionary. The behaviour depends on the
        type of the value. For a
        :py:class:`BaseInput <fastr.core.inputoutput.BaseInput>`,
        the input will simply be added to the list of inputs. For a
        :py:class:`BaseOutput <fastr.core.inputoutput.BaseOutput>`,
        a link between the output and input will be created.

        :param str key: id of the input to assign/link
        :param value: either the input to add or the output to link
        :type value: :py:class:`BaseInput <fastr.core.inputoutput.BaseInput>`
                      or
                      :py:class:`BaseOutput <fastr.core.inputoutput.BaseOutput>`
        :param dict_setitem: the setitem function to use for the underlying
                              OrderedDict insert
        """
        if isinstance(value, Input):
            super(InputDict, self).__setitem__(key, value, dict_setitem=dict_setitem)
        elif isinstance(value, BaseOutput):
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
            inp = self[key]
            for k, i in inp.node.parent.stepids.items():
                if inp.node in i:
                    stepid = k
                    break
            else:
                stepid = None
            network = inp.node.parent
            new_id = 'const_{}_{}'.format(inp.node.id, inp.id)
            const_node = network.create_constant(datatype=inp.datatype, data=value, id_=new_id, stepid=stepid)
            network.create_link(const_node.output, self[key])

        else:
            message = 'Cannot add object of type {} to InputDict'.format(type(value).__name__)
            fastr.log.critical(message)
            raise exceptions.FastrTypeError(message)


class OutputDict(OrderedDict):
    """
    The container containing the Inputs of Node. Only checks if the inserted
    values are actually outputs.
    """

    # We know this class is not really for public interaction, however it we
    # have it to do type checking and consistency with the InputDict
    # pylint: disable=too-few-public-methods

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        """
        Set an output.

        :param str key: the of the item to set
        :param value: the output to set
        :type value: :py:class:`BaseOutput <fastr.core.inputoutput.BaseOutput>`
        :param dict_setitem: the setitem function to use for the underlying
                              OrderedDict insert
        """
        if isinstance(value, Output):
            super(OutputDict, self).__setitem__(key, value, dict_setitem=dict_setitem)
        else:
            message = 'Cannot add object of type {} to OutputDict'.format(type(value).__name__)
            fastr.log.warning(message)


class InputGroup(OrderedDict):
    """
    A class representing a group of inputs. Input groups allow the
    """
    __metaclass__ = UpdateableMeta
    __updatetriggers__ = ['__init__',
                          '__setitem__',
                          '__delitem__',
                          'clear',
                          'pop',
                          'popitem',
                          'setdefault',
                          'update']

    def __init__(self, parent, id_=None):
        """
        Create a new InputGroup representation

        :param parent: the parent node
        :type parent: :py:class:`Node <fastr.core.node.Node>`
        :param str id_: the id of the input group
        :raises FastrTypeError: if parent is not a Node
        """
        if not isinstance(parent, Node):
            raise exceptions.FastrTypeError('parent should be a Node')
        super(InputGroup, self).__init__()
        self._parent = parent
        self.id = id_
        self._size = ()
        self._dimnames = ()
        self._primary = None
        self.__updating__ = True

    def __getitem__(self, key):
        if isinstance(key, SampleIndex):
            index = key

            # Determine which input sample to use for Input
            indexmap = dict(zip(self.dimnames, index))
            data = {}

            sourcegroups = self.parent.parent.sourcegroups

            # Match dimensions if possible
            lookup = {v: dimname for dimname in self.dimnames for value in sourcegroups.values() if dimname in value for v in value}
            lookup.update({x: x for x in self.dimnames})

            for key, value in lookup.items():
                lookup[key] = indexmap[value]

            for id_, input_ in self.items():
                source_index = self.find_source_index(target_size=self.size,
                                                      target_dimnames=self.dimnames,
                                                      source_size=input_.size,
                                                      source_dimnames=input_.dimnames,
                                                      target_index=index)

                # Get data from Input
                if source_index is not None:
                    data[id_] = input_[source_index]
                else:
                    data[id_] = SampleItem(index, '__EMPTY__', [], set())

            # Aggregate data for input group
            sample_id = data[self.primary.id].id
            hold_jobs = set.union(*[val.jobs for val in data.values()])

            return SamplePayload(index, sample_id, data, hold_jobs)
        else:
            return super(InputGroup, self).__getitem__(key)

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        """
        Assign an input to this input group.

        :param str key: id of the input
        :param value: the input to assign
        :type value: :py:class:`Input <fastr.core.inputoutput.Input>`
        :raises FastrTypeError: if value of valid type
        """
        if not isinstance(value, Input):
            message = 'Cannot assign a non-Input to an InputGroup'
            fastr.log.error(message)
            raise exceptions.FastrTypeError(message)

        if self._parent is not None and value.node is not self._parent:
            message = 'Input has a different parent Node than the InputGroup, this is not a valid assignment!'
            fastr.log.error(message)
            raise exceptions.FastrParentMismatchError(message)

        super(InputGroup, self).__setitem__(key, value)

    @property
    def parent(self):
        """
        The parent node of this InputGroup
        """
        return self._parent

    @property
    def size(self):
        """
        The sample size of this InputGroup
        """
        return self._size

    @property
    def dimnames(self):
        """
        The names of the dimensions in this InputGroup
        """
        return self._dimnames

    @property
    def primary(self):
        """
        The primary Input in this InputGroup. The primary Input is the Input
        that defines the size of this InputGroup. In case of ties it will be
        the first in the tool definition.
        """
        return self._primary

    @property
    def empty(self):
        """
        Bool indicating that this InputGroup is empty (has no data connected)
        """
        return self.size is None or len([x for x in self.size if x != 0]) == 0

    @classmethod
    def find_source_index(cls, target_size, target_dimnames, source_size, source_dimnames, target_index):
        # Determine which input sample to use for Input

        if source_size == target_size:
            source_index = target_index
        elif source_size == (1,):
            source_index = SampleIndex(0)
        elif all(x == 0 for x in source_size):
            source_index = None
        else:
            source_index = cls.solve_broadcast(target_size=target_size,
                                               target_dimnames=target_dimnames,
                                               source_size=source_size,
                                               source_dimnames=source_dimnames,
                                               target_index=target_index)

        return source_index

    @staticmethod
    def _get_lookup(target_dimnames, sourcegroups=None):
        if sourcegroups is None:
            sourcegroups = fastr.current_network.sourcegroups

        lookup = {v: dimname for dimname in target_dimnames for value in sourcegroups.values() if dimname in value for v in value}
        lookup.update({x: x for x in target_dimnames})

        return lookup

    @classmethod
    def solve_broadcast(cls, target_size, target_dimnames, source_size, source_dimnames, target_index, sourcegroups=None):
        indexmap = dict(zip(target_dimnames, target_index))
        sizemap = dict(zip(target_dimnames, target_size))
        lookup = cls._get_lookup(target_dimnames, sourcegroups)

        if all(x in lookup for x in source_dimnames):
            matched_dims = [lookup[x] for x in source_dimnames]
            source_index = SampleIndex(indexmap[x] for x in matched_dims)
            estimated_source_size = tuple(sizemap[x] for x in matched_dims)
        else:
            raise exceptions.FastrSizeMismatchError('Cannot broadcast, not all dimnames can be matched! (source dimnames {}, lookup {}'.format(source_dimnames, lookup))

        if source_size != estimated_source_size:
            raise exceptions.FastrSizeMismatchError('The estimated size after broadcast matching is incorrect! (estimated {}, actual {})'.format(estimated_source_size, source_size))

        return source_index

    @property
    def iterinputvalues(self):
        """
        Iterate over the item in this InputGroup

        :returns: iterator yielding :py:class:`SampleItems <fastr.core.sampeidlist.SampleItem>`
        """
        for index, _, _, _ in self.primary.iteritems():
            yield self[index]

    def __updatefunc__(self):
        """
        Update the InputGroup. Triggers when a change is made to the content
        of the InputGroup. Automatically recalculates the size, primary Input
        etc.
        """
        sizes = [x.size for x in self.values()]
        dimnames = [x.dimnames for x in self.values()]

        unique_sizes = set(sizes) - {(0,), (1,), (), None}

        if len(unique_sizes) > 1:
            if not any(all(not isinstance(x, Symbol) for x in size) for size in unique_sizes):
                # All entries in unique sizes are symbols, we cannot really
                # know what will be the size. Assume for now that the first
                # Input with symbolic input will be the primary
                max_dims = max(len(x.dimnames) for x in self.values())
                for input_ in self.values():
                    if input_.size in unique_sizes and len(input_.dimnames) == max_dims:
                        self._size = input_.size
                        self._primary = input_
                        self._dimnames = input_.dimnames
                        break

            # Check if we can match via dimnames
            elif all(len(x) == len(set(x)) for x in dimnames):
                longest_dimname, longest_size = max(zip(dimnames, sizes), key=lambda x: len(x[1]))

                if all(all(x in longest_dimname for x in y) for y in dimnames):
                    self._size = longest_size
                    self._primary = self.values()[sizes.index(self._size)]
                    self._dimnames = longest_dimname
                else:
                    sourcegroups = self.parent.parent.sourcegroups
                    lookup = {v: dimname for dimname in longest_dimname for value in sourcegroups.values() if dimname in value for v in value}
                    lookup.update({x: x for x in longest_dimname})

                    if all(x in lookup for y in dimnames for x in y):
                        self._size = longest_size
                        self._primary = self.values()[sizes.index(self._size)]
                        self._dimnames = longest_dimname
                    else:
                        message = 'Not all dimnames ({}) are present in the highest-dimensional input ({})'.format(
                            [x for y in dimnames for x in y],
                            lookup.keys(),
                        )
                        fastr.log.warning(message)

                        self._size = longest_size
                        self._primary = self.values()[sizes.index(self._size)]
                        self._dimnames = longest_dimname
            else:
                message = 'One or more inputs have non-unique dimnames ({})'.format(dimnames)
                fastr.log.error(message)
                raise exceptions.FastrValueError(message)

        elif len(unique_sizes) == 1:
            self._size = unique_sizes.pop()
            self._primary = self.values()[sizes.index(self._size)]
            self._dimnames = self._primary.dimnames
        elif (1,) in sizes:
            self._size = (1,)
            self._primary = self.values()[sizes.index(self._size)]
            self._dimnames = self._primary.dimnames
        else:
            self._size = ()
            self._primary = None
            self._dimnames = ()


class DefaultInputGroupCombiner(object):
    def __init__(self, input_groups):
        self.input_groups = input_groups
        self.update()

    def merge(self, list_of_items):
        """
        Given a list of items for each input group, it returns the combined
        list of items.

        :param list list_of_items: items to combine
        :return: combined list
        """
        return [x for item in list_of_items for x in item]

    def unmerge(self, item):
        """
        Given a item it will recreate the seperate items, basically this is the
        inverse operation of merge. However, this create an OrderedDict so that
        specific input groups can be easily retrieved. To get a round trip, the
        values of the OrderedDict should be taken::

            >>> list_of_items = combiner.unmerge(item)
            >>> item = combiner.merge(list_of_items.values())

        :param list item: the item to unmerge
        :return: items
        :rtype: OrderedDict
        """
        result = OrderedDict()
        for target in self.input_groups.values():
            mask = [True if ig.id == target.id else False for ig in self.input_groups.values() for _ in ig.size]
            result[target.id] = tuple(k for k, m in zip(item, mask) if m)

        return result

    @property
    def dimnames(self):
        return tuple(self.merge([ig.dimnames for ig in self.input_groups.values()]))

    @property
    def outputsize(self):
        return tuple(self.merge([ig.size for ig in self.input_groups.values()]))

    def merge_sample_id(self, list_of_sample_ids):
        return SampleId(self.merge(list_of_sample_ids))

    def merge_sample_index(self, list_of_sample_indexes):
        return SampleIndex(self.merge(list_of_sample_indexes))

    def merge_sample_data(self, list_of_sample_data):
        return {k: v if v is not None and len(v) > 0 else None for data in list_of_sample_data for k, v in data.items()}

    def merge_sample_jobs(self, list_of_sample_jobs):
        return set.union(*list_of_sample_jobs)

    def merge_payloads(self, sample_payloads):
        # Determine the sample index
        sample_index = self.merge_sample_index([x.index for x in sample_payloads])

        # Create sampleid
        sample_id = self.merge_sample_id([x.id for x in sample_payloads])

        # Extract jobdata and combine in single dict
        job_data = self.merge_sample_data(x.data for x in sample_payloads)

        # Create superset of all job dependencies
        job_depends = self.merge_sample_jobs(x.jobs for x in sample_payloads)

        return sample_index, sample_id, job_data, job_depends

    def iter_input_groups(self):
        for sample_payloads in itertools.product(*[ig.iterinputvalues for ig in self.input_groups.values()]):
            fastr.log.debug('sample_payload: {}'.format(sample_payloads))
            fastr.log.debug('sample payload data: {}'.format([x.data for x in sample_payloads]))
            yield self.merge_payloads(sample_payloads)

    def __iter__(self):
        return self.iter_input_groups()

    def update(self):
        pass


class MergingInputGroupCombiner(DefaultInputGroupCombiner):
    def __init__(self, input_groups, merge_dimension):
        self.merge_dimensions = merge_dimension
        self._merges = None
        self._merge_sizes = None
        self._masks = None
        super(MergingInputGroupCombiner, self).__init__(input_groups)

    def update(self):
        dimnames = [x.dimnames for x in self.input_groups.values()]
        sizes = [x.size for x in self.input_groups.values()]

        # Validate the sample dimensions and sizes are consistent
        unique_dimnames = tuple(set(x for dimname in dimnames for x in dimname))
        unique_sizes = {x: set() for x in unique_dimnames}

        for size, dimname in zip(sizes, dimnames):
            for size_element, dimname_element in zip(size, dimname):
                unique_sizes[dimname_element].add(size_element)
        if not all(len(x) == 1 for x in unique_sizes.values()):
            raise exceptions.FastrValueError('The dimension have incosistent sizes: {}'.format(unique_sizes))
        unique_sizes = {k: v.pop() for k, v in unique_sizes.items()}

        # Check how many merges to perform
        if self.merge_dimensions == 'all':
            counts = {name: [sum(x == name for x in dimname) for dimname in dimnames] for name in unique_dimnames}
            merges = {name: min(value) for name, value in counts.items()}
            merges = tuple(key for key, value in merges.items() for x in range(value))
        else:
            merges = tuple(self.merge_dimensions)

        self._merges = merges

        # Make a merge mask for the dimnames
        masks = []
        for dimname in dimnames:
            temp = []
            temp_merges = list(merges)
            for name in dimname:
                if name in temp_merges:
                    index = temp_merges.index(name)
                    temp.append(index)
                    temp_merges[index] = None
                else:
                    temp.append(slice(unique_sizes[name]))
            masks.append(temp)

        self._masks = masks

        # Do the actual merging
        self._merge_sizes = tuple(unique_sizes[x] for x in merges)

    def merge(self, list_of_items):
        new_item = [x for mask, item in zip(self._masks, list_of_items) for m, x in zip(mask, item) if isinstance(m, slice)]
        new_item.extend(x for x, m in zip(list_of_items[0], self._masks[0]) if not isinstance(m, slice))
        return new_item

    def unmerge(self, item):
        index = 0
        result = OrderedDict()
        nr_slices = sum(isinstance(x, slice) for y in self._masks for x in y)
        for input_group, mask in zip(self.input_groups, self._masks):
            original_item = []
            for m in mask:
                if isinstance(m, slice):
                    original_item.append(item[index])
                    index += 1
                else:
                    original_item.append(item[m + nr_slices])
            result[input_group] = tuple(original_item)

        return result

    def iter_input_groups(self):
        # Create iterator for the merged part of the iteration
        if len(self._merges) > 0:
            fixed_indexes = itertools.product(*[xrange(x) for x in self._merge_sizes])
        else:
            fixed_indexes = [()]

        # Loop over the fixed (merged) indices and then over the remainder
        for fixed_index in fixed_indexes:
            iterators = [itertools.product(*[xrange(m.stop) if isinstance(m, slice) else [fixed_index[m]] for m in mask]) for mask in self._masks]

            for indexes in itertools.product(*iterators):
                # Retrieve the samples from all input groups
                samples = []

                for index, input_group in zip(indexes, self.input_groups.values()):
                    try:
                        samples.append(input_group[SampleIndex(index)])
                    except exceptions.FastrIndexNonexistent:
                        samples.append(None)

                # Merge all sample payloads
                if all(x is not None for x in samples):
                    yield self.merge_payloads(samples)
                else:
                    fastr.log.info('Skipping {} because it is non-existent due to sparsity!'.format(indexes))


class Node(Updateable, Serializable):
    """
    The class encapsulating a node in the network. The node is responsible
    for setting and checking inputs and outputs based on the description
    provided by a tool instance.
    """

    __metaclass__ = ABCMeta
    __dataschemafile__ = 'Node.schema.json'

    _InputType = Input
    _OutputType = Output
    _JobType = Job

    def __init__(self, tool, id_=None, parent=None, cores=None, memory=None, walltime=None):
        """
        Instantiate a node.

        :param tool: The tool to base the node on
        :type tool: :py:class:`Tool <fastr.core.tool.Tool>`
        :param str id_: the id of the node
        :param parent: the parent network of the node
        :param int cores: number of cores required for executing this Node
        :param str memory: amount of memory required in the form \\d+[mMgG]
                           where M is for megabyte and G for gigabyte
        :param str walltime: amount of time required in second or in the form
                             HOURS:MINUTES:SECOND
        :type parent: :py:class:`Network <fastr.core.network.Network>`
        :return: the newly created Node
        """
        super(Node, self).__init__()

        if isinstance(tool, Tool):
            self._tool = tool
        elif isinstance(tool, (str, tuple)):
            if tool in fastr.toollist:
                self._tool = fastr.toollist[tool]
            else:
                message = ('Specified tool ({}) is not in the toollist: {}. '
                           'Check the config (fastr/resources/fastr.config)').format(tool,
                                                                                     fastr.toollist.todict().keys())
                fastr.log.critical(message)
                raise exceptions.FastrToolUnknownError(message)
        elif tool is None:
            self._tool = None
        else:
            message = 'tool should either be a string or a Tool.'
            fastr.log.critical(message)
            raise exceptions.FastrTypeError(message)

        # Don't set parent here, as not info needed for registration is there yet
        self._parent = None
        if parent is not None:
            parent = parent
        elif fastr.current_network is not None:
            parent = fastr.current_network
        else:
            message = 'Both parent argument and fastr.current_network are None, need a parent Network to function!'
            raise exceptions.FastrValueError(message)

        node_number = parent.node_number
        parent.node_number += 1

        if id_ is None:
            # Node ID is a simple $name_$counter format, making sure nodes can
            # not be named the same

            #: The Node id s a unique string identifying the Node
            id_ = 'node_{}_{}'.format(self.name, node_number)

        parent.check_id(id_)
        self._id = id_

        #: The parent is the Network this Node is part of
        self.parent = parent

        #: A list of inputs of this Node
        self.inputs = InputDict()

        #: A list of outputs of this Node
        self.outputs = OutputDict()

        # Create all inputs and outputs, if the class is set in the Tool file,
        # respect that, otherwise use the class default.
        if self._tool is not None:
            for name, input_ in self._tool.inputs.items():
                self.inputs[name] = self._InputType(self, input_)
            for name, output in self._tool.outputs.items():
                self.outputs[name] = self._OutputType(self, output)

        self._input_groups = OrderedDict()
        self.jobs = None

        # Set the job requirements
        self._required_cores = None
        self._required_memory = None
        self._required_time = None
        self.required_cores = cores
        self.required_memory = memory
        self.required_time = walltime

        # Set the flow control
        self._merge_dimensions = None
        self._input_group_combiner = None
        self.merge_dimensions = 'none'

        # Update Inputs and self (which calls Outputs)
        self.update()

    def __repr__(self):
        """
        Get a string representation for the Node

        :return: the string representation
        :rtype: str
        """
        if self._tool is not None:
            toolinfo = '(tool: {tool.id} v{tool.version!s})'.format(tool=self._tool)
        else:
            toolinfo = ''
        return_list = ['{} {} {}'.format(type(self).__name__, self.id, toolinfo)]

        # The "+ [8]" guarantees a minimum of 8 width and avoids empty lists
        width_input_keys = max([len(x) for x in self.inputs.keys()] + [8])
        width_input_types = max([len(x.datatype.id) for x in self.inputs.values()] + [8]) + 2
        width_output_keys = max([len(x) for x in self.outputs.keys()] + [8])
        width_output_types = max([len(x.datatype.id) for x in self.outputs.values()] + [8]) + 2

        return_list.append('{:^{}}  | {:^{}}'.format('Inputs', width_input_types + width_input_keys + 1,
                                                     'Outputs', width_output_types + width_output_keys + 1))
        return_list.append('-' * (width_input_keys + width_input_types + width_output_keys + width_output_types + 7))
        for (input_key, input_, output_key, output) in itertools.izip_longest(self.inputs.keys(), self.inputs.values(), self.outputs.keys(), self.outputs.values()):
            if input_ is None:
                input_id = ''
                input_type = ''
            else:
                input_id = input_key
                input_type = '({})'.format(input_.datatype.id)

            if output is None:
                output_id = ''
                output_type = ''
            else:
                output_id = output_key
                output_type = '({})'.format(output.datatype.id)

            return_list.append('{:{}} {:{}}  |  {:{}} {:{}}'.format(input_id, width_input_keys,
                                                                    input_type, width_input_types,
                                                                    output_id, width_output_keys,
                                                                    output_type, width_output_types))

        return '\n'.join(return_list)

    def __str__(self):
        """
        Get a string version for the Node

        :return: the string version
        :rtype: str
        """
        return "<{}: {}>".format(type(self).__name__, self.id)

    def __eq__(self, other):
        """Compare two Node instances with each other. This function ignores
        the parent and update status, but tests rest of the dict for equality.
        equality

        :param other: the other instances to compare to
        :type other: Node
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, Node):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['_parent']
        del dict_self['_status']
        del dict_self['_input_groups']
        del dict_self['jobs']
        del dict_self['_input_group_combiner']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['_parent']
        del dict_other['_status']
        del dict_other['_input_groups']
        del dict_other['jobs']
        del dict_other['_input_group_combiner']

        return dict_self == dict_other

    def __getstate__(self):
        """
        Retrieve the state of the Node

        :return: the state of the object
        :rtype dict:
        """
        state = super(Node, self).__getstate__()

        # Make id pretier in the result
        state['id'] = self.id

        state['inputs'] = [x.__getstate__() for x in self.inputs.values()]
        state['outputs'] = [x.__getstate__() for x in self.outputs.values()]

        state['tool'] = [self._tool.id, str(self._tool.command['version'])]

        # Add resource requirements
        state['required_cores'] = self._required_cores
        state['required_memory'] = self._required_memory
        state['required_time'] = self._required_time
        state['merge_dimensions'] = self._merge_dimensions

        return state

    def __setstate__(self, state):
        """
        Set the state of the Node by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        self.jobs = None

        if not hasattr(self, '_input_groups'):
            self._input_groups = OrderedDict()

        if 'id' in state:
            self._id = state['id']

        if 'parent' in state:
            parent = state['parent']
            del state['parent']
        else:
            parent = None

        self._tool = fastr.toollist[tuple(state['tool'])]

        # Create Input/Output objects
        inputlist = []
        for input_ in state['inputs']:
            if 'node' in input_:
                # Check if the expected Node id matches our current id
                if input_['node'] != state['id']:
                    raise exceptions.FastrParentMismatchError('This Input has different parent node!')
                del input_['node']

            # It can happen that this has been done by a subclass, check first
            if not isinstance(input_, BaseInput):
                description = self.tool.inputs[input_['id']]
                inputobj = self._InputType(self, description)
                inputobj._node = self
                inputobj.__setstate__(input_)
            else:
                inputobj = input_
            inputlist.append((inputobj.id, inputobj))

        outputlist = []
        for output in state['outputs']:
            if '_node' in output:
                # Check if the expected Node id matches our current id
                if output['_node'] != state['_id']:
                    raise exceptions.FastrParentMismatchError('This Input has different parent node!')
                del output['_node']

            # It can happen that this has been done by a subclass, check first
            if not isinstance(output, Output):
                description = self.tool.outputs[output['id']]
                outputobj = self._OutputType(self, description)
                outputobj.__setstate__(output)
            else:
                outputobj = output
            outputlist.append((outputobj.id, outputobj))

        self.inputs = InputDict(inputlist)
        self.outputs = OutputDict(outputlist)

        super(Node, self).__setstate__(state)

        self._parent = None
        if parent is not None:
            self.parent = parent
        elif fastr.current_network is not None:
            self.parent = fastr.current_network
        else:
            message = 'Both parent argument and fastr.current_network are None, need a parent Network to function!'
            raise exceptions.FastrValueError(message)

        self._required_cores = state['required_cores']
        self._required_memory = state['required_memory']
        self._required_time = state['required_time']

        self.merge_dimensions = state['merge_dimensions']

        self.update()

    @property
    def merge_dimensions(self):
        return self._merge_dimensions

    @merge_dimensions.setter
    def merge_dimensions(self, value):
        if isinstance(value, (str, unicode)):
            options = ['all', 'none']
            if value not in options:
                raise exceptions.FastrValueError('Invalid option {} given (valid options: {})'.format(value, options))
            self._merge_dimensions = value
            if value == 'none':
                self._input_group_combiner = DefaultInputGroupCombiner(self.inputgroups)
            elif value == 'all':
                self._input_group_combiner = MergingInputGroupCombiner(self.inputgroups, value)
        else:
            self._merge_dimensions = value
            self._input_group_combiner = MergingInputGroupCombiner(self.inputgroups, tuple(value))

    @classmethod
    def createobj(cls, state, network=None):
        if 'parent' not in state or not isinstance(state['parent'], fastr.Network):
            if network is not None:
                fastr.log.debug('Setting network to: {}'.format(network))
                state['parent'] = network
            else:
                fastr.log.debug('No network given for de-serialization')
        else:
            fastr.log.debug('Parent is already defined as: {}'.format(network))

        state = dict(state)

        return super(Node, cls).createobj(state, network)

    @property
    def blocking(self):
        """
        Indicate that the results of this Node cannot be determined without first executing the Node, causing a
        blockage in the creation of jobs. A blocking Nodes causes the Chunk borders.
        """
        for output in self.outputs.values():
            if output.blocking:
                fastr.log.info('Blocking because Output {} has cardinality {}'.format(output.fullid,
                                                                                      output.cardinality()))
                return True
        return False

    @property
    def dimnames(self):
        """
        Names of the dimensions in the Node output. These will be reflected
        in the SampleIdList of this Node.
        """
        return self._input_group_combiner.dimnames

    @property
    def fullid(self):
        """
        The full defining ID for the Node
        """
        return '{}/nodelist/{}'.format(self.parent.fullid, self.id)

    @property
    def inputgroups(self):
        """
        A list of inputgroups for this Node. An input group is InputGroup
         object filled according to the Node

        """
        return self._input_groups

    @property
    def outputsize(self):
        """
        Size of the outputs in this Node
        """
        # Get sizes of all input groups
        return self._input_group_combiner.outputsize

    @property
    def id(self):
        """
        The id of the Node
        """
        return self._id

    @property
    def listeners(self):
        """
        All the listeners requesting output of this node, this means the
        listeners of all Outputs and SubOutputs
        """
        return {l for output in self.outputs.values() for l in output.listeners}

    @property
    def name(self):
        """
        Name of the Tool the Node was based on. In case a Toolless Node was
        used the class name is given.
        """
        if hasattr(self, '_tool') and isinstance(self._tool, Tool):
            return self._tool.id
        else:
            return self.__class__.__name__

    @property
    def parent(self):
        """
        The parent network of this node.
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        """
        The parent network of this node. (setter)
        """
        if self._parent is value:
            return  # Setting to same value doesn't do anything

        if self._parent is not None:
            fastr.log.warning('EXCEPTION|FastrAttributeError| Cannot reset attribute once set {} --> {}'.format(self._parent.id, value.id))
            #raise exceptions.FastrAttributeError('Cannot reset attribute once set')


        self._parent = value
        self._parent.add_node(self)

    @property
    def required_cores(self):
        """
        Number of cores required for the execution of this Node
        """
        return self._required_cores

    @required_cores.setter
    def required_cores(self, value):
        """
        Number of cores required for the execution of this Node (setter)
        """
        if value is None:
            self._required_cores = value
        else:
            if not isinstance(value, int):
                raise TypeError('Required number of cores should be an integer or None')

            if value < 1:
                raise ValueError('Required number of cores should be above zero ({} < 1)'.format(value))

            self._required_cores = value

    @property
    def required_memory(self):
        """
        Amount of memory required for the execution of this Node. Follows
        the format \\d+[mMgG] so 500M or 4g would be valid ways to specify
        500 megabytes or 4 gigabyte of memory.
        """
        return self._required_memory

    @required_memory.setter
    def required_memory(self, value):
        """
        Amount of memory required for the execution of this Node. Follows
        the format \\d+[mMgG] so 500M or 4g would be valid ways to specify
        500 megabytes or 4 gigabyte of memory. (setter)
        """
        if value is None:
            self._required_memory = value
        else:
            if not isinstance(value, str):
                raise TypeError('Required number of cores should be a str or None')

            if re.match(r'^\d+[mMgG]$', value) is None:
                raise ValueError('Required memory should be in the form \\d+[mMgG] (found {})'.format(value))

            self._required_memory = value

    @property
    def required_time(self):
        """
        Amount of time required for the execution of this Node. Follows the
        format of a number of second or H:M:S, with H the number of hours,
        M the number of minutes and S the number of seconds.
        """
        return self._required_time

    @required_time.setter
    def required_time(self, value):
        """
        Amount of time required for the execution of this Node. Follows the
        format of a number of second or H:M:S, with H the number of hours,
        M the number of minutes and S the number of seconds. (setter)
        """
        if value is None:
            self._required_time = value
        else:
            if not isinstance(value, str):
                raise TypeError('Required number of cores should be a str or None')

            if re.match(r'^(\d*:\d*:\d*|\d+)$', value) is None:
                raise ValueError('Required memory should be in the form HH:MM:SS or MM:SS (found {})'.format(value))

            self._required_time = value

    @property
    def status(self):
        return self._status

    @property
    def tool(self):
        return self._tool

    def execute(self):
        """
        Execute the node and create the jobs that need to run

        :return: list of jobs to run
        :rtype: list of :py:class:`Jobs <fastr.execution.job.Job>`
        """
        self.update(False, False)

        # Make sure a Node is valid
        if not self.valid:
            message = 'Node {} is not valid'.format(self.fullid)
            fastr.log.error(message)
            fastr.log.error('Messages:\n{}'.format('\n'.join(self.messages)))
            raise exceptions.FastrNodeNotValidError(message)
        inputgroups = self.inputgroups

        # Define output size and dimension names
        ig_masters = [ig.primary.id for ig in inputgroups.values()]
        fastr.log.debug('size: {} dimnames: {} masters: {}'.format(self.outputsize, self.dimnames, ig_masters))

        # Prepare the output of the Node
        fastr.log.debug('Preparing {} with size {} and dimnames {}'.format(self.fullid, self.outputsize, self.dimnames))
        self.prepare()

        # Iterate over all combinations of inputgroups to create sets of data
        job_list = []

        fastr.log.debug('InputGroups: {}'.format(inputgroups.values()))
        fastr.log.debug('Inputs: {}'.format([x for ig in inputgroups.values() for x in ig.values()]))
        fastr.log.debug('Sources: {}'.format([x.source for ig in inputgroups.values() for x in ig.values()]))

        for sample_index, sample_id, job_data, job_depends in self._input_group_combiner:
            fastr.log.debug('----- START -----')
            fastr.log.debug('INDEX: {}'.format(sample_index))
            fastr.log.debug('SAMPLE_ID: {} {}'.format(repr(sample_id), sample_id))
            fastr.log.debug('JOBDATA: {}'.format(job_data))
            fastr.log.debug('JOBDEPS: {}'.format(job_depends))
            fastr.log.debug('------ END ------')

            job_list.append(self.create_job(sample_id, sample_index, job_data, job_depends))

        fastr.log.debug('joblist: {}'.format(job_list))
        fastr.log.debug('===== END execute_node =====')
        return job_list

    def set_result(self, job):
        """
        Incorporate result of a job into the Node.

        :param Type job: job of which the result to store
        """
        sample_id, sample_index = job.sample_id, job.sample_index
        # Replace following code by node.set_data(job.output_data) ? or something like it?
        for output in self.outputs.values():
            if output.id not in job.output_data:
                fastr.log.error('Could not find expected data for {} in {}!'.format(output.fullid, job.output_data))
                continue

            output_data = job.output_data[output.id]
            fastr.log.info('Setting data for blocking node: {} sample: {}'.format(output.fullid, sample_id))

            output_url = '{}/{}/{}'.format(self.parent.tmpurl, self.id, sample_id)
            parsed_url = urlparse.urlparse(output_url)

            output_values = [urlparse.urlunparse(('val',
                                                  parsed_url.netloc,
                                                  url.join(parsed_url.path, '__fastr_result__.pickle.gz'),
                                                  parsed_url.params,
                                                  'outputname={}&nr={}'.format(output.id, c),
                                                  '')) for c in range(len(output_data))]
            fastr.log.info('Setting collected for {} sample_id {} data: {}'.format(output.fullid,
                                                                                   sample_id,
                                                                                   output_values))
            output[sample_id, sample_index] = SampleItem(sample_index,
                                                         sample_id,
                                                         OrderedDict({0: tuple(output_values)}),
                                                         {job})
            self.jobs[sample_id] = job

    def create_job(self, sample_id, sample_index, job_data, job_dependencies, jobid=None, outputurl=None, **kwargs):
        """
        Create a job based on the sample id, job data and job dependencies.

        :param sample_id: the id of the corresponding sample
        :type sample_id: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param dict job_data: dictionary containing all input data for the job
        :param job_dependencies: other jobs that need to finish before this job can run
        :return: the created job
        :rtype: :py:class:`Job <fastr.execution.job.Job>`
        """
        fastr.log.info('Creating job for node {} sample id {!r}, index {!r}'.format(self.fullid, sample_id, sample_index))
        fastr.log.debug('Creating job for sample {} with data {}'.format(sample_id, job_data))

        # Determine subfolder name in tmp mount
        if outputurl is None:
            outputurl = '{}/{}/{}'.format(self.parent.tmpurl, self.id, sample_id)

        # Determine absolute location of output dir and create directory
        outputdir = url.get_path_from_url(outputurl)

        fastr.log.debug('Sample ID: {}'.format(sample_id))
        fastr.log.debug('VFS Output dir: {}'.format(outputurl))

        # Remove output directory if there is old stuff present
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        if not os.path.exists(outputdir):
            fastr.log.critical('Could not create output directory {}!'.format(outputdir))

        # Get the arguments
        input_arguments, output_arguments = self._wrap_arguments(job_data, sample_id, sample_index)

        preferred_types = {output.id: output.preferred_types for output in self.outputs.values()}

        if jobid is None:
            jobid = '{}___{}___{}'.format(self.parent.id, self.id, sample_id)
        fastr.log.debug('Job tempdir set to: {}'.format(outputurl))
        job = self._JobType(jobid, self._tool.id, self._tool.command['version'], self.fullid, sample_id, sample_index, input_arguments, output_arguments, outputurl, [j.jobid for j in job_dependencies], cores=self.required_cores, memory=self.required_memory, walltime=self.required_time, status_callback=self.parent.job_status_callback, preferred_types=preferred_types, **kwargs)
        self.jobs[sample_id] = job

        # Check which outputs are required or connected and set them
        if not self.blocking:
            for output in self.outputs.itervalues():
                fastr.log.debug('Preparing output {}'.format(output.id))
                if output.required or len(output.listeners) > 0:
                    fastr.log.debug('Setting {}'.format(output.id))
                    value = []
                    fastr.log.debug('Cardinality request: spec: {}, job_data: {}, and index: {}'.format(output.cardinality_spec, job_data, sample_index))
                    cardinality = output.cardinality(sample_index, job_data)
                    fastr.log.debug('Cardinality for {} is {}'.format(output.id, cardinality))
                    if not isinstance(cardinality, int):
                        message = 'For execution cardinality should be an int, for output ' \
                                  '{} we found {} (type {})'.format(output.id,
                                                                    cardinality,
                                                                    type(cardinality).__name__)
                        fastr.log.critical(message)
                        raise exceptions.FastrTypeError(message)

                    for cardinality_nr in range(0, cardinality):
                        parsed_url = urlparse.urlparse(outputurl)
                        value.append(urlparse.urlunparse(('val',
                                                          parsed_url.netloc,
                                                          url.join(parsed_url.path, '__fastr_result__.pickle.gz'),
                                                          parsed_url.params,
                                                          'outputname={}&nr={}'.format(output.id, cardinality_nr),
                                                          '')))

                    output[sample_id] = SampleItem(sample_index,
                                                   sample_id,
                                                   {0: tuple(value)},
                                                   {job})
        else:
            fastr.log.debug('Cannot determine blocking node output a priori! Needs to be collected afterwards!')

        return job

    def _wrap_arguments(self, job_data, sample_id, sample_index):
        """
        Wrap arguments into a list of tuples that the execution script can parse

        :param dict job_data: dictionary containing all input data for the job
        :param sample_id: the id of the corresponding sample
        :type sample_id: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the wrapped arguments in a tuple with the form ``(inputs, outputs)``
        """
        arguments = ({}, {})  # format is (input_args, output_args)
        for key, input_ in self.inputs.items():
            # Skip inputs that have no data
            if job_data[key] is None:
                if input_.default is not None:
                    # Insert the default data if present
                    job_data[key] = [input_.datatype(input_.default)]
                elif input_.required:
                    fastr.log.debug('Job data: {}'.format(job_data))
                    raise exceptions.FastrValueError('Node "{}" is missing data for required Input "{}"'.format(self.id, input_.id))
                else:
                    continue

            arguments[0][key] = job_data[key]

        for key, output in self.outputs.items():
            if not output.automatic:
                cardinality = output.cardinality(job_data)
                arguments[1][key] = {'id': key,
                                     'cardinality': cardinality if cardinality is not None else output._output_cardinality,
                                     'datatype': output.resulting_datatype.id}

        return arguments

    def get_sourced_nodes(self):
        """
        A list of all Nodes connected as sources to this Node

        :return: list of all nodes that are connected to an input of this node
        """
        return list(set([n for input_ in self.inputs.values() for n in input_.get_sourced_nodes()]))

    def find_source_index(self, target_index, target, source):
        # If there are multiple inputgroups, select only part of index from
        # the inputgroup which source belongs to
        if len(self.inputgroups) > 1:
            inputgroups = self.inputgroups
            mask = [True if ig.id == source.input_group else False for ig in inputgroups.values() for _ in ig.size]
            target_index = tuple(k for k, m in zip(target_index, mask) if m)

        # Delegate to InputGroup to check mixing within InputGroup
        return self.inputgroups[source.input_group].find_source_index(target_size=target.size,
                                                                      target_dimnames=target.dimnames,
                                                                      source_size=source.size,
                                                                      source_dimnames=source.dimnames,
                                                                      target_index=target_index)

    def prepare(self):
        """
        Prepare the node for execution. It will create a SampleIdList of the
        correct size and prepare the outputs.
        """
        fastr.log.info('Preparing Node {} with size {} and dimnames {}'.format(self.id, self.outputsize, self.dimnames))
        if self.jobs is not None:
            raise exceptions.FastrNodeAreadyPreparedError('This Node has been previously prepared, cannot prepare '
                                                          'again as this will cause data loss!')

        self.jobs = {}

        for output in self.outputs.values():
            output.prepare()

    def _update(self, key, forward=True, backward=False):
        """
        Update the Node information and validity of the Node and propagate
         the update downstream. Updates inputs, inputgroups, outputsize and outputs.

        A Node is valid if:

        * All Inputs are valid (see :py:meth:`Input.update <fastr.core.inputoutput.Input.update>`)
        * All InputGroups are non-zero sized

        An Node is ready if:

        * The Node is valid
        * All Inputs are ready (see :py:meth:`Input.update <fastr.core.inputoutput.Input.update>`)

        """
        # Make sure the Inputs and input groups are up to date
        # fastr.log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.id))

        if backward:
            for sourced_node in self.get_sourced_nodes():
                sourced_node.update(key, False, backward)

        for input_ in self.inputs.values():
            input_.update(key, forward, backward)

        self.update_inputgroups()
        self._input_group_combiner.input_groups = self.inputgroups
        self._input_group_combiner.update()

        # Update own status
        valid = True
        ready = True
        messages = []

        for id_, input_ in self.inputs.items():
            if not input_.valid:
                valid = False
                for message in input_.messages:
                    messages.append('[{}] Input {} is not valid: {}'.format(self.id, input_.id, message))
            if not input_.ready:
                ready = False

        for input_group in self.inputgroups.values():
            if input_group.empty:
                valid = False
                messages.append('[{}] InputGroup {} is empty'.format(self.id, input_group.id))

        for id_, output in self.outputs.items():
            if output.resulting_datatype is not None:
                if not issubclass(output.resulting_datatype, DataType):
                    valid = False
                    messages.append('[{}] Output {} cannot determine the Output DataType (got {}), please specify a '
                                    'valid DataType or add casts to the Links'.format(self.id, id_, output.resulting_datatype))

        self._status['valid'] = valid
        self._status['messages'] = messages
        self._status['ready'] = (valid and ready)

        # Update all outputs
        for output in self.outputs.values():
            output.update(key, forward, backward)

        # Update all downstream listeners
        if forward:
            for listener in self.listeners:
                listener.update(key, forward, False)

    def update_inputgroups(self):
        """
        Update all input groups in this node
        """
        input_groups = OrderedDict()

        for input_ in self.inputs.values():
            if input_.input_group not in input_groups:
                input_groups[input_.input_group] = InputGroup(self, input_.input_group)
            input_groups[input_.input_group][input_.id] = input_

        self._input_groups = input_groups


class MacroNode(Node):
    """
    MacroNode encapsulates an entire network in a single node.
    """
    def __init__(self, network, id_=None, parent=None, cores=None, memory=None, walltime=None):
        """
        :param network: network to create macronode for
        :type network: Network
        """
        super(MacroNode, self).__init__(None, id_, parent=parent, cores=cores, memory=memory, walltime=walltime)

        # If macronode is loaded as a tool retrieve macro definition file(.py .xml .pickle .json) location
        if isinstance(network, Tool):
            # Check if Macro Definition in Tool is absolute Path or Relative
            if os.path.isabs(network.target.binary):
                network_path = network.target.binary
            else:
                network_location = os.path.dirname(network.filename)
                network_file = network.target.binary
                if network.target._paths[0]['type'] == 'bin':
                    network_relative_path = network.target._paths[0]['value']
                else:
                    network_relative_path = ''
                network_path = os.path.join(network_location, network_relative_path, network_file)
            # Check if macro definition exists.
            if not os.path.isfile(network_path):
                message = 'MacroNode \'{}\' definition file {} does not exist'.format(network.id, network_path)
                fastr.log.critical(message)
                raise exceptions.FastrTypeError(message)
            network = network_path

        # If network is an existing network
        if isinstance(network, fastr.Network):
            self._network = network
        # else if network is string(assume it is location to macro definition
        elif isinstance(network, (str, unicode)):
            # Check if file exists
            if not os.path.isfile(network):
                message = 'MacroNode definition file {} does not exist'.format(network)
                fastr.log.critical(message)
                raise exceptions.FastrTypeError(message)
            # If macro is python file
            if network.endswith('.py'):
                # py
                network_loader = imp.load_source('macro_node.utils', network)
                self._network = network_loader.main()
            # Else assume xml json pickkle
            else:
                # xml pickle, json, etc
                self._network = fastr.Network.loadf(network)
        # Else produce error
        else:
            message = 'Macro node should either be a Network a MacroTool or a FileName'
            fastr.log.critical(message)
            raise exceptions.FastrTypeError(message)

        try:
            self._network.is_valid()
            self._add_to_parent()
        except:
            message='Macro Node: {} is not a valid network'.format(id_)
            fastr.log.critical(message)
            raise exceptions.FastrValueError(message)

    def _add_to_parent(self):
        parent = self.parent
        id_ = self.id

        parent.add_stepid(id_, self)
        # Go through nodes and add them to the parent network
        for id, node in self._network.toolnodelist.iteritems():
            node._id = node.id + "__" + id_
            parent.add_stepid(id_, node)
            parent.add_node(node)

        # Go through source to set as macro node input
        for id, source in self._network.sourcelist.iteritems():
            self.inputs[id] = source.output.listeners[0].target.parent

        # Go through constants to set as non-required inputs
        for id, constant in self._network.constantlist.iteritems():
            self.inputs[id] = constant.output.listeners[0].target.parent
            constant._id = constant.id + "__" + id_
            parent.add_stepid(id_, constant)
            parent.add_node(constant)

        # Go through sinks to set as output
        for id, sink in self._network.sinklist.iteritems():
            self.outputs[id] = sink.input.get_sourced_outputs()[0]

        # Go through all links
        for id, link in self._network.linklist.iteritems():
            #if (not isinstance(link.source.node, SourceNode) and not isinstance(link.target.node,SinkNode)):
            source_node = link.source.node
            target_node = link.target.node
            if (not type(source_node) == SourceNode and not isinstance(target_node, SinkNode)):
                link.id = link.id + "__" + id_
                fastr.log.info('New link_id: {}'.format(link.id))
                link._parent = parent
                parent.add_link(link)

    def __getstate__(self):
        """
        Retrieve the state of the MacroNode

        :return: the state of the object
        :rtype dict:
        """
        state = super(MacroNode, self).__getstate__()
        state['network'] = self._network.__getstate__()
        return state

    def __setstate__(self, state):
        super(MacroNode, self).__setstate__(state)
        self._add_to_parent()

    def execute(self):
        raise exceptions.FastrNotImplementedError


class FlowNode(Node):
    """
    A Flow Node is a special subclass of Nodes in which the amount of samples
    can vary per Output. This allows non-default data flows.
    """
    _OutputType = Output

    def __init__(self, tool, id_=None, parent=None, cores=None, memory=None, walltime=None):
        """
        Instantiate a flow node.

        :param tool: The tool to base the node on
        :type tool: :py:class:`Tool <fastr.core.tool.Tool>`
        :param str id_: the id of the node
        :param parent: the parent network of the node
        :type parent: :py:class:`Network <fastr.core.network.Network>`
        :return: the newly created FlowNode
        """
        super(FlowNode, self).__init__(tool, id_, parent=parent, cores=cores, memory=memory, walltime=walltime)

        self._input_groups = OrderedDict()
        self.jobs = None

        # Update Inputs and self (which calls Outputs)
        self.update()

    @property
    def blocking(self):
        """
        A FlowNode is (for the moment) always considered blocking.

        :return: True
        """
        return True

    @property
    def outputsize(self):
        """
        Size of the outputs in this Node
        """
        # Get sizes of all input groups
        output_size = []
        for input_group in self.inputgroups.values():
            if input_group.size is not None:
                output_size.extend(input_group.size)
            else:
                return None

        output_size.append(sympy.symbols('N_{}'.format(self.id)))
        return tuple(output_size)

    @property
    def dimnames(self):
        """
        Names of the dimensions in the Node output. These will be reflected
        in the SampleIdList of this Node.
        """
        return super(FlowNode, self).dimnames + (self.id,)

    def set_result(self, job):
        """
        Incorporate result of a job into the FlowNode.

        :param Type job: job of which the result to store
        """
        fastr.log.info('Job output data: {}'.format(job.output_data))

        # Get the main sample index from the Job
        sample_index = job.sample_index

        for output in self.outputs.values():
            if output.id not in job.output_data:
                fastr.log.error('Could not find expected data for {} in {}!'.format(output.fullid, job.output_data))
                continue

            output_data = job.output_data[output.id]

            fastr.log.debug('output_data = {}'.format(output_data))

            # Make sure dictionary is sorted, can also be list of items
            # which will be kept ordered
            if isinstance(output_data, dict):
                data = sorted(output_data.items())

            if not all(isinstance(x, (list, tuple)) and len(x) == 2 for x in data):
                raise exceptions.FastrValueError('The output data for a FlowNode should be a dictionary or a list of items (length 2 per entry)')

            for sample_nr, (sample_id, sample_data) in enumerate(data):
                orig_sample_id = sample_id

                # Ensure we have a SampleId (cast if need be)
                if not isinstance(sample_id, SampleId):
                    # Make sure sample_id is built from a tuple of str
                    if isinstance(sample_id, (str, unicode)):
                        sample_id = (str(sample_id),)
                    else:
                        sample_id = tuple(str(x) for x in sample_id)

                    sample_id = SampleId(sample_id)

                    fastr.log.debug('Change sample_id from {} ({}) to {} ({})'.format(orig_sample_id,
                                                                                      type(orig_sample_id).__name__,
                                                                                      sample_id,
                                                                                      type(sample_id).__name__))

                if len(sample_id) != output.ndims:
                    sample_id = job.sample_id + sample_id
                    fastr.log.debug('Updated sample_id to {}'.format(sample_id))
                    if len(sample_id) != output.ndims:
                        raise exceptions.FastrValueError('Sample ID {} has the wrong dimensionality!'.format(sample_id))

                fastr.log.debug('Setting data for blocking node: {} sample: {}'.format(output.fullid, sample_id))

                parsed_url = urlparse.urlparse(job.logurl)

                output_values = [type(sample_date_value)(urlparse.urlunparse(('val',
                                                                              parsed_url.netloc,
                                                                              parsed_url.path,
                                                                              parsed_url.params,
                                                                              'outputname={}&nr={}&sampleid={}'.format(output.id,
                                                                                                                       c,
                                                                                                                       orig_sample_id),
                                                                              ''))) for c, sample_date_value in enumerate(sample_data)]

                fastr.log.debug('Setting collected for {} sample_id {} sample_index {!r} data: {}'.format(output.fullid,
                                                                                                          sample_id,
                                                                                                          sample_index + (sample_nr),
                                                                                                          output_values))

                # Save with sample_index and sample nr in the extra dimension
                output[sample_id, sample_index + (sample_nr)] = SampleItem(sample_index + (sample_nr),
                                                                           sample_id,
                                                                           OrderedDict({0: tuple(output_values)}),
                                                                           {job})

                # Register the samples parent job
                self.jobs[sample_id] = job


class AdvancedFlowNode(FlowNode):
    _OutputType = AdvancedFlowOutput

    def execute(self):
        """
        Execute the node and create the jobs that need to run

        :return: list of jobs to run
        :rtype: list of :py:class:`Jobs <fastr.execution.job.Job>`
        """
        self.update(False, False)

        # Make sure a Node is valid
        if not self.valid:
            message = 'Node {} is not valid'.format(self.fullid)
            fastr.log.error(message)
            fastr.log.error('Messages:\n{}'.format('\n'.join(self.messages)))
            raise exceptions.FastrNodeNotValidError(message)
        inputgroups = self.inputgroups

        # Define output size and dimension names
        ig_masters = [ig.primary.id for ig in inputgroups.values()]
        fastr.log.debug('size: {} dimnames: {} masters: {}'.format(self.outputsize, self.dimnames, ig_masters))

        # Prepare the output of the Node
        fastr.log.debug('Preparing {} with size {} and dimnames {}'.format(self.fullid, self.outputsize, self.dimnames))
        self.prepare()

        # Iterate over all combinations of inputgroups to create sets of data
        dimnames = [x for ig in self.inputgroups.values() for x in ig.dimnames]

        fastr.log.debug('InputGroups: {}'.format(inputgroups.values()))
        fastr.log.debug('Inputs: {}'.format([x for ig in inputgroups.values() for x in ig.values()]))
        fastr.log.debug('Sources: {}'.format([x.source for ig in inputgroups.values() for x in ig.values()]))

        data = {x.id: x.items() for x in self.inputs.values()}
        target = self.tool.target

        with target:
            result = self.tool.interface.execute(target, data)

        for output, data in result.result_data.items():
            for key, value in data.items():
                self.outputs[output][key] = value

        return []


class SourceNode(FlowNode):
    """
    Class providing a connection to data resources. This can be any kind of
    file, stream, database, etc from which data can be received.
    """

    __dataschemafile__ = 'SourceNode.schema.json'
    _OutputType = SourceOutput
    _JobType = SourceJob

    def __init__(self, datatype, id_=None):
        """
        Instantiation of the SourceNode.

        :param datatype: The (id of) the datatype of the output.
        :param id_: The url pattern.

        This class should never be instantiated directly (unless you know what
        you are doing). Instead create a source using the network class like
        shown in the usage example below.

        usage example:

        .. code-block:: python

          >>> import fastr
          >>> network = fastr.Network()
          >>> source = network.create_source(datatype=fastr.typelist['ITKImageFile'], id_='sourceN')
        """
        tool = fastr.toollist['Source']

        super(SourceNode, self).__init__(tool, id_)

        self._input_groups = []

        self.jobs = None

        # Set the DataType
        if datatype in fastr.typelist:
            if isinstance(datatype, str):
                datatype = fastr.typelist[datatype]
        else:
            message = 'Invalid DataType for SourceNode {} (found {})!'.format(self.fullid, datatype)
            fastr.log.critical(message)
            raise exceptions.FastrValueError(message)

        self.datatype = datatype
        self._input_data = None
        self._outputsize = None
        self.outputsize = 'N_{}'.format(self.id)

    def __eq__(self, other):
        """Compare two Node instances with each other. This function ignores
        the parent and update status, but tests rest of the dict for equality.
        equality

        :param other: the other instances to compare to
        :type other: Node
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, SourceNode):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['_parent']
        del dict_self['_status']
        del dict_self['_input_groups']
        del dict_self['_input_data']
        del dict_self['_outputsize']
        del dict_self['_input_group_combiner']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['_parent']
        del dict_other['_status']
        del dict_other['_input_groups']
        del dict_other['_input_data']
        del dict_other['_outputsize']
        del dict_other['_input_group_combiner']

        return dict_self == dict_other

    def __getstate__(self):
        """
        Retrieve the state of the SourceNode

        :return: the state of the object
        :rtype dict:
        """
        state = super(SourceNode, self).__getstate__()

        return state

    def __setstate__(self, state):
        """
        Set the state of the SourceNode by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(SourceNode, self).__setstate__(state)

        self._input_data = None
        self._outputsize = None
        self.outputsize = 'N_{}'.format(self.id)

    @property
    def datatype(self):
        """
        The datatype of the data this source supplies.
        """
        return self.outputs['output'].datatype

    @datatype.setter
    def datatype(self, value):
        """
        The datatype of the data this source supplies. (setter)
        """
        self.outputs['output'].datatype = value

    @property
    def sourcegroup(self):
        for name, group in self.parent.sourcegroups.items():
            if self.id in group:
                return name
        return None

    @property
    def dimnames(self):
        """
        Names of the dimensions in the SourceNode output. These will be reflected
        in the SampleIdLists.
        """
        if self.sourcegroup is not None:
            return self.sourcegroup,
        else:
            return self.id,

    @property
    def output(self):
        """
        Shorthand for ``self.outputs['output']``
        """
        return self.outputs['output']

    @property
    def outputsize(self):
        """
        The size of output of this SourceNode
        """
        return self._outputsize

    @outputsize.setter
    def outputsize(self, value):
        # it seems pylint does not realize this is part of a property
        # pylint: disable=arguments-differ
        if isinstance(value, str):
            self._outputsize = (sympy.symbols(value),)
        elif isinstance(value, int):
            self._outputsize = (value,)
        else:
            try:
                self._outputsize = [x if isinstance(x, int) else sympy.symbols(x.replace(' ', '_')) for x in value]
            except TypeError:
                raise exceptions.FastrTypeError('Not a valid input type')

    @property
    def valid(self):
        """
        This does nothing. It only overloads the valid method of Node().
        The original is intended to check if the inputs are connected to
        some output. Since this class does not implement inputs, it is skipped.
        """
        return True

    def execute(self):
        """
        Execute the source node and create the jobs that need to run

        :return: list of jobs to run
        :rtype: list of :py:class:`Jobs <fastr.execution.job.Job>`
        """
        self.update(False, False)

        if not self.ready or self._input_data is None:
            msg = 'Cannot executed a SourceNode that is not ready! Messages:\n{}'.format('\n'.join(self.messages))
            fastr.log.error(msg)
            raise exceptions.FastrValueError(msg)

        joblist = []

        self.prepare()
        for index, (sampleid, value) in enumerate(self._input_data.items()):
            sample_index = SampleIndex(index)

            if all(not url.isurl(x) for x in value):
                # A simple string should not be send to IOPlugin for procesing
                fastr.log.debug('No job needed for sample {} at {}'.format(sampleid, self.fullid))
                self.jobs[sampleid] = None
                output_value = []

                for subvalue in value:
                    # it appears pylint does not realize that self.datatype is a class
                    # pylint: disable=not-callable
                    if self.datatype.isinstance(subvalue):
                        output_value.append(subvalue)
                    else:
                        output_value.append(self.datatype(subvalue))

                self.outputs['output'][sampleid, sample_index + (0,)] = SampleItem(sample_index + (0,),
                                                                                   sampleid,
                                                                                   {0: tuple(output_value)},
                                                                                   set())
            else:
                # We found an URL, should be
                fastr.log.debug('Spawning job for sample {} at {}'.format(sampleid, self.fullid))
                joblist.append(self.create_job(sampleid, sample_index, {'input': value}, []))

        return joblist

    def create_job(self, sample_id, sample_index, job_data, job_dependencies):
        job = super(SourceNode, self).create_job(sample_id, sample_index, job_data, job_dependencies)
        job._datatype = self.datatype.id
        return job

    def _wrap_arguments(self, job_data, sample_id, sample_index):
        """
        Wrap arguments into a list of tuples that the execution script can parse

        :param dict job_data: dictionary containing all input data for the job
        :param sample_id: the id of the corresponding sample
        :type sample_id: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the wrapped arguments in a tuple with the form ``(inputs, outputs)``

        .. note::
            For a SourceNode this function adds a few default (hidden) arguments
        """
        fastr.log.debug('Wrapping SourceNode with {}'.format(job_data))
        arguments = super(SourceNode, self)._wrap_arguments(job_data, sample_id, sample_index)
        arguments[0]['input'] = job_data['input']
        arguments[0]['behaviour'] = ('source',)
        arguments[0]['datatype'] = (self.datatype.id,)
        arguments[0]['sample_id'] = (str(sample_id),)

        outputurl = '{}/{}/{}/result'.format(self.parent.tmpurl, self.id, '__'.join(sample_id))
        outputpath = fastr.vfs.url_to_path(outputurl)
        if not os.path.exists(outputpath):
            os.makedirs(outputpath)
        arguments[0]['targetdir'] = (outputurl,)

        return arguments

    def set_data(self, data, ids=None):
        """
        Set the data of this source node.

        :param data: the data to use
        :type data: dict, OrderedDict or list of urls
        :param ids: if data is a list, a list of accompanying ids
        """
        self._input_data = OrderedDict()

        # Check if data has key or generate keys
        fastr.log.debug('Storing {} (ids {}) in {}'.format(data, ids, self.fullid))
        if isinstance(data, dict):
            # Have data sorted on ids
            ids, data = zip(*sorted(data.items()))
            ids = [SampleId(x) for x in ids]
        elif isinstance(data, OrderedDict):
            ids, data = data.keys(), data.values()
        elif isinstance(data, list):
            if ids is None:
                ids = [SampleId('id_{}'.format(k)) for k in range(len(data))]
            elif not isinstance(ids, list):
                raise exceptions.FastrTypeError('Invalid type! The ids argument should be a list that matches the data samples!')
        elif isinstance(data, tuple):
            # A single sample with cardinality
            ids = [SampleId('id_0')]
            data = [data]
        else:
            ids = [SampleId('id_0')]
            data = [data]

        fastr.log.debug('Set data in {} with {} (Type {})'.format(self.id, data, self.datatype))

        for key, value in zip(ids, data):
            if isinstance(value, tuple):
                self._input_data[key] = tuple(x if self.datatype.isinstance(x) else str(x) for x in value)
            else:
                self._input_data[key] = (value if self.datatype.isinstance(value) else str(value),)
            fastr.log.debug('Result {}: {} (Type {})'.format(key, self._input_data[key], type(self._input_data[key]).__name__))

        self._status['ready'] = True
        self.outputsize = len(self._input_data),

    def _update(self, key, forward=True, backward=False):
        """
        Update the Node information and validity of the Node and propagate
         the update downstream. Updates inputs, inputgroups, outputsize and outputs.

        A Node is valid if:

        * All Inputs are valid (see :py:meth:`Input.update <fastr.core.inputoutput.Input.update>`)
        * All InputGroups are non-zero sized

        An Node is ready if:

        * The Node is valid
        * All Inputs are ready (see :py:meth:`Input.update <fastr.core.inputoutput.Input.update>`)

        """
        # Make sure the Inputs and input groups are up to date
        # fastr.log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.id))

        for input_ in self.inputs.values():
            input_.update(key)

        self.update_inputgroups()

        # Update own status
        valid = True
        ready = True
        messages = []

        for id_, input_ in self.inputs.items():
            if not input_.valid:
                valid = False
                for message in input_.messages:
                    messages.append('Input {} is not valid: {}'.format(id_, message))
            if not input_.ready:
                ready = False

        for input_group in self.inputgroups.values():
            if input_group.empty:
                valid = False
                messages.append('InputGroup {} is empty'.format(input_group.id))

        for id_, output in self.outputs.items():
            if output.resulting_datatype is not None:
                if not issubclass(output.resulting_datatype, DataType):
                    valid = False
                    messages.append(
                        'Output {} cannot determine the Output DataType (got {}), '
                        'please specify a valid DataType or add casts to the Links'.format(
                            id_, output.resulting_datatype))

        self._status['valid'] = valid
        self._status['messages'] = messages
        self._status['ready'] = (valid and ready)

        # Update all outputs
        for output in self.outputs.values():
            output.update(key)

        # Update all downstream listeners
        if forward:
            for listener in self.listeners:
                listener.update(key, forward, backward)


class SinkNode(Node):
    """
    Class which handles where the output goes. This can be any kind of file, e.g.
    image files, textfiles, config files, etc.
    """

    __dataschemafile__ = 'SinkNode.schema.json'
    _JobType = SinkJob

    def __init__(self, datatype, id_=None):
        """ Instantiation of the SourceNode.

        :param datatype: The datatype of the output.
        :param id_: the id of the node to create
        :return: newly created sink node

        usage example:

        .. code-block:: python

          >>> import fastr
          >>> network = fastr.Network()
          >>> sink = network.create_sink(datatype=fastr.typelist['ITKImageFile'], id_='SinkN')

        """
        Node.__init__(self, fastr.toollist['Sink'], id_)
        # Set the DataType
        if datatype in fastr.typelist:
            if isinstance(datatype, str):
                datatype = fastr.typelist[datatype]
        else:
            message = 'Invalid DataType for SinkNode {} (found {})!'.format(self.fullid, datatype)
            fastr.log.critical(message)
            raise exceptions.FastrValueError(message)

        self.datatype = datatype
        # TODO: this code cannot function, need to find a work-around
        #self._tool.inputs['input'].datatype = datatype
        self.url = None

    def __getstate__(self):
        state = super(SinkNode, self).__getstate__()
        state['url'] = self.url
        return state

    def __setstate__(self, state):
        super(SinkNode, self).__setstate__(state)
        self.url = state['url']

    @property
    def datatype(self):
        """
        The datatype of the data this sink can store.
        """
        return self.inputs['input'].datatype

    @datatype.setter
    def datatype(self, value):
        """
        The datatype of the data this sink can store (setter).
        """
        self.inputs['input'].datatype = value

    @property
    def input(self):
        """
        The default input of the sink Node
        """
        return self.inputs['input']

    @input.setter
    def input(self, value):
        """
        The default input of the sink Node (setter)
        """
        self.inputs['input'] = value

    def execute(self):
        """
        Execute the sink node and create the jobs that need to run

        :return: list of jobs to run
        :rtype: list of :py:class:`Jobs <fastr.execution.job.Job>`
        """
        self.update(False, False)

        joblist = []

        self.prepare()

        for sample_index, sampleid, data, jobs in self.inputs['input'].iteritems():
            for cardinality_nr, value in enumerate(data.sequence_part()):
                fastr.log.debug('Spawning job for {}'.format(self.inputs['input'].fullid))
                joblist.append(self.create_job(sampleid, sample_index, {'input': SampleItem(sample_index, sampleid, SampleValue({0: (value,)})), 'cardinality': cardinality_nr}, jobs))

        return joblist

    def set_data(self, data):
        """
        Set the targets of this sink node.

        :param data: the targets rules for where to write the data
        :type data: dict or list of urls

        The target rules can include a few fields that can be filled out:

        =========== ==================================================================
        field       description
        =========== ==================================================================
        sample_id   the sample id of the sample written in string form
        cardinality the cardinality of the sample written
        ext         the extension of the datatype of the written data, including the .
        =========== ==================================================================

        An example of a valid target could be:

        .. code-block:: python

          >>> target = 'vfs://output_mnt/some/path/image_{sample_id}_{cardinality}{ext}'

        """
        if isinstance(data, (str, unicode)):
            try:
                data.format(sample_id='dummy', cardinality=0, ext='.ext')
            except KeyError as error:
                raise exceptions.FastrValueError('Using unknown substitution "{}" in SinkData "{}", valid substitution fields are: sample_id, cardinality, ext'.format(error.message, data))
            self.url = data
            self._status['ready'] = True
        else:
            raise exceptions.FastrTypeError('Invalid datatype for SinkNode data, expected str but got {}!'.format(type(data).__name__))

    def create_job(self, sample_id, sample_index, job_data, job_dependencies):
        """
        Create a job for a sink based on the sample id, job data and job dependencies.

        :param sample_id: the id of the corresponding sample
        :type sample_id: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param dict job_data: dictionary containing all input data for the job
        :param job_dependencies: other jobs that need to finish before this job can run
        :return: the created job
        :rtype: :py:class:`Job <fastr.execution.job.Job>`
        """

        # Create new jobid
        jobid = '{}___{}___{}___{}'.format(self.parent.id, self.id, sample_id, job_data['cardinality'])

        # Determine new tmp dir
        outputurl = '{}/{}/{}__{}'.format(self.parent.tmpurl, self.id, sample_id, job_data['cardinality'])

        substitutions = {'sample_id': sample_id, 'cardinality': job_data['cardinality']}

        job = super(SinkNode, self).create_job(sample_id, sample_index, job_data, job_dependencies, jobid=jobid, outputurl=outputurl, substitutions=substitutions)

        self.jobs[sample_id] = job
        return job

    def _wrap_arguments(self, job_data, sample_id, sample_index):
        """
        Wrap arguments into a list of tuples that the execution script can parse

        :param dict job_data: dictionary containing all input data for the job
        :param sample_id: the id of the corresponding sample
        :type sample_id: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the wrapped arguments in a tuple with the form ``(inputs, outputs)``

        .. note::
            For a SinkNode this function adds a few default (hidden) arguments
        """
        arguments = super(SinkNode, self)._wrap_arguments(job_data, sample_id, sample_index)
        arguments[0]['behaviour'] = ('sink',)
        arguments[0]['output'] = (self.url,)
        arguments[0]['datatype'] = (self.datatype.id,)

        fastr.log.debug('Wrapped Sink arguments to {}'.format(arguments))
        return arguments


class ConstantNode(SourceNode):
    """
    Class encapsulating one output for which a value can be set. For example
    used to set a scalar value to the input of a node.
    """

    __dataschemafile__ = 'ConstantNode.schema.json'

    def __init__(self, datatype, data, id_=None):
        """
        Instantiation of the ConstantNode.

        :param datatype: The datatype of the output.
        :param data: the prefilled data to use.
        :param id_: The url pattern.

        This class should never be instantiated directly (unless you know what
        you are doing). Instead create a constant using the network class like
        shown in the usage example below.

        usage example:

        .. code-block:: python

          >>> import fastr
          >>> network = fastr.Network()
          >>> source = network.create_source(datatype=fastr.typelist['ITKImageFile'], id_='sourceN')

        or alternatively create a constant node by assigning data to an item in an InputDict:

        .. code-block:: python

          >>> node_a.inputs['in'] = ['some', 'data']

        which automatically creates and links a ConstantNode to the specified Input
        """
        super(ConstantNode, self).__init__(datatype, id_)
        self.set_data(data)
        self._data = self._input_data

    def __getstate__(self):
        """
        Retrieve the state of the ConstantNode

        :return: the state of the object
        :rtype dict:
        """
        state = super(ConstantNode, self).__getstate__()

        state['data'] = self._data.items()

        return state

    def __setstate__(self, state):
        """
        Set the state of the ConstantNode by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(ConstantNode, self).__setstate__(state)

        self._data = OrderedDict((SampleId(str(x) for x in key), tuple(str(x) for x in value)) for key, value in state['data'])
        self.set_data()  # Make sure that the output size etc gets set

    def set_data(self, data=None, ids=None):
        """
        Set the data of this constant node in the correct way. This is mainly
        for compatibility with the parent class SourceNode

        :param data: the data to use
        :type data: dict or list of urls
        :param ids: if data is a list, a list of accompanying ids
        """
        # We have to arguments to match the superclas
        # pylint: disable=unused-argument
        if data is None and self.data is not None:
            self._input_data = self.data
        else:
            super(ConstantNode, self).set_data(data, ids)

    @property
    def data(self):
        """
        The data stored in this constant node
        """
        return self._data

    def execute(self):
        """
        Execute the constant node and create the jobs that need to run

        :return: list of jobs to run
        :rtype: list of :py:class:`Jobs <fastr.execution.job.Job>`
        """
        # Make sure the data is set
        self.set_data()

        # Run as a normal SourceNode
        return super(ConstantNode, self).execute()
