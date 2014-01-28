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
from ripcord.db import models
from ripcord.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class Subscriber(base.APIBase):
    """API representation of an subscriber."""

    id = int
    domain = wtypes.text
    email_address = wtypes.text
    ha1 = wtypes.text
    ha1b = wtypes.text
    password = wtypes.text
    project_id = wtypes.text
    rpid = wtypes.text
    user_id = wtypes.text
    username = wtypes.text
    uuid = wtypes.text

    def __init__(self, **kwargs):
        self.fields = vars(models.Subscriber)
        for k in self.fields:
            setattr(self, k, kwargs.get(k))


class SubscribersController(rest.RestController):
    """REST Controller for Subscriber."""

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, uuid):
        """Delete an subscriber."""
        pecan.request.db_api.delete_subscriber(uuid=uuid)

    @wsme_pecan.wsexpose([Subscriber])
    def get_all(self):
        """Retrieve a list of subscribers."""
        res = pecan.request.db_api.list_subscribers()

        return res

    @wsme_pecan.wsexpose(Subscriber, unicode)
    def get_one(self, uuid):
        """Retrieve information about the given subscriber."""
        try:
            result = pecan.request.db_api.get_subscriber(uuid)
        except exception.SubscriberNotFound:
            # TODO(pabelanger): See if there is a better way of handling
            # exceptions.
            raise wsme.exc.ClientSideError('Not found')

        return result

    @wsme.validate(Subscriber)
    @wsme_pecan.wsexpose(Subscriber, body=Subscriber)
    def post(self, body):
        """Create a new subscriber."""
        user_id = pecan.request.headers.get('X-User-Id')
        project_id = pecan.request.headers.get('X-Tenant-Id')

        try:
            d = body.as_dict()

            d['user_id'] = user_id
            d['project_id'] = project_id
            new_subscriber = pecan.request.db_api.create_subscriber(d)
        except Exception:
            # TODO(pabelanger): See if there is a better way of handling
            # exceptions.
            raise wsme.exc.ClientSideError('Invalid data')
        return new_subscriber

    @wsme.validate(Subscriber)
    @wsme_pecan.wsexpose(Subscriber, wtypes.text, body=Subscriber)
    def put(self, uuid, body):
        """Update an existing subscriber."""
        subscriber = pecan.request.db_api.get_subscriber(uuid=uuid)
        items = body.as_dict().items()
        for k, v in [(k, v) for (k, v) in items if v]:
            subscriber[k] = v

        subscriber.save()
        return subscriber
