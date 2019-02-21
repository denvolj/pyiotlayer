import unittest

import os
import sys
import json
import unittest

from pyiotlayer.utils import IotUtils
from pyiotlayer.objects import IotContainer
from pyiotlayer.worker.modules.fragmentator import ContainerFragmentator

class FragmentatorTestCase(unittest.TestCase):
    def setUp(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, 'data.json')) as f:
            json_data = json.load(f)
        self.data = IotContainer.parse(json_data)

    def test_container_mtu_limits_fragmentation(self):
        mtu = 450

        data_sets = []
        for container in self.data:
            data_sets += [ContainerFragmentator(container, mtu).do()]

        i = 0
        for fragments in data_sets:
            for fragment in fragments:
                with self.subTest(i):
                    i += 1
                    self.assertLessEqual(IotUtils.getSize(fragment), mtu, "Length more than MTU")



if __name__ == '__main__':
    unittest.main()