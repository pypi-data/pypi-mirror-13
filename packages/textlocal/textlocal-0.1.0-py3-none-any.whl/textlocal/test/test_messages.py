import base64
from datetime import datetime
import unittest

from textlocal.messages import Message, SMS, MMS


class MessageTest(unittest.TestCase):

    def test_init_numbers_or_group_id(self):
        with self.assertRaises(Exception):
            message = Message('message', numbers=None, group_id=None)

    def test_init_numbers(self):
        message_text = 'message'
        number = '4470123456789'
        message = Message(message_text, numbers=[number, ])
        self.assertEqual(message.message, message_text)
        self.assertTrue(type(message.numbers), list)
        self.assertIn(number, message.numbers)

    def test_init_group_id(self):
        message_text = 'message'
        group_id = '4'
        message = Message(message_text, group_id=group_id)
        self.assertEqual(message.message, message_text)
        self.assertEqual(message.group_id, group_id)

    def test_init_schedule_time(self):
        message_text = 'message'
        number = '4470123456789'
        with self.assertRaises(TypeError):
            message = Message(message_text, [number, ], schedule_time="time")
        schedule_time = datetime.today()
        message = Message(message_text, numbers=[number, ],
                          schedule_time=schedule_time)
        self.assertEqual(message.schedule_time, schedule_time)

    def test_init_optouts(self):
        message_text = 'message'
        number = '4470123456789'
        with self.assertRaises(TypeError):
            message = Message(message_text, numbers=[number, ], optouts='true')
        optouts = True
        message = Message(message_text, numbers=[number, ], optouts=True)
        self.assertTrue(message.optouts)

    def test_message_size(self):
        message_text = 'message'
        number = '4470123456789'
        message = Message(message_text, [number, ])
        self.assertEqual(message.message_size(), 7)
        self.assertEqual(len(message), 7)
        message.message = '𠜎'
        self.assertEqual(message.message_size(), 4)
        self.assertEqual(len(message), 4)

    def test_as_dict(self):
        message_text = 'message'
        numbers = ['44012345678910']
        group_id = None
        message = Message(message_text, numbers, group_id=group_id)
        dic = message.as_dict()
        self.assertIn('message', dic)
        self.assertIn('numbers', dic)
        self.assertNotIn('group_id', dic)

    def test_prepare(self):
        schedule_time = datetime.today()
        message = Message('message', [1,], schedule_time=schedule_time)
        dic = message.prepare()
        self.assertIsInstance(dic, dict)
        self.assertEqual(dic.get('schedule_time'), schedule_time.timestamp())

class SMSTest(unittest.TestCase):

    def test_init_simple_reply(self):
        message_text = 'message'
        number = '4470123456789'
        simple_reply = True
        message = SMS(message_text, numbers=[number, ],
                      simple_reply=simple_reply)
        self.assertTrue(message.simple_reply)

    def test_message_size(self):
        message_text = 'message'
        number = '4470123456789'
        message = SMS(message_text, [number, ])
        self.assertEqual(message.message_size(), 7)
        self.assertEqual(len(message), 7)
        message.message = '𠜎'
        self.assertEqual(message.message_size(), 4)
        self.assertEqual(len(message), 4)


class MMSTest(unittest.TestCase):

    def test_init_url(self):
        message_text = 'message'
        number = '4470123456789'
        url = 'http://example.com'
        message = MMS(message_text, [number, ], url=url)
        self.assertEqual(message.url, url)

    def test_init_encoded_image(self):
        message_text = 'message'
        number = '4470123456789'
        with self.assertRaises(TypeError):
            message = MMS(message_text, [number, ], image='test_file')
        with open(__file__, 'rb') as test_file:
            message = MMS(message_text, [number, ], image=test_file)
            test_file.seek(0)
            encoded_file = base64.b64encode(test_file.read())
        self.assertEqual(message.encoded_image, encoded_file)

    def test_message_size(self):
        message_text = 'message'
        number = '4470123456789'
        with open(__file__, 'rb') as test_file:
            message = MMS(message_text, [number, ], image=test_file)
            test_file.seek(0)
            encoded_file = base64.b64encode(test_file.read())
        self.assertEqual(message.message_size(), 7 + len(encoded_file))
        self.assertEqual(len(message), 7 + len(encoded_file))

if __name__ == '__main__':
    unittest.main()
