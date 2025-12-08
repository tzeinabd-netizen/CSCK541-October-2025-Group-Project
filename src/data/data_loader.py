"""
Example usage in GUI:

from src.data.data_loader import LoadCountries, LoadCities


self.country_list = LoadCountries()  
self.city_list = LoadCities()

then assign these lists to the relevant dropdown menus.
"""


import csv  
import os  
from typing import List, Dict, Optional  
  
  
def GetDataPath(filename: str) -> str:  
    """  
    return the absolute path to a file in the data folder  
    """  
    base_dir = os.path.dirname(os.path.abspath(__file__))  # src/data  
    return os.path.join(base_dir, filename)  
  
  
def LoadCountries() -> List[str]:  
    """  
    this function loads country names from countries.csv in the data folder 
  
    Returns:  
        List of countries as strings: ['United States', 'United Kingdom', ...]  
    """  
    path = GetDataPath("countries.csv")  
    country_names: List[str] = []  
  
    with open(path, mode="r", encoding="utf-8") as f:  
        reader = csv.DictReader(f)  
        for row in reader:  
            country_names.append(row["country_name"])  
    return country_names  
  
  
def LoadCities() -> List[str]:  
    """  
    this function loads city names from cities.csv in the data folder
  
    Returns:  
        List of cities as strings: ['New York', 'Los Angeles', ...]  
    """  
    path = GetDataPath("cities.csv")  
    city_names: List[str] = []  
  
    with open(path, mode="r", encoding="utf-8") as f:  
        reader = csv.DictReader(f)  
        for row in reader:  
            city_names.append(row["city_name"])  
    return city_names


# Aliases for GUI compatibility
load_country_names = LoadCountries
load_city_names = LoadCities

