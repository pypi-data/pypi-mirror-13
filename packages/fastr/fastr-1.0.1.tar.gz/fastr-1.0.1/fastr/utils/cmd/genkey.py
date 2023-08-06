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
    parser = argparse.ArgumentParser(description="Generate a keypair for secure client to server communication")
    parser.add_argument('--force', action='store_true', help='generate a new key even if one already exists')
    parser.add_argument('--nbits', type=int, help='size of the key in bits, default 4096', default=4096)
    return parser


def main(args=None, unknown_args=None):
    """
    (Re-)Generate a key pair for the fastr daemon
    """
    if args is None and unknown_args is None:
        # No arguments were parsed yet, parse them now
        parser = get_parser()
        args, unknown_args = parser.parse_known_args()

    from fastr.utils import keygen

    nbits = args.nbits

    if args.force:
        # Forced to generate keys
        keygen.update_key_pair(nbits=nbits)
    else:
        # Only make a new pair when there is no key present.
        keygen.check_key_pair(nbits=nbits)

if __name__ == '__main__':
    main()
