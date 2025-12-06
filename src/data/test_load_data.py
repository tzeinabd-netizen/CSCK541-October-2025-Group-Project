"""
Test script to verify loading of city and country names from data files.
"""

from data.data_loader import LoadCities, LoadCountries  
  
if __name__ == "__main__":  
    countries = LoadCountries()  
    print("Country Names:")  
    for c in countries:  
        print(c)  
  
    print("\nCity Names:")  
    cities = LoadCities()  
    for city in cities:  
        print(city)