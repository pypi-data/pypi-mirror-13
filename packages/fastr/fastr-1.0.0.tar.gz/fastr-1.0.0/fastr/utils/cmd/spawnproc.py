#!/usr/bin/env python

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

import argparse

FASTR_LOG_TYPE = 'worker'


def get_parser():
    parser = argparse.ArgumentParser(description="Start a child processing running a Fastr service.")
    parser.add_argument('-s', '--service', default='fastrd', help="Indicate which service should be started.")
    parser.add_argument('-a', '--address', default='0.0.0.0', help="Address of the parent service.")
    parser.add_argument('-p', '--port', default='0', help="Port of the parent service.")
    parser.add_argument('-n', '--name', default='fastrd', help="Give the process a name")
    return parser


def main(args=None, unknown_args=None):
    """
    Spawn a worker process (not intended for human use)
    """
    if args is None and unknown_args is None:
        # No arguments were parsed yet, parse them now
        parser = get_parser()
        args, unknown_args = parser.parse_known_args()

    import sys
    import multiprocessing

    # Get magic and determine log type
    magic = sys.stdin.read()

    # Set the python internal process name to something more readable
    procname = args.name
    if not procname.startswith('fastr'):
        procname = 'fastr-{}'.format(procname)

    cp = multiprocessing.current_process()
    cp.name = procname

    # If possible, change the system process name to something more readable
    try:
        import setproctitle
        setproctitle.setproctitle(procname)
    except ImportError:
        pass

    from fastr.services.service import start_service
    start_service(args, magic)


if __name__ == '__main__':
    main()
