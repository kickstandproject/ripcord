# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Ripcord base exception handling.
"""

from oslo.config import cfg

from ripcord.openstack.common import log as logging

LOG = logging.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help='make exception message format errors fatal'),
]

CONF = cfg.CONF
CONF.register_opts(exc_log_opts)


class RipcordException(Exception):
    """Base Ripcord Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = ("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.message % kwargs

            except Exception as e:
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception('Exception in string format operation')
                for name, value in kwargs.iteritems():
                    LOG.error("%s: %s" % (name, value))

                if CONF.fatal_exception_format_errors:
                    raise e
                else:
                    # at least get the core message out if something happened
                    message = self.message

        super(RipcordException, self).__init__(message)

    def format_message(self):
        if self.__class__.__name__.endswith('_Remote'):
            return self.args[0]
        else:
            return unicode(self)


class Conflict(RipcordException):
    code = 409
    message = 'Conflict'


class DomainAlreadyExists(Conflict):
    message = 'Domain %(name) already exists'


class NotFound(RipcordException):
    message = 'Resource could not be found'
    code = 404


class DomainNotFound(NotFound):
    message = 'Domain %(uuid)s could not be found'


class SubscriberAlreadyExists(Conflict):
    message = ('A subscriber with username %(username) and domain %(domains) '
               'already exists')


class SubscriberNotFound(NotFound):
    message = 'Subscriber %(uuid)s could not be found'


class QuotaAlreadyExists(Conflict):
    message = 'Quota %(name) already exists'


class QuotaNotFound(NotFound):
    message = 'Quota could not be found'


class QuotaResourceUnknown(QuotaNotFound):
    message = 'Unknown quota resources %(unknown)s'
