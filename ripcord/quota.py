# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
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

"""Quotas for ripcord."""

from oslo.config import cfg

from ripcord.common import exception
from ripcord.db import api as db_api
from ripcord.openstack.common import importutils
from ripcord.openstack.common import log as logging

LOG = logging.getLogger(__name__)

quota_opts = [
    cfg.IntOpt(
        'quota_domains', default=1,
        help='Number of domains allowed per project'),
    cfg.IntOpt(
        'quota_subscribers', default=10,
        help='Number of subscribers allowed per project'),
    cfg.StrOpt(
        'quota_driver', default='ripcord.quota.DbQuotaDriver',
        help='Default driver to use for quota checks'),
]

CONF = cfg.CONF
CONF.register_opts(quota_opts, 'quotas')


class DbQuotaDriver(object):
    """Database quota driver.

    Driver to perform necessary checks to enforce quotas and obtain quota
    information.  The default driver utilizes the local database.
    """

    def get_defaults(self, resources):
        """Given a list of resources, retrieve the default quotas.
        Use the class quotas named `_DEFAULT_QUOTA_NAME` as default quotas,
        if it exists.

        :param resources: A dictionary of the registered resources.
        """

        quotas = {}
        default_quotas = db_api.get_default_quota_class()
        for resource in resources.values():
            quotas[resource.name] = default_quotas.get(
                resource.name, resource.default)

        return quotas


class NoopQuotaDriver(object):
    """Noop quota driver.

    Driver that turns quotas calls into no-ops and pretends that quotas for
    all resources are unlimited. This can be used if you do not wish to wish
    to have any quota checking.
    """

    def get_defaults(self, resources):
        """Given a list of resources, retrieve the default quotas.

        :param context: The request context, for access checks.
        :param resources: A dictionary of the registered resources.
        """
        quotas = {}
        for resource in resources.values():
            quotas[resource.name] = -1
        return quotas


class BaseResource(object):
    """Describe a single resource for quota checking."""

    def __init__(self, name, flag=None):
        """Initializes a Resource.

        :param name: The name of the resource, i.e., "instances".
        :param flag: The name of the flag or configuration option
                     which specifies the default value of the quota
                     for this resource.
        """

        self.name = name
        self.flag = flag

    @property
    def default(self):
        """Return the default value of the quota."""
        return CONF.quotas[self.flag] if self.flag else -1


class CountableResource(BaseResource):
    """Describe a resource where the counts are determined by a function."""

    def __init__(self, name, count, flag=None):
        """Initializes a CountableResource.

        Countable resources are those resources which directly
        correspond to objects in the database, i.e., netowk, subnet,
        etc.,.  A CountableResource must be constructed with a counting
        function, which will be called to determine the current counts
        of the resource.

        The counting function will be passed the context, along with
        the extra positional and keyword arguments that are passed to
        Quota.count().  It should return an integer specifying the
        count.

        :param name: The name of the resource, i.e., "instances".
        :param count: A callable which returns the count of the
                      resource.  The arguments passed are as described
                      above.
        :param flag: The name of the flag or configuration option
                     which specifies the default value of the quota
                     for this resource.
        """

        super(CountableResource, self).__init__(name, flag=flag)
        self.count = count


class QuotaEngine(object):
    """Represent the set of recognized quotas."""

    def __init__(self, quota_driver_class=None):
        """Initialize a Quota object."""

        self._resources = {}
        self._driver_cls = quota_driver_class
        self.__driver = None

    @property
    def _driver(self):
        if self.__driver:
            return self.__driver
        if not self._driver_cls:
            self._driver_cls = CONF.quotas.quota_driver
        if isinstance(self._driver_cls, basestring):
            self._driver_cls = importutils.import_object(self._driver_cls)
        self.__driver = self._driver_cls

        return self.__driver

    def count(self, resource, *args, **kwargs):
        """Count a resource.

        For countable resources, invokes the count() function and
        returns its result.  Arguments following the context and
        resource are passed directly to the count function declared by
        the resource.

        :param resource: The name of the resource, as a string.
        """

        res = self._resources.get(resource)
        if not res or not hasattr(res, 'count'):
            raise exception.QuotaResourceUnknown(unknown=[resource])

        return res.count(*args, **kwargs)

    def get_defaults(self):
        """Retrieve the default quotas."""

        return self._driver.get_defaults(self._resources)

    def limit_check(self, project_id=None, user_id=None, **values):
        """Check simple quota limits.

        For limits--those quotas for which there is no usage
        synchronization function--this method checks that a set of
        proposed values are permitted by the limit restriction.  The
        values to check are given as keyword arguments, where the key
        identifies the specific quota limit to check, and the value is
        the proposed value.

        This method will raise a QuotaResourceUnknown exception if a
        given resource is unknown or if it is not a simple limit
        resource.

        If any of the proposed values is over the defined quota, an
        OverQuota exception will be raised with the sorted list of the
        resources which are too high.  Otherwise, the method returns
        nothing.

        :param project_id: Specify the project_id if current context
                           is admin and admin wants to impact on
                           common user's tenant.
        :param user_id: Specify the user_id if current context
                        is admin and admin wants to impact on
                        common user.
        """

        return self._driver.limit_check(
            self._resources, values, project_id=project_id, user_id=user_id)

    def register_resource(self, resource):
        """Register a resource."""

        self._resources[resource.name] = resource

    def register_resources(self, resources):
        """Register a list of resources."""

        for resource in resources:
            self.register_resource(resource)

    @property
    def resources(self):
        return sorted(self._resources.keys())


QUOTAS = QuotaEngine()


resources = [
    CountableResource(
        'domains', 'foo', 'quota_domains'),
    CountableResource(
        'subscribers', 'foo', 'quota_subscribers'),
]


QUOTAS.register_resources(resources)
