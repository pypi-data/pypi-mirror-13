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

import fastr
from fastr.execution.job import Job
import copy
try:
    import drmaa
    load_drmaa = True
except RuntimeError:
    fastr.log.warning("DRMAA module is not available.")
    load_drmaa = False
import threading
import os
import sys

from fastr.execution.executionpluginmanager import ExecutionPlugin


class DRMAAExecution(ExecutionPlugin):
    if load_drmaa:
        try:
            # Try to create a session
            session = drmaa.Session()
            session.initialize()
            session.exit()
            del session
        except:
            _status = ('Failed', 'Could not create a DRMAA session')
    else:
        _status = ('Failed', 'Could not load DRMAA module required for cluster communication')

    def __init__(self, finished_callback=None, cancelled_callback=None, status_callback=None):
        super(DRMAAExecution, self).__init__(finished_callback, cancelled_callback, status_callback)

        # Some default
        self.default_queue = 'day'

        # Create the DRMAA session
        self.session = drmaa.Session()
        self.session.initialize()
        fastr.log.info('A DRMAA session was started successfully')
        response = self.session.contact
        fastr.log.info('session contact returns: ' + response)

        # Create job translation table
        self.job_translation_table = self.status_manager.dict()
        self.job_lookup_table = dict()

        # Create even queue lock
        self.queue_lock = threading.Event()

        # Create callback collector
        fastr.log.debug('Creating job collector')
        self.collector = threading.Thread(name='DRMAAJobCollector-0', target=self.collect_jobs, args=())
        self.collector.daemon = True
        fastr.log.debug('Starting job collector')
        self.running = True
        self.collector.start()

    def cleanup(self):
        fastr.log.debug('Stopping DRMAA executor')
        self.running = False  # Signal collector thread to stop running
        try:
            self.session.exit()
            fastr.log.debug('Exiting DRMAA session')
        except drmaa.NoActiveSessionException:
            pass
        if self.collector.isAlive():
            fastr.log.debug('Terminating job collector thread')
            self.collector.join()
        fastr.log.debug('DRMAA executor stopped!')

    def _queue_job(self, job):
        # Get job command and write to file
        command = [sys.executable,
                   os.path.join(fastr.config.executionscript),
                   job.commandfile]

        fastr.log.debug('Command to queue: {}'.format(command))
        fastr.log.debug('Queueing {} via DRMAA'.format(job.jobid))

        # Submit command to schedular
        cl_job_id = self.send_job(command[0], command[1:], job_name='fastr_{}'.format(job.jobid),
                                  memory=job.required_memory,
                                  ncores=job.required_cores,
                                  walltime=job.required_time,
                                  outputLog=job.stdoutfile,
                                  errorLog=job.stderrfile,
                                  hold_job=[self.job_lookup_table[x] for x in job.hold_jobs if x in self.job_lookup_table],
                                  )

        # Register job in the translation tables
        self.job_translation_table[cl_job_id] = job
        fastr.log.debug('Inserting {} in lookup table pointing to {}'.format(job.jobid, cl_job_id))
        self.job_lookup_table[job.jobid] = cl_job_id
        fastr.log.info('Job {} queued via DRMAA'.format(job.jobid))

        # Set the queue lock to indicate there is content in the queue
        if not self.queue_lock.is_set():
            fastr.log.debug('Setting queue_lock')
            self.queue_lock.set()

    def _cancel_job(self, jobid):
        if isinstance(jobid, Job):
            jobid = jobid.jobid

        drmaa_job_id = self.job_lookup_table[jobid]
        fastr.log.info('Cancelling job {}'.format(drmaa_job_id))
        try:
            self.session.control(drmaa_job_id, 'terminate')
        except drmaa.InvalidJobException:
            fastr.log.warning('Trying to cancel an unknown job, already finished/cancelled?')

        del self.job_translation_table[drmaa_job_id]

    def _release_job(self, jobid):
        pass

    def _job_finished(self, result):
        pass

    # FIXME This needs to be more generic! This is for our SGE cluster only!
    def send_job(self, command, arguments, queue=None, walltime=None, job_name=None, memory=None, ncores=None, joinLogFiles=False, outputLog=None, errorLog=None, hold_job=None):

        # Create job template
        jt = self.session.createJobTemplate()
        jt.remoteCommand = command

        jt.args = arguments
        jt.joinFiles = joinLogFiles
        env = os.environ
        # Make sure environment modules do not annoy use with bash warnings
        # after the shellshock bug was fixed
        env.pop('BASH_FUNC_module()', None)
        jt.jobEnvironment = env

        if queue is None:
            queue = self.default_queue

        native_spec = '-cwd -q %s' % queue

        if walltime is not None:
            native_spec += ' -l h_rt=%s' % walltime

        if memory is not None:
            native_spec += ' -l h_vmem=%s' % memory

        if ncores is not None:
            native_spec += ' -pe smp %d' % ncores

        if outputLog is not None:
            native_spec += ' -o %s' % outputLog

        if errorLog is not None:
            native_spec += ' -e %s' % errorLog

        if hold_job is not None:
            if isinstance(hold_job, int):
                native_spec += ' -hold_jid {}'.format(hold_job)
            elif isinstance(hold_job, list) or isinstance(hold_job, tuple):
                if len(hold_job) > 0:
                    jid_list = ','.join([str(x) for x in hold_job])
                    native_spec += ' -hold_jid {}'.format(jid_list)
            else:
                fastr.log.error('Incorrect hold_job type!')

        fastr.log.debug('Setting native spec to: {}'.format(native_spec))
        jt.nativeSpecification = native_spec
        if job_name is None:
            job_name = command
            job_name = job_name.replace(' ', '_')
            job_name = job_name.replace('"', '')
            if len(job_name) > 32:
                job_name = job_name[0:32]

        jt.jobName = job_name

        # Send job to cluster
        jobid = self.session.runJob(jt)

        # Remove job template
        self.session.deleteJobTemplate(jt)

        return jobid

    def collect_jobs(self):
        first_wait = True
        second_wait = True

        while self.running:
            # Wait for the queue to contain
            if first_wait and not self.queue_lock.is_set():
                fastr.log.debug('Waiting jobs to be queued...')

            if not self.queue_lock.wait(2):
                first_wait = False
                continue

            first_wait = True

            if second_wait:
                fastr.log.debug('Waiting for a job to finish...')

            try:
                info = self.session.wait(drmaa.Session.JOB_IDS_SESSION_ANY, 5)
                second_wait = True
            except drmaa.ExitTimeoutException:
                second_wait = False
                continue
            except drmaa.InvalidJobException:
                fastr.log.debug('No valid jobs (session queue appears to be empty)')
                fastr.log.debug('Clearing queue_lock')
                self.queue_lock.clear()
                continue
            except drmaa.NoActiveSessionException:
                if not self.running:
                    fastr.log.info('DRMAA session no longer active, quiting collector...')
                else:
                    fastr.log.critical('DRMAA session no longer active, but DRMAA executor not stopped properly! Quitting')
                    self.running = False
                continue
            except drmaa.errors.DrmaaException as exception:
                # Avoid the collector getting completely killed on another DRMAA exception
                fastr.log.warning('Encountered unexpected DRMAA exception: {}'.format(exception))
                second_wait = True
            except Exception as exception:
                if exception.message == 'code 24: no usage information was returned for the completed job':
                    # Avoid the collector getting completely killed this specific exception
                    fastr.log.warning('Encountered unexpected DRMAA exception: {}'.format(exception))
                    second_wait = True
                else:
                    raise

            fastr.log.info('Cluster DRMAA job {} finished'.format(info.jobId))

            # Create a copy of the job that finished and remove from the translation table
            job = copy.deepcopy(self.job_translation_table.get(info.jobId))

            if job is not None:
                del self.job_translation_table[info.jobId]

                # Send the result to the callback function
                self.job_finished(job)
            else:
                fastr.log.warning('Job {} no longer available (got cancelled?)'.format(info.jobId))
