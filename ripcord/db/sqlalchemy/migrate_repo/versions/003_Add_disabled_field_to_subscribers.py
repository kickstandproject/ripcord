# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (C) 2013 PolyBeacon, Inc.
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

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import text
from sqlalchemy import UniqueConstraint

from ripcord.openstack.common import log as logging

LOG = logging.getLogger(__name__)

COLUMN_NAME = 'disabled'
TABLE_NAME = 'subscribers'


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table(TABLE_NAME, meta, autoload=True)
    default = text('0') if migrate_engine.name == 'sqlite' else text('false')
    preserve_ephemeral_col = Column(
        COLUMN_NAME, Boolean, server_default=default)
    t.create_column(preserve_ephemeral_col)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    # NOTE(pabelanger): We need to setup our UniqueConstraint again, otherwise
    # autoload=True doesn't seem to pick it up.
    t = Table(
        TABLE_NAME, meta,
        UniqueConstraint(
            'username', 'domain',
            name='uniq_subscriber0username0domain'),
        autoload=True)

    # NOTE(pabelanger): SQLite doesn't have native BOOLEAN type, so it's
    # emulated by adding a CHECK constraint. We must explicitly omit that
    # constraint here so we don't receive 'no such column' error when dropping
    # the column.
    if migrate_engine.name == 'sqlite':
        t.constraints = set([
            c
            for c in t.constraints
            if not (hasattr(c, 'sqltext') and COLUMN_NAME in str(c.sqltext))
        ])

    t.drop_column(COLUMN_NAME)
