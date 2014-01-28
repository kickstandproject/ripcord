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

"""Initialize tables

Revision ID: 176d8f8e7e68
Revises: None
Create Date: 2014-01-28 16:30:05.811938

"""

from alembic import op
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

revision = '176d8f8e7e68'
down_revision = None

subscriber = (
    'subscriber',
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('created_at', DateTime),
    Column('domain', String(length=64), nullable=False, default=''),
    Column('email_address', String(length=64), nullable=False, default=''),
    Column('ha1', String(length=64), nullable=False, default=''),
    Column('ha1b', String(length=64), nullable=False, default=''),
    Column('password', String(length=25), nullable=False, default=''),
    Column('project_id', String(length=255)),
    Column('rpid', String(length=64)),
    Column('updated_at', DateTime),
    Column('user_id', String(length=255)),
    Column('username', String(length=64), nullable=False, default=''),
    Column('uuid', String(length=255)),
)

tables = [subscriber]


def upgrade():
    for table in sorted(tables):
        op.create_table(*table)


def downgrade():
    for table in sorted(tables):
        op.drop_table(table[0])
