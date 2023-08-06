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


def get_parser():
    parser = argparse.ArgumentParser(description="Stop the fastr daemon")
    return parser


def main(args=None, unknown_args=None):
    """
    Stop the fastr daemon
    """
    if args is None and unknown_args is None:
        # No arguments were parsed yet, parse them now
        parser = get_parser()
        args, unknown_args = parser.parse_known_args()

    # Set log
    import fastr
    fastr.config.logtype = 'daemon'
    fastr.config._update_logging()

    # Start the daemon
    from fastr.services.daemonizer import Daemonizer
    daemonizer = Daemonizer()
    daemonizer.stop()


if __name__ == '__main__':
    main()
