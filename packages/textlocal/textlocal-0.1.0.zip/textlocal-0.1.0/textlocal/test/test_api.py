import os
import unittest

from textlocal import Textlocal


API_KEY = os.environ['API_KEY']


class TextlocalTest(unittest.TestCase):

    def setUp(self):
        self.textlocal = Textlocal(api_key=API_KEY)

    def test_init_api_key(self):
        with self.assertRaises(Exception):
            textlocal = Textlocal()
        textlocal = Textlocal(api_key=API_KEY)
        self.assertEqual(type(textlocal), Textlocal)

    def test_init_password_username(self):
        with self.assertRaises(Exception):
            textlocal = Textlocal(username='username')
        with self.assertRaises(Exception):
            textlocal = Textlocal(password='password')
        textlocal = Textlocal(username='username', password='password')
        self.assertEqual(type(textlocal), Textlocal)

    def test_init_kwargs_sender(self):
        sender = 'sender'
        textlocal = Textlocal(api_key=API_KEY)
        self.assertEqual(textlocal.sender, None)
        textlocal = Textlocal(api_key=API_KEY, sender=sender)
        self.assertEqual(textlocal.sender, sender)

    def test_init_kwargs_simple_reply(self):
        simple_reply = True
        textlocal = Textlocal(api_key=API_KEY)
        self.assertEqual(textlocal.simple_reply, None)
        textlocal = Textlocal(api_key=API_KEY, simple_reply=simple_reply)
        self.assertEqual(textlocal.simple_reply, simple_reply)

    def test_init_kwargs_test(self):
        test = True
        textlocal = Textlocal(api_key=API_KEY)
        self.assertEqual(textlocal.test, False)
        textlocal = Textlocal(api_key=API_KEY, test=test)
        self.assertEqual(textlocal.test, test)

    def test_get_credentials_returns_dict(self):
        USERNAME = 'username'
        PASSWORD = 'password'
        textlocal = Textlocal(api_key=API_KEY)
        credentials = textlocal._get_credentials()
        self.assertIsInstance(credentials, dict)
        textlocal = Textlocal(username=USERNAME, password=PASSWORD)
        credentials = textlocal._get_credentials()
        self.assertIsInstance(credentials, dict)

    def test_get_credentials_returns_credentials(self):
        USERNAME = 'username'
        PASSWORD = 'password'
        textlocal = Textlocal(api_key=API_KEY)
        credentials = textlocal._get_credentials()
        self.assertEqual(credentials['apiKey'], API_KEY)
        textlocal = Textlocal(username=USERNAME, password=PASSWORD)
        credentials = textlocal._get_credentials()
        self.assertEqual(credentials['username'], USERNAME)
        self.assertEqual(credentials['hash'], PASSWORD)
        textlocal = Textlocal(api_key=API_KEY,
                              username=USERNAME,
                              password=PASSWORD)
        credentials = textlocal._get_credentials()
        self.assertEqual(credentials['apiKey'], API_KEY)

    def test_get_credentials_prefers_api_key(self):
        USERNAME = 'username'
        PASSWORD = 'password'
        textlocal = Textlocal(api_key=API_KEY,
                              username=USERNAME,
                              password=PASSWORD)
        credentials = textlocal._get_credentials()
        self.assertEqual(len(credentials), 1)

    def test_call(self):
        response = self.textlocal._call('get', '')
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 2)
        self.assertEqual(response['status'], 'failure')

    def test_get(self):
        response = self.textlocal._get('')
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 2)
        self.assertEqual(response['status'], 'failure')

    def test_post(self):
        response = self.textlocal._post('')
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 2)
        self.assertEqual(response['status'], 'failure')

    def test_get_balance_returns_tuple(self):
        balance = self.textlocal.get_balance()
        self.assertIsInstance(balance, tuple)

    def test_get_balance_tuple_has_length_two(self):
        balance = self.textlocal.get_balance()
        self.assertEqual(len(balance), 2)

    def test_get_balance_returns_ints(self):
        balance = self.textlocal.get_balance()
        self.assertIsInstance(balance[0], int)
        self.assertIsInstance(balance[1], int)

    def test_get_templates_returns_list(self):
        templates = self.textlocal.get_templates()
        self.assertIsInstance(templates, list)

    def test_get_message_defaults_empty(self):
        message_defaults = self.textlocal._get_message_defaults()
        self.assertIsInstance(message_defaults, dict)
        self.assertEqual(len(message_defaults), 0)

    def test_get_message_defaults(self):
        test = True
        simple_reply = True
        sender = 'Sender'
        textlocal = Textlocal(api_key='None', test=test, sender=sender,
                              simple_reply=simple_reply)
        message_defaults = textlocal._get_message_defaults()
        self.assertIsInstance(message_defaults, dict)
        self.assertEqual(len(message_defaults), 3)
        self.assertEqual(message_defaults.get('test'), test)
        self.assertEqual(message_defaults.get('sender'), sender)
        self.assertEqual(message_defaults.get('simple_reply'), simple_reply)

if __name__ == '__main__':
    unittest.main()
