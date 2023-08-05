# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2015 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for the Juju Quickstart jenv generated files handling."""

from __future__ import unicode_literals

from contextlib import contextmanager
import json
import os
import shutil
import tempfile
import unittest

import mock

from quickstart.models import apiinfo
from quickstart.tests import helpers


class TestInfo(
        unittest.TestCase, helpers.CallTestsMixin, helpers.JenvFileTestsMixin):

    def setUp(self):
        # Instantiate an Info object.
        self.juju_command = '/path/to/juju'
        self.info = apiinfo.Info(self.juju_command)

    @contextmanager
    def make_juju_home(self, envs=()):
        """Create a Juju home with the given optional environments.

        An empty jenv file is created for each environment name in envs.
        The "environments" subdir of the Juju home is provided in the context
        block.
        """
        home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, home)
        envs_dir = os.path.join(home, 'environments')
        os.mkdir(envs_dir)
        for env in envs:
            jenv = os.path.join(envs_dir, env + '.jenv')
            open(jenv, 'a').close()
        with mock.patch('quickstart.settings.JUJU_HOME', home):
            yield envs_dir

    def test_get(self):
        # The environment info is returned correctly.
        output = json.dumps({
            'user': 'who',
            'password': 'Secret!',
            'environ-uuid': 'env-uuid',
            'state-servers': ['localhost:17070', '10.0.3.1:17070'],
        })
        with self.patch_call(0, output, '') as mock_call:
            info = self.info.get('ec2')
        mock_call.assert_called_once_with(
            self.juju_command, 'api-info', '-e', 'ec2', '--password',
            '--format', u'json')
        expected_info = {
            'name': 'ec2',
            'user': 'who',
            'password': 'Secret!',
            'uuid': 'env-uuid',
            'state-servers': ['localhost:17070', '10.0.3.1:17070'],
        }
        self.assertEqual(expected_info, info)

    def test_get_error(self):
        # An empty dict is returned if the environment info cannot be
        # retrieved.
        expected_message = 'unable to get API info for ec2: bad wolf'
        with self.patch_call(1, '', 'bad wolf'):
            with helpers.assert_logs([expected_message], level='debug'):
                info = self.info.get('ec2')
        self.assertEqual({}, info)

    def test_all(self):
        # The active environments database is properly returned.
        output1 = '\n'.join(['local', 'ec2'])
        output2 = json.dumps({
            'user': 'local-user',
            'password': 'pswd1',
            'environ-uuid': 'local-uuid',
            'state-servers': ['localhost:17070', '10.0.3.1:17070'],
        })
        output3 = json.dumps({
            'user': 'ec2-user',
            'password': 'pswd2',
            'environ-uuid': 'ec2-uuid',
            'state-servers': ['1.2.3.4:17070'],
        })
        side_effect = [
            # First call to retrieve the list of environments.
            (0, output1, ''),
            # Second call to retrieve info on the local environment.
            (0, output2, ''),
            # Third call to retrieve info on the ec2 environment.
            (0, output3, ''),
        ]
        with self.patch_multiple_calls(side_effect) as mock_call:
            db = self.info.all()
        self.assertEqual(3, mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call(self.juju_command, 'system', 'list'),
            mock.call(self.juju_command, 'api-info', '-e', 'local',
                      '--password', '--format', u'json'),
            mock.call(self.juju_command, 'api-info', '-e', 'ec2', '--password',
                      '--format', u'json'),
        ])
        expected_db = {'environments': {
            'ec2': {
                'name': 'ec2',
                'user': 'ec2-user',
                'password': 'pswd2',
                'uuid': 'ec2-uuid',
                'state-servers': ['1.2.3.4:17070'],
            },
            'local': {
                'name': 'local',
                'user': 'local-user',
                'password': 'pswd1',
                'uuid': 'local-uuid',
                'state-servers': ['localhost:17070', '10.0.3.1:17070'],
            },
        }}
        self.assertEqual(expected_db, db)

    def test_all_empty(self):
        # An empty active environments database is returned when there are no
        # active environments.
        with self.patch_call(0, '', '') as mock_call:
            db = self.info.all()
        mock_call.assert_called_once_with(self.juju_command, 'system', 'list')
        self.assertEqual({'environments': {}}, db)

    def test_all_legacy(self):
        # Active environments are detected even when using an old version of
        # Juju not supporting controllers.
        output1 = json.dumps({
            'user': 'ec2-user',
            'password': 'pswd2',
            'environ-uuid': 'ec2-uuid',
            'state-servers': ['1.2.3.4:17070'],
        })
        output2 = json.dumps({
            'user': 'local-user',
            'password': 'pswd1',
            'environ-uuid': 'local-uuid',
            'state-servers': ['localhost:17070', '10.0.3.1:17070'],
        })
        side_effect = [
            # First call to retrieve the list of environments.
            (1, '', 'not implemented'),
            # Second call to retrieve info on the local environment.
            (0, output1, ''),
            # Third call to retrieve info on the ec2 environment.
            (0, output2, ''),
        ]
        with self.make_juju_home(envs=('local', 'ec2')):
            with self.patch_multiple_calls(side_effect) as mock_call:
                db = self.info.all()
        self.assertEqual(3, mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call(self.juju_command, 'system', 'list'),
            mock.call(self.juju_command, 'api-info', '-e', 'ec2', '--password',
                      '--format', u'json'),
            mock.call(self.juju_command, 'api-info', '-e', 'local',
                      '--password', '--format', u'json'),
        ])
        expected_db = {'environments': {
            'ec2': {
                'name': 'ec2',
                'user': 'ec2-user',
                'password': 'pswd2',
                'uuid': 'ec2-uuid',
                'state-servers': ['1.2.3.4:17070'],
            },
            'local': {
                'name': 'local',
                'user': 'local-user',
                'password': 'pswd1',
                'uuid': 'local-uuid',
                'state-servers': ['localhost:17070', '10.0.3.1:17070'],
            },
        }}
        self.assertEqual(expected_db, db)

    def test_all_legacy_empty(self):
        # An empty active environments database is returned when there are no
        # active environments and an old version of Juju is in use.
        with self.make_juju_home() as envs_dir:
            # Directories and non-jenv files are ignored.
            os.mkdir(os.path.join(envs_dir, 'dir'))
            open(os.path.join(envs_dir, 'ec2.ext'), 'a').close()
            with self.patch_call(2, '', 'not implemented'):
                db = self.info.all()
        self.assertEqual({'environments': {}}, db)

    def test_all_legacy_no_juju_home(self):
        # An empty active environments database is returned when the Juju home
        # does not exist and an old version of Juju is in use.
        with self.make_juju_home() as envs_dir:
            # Remove the environments directory.
            os.rmdir(envs_dir)
            with self.patch_call(2, '', 'not implemented'):
                db = self.info.all()
        self.assertEqual({'environments': {}}, db)


class TestGetEnvDetails(unittest.TestCase):

    def test_details(self):
        # The environment details are properly returned.
        env_data = {
            'name': 'lxc',
            'user': 'who',
            'password': 'pswd',
            'uuid': 'env-uuid',
            'state-servers': ('1.2.3.4:17060', 'localhost:17070'),
        }
        expected_details = [
            ('name', 'lxc'),
            ('user', 'who'),
            ('uuid', 'env-uuid'),
            ('state servers', '1.2.3.4:17060, localhost:17070'),
        ]
        details = apiinfo.get_env_details(env_data)
        self.assertEqual(expected_details, details)
