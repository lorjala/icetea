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

import unittest
from icedtea_lib.AllocationContext import AllocationContext, AllocationContextList
import logging
import mock

from icedtea_lib.DeviceConnectors.Dut import DutConnectionError
from icedtea_lib.ResourceProvider.exceptions import ResourceInitError


class AllocContextTestcase(unittest.TestCase):

    def test_set(self):
        con1 = AllocationContext("id1", "al_id1", {"data": "data1"})
        con1["test"] = "test"
        self.assertEqual(con1.get_alloc_data()["test"], "test")
        con1.set("test", "test2")
        self.assertEqual(con1.get_alloc_data()["test"], "test2")

    def test_get(self):
        con1 = AllocationContext("id1", "al_id1", {"data": "data1"})
        con1.set("test", "test3")
        self.assertEqual(con1.get("test"), "test3")
        self.assertEqual(con1["test"], "test3")


class AllocContextListTestcase(unittest.TestCase):

    def setUp(self):
        self.nulllogger = logging.getLogger("test")
        self.nulllogger.addHandler(logging.NullHandler())

    def test_append_and_len(self):
        con1 = AllocationContext("id1", "al_id1", {"data": "data1"})
        con2 = AllocationContext("id2", "al_id2", {"data": "data2"})
        con_list = AllocationContextList(self.nulllogger)
        self.assertEqual(len(con_list), 0)
        con_list.append(con1)
        self.assertEqual(len(con_list), 1)
        con_list.append(con2)
        self.assertEqual(len(con_list), 2)

    def test_get_and_set_item(self):
        con1 = AllocationContext("id1", "al_id1", {"data": "data1"})
        con2 = AllocationContext("id2", "al_id2", {"data": "data2"})
        con_list = AllocationContextList(self.nulllogger)
        con_list.append(con1)
        con_list.append(con2)

        self.assertEqual(con_list[0].resource_id, "id1")
        self.assertEqual(con_list[1].alloc_id, "al_id2")
        con_list[0] = con2
        self.assertEqual(con_list[0].resource_id, "id2")

        with self.assertRaises(IndexError):
            er = con_list[2]
        with self.assertRaises(IndexError):
            er = con_list[-1]
        with self.assertRaises(IndexError):
            con_list[-1] = "test"
        with self.assertRaises(IndexError):
            con_list[3] = "test"

        with self.assertRaises(TypeError):
            er = con_list["test"]
        with self.assertRaises(TypeError):
            con_list["test"] = "test"

    def test_open_dut_connections(self):
        con_list = AllocationContextList(self.nulllogger)
        # Setup mocked duts
        d1 = mock.MagicMock()
        d1.start_dut_thread = mock.MagicMock()
        d1.start_dut_thread.return_value = "ok"
        d1.open_dut = mock.MagicMock()
        d1.open_dut.return_value = "ok"
        d1.close_dut = mock.MagicMock()
        d1.close_connection = mock.MagicMock()
        d2 = mock.MagicMock()
        d2.start_dut_thread = mock.MagicMock()
        d2.start_dut_thread.side_effect = [DutConnectionError]
        d2.open_dut = mock.MagicMock()
        d2.open_dut.return_value = "ok"
        d2.close_dut = mock.MagicMock()
        d2.close_connection = mock.MagicMock()

        con_list.duts = [d1]
        con_list.open_dut_connections()
        d1.start_dut_thread.assert_called()
        d1.open_dut.assert_called()

        con_list.duts.append(d2)
        with self.assertRaises(DutConnectionError):
            con_list.open_dut_connections()
        d2.start_dut_thread.assert_called()
        d2.close_dut.assert_called()
        d2.close_connection.assert_called()

    @mock.patch("icedtea_lib.AllocationContext.os.path.isfile")
    @mock.patch("icedtea_lib.AllocationContext.AllocationContextList.get_build")
    def test_check_flashing_need(self, mock_get_build, mock_isfile):
        con_list = AllocationContextList(self.nulllogger)
        mock_get_build.return_value = "test_name.bin"
        mock_isfile.return_value = True
        self.assertTrue(con_list.check_flashing_need("hardware", "test_build", False))
        mock_get_build.return_value = "test_name.hex"
        self.assertTrue(con_list.check_flashing_need("hardware", "test_build", False))
        mock_get_build.return_value = "test_name"
        self.assertFalse(con_list.check_flashing_need("hardware", "test_build", False))

        self.assertTrue(con_list.check_flashing_need("hardware", "test_build", True))

        mock_isfile.return_value = False
        with self.assertRaises(ResourceInitError):
            con_list.check_flashing_need("hardware", "test_build", False)


if __name__ == '__main__':
    unittest.main()