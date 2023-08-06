"""
textlocal.messages
~~~~~~~~~~~~~~~~~~

This module defines the messages used by Textlocal.
"""
import base64
from datetime import datetime


class Message(object):
    """
    Base message class

    Attributes:
        message: The message content.
        numbers: A List of numbers to send the message to.
        group_id: The group_id to send the message to. Overrides numbers.
        schedule_time: A datetime object specifying when to send the message.
        optouts: A Boolean setting whether to check the recipients against an optout list.
    """

    def __init__(self, message, numbers=None, group_id=None,
                 schedule_time=None, optouts=False):
        """
        Returns a new Message object
        """
        # pylint: disable-msg=R0913
        self.message = message
        if numbers is None and group_id is None:
            raise Exception('numbers or group_id must be set.')
        else:
            self.numbers = numbers
            self.group_id = group_id
        self.numbers = numbers
        if schedule_time is not None and not isinstance(schedule_time, datetime):
            raise TypeError("If set 'schedule_time' should be a 'datetime'.")
        else:
            self.schedule_time = schedule_time
        if not isinstance(optouts, bool):
            raise TypeError("If set 'optouts' must be a boolean.")
        else:
            self.optouts = optouts

    def message_size(self):
        """
        Calculates the size of the message in bytes.
        """
        string = self.message.encode('utf8')
        return len(string)

    def __len__(self):
        return self.message_size()

    def as_dict(self):
        dic = self.__dict__.items()
        return {k: v for k, v in dic if v}

    def prepare(self):
        dic = self.as_dict()
        if 'schedule_time' in dic:
            dic['schedule_time'] = dic['schedule_time'].timestamp()
        return dic

class SMS(Message):
    """
    SMS message.

    Attributes:
        simple_reply: A Boolean setting whether or not to use the simple reply service.
    """

    def __init__(self, message, numbers=None, group_id=None,
                 schedule_time=None, simple_reply=False):
        """Returns a new SMS object."""
        # pylint: disable-msg=R0913
        super().__init__(message, numbers, group_id, schedule_time)
        self.simple_reply = simple_reply


class MMS(Message):
    """
    MMS message

    Attributes:
        url: A url giving the location of a media file.
        image: A file-like object to base64 encode.
    """

    def __init__(self, message, numbers=None, group_id=None,
                 schedule_time=None, optouts=False, url=None, image=None):
        """
        Returns new MMS object
        """
        # pylint: disable-msg=R0913
        super().__init__(message, numbers, group_id, schedule_time, optouts)
        self.url = url
        if image is not None:
            try:
                self.encoded_image = base64.b64encode(image.read())
            except AttributeError as e:
                raise TypeError("If 'image' is used it must"
                                " be a file-like object.") from e

    def message_size(self):
        size = super().message_size()
        return size + len(self.encoded_image)
