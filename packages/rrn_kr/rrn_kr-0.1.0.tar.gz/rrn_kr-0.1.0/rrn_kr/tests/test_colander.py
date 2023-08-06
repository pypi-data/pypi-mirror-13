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

from unittest import TestCase


class ValidatorTest(TestCase):

    def test_validator(self):
        import colander
        from ..colander import validate_rrn

        class Person(colander.MappingSchema):
            rrn = colander.SchemaNode(
                colander.String(),
                validator=validate_rrn
            )

        schema = Person()

        try:
            schema.deserialize({
                'rrn': '123456',
            })
        except colander.Invalid as e:
            self.assertEquals({
                'rrn': 'Invalid length',
            }, e.asdict())
        else:
            assert False

        try:
            schema.deserialize({
                'rrn': '1234561234567',
            })
        except colander.Invalid as e:
            self.assertEquals({
                'rrn': 'Invalid length',
            }, e.asdict())
        else:
            assert False

        try:
            schema.deserialize({
                'rrn': '801231=2011378',
            })
        except colander.Invalid as e:
            self.assertEquals({
                'rrn': 'Invalid format',
            }, e.asdict())
        else:
            assert False

        try:
            schema.deserialize({
                'rrn': '123456-a234567',
            })
        except colander.Invalid as e:
            self.assertEquals({
                'rrn': 'Invalid digits',
            }, e.asdict())
        else:
            assert False

        try:
            schema.deserialize({
                'rrn': '801231-2011378',
            })
        except colander.Invalid as e:
            self.assertEquals({
                'rrn': 'Invalid value',
            }, e.asdict())
        else:
            assert False

        self.assertEquals({
            'rrn': '801231-2011379',
        }, schema.deserialize({
            'rrn': '801231-2011379',
        }))


class RRNTest(TestCase):

    def test_deserialize(self):
        import colander
        from ..colander import RRN

        class Person(colander.MappingSchema):
            rrn = RRN()

        schema = Person()

        schema.deserialize({
            'rrn': {
                'head': '801231',
                'tail': '2011379'
            },
        })
