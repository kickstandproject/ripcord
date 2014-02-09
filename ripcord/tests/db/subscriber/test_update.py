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

    def test_failure(self):
        self.assertRaises(
            exception.SubscriberNotFound,
            self.db_api.update_subscriber,
            uuid='0eda016a-b078-4bef-94ba-1ab10fe15a7d', disabled=False)

    def test_all_fields(self):
        row = {
            'disabled': False,
            'domain': 'example.org',
            'email_address': '',
            'ha1': '84ed3e3a76703c1044da21c8609334a2',
            'ha1b': '2dc0ac0e03670d8474db6b1e62df8fd1',
            'id': 1,
            'password': 'foobar',
            'project_id': '793491dd5fa8477eb2d6a820193a183b',
            'rpid': '',
            'updated_at': None,
            'user_id': '02d99a62af974b26b510c3564ba84644',
            'username': 'alice',
        }
        tmp = self.db_api.create_subscriber(
            username=row['username'], domain=row['domain'],
            password=row['password'], user=row['user_id'],
            project=row['project_id'], disabled=row['disabled'],
            email=row['email_address'], rpid=row['rpid'])
        self.assertTrue(uuidutils.is_uuid_like(tmp['uuid']))

        row = {
            'disabled': True,
            'domain': 'example.net',
            'email_address': 'bob@example.net',
            'ha1': '9ea0e7b974be5095939ab2e6795f0159',
            'ha1b': '335bfe1e9cb562b4c76f285b69e9f9fa',
            'id': 1,
            'password': 'secret',
            'project_id': '02d99a62af974b26b510c3564ba84644',
            'rpid': 'bob@example.org',
            'user_id': '793491dd5fa8477eb2d6a820193a183b',
            'username': 'bob',
        }
        res = self.db_api.update_subscriber(
            uuid=tmp['uuid'], username=row['username'], domain=row['domain'],
            password=row['password'], user=row['user_id'],
            project=row['project_id'], disabled=row['disabled'],
            email=row['email_address'], rpid=row['rpid'])

        for k, v in row.iteritems():
            self.assertEqual(res[k], v)

        self.assertEqual(type(res['created_at']), datetime.datetime)
        self.assertEqual(type(res['updated_at']), datetime.datetime)
        self.assertTrue(uuidutils.is_uuid_like(res['uuid']))

        # NOTE(pabelanger): We add 4 because of created_at, updated_at, uuid,
        # and hidden sqlalchemy object.
        self.assertEqual(len(res.__dict__), len(row) + 4)

    def test_no_fields(self):
        row = {
            'disabled': False,
            'domain': 'example.org',
            'email_address': '',
            'ha1': '84ed3e3a76703c1044da21c8609334a2',
            'ha1b': '2dc0ac0e03670d8474db6b1e62df8fd1',
            'id': 1,
            'password': 'foobar',
            'project_id': '793491dd5fa8477eb2d6a820193a183b',
            'rpid': '',
            'updated_at': None,
            'user_id': '02d99a62af974b26b510c3564ba84644',
            'username': 'alice',
        }
        tmp = self.db_api.create_subscriber(
            username=row['username'], domain=row['domain'],
            password=row['password'], user=row['user_id'],
            project=row['project_id'], disabled=row['disabled'],
            email=row['email_address'], rpid=row['rpid'])
        self.assertTrue(uuidutils.is_uuid_like(tmp['uuid']))

        res = self.db_api.update_subscriber(uuid=tmp['uuid'])

        for k, v in row.iteritems():
            self.assertEqual(res[k], v)

        self.assertEqual(type(res['created_at']), datetime.datetime)
        self.assertTrue(uuidutils.is_uuid_like(res['uuid']))

        # NOTE(pabelanger): We add 3 because of created_at, uuid, and hidden
        # sqlalchemy object.
        self.assertEqual(len(res.__dict__), len(row) + 3)
