__version__ = '0.0.1'

import json
import urllib

import requests

BASE_URL = "https://exp.host/"
# BASE_URL = "http://localhost:3000/"
BASE_API_URL = BASE_URL + "--/api/"

class Push(object):
    """Push Notifications"""

    @classmethod
    def is_exponent_push_token(cls, token):
        """Returns `True` if the token is an Exponent push token"""

        return (type(token) is str) and token.startswith('ExponentPushToken')

class Client(object):
    """Client stuff"""

    def publish(self, exponentPushToken=None, message="", data={}):
        """Sends a push notification with the given options and data"""

        #response = requests.post("https://exp.host/--/api/notify/" + urllib.quote_plus(json.dumps({
        response = requests.post(BASE_API_URL + "notify/" + json.dumps([{
            "exponentPushToken": exponentPushToken,
            "message": message,
        }]),
            data=json.dumps(data),
            headers={
                'Content-Type': 'application/json',
            }
        )

        if response.status_code == 400:
            raise InvalidPushTokenError("Token: %s" % exponentPushToken, response)

class InvalidPushTokenError(Exception):
    """Raised when a push token is not a valid ExponentPushToken"""

    def __init__(self, message, response):
        self.message = message
        self.response = response
