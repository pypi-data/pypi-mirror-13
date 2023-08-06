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
The base class for all Plugins in the fastr system
"""

from abc import ABCMeta
import gzip
import StringIO

from fastr import exceptions
from fastr.utils.classproperty import classproperty


class BasePlugin(object):
    """
    Base class for Plugins in the fastr system.
    """
    __metaclass__ = ABCMeta

    #: The status of the plugin
    _status = ('Uninitialized', 'Plugin object created')
    _source_code = None

    def __init__(self):
        """
        The BasePlugin constructor.

        :return: the created plugin
        :rtype: BasePlugin
        :raises FastrPluginNotLoaded: if the plugin did not load correctly
        """

        if not self._status[0] == 'Loaded':
            raise exceptions.FastrPluginNotLoaded('Plugin was not properly loaded: [{}] {}'.format(self._status[0], self._status[1]))

    def __str__(self):
        """
        Creare string representation of the plugin.

        :return: string represenation
        :rtype: str
        """
        return '<Plugin: {}>'.format(self.__class__.__name__)

    @classproperty
    def id(cls):
        """
        The id of this plugin
        """
        return cls.__name__

    @classproperty
    def source_code(cls):
        """
        The source code of this plugin
        """
        code_gzip = StringIO.StringIO(cls._source_code)
        with gzip.GzipFile(fileobj=code_gzip, mode='rb') as gzip_stream:
            return gzip_stream.read()

    @classproperty
    def status(cls):
        """
        The status of the plugin.
        """
        return cls._status[0]

    @classproperty
    def status_message(cls):
        """
        The message explaining the status of the plugin.
        """
        return cls._status[1]

    @classmethod
    def set_status(cls, status, message):
        """
        Update the status of the plugin

        :param str status: the new status
        :param str message: message explaining the status change
        """
        cls._status = (status, message)

    @classmethod
    def set_code(cls, source_code):
        """
        Set the filename and source code of the plugin

        :param str source_code: the source code of the plugin
        """
        if cls._source_code is not None:
            raise exceptions.FastrCannotChangeAttributeError('Filename and/or source code are already set!')

        # We gzip the source code before storing
        code_gzip = StringIO.StringIO()
        with gzip.GzipFile(fileobj=code_gzip, mode='w') as gzip_stream:
            gzip_stream.write(source_code)
        cls._source_code = code_gzip.getvalue()

    def cleanup(self):
        """
        Perform any cleanup action needed when the plugin use ended. This can
        be closing files/streams etc.
        """
        pass

    @classmethod
    def test(cls):
        """
        Test the plugin, default behaviour is just to instantiate the plugin
        """
        obj = cls()
        obj.cleanup()
        del obj
