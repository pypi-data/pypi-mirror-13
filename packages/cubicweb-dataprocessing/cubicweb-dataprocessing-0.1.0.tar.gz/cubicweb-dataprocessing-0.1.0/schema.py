# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-dataprocessing schema"""

from yams.buildobjs import EntityType, RelationDefinition, String

from cubicweb.schema import (RRQLExpression, ERQLExpression,
                             WorkflowableEntityType)

from cubes.file.schema import File


_ = unicode


SCRIPT_UPDATE_PERMS_RQLEXPR = (
    'NOT EXISTS(P1 process_script X) OR '
    'EXISTS(P2 process_script X, P2 in_state S,'
    '       S name "wfs_dataprocess_initialized")')


class Script(EntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'update': ('managers', ERQLExpression(SCRIPT_UPDATE_PERMS_RQLEXPR)),
        'delete': ('managers', ERQLExpression(SCRIPT_UPDATE_PERMS_RQLEXPR)),
        'add': ('managers', 'users')
    }
    name = String(required=True, fulltextindexed=True)
    accepted_format = String(
        maxsize=128,
        description=_('the MIME type of input files that this script accepts '
                      '(if unspecified, the script is assumed to handle any '
                      'kind of format)'),
    )


class implemented_by(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (RRQLExpression('U has_update_permission S'), ),
        'delete': (RRQLExpression('U has_update_permission S'), ),
    }
    subject = 'Script'
    object = 'File'
    cardinality = '1?'
    inlined = True
    composite = 'subject'
    description = _('the resource (file) implementing a script')


DATAPROCESS_UPDATE_PERMS_RQLEXPR = (
    'X in_state S, S name "wfs_dataprocess_initialized"')


class _DataProcess(WorkflowableEntityType):
    __abstract__ = True
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'update': (),
        'delete': ('managers',
                   ERQLExpression(DATAPROCESS_UPDATE_PERMS_RQLEXPR)),
        'add': ()
    }


class DataTransformationProcess(_DataProcess):
    """Data transformation process"""


class DataValidationProcess(_DataProcess):
    """Data validation process"""


class process_depends_on(RelationDefinition):
    subject = 'DataTransformationProcess'
    object = 'DataValidationProcess'
    cardinality = '??'


class process_input_file(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression(
            'S in_state ST, ST name "wfs_dataprocess_initialized"')),
        'delete': ('managers', RRQLExpression('U has_update_permission S'))}
    subject = ('DataTransformationProcess', 'DataValidationProcess')
    object = 'File'
    cardinality = '?*'
    description = _('input file of the data process')


class validated_by(RelationDefinition):
    """A File may be validated by a validation process"""
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': (),
                       'delete': ()}
    subject = 'File'
    object = 'DataValidationProcess'
    cardinality = '**'


class produced_by(RelationDefinition):
    """A File may be produced by a transformation process"""
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': (),
                       'delete': ()}
    subject = 'File'
    object = 'DataTransformationProcess'
    cardinality = '?*'


# Set File permissions:
#  * use `produced_by` relation to prevent modification of generated files
#  * bind the update permissions on the Script which uses the File as
#    implementation if any
_update_file_perms = ('managers', ERQLExpression(
    'NOT EXISTS(X produced_by Y), '
    'NOT EXISTS(S1 implemented_by X)'
    ' OR EXISTS(S implemented_by X, U has_update_permission S)'
))
File.__permissions__ = File.__permissions__.copy()
File.__permissions__.update({'update': _update_file_perms,
                             'delete': _update_file_perms})


class process_script(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users'),
        'delete': (RRQLExpression('U has_update_permission S'), )
    }
    subject = ('DataTransformationProcess', 'DataValidationProcess')
    object = 'Script'
    cardinality = '1*'
    inlined = True
