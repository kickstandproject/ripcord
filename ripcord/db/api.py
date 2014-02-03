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

from oslo.config import cfg

from ripcord.openstack.common.db import api as db_api
from ripcord.openstack.common import log as logging

CONF = cfg.CONF

_BACKEND_MAPPING = {'sqlalchemy': 'ripcord.db.sqlalchemy.api'}

IMPL = db_api.DBAPI(backend_mapping=_BACKEND_MAPPING)
LOG = logging.getLogger(__name__)


def create_subscriber(
        username, domain, password, user, project, email='', rpid=''):
    return IMPL.create_subscriber(
        username=username, domain=domain, password=password, user=user,
        project=project, email=email, rpid=rpid)


def delete_subscriber(uuid):
    return IMPL.delete_subscriber(uuid=uuid)


def get_subscriber(uuid):
    return IMPL.get_subscriber(uuid=uuid)


def list_subscribers():
    return IMPL.list_subscribers()
