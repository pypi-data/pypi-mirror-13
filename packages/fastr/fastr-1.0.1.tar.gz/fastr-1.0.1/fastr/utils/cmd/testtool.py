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
    parser = argparse.ArgumentParser(description="Run the tests for a Tool to check the function")
    parser.add_argument('tool', metavar='TOOL', help='the id of the tool to test')
    return parser


def main(args=None, unknown_args=None):
    """
    Run the tests of a tool to verify the proper function    
    """
    if args is None and unknown_args is None:
        # No arguments were parsed yet, parse them now
        parser = get_parser()
        args, unknown_args = parser.parse_known_args()

    import fastr
    tool = fastr.toollist[args.tool]
    try:
        tool.test()
    except fastr.exceptions.FastrValueError as e:
        fastr.log.error('Tool is not valid: {}'.format(e))

if __name__ == '__main__':
    main()
