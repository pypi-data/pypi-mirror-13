import unittest

from textlocal.exceptions import TextlocalException
from textlocal.models import Response


class ResponseTest(unittest.TestCase):

    def test_init_failure_raises_exception(self):
        message = "No command specified"
        json = {"errors": [{"code": 1, "message": message}, ],
                "status": "failure"}
        with self.assertRaises(TextlocalException):
            Response(json)
        with self.assertRaisesRegex(TextlocalException, message):
            Response(json)

if __name__ == '__main__':
    unittest.main()
