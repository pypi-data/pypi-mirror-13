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
from datetime import date

from unittest import TestCase


class CoreTest(TestCase):

    def test_construct_string(self):
        from ..core import authenticate_string
        from ..core import construct_string
        from ..core import region_codes
        birth_date = date(1980, 12, 31)
        s = construct_string(birth_date, male=False, foreigner=False,
                             region_code=region_codes['서울'][1],
                             rcn=13, serial=7)
        self.assertEquals('801231-2011379', s)
        authenticate_string(s)

    def test_authenticate_string(self):
        from ..core import authenticate_string
        s = '801231-2011379'
        actual = authenticate_string(s)
        self.assertEquals('801231-2011379', actual)

    def test_authenticate_string_invalid_digits(self):
        from ..core import authenticate_string
        from ..core import InvalidDigits
        s = '801231-a011379'
        self.assertRaises(InvalidDigits, authenticate_string, s)

    def test_authenticate_string_invalid_length(self):
        from ..core import authenticate_string
        from ..core import InvalidLength
        s = '8012312011379'
        self.assertRaises(InvalidLength, authenticate_string, s)

    def test_authenticate_string_invalid_format(self):
        from ..core import authenticate_string
        from ..core import InvalidFormat
        s = '801231=2011379'
        self.assertRaises(InvalidFormat, authenticate_string, s)

    def test_authenticate_string_bad_authentication(self):
        from ..core import authenticate_string
        from ..core import BadAuthentication
        s = '801231-2011378'
        self.assertRaises(BadAuthentication, authenticate_string, s)

    def test_RRN(self):
        from ..core import RRN
        rrn = RRN.fromstring('801231-2011379')
        self.assertEquals(date(1980, 12, 31),
                          rrn.birth_date)
        self.assertEquals(False, rrn.male)
        self.assertEquals(False, rrn.foreigner)
        self.assertEquals('서울', rrn.region_name)
        self.assertEquals(13, rrn.rcn)
        self.assertEquals(7, rrn.serial)
