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

from ripcord.common import exception
from ripcord.tests.db import base


class TestCase(base.FunctionalTest):

    def test_failure(self):
        self.assertRaises(
            exception.SubscriberNotFound,
            self.db_api.delete_subscriber,
            '0eda016a-b078-4bef-94ba-1ab10fe15a7d')

    def test_success(self):
        row = {
            'domain': 'example.org',
            'password': 'foobar',
            'project_id': '793491dd5fa8477eb2d6a820193a183b',
            'user_id': '02d99a62af974b26b510c3564ba84644',
            'username': 'alice',
        }
        res = self.db_api.create_subscriber(
            username=row['username'], domain=row['domain'],
            password=row['password'], user=row['user_id'],
            project=row['project_id'])

        self.assertTrue(res)
        self.db_api.delete_subscriber(uuid=res['uuid'])
        self.assertRaises(
            exception.SubscriberNotFound,
            self.db_api.get_subscriber, res['uuid'])
