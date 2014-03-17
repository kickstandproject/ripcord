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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import schema
from sqlalchemy import String

from ripcord.openstack.common.db.sqlalchemy import models


class RipcordBase(models.TimestampMixin, models.ModelBase):

    metadata = None


Base = declarative_base(cls=RipcordBase)


class Domain(Base):
    __tablename__ = 'domains'
    __table_args__ = (
        schema.Index('uuid', 'uuid', unique=True),
        schema.UniqueConstraint('name', name='uniq_domain0name'))

    id = Column(Integer, primary_key=True, autoincrement=True)
    disabled = Column(Boolean, default=False)
    name = Column(String(64), nullable=False, default='')
    project_id = Column(String(255))
    user_id = Column(String(255))
    uuid = Column(String(255))


class Quota(Base):
    """Represents a single quota override for a project.

    If there is no row for a given project id and resource, then the
    default for the quota class is used.  If there is no row for a
    given quota class and resource, then the default for the
    deployment is used. If the row is present but the hard limit is
    Null, then the resource is unlimited.
    """

    __tablename__ = 'quotas'
    __table_args__ = (
        schema.UniqueConstraint(
            'project_id', 'resource',
            name='uniq_quotas0project_id0resource'),)

    id = Column(Integer, primary_key=True)
    hard_limit = Column(Integer)
    project_id = Column(String(255))
    resource = Column(String(255), nullable=False)


class QuotaClass(Base):
    """Represents a single quota override for a quota class.

    If there is no row for a given quota class and resource, then the
    default for the deployment is used.  If the row is present but the
    hard limit is Null, then the resource is unlimited.
    """

    __tablename__ = 'quota_classes'

    id = Column(Integer, primary_key=True)
    class_name = Column(String(255))
    hard_limit = Column(Integer)
    resource = Column(String(255))


class Subscriber(Base):
    __tablename__ = 'subscribers'
    __table_args__ = (
        schema.UniqueConstraint(
            'username', 'domain_id',
            name='uniq_subscriber0username0domain_id'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    disabled = Column(Boolean, default=False)
    domain_id = Column(String(255), ForeignKey('domains.uuid'))
    email_address = Column(String(64), nullable=False, default='')
    ha1 = Column(String(64), nullable=False, default='')
    ha1b = Column(String(64), nullable=False, default='')
    password = Column(String(25), nullable=False, default='')
    project_id = Column(String(255))
    rpid = Column(String(64))
    user_id = Column(String(255))
    username = Column(String(64), nullable=False, default='')
    uuid = Column(String(255), unique=True)
