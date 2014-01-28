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

    def test_create_subscriber(self):
        self._create_test_subscriber()

    def test_delete_subscriber(self):
        subscriber = self._create_test_subscriber()
        self.db_api.delete_subscriber(uuid=subscriber['uuid'])
        self.assertRaises(
            exception.SubscriberNotFound, self.db_api.get_subscriber,
            subscriber['uuid'])

    def test_delete_subscriber_not_found(self):
        self.assertRaises(
            exception.SubscriberNotFound, self.db_api.delete_subscriber, 123)

    def test_list_subscribers(self):
        subscriber = []
        for i in xrange(1, 6):
            q = self._create_test_subscriber(uuid=i)
            subscriber.append(q)
        res = self.db_api.list_subscribers()
        res.sort()
        subscriber.sort()
        self.assertEqual(len(res), len(subscriber))
