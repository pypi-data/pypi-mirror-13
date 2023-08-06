#!/usr/bin/python

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
The executionscript is the script that wraps around a tool executable. It
takes a job, builds the command, executes the command (while profiling it)
and collects the results.
"""

import gzip
import os
import pickle
import sys
import traceback
import urlparse

FASTR_LOG_TYPE = 'console'
import fastr
from fastr import exceptions
from fastr.execution.job import Job, SinkJob
from fastr.utils.sysinfo import get_hostinfo, get_sysinfo

_MONITOR_INTERVAL = 1.0

# We will run untrusted subprocesses and want to log everything also in case
# of an error. Therefor there are a few bare-except blocks which are intended
# to ensure as much as possible logging in case of errors.
# pyline: disable=bare-except

fastr.toollist._populate()

def execute_job(job):
    """
    Execute a Job and save the result to disk

    :param job: the job to execute
    """
    fastr.log.info('FASTR loaded from {}'.format(fastr.__file__))
    job_dir = fastr.vfs.url_to_path(job.tmpdir)
    fastr.log.info('Set current directory to job output dir {}'.format(job_dir))
    os.chdir(job_dir)

    logfile_path = job.logfile
    fastr.log.info('Job log path: {}'.format(logfile_path))

    fastr.log.info('Running job {}\n  command: {} v{}\n  arguments: {}\n  outputs: {}\n'.format(job.jobid, job.tool_name, job.tool_version, job.input_arguments, job.output_arguments))
    try:
        job.info_store['status'].append('running')
        job.info_store['hostinfo'] = get_hostinfo()
        job.info_store['sysinfo_start'] = get_sysinfo()

        fastr.log.info('DRMAA info: {}'.format(job.info_store['hostinfo']['drmaa']))

        job.execute()

        # Document system information after
        fastr.log.info('Job subprocess finished')
        job.info_store['sysinfo_end'] = get_sysinfo()

        job.hash_results()

    except:
        # Log errors to the info store
        if 'process' not in job.info_store:
            job.info_store['errors'].append(exceptions.FastrSubprocessNotFinished('There is no information that the subprocess finished properly: appears the job crashed before the subprocess registered as finished.').excerpt())
        elif job.info_store['process']['stderr'] != '':
            job.info_store['errors'].append(exceptions.FastrErrorInSubprocess(job.info_store['process']['stderr']).excerpt())
        exc_type, exception, trace = sys.exc_info()
        exc_info = traceback.format_exc()
        if isinstance(exception, exceptions.FastrError):
            job.info_store['errors'].append((exc_type.__name__, exception, exception.filename, exception.linenumber))
        else:
            trace = traceback.extract_tb(trace, 1)[0]
            job.info_store['errors'].append((exc_type.__name__, exception, trace[0], trace[1]))
        fastr.log.critical('Execution script encountered errors: {}'.format(exc_info))
        job.info_store['status'].append('exec_failed')
    else:
        job.info_store['status'].append('exec_done')
    finally:
        fastr.log.info('Writing job result to: {}'.format(logfile_path))
        with gzip.open(logfile_path, 'wb') as result_file:
            result_file.write(pickle.dumps(job))

        # If Sink Job write prov next to sink output.
        if isinstance(job, SinkJob):
            fastr.log.info('SinkJob input arguments: {}'.format(job.input_arguments))
            arguments = {key: value for key, value in job.input_arguments.items()}
            for output_value in arguments['output']:
                # TODO: Since we want to move to other means of storing prov documents, this is a quick and dirty fix for supporting url's with query information.
                url = urlparse.urlparse(job.substitute(output_value, datatype=type(arguments['input'].data.sequence_part()[0])))
                result_url = urlparse.urlunparse(url._replace(path=url.path+".prov.pickle.gz"))
                fastr.ioplugins.put_url(logfile_path, result_url)
        # Cleanup all plugins
        fastr.ioplugins.cleanup()


def main(joblist=None):
    """
    This is the main code. Wrapped inside a function to avoid the variables
    being seen as globals and to shut up pylint. Also if the joblist argument
    is given it can run any given job, otherwise it takes the first command
    line argument.
    """
    fastr.log.info('----- Execution script -----\n')
    if joblist is None:
        joblist = sys.argv[1]

    if os.path.exists(joblist) and os.path.isfile(joblist):
        fastr.log.info('Loading pickled command from file')
        with gzip.open(joblist, 'rb') as fin:
            joblist = pickle.load(fin)

    # Both the error we raise and not able to iterate joblist will result in a
    # TypeError, so we catch both and give our own TypeError message
    try:
        if not isinstance(joblist, Job) and not all(isinstance(x, Job) for x in joblist):
            raise TypeError('Wrong type!')
    except TypeError:
        message = 'Argument should be a Job or a iterable of Jobs! (Found: {})'.format(joblist)
        fastr.log.critical(message)
        raise exceptions.FastrTypeError(message)

    fastr.log.info('Received command: {command}\n'.format(command=joblist))

    if isinstance(joblist, list) or isinstance(joblist, tuple):
        for job in joblist:
            execute_job(job)
    elif isinstance(joblist, Job):
        execute_job(joblist)
    fastr.log.info('---------------------------\n')


if __name__ == '__main__':
    main()
