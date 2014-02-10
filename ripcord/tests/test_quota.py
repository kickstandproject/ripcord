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

from oslo.config import cfg

from ripcord.common import exception
from ripcord.db import api as db_api
from ripcord import quota
from ripcord import test

CONF = cfg.CONF


class FakeDriver(object):

    def __init__(self):
        self.called = []

    def get_defaults(self, resources):
        self.called.append(('get_defaults', resources))

        return resources

    def limit_check(self, resources, values, project_id=None, user_id=None):
        self.called.append(
            ('limit_check', resources, values, project_id, user_id))


class BaseResourceTestCase(test.TestCase):
    def test_no_flag(self):
        resource = quota.BaseResource('test_resource')

        self.assertEqual(resource.name, 'test_resource')
        self.assertEqual(resource.flag, None)
        self.assertEqual(resource.default, -1)

    def test_with_flag(self):
        self.flags(group='quotas', quota_subscribers=10)
        resource = quota.BaseResource('test_resource', 'quota_subscribers')

        self.assertEqual(resource.name, 'test_resource')
        self.assertEqual(resource.flag, 'quota_subscribers')
        self.assertEqual(resource.default, 10)

    def test_with_flag_no_quota(self):
        self.flags(group='quotas', quota_subscribers=-1)
        resource = quota.BaseResource('test_resource', 'quota_subscribers')

        self.assertEqual(resource.name, 'test_resource')
        self.assertEqual(resource.flag, 'quota_subscribers')
        self.assertEqual(resource.default, -1)


class QuotaEngineTestCase(test.TestCase):
    def test_init(self):
        quota_obj = quota.QuotaEngine()

        self.assertEqual(quota_obj._resources, {})
        self.assertTrue(isinstance(quota_obj._driver, quota.DbQuotaDriver))

    def test_register_resource(self):
        quota_obj = quota.QuotaEngine()
        resource = quota.BaseResource('test_resouce')
        quota_obj.register_resource(resource)

        self.assertEqual(quota_obj._resources, dict(test_resouce=resource))

    def test_register_resources(self):
        quota_obj = quota.QuotaEngine()
        resources = [
            quota.BaseResource('test_resource1'),
            quota.BaseResource('test_resource2'),
            quota.BaseResource('test_resource3'),
        ]
        quota_obj.register_resources(resources)

        self.assertEqual(quota_obj._resources, dict(
            test_resource1=resources[0],
            test_resource2=resources[1],
            test_resource3=resources[2],
        ))

    def _make_quota_obj(self, driver):
        quota_obj = quota.QuotaEngine(quota_driver_class=driver)
        resources = [
            quota.BaseResource('test_resource4'),
            quota.BaseResource('test_resource3'),
            quota.BaseResource('test_resource2'),
            quota.BaseResource('test_resource1'),
        ]
        quota_obj.register_resources(resources)

        return quota_obj

    def test_count_no_resource(self):
        driver = FakeDriver()
        quota_obj = self._make_quota_obj(driver=driver)
        self.assertRaises(
            exception.QuotaResourceUnknown,
            quota_obj.count, 'test_resource5', True, foo='bar')

    def test_count_wrong_resource(self):
        driver = FakeDriver()
        quota_obj = self._make_quota_obj(driver=driver)
        self.assertRaises(
            exception.QuotaResourceUnknown,
            quota_obj.count, 'test_resource1', True, foo='bar')

    def test_count(self):
        def fake_count(*args, **kwargs):
            self.assertEqual(args, (True,))
            self.assertEqual(kwargs, dict(foo='bar'))
            return 5

        driver = FakeDriver()
        quota_obj = self._make_quota_obj(driver=driver)
        quota_obj.register_resource(
            quota.CountableResource('test_resource5', fake_count))
        result = quota_obj.count('test_resource5', True, foo='bar')

        self.assertEqual(result, 5)

    def test_get_defaults(self):
        driver = FakeDriver()
        quota_obj = self._make_quota_obj(driver=driver)
        result = quota_obj.get_defaults()

        self.assertEqual(
            driver.called, [('get_defaults', quota_obj._resources), ])
        self.assertEqual(result, quota_obj._resources)

    def test_limit_check(self):
        driver = FakeDriver()
        quota_obj = self._make_quota_obj(driver=driver)
        quota_obj.limit_check(
            test_resource1=4, test_resource2=3, test_resource3=2,
            test_resource4=1)

        self.assertEqual(driver.called, [
            ('limit_check', quota_obj._resources, dict(
                test_resource1=4,
                test_resource2=3,
                test_resource3=2,
                test_resource4=1,
            ), None, None),
        ])

    def test_resources(self):
        quota_obj = self._make_quota_obj(driver=None)

        self.assertEqual(quota_obj.resources, [
            'test_resource1', 'test_resource2', 'test_resource3',
            'test_resource4'])


class DbQuotaDriverTestCase(test.TestCase):
    def setUp(self):
        super(DbQuotaDriverTestCase, self).setUp()

        self.flags(
            group='quotas',
            quota_domains=100,
            quota_subscribers=255)

        self.driver = quota.DbQuotaDriver()

    def test_get_defaults(self):
        self._stub_get_default_quota_class()
        result = self.driver.get_defaults(quota.QUOTAS._resources)

        self.assertEqual(
            result, dict(domains=100, subscribers=255))

    def _stub_get_default_quota_class(self):

        def fake_gdqc():
            return dict(
                subscribers=255)

        self.stubs.Set(db_api, 'get_default_quota_class', fake_gdqc)


class NoopQuotaDriverTestCase(test.TestCase):
    def setUp(self):
        super(NoopQuotaDriverTestCase, self).setUp()

        self.expected_without_dict = {}
        for r in quota.QUOTAS._resources:
            self.expected_without_dict[r] = -1

        self.driver = quota.NoopQuotaDriver()

    def test_get_defaults(self):
        result = self.driver.get_defaults(quota.QUOTAS._resources)
        self.assertEqual(self.expected_without_dict, result)
