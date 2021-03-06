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

_DEFAULT_QUOTA_NAME = 'default'


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


def create_domain(name, project_id, user_id, disabled=False):
    """Create a new domain."""
    values = {
        'disabled': disabled,
        'name': name,
        'project_id': project_id,
        'user_id': user_id,
    }

    values['uuid'] = uuidutils.generate_uuid()

    try:
        res = _create_model(model=models.Domain(), values=values)
    except db_exc.DBDuplicateEntry:
        raise exception.DomainAlreadyExists(name=values['name'])

    return res


def create_subscriber(
        username, domain_id, password, user_id, project_id, description='',
        disabled=False, email='', rpid=''):
    """Create a new subscriber."""

    model = get_domain(uuid=domain_id)

    values = {
        'description': description,
        'disabled': disabled,
        'domain_id': domain_id,
        'email_address': email,
        'password': password,
        'project_id': project_id,
        'rpid': rpid,
        'user_id': user_id,
        'username': username,
    }

    values['ha1'] = hashlib.md5(
        '%s:%s:%s' % (
            values['username'], model['name'],
            values['password'])).hexdigest()
    values['ha1b'] = hashlib.md5(
        '%s@%s:%s:%s' % (
            values['username'], model['name'], model['name'],
            values['password'])).hexdigest()
    values['uuid'] = uuidutils.generate_uuid()

    try:
        res = _create_model(model=models.Subscriber(), values=values)
    except db_exc.DBDuplicateEntry:
        raise exception.SubscriberAlreadyExists(
            username=values['username'], domain_id=model['name'])

    return res


def delete_domain(uuid):
    """Delete a domain."""
    res = _delete_model(model=models.Domain, uuid=uuid)

    if res != 1:
        raise exception.DomainNotFound(uuid=uuid)


def delete_subscriber(uuid):
    """Delete a subscriber."""
    res = _delete_model(model=models.Subscriber, uuid=uuid)

    if res != 1:
        raise exception.SubscriberNotFound(uuid=uuid)


def get_domain(uuid):
    """Retrieve information about the given domain."""
    try:
        res = _get_model(model=models.Domain, uuid=uuid)
    except exc.NoResultFound:
        raise exception.DomainNotFound(uuid=uuid)

    return res


def get_subscriber(uuid):
    """Retrieve information about the given subscriber."""
    try:
        res = _get_model(model=models.Subscriber, uuid=uuid)
    except exc.NoResultFound:
        raise exception.SubscriberNotFound(uuid=uuid)

    return res


def list_domains(project_id):
    """Retrieve a list of domains."""
    res = _list_model(model=models.Domain, project_id=project_id)

    return res


def list_subscribers(project_id):
    """Retrieve a list of subscribers."""
    res = _list_model(model=models.Subscriber, project_id=project_id)

    return res


def update_domain(
        uuid, name=None, disabled=None, project_id=None, user_id=None):
    """Update an existing domain."""
    res = get_domain(uuid=uuid)

    if disabled is not None:
        res['disabled'] = disabled
    if name is not None:
        res['name'] = name
    if project_id is not None:
        res['project_id'] = project_id
    if user_id is not None:
        res['user_id'] = user_id

    res.save()

    return res


def update_subscriber(
        uuid, description=None, disabled=None, domain_id=None, email=None,
        password=None, project_id=None, rpid=None, user_id=None,
        username=None):
    """Update an existing subscriber."""
    res = get_subscriber(uuid=uuid)

    if description is not None:
        res['description'] = description
    if disabled is not None:
        res['disabled'] = disabled
    if domain_id is not None:
        res['domain_id'] = domain_id
    if email is not None:
        res['email_address'] = email
    if password is not None:
        res['password'] = password
    if project_id is not None:
        res['project_id'] = project_id
    if rpid is not None:
        res['rpid'] = rpid
    if user_id is not None:
        res['user_id'] = user_id
    if username is not None:
        res['username'] = username

    model = get_domain(uuid=res['domain_id'])

    res['ha1'] = hashlib.md5(
        '%s:%s:%s' % (
            res['username'], model['name'],
            res['password'])).hexdigest()
    res['ha1b'] = hashlib.md5(
        '%s@%s:%s:%s' % (
            res['username'], model['name'], model['name'],
            res['password'])).hexdigest()

    res.save()

    return res


def get_default_quota_class():
    rows = model_query(
        models.QuotaClass).filter_by(class_name=_DEFAULT_QUOTA_NAME).all()

    result = {
        'class_name': _DEFAULT_QUOTA_NAME
    }
    for row in rows:
        result[row.resource] = row.hard_limit

    return result


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
