import unittest

import textlocal.contacts


class GroupTest(unittest.TestCase):

    def test_group_with_only_name(self):
        name = 'name'
        group = textlocal.contacts.Group(name)
        self.assertEqual(group.name, name)
        self.assertEqual(group.id, None)
        self.assertEqual(group.size, None)

    def test_group_with_group_id(self):
        name = 'name'
        group_id = 1
        group = textlocal.contacts.Group(name, group_id)
        self.assertEqual(group.id, group_id)

    def test_group_with_size(self):
        name = 'name'
        size = 1
        group = textlocal.contacts.Group(name, size=size)
        self.assertEqual(group.size, size)

class ContactTest(unittest.TestCase):

    def test_init_with_number_and_group(self):
        number = '4412345678910'
        group_id = 1
        contact = textlocal.contacts.Contact(number, group_id)
        self.assertEqual(contact.number, number)
        self.assertEqual(contact.group_id, group_id)

    def test_init_with_empty_kwargs(self):
        number = '4412345678910'
        group_id = 1
        fields = ('first_name', 'last_name', 'custom1', 'custom2', 'custom3')
        contact = textlocal.contacts.Contact(number, group_id)
        for field in fields:
            self.assertEqual(getattr(contact, field), '')

    def test_init_with_kwargs(self):
        number = '4412345678910'
        group_id = 1
        fields = ('first_name', 'last_name', 'custom1', 'custom2', 'custom3')
        kwargs = {v:v for v in fields}
        contact = textlocal.contacts.Contact(number, group_id, **kwargs)
        for field in fields:
            self.assertEqual(getattr(contact, field), kwargs[field])

if __name__ == '__main__':
    unittest.main()
