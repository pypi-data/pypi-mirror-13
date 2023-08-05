# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
DataSync Utilities
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm


def make_dependency_sorter(model):
    """
    Return a function suitable for use when sorting data model class names,
    according to the underlying foreign key dependencies between the tables.
    """

    def dependency_sorter(x, y):
        map_x = orm.class_mapper(getattr(model, x))
        map_y = orm.class_mapper(getattr(model, y))

        dep_x = []
        table_y = map_y.tables[0].name
        for column in map_x.columns:
            for key in column.foreign_keys:
                if key.column.table.name == table_y:
                    return 1
                dep_x.append(key)

        dep_y = []
        table_x = map_x.tables[0].name
        for column in map_y.columns:
            for key in column.foreign_keys:
                if key.column.table.name == table_x:
                    return -1
                dep_y.append(key)

        if dep_x and not dep_y:
            return 1
        if dep_y and not dep_x:
            return -1
        return 0

    return dependency_sorter
