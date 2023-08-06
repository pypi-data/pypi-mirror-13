# -*- coding: utf-8 -*-
"""Test for Access Trail api class."""

from accesstrailclient import access_trail
from accesstrailclient.tests import base

import json
from mock import patch


class AccessTrailApiTestCase(base.TestCase):
    """Test case for access trail api."""

    def setUp(self):
        super(AccessTrailApiTestCase, self).setUp()
        fake_url = 'https://iauth.stage1.edge.bluemix.net/v1/trail'
        fake_token = 'eP3tD0PGrTmG'
        fake_project_id = 'eee11302-14b9-4ad1-9b3d-66a0a82f570b'
        self.api = access_trail.AccessTrailApi(fake_url, fake_token,
                                               fake_project_id)

    @patch("time.time")
    @patch("accesstrailclient.common.encode_utils.encrypt_data")
    def test_build_header(self, mock_encrypt_data, mock_time):
        fake_return_token = "fake_return_token"
        fake_timestamp = 1234567689
        mock_encrypt_data.return_value = fake_return_token
        mock_time.return_value = fake_timestamp
        result = self.api._build_header()
        expected = {
            "X-Auth-Token": fake_return_token,
            "X-Auth-Project-Id": "eee11302-14b9-4ad1-9b3d-66a0a82f570b",
            "X-Auth-Timestamp": 1234567689
        }
        self.assertEqual(result, expected)

    def test_send_message(self):
        latencies = 100
        message = {
            "started_at": 12345678,
            "request": {
                "method": "GET",
                "uri": "/v1/version",
                "size": "11",
                "request_uri": "http://example.com/v1/version",
                "querystring": {
                    "key": "value"
                },
                "request_body": "Hello World",
                "headers": {
                    "content-type": "application/json",
                    "connection": "keep-alive",
                    "accept": "application/json",
                    "X-Auth-Token": "Token"
                }
            },
            "response": {
                "status": 200,
                "response_body": "Status OK",
                "size": "9",
                "headers": {
                    "content-type": "application/json"
                }
            },
            "client_ip": "127.0.0.1",
            "latencies": {
                "request": latencies
            }
        }
        self.api.send_message(json.dumps(message))
