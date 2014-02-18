# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Boris Pavlovic (boris@pavlovic.me).
# Copyright (C) 2013 PolyBeacon, Inc.
# All Rights Reserved.
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

import re

from migrate.changeset import UniqueConstraint, ForeignKeyConstraint
from sqlalchemy import Column
from sqlalchemy.engine import reflection
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import Index
from sqlalchemy import MetaData
from sqlalchemy import schema
from sqlalchemy.sql.expression import UpdateBase
from sqlalchemy import Table
from sqlalchemy.types import NullType

from ripcord.common import exception


def get_table(engine, name):
    """Returns an sqlalchemy table dynamically from db.

    Needed because the models don't work for us in migrations
    as models will be far out of sync with the current data.
    """

    metadata = MetaData()
    metadata.bind = engine

    return Table(name, metadata, autoload=True)


class InsertFromSelect(UpdateBase):
    def __init__(self, table, select):
        self.table = table
        self.select = select


@compiles(InsertFromSelect)
def visit_insert_from_select(element, compiler, **kw):
    return "INSERT INTO %s %s" % (
        compiler.process(element.table, asfrom=True),
        compiler.process(element.select))


def _get_not_supported_column(col_name_col_instance, column_name):
    try:
        column = col_name_col_instance[column_name]
    except Exception:
        msg = _("Please specify column %s in col_name_col_instance "
                "param. It is required because column has unsupported "
                "type by sqlite).")
        raise exception.NovaException(msg % column_name)

    if not isinstance(column, Column):
        msg = _("col_name_col_instance param has wrong type of "
                "column instance for column %s It should be instance "
                "of sqlalchemy.Column.")
        raise exception.NovaException(msg % column_name)
    return column


def _get_unique_constraints_in_sqlite(migrate_engine, table_name):
    regexp = "CONSTRAINT (\w+) UNIQUE \(([^\)]+)\)"

    meta = MetaData(bind=migrate_engine)
    table = Table(table_name, meta, autoload=True)

    sql_data = migrate_engine.execute(
        """
            SELECT sql
            FROM
                sqlite_master
            WHERE
                type = 'table' AND
                name = :table_name;
        """,
        table_name=table_name
    ).fetchone()[0]

    uniques = set([
        schema.UniqueConstraint(
            *[getattr(table.c, c.strip(' "'))
              for c in cols.split(",")], name=name
        )
        for name, cols in re.findall(regexp, sql_data)
    ])

    return uniques


def _drop_unique_constraint_in_sqlite(migrate_engine, table_name, uc_name,
                                      **col_name_col_instance):
    insp = reflection.Inspector.from_engine(migrate_engine)
    meta = MetaData(bind=migrate_engine)

    table = Table(table_name, meta, autoload=True)
    columns = []
    for column in table.columns:
        if isinstance(column.type, NullType):
            new_column = _get_not_supported_column(col_name_col_instance,
                                                   column.name)
            columns.append(new_column)
        else:
            columns.append(column.copy())

    uniques = _get_unique_constraints_in_sqlite(migrate_engine, table_name)
    table.constraints.update(uniques)

    constraints = [constraint for constraint in table.constraints
                   if not constraint.name == uc_name and
                   not isinstance(constraint, schema.ForeignKeyConstraint)]

    new_table = Table(table_name + "__tmp__", meta, *(columns + constraints))
    new_table.create()

    indexes = []
    for index in insp.get_indexes(table_name):
        column_names = [new_table.c[c] for c in index['column_names']]
        indexes.append(Index(index["name"],
                             *column_names,
                             unique=index["unique"]))
    f_keys = []
    for fk in insp.get_foreign_keys(table_name):
        refcolumns = [fk['referred_table'] + '.' + col
                      for col in fk['referred_columns']]
        f_keys.append(ForeignKeyConstraint(fk['constrained_columns'],
                      refcolumns, table=new_table, name=fk['name']))

    ins = InsertFromSelect(new_table, table.select())
    migrate_engine.execute(ins)
    table.drop()

    [index.create(migrate_engine) for index in indexes]
    for fkey in f_keys:
        fkey.create()
    new_table.rename(table_name)


def drop_unique_constraint(migrate_engine, table_name, uc_name, *columns,
                           **col_name_col_instance):
    """Drop unique constraint.

    This method drops UC from table and works for mysql, postgresql and sqlite.
    In mysql and postgresql we are able to use "alter table" constuction. In
    sqlite is only one way to drop UC:
        1) Create new table with same columns, indexes and constraints
           (except one that we want to drop).
        2) Copy data from old table to new.
        3) Drop old table.
        4) Rename new table to the name of old table.

    :param migrate_engine: sqlalchemy engine
    :param table_name:     name of table that contains uniq constarint.
    :param uc_name:        name of uniq constraint that will be dropped.
    :param columns:        columns that are in uniq constarint.
    :param col_name_col_instance:   contains pair column_name=column_instance.
                            column_instance is instance of Column. These params
                            are required only for columns that have unsupported
                            types by sqlite. For example BigInteger.
    """
    if migrate_engine.name == "sqlite":
        _drop_unique_constraint_in_sqlite(migrate_engine, table_name, uc_name,
                                          **col_name_col_instance)
    else:
        meta = MetaData()
        meta.bind = migrate_engine
        t = Table(table_name, meta, autoload=True)
        uc = UniqueConstraint(*columns, table=t, name=uc_name)
        uc.drop()
