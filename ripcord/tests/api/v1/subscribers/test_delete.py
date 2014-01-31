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

from ripcord.tests.api.v1 import base


class TestCase(base.FunctionalTest):

    def test_failure(self):
        res = self.delete(
            '/subscribers/%s' % '0eda016a-b078-4bef-94ba-1ab10fe15a7d',
            status=404, expect_errors=True)

        self.assertEqual(res.status_int, 404)
        self.assertTrue(res.json['error_message'])

    def test_success(self):
        json = {
            'domain': 'example.org',
            'email_address': 'alice@example.org',
            'password': 'foobar',
            'project_id': '5fccabbb-9d65-417f-8b0b-a2fc77b501e6',
            'rpid': 'alice@example.org',
            'user_id': '09f07543-6dad-441b-acbf-1c61b5f4015e',
            'username': 'alice',
        }

        params = {
            'domain': json['domain'],
            'email_address': json['email_address'],
            'password': json['password'],
            'rpid': json['rpid'],
            'username': json['username'],
        }
        headers = {
            'X-User-Id': '09f07543-6dad-441b-acbf-1c61b5f4015e',
            'X-Tenant-Id': '5fccabbb-9d65-417f-8b0b-a2fc77b501e6',
        }

        tmp = self.post_json(
            '/subscribers', params=params, status=200, headers=headers)

        self.assertTrue(tmp)
        self.delete(
            '/subscribers/%s' % tmp.json['uuid'], status=204)
        res = self.get_json(
            '/subscribers/%s' % tmp.json['uuid'], expect_errors=True)
        self.assertEqual(res.status_int, 404)
        self.assertTrue(res.json['error_message'])
