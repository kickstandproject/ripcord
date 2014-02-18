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

    def setUp(self):
        super(TestCase, self).setUp()
        self.domain_name = 'example.org'
        self.project_id = '793491dd5fa8477eb2d6a820193a183b'
        self.user_id = '02d99a62af974b26b510c3564ba84644'

        params = {
            'name': self.domain_name,
        }

        self.headers = {
            'X-Tenant-Id': self.project_id,
            'X-User-Id': self.user_id,
        }

        res = self.post_json(
            '/domains', params=params, status=200, headers=self.headers)

        self.domain_id = res.json['uuid']
        self.assertTrue(uuidutils.is_uuid_like(self.domain_id))

        json = {
            'disabled': False,
            'domain_id': self.domain_id,
            'email_address': 'bob@example.org',
            'password': 'foobar',
            'project_id': self.project_id,
            'rpid': 'bob@example.org',
            'user_id': self.user_id,
            'username': 'bob',
        }
        params = {
            'disabled': json['disabled'],
            'domain_id': json['domain_id'],
            'email_address': json['email_address'],
            'password': json['password'],
            'rpid': json['rpid'],
            'username': json['username'],
        }

        tmp = self.post_json(
            '/subscribers', params=params, status=200, headers=self.headers)
        self.assertTrue(tmp)

    def test_get_one_failure(self):
        res = self.get_json(
            '/subscribers/%s' % '0eda016a-b078-4bef-94ba-1ab10fe15a7d',
            expect_errors=True)
        self.assertEqual(res.status_int, 404)
        self.assertTrue(res.json['error_message'])

    def test_get_one_success(self):
        json = {
            'disabled': False,
            'domain_id': self.domain_id,
            'email_address': 'alice@example.org',
            'ha1': '84ed3e3a76703c1044da21c8609334a2',
            'ha1b': '2dc0ac0e03670d8474db6b1e62df8fd1',
            'password': 'foobar',
            'project_id': self.project_id,
            'rpid': 'alice@example.org',
            'updated_at': None,
            'user_id': self.user_id,
            'username': 'alice',
        }
        params = {
            'disabled': json['disabled'],
            'domain_id': json['domain_id'],
            'email_address': json['email_address'],
            'password': json['password'],
            'rpid': json['rpid'],
            'username': json['username'],
        }

        tmp = self.post_json(
            '/subscribers', params=params, status=200, headers=self.headers)

        self.assertTrue(tmp)
        res = self.get_json('/subscribers/%s' % tmp.json['uuid'])

        for k, v in json.iteritems():
            self.assertEqual(res[k], v)

        self.assertTrue(res['created_at'])
        self.assertTrue(uuidutils.is_uuid_like(res['uuid']))

        # NOTE(pabelanger): We add 2 because of created_at and uuid.
        self.assertEqual(len(res), len(json) + 2)

    def test_get_all_success(self):
        domain_name = 'example.net'
        project_id = '5fccabbb-9d65-417f-8b0b-a2fc77b501e6'
        user_id = '09f07543-6dad-441b-acbf-1c61b5f4015e'

        params = {
            'name': domain_name,
        }
        headers = {
            'X-Tenant-Id': project_id,
            'X-User-Id': user_id,
        }

        res = self.post_json(
            '/domains', params=params, status=200, headers=headers)

        json = {
            'disabled': False,
            'domain_id': res.json['uuid'],
            'email_address': 'alice@example.net',
            'ha1': '1f66286e1db577f81e06c22c017c137b',
            'ha1b': '88bb93a6b9273446665753b5972265a8',
            'password': 'foobar',
            'project_id': project_id,
            'rpid': 'alice@example.net',
            'updated_at': None,
            'user_id': user_id,
            'username': 'alice',
        }
        params = {
            'disabled': json['disabled'],
            'domain_id': json['domain_id'],
            'email_address': json['email_address'],
            'password': json['password'],
            'rpid': json['rpid'],
            'username': json['username'],
        }

        tmp = self.post_json(
            '/subscribers', params=params, status=200, headers=headers)

        self.assertTrue(tmp)
        res = self.get_json('/subscribers', headers=headers)
        self.assertEqual(len(res), 1)

        for k, v in json.iteritems():
            self.assertEqual(res[0][k], v)

        self.assertTrue(res[0]['created_at'])
        self.assertTrue(uuidutils.is_uuid_like(res[0]['uuid']))

        # NOTE(pabelanger): We add 2 because of created_at and uuid.
        self.assertEqual(len(res[0]), len(json) + 2)
