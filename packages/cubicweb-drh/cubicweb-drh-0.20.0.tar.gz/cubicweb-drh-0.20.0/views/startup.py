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

from logilab.mtconverter import xml_escape

from cubicweb.web.views import startup

try:
    from cubicweb import _
except ImportError:
    _ = unicode

class IndexView(startup.IndexView):
    title = _('Index')

    def call(self):
        _ = self._cw._
        user = self._cw.user
        self.w(u'<h1>%s</h1>' % self._cw.property_value('ui.site-title'))
        # email addresses not linked
        rql = 'Any X WHERE NOT P use_email X'
        title = u'email addresses not linked to a person'
        rset = self._cw.execute(rql)
        if rset:
            self.w(u'<p><a href="%s">%s %s</a></p>'
                   % (xml_escape(self._cw.build_url(rql=rql, vtitle=title)),
                      len(rset), title))
        # email threads not linked to an application
        rql = 'Any T WHERE T is EmailThread, NOT T topic X'
        title = u'message threads without topic'
        rset = self._cw.execute(rql)
        if rset:
            self.w(u'<p><a href="%s">%s %s</a></p>'
                   % (xml_escape(self._cw.build_url(rql=rql, vtitle=title)),
                      len(rset), title))
        # candidatures en attente
        rset = self._cw.execute('Any A,P,group_concat(TN),E,B '
                                'GROUPBY A,P,E,B,CD ORDERBY CD '
                                'WHERE A is Application, A in_state X, '
                                'X name "received", '
                                'A for_person P, P has_studied_in E?, '
                                'P birthday B, T? tags A, T name TN, '
                                'A creation_date CD')
        if rset:
            self.w(u'<h2>%s</h2>' % _('Juger candidatures'))
            self.wview('table',rset,'null')
        else:
            self.w(u'<p>%s</p>' % _('aucune candidature en attente'))




def registration_callback(vreg):
    vreg.register_and_replace(IndexView, startup.IndexView)
