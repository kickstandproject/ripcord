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

    def test_success(self):
        json = {
            'domains': 1,
            'subscribers': 10,
        }

        res = self.get_json(
            '/quotas/%s/defaults' % '0eda016a-b078-4bef-94ba-1ab10fe15a7d')
        self.assertEqual(res, json)
