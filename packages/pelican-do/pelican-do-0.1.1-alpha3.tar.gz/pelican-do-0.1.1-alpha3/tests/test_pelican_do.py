import unittest
import pelican_do

def fun(x):
    return x + 1

class MainTest(unittest.TestCase):
    def test(self):
        self.assertEqual(fun(3), 4)

