import unittest
from flipexception import FlipValueError

class FlipAllTheThings(unittest.TestCase):
    def setUp(self):
        pass

    def test_exception_base(self):
        """
        Testing Eexception Base
        """

        with self.assertRaises(Exception):
            raise FlipValueError()

    def test_exception_flip(self):
        """
        Testing Eexception Base
        """

        with self.assertRaises(FlipValueError):
            raise FlipValueError()
