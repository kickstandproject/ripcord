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

from pecan import rest
from wsmeext import pecan as wsme_pecan

from ripcord.openstack.common import log as logging
from ripcord import quota

LOG = logging.getLogger(__name__)
QUOTAS = quota.QUOTAS


class QuotasController(rest.RestController):
    """REST Controller for Quota."""

    _custom_actions = {
        'defaults': ['GET'],
    }

    @wsme_pecan.wsexpose(unicode, unicode)
    def defaults(self, project_id):
        return QUOTAS.get_defaults()
