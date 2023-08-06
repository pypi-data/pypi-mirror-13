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
from collections import namedtuple
from datetime import date


class InvalidValue(ValueError):
    pass


class InvalidFormat(InvalidValue):
    pass


class InvalidLength(InvalidFormat):
    pass


class InvalidDigits(InvalidFormat):
    pass


class BadAuthentication(InvalidValue):
    pass


def authenticate_string(string):
    if len(string) != 14:
        raise InvalidLength(string)

    if string[6] != '-':
        raise InvalidFormat(string)

    digits = map(lambda x: ord(x) - ord('0'),
                 string[:6] + string[7:])
    digits = tuple(digits)
    if not all(0 <= d < 10 for d in digits):
        raise InvalidDigits(string)

    authenticate_digits(digits)

    return string


def authenticate_digits(digits):
    if len(digits) != 13:
        raise InvalidLength(digits)

    authcode = calculate_authcode(digits)

    last = digits[12]
    if authcode != last:
        raise BadAuthentication(authcode)

    return digits


def calculate_authcode(digits):
    if len(digits) < 12:
        raise InvalidLength(digits)

    weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]

    weighted = map(lambda x, y: x * y, weights, digits[:12])
    summed = sum(weighted)
    return 11 - (summed % 11)


def construct_string(birth_date, male, foreigner, region_code, rcn, serial):
    birth_century = birth_date.year // 100 * 100
    birth_year = '%02d' % (birth_date.year % 100)
    birth_month = '%02d' % birth_date.month
    birth_day = '%02d' % birth_date.day

    if birth_century not in [1800, 1900, 2000]:
        raise ValueError(birth_century)

    sexcode = get_sexcode(birth_century, male, foreigner)
    sexcode = '%01d' % sexcode

    get_region_name(region_code)
    regioncode = '%02d' % region_code

    if not (0 <= rcn <= 99):
        raise ValueError(rcn)
    rcncode = '%02d' % rcn

    if not (0 <= serial <= 9):
        raise ValueError(serial)
    serialcode = '%01d' % serial

    s = ''.join([birth_year,
                 birth_month,
                 birth_day,
                 sexcode,
                 regioncode,
                 rcncode,
                 serialcode])
    digits = map(lambda x: ord(x) - ord('0'), s)
    digits = tuple(digits)
    authcode = calculate_authcode(digits)
    s += '%01d' % authcode
    s = '-'.join([s[:6], s[6:]])
    return s


class RRN(namedtuple('RRN', [
    'birth_year',
    'birth_month',
    'birth_day',
    'sexcode',
    'regioncode',
    'rcncode',
    'serialcode',
    'authcode',
])):

    @classmethod
    def fromstring(cls, s):
        s = authenticate_string(s)
        int(s[0:2])
        int(s[2:4])
        int(s[4:6])
        int(s[7:8])
        int(s[8:10])
        int(s[10:12])
        int(s[12:13])
        int(s[13:14])
        birth_year = s[0:2]
        birth_month = s[2:4]
        birth_day = s[4:6]
        sexcode = s[7:8]
        regioncode = s[8:10]
        rcncode = s[10:12]
        serialcode = s[12:13]
        authcode = s[13:14]
        return cls(birth_year=birth_year,
                   birth_month=birth_month,
                   birth_day=birth_day,
                   sexcode=sexcode,
                   regioncode=regioncode,
                   rcncode=rcncode,
                   serialcode=serialcode,
                   authcode=authcode)

    def __str__(self):
        return ''.join(self)

    @property
    def birth_date(self):
        year = self.birth_century + int(self.birth_year)
        month = int(self.birth_month)
        day = int(self.birth_day)
        return date(year, month, day)

    @property
    def birth_century(self):
        return birth_centruries_by_sexcode[int(self.sexcode)]

    @property
    def male(self):
        sexcode = int(self.sexcode)
        return sexcode_table[sexcode].male

    @property
    def foreigner(self):
        sexcode = int(self.sexcode)
        return sexcode_table[sexcode].foreigner

    @property
    def region_name(self):
        return get_region_name(self.regioncode)

    @property
    def rcn(self):
        '''
        읍면동 주민센터 고유번호
        '''
        return int(self.rcncode)

    @property
    def serial(self):
        return int(self.serialcode)


SexcodeTableEntry = namedtuple('SexcodeTableEntry', [
    'birth_century',
    'male',
    'foreigner',
])


sexcode_table = {
    9: SexcodeTableEntry(1800, True, False),
    0: SexcodeTableEntry(1800, False, False),
    1: SexcodeTableEntry(1900, True, False),
    2: SexcodeTableEntry(1900, False, False),
    3: SexcodeTableEntry(2000, True, False),
    4: SexcodeTableEntry(2000, False, False),
    5: SexcodeTableEntry(1900, True, True),
    6: SexcodeTableEntry(1900, False, True),
    7: SexcodeTableEntry(2000, True, True),
    8: SexcodeTableEntry(2000, False, True),
}


def get_sexcode(birth_century, male, foreigner):
    needle = SexcodeTableEntry(birth_century, male, foreigner)
    for sexcode, entry in sexcode_table.items():
        if entry == needle:
            return sexcode
    raise KeyError()


birth_centruries_by_sexcode = {
    9: 1800,
    0: 1800,
    1: 1900,
    2: 1900,
    3: 2000,
    4: 2000,
    5: 1900,
    6: 1900,
    7: 2000,
    8: 2000,
}


region_codes = {
    '서울': tuple(range(0, 9)),
    '부산': tuple(range(9, 13)),
    '인천': tuple(range(13, 16)),
    '경기': tuple(range(16, 26)),
    '강원': tuple(range(26, 35)),
    '강원': tuple(range(26, 34)),
    '충청북도': tuple(range(35, 40)),
    '대전': tuple([40]),
    '충청남도': tuple(range(41, 48)),
    '전라북도': tuple(range(48, 55)),
    '전라남도': tuple(range(55, 66)),
    '광주': tuple(range(65, 67)),
    '대구': tuple(range(67, 71)),
    '경상북도': tuple(range(71, 81)),
    '경상남도': tuple(range(81, 85)) + tuple(range(86, 91)),
    '울산': tuple([85]),
    '제주': tuple(range(91, 96)),
    '세종': tuple([44, 96]),
}


def get_region_name(region_code):
    code = int(region_code)
    for name in region_codes:
        codes = region_codes[name]
        if code in codes:
            return name
    raise ValueError(code)
