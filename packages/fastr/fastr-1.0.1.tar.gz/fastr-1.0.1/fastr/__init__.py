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

""" FASTR is a top level package which includes all parts required to create
networks and edit networks.

.. class:: Network

    The class representing a Network, this is in fact a reference to
    :py:class:`fastr.core.network.Network`.

.. class:: Node

    The class representing a Node, this is in fact a reference to
    :py:class:`fastr.core.node.Node`.

.. class:: Link

    The class representing a Link, this is in fact a reference to
    :py:class:`fastr.core.link.Link`.

.. class:: SourceNode

    The class representing a data source, this is in fact a reference to
    :py:class:`fastr.core.node.SourceNode`.

.. class:: SinkNode

    The class representing a data sink, this is in fact a reference to
    :py:class:`fastr.core.node.SinkNode`.

.. class:: ConstantNode

    The class representing a constant data source, this is in fact a reference
    to :py:class:`fastr.core.node.ConstantNode`.

.. data:: toollist

    A :py:class:`fastr.core.toolmanager.ToolManager` containing all Tools known
    to the FASTR environment. The toollist can be accessed in a similar way to
    a dict. Indexing with a tool id will return the newest version of the Tool.
    If a specific version of the tool is required a tuple can be used as the
    index:

    .. code-block:: python

        >>> import fastr
        >>> fastr.toollist['testtool']
        <Tool: testtool version: 4.2>
        >>> fastr.toollist['testtool', '2.0']
        <Tool: testtool version: 2.0>


.. data:: typelist

    A :py:class:`fastr.core.datatypemanager.DataTypeManager` containing all
    Types known to the FASTR environment. This is usuable as a dict where
    the key is the datatype id and the value is the datatype itself.
"""

# In the top level module we want to add some variables which are constants
# but use a non-constant name (not caps)
# pylint: disable=invalid-name

from fastr.configmanager import Config

# Get version info
from fastr.version import version as __version__

#: Configuration of the fastr system
config = Config()

# Reference the logger object from the config
log = config.log

# Import all fastr components
from fastr.core.network import Network
from fastr.core.link import Link
from fastr.core.node import Node
from fastr.core.node import ConstantNode
from fastr.core.node import SourceNode
from fastr.core.node import SinkNode
from fastr.core.toolmanager import toollist
from fastr.core.interface import InterfacePluginManager
from fastr.core.ioplugin import IOPluginManager
from fastr.core.datatypemanager import typelist
from fastr.core.vfs import VirtualFileSystem

# The following loads all ioplugins from the resources folder and registers the built-in vfs with the plugin list
ioplugins = IOPluginManager()
vfs = VirtualFileSystem()

#: The currently active Network in fastr
current_network = None

def find(object_fullid):
    """Find a object by its fullid and return it.

    :param object_fullid: The full id of the object to retrieve
    :return: the desire object, or None if object not found
    """
    if current_network is None:
        log.info('No current network is set, cannot retrieve objects')
        return None

    try:
        return current_network[object_fullid]
    except (KeyError, IndexError):
        log.debug('Could not find "{}" in current network'.format(object_fullid))
        return None

# Register the val URL for Python version under 2.7.3
ioplugins.register_url_scheme('val')
interfaces = InterfacePluginManager()

log.info('Finished with the FASTR environment set up')
