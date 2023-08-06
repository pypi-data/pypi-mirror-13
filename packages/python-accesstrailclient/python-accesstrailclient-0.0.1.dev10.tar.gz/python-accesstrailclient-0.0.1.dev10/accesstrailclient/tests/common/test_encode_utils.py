# -*- coding: utf-8 -*-
"""Test for encode utils."""

from accesstrailclient.common import encode_utils
from accesstrailclient.tests import base


class EncodeUtilsTestCase(base.TestCase):
    """Encode utils test cases."""

    def test_encode_data(self):
        fake_token = "test"
        fake_data = "test"
        expected_token = "DJRRXBXlCVuKh6ULoN87847QX+Y="
        result = encode_utils.encrypt_data(fake_token, fake_data)
        self.assertEqual(result, expected_token)
