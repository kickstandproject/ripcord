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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer
from sqlalchemy import String

from ripcord.openstack.common.db.sqlalchemy import models


class RipcordBase(models.TimestampMixin, models.ModelBase):

    metadata = None


Base = declarative_base(cls=RipcordBase)


class Subscriber(Base):
    __tablename__ = 'subscriber'
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(64), nullable=False, default='')
    email_address = Column(String(64), nullable=False, default='')
    ha1 = Column(String(64), nullable=False, default='')
    ha1b = Column(String(64), nullable=False, default='')
    password = Column(String(25), nullable=False, default='')
    project_id = Column(String(255))
    rpid = Column(String(64))
    user_id = Column(String(255))
    username = Column(String(64), nullable=False, default='')
    uuid = Column(String(255), unique=True)
