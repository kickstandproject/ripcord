# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (C) 2013 PolyBeacon, Inc.
# Copyright 2014 Rackspace Hosting
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fixtures
import mock
import testtools

from ripcord.cmd import manage
from ripcord.db import migration as db_migration
from ripcord.openstack.common.db.sqlalchemy import migration
from ripcord.openstack.common import log

LOG = log.getLogger(__name__)


class TestCase(testtools.TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

        def clear_conf():
            manage.CONF.reset()
            manage.CONF.unregister_opt(manage.command_opt)

        self.addCleanup(clear_conf)

    def _main_test_helper(self, argv, func_name=None, **exp_args):
        self.useFixture(fixtures.MonkeyPatch('sys.argv', argv))
        manage.main()
        func_name.assert_called_once_with(**exp_args)

    def test_db_sync(self):
        migration.db_sync = mock.Mock()
        self._main_test_helper(
            ['ripcord.cmd.manage', 'db-sync'],
            migration.db_sync,
            abs_path=db_migration.MIGRATE_REPO_PATH, version=None)

    def test_db_sync_version(self):
        migration.db_sync = mock.Mock()
        self._main_test_helper(
            ['ripcord.cmd.manage', 'db-sync', '20'],
            migration.db_sync,
            abs_path=db_migration.MIGRATE_REPO_PATH, version='20')

    def test_db_version(self):
        migration.db_version = mock.Mock()
        self._main_test_helper(
            ['ripcord.cmd.manage', 'db-version'],
            migration.db_version,
            abs_path=db_migration.MIGRATE_REPO_PATH, init_version=0)
