# -*- coding: utf-8 -*-
"""Send requests to Access Trail api."""

import requests
import threading
import time

from accesstrailclient.common import encode_utils as utils
from accesstrailclient.common import exceptions

_ACCESS_TRAIL_API = None
_RETRY_INTERVAL = 10
_MESSAGE_CACHE = []


def periodic_retry():
    """Retry to send message."""
    global _MESSAGE_CACHE
    print("Start periodic retry task, message: {}".format(_MESSAGE_CACHE))
    for message in _MESSAGE_CACHE:
        try:
            _ACCESS_TRAIL_API.send_message(message, retry=True)
        except (exceptions.NoValidRequest,
                exceptions.AuthenticationFailed):
            # No need to retry for this kind of message
            # FIXME: Message will be lost here. But if we
            # use this client correctly, these exceptions can
            # be avoid.
            _MESSAGE_CACHE.remove(message)
        except (exceptions.ServerUnavailable,
                exceptions.InternalServerError):
            pass
        else:
            # Send successfully
            _MESSAGE_CACHE.remove(message)
    threading.Timer(_RETRY_INTERVAL, periodic_retry).start()


def get_instance(url, token, project_id, retry_interval=_RETRY_INTERVAL):
    """Get the instance for Access Trail API.

    :param url: The Access Trail url to send message to.
    :param token: The token which take from Access Trail.
    :param project: The service provider project id.
    :param retry_interval: Interval to retry to send message.
    :returns: A access trail api object.
    """
    global _ACCESS_TRAIL_API
    global _RETRY_INTERVAL
    if _ACCESS_TRAIL_API is None:
        _ACCESS_TRAIL_API = AccessTrailApi(url, token, project_id)
        # Start the periodic retry task
        _RETRY_INTERVAL = retry_interval
        periodic_retry()
    return _ACCESS_TRAIL_API


class AccessTrailApi(object):
    """Access Trail Api Class."""

    def __init__(self, url, token, project_id):
        """Init for access trail api class.

        :param url: The Access Trail url to send message to.
        :param token: The token which take from Access Trail.
        :param project: The service provider project id.
        """
        self.url = url
        self.token = token
        self.project_id = project_id

    def send_message(self, body, retry=False):
        """Send message to Access Trail."""
        global _MESSAGE_CACHE
        headers = self._build_header()
        try:
            r = requests.post(
                self.url,
                headers=headers,
                data=body)
        except requests.exceptions.ConnectionError:
            print("Server is unavailable at this time, will retry....")
            if retry:
                raise exceptions.ServerUnavailable(server=self.url)
            else:
                _MESSAGE_CACHE.append(body)
                return

        if r.status_code == 400:
            raise exceptions.NoValidRequest()
        elif r.status_code == 403:
            raise exceptions.AuthenticationFailed()
        elif r.status_code in (500, 502):
            if retry:
                raise exceptions.InternalServerError()
            else:
                _MESSAGE_CACHE.append(body)
        elif r.status_code == 200:
            print("Send sucessfully!")
        return r.status_code

    def _build_header(self):
        """Build header for request.

        request_token = HMAC+SHA1(key=token, data=(timestamp+token))

        :param timestamp: The timestamp right now.
        :returns: The header dict for a request
        """
        timestamp = int(time.time())
        data = str(timestamp) + self.token
        print("data = {}".format(data))
        token = utils.encrypt_data(self.token, data)
        print("token = {}".format(token))
        headers = {
            "X-Auth-Token": token,
            "X-Auth-Project-Id": self.project_id,
            "X-Auth-Timestamp": timestamp,
        }
        return headers
