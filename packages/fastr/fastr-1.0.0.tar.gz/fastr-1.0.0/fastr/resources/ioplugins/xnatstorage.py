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
This module contains the XNATStorage plugin for fastr
"""

from abc import ABCMeta, abstractproperty
from collections import OrderedDict, MutableMapping
import fnmatch
from itertools import izip
import netrc
import os
import sys
import tempfile
import textwrap
import threading
import urllib
import urlparse
from zipfile import ZipFile

import requests

import fastr
from fastr import exceptions
from fastr.core.ioplugin import IOPlugin


def caching(func):
    """
    This decorator caches the value in self._cache to avoid data to be
    computed multiple times. Also this function corrects the sigma for
    the voxel spacing.
    """
    name = func.func_name

    def wrapper(self):
        # We use self._cache here, in the decorator _cache will be a member of
        #  the objects, so nothing to worry about
        # pylint: disable=protected-access
        if not self.caching or name not in self._cache:
            # Compute the value if not cached
            self._cache[name] = func(self)

        return self._cache[name]

    docstring = func.__doc__ if func.__doc__ is not None else ''
    wrapper.__doc__ = textwrap.dedent(docstring) + '\nCached using the caching decorator'
    return wrapper


class XNATResponseError(ValueError):
    pass


class XNATUploadError(IOError):
    pass


class XNAT(object):
    def __init__(self, server=None, user=None, password=None, keepalive=840):
        self._interface = None
        self._projects = None
        self._server = None
        self._cache = {}
        self.caching = True

        # Set the keep alive settings and spawn the keepalive thread for sending heartbeats
        if isinstance(keepalive, int) and keepalive > 0:
            self._keepalive = True
            self._keepalive_interval = keepalive
        else:
            self._keepalive = False
            self._keepalive_interval = 14 * 60

        self._keepalive_running = False
        self._keepalive_thread = None
        self._keepalive_event = threading.Event()

        # If needed connect here
        if server is not None:
            self.connect(server, user, password)

    def __del__(self):
        self.disconnect()

    def __enter__(self):
        if self._server is not None:
            self.connect(self._server, self._user, self._password)
        else:
            raise ValueError('No server given!')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self, server, user=None, password=None):
        fastr.log.info('Connecting to server {}'.format(server))
        if self._interface is not None:
            self.disconnect()

        self._interface = requests.Session()
        if (user is not None) or (password is not None):
            self._interface.auth = (user, password)
        self._server = urlparse.urlparse(server)

        # Create a keepalive thread
        self._keepalive_running = True
        self._keepalive_thread = threading.Thread(target=self._keepalive_thread_run)
        self._keepalive_thread.daemon = True  # Make sure thread stops if program stops
        self._keepalive_thread.start()

    def disconnect(self):
        # Stop the keepalive thread
        self._keepalive_running = False
        self._keepalive_event.set()

        if self._keepalive_thread is not None:
            if self._keepalive_thread.is_alive():
                self._keepalive_thread.join(3.0)
            self._keepalive_thread = None

        # Kill the session
        if self._server is not None and self._interface is not None:
            self.delete('/data/JSESSION')

        # Set the server and interface to None
        self._interface = None
        self._server = None

    @property
    def keepalive(self):
        return self._keepalive

    @keepalive.setter
    def keepalive(self, value):
        if isinstance(value, int):
            if value > 0:
                self._keepalive_interval = value
                value = True
            else:
                value = False

        if not isinstance(value, bool):
            raise TypeError('Type should be an integer or boolean!')

        self._keepalive = value

        if self.keepalive:
            # Send a new heartbeat and restart the timer to make sure the interval is correct
            self._keepalive_event.set()
            self.heartbeat()

    def heartbeat(self):
        self.get('/data/JSESSION')

    def _keepalive_thread_run(self):
        # This thread runs until the program stops, it should be inexpensive if not used due to the long sleep time
        while self._keepalive_running:
            # Wait returns False on timeout and True otherwise
            if not self._keepalive_event.wait(self._keepalive_interval):
                if self.keepalive:
                    self.heartbeat()
            else:
                self._keepalive_event.clear()

    @property
    def interface(self):
        return self._interface

    @property
    def fulluri(self):
        return '/data/archive'

    @property
    def xnat(self):
        return self

    def _check_response(self, response, accepted_status=None):
        if accepted_status is None:
            accepted_status = [200, 201, 202, 203, 204, 205, 206]  # All successful responses of HTML
        if response.status_code not in accepted_status or response.text.startswith(('<!DOCTYPE', '<html>')):
            raise XNATResponseError('Invalid response from XNAT (status {}):\n{}'.format(response.status_code, response.text))

    def get(self, path, format=None, query=None):
        fastr.log.debug('CALL GET {}'.format(path))
        uri = self._format_uri(path, format, query=query)
        fastr.log.debug('GET URI {}'.format(uri))
        try:
            response = self.interface.get(uri)
        except requests.exceptions.SSLError:
            raise exceptions.FastrIOError('Encountered a problem with the SSL connection, are you sure the server is offering https?')
        self._check_response(response, [200])  # Allow OK, as we want to get data
        return response

    def post(self, path, data, format=None, query=None):
        fastr.log.debug('CALL POST {}'.format(path))
        uri = self._format_uri(path, format, query=query)
        try:
            response = self._interface.post(uri, data=data)
        except requests.exceptions.SSLError:
            raise exceptions.FastrIOError('Encountered a problem with the SSL connection, are you sure the server is offering https?')
        self._check_response(response)
        return response

    def put(self, path, data=None, files=None, format=None, query=None):
        fastr.log.debug('CALL PUT {}'.format(path))
        uri = self._format_uri(path, format, query=query)
        try:
            response = self._interface.put(uri, data=data, files=files)
        except requests.exceptions.SSLError:
            raise exceptions.FastrIOError('Encountered a problem with the SSL connection, are you sure the server is offering https?')
        self._check_response(response, [200, 201])  # Allow created OK or Create status (OK if already exists)
        return response

    def delete(self, path):
        fastr.log.debug('CALL DELETE {}'.format(path))
        uri = self._format_uri(path)
        try:
            response = self.interface.delete(uri)
        except requests.exceptions.SSLError:
            raise exceptions.FastrIOError('Encountered a problem with the SSL connection, are you sure the server is offering https?')
        self._check_response(response)
        return response

    def _format_uri(self, path, format=None, query=None):
        if path[0] != '/':
            raise ValueError('The requested URI path should start with a / (e.g. /data/projects), found {}'.format(path))

        if query is None:
            query = {}

        if format is not None:
            query['format'] = format

        # Create the query string
        if len(query) > 0:
            query_string = urllib.urlencode(query)
        else:
            query_string = ''

        data = (self._server.scheme,
                self._server.netloc,
                self._server.path.rstrip('/') + path,
                '',
                query_string,
                '')

        return urlparse.urlunparse(data)

    def get_json(self, uri):
        response = self.get(uri, format='json')
        return response.json()

    def download(self, uri, target, format=None):
        uri = self._format_uri(uri, format=format)
        fastr.log.debug("CALL GET {}".format(uri))

        # Stream the get and write to file
        response = self.interface.get(uri, stream=True)

        if response.status_code != 200:
            raise ValueError('Invalid response from XNAT (status {}):\n{}'.format(response.status_code, response.text))

        bytes_read = 0
        fastr.log.debug('Downloading {}:'.format(uri))
        with open(target, 'wb') as out_fh:
            for chunk in response.iter_content(512 * 1024):
                if bytes_read == 0 and chunk.startswith(('<!DOCTYPE', '<html>')):
                    raise ValueError('Invalid response from XNAT (status {}):\n{}'.format(response.status_code, chunk))

                bytes_read += len(chunk)
                out_fh.write(chunk)
                sys.stdout.write('\r{:d} kb'.format(bytes_read / 1024))
                sys.stdout.flush()

        sys.stdout.write('\nSaved as {}...\n'.format(target))
        sys.stdout.flush()

    def download_zip(self, uri, target):
        self.download(uri, target, format='zip')

    def upload(self, uri, file, retries=3):
        uri = self._format_uri(uri)
        attempt = 0
        success = False

        while not success and attempt < retries:
            with open(file, 'rb') as file_handle:
                attempt += 1

                try:
                    response = requests.put(uri, files={'file': file_handle})
                    self._check_response(response)
                    success = True
                except XNATResponseError:
                    pass

        if not success:
            raise XNATUploadError('Upload failed after {} attempts! Status code {}, response text {}'.format(retries, response.status_code, response.text))

    @property
    @caching
    def projects(self):
        result = self.get_json(self.fulluri + '/projects')['ResultSet']['Result']
        return XNATCollection('name', ((x['ID'], Project(self,
                                                         id_=x['ID'],
                                                         uri=x['URI'],
                                                         description=x['description'],
                                                         name=x['name'],
                                                         pi_firstname=x['pi_firstname'],
                                                         pi_lastname=x['pi_lastname'],
                                                         secondary_id=x['secondary_ID'])) for x in result))

    @property
    @caching
    def subjects(self):
        result = self.get_json(self.fulluri + '/subjects')['ResultSet']['Result']
        return XNATCollection('label', ((x['ID'], Subject(self,
                                                          id_=x['ID'],
                                                          uri=x['URI'],
                                                          insert_date=x['insert_date'],
                                                          insert_user=x['insert_user'],
                                                          label=x['label'],
                                                          project=x['project'])) for x in result))

    @property
    @caching
    def experiments(self):
        result = self.get_json(self.fulluri + '/experiments')['ResultSet']['Result']
        return XNATCollection('label', ((x['ID'], Experiment(self,
                                                             id_=x['ID'],
                                                             uri=x['URI'],
                                                             date=x['date'],
                                                             insert_date=x['insert_date'],
                                                             label=x['label'],
                                                             project=x['project'],
                                                             type_=x['xsiType']))
                                        for x in result))

    def clearcache(self):
        self._cache.clear()


class CustomVariableMap(MutableMapping):
    def __init__(self, parent):
        self._cache = {}
        self.caching = True
        self.parent = parent

    def __repr__(self):
        return "<CustomVariables {}>".format(dict(self))

    @property
    @caching
    def data(self):
        xnat_object = self.xnat.get_json(self.parent.fulluri)
        try:
            fields = next(x for x in xnat_object['items'][0]['children'] if x['field'] == 'fields/field')
            fields_map = {x['data_fields']['name']: x['data_fields']['field'] for x in fields['items'] if 'field' in x['data_fields']}
        except StopIteration:
            fields_map = {}

        return fields_map

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        query = {'xsiType': self.parent.type,
                 '{type_}/fields/field[name={key}]/field'.format(type_=self.parent.type,
                                                                 key=key): value}
        self.xnat.put(self.fulluri, query=query)

        # Remove cache and make sure the reload the data
        if 'data' in self._cache:
            del self._cache['data']

    def __delitem__(self, key):
        fastr.log.warning('Deleting of custom variables is currently not supported!')

    def __iter__(self):
        for key in self.data.keys():
            yield key

    def __len__(self):
        return len(self.data)

    @property
    def fulluri(self):
        return self.parent.fulluri

    @property
    def xnat(self):
        return self.parent.xnat

class XNATObject(object):
    __metaclass__ = ABCMeta

    def __init__(self, parent):
        # Set the xnat session
        self._cache = {}
        self.caching = True
        self._parent = parent
        self._xnat = parent.xnat
        self._uri = None
        self._id = None

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.id)

    @property
    def id(self):
        return self._id

    @property
    def parent(self):
        return self._parent

    @property
    def xnat(self):
        return self._xnat

    @property
    def uri(self):
        return self._uri

    @property
    def fulluri(self):
        return '{}/{}/{}'.format(self.parent.fulluri, self.subpath, self.id)

    @abstractproperty
    def _subpath(self):
        pass

    @property
    def subpath(self):
        return self._subpath

    def clearcache(self):
        self._cache.clear()


class XNATCollection(OrderedDict):
    def __init__(self, second_id, *args, **kwargs):
        super(XNATCollection, self).__init__(*args, **kwargs)
        self.second_id = second_id

    def __repr__(self):
        content = ', '.join('({}, {}): {}'.format(k, getattr(v, self.second_id), v) for k, v in self.items())
        return '<XNATCollection {}>'.format(content)

    def __getitem__(self, item):
        if item in self:
            return super(XNATCollection, self).__getitem__(item)
        else:
            try:
                return next(x for x in self.values() if getattr(x, self.second_id) == item)
            except StopIteration:
                raise KeyError('Could not find ID/label {} in collection!'.format(item))

    def get(self, k, d=None):
        try:
            return self[k]
        except KeyError:
            return d

    def search(self, search_string):
        values = {x.id: x for x in self.values() if fnmatch.fnmatchcase(getattr(x, self.second_id), search_string) or x.id == search_string}
        return type(self)(self.second_id, values)


class Project(XNATObject):
    def __init__(self, parent, id_, uri, description, name, pi_firstname, pi_lastname, secondary_id):
        # Call superclass constructor
        super(Project, self).__init__(parent=parent)

        # Set the cache for the subjects
        self._subjects = None

        # Set the properties
        self._id = id_
        self._uri = uri
        self._description = description
        self._name = name
        self._pi_firstname = pi_firstname
        self._pi_lastname = pi_lastname
        self._secondary_id = secondary_id
        self.fields = CustomVariableMap(self)

    @property
    def _subpath(self):
        return 'projects'

    @property
    def description(self):
        return self._description

    @property
    def name(self):
        return self._name

    @property
    def pi_firstname(self):
        return self._pi_firstname

    @property
    def pi_lastname(self):
        return self._pi_lastname

    @property
    def secondary_id(self):
        return self._secondary_id

    @property
    def type(self):
        return "xnat:projectData"

    @property
    @caching
    def subjects(self):
        result = self._xnat.get_json(self.uri + '/subjects')['ResultSet']['Result']
        return XNATCollection('label', ((x['ID'], Subject(self,
                                                          id_=x['ID'],
                                                          uri=x['URI'],
                                                          insert_date=x['insert_date'],
                                                          insert_user=x['insert_user'],
                                                          label=x['label'],
                                                          project=x['project'])) for x in result))

    @property
    @caching
    def experiments(self):
        result = self._xnat.get_json(self.uri + '/experiments')['ResultSet']['Result']
        return XNATCollection('label', ((x['ID'], Experiment(self,
                                                             id_=x['ID'],
                                                             uri=x['URI'],
                                                             date=x['date'],
                                                             insert_date=x['insert_date'],
                                                             label=x['label'],
                                                             project=x['project'],
                                                             type_=x['xsiType']))
                                        for x in result))


class Subject(XNATObject):
    def __init__(self, parent, id_, uri, insert_date, insert_user, label, project):
        # Call superclass constructor
        super(Subject, self).__init__(parent=parent)

        # Set the experiments cache
        self._experiments = None

        # Set the properties
        self._id = id_
        self._uri = uri
        self._insert_date = insert_date
        self._insert_user = insert_user
        self._label = label
        self._project = project
        self.fields = CustomVariableMap(self)

    @property
    def _subpath(self):
        return 'subjects'

    @property
    def project(self):
        return self.parent

    @property
    def insert_date(self):
        return self._insert_date

    @property
    def insert_user(self):
        return self._insert_user

    @property
    def label(self):
        return self._label

    @property
    def projectname(self):
        return self._project

    @property
    def type(self):
        return "xnat:subjectData"

    @property
    @caching
    def experiments(self):
        # This is not simply self.uri + '/experiments' because that XNAT REST path does not exist!
        result = self._xnat.get_json('{}/projects/{}/subjects/{}/experiments'.format(self.xnat.fulluri, self.projectname, self.id))['ResultSet']['Result']
        return XNATCollection('label', ((x['ID'], Experiment(self,
                                                             id_=x['ID'],
                                                             uri=x['URI'],
                                                             date=x['date'],
                                                             insert_date=x['insert_date'],
                                                             label=x['label'],
                                                             project=x['project'],
                                                             type_=x['xsiType']))
                                        for x in result))


class BaseExperiment(XNATObject):
    def __init__(self, parent, id_, uri, date, insert_date, label, project, type_):
        # Call superclass constructor
        super(BaseExperiment, self).__init__(parent=parent)

        # Set the experiments cache
        self._scans = None

        # Set the properties
        self._id = id_
        self._uri = uri
        self._date = date
        self._insert_date = insert_date
        self._label = label
        self._project = project
        self._type = type_
        self.fields = CustomVariableMap(self)

    @property
    def project(self):
        return self.parent.project

    @property
    def subject(self):
        return self.parent

    @property
    def date(self):
        return self._date

    @property
    def insert_date(self):
        return self._insert_date

    @property
    def label(self):
        return self._label

    @property
    def projectname(self):
        return self._project

    @property
    def type(self):
        return self._type


class Experiment(BaseExperiment):
    @property
    def _subpath(self):
        return 'experiments'

    @property
    @caching
    def scans(self):
        #result = self._xnat.get_json(self.fulluri + '/scans')['ResultSet']['Result']
        result = self._xnat.get_json(self.uri + '/scans')['ResultSet']['Result']
        return XNATCollection('series_description', ((x['ID'], Scan(self,
                                                                    id_=x['ID'],
                                                                    uri=x['URI'],
                                                                    note=x['note'],
                                                                    quality=x['quality'],
                                                                    series_description=x['series_description'],
                                                                    type_=x['type'],
                                                                    xnat_imagescandata_id=x['xnat_imagescandata_id']))
                                                     for x in result))

    @property
    @caching
    def assessors(self):
        result = self._xnat.get_json(self.uri + '/assessors')['ResultSet']['Result']
        return XNATCollection('label', ((x['ID'], Assessor(self,
                                                           id_=x['ID'],
                                                           uri=x['URI'],
                                                           date=x['date'],
                                                           insert_date=x['insert_date'],
                                                           label=x['label'],
                                                           project=x['project'],
                                                           type_=x['xsiType']))
                                        for x in result))

    @property
    @caching
    def reconstructions(self):
        # TODO: test the reconstructions, couldn't test due to lack of data on the server :-)
        result = self._xnat.get_json(self.uri + '/reconstructions')['ResultSet']['Result']
        return XNATCollection('label', ((x['ID'], Assessor(self,
                                                           id_=x['ID'],
                                                           uri=x['URI'],
                                                           date=x['date'],
                                                           insert_date=x['insert_date'],
                                                           label=x['label'],
                                                           project=x['project'],
                                                           type_=x['xsiType']))
                                        for x in result))

    def add_assessor(self, label, type_='xnat:mrAssessorData'):
        uri = '{}/assessors/{label}?xsiType={type}&label={label}&req_format=qs'.format(self.fulluri,
                                                                                       type=type_,
                                                                                       label=label)
        self.xnat.put(uri, expected_code=(200, 201))
        self.clearcache()  # The resources changed, so we have to clear the cache

    def download(self, path):
        self.xnat.download_zip(self.fulluri + '/scans/ALL/files', path)


class DerivedExperiment(BaseExperiment):
    @property
    @caching
    def files(self):
        result = self._xnat.get_json(self.fulluri + '/files')['ResultSet']['Result']
        return XNATCollection('name', ((x['Name'], File(self,
                                                        id_=x['URI'],
                                                        name=x['Name'],
                                                        size=x['Size'],
                                                        uri=x['URI'],
                                                        cat_id=x['cat_ID'],
                                                        collection=x['collection'],
                                                        file_content=x['file_content'],
                                                        file_format=x['file_format'],
                                                        file_tags=x['file_tags']))
                                       for x in result))

    @property
    @caching
    def resources(self):
        result = self._xnat.get_json(self.fulluri + '/resources')['ResultSet']['Result']
        return XNATCollection('label', ((x['xnat_abstractresource_id'], Resource(self,
                                                                                 id_=x['xnat_abstractresource_id'],
                                                                                 cat_desc=x['cat_desc'],
                                                                                 cat_id=x['cat_id'],
                                                                                 category=x['category'],
                                                                                 content=x['content'],
                                                                                 file_count=x['file_count'],
                                                                                 file_size=x['file_size'],
                                                                                 format=x['format'],
                                                                                 label=x['label'],
                                                                                 tags=x['tags']))
                                        for x in result))

    def add_resource(self, label, format=None):
        uri = '{}/resources/{}'.format(self.fulluri, label)
        self.xnat.put(uri, format=format)
        self.clearcache()  # The resources changed, so we have to clear the cache

    def download(self, path):
        self.xnat.download_zip(self.fulluri + '/files', path)


class Reconstruction(DerivedExperiment):
    @property
    def _subpath(self):
        return 'reconstrutions'


class Assessor(DerivedExperiment):
    @property
    def _subpath(self):
        return 'assessors'


class Scan(XNATObject):
    def __init__(self, parent, id_, uri, note, quality, series_description, type_, xnat_imagescandata_id):
        # Call superclass constructor
        super(Scan, self).__init__(parent=parent)

        # Set the experiments cache
        self._files = None
        self._resources = None

        # Set the properties
        self._id = id_
        self._uri = uri
        self._note = note
        self._quality = quality
        self._series_description = series_description
        self._type = type_
        self._xnat_imagescandata_id = xnat_imagescandata_id
        self.fields = CustomVariableMap(self)

    @property
    def _subpath(self):
        return 'scans'

    @property
    def label(self):
        return self.series_description

    @property
    def project(self):
        return self.parent.project

    @property
    def subject(self):
        return self.parent.subject

    @property
    def experiment(self):
        return self.parent

    @property
    def series_description(self):
        return self._series_description

    @property
    def type(self):
        return self._type

    @property
    @caching
    def files(self):
        result = self._xnat.get_json(self.uri + '/files')['ResultSet']['Result']
        return XNATCollection('name', ((x['Name'], File(self,
                                                        id_=x['URI'],
                                                        name=x['Name'],
                                                        size=x['Size'],
                                                        uri=x['URI'],
                                                        cat_id=x['cat_ID'],
                                                        collection=x['collection'],
                                                        file_content=x['file_content'],
                                                        file_format=x['file_format'],
                                                        file_tags=x['file_tags']))
                                       for x in result))

    @property
    @caching
    def resources(self):
        result = self._xnat.get_json(self.uri + '/resources')['ResultSet']['Result']
        return XNATCollection('label', ((x['xnat_abstractresource_id'], Resource(self,
                                                                                 id_=x['xnat_abstractresource_id'],
                                                                                 cat_desc=x['cat_desc'],
                                                                                 cat_id=x['cat_id'],
                                                                                 category=x['category'],
                                                                                 content=x['content'],
                                                                                 file_count=x['file_count'],
                                                                                 file_size=x['file_size'],
                                                                                 format=x['format'],
                                                                                 label=x['label'],
                                                                                 tags=x['tags']))
                                        for x in result))

    def add_resource(self, label, format=None):
        uri = '{}/resources/{}'.format(self.fulluri, label)
        self.xnat.put(uri, format=format)
        self.clearcache()  # The resources changed, so we have to clear the cache

    def download(self, path):
        self.xnat.download_zip(self.fulluri + '/files', path)


class Resource(XNATObject):
    def __init__(self, parent, id_, cat_desc, cat_id, category, content, file_count, file_size, format, label, tags):
        super(Resource, self).__init__(parent=parent)

        # Set the experiments cache
        self._files = None

        # Set the properties
        self._id = id_
        self._cat_desc = cat_desc
        self._cat_id = cat_id
        self._category = category
        self._content = content
        self._file_count = file_count
        self._file_size = file_size
        self._format = format
        self._label = label
        self._tags = tags

    @property
    def _subpath(self):
        return 'resources'

    @property
    def project(self):
        return self.parent.project

    @property
    def subject(self):
        return self.parent.subject

    @property
    def experiment(self):
        return self.parent.experiment

    @property
    def scan(self):
        return self.parent

    @property
    def label(self):
        return self._label

    @property
    @caching
    def files(self):
        result = self._xnat.get_json(self.uri + '/files')['ResultSet']['Result']
        return XNATCollection('name', ((x['Name'], File(self,
                                                        id_=x['URI'],
                                                        name=x['Name'],
                                                        size=x['Size'],
                                                        uri=x['URI'],
                                                        cat_id=x['cat_ID'],
                                                        collection=x['collection'],
                                                        file_content=x['file_content'],
                                                        file_format=x['file_format'],
                                                        file_tags=x['file_tags']))
                                       for x in result))

    def download(self, path):
        self.xnat.download_zip(self.fulluri + '/files', path)

    def upload(self, localpath, remotepath):
        fastr.log.debug('Upload to resource {}, local {}, remote {}'.format(self.id, localpath, remotepath))
        uri = '{}/files/{}'.format(self.fulluri, remotepath)
        self.xnat.upload(uri, localpath)


class File(XNATObject):
    def __init__(self, parent, id_, name, size, uri, cat_id, collection, file_content, file_format, file_tags):
        # Call superclass constructor
        super(File, self).__init__(parent=parent)

        # Set the properties
        self._id = id_
        self._uri = uri
        self._name = name
        self._size = size
        self._cat_id = cat_id
        self._collection = collection
        self._file_content = file_content
        self._file_format = file_format
        self._file_tags = file_tags

    @property
    def _subpath(self):
        return 'files'

    @property
    def project(self):
        return self.parent.project

    @property
    def subject(self):
        return self.parent.subject

    @property
    def experiment(self):
        return self.parent.experiment

    @property
    def scan(self):
        return self.parent.scan

    @property
    def resource(self):
        return self.parent

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def cat_id(self):
        return self._cat_id

    @property
    def collection(self):
        return self._collection

    @property
    def file_content(self):
        return self._file_content

    @property
    def file_format(self):
        return self._file_format

    @property
    def file_tags(self):
        return self._file_tags

    def download(self, path):
        self.xnat.download(self.uri, path)


class XNATStorage(IOPlugin):

    """
    .. warning::

        As this IOPlugin is under development, it has not been thoroughly
        tested.

    The XNATStorage plugin is an IOPlugin that can download data from and
    upload data to an XNAT server. It uses its own ``xnat://`` URL scheme.
    This is a scheme specific for this plugin and though it looks somewhat
    like the XNAT rest interface, a different type or URL.

    Data resources can be access directly by a data url::

        xnat://xnat.example.com/data/archive/projects/sandbox/subjects/subject001/experiments/experiment001/scans/T1/resources/DICOM
        xnat://xnat.example.com/data/archive/projects/sandbox/subjects/subject001/experiments/*_BRAIN/scans/T1/resources/DICOM

    In the second URL you can see a wildcard being used. This is possible at
    long as it resolves to exactly one item. If you want to do a search where
    multiple resources are returned, it is possible to use a search url::

        xnat://xnat.example.com/search?project=sandbox&subjects=subject[0-9][0-9][0-9]&experiment=*_BRAIN&scan=T1&resource=DICOM

    This will return all experiments that end with _BRAIN that belong to a
    subjectXXX where XXX is a 3 digit number. By default the ID for the samples
    will be the experiment XNAT ID (e.g. XNAT_E00123). The wildcards that can
    be the used are the same UNIX shell-style wildcards as provided by the
    module :py:mod:`fnmatch`.

    It is possible to change the id to a different fields id or label. Valid
    fields are project, subject, experiment, scan, and resource::

        xnat://xnat.example.com/search?project=sandbox&subject=subject[0-9][0-9][0-9]&experiment=*_BRAIN&scan=T1&resource=DICOM?id=subject&label=true

    The ``id`` query element will change the field from the default experiment to
    subject and the ``label`` query element sets the use of the label to ``True``
    (the default is ``False``)

    .. note::

        As the default transport ``https`` will be assumed, if ``http`` is
        desired, this can be done by adding ``insure=true`` to the query string

    To disable ``https`` transport and use ``http`` instead the query string
    can be modified to add ``insecure=true``. This will make the plugin send
    requests over ``http``::

        xnat://xnat.example.com/data/archive/projects/sandbox/subjects/subject001/experiments/*_BRAIN/scans/T1/resources/DICOM?insecure=true

    For storing credential the ``.netrc`` file can be used. This is a common
    way to store credential on UNIX systems. It is required that the file is
    only accessible by the owner only or a ``NetrcParseError`` will be raised.
    A netrc file is really easy to create, as its entries look like::

        machine xnat.example.com
                login username
                password secret123

    See the :py:mod:`netrc module <netrc>` or the
    `GNU inet utils website <http://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html#The-_002enetrc-file>`_
    for more information about the ``.netrc`` file.

    .. note::

        For scan the label will be the series description.

    .. warning::

        labels in XNAT are not guaranteed to be unique, so be careful
        when using them as the sample ID.

    For background on XNAT, see the
    `XNAT API DIRECTORY <https://wiki.xnat.org/display/XNAT16/XNAT+REST+API+Directory>`_
    for the REST API of XNAT.
    """
    scheme = 'xnat'

    def __init__(self):
        # initialize the instance and register the scheme
        super(XNATStorage, self).__init__()
        self._xnat = (None, None)

    def cleanup(self):
        if self.xnat is not None:
            self.xnat.disconnect()

    @property
    def server(self):
        return self._xnat[0]

    @property
    def xnat(self):
        return self._xnat[1]

    def connect(self, server, path='', insecure=False):
        if self.server != server:
            # Try to neatly clean previous connection
            if self.xnat is not None:
                self.xnat.disconnect()

            try:
                user, _, password = netrc.netrc().authenticators(server)
            except TypeError:
                raise exceptions.FastrValueError('Could not retrieve login info for "{}" from the .netrc file!'.format(server))

            # Create the URL for the XNAT connection
            schema = 'http' if insecure else 'https'
            xnat = XNAT(urlparse.urlunparse([schema, server, path, '', '', '']), user, password)

            self._xnat = (server, xnat)

    @staticmethod
    def _path_to_dict(path):
        if not path.startswith('/data/archive/'):
            # prefix, path = path.split('/data/archive')
            raise ValueError('Resources to be located should have a path starting with /data/ (found {})'.format(path))

        # Break path apart
        parts = path.lstrip('/').split('/', 13)  # Check if len is 13!

        # Ignore first two parts and build a dict from /key/value/key/value pattern
        path_iterator = parts[2:].__iter__()
        location = dict(izip(path_iterator, path_iterator))
        return location

    def _locate_resource(self, url, create=False):
        fastr.log.info('Locating {}'.format(url))
        # Parse url
        parsed_url = urlparse.urlparse(url)
        path = parsed_url.path

        if not path.startswith('/data/'):
            raise ValueError('Resources to be located should have a path starting with /data/')

        # Create a search uri
        location = self._path_to_dict(path)
        query = urllib.urlencode(location)
        scans = self._find_scans(query)
        resources = self._find_resources(query, scans=scans)

        if len(resources) == 0:
            if not create:
                raise ValueError('Could not find data object at {}'.format(url))
            elif len(scans) == 1:
                fastr.log.debug('Scans: {}'.format(scans))
                scanid, scan = scans.popitem()
                resource = location['resources']
                if '*' in resource or '?' in resource or '[' in resource or ']' in resource:
                    raise ValueError('Illegal characters found in name of resource to create! (characters ?*[] or illegal!)')
                scan.add_resource(resource)
                resources = self._find_resources(query, scans={scanid: scan})
                if len(resources) != 1:
                    raise ValueError('There appears to be a problem creating the resource!')
                return resources.popitem()[1]
            else:
                raise ValueError('To create a resources, the path should point to a unique scan! Found {} matching scans'.format(len(scans)))

        elif len(resources) == 1:
            return resources.popitem()[1]
        else:
            raise ValueError('Data item does not point to a unique resource! Matches found: {}'.format([x.fulluri for x in resources.values()]))

    def fetch_url(self, inurl, outpath):
        """
        Get the file(s) or values from XNAT.

        :param inurl: url to the item in the data store
        :param outpath: path where to store the fetch data locally
        :param datatype: the DataType of the retrieved URL
        """

        if fastr.data.url.get_url_scheme(inurl) != self.scheme:
            raise exceptions.FastrValueError('URL not of {} type!'.format(self.scheme))

        # Create a session for this retrieval
        url = urlparse.urlparse(inurl)
        path_prefix = url.path[:url.path.find('/data/archive')]
        url = url._replace(path=url.path[len(path_prefix):])  # Strip the prefix of the url path
        inurl = urlparse.urlunparse(url)

        insecure = urlparse.parse_qs(url.query).get('insecure', ['false'])[0] in ['true', '1']
        self.connect(url.netloc, path=path_prefix, insecure=insecure)
        path_dict = self._path_to_dict(url.path)

        present = {x: x in path_dict for x in ('projects', 'subjects', 'experiments', 'scans', 'resources')}

        fastr.log.info('Fetching from location {} (from {})'.format(path_dict, url.path))
        if not all(present.values()):
            raise ValueError('Not all required fields are present in URL, found fields: {}, required fields found: {}'.format(path_dict, present))

        filepath = path_dict.get('files', '')

        if not url.scheme == 'xnat':
            raise ValueError('URL does not has an xnat scheme')

        if not url.path.startswith('/data/archive'):
            raise ValueError('Can only fetch urls with the /data/archive path')

        resource = self._locate_resource(inurl)

        # Download the Resource
        workdir = outpath
        if not os.path.isdir(workdir):
            os.makedirs(workdir)

        # Create uniquer dir to download in
        workdir = tempfile.mkdtemp(prefix='fastr_xnat_{}_tmp'.format(resource.id), dir=outpath)
        zip_path = os.path.join(workdir, 'xnat_resource_{}.zip'.format(resource.id))
        fastr.log.info('Attempting to download {}'.format(resource.fulluri))
        resource.download(zip_path)

        # Extract contents of the zip file
        with ZipFile(zip_path) as zip_file:
            zip_file.extractall(workdir)

        # Remove extracted zip file
        os.remove(zip_path)

        # Determine data path
        data_path = os.path.join(workdir,
                                 resource.experiment.label.replace(' ', '_'),
                                 'scans', '{}-{}'.format(resource.scan.id, "".join([c if c.isalnum() else "_" for c in resource.scan.type])),
                                 'resources',
                                 resource.label.replace(' ', '_'),
                                 'files',
                                 filepath)
        fastr.log.debug('Data located in: {}'.format(data_path))
        return data_path

    def put_url(self, inpath, outurl):
        """
        Upload the files to the XNAT storage

        :param inpath: path to the local data
        :param outurl: url to where to store the data in the external data store.
        """
        # Create a session for this retrieval
        url = urlparse.urlparse(outurl)
        path_prefix = url.path[:url.path.find('/data/archive')]
        url = url._replace(path=url.path[len(path_prefix):])  # Strip the prefix of the url path
        outurl = urlparse.urlunparse(url)

        insecure = urlparse.parse_qs(url.query).get('insecure', ['false'])[0] in ['true', '1']
        self.connect(url.netloc, path=path_prefix, insecure=insecure)

        # Determine the resource to upload to
        resource = self._locate_resource(outurl, create=True)

        # Determine the file within xnat
        parsed_url = urlparse.urlparse(outurl)
        location = self._path_to_dict(parsed_url.path)

        # Upload the file
        fastr.log.debug('Uploading to: {}'.format(resource.fulluri))
        try:
            resource.upload(inpath, location['files'])
            return True
        except XNATUploadError:
            return False

    def _find_projects(self, query):
        """
        Get all matching projects

        :param dict query: the query to find projects to match for
        :return:
        """
        # Get the query
        if isinstance(query, str):
            query = urlparse.parse_qs(query)

        fastr.log.info('Find projects: {}'.format(query))
        project = query.get('projects', ['*'])[0]

        # Get a list of desired scans
        projects = self.xnat.projects.search(project)

        if projects is None:
            raise exceptions.FastrValueError('Could not find project {} in XNAT project list ({})'.format(project, self.xnat.projects.keys()))

        return projects.values()

    def _find_subjects(self, query, projects=None):
        """
        Get all matching subjects

        :param dict query: the query to find subjects to match for
        :param dict projects: the projects to search through
        :return:
        """
        # Get the query
        if isinstance(query, str):
            query = urlparse.parse_qs(query)

        fastr.log.info('Find subjects: {} (projects: {})'.format(query, projects))
        if projects is None:
            projects = self._find_projects(query)

        subject = query.get('subjects', ['*'])[0]

        # Get all subjects
        subjects = {}
        for project in projects:
            extra_subjects = project.subjects.search(subject)
            subjects.update(extra_subjects)

        return subjects

    def find_experiments(self, query, subjects=None):
        """
        Get all matching experiments

        :param dict query: the query to find experiments to match for
        :param dict subjects: the subjects to search through
        :return:
        """
        # Get the query
        if isinstance(query, str):
            query = urlparse.parse_qs(query)

        fastr.log.info('Find experiments: {} (subjects: {})'.format(query, subjects))
        if subjects is None:
            subjects = self._find_subjects(query)

        experiment = query.get('experiments', ['*'])[0]

        experiments = {}
        for subject in subjects.values():
            extra_experiments = subject.experiments.search(experiment)
            experiments.update(extra_experiments)

        return experiments

    def _find_scans(self, query, experiments=None):
        """
        Get all matching resources

        :param dict query: the query to find scans to match for
        :param dict experiments: the experiments to search through
        :return:
        """
        # Get the query
        if isinstance(query, str):
            query = urlparse.parse_qs(query)

        fastr.log.info('Find scans: {} (experimetns: {})'.format(query, experiments))
        if experiments is None:
            experiments = self.find_experiments(query)

        scan = query.get('scans', ['*'])[0]

        scans = {}
        for experiment in experiments.values():
            extra_scans = experiment.scans.search(scan)
            # Here we make sure the scan id is unique by prefixing the experiment id
            #  (otherwise there will be conflicts for sure)
            extra_scans = {'{}__{}'.format(experiment.id, k): v for k, v in extra_scans.items()}
            scans.update(extra_scans)

        return scans

    def _find_resources(self, query, scans=None):
        """
        Get all matching resources

        :param dict query: the query to find resources to match for
        :param dict scans: the scans to search through
        :return:
        """
        # Get the query
        if isinstance(query, str):
            query = urlparse.parse_qs(query)

        fastr.log.info('Find resources: {} (scans: {})'.format(query, scans))
        if scans is None:
            scans = self._find_scans(query)

        resource = query.get('resources', ['*'])[0]

        resources = {}
        for scan in scans.values():
            extra_resources = scan.resources.search(resource)
            resources.update(extra_resources)

        return resources

    def expand_url(self, url):
        # Check if there is a wildcard in the URL:
        parsed_url = urlparse.urlparse(url)

        if parsed_url.path == '/search':
            # Make sure we are connect to the correct server
            self.connect(parsed_url.netloc)

            # Parse the query
            query = urlparse.parse_qs(parsed_url.query)

            id_field = query.get('id', ['experiment'])[0]
            id_use_label = query.get('label', ['0'])[0].lower() in ['1', 'true']

            if id_field not in ['project', 'subject', 'experiment', 'scan', 'resource']:
                raise exceptions.FastrValueError('Requested id field ({}) is not a valid option!'.format(id_field))

            # Find all matching resources
            resources = self._find_resources(query)

            # Format the new expanded urls
            urls = []
            for id_, resource in resources.items():
                # TODO: Just use resource.fulluri + '/files/filename' ?
                newpath = '/data/archive/projects/{}/subjects/{}/experiments/{}/scans/{}/resources/{}/files/{}'.format(
                    resource.project.id,
                    resource.subject.id,
                    resource.experiment.id,
                    resource.scan.id,
                    resource.id,
                    query.get('files', [''])[0]
                )

                newurl = urlparse.urlunparse(('xnat', parsed_url.netloc, newpath, parsed_url.params, '', ''))

                # Determine the ID of the sample
                if id_field == 'resource':
                    id_obj = resource
                else:
                    id_obj = getattr(resource, id_field)

                if id_use_label:
                    id_ = id_obj.label
                else:
                    id_ = id_obj.id

                urls.append((id_, newurl))

            return tuple(urls)
        else:
            return url
