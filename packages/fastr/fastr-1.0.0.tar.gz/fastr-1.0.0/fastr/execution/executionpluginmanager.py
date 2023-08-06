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
This module holds the ExecutionPluginManager as well as the base-class
for all ExecutionPlugins.
"""

from abc import abstractmethod
import gzip
import multiprocessing
import os
import pickle
import sys
import threading
import traceback

import fastr
from fastr import exceptions
from fastr.core.baseplugin import BasePlugin
from fastr.core.pluginmanager import PluginManager


class ExecutionPlugin(BasePlugin):
    """
    This class is the base for all Plugins to execute jobs somewhere. There are
    many methods already in place for taking care of stuff. Most plugins should
    only need to redefine a few abstract methods:

    # __init__
    # cleanup
    # _queue_job
    # _cancel_job
    # _release_job
    # _job_finished

    When overwriting other function, extreme care must be taken not to break
    the plugins working.
    """

    @abstractmethod
    def __init__(self, finished_callback=None, cancelled_callback=None, status_callback=None):
        """
        Setup the ExecutionPlugin

        :param finished_callback: the callback to call after a job finished
        :param cancelled_callback: the callback to call after a job cancelled
        :return: newly created ExecutionPlugin
        """
        super(ExecutionPlugin, self).__init__()

        self.status_manager = multiprocessing.Manager()

        # Pylint seems to be unable to figure out the .dict() member
        # pylint: disable=no-member

        self.job_status = {}
        self.job_dict = {}
        self._finished_callback = finished_callback
        self._cancelled_callback = cancelled_callback
        self._status_callback = status_callback

        # Dict indicating the depending jobs for a certain jobs (who is waiting on the key jobid)
        self.held_queue = {}
        self.held_queue_lock = threading.Lock()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.cleanup()

    def __del__(self):
        """
        Cleanup if the variable was deleted on purpose
        """
        fastr.log.debug('Calling cleanup')
        self.cleanup()

    @abstractmethod
    def cleanup(self):
        """
        Method to call to clean up the ExecutionPlugin. This can be to clear
        temporary data, close connections, etc.

        :param force: force cleanup (e.g. kill instead of join a process)
        """
        pass

    def queue_job(self, job):
        """
        Add a job to the execution queue

        :param Job job: job to add
        """
        if isinstance(job, list):
            for j in job:
                self.queue_job(j)
            return

        self.job_dict[job.jobid] = job
        self.job_status[job.jobid] = 'queued'
        job.status = 'queued'

        for hold_id in job.hold_jobs:
            # Add job reference to held queue to receive signal when the
            # required jobs are finished/failed. Do not subscribe for jobs that
            # are already finished.
            if hold_id in self.job_status and self.job_status[hold_id] in ['finished', 'failed', 'cancelled']:
                continue

            with self.held_queue_lock:
                if hold_id not in self.held_queue:
                    self.held_queue[hold_id] = []

                # append to held_queue, because of the managed dict, we need to replace the value (not update)
                self.held_queue[hold_id].append(job.jobid)

        # Save the job to file before serializing
        with gzip.open(job.commandfile, 'wb') as fout:
            fastr.log.debug('Writing job pickle.gz to: {}'.format(job.commandfile))
            pickle.dump(job, fout)

        self._queue_job(job)

    def cancel_job(self, jobid):
        """
        Cancel a job previously queued

        :param jobid: job to cancel
        """
        fastr.log.debug('Cancelling {}'.format(jobid))
        job = self.job_dict[jobid]
        job.status = 'cancelled'
        self.job_status[jobid] = 'cancelled'

        self._cancel_job(job)

        fastr.log.debug('Cancelling children for {}'.format(jobid))
        if jobid in self.held_queue:
            fastr.log.debug('Found children....')
            held_queue = self.held_queue[jobid]
            for dependent_job in held_queue:
                fastr.log.debug('Checking sub {}'.format(dependent_job))
                if dependent_job in self.job_dict and dependent_job in self.job_status and self.job_status[dependent_job] not in ['failed', 'finished', 'cancelled']:
                    fastr.log.debug('Cancelling sub {}'.format(dependent_job))
                    self.cancel_job(dependent_job)
        else:
            fastr.log.debug('No children....')

        fastr.log.debug('Updating jobdict for {}'.format(job.jobid))
        self.job_dict[jobid] = job

        fastr.log.debug('Calling cancelled for {}'.format(jobid))
        if self._cancelled_callback is not None:
            self._cancelled_callback(job)

    def release_job(self, jobid):
        """
        Release a job that has been put on hold

        :param jobid: job to release
        """
        job = self.job_dict[jobid]
        job.status = 'queued'
        self._release_job(jobid)

    def job_finished(self, job, blocking=False):
        """
        The default callback that is called when a Job finishes. This will
        create a new thread that handles the actual callback.

        :param Job job: the job that finished
        :return:
        """
        if not blocking:
            # The callback has to finish immediately, so create thead to handle callback and return
            callback_thread = threading.Thread(target=self._job_finished_body,
                                               name='fastr_jobfinished_callback',
                                               args=(job,))
            callback_thread.start()
        else:
            self._job_finished_body(job)

    def _job_finished_body(self, job):
        """
        The actual callback that is executed in a separate thread. This
        method handles the collection of the result, the release of depending
        jobs and calling the user defined callback.

        :param Job job: the job that finished
        """
        fastr.log.debug('ExecutorInterface._job_finished_callback called')

        # The Job finished should always log the errors rather than
        # crashing the whole execution system
        # pylint: disable=bare-except
        try:
            if os.path.exists(job.logfile):
                with gzip.open(job.logfile, 'rb') as fin:
                    job = pickle.loads(fin.read())
                    if self._status_callback is not None:
                        self._status_callback(job)
                        job.status_callback = self._status_callback
            else:
                job.info_store['errors'].append(
                    exceptions.FastrResultFileNotFound(
                        ('Could not find job result file {}, assuming '
                         'the job crashed before it created output.').format(job.logfile)).excerpt())
                job.status = 'failed'
        except:
            exc_type, _, trace = sys.exc_info()
            exc_info = traceback.format_exc()
            trace = traceback.extract_tb(trace, 1)[0]
            fastr.log.error('Encountered exception ({}) during execution:\n{}'.format(exc_type.__name__, exc_info))
            if 'errors' not in job.info_store:
                job.info_store['errors'] = []
            job.info_store['errors'].append((exc_type.__name__, exc_info, trace[0], trace[1]))
            job.status = 'error'

        result = job
        fastr.log.debug('Finished {} with status {}'.format(job.jobid, job.status))
        jobid = result.jobid

        # Make sure the status is either finished or failed
        if result.status == 'exec_done':
            result.status = 'finished'
        elif result.status != 'failed':
            result.status = 'failed'

        fastr.log.debug('Changing status of {} to {}'.format(jobid, result.status))
        self.job_status[jobid] = result.status
        self.job_dict[jobid] = result

        # The ProcessPoolExecutor has to track job dependencies itself, so
        # therefor we have to check for jobs depending on the finished job
        if jobid in self.held_queue:
            fastr.log.debug('Signaling depending jobs {}'.format(self.held_queue[jobid]))
            ready_jobs = []
            for held_jobid in self.held_queue[jobid]:
                action = self.check_job_requirements(held_jobid)
                if action == 'ready':
                    # Re-assign managed dict member
                    held_job = self.job_dict[held_jobid]
                    held_job.status = 'ready'
                    self.job_dict[held_jobid] = held_job
                    fastr.log.debug('Job {} is now ready to be submitted'.format(held_jobid))

                    # If ready, flag job for removal from held queue and send
                    # to pool queue to be executed
                    ready_jobs.append(held_jobid)
                    self.release_job(held_jobid)
                elif action == 'cancel':
                    fastr.log.info('Job {} will be cancelled'.format(held_jobid))
                    ready_jobs.append(held_jobid)
                    self.cancel_job(held_jobid)
                else:
                    fastr.log.debug('Job {} still has unmet dependencies'.format(held_jobid))

            # Remove jobs that no longer need to be held from held_queue
            for readyjobid in ready_jobs:
                job = self.job_dict[readyjobid]
                for hold_id in job.hold_jobs:
                    with self.held_queue_lock:
                        if hold_id in self.held_queue:
                            # remove from held_queue. because of the managed dict,
                            # we need to replace the value (not update)
                            required_job = self.held_queue[hold_id]
                            if readyjobid in required_job:
                                required_job.remove(readyjobid)
                            else:
                                fastr.log.warning('Could not remove {} from {}'.format(readyjobid, required_job))

            with self.held_queue_lock:
                del self.held_queue[jobid]

        # Extra subclass options
        fastr.log.debug('Subclass callback')
        self._job_finished(result)

        fastr.log.debug('Calling callback for {}'.format(jobid))
        if self._finished_callback is not None:
            self._finished_callback(result)
        else:
            fastr.log.debug('No callback specified')

    @abstractmethod
    def _queue_job(self, job):
        """
        Method that a subclass implements to actually queue a Job for execution

        :param job: job to queue
        """
        pass

    @abstractmethod
    def _cancel_job(self, jobid):
        """
        Method that a subclass implements to actually cancel a Job

        :param jobid: job to queue
        """
        pass

    @abstractmethod
    def _release_job(self, jobid):
        """
        Method that a subclass implements to actually realse a job

        :param jobid: job to queue
        """
        pass

    @abstractmethod
    def _job_finished(self, job):
        """
        Method that a subclass can implement to add to the default callback.
        It will be called by ``_job_finished_body`` right before the user
        defined callback will be called.

        :param job: Job that resulted from the execution
        """
        pass

    def show_jobs(self, req_status=None):
        """
        List the queued jobs, possible filtered by status

        :param req_status: requested status to filter on
        :return: list of jobs
        """
        if req_status not in [None, 'queued', 'hold', 'running', 'finished', 'failed', 'cancelled']:
            return []

        results = []
        for key, status in self.job_status.items():
            if req_status is None or status == req_status:
                results.append(self.job_dict[key])

        return results

    def check_job_status(self, jobid):
        """
        Get the status of a specified job

        :param jobid: the target job
        :return: the status of the job (or None if job not found)
        """
        if jobid in self.job_status:
            return self.job_status[jobid]
        else:
            return None

    def check_job_requirements(self, jobid):
        """
        Check if the requirements for a job are fulfilled.

        :param jobid: job to check
        :return: a string from {'ready', 'hold', 'cancel'} indicating
                 what should happen with the job
        """
        job = self.job_dict[jobid]
        if job.hold_jobs is None or len(job.hold_jobs) == 0:
            return 'ready'

        all_done = True
        for hold_id in job.hold_jobs:
            status = self.check_job_status(hold_id)
            if status in ['failed', 'cancelled']:
                return 'cancel'
            elif status != 'finished':
                fastr.log.debug('Dependency {} for {} is unmet ({})'.format(hold_id, jobid, status))
                all_done = False

        if all_done:
            return 'ready'
        else:
            return 'hold'


class ExecutionPluginManager(PluginManager):
    """
    Container holding all the ExecutionPlugins known to the Fastr system
    """

    def __init__(self, path=None, recursive=False):
        """
        Initialize a ExecutionPluginManager and load plugins.

        :param path: path to search for plugins
        :param recursive: flag for searching recursively
        :return: newly created ExecutionPluginManager
        """
        super(ExecutionPluginManager, self).__init__(path, recursive)

    @property
    def plugin_class(self):
        """
        The class of the Plugins expected in this PluginManager
        """
        return ExecutionPlugin

    @property
    def _instantiate(self):
        """
        Flag indicating if Plugins should not be saved in instantiated form
        """
        return False
