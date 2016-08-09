# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014, 2016 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals, print_function
from io import BytesIO
from unittest import TestCase
from gs.group.member.invite.csv.unicodereader import UnicodeDictReader
from . import test_data


class TestGuessEncoding(TestCase):
    'Test the guessing of the encodings'

    def test_guess_encoding_ascii(self):
        'Guess ASCII?'
        r = UnicodeDictReader.guess_encoding(BytesIO(b'Member'))
        self.assertEqual('ascii', r)

    def test_guess_encoding_latin1(self):
        'Guess ISO Latin-1'
        r = UnicodeDictReader.guess_encoding(BytesIO(b'M\xe9mb\xe9r'))
        self.assertEqual('ISO-8859-2', r)

    def test_guess_encoding_utf8(self):
        'Guess UTF-8?'
        m = BytesIO(b'\0360\0237\0230\0204 Mémbér')
        r = UnicodeDictReader.guess_encoding(m)
        self.assertEqual('utf-8', r)

    def test_guess_encoding_image(self):
        'Do we assume UTF-8 if we feed in an image?'
        with test_data('gs-logo-16x16.png') as img:
            r = UnicodeDictReader.guess_encoding(img)
        self.assertEqual('utf-8', r)


class TestGuessDialect(TestCase):
    'Test the guessing of the CSV dialect'

    def assert_delimiter(self, delimiter, dialect):
        '''Assert that the delimiter in the CSV dialect is correct'''
        self.assertTrue(hasattr(dialect, 'delimiter'), 'Not a CSV dialect instance')
        m = 'Delimiter is "{delimiter}"; expected "{dialect.delimiter}"'
        self.assertEqual(delimiter, dialect.delimiter,
                         m.format(delimiter=delimiter, dialect=dialect))

    def test_sniff_quote_csv(self):
        '''Test sniffing a CSV where everything is quoted'''
        with test_data('ascii-quote.csv') as csv:
            r = UnicodeDictReader.guess_dialect(csv)
        self.assert_delimiter(',', r)

    def test_sniff_some_csv(self):
        '''Test sniffing a CSV where somethings are quoted'''
        with test_data('utf8-some.csv') as csv:
            r = UnicodeDictReader.guess_dialect(csv)
        self.assert_delimiter(',', r)
        self.assertTrue(r.doublequote)

    def test_sniff_some_tsv(self):
        '''Test sniffing a tab-seperated file where somethings are quoted'''
        with test_data('utf8-some.tsv') as tsv:
            r = UnicodeDictReader.guess_dialect(tsv)
        self.assert_delimiter('\t', r)
        self.assertTrue(r.doublequote)

    def test_sniff_quote_tsv(self):
        '''Test sniffing a tab-seperated file where everything is quoted'''
        with test_data('ascii-quote.tsv') as tsv:
            r = UnicodeDictReader.guess_dialect(tsv)
        self.assert_delimiter('\t', r)

    def test_image(self):
        'Do we assume excel if we feed in an image?'
        with test_data('gs-logo-16x16.png') as img:
            r = UnicodeDictReader.guess_dialect(img)
        self.assertEqual('excel', r)


class TestUnicodeReader(TestCase):
    'Test the UnicodeDictReader'

    def assert_name_email(self, name, email, item):
        '''Test that a name and email address match a row from a CSV
:param str name: The expected name.
:param str email: The expected email address.
:param dict item: The row from the CSV.'''
        m = 'Name does not match: {0} != {1}'.format(name, item['name'])
        self.assertEqual(name, item['name'], m)
        m = 'Email does not match: {0} != {1}'.format(email, item['email'])
        self.assertEqual(email, item['email'], m)

    def test_csv_all_quote(self):
        '''Test a CSV where everything is quoted'''
        csv = BytesIO('''"Example Member","member@example.com"
"Another Member","another@example.com"'''.encode('utf-8'))
        u = UnicodeDictReader(csv, ['name', 'email'])
        l = list(u)

        self.assertEqual(2, len(l))
        self.assert_name_email('Example Member', 'member@example.com', l[0])
        self.assert_name_email('Another Member', 'another@example.com', l[1])

    def test_tsv_all_quote(self):
        '''Test a tab-seperated file where everything is quoted'''
        s = '''"Example Member"\t"member@example.com"
"Another Member"\t"another@example.com"'''.encode('utf-8')
        csv = BytesIO(s)
        u = UnicodeDictReader(csv, ['name', 'email'])
        l = list(u)

        self.assertEqual(2, len(l))
        self.assert_name_email('Example Member', 'member@example.com', l[0])
        self.assert_name_email('Another Member', 'another@example.com', l[1])

    def test_ascii(self):
        '''Ensure we read an ASCII encoded CSV'''
        csv = BytesIO(b'''"Michael JasonSmith",mpj17@onlinegroups.net
Member,member@example.com''')

        u = UnicodeDictReader(csv, ['name', 'email'], encoding='ascii')

        l = list(u)
        self.assertEqual(2, len(l))
        self.assert_name_email('Michael JasonSmith',
                               'mpj17@onlinegroups.net', l[0])
        self.assert_name_email('Member',
                               'member@example.com', l[1])

    def test_latin1(self):
        '''Ensure we read a ISO Latin-1 encoded CSV'''
        csv = BytesIO(b'''"Michael JasonSmith",mpj17@onlinegroups.net
M\xe9mb\xe9r,member@example.com''')

        u = UnicodeDictReader(csv, ['name', 'email'], encoding='latin-1')

        l = list(u)
        self.assertEqual(2, len(l))
        self.assert_name_email('Michael JasonSmith',
                               'mpj17@onlinegroups.net', l[0])
        self.assert_name_email('Mémbér',
                               'member@example.com', l[1])

    def test_utf8(self):
        '''Ensure we read a UTF-8 encoded CSV'''
        csv = BytesIO(b'''"Michael JasonSmith",mpj17@onlinegroups.net
M\xc3\xa9mb\xc3\xa9r \xf0\x9f\x98\x84,member@example.com''')

        u = UnicodeDictReader(csv, ['name', 'email'], encoding='utf-8')

        l = list(u)
        self.assertEqual(2, len(l))
        self.assert_name_email('Michael JasonSmith',
                               'mpj17@onlinegroups.net', l[0])
        self.assert_name_email('Mémbér \U0001f604',
                               'member@example.com', l[1])
