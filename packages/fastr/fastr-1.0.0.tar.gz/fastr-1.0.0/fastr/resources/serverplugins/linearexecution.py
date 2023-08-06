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

import os
import subprocess
import sys
import traceback
import fastr
import fastr.resources
from fastr.execution.executionpluginmanager import ExecutionPlugin

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


class LinearExecution(ExecutionPlugin):
    def __init__(self, finished_callback=None, cancelled_callback=None, status_callback=None):
        super(LinearExecution, self).__init__(finished_callback, cancelled_callback, status_callback)

    def cleanup(self):
        pass

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
            run_job(job, self.job_status)
            self.job_finished(job)
