#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_netuitive
----------------------------------

Tests for `netuitive` module.
"""

import unittest
import mock

import os
import json
import time
import netuitive

try:
    from cStringIO import StringIO

except ImportError:
    try:
        from StringIO import StringIO

    except ImportError:
        from io import StringIO

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

try:
    import http.client as httplib
except ImportError:
    import httplib


def getFixtureDirPath():
    path = os.path.join(
        os.path.dirname('tests/'),
        'fixtures')
    return path


def getFixturePath(fixture_name):
    path = os.path.join(getFixtureDirPath(),
                        fixture_name)
    if not os.access(path, os.R_OK):
        print('Missing Fixture ' + path)
    return path


def getFixture(fixture_name):
    with open(getFixturePath(fixture_name), 'r') as f:
        return StringIO(f.read())


class MockResponse(object):

    def __init__(self,
                 resp_data='',
                 headers={'content-type': 'text/plain; charset=utf-8'},
                 code=200,
                 msg='OK'):

        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = headers

    def read(self):
        return self.resp_data

    def getcode(self):
        return self.code

    def close(self):
        return True


class TestClientSamplePost(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_success(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=202)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')

        e = netuitive.Element()

        e.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')

        resp = a.post(e)

        self.assertTrue(resp)

        self.assertEqual(mock_logging.exception.call_args_list, [])

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_failure_general(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=500)
        mock_post.side_effect = urllib2.HTTPError(*[None] * 5)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')

        e = netuitive.Element()

        e.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')

        resp = a.post(e)

        self.assertNotEqual(resp, True)

        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'error posting payload to api ingest endpoint (%s): %s')

    def tearDown(self):
        pass


class TestClientEventPost(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_success(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=202)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')

        e = netuitive.Event(
            'test', 'INFO', 'test event', 'big old test message', 'INFO')

        resp = a.post_event(e)

        self.assertTrue(resp)

        self.assertEqual(mock_logging.exception.call_args_list, [])

    @mock.patch('netuitive.client.urllib2.urlopen')
    @mock.patch('netuitive.client.logging')
    def test_failure_general(self, mock_logging, mock_post):

        mock_post.return_value = MockResponse(code=500)
        mock_post.side_effect = urllib2.HTTPError(*[None] * 5)

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')

        e = netuitive.Event(
            'test', 'INFO', 'test event', 'big old test message', 'INFO')

        resp = a.post_event(e)

        self.assertNotEqual(resp, True)

        self.assertEqual(mock_logging.exception.call_args_list[0][0][
                         0], 'error posting payload to api ingest endpoint (%s): %s')

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
