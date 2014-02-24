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

There are also "opportunistic" tests for mysql in here, which allows testing
against all 2 databases (sqlite in memory, mysql) in a properly configured
unit test environment.

For the opportunistic testing you need to set up a db named 'kickstand_citest'
with user 'kickstand_citest' and password 'kickstand_citest' on localhost.
The test will then use that db and u/p combo to run the tests.
"""

import commands
import ConfigParser
import glob
import os
import urlparse

from migrate.versioning import repository
import sqlalchemy
from sqlalchemy import exc

import ripcord.db.sqlalchemy.migrate_repo
from ripcord.db.sqlalchemy import utils as db_utils
from ripcord.openstack.common import log as logging
from ripcord import test


LOG = logging.getLogger(__name__)


def _get_connect_string(backend, user, passwd, database):
    """Get connection string.

    Try to get a connection with a very specific set of values, if we get
    these then we'll run the tests, otherwise they are skipped
    """
    if backend == "mysql":
        backend = "mysql+mysqldb"
    else:
        raise Exception("Unrecognized backend: '%s'" % backend)

    return ("%s://%s:%s@localhost/%s" % (backend, user, passwd, database))


def _is_backend_avail(backend, user, passwd, database):
    try:
        connect_uri = _get_connect_string(backend, user, passwd, database)
        engine = sqlalchemy.create_engine(connect_uri)
        connection = engine.connect()
    except Exception:
        # intentionally catch all to handle exceptions even if we don't
        # have any backend code loaded.
        return False
    else:
        connection.close()
        engine.dispose()
        return True


def _have_mysql(user, passwd, database):
    present = os.environ.get('RIPCORD_TEST_MYSQL_PRESENT')
    if present is None:
        return _is_backend_avail('mysql', user, passwd, database)
    return present.lower() in ('', 'true')


def get_mysql_connection_info(conn_pieces):
    database = conn_pieces.path.strip('/')
    loc_pieces = conn_pieces.netloc.split('@')
    host = loc_pieces[1]
    auth_pieces = loc_pieces[0].split(':')
    user = auth_pieces[0]
    password = ""
    if len(auth_pieces) > 1:
        if auth_pieces[1].strip():
            password = "-p\"%s\"" % auth_pieces[1]

    return (user, password, database, host)


class CommonTestsMixIn(object):
    """These tests are shared between TestRipcordMigrations and
    TestBaremetalMigrations.

    BaseMigrationTestCase is effectively an abstract class, meant to be derived
    from and not directly tested against; that's why these `test_` methods need
    to be on a Mixin, so that they won't be picked up as valid tests for
    BaseMigrationTestCase.
    """
    def test_walk_versions(self):
        for key, engine in self.engines.items():
            self._walk_versions(engine, self.snake_walk)

    def test_mysql_opportunistically(self):
        self._test_mysql_opportunistically()

    def test_mysql_connect_fail(self):
        """Check mysql doesn't exists.

        Test that we can trigger a mysql connection failure and we fail
        gracefully to ensure we don't break people without mysql
        """
        if _is_backend_avail('mysql', "kickstand_cifail", self.PASSWD,
                             self.DATABASE):
            self.fail("Shouldn't have connected")


class BaseMigrationTestCase(test.NoDBTestCase):
    """Base class fort testing migrations and migration utils."""
    USER = None
    PASSWD = None
    DATABASE = None

    def __init__(self, *args, **kwargs):
        super(BaseMigrationTestCase, self).__init__(*args, **kwargs)

        self.DEFAULT_CONFIG_FILE = os.path.join(
            os.path.dirname(__file__), 'test_migrations.conf')
        # Test machines can set the RIPCORD_TEST_MIGRATIONS_CONF variable
        # to override the location of the config file for migration testing
        self.CONFIG_FILE_PATH = os.environ.get(
            'RIPCORD_TEST_MIGRATIONS_CONF', self.DEFAULT_CONFIG_FILE)
        self.MIGRATE_FILE = ripcord.db.sqlalchemy.migrate_repo.__file__
        self.REPOSITORY = repository.Repository(
            os.path.abspath(os.path.dirname(self.MIGRATE_FILE)))
        self.INIT_VERSION = 0

        self.snake_walk = False
        self.test_databases = {}
        self.migration = None
        self.migration_api = None

    def setUp(self):
        super(BaseMigrationTestCase, self).setUp()

        # Load test databases from the config file. Only do this
        # once. No need to re-run this on each test...
        LOG.debug('config_path is %s' % self.CONFIG_FILE_PATH)
        if os.path.exists(self.CONFIG_FILE_PATH):
            cp = ConfigParser.RawConfigParser()
            try:
                cp.read(self.CONFIG_FILE_PATH)
                defaults = cp.defaults()
                for key, value in defaults.items():
                    self.test_databases[key] = value
                self.snake_walk = cp.getboolean('walk_style', 'snake_walk')
            except ConfigParser.ParsingError as e:
                self.fail("Failed to read test_migrations.conf config "
                          "file. Got error: %s" % e)
        else:
            self.fail("Failed to find test_migrations.conf config "
                      "file.")

        self.engines = {}
        for key, value in self.test_databases.items():
            self.engines[key] = sqlalchemy.create_engine(value)

        # We start each test case with a completely blank slate.
        self._reset_databases()

    def tearDown(self):
        # We destroy the test data store between each test case,
        # and recreate it, which ensures that we have no side-effects
        # from the tests
        self._reset_databases()
        super(BaseMigrationTestCase, self).tearDown()

    def execute_cmd(self, cmd=None):
        status, output = commands.getstatusoutput(cmd)
        LOG.debug(output)
        self.assertEqual(0, status,
                         "Failed to run: %s\n%s" % (cmd, output))

    def _reset_databases(self):
        for key, engine in self.engines.items():
            conn_string = self.test_databases[key]
            conn_pieces = urlparse.urlparse(conn_string)
            engine.dispose()
            if conn_string.startswith('sqlite'):
                # We can just delete the SQLite database, which is
                # the easiest and cleanest solution
                db_path = conn_pieces.path.strip('/')
                if os.path.exists(db_path):
                    os.unlink(db_path)
                # No need to recreate the SQLite DB. SQLite will
                # create it for us if it's not there...
            elif conn_string.startswith('mysql'):
                # We can execute the MySQL client to destroy and re-create
                # the MYSQL database, which is easier and less error-prone
                # than using SQLAlchemy to do this via MetaData...trust me.
                (user, password, database, host) = \
                    get_mysql_connection_info(conn_pieces)
                sql = ("drop database if exists %(database)s; "
                       "create database %(database)s;"
                       % {'database': database})
                cmd = ("mysql -u \"%(user)s\" %(password)s -h %(host)s "
                       "-e \"%(sql)s\"" % {'user': user,
                       'password': password, 'host': host, 'sql': sql})
                self.execute_cmd(cmd)

    def _test_mysql_opportunistically(self):
        # Test that table creation on mysql only builds InnoDB tables
        if not _have_mysql(self.USER, self.PASSWD, self.DATABASE):
            self.skipTest("mysql not available")
        # add this to the global lists to make reset work with it, it's removed
        # automatically in tearDown so no need to clean it up here.
        connect_string = _get_connect_string(
            "mysql", self.USER, self.PASSWD, self.DATABASE)
        (user, password, database, host) = \
            get_mysql_connection_info(urlparse.urlparse(connect_string))
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

    def _walk_versions(self, engine=None, snake_walk=False, downgrade=True):
        # Determine latest version script from the repo, then
        # upgrade from 1 through to the latest, with no data
        # in the databases. This just checks that the schema itself
        # upgrades successfully.

        # Place the database under version control
        self.migration_api.version_control(
            engine, self.REPOSITORY, self.INIT_VERSION)
        self.assertEqual(
            self.INIT_VERSION, self.migration_api.db_version(
                engine, self.REPOSITORY))

        LOG.debug('latest version is %s' % self.REPOSITORY.latest)
        versions = range(self.INIT_VERSION + 1, self.REPOSITORY.latest + 1)

        for version in versions:
            # upgrade -> downgrade -> upgrade
            self._migrate_up(engine, version, with_data=True)
            if snake_walk:
                downgraded = self._migrate_down(
                    engine, version - 1, with_data=True)
                if downgraded:
                    self._migrate_up(engine, version, with_data=True)

        if downgrade:
            # Now walk it back down to 0 from the latest, testing
            # the downgrade paths.
            for version in reversed(versions):
                # downgrade -> upgrade -> downgrade
                downgraded = self._migrate_down(
                    engine, version - 1, with_data=True)

                if snake_walk and downgraded:
                    self._migrate_up(engine, version, with_data=True)
                    self._migrate_down(engine, version - 1, with_data=True)

    def _migrate_down(self, engine, version, with_data=False):
        try:
            self.migration_api.downgrade(engine, self.REPOSITORY, version)
        except NotImplementedError:
            # NOTE(sirp): some migrations, namely release-level
            # migrations, don't support a downgrade.
            return False

        self.assertEqual(version,
                         self.migration_api.db_version(
                             engine, self.REPOSITORY))

        # NOTE(sirp): `version` is what we're downgrading to (i.e. the 'target'
        # version). So if we have any downgrade checks, they need to be run for
        # the previous (higher numbered) migration.
        if with_data:
            post_downgrade = getattr(
                self, "_post_downgrade_%03d" % (version + 1), None)
            if post_downgrade:
                post_downgrade(engine)

        return True

    def _migrate_up(self, engine, version, with_data=False):
        """migrate up to a new version of the db.

        We allow for data insertion and post checks at every
        migration version with special _pre_upgrade_### and
        _check_### functions in the main test.
        """
        # NOTE(sdague): try block is here because it's impossible to debug
        # where a failed data migration happens otherwise
        try:
            if with_data:
                data = None
                pre_upgrade = getattr(
                    self, "_pre_upgrade_%03d" % version, None)
                if pre_upgrade:
                    data = pre_upgrade(engine)

            self.migration_api.upgrade(engine, self.REPOSITORY, version)
            self.assertEqual(version,
                             self.migration_api.db_version(engine,
                                                           self.REPOSITORY))
            if with_data:
                check = getattr(self, "_check_%03d" % version, None)
                if check:
                    check(engine, data)
        except Exception:
            LOG.error("Failed to migrate to version %s on engine %s" %
                      (version, engine))
            raise


class TestRipcordMigrations(BaseMigrationTestCase, CommonTestsMixIn):
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
        self.MIGRATE_FILE = ripcord.db.sqlalchemy.migrate_repo.__file__
        self.REPOSITORY = repository.Repository(
            os.path.abspath(os.path.dirname(self.MIGRATE_FILE)))

    def setUp(self):
        super(TestRipcordMigrations, self).setUp()

        if self.migration is None:
            self.migration = __import__(
                'ripcord.db.migration',
                globals(), locals(), ['INIT_VERSION'], -1)
            self.INIT_VERSION = self.migration.INIT_VERSION
        if self.migration_api is None:
            temp = __import__(
                'ripcord.openstack.common.db.sqlalchemy.migration',
                globals(), locals(), ['versioning_api'], -1)
            self.migration_api = temp.versioning_api

    def assertColumnExists(self, engine, table, column):
        t = db_utils.get_table(engine, table)
        self.assertIn(column, t.c)

    def assertColumnNotExists(self, engine, table, column):
        t = db_utils.get_table(engine, table)
        self.assertNotIn(column, t.c)

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

    def _check_003(self, engine, data):
        self.assertColumnExists(engine, 'subscribers', 'disabled')
        table = db_utils.get_table(engine, 'subscribers')

        subscribers = table.select(
            table.c.disabled == 0).execute().fetchall()
        self.assertEqual(len(subscribers), 1)

    def _post_downgrade_003(self, engine):
        self.assertColumnNotExists(engine, 'subscribers', 'disabled')


class ProjectTestCase(test.NoDBTestCase):

    def test_all_migrations_have_downgrade(self):
        topdir = os.path.normpath(os.path.dirname(__file__) + '/../../../')
        py_glob = os.path.join(topdir, "ripcord", "db", "sqlalchemy",
                               "migrate_repo", "versions", "*.py")

        missing_downgrade = []
        for path in glob.iglob(py_glob):
            has_upgrade = False
            has_downgrade = False
            with open(path, "r") as f:
                for line in f:
                    if 'def upgrade(' in line:
                        has_upgrade = True
                    if 'def downgrade(' in line:
                        has_downgrade = True

                if has_upgrade and not has_downgrade:
                    fname = os.path.basename(path)
                    missing_downgrade.append(fname)

        helpful_msg = ("The following migrations are missing a downgrade:"
                       "\n\t%s") % '\n\t'.join(sorted(missing_downgrade))
        self.assertTrue(not missing_downgrade, helpful_msg)
