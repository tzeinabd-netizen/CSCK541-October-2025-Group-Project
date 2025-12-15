"""
Unit tests for functions in the module data_loader
They test that the units of code for loading countries and cities
from the csv file are functioning.
"""


import unittest
import os
import sys

# Ensure src/ is on path so local imports work when running module directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_loader import LoadCountries, LoadCities


class TestDataLoader(unittest.TestCase):

    def test_load_countries(self):
        """
        Test the LoadCountries function from csv
        This test should pass.
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

        self.assertEqual (result, country_list_reference)

    def test_load_countries_fail(self):
        """
        Test the LoadCountries function from csv.
        This test should fail as there is
        a country missing.
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
                                  "Malaysia"] # Country removed

        self.assertEqual(result, country_list_reference)

    def test_load_cities(self):
        """
        Test the LoadCities function from csv
        This test should pass.
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

        self.assertEqual(result, city_list_reference)


    def test_load_cities_fail(self):
        """
        Test the LoadCities function from csv
        This test should fail as there is
        an error in a city name.
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
                               "Riyad", #h removed from city name
                               "Singapore",
                               "Hong Kong",
                               "Bangkok",
                               "Kuala Lumpur",
                               "Jakarta", ]

        self.assertEqual(result, city_list_reference)

if __name__ == '__main__':
    unittest.main(verbosity=2)  # Give detailed feedback
