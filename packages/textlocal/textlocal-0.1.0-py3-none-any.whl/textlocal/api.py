"""
textlocal.api
~~~~~~~~~~~~~

This module contains the Textlocal api.
"""
import json
import urllib.parse

import requests

from textlocal.messages import SMS

class Textlocal(object):
    """
    Textlocal([api_key[, username[, password[, **kwargs]]]])

    The api_key or username and password are required.
    """
    DOMAIN = 'https://api.txtlocal.com'

    def __init__(self, api_key=None, username=None, password=None, **kwargs):
        if api_key == username == password == None:
            raise Exception(
                "Either api_key or username and password must be used.")
        elif ((username is None and password is not None)
                or
                (password is None and username is not None)):
            raise Exception("If using username and password both must be set.")
        self.api_key = api_key
        self.username = username
        self.password = password
        self.sender = kwargs.get('sender', None)
        self.simple_reply = kwargs.get('simple_reply', None)
        self.test = kwargs.get('test', False)

    def get_balance(self):
        """
        Gets the credit balance

        Returns as two-tuple in the form `(sms, mms)`.

        Returns:
            tuple: two-tuple in the form :code:`(sms, mms)`
        """
        PATHNAME = 'balance'
        response = self._get(PATHNAME)
        balance = response.get('balance')
        return balance['sms'], balance['mms']

    def get_templates(self):
        """
        Fetches all of the templates stored on Textlocal

        Returns:
            list: A list of :class:`Template`s
        """
        PATHNAME = 'get_templates'
        response = self._get(PATHNAME)
        return response.get('templates')

    def check_keyword(self, keyword):
        """
        Checks the availablity of a keyword on 60777 and 66777.

        Arguments:
            keyword (str): The keyword to check

        Returns:
            list: A list of the numbers the keyword is available on.

        Raises:
            TextlocalException: If the keyword is too short
            TextlocalException: If the keyword is too long
        """
        PATHNAME = 'check_keyword'
        response = self._get(PATHNAME, {'keyword' : str(keyword)})
        return response.get('templates')

    def txt(self, numbers, message):
        """
        Arguments:
            numbers (list): A list of :class:`PhoneNumber`
        """
        sms = SMS(message, numbers)
        return self._send(sms)

    def _send(self, message):
        data = self._get_message_defaults()
        data.update(message.as_dict())
        return self._post('send', data)

    def _get(self, pathname, data=None):
        return self._call('get', pathname, data)

    def _post(self, pathname, data=None):
        return self._call('post', pathname, data)

    def _call(self, method, pathname, data=None):
        """
        Makes a request to the textlocal api. Returns a JSON dictionary.
        """
        url = urllib.parse.urljoin(self.DOMAIN, pathname)
        if not data:
            data = dict()
        data.update(self._get_credentials())
        r = getattr(requests, method)(url, data)
        return r.json()

    def _get_credentials(self):
        """
        Creates a dictionary of the api credentials

        Prefers an api key over username/password.
        """
        if self.api_key:
            return {'apiKey': self.api_key}
        else:
            return {'username': self.username, 'hash': self.password}

    def _get_message_defaults(self):
        """
        Provides the default message fields.

        Returns:
            dict: A dictionay of messages settings.
        """
        defaults = {}
        if self.sender:
            defaults['sender'] = self.sender
        if self.simple_reply:
            defaults['simple_reply'] = self.simple_reply
        if self.test:
            defaults['test'] = self.test
        return defaults
