"""
textlocal.contacts
~~~~~~~~~~~~~~~~~~

This module defines the classes used for contact management.
"""
class Contact(object):
    """
    Represents a contact with a single phone number.

    Arguments:
        number (PhoneNumber): The contacts phone number.
        group_id (int)
    """
    def __init__(self, number, group_id, **kwargs):
        self.number = number
        self.group_id = group_id
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self.custom1 = kwargs.get('custom1', '')
        self.custom2 = kwargs.get('custom2', '')
        self.custom3 = kwargs.get('custom3', '')

class Group(object):
    def __init__(self, name, group_id=None, size=None):
        self.name = name
        self.id = group_id
        self.size = size
