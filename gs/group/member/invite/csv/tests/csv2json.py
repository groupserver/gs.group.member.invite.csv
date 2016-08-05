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
from __future__ import absolute_import, unicode_literals
from json import dumps as to_json
from mock import MagicMock
from unittest import TestCase
from gs.group.member.invite.csv.csv2json import CSV2JSON
from . import test_data


class TestCSV2JSON(TestCase):
    def test_content_type_missmatch(self):
        'Test that we error when given an image, rather than a CSV'
        data = {}
        data['columns'] = ['Name', 'Email']
        with test_data('gs-logo-16x16.png') as i:
            data['csv'] = i.read()
        mockSite = MagicMock()
        mockRequest = MagicMock()

        csv2json = CSV2JSON(mockSite, mockRequest)
        r = csv2json.actual_process(data)

        self.assertIn('"status": -2', r)

    def test_col_missmatch(self):
        'Test that we error when we have too many columns'
        data = {}
        data['columns'] = ['Name', 'Email']
        data['csv'] = b'''"Michael JasonSmith",mpj17@onlinegroups.net,37
M\xc3\xa9mb\xc3\xa9r \xf0\x9f\x98\x84,member@example.com,28'''
        mockSite = MagicMock()
        mockRequest = MagicMock()

        csv2json = CSV2JSON(mockSite, mockRequest)
        r = csv2json.actual_process(data)

        self.assertIn('"status": -3', r)

    def test_header_csv(self):
        'Test that we error when we have a CSV with only a header'
        data = {}
        data['columns'] = ['Name', 'Email']
        data['csv'] = b'Name,Email\n'
        mockSite = MagicMock()
        mockRequest = MagicMock()

        csv2json = CSV2JSON(mockSite, mockRequest)
        r = csv2json.actual_process(data)

        self.assertIn('"status": -4', r)

    def test_empty_csv(self):
        'Test that we error when we have an empty CSV'
        data = {}
        data['columns'] = ['Name', 'Email']
        data['csv'] = b''
        mockSite = MagicMock()
        mockRequest = MagicMock()

        csv2json = CSV2JSON(mockSite, mockRequest)
        r = csv2json.actual_process(data)

        self.assertIn('"status": -5', r)

    def test_csv(self):
        'Test that a normal CSV is fine'
        data = {}
        data['columns'] = ['Name', 'Email']
        with test_data('test-utf-8.csv') as i:
            data['csv'] = i.read()
        mockSite = MagicMock()
        mockRequest = MagicMock()

        csv2json = CSV2JSON(mockSite, mockRequest)
        r = csv2json.actual_process(data)

        e = [
            {"Name": "Michael JasonSmith",
             'Email': 'mpj17@onlinegroups.net'},
            {"Name": "My God\u2026 it is full of stars",
             "Email": "stars@example.com"},
            {"Name": "Dirk \u201cBox Crusher\u201d Dinsdale",
             "Email": "dirk@example.com"}]
        expected = to_json(e)
        self.assertEqual(expected, r)
