from pyiotlayer.transport.objects import IotContainer
import unittest
import json

class TestParsing(unittest.TestCase):

    def test_clone(self):
        tests = [
            {"o":{"d":{}}},
            {"o":{"d":[{}]}},
            {"o":[{"d":{}}]},
            {"o":[{"d":[{}]}]}
        ]

        for value in tests:
            with self.subTest(value=value):
                control = IotContainer.parse(value)
                self.assertEqual(control.toJSON(), control.clone().toJSON())

    
    def test_getSize(self):
        tests = [
            {"o":{"d":{}}},
            {"o":{"d":[{}]}},
            {"o":[{"d":{}}]},
            {"o":[{"d":[{}]}]}
        ]

        for value in tests:
            with self.subTest(value=value):
                control = IotContainer.parse(value)
                self.assertGreater(control.getSize(), 5)


if __name__ == '__main__':
    unittest.main()