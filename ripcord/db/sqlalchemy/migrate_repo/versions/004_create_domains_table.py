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

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import UniqueConstraint

from ripcord.openstack.common import log as logging

LOG = logging.getLogger(__name__)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    domain = Table(
        'domains', meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('created_at', DateTime),
        Column('name', String(length=64), nullable=False),
        Column('project_id', String(length=255)),
        Column('updated_at', DateTime),
        Column('user_id', String(length=255)),
        Column('uuid', String(length=255)),
        UniqueConstraint('name', name='uniq_domain0name'),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    tables = [domain]

    for table in tables:
        try:
            table.create()
        except Exception as e:
            LOG.exception(e)
            meta.drop_all(tables=tables)
            raise


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    domain = Table('domains', meta, autoload=True)

    tables = [domain]

    for table in tables:
        table.drop()
