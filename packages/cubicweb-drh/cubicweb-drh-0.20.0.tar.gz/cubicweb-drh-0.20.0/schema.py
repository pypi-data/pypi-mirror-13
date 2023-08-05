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

from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation,
                            String, Date, Datetime)
from cubicweb.schema import WorkflowableEntityType


class School(EntityType):
    """an (high) school"""
    name        = String(required=True, fulltextindexed=True, maxsize=128)
    address     = String(maxsize=512)
    description = String(fulltextindexed=True)

    phone     = SubjectRelation('PhoneNumber', composite='subject')
    use_email = SubjectRelation('EmailAddress', composite='subject')


class Application(WorkflowableEntityType):
    date = Datetime(default='TODAY', required=True)
    for_person = SubjectRelation('Person', cardinality='1*', composite='object')


class comments(RelationDefinition):
    subject = 'Comment'
    object = 'Person', 'Task', 'Event'
    cardinality = '1*'
    composite = 'object'

class tags(RelationDefinition):
    subject = 'Tag'
    object = ('Person', 'Application')


class birthday(RelationDefinition):
    subject = 'Person'
    object = 'Date'

class concerned_by(RelationDefinition):
    subject = 'Person'
    object = 'File'

class has_studied_in(RelationDefinition):
    """used to indicate an estabishment where a person has been studying"""
    # XXX promotion?
    subject = 'Person'
    object = 'School'


class interested_in(RelationDefinition):
    subject = ('Person', 'CWUser')
    object = 'Event'


class todo_by(RelationDefinition):
    subject = 'Task'
    object = 'Person'


class topic(RelationDefinition):
    subject = 'EmailThread'
    object = 'Application'

