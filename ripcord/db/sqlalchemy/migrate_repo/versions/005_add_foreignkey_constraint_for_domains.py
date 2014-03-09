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

from migrate.changeset.constraint import ForeignKeyConstraint
from migrate.changeset import UniqueConstraint
from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table

from ripcord.db.sqlalchemy import utils
from ripcord.openstack.common import log as logging

LOG = logging.getLogger(__name__)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    domains = Table('domains', meta, autoload=True)
    subscribers = Table('subscribers', meta, autoload=True)

    utils.drop_unique_constraint(
        migrate_engine, 'subscribers', 'uniq_subscriber0username0domain',
        'username', 'domain')

    d = Column('domain_id', String(length=255))
    subscribers.create_column(d)

    UniqueConstraint(
        'username', 'domain_id', table=subscribers,
        name='uniq_subscriber0username0domain_id').create()

    Index('uuid', domains.c.uuid, unique=True).create()

    ForeignKeyConstraint(
        columns=[subscribers.c.domain_id],
        refcolumns=[domains.c.uuid]).create()

    domains_list = list(domains.select().execute())

    # If we have a domain, upgrade the subscribers with the correct UUID.
    for domain in domains_list:
        subscribers.update().\
            where(subscribers.c.domain == domain.name).\
            where(subscribers.c.project_id == domain.project_id).\
            values(domain_id=domain.uuid).execute()

    subscribers.drop_column('domain')


def downgrade(migrate_engine):
    if migrate_engine.name == 'sqlite':
        raise NotImplementedError('Downgrade with SQLite not supported.')

    meta = MetaData()
    meta.bind = migrate_engine

    domains = Table('domains', meta, autoload=True)
    subscribers = Table('subscribers', meta, autoload=True)

    ForeignKeyConstraint(
        columns=[subscribers.c.domain_id],
        refcolumns=[domains.c.uuid]).drop()

    Index('uuid', domains.c.uuid, unique=True).drop()

    utils.drop_unique_constraint(
        migrate_engine, 'subscribers', 'uniq_subscriber0username0domain_id',
        'username', 'domain_id')

    d = Column('domain', String(length=64), nullable=True)
    d.create(subscribers)

    UniqueConstraint(
        'username', 'domain', table=subscribers,
        name='uniq_subscriber0username0domain').create()

    domains_list = list(domains.select().execute())

    # If we have a domain, upgrade the subscribers with the correct name.
    for domain in domains_list:
        subscribers.update().\
            where(subscribers.c.domain_id == domain.uuid).\
            where(subscribers.c.project_id == domain.project_id).\
            values(domain=domain.name).execute()

    subscribers.c.domain.alter(nullable=False)
    subscribers.drop_column('domain_id')
