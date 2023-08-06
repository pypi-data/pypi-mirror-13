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
FASTR_LOG_TYPE = 'none'  # Do not get info about fastr


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', metavar='result.pickle.gz', help='result file to cat')
    parser.add_argument('path', help='path of the data to print')
    return parser


def main(args=None, unknown_args=None):
    """
    Print information from a job file
    """
    if args is None and unknown_args is None:
        # No arguments were parsed yet, parse them now
        parser = get_parser()
        args, unknown_args = parser.parse_known_args()

    import gzip
    import os
    import pickle
    from pprint import pprint

    infile = args.infile
    path = args.path.strip('/').split('/')

    if os.path.isdir(infile):
        infile = os.path.join(infile, '__fastr_result__.pickle.gz')

        if not os.path.isfile(infile):
            print('ERROR: Input file does not exist!')
            return

    try:
        with gzip.open(infile) as fh:
            job = pickle.load(fh)
    except IOError:
        print('ERROR: Could not open {} for reading'.format(infile))

    data = job.info_store

    for part in path:
        try:
            data = data[part]
        except KeyError:
            raise KeyError('{} not found in {}'.format(part, data.keys()))

    if isinstance(data, str):
        for line in data.split('\n'):
            print line
    else:
        pprint(data)


if __name__ == '__main__':
    main()
