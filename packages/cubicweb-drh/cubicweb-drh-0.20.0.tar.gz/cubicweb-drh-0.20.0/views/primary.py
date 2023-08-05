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

from cubicweb.predicates import is_instance, rql_condition
from cubicweb.web import component

try:
    from cubicweb import _
except ImportError:
    _ = unicode

class SentMailVComponent(component.EntityCtxComponent):
    """email sent by this person"""
    __regid__ = 'sentmail'
    __select__ = (component.EntityCtxComponent.__select__
                  & is_instance('Person')
                  & rql_condition('X use_email EA, E sender EA'))
    title = _('ctxcomponents_sentmail')
    order = 40

    def render_body(self, w):
        rset = self._cw.execute('Any E ORDERBY D DESC WHERE P use_email EA, '
                                'E sender EA, E date D, P eid %(x)s',
                                {'x': self.entity.eid})
        self._cw.view('list', rset, w=w)

class ThreadTopicVComponent(component.EntityCtxComponent):
    """email in threads related to this topic"""
    __regid__ = 'threadtopic'
    __select__ = (component.EntityCtxComponent.__select__
                  & is_instance('Application')
                  & rql_condition('E in_thread T, T topic X'))
    title = _('ctxcomponents_mailtopic')
    order = 40

    def render_body(self, w):
        rset = self._cw.execute('Any E ORDERBY D DESC WHERE E date D, '
                                'E in_thread T, T topic A, A eid %(x)s',
                                {'x': self.entity.eid})
        self._cw.view('list', rset, w=w)

