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

from ripcord.openstack.common import uuidutils
from ripcord.tests.api.v1 import base


class TestCase(base.FunctionalTest):

    def test_all_fields(self):
        json = {
            'name': 'example.org',
            'project_id': '793491dd5fa8477eb2d6a820193a183b',
            'updated_at': None,
            'user_id': '02d99a62af974b26b510c3564ba84644',
        }
        params = {
            'name': json['name'],
        }
        headers = {
            'X-Tenant-Id': json['project_id'],
            'X-User-Id': json['user_id'],
        }

        res = self.post_json(
            '/domains', params=params, status=200, headers=headers)

        for k, v in json.iteritems():
            self.assertEqual(res.json[k], v)

        self.assertTrue(res.json['created_at'])
        self.assertTrue(uuidutils.is_uuid_like(res.json['uuid']))

        # NOTE(pabelanger): We add 3 because of created_at, uuid, and hidden
        # sqlalchemy object.
        self.assertEqual(len(res.json), len(json) + 2)

    def test_domain_already_exists(self):
        json = {
            'name': 'example.org',
        }
        tmp = self.post_json(
            '/domains', params=json, status=200, headers=self.auth_headers)
        self.assertTrue(tmp)
        res = self.post_json(
            '/domains', params=json, status=409, headers=self.auth_headers,
            expect_errors=True)
        self.assertEqual(res.status_int, 409)
        self.assertTrue(res.json['error_message'])
