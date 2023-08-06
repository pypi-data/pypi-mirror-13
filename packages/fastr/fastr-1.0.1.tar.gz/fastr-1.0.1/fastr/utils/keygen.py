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

import fastr
import os
import stat
from fastr import config
from Crypto.PublicKey import RSA

PUBLIC_KEY_FILENAME = 'fastrpublic.pem'
PRIVATE_KEY_FILENAME = 'fastrprivate.pem'


def check_key(filename):
    """ Raise IOError if filename exists but is not a file. Otherwise return True. """
    if os.path.exists(filename) and not os.path.isfile(filename):
        raise IOError("Key has to be a file ({})".format(filename))
    return True


def check_permissions(filename, mode=stat.S_IRUSR | stat.S_IWUSR):
    return (os.stat(filename).st_mode & 0777) == mode


def enforce_permissions(filename, mode=stat.S_IRUSR | stat.S_IWUSR):
    """ Enforce the permissions defined by mode to filename. Default mode is '0600'. """
    check_permissions(filename, mode)
    os.chmod(filename, mode)
    # If the permissions were not correctly set, remove the file.
    if not check_permissions(filename, mode):
        fastr.log.warning("rollback {}".format(filename))
        os.remove(filename)
        return False


def update_key_pair(directory=fastr.config.secretdir, nbits=4096):
    public_key_file = os.path.join(directory, PUBLIC_KEY_FILENAME)
    private_key_file = os.path.join(directory, PRIVATE_KEY_FILENAME)

    if check_key(public_key_file) and check_key(private_key_file):
        fastr.log.info("Creating a new public/private keypair.")
        priv_key = RSA.generate(nbits)
        pub_key = priv_key.publickey()
        with open(public_key_file, 'w') as pubkfh, open(private_key_file, 'w') as privkfh:
            pubkfh.write(pub_key.exportKey())
            privkfh.write(priv_key.exportKey())

        enforce_permissions(private_key_file)
        enforce_permissions(public_key_file)


def check_key_pair(nbits=4096):
    if not config.authentication['allow_anonymous']:
        private_key_file = os.path.join(config.secretdir, PRIVATE_KEY_FILENAME)
        public_key_file = os.path.join(config.secretdir, PUBLIC_KEY_FILENAME)
        # Check if the private and public keyfile can be written.
        if check_key(private_key_file) or check_key(public_key_file):
            # If the pair is incomplete or non-existent generate a new key pair.
            if not os.path.isfile(private_key_file) or not os.path.isfile(public_key_file):
                fastr.log.info("(New) private/public keypair is generated.")
                update_key_pair(nbits=nbits)
            else:
                fastr.log.info("Using the existing private/public keypair.")
    else:
        fastr.log.warning("Skipping public/private key check because allow_anonymous is set to True in the config. Force to make a new key pair by supplying -k/--generate-keys flag to the daemon.")


def get_public_key():
    key_fname = os.path.join(fastr.config.secretdir, PUBLIC_KEY_FILENAME)
    if os.path.isfile(key_fname):
        with open(key_fname, 'r') as f:
            key = RSA.importKey(f.read())
            pub_key = key.publickey().exportKey()

    else:
        pub_key = None
    return pub_key


def get_private_key():
    key_fname = os.path.join(fastr.config.secretdir, PRIVATE_KEY_FILENAME)
    if os.path.isfile(key_fname):
        with open(key_fname, 'r') as f:
            key = RSA.importKey(f.read())
    else:
        key = None
    return key


if __name__ == "__main__":
    update_key_pair()