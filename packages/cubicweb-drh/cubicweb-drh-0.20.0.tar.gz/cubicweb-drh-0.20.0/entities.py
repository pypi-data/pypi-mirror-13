# -*- coding: utf-8 -*-
#
# copyright 2011-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from cubicweb.predicates import is_instance
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.adapters import ITreeAdapter

class School(AnyEntity):
    __regid__ = 'School'
    fetch_attrs, cw_fetch_order = fetch_config(['name'])


class EmailThreadITreeAdapter(ITreeAdapter):
    __select__ = is_instance('EmailThread')
    tree_relation = 'topic'
    parent_role = 'object'
    child_role = 'subject'

    def different_type_children(self, entities=True):
        if entities: return []
        return self._cw.empty_rset()

    def same_type_children(self, entities=True):
        if entities: return []
        return self._cw.empty_rset()

    def children(self, entities=True, sametype=False):
        if sametype:
            return self.same_type_children(entities)
        else:
            return self._cw.empty_rset()

class ApplicationITreeAdapter(ITreeAdapter):
    __select__ = is_instance('Application')
    tree_relation = 'for_person'
    parent_role = 'object'
    child_role = 'subject'

    def children_rql(self):
        """Returns RQL to get the children of the entity."""
        return self.entity.cw_related_rql('topic', 'object')

    def different_type_children(self, entities=True):
        res = self.entity.related('topic', 'object', entities=entities)
        eschema = self.entity.e_schema
        if entities:
            return [e for e in res if e.e_schema != eschema]
        return res.filtered_rset(lambda x: x.e_schema != eschema, self.entity.cw_col)

    def same_type_children(self, entities=True):
        res = self.entity.related('topic', 'object', entities=entities)
        eschema = self.entity.e_schema
        if entities:
            return [e for e in res if e.e_schema == eschema]
        return res.filtered_rset(lambda x: x.e_schema is eschema, self.entity.cw_col)

    def children(self, entities=True, sametype=False):
        if sametype:
            return self.same_type_children(entities)
        else:
            return self.entity.related('topic', 'object', entities=entities)

