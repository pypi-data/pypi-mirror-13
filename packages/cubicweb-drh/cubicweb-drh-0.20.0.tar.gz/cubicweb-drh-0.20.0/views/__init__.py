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

from cubicweb.web.views import uicfg

uicfg.actionbox_appearsin_addmenu.tag_subject_of(('Person', 'concerned_by', '*'), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('*', 'todo_by', 'Person'), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('Application', 'for_person', 'Person'), True)
uicfg.actionbox_appearsin_addmenu.tag_subject_of(('School', 'filed_under', 'Folder'), False)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('Application', 'for_person', 'Person'), True)
uicfg.autoform_section.tag_subject_of(('School', 'use_email', '*'), 'main', 'attributes')
uicfg.autoform_section.tag_subject_of(('School', 'phone', '*'), 'main', 'attributes')
uicfg.primaryview_section.tag_subject_of(('Person', 'concerned_by', '*'), 'hidden')
uicfg.primaryview_section.tag_object_of(('*', 'topic', 'Application'), 'hidden')
uicfg.autoform_section.tag_subject_of(('Application', 'for_person', 'Person'), 'main', 'attributes')
