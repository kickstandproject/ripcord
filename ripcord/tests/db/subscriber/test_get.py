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

import datetime

from ripcord.common import exception
from ripcord.openstack.common import uuidutils
from ripcord.tests.db import base


class TestCase(base.FunctionalTest):

    def setUp(self):
        super(TestCase, self).setUp()
        self.domain_name = 'example.org'
        self.project_id = '793491dd5fa8477eb2d6a820193a183b'
        self.user_id = '02d99a62af974b26b510c3564ba84644'

        res = self.db_api.create_domain(
            name=self.domain_name, project_id=self.project_id,
            user_id=self.user_id)
        self.domain_id = res['uuid']
        self.assertTrue(uuidutils.is_uuid_like(self.domain_id))

    def test_failure(self):
        self.assertRaises(
            exception.SubscriberNotFound,
            self.db_api.get_subscriber,
            '0eda016a-b078-4bef-94ba-1ab10fe15a7d')

    def test_success(self):
        row = {
            'description': 'a subscriber',
            'disabled': False,
            'domain_id': self.domain_id,
            'email_address': 'alice@example.org',
            'ha1': '84ed3e3a76703c1044da21c8609334a2',
            'ha1b': '2dc0ac0e03670d8474db6b1e62df8fd1',
            'id': 1,
            'password': 'foobar',
            'project_id': self.project_id,
            'rpid': 'alice@example.org',
            'updated_at': None,
            'user_id': self.user_id,
            'username': 'alice',
        }
        tmp = self.db_api.create_subscriber(
            username=row['username'], domain_id=row['domain_id'],
            password=row['password'], user_id=row['user_id'],
            project_id=row['project_id'], description=row['description'],
            disabled=row['disabled'], email=row['email_address'],
            rpid=row['rpid'])

        res = self.db_api.get_subscriber(
            uuid=tmp['uuid'])

        for k, v in row.iteritems():
            self.assertEqual(res[k], v)

        self.assertEqual(type(res['created_at']), datetime.datetime)
        self.assertTrue(uuidutils.is_uuid_like(res['uuid']))

        # NOTE(pabelanger): We add 3 because of created_at, uuid, and hidden
        # sqlalchemy object.
        self.assertEqual(len(res.__dict__), len(row) + 3)
