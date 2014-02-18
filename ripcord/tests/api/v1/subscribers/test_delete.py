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

    def test_failure(self):
        res = self.delete(
            '/subscribers/%s' % '0eda016a-b078-4bef-94ba-1ab10fe15a7d',
            status=404, expect_errors=True)

        self.assertEqual(res.status_int, 404)
        self.assertTrue(res.json['error_message'])

    def test_success(self):
        json = {
            'domain_id': self.domain_id,
            'email_address': 'alice@example.org',
            'password': 'foobar',
            'project_id': self.project_id,
            'rpid': 'alice@example.org',
            'user_id': self.user_id,
            'username': 'alice',
        }

        params = {
            'domain_id': json['domain_id'],
            'email_address': json['email_address'],
            'password': json['password'],
            'rpid': json['rpid'],
            'username': json['username'],
        }

        tmp = self.post_json(
            '/subscribers', params=params, status=200, headers=self.headers)

        self.assertTrue(tmp)
        self.delete(
            '/subscribers/%s' % tmp.json['uuid'], status=204)
        res = self.get_json(
            '/subscribers/%s' % tmp.json['uuid'], expect_errors=True)
        self.assertEqual(res.status_int, 404)
        self.assertTrue(res.json['error_message'])
