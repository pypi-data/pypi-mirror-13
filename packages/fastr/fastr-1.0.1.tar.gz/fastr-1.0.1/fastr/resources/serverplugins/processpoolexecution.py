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

import multiprocessing
import os
import subprocess
import sys
import traceback
import fastr
from fastr.execution.executionpluginmanager import ExecutionPlugin
from fastr.utils.multiprocesswrapper import function_wrapper


def run_job(job, job_status):
    try:
        fastr.log.debug('Running job {}'.format(job.jobid))
        job_status[job.jobid] = 'running'

        command = [sys.executable,
                   os.path.join(fastr.config.executionscript),
                   job.commandfile]

        with open(job.stdoutfile, 'w') as fh_stdout, open(job.stderrfile, 'w') as fh_stderr:
            proc = subprocess.Popen(command, stdout=fh_stdout, stderr=fh_stderr)
            proc.wait()
            fastr.log.debug('Subprocess finished')
        fastr.log.debug('Finished {}'.format(job.jobid))
    except Exception:
        exc_type, _, trace = sys.exc_info()
        exc_info = traceback.format_exc()
        trace = traceback.extract_tb(trace, 1)[0]
        fastr.log.error('Encountered exception ({}) during execution:\n{}'.format(exc_type.__name__, exc_info))
        job.info_store['errors'].append((exc_type.__name__, exc_info, trace[0], trace[1]))
        job.status = 'failed'

    return job


class ProcessPoolExecution(ExecutionPlugin):
    _status = ('Uninitialized', 'Please use the test() function to check DRMAA capability')

    def __init__(self, finished_callback=None, cancelled_callback=None, status_callback=None, nr_of_workers=None):
        super(ProcessPoolExecution, self).__init__(finished_callback, cancelled_callback, status_callback)

        # Default number of workers is core - 1 (to assure system
        # responsiveness)
        if nr_of_workers is None:
            nr_of_workers = max(multiprocessing.cpu_count() - 1, 1)

        self.pool = multiprocessing.Pool(processes=nr_of_workers)

    def cleanup(self):
        # Close the multiprocess pool
        fastr.log.debug('Stopping ProcessPool')

        fastr.log.debug('Terminating worker processes...')
        self.pool.terminate()

        fastr.log.debug('Joining worker processes...')
        self.pool.join()

        fastr.log.debug('ProcessPool stopped!')

    @classmethod
    def test(cls):
        try:
            # See if we can make a Pool and then remove it
            fastr.log.debug('Creating Pool')
            pool = multiprocessing.Pool(processes=2)
            fastr.log.debug('Terminating Pool')
            pool.terminate()
            del pool
            _status = ('Loaded', '')
        except OSError:
            _status = ('Failed', 'Multiprocessing Failed ({}):\n{}'.format(sys.exc_info()[0].__name__, traceback.format_exc()))

        cls._status = _status

    def _job_finished(self, result):
        pass

    def _cancel_job(self, jobid):
        pass

    def _release_job(self, jobid):
        self.queue_job(self.job_dict[jobid])

    def _queue_job(self, job):
        # Check if the job is ready to run or must be held
        action = self.check_job_requirements(job.jobid)
        if action == 'hold':
            fastr.log.debug('Holding {} until dependencies are met'.format(job.jobid))
            self.job_status[job.jobid] = 'hold'
            job.status = 'hold'
        elif action == 'cancel':
            self.cancel_job(job)
        else:
            fastr.log.debug('Queueing {}'.format(job.jobid))
            self.pool.apply_async(function_wrapper, [os.path.abspath(__file__), 'run_job', job, self.job_status], callback=self.job_finished)
