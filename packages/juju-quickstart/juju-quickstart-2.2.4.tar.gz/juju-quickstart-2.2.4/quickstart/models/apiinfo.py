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

"""Juju Quickstart API info handling.

This module is used to collect information about already bootstrapped
environments. The Juju command line is used to retrieve data useful when
connecting to these environments.
"""

from __future__ import unicode_literals

import json
import logging
import os

from quickstart import (
    settings,
    utils,
)


class Info(object):
    """Collect methods used for retrieving environment information."""

    def __init__(self, juju_command):
        """Initialize the object with the path to the Juju command."""
        self._juju_command = juju_command

    def get(self, env_name):
        """Return info on the given bootstrapped environment.

        Return an empty dict if the environment is not found, is not
        bootstrapped or it is not possible to retrieve information, for
        instance because Juju is not installed.
        """
        retcode, output, error = utils.call(
            self._juju_command, 'api-info',
            '-e', env_name, '--password', '--format', 'json')
        if retcode:
            logging.debug(
                'unable to get API info for {}: {}'.format(env_name, error))
            return {}

        data = json.loads(output)
        return {
            'name': env_name,
            'user': data['user'],
            'password': data['password'],
            'uuid': data['environ-uuid'],
            'state-servers': data['state-servers'],
        }

    def all(self):
        """Return information about all bootstrapped environments.

        The returned dict is similar to what is returned by models.envs.load().

        The environment database returned by this method does not contain the
        usual fields used as bootstrap options. The included fields are:
        "name", "user", "password", "uuid" and "state-servers".
        """
        retcode, output, _ = utils.call(self._juju_command, 'system', 'list')
        names = _env_names_from_jenvs() if retcode else output.splitlines()
        return {'environments': dict((name, self.get(name)) for name in names)}


def _env_names_from_jenvs():
    """Return active environment names by searching for jenv files."""
    names = []
    path = os.path.expanduser(os.path.join(settings.JUJU_HOME, 'environments'))
    if not os.path.isdir(path):
        logging.debug('environments directory not found in the Juju home')
        return names
    for filename in sorted(os.listdir(path)):
        fullpath = os.path.join(path, filename)
        # Check that the current file is a jenv file.
        if not os.path.isfile(fullpath):
            continue
        name, ext = os.path.splitext(filename)
        if ext == '.jenv':
            names.append(name)
    return names


def get_env_details(env_data):
    """Return the environment details as a sequence of tuples (label, value).

    In each tuple, the label is the field name, and the value is the
    corresponding value in the given env_data.
    """
    return [
        ('name', env_data['name']),
        ('user', env_data['user']),
        ('uuid', env_data['uuid']),
        ('state servers', ', '.join(env_data['state-servers'])),
    ]
