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

    quota = Table(
        'quotas', meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('created_at', DateTime),
        Column('hard_limit', Integer),
        Column('project_id', String(length=255)),
        Column('resource', String(length=255), nullable=False),
        Column('updated_at', DateTime),
        UniqueConstraint(
            'project_id', 'resource',
            name='uniq_quotas0project_id0resource'),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    quota_class = Table(
        'quota_classes', meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('class_name', String(length=255)),
        Column('created_at', DateTime),
        Column('hard_limit', Integer),
        Column('resource', String(length=255)),
        Column('updated_at', DateTime),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    tables = [quota, quota_class]

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

    quota = Table('quotas', meta, autoload=True)
    quota_class = Table('quota_classes', meta, autoload=True)

    tables = [quota, quota_class]

    for table in tables:
        table.drop()
