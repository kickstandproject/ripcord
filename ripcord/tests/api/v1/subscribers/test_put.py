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
            '/subscribers/%s' % '0eda016a-b078-4bef-94ba-1ab10fe15a7d',
            status=404, expect_errors=True)

        self.assertEqual(res.status_int, 404)
        self.assertTrue(res.json['error_message'])

    def test_all_fields(self):
        json = {
            'disabled': True,
            'domain': 'example.org',
            'email_address': '',
            'ha1': '84ed3e3a76703c1044da21c8609334a2',
            'ha1b': '2dc0ac0e03670d8474db6b1e62df8fd1',
            'password': 'foobar',
            'project_id': '5fccabbb-9d65-417f-8b0b-a2fc77b501e6',
            'rpid': '',
            'updated_at': None,
            'user_id': '09f07543-6dad-441b-acbf-1c61b5f4015e',
            'username': 'alice',
        }
        params = {
            'disabled': json['disabled'],
            'domain': json['domain'],
            'email_address': json['email_address'],
            'password': json['password'],
            'rpid': json['rpid'],
            'username': json['username'],
        }
        headers = {
            'X-User-Id': json['user_id'],
            'X-Tenant-Id': json['project_id'],
        }

        tmp = self.post_json(
            '/subscribers', params=params, status=200, headers=headers)
        self.assertTrue(uuidutils.is_uuid_like(tmp.json['uuid']))

        json = {
            'disabled': False,
            'domain': 'example.net',
            'email_address': 'bob@example.net',
            'ha1': '9ea0e7b974be5095939ab2e6795f0159',
            'ha1b': '335bfe1e9cb562b4c76f285b69e9f9fa',
            'password': 'secret',
            'project_id': '09f07543-6dad-441b-acbf-1c61b5f4015e',
            'rpid': 'bob@example.net',
            'user_id': '5fccabbb-9d65-417f-8b0b-a2fc77b501e6',
            'username': 'bob',
        }
        params = {
            'disabled': json['disabled'],
            'domain': json['domain'],
            'email_address': json['email_address'],
            'password': json['password'],
            'rpid': json['rpid'],
            'username': json['username'],
        }
        headers = {
            'X-User-Id': json['user_id'],
            'X-Tenant-Id': json['project_id'],
        }
        res = self.put_json(
            '/subscribers/%s' % tmp.json['uuid'], params=params, status=200,
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
            'domain': 'example.org',
            'email_address': '',
            'ha1': '84ed3e3a76703c1044da21c8609334a2',
            'ha1b': '2dc0ac0e03670d8474db6b1e62df8fd1',
            'password': 'foobar',
            'project_id': '5fccabbb-9d65-417f-8b0b-a2fc77b501e6',
            'rpid': '',
            'updated_at': None,
            'user_id': '09f07543-6dad-441b-acbf-1c61b5f4015e',
            'username': 'alice',
        }
        params = {
            'disabled': json['disabled'],
            'domain': json['domain'],
            'email_address': json['email_address'],
            'password': json['password'],
            'rpid': json['rpid'],
            'username': json['username'],
        }
        headers = {
            'X-User-Id': json['user_id'],
            'X-Tenant-Id': json['project_id'],
        }

        tmp = self.post_json(
            '/subscribers', params=params, status=200, headers=headers)
        self.assertTrue(uuidutils.is_uuid_like(tmp.json['uuid']))

        res = self.put_json(
            '/subscribers/%s' % tmp.json['uuid'])

        for k, v in json.iteritems():
            self.assertEqual(res.json[k], v)

        self.assertTrue(res.json['created_at'])
        self.assertTrue(uuidutils.is_uuid_like(res.json['uuid']))

        # NOTE(pabelanger): We add 3 because of created_at and uuid
        self.assertEqual(len(res.json), len(json) + 2)
