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
            exception.DomainNotFound,
            self.db_api.update_domain,
            uuid='0eda016a-b078-4bef-94ba-1ab10fe15a7d')

    def test_all_fields(self):
        row = {
            'disabled': True,
            'name': 'example.org',
            'id': 1,
            'project_id': '793491dd5fa8477eb2d6a820193a183b',
            'updated_at': None,
            'user_id': '02d99a62af974b26b510c3564ba84644',
        }
        tmp = self.db_api.create_domain(
            name=row['name'], disabled=row['disabled'],
            project_id=row['project_id'], user_id=row['user_id'])
        self.assertTrue(uuidutils.is_uuid_like(tmp['uuid']))

        row = {
            'disabled': False,
            'name': 'example.net',
            'id': 1,
            'project_id': '02d99a62af974b26b510c3564ba84644',
            'user_id': '793491dd5fa8477eb2d6a820193a183b',
        }
        res = self.db_api.update_domain(
            uuid=tmp['uuid'], name=row['name'], disabled=row['disabled'],
            project_id=row['project_id'], user_id=row['user_id'])

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
            'name': 'example.org',
            'id': 1,
            'project_id': '793491dd5fa8477eb2d6a820193a183b',
            'updated_at': None,
            'user_id': '02d99a62af974b26b510c3564ba84644',
        }
        tmp = self.db_api.create_domain(
            name=row['name'], disabled=row['disabled'],
            project_id=row['project_id'], user_id=row['user_id'])
        self.assertTrue(uuidutils.is_uuid_like(tmp['uuid']))

        res = self.db_api.update_domain(uuid=tmp['uuid'])

        for k, v in row.iteritems():
            self.assertEqual(res[k], v)

        self.assertEqual(type(res['created_at']), datetime.datetime)
        self.assertTrue(uuidutils.is_uuid_like(res['uuid']))

        # NOTE(pabelanger): We add 3 because of created_at, uuid, and hidden
        # sqlalchemy object.
        self.assertEqual(len(res.__dict__), len(row) + 3)
