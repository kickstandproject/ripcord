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

    def test_get_one_failure(self):
        res = self.get_json(
            '/domains/%s' % '0eda016a-b078-4bef-94ba-1ab10fe15a7d',
            expect_errors=True)
        self.assertEqual(res.status_int, 404)
        self.assertTrue(res.json['error_message'])

    def test_get_one_success(self):
        json = {
            'disabled': False,
            'name': 'example.org',
            'project_id': '793491dd5fa8477eb2d6a820193a183b',
            'updated_at': None,
            'user_id': '02d99a62af974b26b510c3564ba84644',
        }
        params = {
            'disabled': json['disabled'],
            'name': json['name'],
        }
        headers = {
            'X-Tenant-Id': json['project_id'],
            'X-User-Id': json['user_id'],
        }
        tmp = self.post_json(
            '/domains', params=params, status=200, headers=headers)

        self.assertTrue(tmp)
        res = self.get_json('/domains/%s' % tmp.json['uuid'])

        for k, v in json.iteritems():
            self.assertEqual(res[k], v)

        self.assertTrue(res['created_at'])
        self.assertTrue(uuidutils.is_uuid_like(res['uuid']))

        # NOTE(pabelanger): We add 3 because of created_at, uuid, and hidden
        # sqlalchemy object.
        self.assertEqual(len(res), len(json) + 2)

    def test_get_all_success(self):
        json = {
            'disabled': False,
            'name': 'example.org',
            'project_id': '793491dd5fa8477eb2d6a820193a183b',
            'updated_at': None,
            'user_id': '02d99a62af974b26b510c3564ba84644',
        }
        params = {
            'disabled': json['disabled'],
            'name': json['name'],
        }
        headers = {
            'X-Tenant-Id': json['project_id'],
            'X-User-Id': json['user_id'],
        }
        tmp = self.post_json(
            '/domains', params=params, status=200, headers=headers)

        self.assertTrue(tmp)
        res = self.get_json('/domains', headers=headers)

        for k, v in json.iteritems():
            self.assertEqual(res[0][k], v)

        self.assertTrue(res[0]['created_at'])
        self.assertTrue(uuidutils.is_uuid_like(res[0]['uuid']))

        # NOTE(pabelanger): We add 3 because of created_at, uuid, and hidden
        # sqlalchemy object.
        self.assertEqual(len(res[0]), len(json) + 2)
