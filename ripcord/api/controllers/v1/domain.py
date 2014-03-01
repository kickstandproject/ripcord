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

import pecan
import wsme

from pecan import rest
from wsme import types as wtypes
from wsmeext import pecan as wsme_pecan

from ripcord.api.controllers.v1 import base
from ripcord.common import exception
from ripcord.db.sqlalchemy import models
from ripcord.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class Domain(base.APIBase):
    """API representation of a domain."""

    name = wtypes.text
    project_id = wtypes.text
    user_id = wtypes.text
    uuid = wtypes.text

    def __init__(self, **kwargs):
        self.fields = vars(models.Domain)
        for k in self.fields:
            setattr(self, k, kwargs.get(k))


class DomainsController(rest.RestController):
    """REST Controller for Domain."""

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, uuid):
        """Delete a domain."""
        try:
            pecan.request.db_api.delete_domain(uuid=uuid)
        except exception.DomainNotFound as e:
            raise wsme.exc.ClientSideError(e.message, status_code=e.code)

    @wsme_pecan.wsexpose([Domain])
    def get_all(self):
        """Retrieve a list of domains."""
        project_id = pecan.request.headers.get('X-Tenant-Id')
        res = pecan.request.db_api.list_domains(project_id=project_id)

        return res

    @wsme_pecan.wsexpose(Domain, unicode)
    def get_one(self, uuid):
        """Retrieve information about the given domain."""
        try:
            result = pecan.request.db_api.get_domain(uuid=uuid)
        except exception.DomainNotFound as e:
            raise wsme.exc.ClientSideError(e.message, status_code=e.code)

        return result

    @wsme.validate(Domain)
    @wsme_pecan.wsexpose(Domain, body=Domain)
    def post(self, body):
        """Create a new domain."""
        try:
            user_id = pecan.request.headers.get('X-User-Id')
            project_id = pecan.request.headers.get('X-Tenant-Id')

            d = body.as_dict()

            res = pecan.request.db_api.create_domain(
                name=d['name'], user_id=user_id, project_id=project_id)
        except exception.DomainAlreadyExists as e:
            raise wsme.exc.ClientSideError(e.message, status_code=e.code)

        return res

    @wsme.validate(Domain)
    @wsme_pecan.wsexpose(Domain, wtypes.text, body=Domain)
    def put(self, uuid, body):
        """Update an existing domain."""
        try:
            user_id = pecan.request.headers.get('X-User-Id')
            project_id = pecan.request.headers.get('X-Tenant-Id')

            d = body.as_dict()

            res = pecan.request.db_api.update_domain(
                uuid=uuid, name=d['name'], user_id=user_id,
                project_id=project_id)
        except exception.DomainNotFound as e:
            raise wsme.exc.ClientSideError(e.message, status_code=e.code)

        return res
