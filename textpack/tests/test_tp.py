import unittest

from textpack import tp


class TestTextPack(unittest.TestCase):
    def test_build_group_index(self):
        cl_vehicles = tp.read_csv('./textpack/tests/craigslistVehicles.csv', ['manufacturer', 'make'])
        cl_vehicles.build_group_lookup()

        expected = 'toyotacamry'
        result = cl_vehicles.group_lookup['toyotacamry dx v6']

        self.assertEqual(expected, result)
