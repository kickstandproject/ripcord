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

    def test_failure(self):
        res = self.put_json(
            '/domains/%s' % '0eda016a-b078-4bef-94ba-1ab10fe15a7d',
            status=404, expect_errors=True)

        self.assertEqual(res.status_int, 404)
        self.assertTrue(res.json['error_message'])

    def test_all_fields(self):
        json = {
            'disabled': True,
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
            'X-User-Id': json['user_id'],
            'X-Tenant-Id': json['project_id'],
        }

        tmp = self.post_json(
            '/domains', params=params, status=200, headers=headers)
        self.assertTrue(uuidutils.is_uuid_like(tmp.json['uuid']))

        json = {
            'disabled': True,
            'name': 'example.org',
            'project_id': '09f07543-6dad-441b-acbf-1c61b5f4015e',
            'user_id': '5fccabbb-9d65-417f-8b0b-a2fc77b501e6',
        }
        params = {
            'disabled': json['disabled'],
            'name': json['name'],
        }
        headers = {
            'X-User-Id': json['user_id'],
            'X-Tenant-Id': json['project_id'],
        }
        res = self.put_json(
            '/domains/%s' % tmp.json['uuid'], params=params, status=200,
            headers=headers)

        for k, v in json.iteritems():
            self.assertEqual(res.json[k], v)

        self.assertTrue(res.json['created_at'])
        self.assertTrue(res.json['updated_at'])
        self.assertTrue(uuidutils.is_uuid_like(res.json['uuid']))

        # NOTE(pabelanger): We add 3 because of created_at, updated_at, and
        # uuid
        self.assertEqual(len(res.json), len(json) + 3)

    def test_no_fields(self):
        json = {
            'disabled': False,
            'name': 'example.org',
            'project_id': '5fccabbb-9d65-417f-8b0b-a2fc77b501e6',
            'updated_at': None,
            'user_id': '09f07543-6dad-441b-acbf-1c61b5f4015e',
        }
        params = {
            'name': json['name'],
        }
        headers = {
            'X-User-Id': json['user_id'],
            'X-Tenant-Id': json['project_id'],
        }

        tmp = self.post_json(
            '/domains', params=params, status=200, headers=headers)
        self.assertTrue(uuidutils.is_uuid_like(tmp.json['uuid']))

        res = self.put_json(
            '/domains/%s' % tmp.json['uuid'])

        for k, v in json.iteritems():
            self.assertEqual(res.json[k], v)

        self.assertTrue(res.json['created_at'])
        self.assertTrue(uuidutils.is_uuid_like(res.json['uuid']))

        # NOTE(pabelanger): We add 2 because of created_at and uuid
        self.assertEqual(len(res.json), len(json) + 2)
