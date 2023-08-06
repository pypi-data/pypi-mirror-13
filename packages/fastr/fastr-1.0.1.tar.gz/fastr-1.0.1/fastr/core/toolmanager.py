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
This module contains the tool manager class
"""

import re

import fastr
from fastr import config
from fastr.core.basemanager import BaseManager
from fastr.core.tool import Tool
from fastr.core.version import Version
import fastr.exceptions as exceptions


class ToolManager(BaseManager):
    """
    Class for managing all the tools loaded in the fastr system
    """
    extmatch = re.compile(r'^(.*)\.xml$')

    def __init__(self, path):
        """
        Create a ToolManager and scan path to search for Tools

        :param path: the path(s) to scan for Tools
        :type path: str or iterable of str
        :return: newly created ToolManager
        """
        super(ToolManager, self).__init__(path, True)

    def __contains__(self, key):
        """
        Check if an item is in the ToolManager

        :param key: tool id or tuple (toolid, version)
        :type key: str or tuple
        :return: flag indicating the item is in the manager
        """
        return self.__keytransform__(key) in self.data

    def __getitem__(self, key):
        """
        Retrieve a Tool from the ToolManager. You can request by only an id,
        which results in the newest version of the Tool being returned, or
        request using both an id and a version.

        :param key: tool id or tuple (toolid, version)
        :type key: str or tuple
        :return: the requested Tool
        :raises FastrToolUnknownError: if a non-existing Tool was requested
        """
        if self.__keytransform__(key) not in self.data:
            raise exceptions.FastrToolUnknownError('Key "{}" not found in {}'.format(key, type(self).__name__))

        tool = self.data[self.__keytransform__(key)]
        if tool.target is None:
            fastr.log.error('Tool {} has no valid target for this system defined!'.format(tool.id))

        return tool

    def __keytransform__(self, key):
        """
        Key transform, used for allowing indexing both by id-only and by
        ``(id, version)``

        :param key: key to transform
        :return: key in form ``(id, version)``
        """
        if isinstance(key, (str, unicode)):
            versions = [k[1] for k in self.keys() if k[0] == key]

            if len(versions) == 0:
                if '/' in key:
                    key = key.split('/', 1)
                    return (key[0], Version(key[1]))
                else:
                    return key, None

            return key, max(versions)
        else:
            if isinstance(key[1], (str, unicode)):
                return (key[0], Version(key[1]))
            else:
                return key

    @property
    def _item_extension(self):
        """
        Extension of files to load
        """
        return '.xml'

    def _populate(self):
        super(ToolManager, self)._populate()
        fastr.ioplugins.create_ioplugin_tool()

    def _print_key(self, key):
        """
        Print function for the keys
        """
        return (key[0], 'v{}'.format(str(key[1])))

    def _print_value(self, value):
        """
        Print function for the values
        """
        return value.filename

    def _load_item(self, filepath):
        """
        Load a Tool file and store it in the Manager
        """
        tool = Tool(filepath)
        self._store_item((tool.id, tool.command['version']), tool)

    def todict(self):
        """
        Return a dictionary version of the Manager

        :return: manager as a dict
        """
        result = {}
        for key in self.keys():
            if key[0] not in result:
                result[key[0]] = []

            if str(key[1]) not in result[key[0]]:
                result[key[0]].append(str(key[1]))

        return result

    def toolversions(self, tool):
        """
        Return a list of available versions for the tool

        :param tool: The tool to check the versions for. Can be either a `Tool` or a `str`.
        :return: List of version objects. Returns `None` when the given tool is not known.
        """

        if isinstance(tool, Tool):
            toolname = tool.id
        else:
            try:
                tool = self[tool]
                toolname = tool.id
            except exceptions.FastrToolUnknownError as e:
                fastr.log.error("Error requesting tool versions: Tool ({}) is not known.".format(tool))
                return None
        fastr.log.info("toolname: {}".format(toolname))
        return [key[1] for key in self.keys() if key[0] == toolname]


if 'toollist' not in locals():
    #: The fastr toollist
    toollist = ToolManager(config.tools_path)