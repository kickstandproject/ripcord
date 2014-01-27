# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Hewlett-Packard Development Company, L.P.
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

"""SQLAlchemy storage backend."""

from ripcord.openstack.common.db import api
from ripcord.openstack.common.db.sqlalchemy import session as db_session
from ripcord.openstack.common import log as logging

LOG = logging.getLogger(__name__)

get_session = db_session.get_session


def get_instance():
    """Return a DB API instance."""
    backend_mapping = {'sqlalchemy': 'ripcord.db.api'}

    return api.DBAPI(backend_mapping=backend_mapping)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


class Connection(object):
    """SqlAlchemy connection."""

    def __init__(self):
        pass
