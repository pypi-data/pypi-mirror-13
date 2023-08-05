import unittest

class TestSanity(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sanity(self):
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()
