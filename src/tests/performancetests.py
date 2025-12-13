"""  
Performance tests for the data loader and record manager modules.
They test the functions LoadCounties, LoadCities and the load capacity
of adding new clients to the record manager.

"""  
from src.data.data_loader import LoadCountries, LoadCities
import os
import sys
import random
from time import process_time
from src.record.record_manager import RecordManager
import string
# Add parent directory to path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def performance_test(function_handle, function_name, *args):
    """
    A function that tests execution time.
    Function_name is used so that each function can be called.
    """
    start_time = (process_time())
    function_handle(*args)
    end_time = (process_time())
    print("Time elapsed for {name} : {time}".format(
        name=function_name, time=(end_time-start_time)))


def load_capacity_test(amount_of_clients):
    """
    Test load capacity of the record manager.
    It creates random clients.
    """
    test_file = "tests_records/test_records.jsonl"
    manager = RecordManager(test_file)
    for i in range(amount_of_clients):
        manager.CreateClient(
            name="".join(random.choices(string.ascii_lowercase, k=5)),
            address_line1="123 Main St",
            address_line2="Apt 4B",
            address_line3="",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
            phone_number="555-1234"
        )

def main():
    """
    Call performance tests
    """

    performance_test(LoadCountries, "function LoadCountries")
    performance_test(LoadCities, "function LoadCities")
    performance_test(load_capacity_test, "load capacity test",1000) #Generate 1000 random clients



if __name__ == '__main__':
    main()



