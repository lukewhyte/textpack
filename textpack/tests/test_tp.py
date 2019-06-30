import unittest
import json

from textpack import tp


class TestTextPack(unittest.TestCase):
    def test_build_group_index(self):
        cl_vehicles = tp.read_csv('./textpack/tests/craigslistVehicles.csv', ['manufacturer', 'make'])
        cl_vehicles.build_group_lookup()

        expected = 'toyotacamry'
        result = cl_vehicles.group_lookup['toyotacamry dx v6']

        self.assertEqual(expected, result)

    def test_add_grouped_column_to_data(self):
        cl_vehicles = tp.read_csv('./textpack/tests/craigslistVehicles.csv', ['manufacturer', 'make'])

        cl_vehicles.build_group_lookup()
        cl_vehicles.add_grouped_column_to_data()

        expected = 443405
        result = cl_vehicles.df['textpackGrouper'].shape[0]

        self.assertEqual(expected, result)

    def test_export_json(self):
        cl_vehicles = tp.read_csv('./textpack/tests/craigslistVehicles.csv', ['manufacturer', 'make'])

        cl_vehicles.run()

        expected = 'https://youngstown.craigslist.org/ctd/d/youngstown-2018-kia-forte-lx-sedan-4d/6886405952.html'
        result = json.loads(cl_vehicles.export_json())['url']['439513']

        self.assertEqual(expected, result)
