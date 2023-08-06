import datetime
import functools
import multiprocessing
import threading

import fastr
from fastr.web import app
from flask import Flask, Response, abort, url_for
from flask.ext.restful import Api, Resource, reqparse, marshal, fields, inputs

api = Api(app)

from fastr.core.network import Network

networks = [
]

networks = {x.id: x for x in networks}

runs = {}


STATUS_MANAGER = multiprocessing.Manager()


def update_status(job, job_status):
    job_status[job.jobid] = job.status


def update_job_result(job, job_status, job_results):
    job_results[job.jobid] = str(job.output_data)


def network_lock_thread(lock, network):
    fastr.log.debug('WAITING FOR LOCK')
    with lock:
        fastr.log.debug('CALLING NETWORK ABORT')
        network.abort()


def network_runner(network, source_data, sink_data, chuck_status, job_status, job_results, abort_lock):
    network.job_finished_callback = functools.partial(update_job_result, job_status=job_status, job_results=job_results)
    network.job_status_callback = functools.partial(update_status, job_status=job_status)
    abort_lock.acquire()
    abort_thread = threading.Thread(name="NetworkAbort", target=network_lock_thread, args=(abort_lock, network))
    abort_thread.start()

    network.execute(source_data, sink_data)


class Run(object):
    def __init__(self, id, network, source_data, sink_data):
        self.id = id
        self.chunks = STATUS_MANAGER.list()
        self.jobs = STATUS_MANAGER.dict()
        self.job_results = STATUS_MANAGER.dict()
        self.source_data = source_data
        self.sink_data = sink_data
        self.network = network.id
        self.abort_lock = multiprocessing.Lock()
        self.process = self.run_network(network, source_data, sink_data, self.abort_lock)

    def run_network(self, network, source_data, sink_data, abort_lock):
        process = multiprocessing.Process(target=network_runner,
                                          args=(network,
                                                source_data,
                                                sink_data,
                                                self.chunks,
                                                self.jobs,
                                                self.job_results,
                                                abort_lock),
                                          name=self.id)
        process.start()
        return process

    def status(self):
        return {'job_status': dict(self.jobs),
                'job_results': dict(self.job_results)}

    def abort(self):
        fastr.log.debug('RELEASING ABORT LOCK')
        self.abort_lock.release()

        if self.process:
            fastr.log.debug('JOINING PROCESS')
            self.process.join(timeout=3)

            if self.process.is_alive():
                fastr.log.debug('TERMINATING PROCESS')
                self.process.terminate()


class ObjectUrl(fields.Raw):
    def __init__(self, object_classs, **kwargs):
        super(ObjectUrl, self).__init__(**kwargs)
        self._object_class = object_classs

    def format(self, value):
        if isinstance(self._object_class, str):
            return url_for(self._object_class, id=value)
        else:
            return api.url_for(self._object_class, id=value)


class SubUrl(fields.Raw):
    def __init__(self, object_classs, subfield, **kwargs):
        super(SubUrl, self).__init__(**kwargs)
        self._object_class = object_classs
        self._subfield = subfield

    def format(self, value):
        if isinstance(self._object_class, str):
            url = url_for(self._object_class, id=value)
        else:
            url = api.url_for(self._object_class, id=value)

        return '{}/{}'.format(url, self._subfield)


class NetworkApi(Resource):
    def get(self, id):
        return networks[id].dumps(method='dict')


class NetworkListApi(Resource):
    _fields = {
        'networks': fields.List(ObjectUrl('network', attribute='id'))
    }

    def get(self):
        data = {'networks': networks.values()}
        print('Data: {}'.format(data))
        return marshal(data, self._fields)


class RunApi(Resource):
    _fields = {
        'url': fields.Url,
        'network': ObjectUrl('network', attribute='network'),
        'status': ObjectUrl('status', attribute='id'),
        'source_data': fields.Raw,
        'sink_data': fields.Raw,
    }

    def get(self, id):
        return marshal(runs[id], self._fields)

    def delete(self, id):
        if id in runs:
            runs[id].abort()
        return None, 204


class RunListApi(Resource):
    _fields = {
        'runs': fields.List(ObjectUrl('run', attribute='id'))
    }

    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument('network', type=str, required=True, location='json',
                                         help='No network id specified')
        self.request_parser.add_argument('source_data', type=dict, required=True, location='json',
                                         help='No source data was supplied')
        self.request_parser.add_argument('sink_data', type=dict, required=True, location='json',
                                         help='No sink data was supplied')

    def get(self):
        return marshal({'runs': runs.values()}, self._fields)

    def post(self):
        args = self.request_parser.parse_args()

        network = networks[args['network']]
        run_id = '{}_{}'.format(network.id, datetime.datetime.now().isoformat())
        runs[run_id] = Run(run_id, network, args['source_data'], args['sink_data'])

        return {'run_id': run_id,
                'run': url_for('run', id=run_id, _external=True),
                'status': url_for('status', id=run_id, _external=True)}, 201, {'Location': url_for('run', id=run_id)}


class StatusApi(Resource):
    def get(self, id):
        status = runs[id].status()
        return status


api.add_resource(NetworkApi, '/api/networks/<id>', endpoint='network')
api.add_resource(NetworkListApi, '/api/networks', endpoint='networks')
api.add_resource(RunApi, '/api/runs/<id>', endpoint='run')
api.add_resource(RunListApi, '/api/runs', endpoint='runs')
api.add_resource(StatusApi, '/api/runs/<id>/status', endpoint='status')

