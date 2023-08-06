# -*- coding: utf-8 -*-
"""Data Encrypt."""

import base64
from hashlib import sha1
import hmac


def encrypt_data(key, data):
    """Encrypt token using Hmac-Sha1.

    :param key: The key to encode the data
    :param data: The data need to encode
    :returns: The encryptd data with base64 encoded
    """
    message = bytes(data).encode('utf-8')
    secret = bytes(key).encode('utf-8')

    hmac_obj = hmac.new(secret, message, digestmod=sha1)
    signature = base64.b64encode(hmac_obj.digest())
    return signature
