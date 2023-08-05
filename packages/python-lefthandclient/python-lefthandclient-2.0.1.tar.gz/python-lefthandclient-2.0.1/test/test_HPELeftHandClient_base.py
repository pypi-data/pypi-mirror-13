# (c) Copyright 2015 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test base class of LeftHand Client"""

import sys
import os

import unittest
import subprocess
import time
import inspect
from testconfig import config
import datetime

from hpelefthandclient import client

try:
    # For Python 3.0 and later
    from urllib.parse import urlparse
except ImportError:
    # Fall back to Python 2's urllib2
    from urlparse import urlparse

TIME = datetime.datetime.now().strftime('%H%M%S')


class HPELeftHandClientBaseTestCase(unittest.TestCase):

    cluster_id = 0
    GB_TO_BYTES = 1073741824    # Gibibytes to bytes
    MISSING_SERVER_ID = sys.maxsize
    MISSING_VOLUME_ID = -1

    user = config['TEST']['user']
    password = config['TEST']['pass']
    cluster = config['TEST']['cluster']
    flask_url = config['TEST']['flask_url']
    url_lhos = config['TEST']['lhos_url']
    debug = config['TEST']['debug'].lower() == 'true'
    unitTest = config['TEST']['unit'].lower() == 'true'
    startFlask = config['TEST']['start_flask_server'].lower() == 'true'

    remote_copy = config['TEST']['run_remote_copy'].lower() == 'true'
    run_remote_copy = remote_copy and not unitTest
    if run_remote_copy:
        secondary_user = config['TEST_REMOTE_COPY']['user']
        secondary_password = config['TEST_REMOTE_COPY']['pass']
        secondary_url_lhos = config['TEST_REMOTE_COPY']['lhos_url']
        secondary_cluster = config['TEST_REMOTE_COPY']['cluster']

    ssh_port = None
    if 'ssh_port' in config['TEST']:
        ssh_port = int(config['TEST']['ssh_port'])
    elif unitTest:
        ssh_port = 2200
    else:
        ssh_port = 16022

    # Don't setup SSH unless needed.  It slows things down.
    withSSH = False

    if 'known_hosts_file' in config['TEST']:
        known_hosts_file = config['TEST']['known_hosts_file']
    else:
        known_hosts_file = None

    if 'missing_key_policy' in config['TEST']:
        missing_key_policy = config['TEST']['missing_key_policy']
    else:
        missing_key_policy = None

    def setUp(self, withSSH=False):

        self.withSSH = withSSH

        cwd = os.path.dirname(os.path.abspath(
                              inspect.getfile(inspect.currentframe())))

        if self.unitTest:
            self.printHeader('Using flask ' + self.flask_url)
            self.cl = client.HPELeftHandClient(self.flask_url)
            parsed_url = urlparse(self.flask_url)
            userArg = '-user=%s' % self.user
            passwordArg = '-password=%s' % self.password
            portArg = '-port=%s' % parsed_url.port

            script = 'HPELeftHandMockServer_flask.py'
            path = "%s/%s" % (cwd, script)
            try:
                if self.startFlask:
                    self.mockServer = subprocess.Popen([sys.executable,
                                                        path,
                                                        userArg,
                                                        passwordArg,
                                                        portArg],
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE,
                                                       stdin=subprocess.PIPE)
                else:
                    pass
            except Exception:
                pass
            time.sleep(1)

            if self.withSSH:
                self.printHeader('Using paramiko SSH server on port %s' %
                                 self.ssh_port)

                ssh_script = 'HPELeftHandMockServer_ssh.py'
                ssh_path = "%s/%s" % (cwd, ssh_script)

                self.mockSshServer = subprocess.Popen([sys.executable,
                                                       ssh_path,
                                                       str(self.ssh_port)],
                                                      stdout=subprocess.PIPE,
                                                      stderr=subprocess.PIPE,
                                                      stdin=subprocess.PIPE)
                time.sleep(1)
        else:
            self.printHeader('Using LeftHand ' + self.url_lhos)
            self.cl = client.HPELeftHandClient(self.url_lhos)

        if self.withSSH:
            # This seems to slow down the test cases, so only use this when
            # requested
            if self.unitTest:
                # The mock SSH server can be accessed at 0.0.0.0.
                ip = '0.0.0.0'
            else:
                parsed_lh_url = urlparse(self.url_lhos)
                ip = parsed_lh_url.hostname.split(':').pop()
            try:
                # Now that we don't do keep-alive, the conn_timeout needs to
                # be set high enough to avoid sometimes slow response in
                # the File Persona tests.
                self.cl.setSSHOptions(
                    ip,
                    self.user,
                    self.password,
                    port=self.ssh_port,
                    conn_timeout=500,
                    known_hosts_file=self.known_hosts_file,
                    missing_key_policy=self.missing_key_policy)
            except Exception as ex:
                print(ex)
                self.fail("failed to start ssh client")

        # Setup remote copy target
        if self.run_remote_copy:
            parsed_lh_url = urlparse(self.secondary_url_lhos)
            ip = parsed_lh_url.hostname.split(':').pop()
            self.secondary_cl = client.HPELeftHandClient(
                self.secondary_url_lhos)
            try:
                self.secondary_cl.setSSHOptions(
                    ip,
                    self.secondary_user,
                    self.secondary_password,
                    port=self.ssh_port,
                    conn_timeout=500,
                    known_hosts_file=self.known_hosts_file,
                    missing_key_policy=self.missing_key_policy)
            except Exception as ex:
                print(ex)
                self.fail("failed to start ssh client")
            self.secondary_cl.login(self.secondary_user,
                                    self.secondary_password)

        if self.debug:
            self.cl.debug_rest(True)

        self.cl.login(self.user, self.password)

    def tearDown(self):
        self.cl.logout()
        if self.run_remote_copy:
            self.secondary_cl.logout()
        if self.unitTest and self.startFlask:
            #TODO: it seems to kill all the process except the last one...
            #don't know why
            self.mockServer.kill()
            if self.withSSH:
                self.mockSshServer.kill()

    def printHeader(self, name):
        print("\n##Start testing '%s'" % name)

    def printFooter(self, name):
        print("##Compeleted testing '%s\n" % name)

    def findInDict(self, dic, key, value=None):
        for i in dic:
            if key in i:
                if value:
                    if i[key] == value:
                        return True
                else:  # If value is None, only check key
                    return True

        return False
