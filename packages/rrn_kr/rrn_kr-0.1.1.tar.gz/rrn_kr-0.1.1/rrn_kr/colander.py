# -*- coding: utf-8 -*-
#
#   rrn_kr : ROK Resident Registry Number (RRN) validator
#   Copyright (C) 2016 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from __future__ import unicode_literals

from translationstring import TranslationStringFactory
import colander

from .core import authenticate_string
from .core import InvalidDigits
from .core import InvalidFormat
from .core import InvalidLength
from .core import BadAuthentication
from .core import InvalidValue


_ = TranslationStringFactory('rrn_kr')


class ValidateRRN(object):

    def __init__(self, check_authcode=True):
        self.check_authcode = check_authcode

    def __call__(self, node, cstruct):
        try:
            authenticate_string(cstruct)
        except InvalidLength:
            raise colander.Invalid(node, _('Invalid length'))
        except InvalidDigits:
            raise colander.Invalid(node, _('Invalid digits'))
        except InvalidFormat:
            raise colander.Invalid(node, _('Invalid format'))
        except BadAuthentication:
            if self.check_authcode:
                raise colander.Invalid(node, _('Invalid value'))
        except InvalidValue:
            raise colander.Invalid(node, _('Invalid value'))


validate_rrn = ValidateRRN()


class RRN(colander.MappingSchema):
    head = colander.SchemaNode(colander.String())
    tail = colander.SchemaNode(colander.String())

    def validator(self, node, cstruct):
        rrn = '-'.join([cstruct['head'], cstruct['tail']])
        validate_rrn(node, rrn)
