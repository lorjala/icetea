"""
Copyright 2017 ARM Limited
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import unittest

from icedtea_lib.TestSuite.TestcaseFilter import TestcaseFilter
from icedtea_lib.TestSuite.TestcaseContainer import TestcaseContainer
from icedtea_lib.IcedTeaManager import TCMetaSchema

class TCFilterTestcase(unittest.TestCase):

    def test_create_filter_simple(self):
        filt = TestcaseFilter().tc("test_cmdline")
        self.assertDictEqual(filt._filter, {'status': False, 'group': False, 'name': 'test_cmdline', 'comp': False,
                                          'list': False, 'subtype': False, 'type': False, 'feature': False})

        with self.assertRaises(TypeError):
            TestcaseFilter().tc(0)
        with self.assertRaises(IndexError):
            TestcaseFilter().tc([])
        with self.assertRaises(TypeError):
            TestcaseFilter().tc(None)
        with self.assertRaises(TypeError):
            TestcaseFilter().tc(True)


        self.assertDictEqual(TestcaseFilter().tc(1)._filter, {'status': False, 'group': False, 'name': False,
                                                                        'comp': False, 'list': [0], 'subtype': False,
                                                                        'type': False, 'feature': False})
        self.assertDictEqual(TestcaseFilter().tc([1, 4])._filter, {'status': False, 'group': False, 'name': False,
                                                               'comp': False, 'list': [0, 3],
                                                               'subtype': False, 'type': False, 'feature': False})

    def test_create_filter_complex(self):
        filt = TestcaseFilter()

        filt.tc("test_test")
        filt.component("test_comp")
        filt.group("test_group")
        filt.status("test_status")
        filt.testtype("test_type")
        filt.subtype("test_subtype")
        filt.feature("test_feature")

        self.assertDictEqual(filt._filter, {"status": "test_status", "group": "test_group", "name": "test_test",
                                            "type": "test_type", "subtype": "test_subtype",
                                            "comp": "test_comp", 'list': False, 'feature': "test_feature"})

        with self.assertRaises(TypeError):
            filt.component(2)

    def test_match(self):
        tc = TestcaseContainer.find_testcases("examples.test_cmdline", "." + os.path.sep + "examples", TCMetaSchema().get_meta_schema())
        filt = TestcaseFilter().tc("test_cmdline")
        self.assertTrue(filt.match(tc[0], 0))
        filt.component("cmdline,testcomponent")
        filt.group("examples")
        self.assertTrue(filt.match(tc[0], 0))
        filt.tc("test_something_else")
        self.assertFalse(filt.match(tc[0], 0))
        filt = TestcaseFilter().tc([1])
        self.assertTrue(filt.match(tc[0], 0))
        self.assertFalse(filt.match(tc[0], 1))



if __name__ == '__main__':
    unittest.main()