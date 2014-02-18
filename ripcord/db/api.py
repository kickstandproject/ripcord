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


def create_domain(name, project_id, user_id):
    return IMPL.create_domain(
        name=name, project_id=project_id, user_id=user_id)


def delete_domain(uuid):
    return IMPL.delete_domain(uuid=uuid)


def create_subscriber(
        username, domain_id, password, user_id, project_id, disabled=False,
        email='', rpid=''):
    return IMPL.create_subscriber(
        username=username, domain_id=domain_id, password=password,
        user_id=user_id, project_id=project_id, disabled=disabled,
        email=email, rpid=rpid)


def delete_subscriber(uuid):
    return IMPL.delete_subscriber(uuid=uuid)


def get_domain(uuid):
    return IMPL.get_domain(uuid=uuid)


def get_subscriber(uuid):
    return IMPL.get_subscriber(uuid=uuid)


def list_domains(project_id):
    return IMPL.list_domains(project_id=project_id)


def list_subscribers(project_id):
    return IMPL.list_subscribers(project_id=project_id)


def update_domain(uuid, name=None, project_id=None, user_id=None):
    return IMPL.update_domain(
        uuid, name=name, project_id=project_id, user_id=user_id)


def update_subscriber(
        uuid, disabled=None, domain_id=None, email=None, password=None,
        project_id=None, rpid=None, user_id=None, username=None):
    return IMPL.update_subscriber(
        uuid, disabled=disabled, domain_id=domain_id, email=email,
        password=password, project_id=project_id, rpid=rpid, user_id=user_id,
        username=username)
