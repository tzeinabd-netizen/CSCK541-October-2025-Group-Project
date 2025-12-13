"""
Unit tests for functions in the module data_loader
They test that the units of code for loading countries and cities
from the csv file are functioning.
"""


import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from src.data.data_loader import LoadCountries, LoadCities


class TestDataLoader(unittest.TestCase):

    def test_load_countries(self):
        """
        Test the LoadCountries function from csv
        """
        result = LoadCountries()
        country_list_reference = ["United States",
                                  "United Kingdom",
                                  "France",
                                  "Germany",
                                  "Japan",
                                  "Australia",
                                  "Canada",
                                  "India",
                                  "United Arab Emirates",
                                  "Qatar",
                                  "Saudi Arabia",
                                  "Singapore",
                                  "Hong Kong",
                                  "Thailand",
                                  "Malaysia",
                                  "Indonesia"]

        if len(result) != len(country_list_reference):
            self.assertTrue(False)
            return

        for index, country in enumerate(result):
            self.assertEqual(country, country_list_reference[index])

    def test_load_cities(self):
        """
        Test the LoadCities function from csv
        """
        result = LoadCities()
        city_list_reference = ["New York",
                               "Los Angeles",
                               "Chicago",
                               "Houston",
                               "Phoenix",
                               "London",
                               "Manchester",
                               "Birmingham",
                               "Glasgow",
                               "Liverpool",
                               "Paris",
                               "Lyon",
                               "Marseille",
                               "Toulouse",
                               "Nice",
                               "Berlin",
                               "Munich",
                               "Frankfurt",
                               "Hamburg",
                               "Cologne",
                               "Tokyo",
                               "Osaka",
                               "Nagoya",
                               "Sapporo",
                               "Fukuoka",
                               "Sydney",
                               "Melbourne",
                               "Brisbane",
                               "Perth",
                               "Adelaide",
                               "Toronto",
                               "Vancouver",
                               "Montreal",
                               "Calgary",
                               "Ottawa",
                               "Mumbai",
                               "Delhi",
                               "Bengaluru",
                               "Chennai",
                               "Kolkata",
                               "Dubai",
                               "Abu Dhabi",
                               "Sharjah",
                               "Doha",
                               "Riyadh",
                               "Singapore",
                               "Hong Kong",
                               "Bangkok",
                               "Kuala Lumpur",
                               "Jakarta", ]

        if len(result) != len(city_list_reference):
            self.assertTrue(False)
            return

        for index, city in enumerate(result):
            self.assertEqual(city, city_list_reference[index])


if __name__ == '__main__':
    unittest.main(verbosity=2)  # Give detailed feedback
