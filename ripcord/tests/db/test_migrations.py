# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010-2011 OpenStack Foundation
# Copyright 2012-2013 IBM Corp.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Tests for database migrations. This test case reads the configuration
file test_migrations.conf for database connection settings
to use in the tests. For each connection found in the config file,
the test case runs a series of test cases to ensure that migrations work
properly both upgrading and downgrading, and that no data loss occurs
if possible.

There are also "opportunistic" tests for mysql and postgresql in here, which
allows testing against all 3 databases (sqlite in memory, mysql and postgresql)
in a properly configured unit test environment.

For the opportunistic testing you need to set up a db named 'kickstand_citest'
with user 'kickstand_citest' and password 'kickstand_citest' on localhost.
The test will then use that db and u/p combo to run the tests.
"""

import os
import shutil
import tempfile
import urlparse

from migrate.versioning import repository
from oslo.config import cfg
import sqlalchemy
from sqlalchemy import exc

from ripcord.db import migration
from ripcord.db.sqlalchemy import migrate_repo
from ripcord.db.sqlalchemy import utils as db_utils
from ripcord.openstack.common.db.sqlalchemy import test_migrations
from ripcord.openstack.common import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class TestRipcordMigrations(test_migrations.BaseMigrationTestCase,
                            test_migrations.WalkVersionsMixin):
    """Test sqlalchemy-migrate migrations."""

    USER = "kickstand_citest"
    PASSWD = "kickstand_citest"
    DATABASE = "kickstand_citest"

    def __init__(self, *args, **kwargs):
        super(TestRipcordMigrations, self).__init__(*args, **kwargs)

        self.DEFAULT_CONFIG_FILE = os.path.join(
            os.path.dirname(__file__), 'test_migrations.conf')
        # Test machines can set the RIPCORD_TEST_MIGRATIONS_CONF variable
        # to override the location of the config file for migration testing
        self.CONFIG_FILE_PATH = os.environ.get(
            'RIPCORD_TEST_MIGRATIONS_CONF', self.DEFAULT_CONFIG_FILE)
        self.MIGRATE_FILE = migrate_repo.__file__
        self.REPOSITORY = repository.Repository(
            os.path.abspath(os.path.dirname(self.MIGRATE_FILE)))

    def setUp(self):
        lock_path = tempfile.mkdtemp()
        CONF.set_override('lock_path', lock_path)

        super(TestRipcordMigrations, self).setUp()

        def clean_lock_path():
            shutil.rmtree(lock_path, ignore_errors=True)

        self.addCleanup(clean_lock_path)
        self.snake_walk = True
        self.downgrade = True
        self.INIT_VERSION = migration.INIT_VERSION

        if self.migration_api is None:
            temp = __import__(
                'ripcord.openstack.common.db.sqlalchemy.migration',
                globals(), locals(), ['versioning_api'], -1)
            self.migration_api = temp.versioning_api

    def _test_mysql_opportunistically(self):
        # Test that table creation on mysql only builds InnoDB tables
        if not test_migrations._have_mysql(
                self.USER, self.PASSWD, self.DATABASE):
            self.skipTest("mysql not available")
        # add this to the global lists to make reset work with it, it's removed
        # automatically in tearDown so no need to clean it up here.
        connect_string = test_migrations._get_connect_string(
            "mysql", self.USER, self.PASSWD, self.DATABASE)
        (user, password, database, host) = \
            test_migrations.get_db_connection_info(urlparse.urlparse(
                connect_string))
        engine = sqlalchemy.create_engine(connect_string)
        self.engines[database] = engine
        self.test_databases[database] = connect_string

        # build a fully populated mysql database with all the tables
        self._reset_databases()
        self._walk_versions(engine, self.snake_walk)

        connection = engine.connect()
        # sanity check
        total = connection.execute("SELECT count(*) "
                                   "from information_schema.TABLES "
                                   "where TABLE_SCHEMA='%(database)s'" %
                                   {'database': database})
        self.assertTrue(total.scalar() > 0, "No tables found. Wrong schema?")

        noninnodb = connection.execute("SELECT count(*) "
                                       "from information_schema.TABLES "
                                       "where TABLE_SCHEMA='%(database)s' "
                                       "and ENGINE!='InnoDB' "
                                       "and TABLE_NAME!='migrate_version'" %
                                       {'database': database})
        count = noninnodb.scalar()
        self.assertEqual(count, 0, "%d non InnoDB tables created" % count)
        connection.close()

    def _test_postgresql_opportunistically(self):
        # Test postgresql database migration walk
        if not test_migrations._have_postgresql(
                self.USER, self.PASSWD, self.DATABASE):
            self.skipTest("postgresql not available")
        # add this to the global lists to make reset work with it, it's removed
        # automatically in tearDown so no need to clean it up here.
        connect_string = test_migrations._get_connect_string(
            "postgres", self.USER, self.PASSWD, self.DATABASE)
        engine = sqlalchemy.create_engine(connect_string)
        (user, password, database, host) = \
            test_migrations.get_db_connection_info(urlparse.urlparse(
                connect_string))
        self.engines[database] = engine
        self.test_databases[database] = connect_string

        # build a fully populated postgresql database with all the tables
        self._reset_databases()
        self._walk_versions(engine, self.snake_walk)

    def assertColumnExists(self, engine, table, column):
        t = db_utils.get_table(engine, table)
        self.assertIn(column, t.c)

    def assertColumnNotExists(self, engine, table, column):
        t = db_utils.get_table(engine, table)
        self.assertNotIn(column, t.c)

    def assertIndexExists(self, engine, table, index):
        t = db_utils.get_table(engine, table)
        index_names = [idx.name for idx in t.indexes]
        self.assertIn(index, index_names)

    def assertIndexNotExists(self, engine, table, index):
        t = db_utils.get_table(engine, table)
        index_names = [idx.name for idx in t.indexes]
        self.assertNotIn(index, index_names)

    def test_mysql_opportunistically(self):
        self._test_mysql_opportunistically()

    def test_mysql_connect_fail(self):
        """Check mysql doesn't exists.

        Test that we can trigger a mysql connection failure and we fail
        gracefully to ensure we don't break people without mysql
        """
        if test_migrations._is_backend_avail(
                'mysql', 'kickstand_cifail', self.PASSWD, self.DATABASE):
            self.fail("Shouldn't have connected")

    def test_postgresql_opportunistically(self):
        self._test_postgresql_opportunistically()

    def test_postgresql_connect_fail(self):
        """Check postgres doesn't exists.

        Test that we can trigger a postgres connection failure and we fail
        gracefully to ensure we don't break people without postgres
        """
        if test_migrations._is_backend_avail(
                'postgres', 'kickstand_cifail', self.PASSWD, self.DATABASE):
            self.fail("Shouldn't have connected")

    def test_walk_versions(self):
        for key, engine in self.engines.items():
            self._walk_versions(engine, self.snake_walk, self.downgrade)

    def _check_001(self, engine, data):
        subscriber = db_utils.get_table(engine, 'subscriber')

        cols = [
            'id', 'created_at', 'domain', 'email_address', 'ha1', 'ha1b',
            'password', 'project_id', 'rpid', 'updated_at', 'user_id',
            'username', 'uuid']

        for c in cols:
            self.assertIn(c, subscriber.c)

        insert = subscriber.insert()

        dupe_id = dict(
            id=1, email_address='alice@example.org', domain='example.org',
            ha1='foo', ha1b='bar', password='foobar', username='alice')

        insert.execute(dupe_id)
        self.assertRaises(exc.IntegrityError, insert.execute, dupe_id)

        del dupe_id['id']
        self.assertRaises(exc.IntegrityError, insert.execute, dupe_id)

    def _post_downgrade_001(self, engine):
        self.assertRaises(
            exc.NoSuchTableError, db_utils.get_table, engine, 'subscriber')

    def _pre_upgrade_003(self, engine):
        data = {
            'email_address': 'alice@example.org',
            'domain': 'example.org',
            'ha1': '84ed3e3a76703c1044da21c8609334a2',
            'ha1b': '2dc0ac0e03670d8474db6b1e62df8fd1',
            'password': 'foobar',
            'project_id': 'project1',
            'user_id': 'user1',
            'username': 'alice',
            'uuid': '5aedf7195c084e7a9ee0890cab045996',
        }
        table = db_utils.get_table(engine, 'subscribers')
        engine.execute(table.insert(), data)

        return data

    def _check_003(self, engine, data):
        self.assertColumnExists(engine, 'subscribers', 'disabled')
        table = db_utils.get_table(engine, 'subscribers')

        subscribers = table.select().where(
            table.c.disabled != True).execute().fetchall()  # flake8: noqa
        self.assertEqual(len(subscribers), 1)

    def _post_downgrade_003(self, engine):
        self.assertColumnNotExists(engine, 'subscribers', 'disabled')

    def _check_004(self, engine, data):
        table = db_utils.get_table(engine, 'domains')

        cols = [
            'id', 'created_at', 'name', 'project_id', 'updated_at', 'user_id',
            'uuid']

        for c in cols:
            self.assertIn(c, table.c)

        insert = table.insert()

        dupe_id = dict(
            id=1, name='example.org')

        insert.execute(dupe_id)
        self.assertRaises(exc.IntegrityError, insert.execute, dupe_id)

        del dupe_id['id']
        self.assertRaises(exc.IntegrityError, insert.execute, dupe_id)

    def _post_downgrade_004(self, engine):
        self.assertRaises(
            exc.NoSuchTableError, db_utils.get_table, engine, 'domains')

    def _pre_upgrade_005(self, engine):
        data = {
            'name': 'example.org',
            'project_id': 'project1',
            'user_id': 'user1',
            'uuid': 'd2901cc09db24ee5a8d2aa241c457b17',
        }
        table = db_utils.get_table(engine, 'domains')
        engine.execute(table.insert(), data)

        return data

    def _check_005(self, engine, data):
        self.assertColumnExists(engine, 'subscribers', 'domain_id')
        self.assertColumnNotExists(engine, 'subscribers', 'domain')
        self.assertIndexExists(engine, 'domains', 'uuid')

        table = db_utils.get_table(engine, 'subscribers')
        subscriber = table.select().\
            where(table.c.username == 'alice').\
            where(table.c.domain_id == 'd2901cc09db24ee5a8d2aa241c457b17').\
            execute().fetchone()
        self.assertEqual(subscriber.uuid, '5aedf7195c084e7a9ee0890cab045996')

        insert = table.insert()
        data = dict(
            email_address='alice@example.org',
            domain_id='d2901cc09db24ee5a8d2aa241c457b17',
            ha1='84ed3e3a76703c1044da21c8609334a2',
            ha1b='2dc0ac0e03670d8474db6b1e62df8fd1',
            password='foobar',
            project_id='project1',
            user_id='user1',
            username='alice')

        self.assertRaises(exc.IntegrityError, insert.execute, data)

    def _post_downgrade_005(self, engine):
        self.assertColumnExists(engine, 'subscribers', 'domain')
        self.assertColumnNotExists(engine, 'subscribers', 'domain_id')
        self.assertIndexNotExists(engine, 'domains', 'uuid')

        table = db_utils.get_table(engine, 'subscribers')
        subscriber = table.select().\
            where(table.c.username == 'alice').\
            where(table.c.domain == 'example.org').\
            execute().fetchone()
        self.assertEqual(subscriber.uuid, '5aedf7195c084e7a9ee0890cab045996')

        insert = table.insert()
        data = dict(
            email_address='alice@example.org',
            domain='example.org',
            ha1='84ed3e3a76703c1044da21c8609334a2',
            ha1b='2dc0ac0e03670d8474db6b1e62df8fd1',
            password='foobar',
            project_id='project1',
            user_id='user1',
            username='alice')

        self.assertRaises(exc.IntegrityError, insert.execute, data)

    def _check_007(self, engine, data):
        self.assertColumnExists(engine, 'domains', 'disabled')
        table = db_utils.get_table(engine, 'domains')

        domains = table.select(
            table.c.disabled != True).execute().fetchall()  #flake8: noqa
        self.assertEqual(len(domains), 1)

    def _post_downgrade_007(self, engine):
        self.assertColumnNotExists(engine, 'domains', 'disabled')

    def _check_008(self, engine, data):
        self.assertColumnExists(engine, 'subscribers', 'description')
        table = db_utils.get_table(engine, 'subscribers')

        self.assertIsInstance(
            table.c.description.type, sqlalchemy.types.String)

        subscribers = table.select().where(
            table.c.description == '').execute().fetchall()  #flake8: noqa
        self.assertEqual(len(subscribers), 1)

    def _post_downgrade_008(self, engine):
        self.assertColumnNotExists(engine, 'subscribers', 'description')
