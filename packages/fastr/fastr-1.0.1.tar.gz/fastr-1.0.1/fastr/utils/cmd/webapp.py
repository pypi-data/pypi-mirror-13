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
from threading import Timer
from webbrowser import open_new_tab

from fastr import config
from fastr.web.run import runapp

def get_parser():
    parser = argparse.ArgumentParser(description="Fastr web client")
    parser.add_argument('-d', '--debug', action="store_true", help="Debug mode.")
    return parser


def open_url(url):
    print('Opening webapp in webbrowser using {}'.format(url))
    open_new_tab(url)


def main(args=None, unknown_args=None):
    """
    Start the fastr webapp and open in a new browser tab
    """
    if args is None and unknown_args is None:
        # No arguments were parsed yet, parse them now
        parser = get_parser()
        args, unknown_args = parser.parse_known_args()

    url = 'http://{host}:{port}'.format(host=config.web['hostname'], port=config.web['port'])
    t = Timer(1.0, open_url, args=[url])
    t.daemon = True
    t.start()
    runapp(args.debug)


if __name__ == '__main__':
    main()
