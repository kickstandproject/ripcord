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

import hashlib
import sys

from sqlalchemy.orm import exc

from ripcord.common import exception
from ripcord.db.sqlalchemy import models
from ripcord.openstack.common.db import exception as db_exc
from ripcord.openstack.common.db.sqlalchemy import session as db_session
from ripcord.openstack.common import log as logging
from ripcord.openstack.common import uuidutils

LOG = logging.getLogger(__name__)

get_session = db_session.get_session


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def create_subscriber(
        username, domain, password, user, project, disabled=False, email='',
        rpid=''):
    """Create a new subscriber."""
    values = {
        'disabled': disabled,
        'domain': domain,
        'email_address': email,
        'password': password,
        'project_id': project,
        'rpid': rpid,
        'user_id': user,
        'username': username,
    }

    values['ha1'] = hashlib.md5(
        '%s:%s:%s' % (
            values['username'], values['domain'],
            values['password'])).hexdigest()
    values['ha1b'] = hashlib.md5(
        '%s@%s:%s:%s' % (
            values['username'], values['domain'], values['domain'],
            values['password'])).hexdigest()
    values['uuid'] = uuidutils.generate_uuid()

    try:
        res = _create_model(model=models.Subscriber(), values=values)
    except db_exc.DBDuplicateEntry:
        raise exception.SubscriberAlreadyExists(
            username=values['username'], domain=values['domain'])

    return res


def delete_subscriber(uuid):
    """Delete a subscriber."""
    res = _delete_model(model=models.Subscriber, uuid=uuid)

    if res != 1:
        raise exception.SubscriberNotFound(uuid=uuid)


def get_subscriber(uuid):
    """Retrieve information about the given subscriber."""
    try:
        res = _get_model(model=models.Subscriber, uuid=uuid)
    except exc.NoResultFound:
        raise exception.SubscriberNotFound(uuid=uuid)

    return res


def list_subscribers():
    """Retrieve a list of subscribers."""
    res = _list_model(model=models.Subscriber)

    return res


def _create_model(model, values):
    """Create a new model."""
    model.update(values)
    model.save()

    return model


def _delete_model(model, **kwargs):
    session = get_session()
    with session.begin():
        query = model_query(
            model, session=session
        ).filter_by(**kwargs)

        count = query.delete()

        return count


def _get_model(model, **kwargs):
    """Retrieve information about the given model."""
    query = model_query(model).filter_by(**kwargs)
    res = query.one()

    return res


def _list_model(model, **kwargs):
    """Retrieve a list of the given model."""
    query = model_query(model).filter_by(**kwargs)

    return query.all()
