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

from os import makedirs
from os.path import join, exists

from datetime import datetime
from cubicweb.predicates import is_instance, has_related_entities
from cubicweb.server.hook import match_rtype
from cubicweb.server.hook import Hook, DataOperationMixIn, Operation
from cubicweb.server.sources import storages


class ServerStartupHook(Hook):
    __regid__ = 'drh.serverstartup'
    events = ('server_startup', 'server_maintenance')

    def __call__(self):
        bfssdir = join(self.repo.config.appdatahome, 'bfss')
        if not exists(bfssdir):
            makedirs(bfssdir)
        storage = storages.BytesFileSystemStorage(bfssdir)
        storages.set_attribute_storage(self.repo, 'File', 'data', storage)


class CreatePersonHook(Hook):
    __regid__ = 'drh.createperson'
    __select__ = (Hook.__select__ & is_instance('EmailAddress') &
                  ~has_related_entities('use_email', 'object', 'CWUser'))
    events = ('after_add_entity', )

    def __call__(self):
        CreatePersonOp.get_instance(self._cw).add_data(self.entity.eid)


class CreatePersonOp(DataOperationMixIn, Operation):
    """Operation that creates a Person and an Application if an
    EmailAddress is not linked to a Person

    """
    def precommit_event(self):
        rql = 'Any P WHERE X is EmailAddress, X eid %(eid)s, P use_email X'
        for email_eid in self.get_data():
            # ensure email address is not the primary emai of a CWUser
            if self.cnx.execute('Any U WHERE U primary_email X, X eid %(eid)s',
                                {'eid': email_eid}):
                return
            if not self.cnx.execute(rql, {'eid': email_eid}):
                # naive surname/firstname guessing...
                email = self.cnx.entity_from_eid(email_eid)
                surname = u'xxx'
                firstname = u''
                if email.alias:
                    if ',' in email.alias:
                        # most often, if there is a comma, it's "Surname, Firstname"
                        surname, firstname = [chunk.strip().title()
                                              for chunk in email.alias.split(',', 1)]
                    else:
                        try:
                            firstname, surname = [chunk.title()
                                              for chunk in email.alias.split(' ', 1)]
                        except ValueError:
                            surname = email.alias.title()
                else:
                    try:
                        login = email.address.split('@')[0]
                        firstname, surname = [chunk.replace('.', ' ').title()
                                              for chunk in login.split('.', 1)]
                    except ValueError:
                        pass
                person = self.cnx.create_entity('Person',
                                                surname=surname,
                                                firstname=firstname,
                                                use_email=email)
                application = self.cnx.create_entity('Application',
                                                     date=datetime.utcnow(),
                                                     for_person=person)


class LinkAttachmentsToPersonHook(Hook):
    __regid__ = 'drh.linkattachments'
    __select__ = (Hook.__select__ & (match_rtype('sender', 'attachment') |
                                     match_rtype('use_email', frometypes=('Person',))))
    events = ('after_add_relation', )

    def __call__(self):
        LinkAttachmentsToPersonOp.get_instance(self._cw).add_data(
            (self.rtype, self.eidfrom, self.eidto))

class LinkAttachmentsToPersonOp(DataOperationMixIn, Operation):
    """Operation that links files embedded in emails to a Person
    """
    def precommit_event(self):
        for rtype, eidfrom, eidto in self.get_data():
            rql = ('WHERE P is Person, P use_email EA, '
                   'E sender EA, E attachment F, NOT P concerned_by F')
            if rtype == 'use_email':
                rql += ', P eid %(person)s, EA eid %(emailaddress)s'
                args = {'person': eidfrom, 'emailaddress': eidto}
            elif rtype == 'sender':
                rql += ', EA eid %(emailaddress)s, E eid %(email)s'
                args = {'email': eidfrom, 'emailaddress': eidto}
            else: # attachment
                rql += ', F eid %(file)s, E eid %(email)s'
                args = {'file': eidto, 'email': eidfrom}
            if self.cnx.execute('Any P, F ' + rql, args):
                self.cnx.execute('SET P concerned_by F ' + rql, args)
