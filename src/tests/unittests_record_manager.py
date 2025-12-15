"""
Unit tests for RecordManager class
"""

import unittest
import os
import sys
from datetime import datetime

# Ensure src/ is on path so local imports work when running module directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.record.record_manager import RecordManager


class TestRecordManager(unittest.TestCase):
    """Test cases for RecordManager"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_file = "tests/test_records.jsonl"
        self.manager = RecordManager(self.test_file)

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_create_client_record(self):
        """Test creating a client record"""
        record = self.manager.CreateClient(
            name="John Doe",
            address_line1="123 Main St",
            address_line2="Apt 4B",
            address_line3="",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
            phone_number="555-1234"
        )

        self.assertIsNotNone(record)
        self.assertEqual(record['Type'], 'Client')
        self.assertEqual(record['Name'], 'John Doe')
        self.assertEqual(record['City'], 'New York')
        self.assertEqual(record['Phone_Number'], '555-1234')
        self.assertIn('ID', record)
        self.assertEqual(record['ID'], 1)


    def test_create_airline_record(self):
        """Test creating an airline record"""
        record = self.manager.CreateAirline("Delta Airlines")

        self.assertIsNotNone(record)
        self.assertEqual(record['Type'], 'Airline')
        self.assertEqual(record['Company_Name'], 'Delta Airlines')
        self.assertIn('ID', record)
        self.assertEqual(record['ID'], 1)

    def test_create_flight_record(self):
        """Test creating a flight record"""
        flight_date = datetime(2024, 12, 25, 10, 0, 0)
        record = self.manager.CreateFlight(
            client_id=1,
            airline_id=1,
            date=flight_date,
            start_city="New York",
            end_city="Los Angeles"
        )

        self.assertIsNotNone(record)
        self.assertEqual(record['Type'], 'Flight')
        self.assertEqual(record['Client_ID'], 1)
        self.assertEqual(record['Airline_ID'], 1)
        self.assertIsInstance(record['Date'], datetime)
        self.assertEqual(record['Start_City'], 'New York')
        self.assertEqual(record['End_City'], 'Los Angeles')

    # READ tests
    def test_get_record_by_id(self):
        """Test retrieving a record by ID"""
        # Create a client record
        created_client = self.manager.CreateClient(
            name="Jane Smith",
            address_line1="456 Oak Ave",
            address_line2="",
            address_line3="",
            city="Los Angeles",
            state="CA",
            zip_code="90001",
            country="USA",
            phone_number="555-5678"
        )

        # Retrieve the client by ID
        retrieved_client = self.manager.GetRecordById(created_client['ID'], 'Client')

        self.assertIsNotNone(retrieved_client)
        self.assertEqual(retrieved_client['ID'], created_client['ID'])
        self.assertEqual(retrieved_client['Name'], 'Jane Smith')
        self.assertEqual(retrieved_client['Type'], 'Client')

        # Create an airline record
        created_airline = self.manager.CreateAirline("United Airlines")

        # Retrieve the airline by ID
        retrieved_airline = self.manager.GetRecordById(created_airline['ID'], 'Airline')

        self.assertIsNotNone(retrieved_airline)
        self.assertEqual(retrieved_airline['ID'], created_airline['ID'])
        self.assertEqual(retrieved_airline['Company_Name'], 'United Airlines')

        # Test retrieving non-existent record
        non_existent = self.manager.GetRecordById(999, 'Client')
        self.assertIsNone(non_existent)

    def test_get_all_records(self):
        """Test retrieving all records"""
        # Initially should be empty
        all_records = self.manager.GetAllRecords()
        self.assertEqual(len(all_records), 0)

        # Create multiple records
        self.manager.CreateClient(
            name="Client 1",
            address_line1="Address 1",
            address_line2="",
            address_line3="",
            city="City 1",
            state="ST",
            zip_code="11111",
            country="Country 1",
            phone_number="555-0001"
        )

        self.manager.CreateClient(
            name="Client 2",
            address_line1="Address 2",
            address_line2="",
            address_line3="",
            city="City 2",
            state="ST",
            zip_code="22222",
            country="Country 2",
            phone_number="555-0002"
        )

        self.manager.CreateAirline("Airline 1")
        self.manager.CreateAirline("Airline 2")

        self.manager.CreateFlight(1, 1, datetime(2024, 12, 25, 10, 0), "NYC", "LA")

        # Get all records
        all_records = self.manager.GetAllRecords()
        self.assertEqual(len(all_records), 5)

        # Get records filtered by type
        clients = self.manager.GetAllRecords('Client')
        self.assertEqual(len(clients), 2)

        airlines = self.manager.GetAllRecords('Airline')
        self.assertEqual(len(airlines), 2)

        flights = self.manager.GetAllRecords('Flight')
        self.assertEqual(len(flights), 1)

    def test_search_records(self):
        """Test searching records"""
        # Create test data
        self.manager.CreateClient(
            name="John Doe",
            address_line1="123 Main St",
            address_line2="",
            address_line3="",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
            phone_number="555-1234"
        )

        self.manager.CreateClient(
            name="Jane Smith",
            address_line1="456 Oak Ave",
            address_line2="",
            address_line3="",
            city="Los Angeles",
            state="CA",
            zip_code="90001",
            country="USA",
            phone_number="555-5678"
        )

        self.manager.CreateAirline("Delta Airlines")
        self.manager.CreateAirline("United Airlines")

        # Search by name
        results = self.manager.SearchRecords("John")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['Name'], 'John Doe')

        # Search by city
        results = self.manager.SearchRecords("Los Angeles")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['City'], 'Los Angeles')

        # Search case-insensitive
        results = self.manager.SearchRecords("delta")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['Company_Name'], 'Delta Airlines')

        # Search with type filter
        results = self.manager.SearchRecords("Airlines", record_type='Airline')
        self.assertEqual(len(results), 2)
        for record in results:
            self.assertEqual(record['Type'], 'Airline')

        # Search by ID
        results = self.manager.SearchRecords("1")
        self.assertGreater(len(results), 0)

        # Search with no results
        results = self.manager.SearchRecords("NonExistent")
        self.assertEqual(len(results), 0)

    # UPDATE tests
    def test_update_client_record(self):
        """Test updating a client record"""
        # Create a client
        client = self.manager.CreateClient(
            name="Old Name",
            address_line1="Old Address",
            address_line2="",
            address_line3="",
            city="Old City",
            state="OS",
            zip_code="11111",
            country="Old Country",
            phone_number="555-0000"
        )

        # Update single field
        updated = self.manager.UpdateClient(client['ID'], Name="New Name")
        self.assertIsNotNone(updated)
        self.assertEqual(updated['Name'], 'New Name')
        self.assertEqual(updated['City'], 'Old City')  # Other fields unchanged

        # Update multiple fields
        updated = self.manager.UpdateClient(
            client['ID'],
            City="New City",
            Phone_Number="555-9999",
            Address_Line_1="New Address"
        )
        self.assertEqual(updated['City'], 'New City')
        self.assertEqual(updated['Phone_Number'], '555-9999')
        self.assertEqual(updated['Address_Line_1'], 'New Address')
        self.assertEqual(updated['Name'], 'New Name')  # Previously updated field

        # Try to update non-existent record
        result = self.manager.UpdateClient(999, Name="Test")
        self.assertIsNone(result)

    def test_update_airline_record(self):
        """Test updating an airline record"""
        # Create an airline
        airline = self.manager.CreateAirline("Old Airline Name")

        # Update the airline
        updated = self.manager.UpdateAirline(airline['ID'], "New Airline Name")
        self.assertIsNotNone(updated)
        self.assertEqual(updated['Company_Name'], 'New Airline Name')
        self.assertEqual(updated['ID'], airline['ID'])

        # Try to update non-existent record
        result = self.manager.UpdateAirline(999, "Test Airline")
        self.assertIsNone(result)

    def test_update_flight_record(self):
        """Test updating a flight record"""
        # Create a flight
        old_date = datetime(2024, 12, 25, 10, 0, 0)
        self.manager.CreateFlight(
            client_id=1,
            airline_id=1,
            date=old_date,
            start_city="New York",
            end_city="Los Angeles"
        )

        # Update single field
        new_date = datetime(2024, 12, 26, 14, 30, 0)
        updated = self.manager.UpdateFlight(1, 1, Date=new_date)
        self.assertIsNotNone(updated)
        self.assertEqual(updated['Date'], new_date)
        self.assertEqual(updated['Start_City'], 'New York')  # Unchanged

        # Update multiple fields
        updated = self.manager.UpdateFlight(
            1, 1,
            Start_City="Boston",
            End_City="San Francisco"
        )
        self.assertEqual(updated['Start_City'], 'Boston')
        self.assertEqual(updated['End_City'], 'San Francisco')
        self.assertEqual(updated['Date'], new_date)  # Previously updated field

        # Try to update non-existent flight
        result = self.manager.UpdateFlight(999, 999, Start_City="Test")
        self.assertIsNone(result)

    # DELETE tests
    def test_delete_record(self):
        """Test deleting a record"""
        # Create and delete a client
        client = self.manager.CreateClient(
            name="To Delete",
            address_line1="Address",
            address_line2="",
            address_line3="",
            city="City",
            state="ST",
            zip_code="12345",
            country="Country",
            phone_number="555-0000"
        )

        result = self.manager.DeleteRecord(client['ID'], 'Client')
        self.assertTrue(result)

        # Verify it's deleted
        retrieved = self.manager.GetRecordById(client['ID'], 'Client')
        self.assertIsNone(retrieved)

        # Create and delete an airline
        airline = self.manager.CreateAirline("To Delete Airlines")
        result = self.manager.DeleteRecord(airline['ID'], 'Airline')
        self.assertTrue(result)

        # Verify it's deleted
        retrieved = self.manager.GetRecordById(airline['ID'], 'Airline')
        self.assertIsNone(retrieved)

        # Try to delete non-existent record
        result = self.manager.DeleteRecord(999, 'Client')
        self.assertFalse(result)

    def test_delete_flight_record(self):
        """Test deleting a flight record"""
        # Create a flight
        self.manager.CreateFlight(
            client_id=1,
            airline_id=1,
            date=datetime(2024, 12, 25, 10, 0, 0),
            start_city="New York",
            end_city="Los Angeles"
        )

        # Verify it exists
        flights = self.manager.GetAllRecords('Flight')
        self.assertEqual(len(flights), 1)

        # Delete the flight
        result = self.manager.DeleteFlight(1, 1)
        self.assertTrue(result)

        # Verify it's deleted
        flights = self.manager.GetAllRecords('Flight')
        self.assertEqual(len(flights), 0)

        # Try to delete non-existent flight
        result = self.manager.DeleteFlight(999, 999)
        self.assertFalse(result)

    # Edge cases
    def test_generate_unique_ids(self):
        """Test that IDs are unique"""
        # Create multiple clients
        client1 = self.manager.CreateClient(
            name="Client 1",
            address_line1="Address 1",
            address_line2="",
            address_line3="",
            city="City 1",
            state="S1",
            zip_code="11111",
            country="Country 1",
            phone_number="555-0001"
        )

        client2 = self.manager.CreateClient(
            name="Client 2",
            address_line1="Address 2",
            address_line2="",
            address_line3="",
            city="City 2",
            state="S2",
            zip_code="22222",
            country="Country 2",
            phone_number="555-0002"
        )

        client3 = self.manager.CreateClient(
            name="Client 3",
            address_line1="Address 3",
            address_line2="",
            address_line3="",
            city="City 3",
            state="S3",
            zip_code="33333",
            country="Country 3",
            phone_number="555-0003"
        )

        # Check IDs are unique and sequential
        self.assertEqual(client1['ID'], 1)
        self.assertEqual(client2['ID'], 2)
        self.assertEqual(client3['ID'], 3)

        # Create multiple airlines
        airline1 = self.manager.CreateAirline("Airline 1")
        airline2 = self.manager.CreateAirline("Airline 2")

        # Airlines should have their own ID sequence
        self.assertEqual(airline1['ID'], 1)
        self.assertEqual(airline2['ID'], 2)

        # Delete a client and create a new one
        self.manager.DeleteRecord(client2['ID'], 'Client')
        client4 = self.manager.CreateClient(
            name="Client 4",
            address_line1="Address 4",
            address_line2="",
            address_line3="",
            city="City 4",
            state="S4",
            zip_code="44444",
            country="Country 4",
            phone_number="555-0004"
        )

        # New ID should be 4 (not reusing deleted ID 2)
        self.assertEqual(client4['ID'], 4)

    def test_persistence(self):
        """Test that records persist to file"""
        # Create records
        client = self.manager.CreateClient(
            name="Persist Test",
            address_line1="123 Persist St",
            address_line2="",
            address_line3="",
            city="Persist City",
            state="PS",
            zip_code="99999",
            country="Persist Country",
            phone_number="555-9999"
        )

        airline = self.manager.CreateAirline("Persist Airlines")

        flight_date = datetime(2024, 12, 25, 15, 45, 30)
        flight = self.manager.CreateFlight(
            client_id=client['ID'],
            airline_id=airline['ID'],
            date=flight_date,
            start_city="Start City",
            end_city="End City"
        )

        # Verify file exists
        self.assertTrue(os.path.exists(self.test_file))

        # Create a new manager instance (should load from file)
        new_manager = RecordManager(self.test_file)

        # Verify all records were loaded
        self.assertEqual(len(new_manager.records), 3)

        # Verify client was loaded correctly
        loaded_client = new_manager.GetRecordById(client['ID'], 'Client')
        self.assertIsNotNone(loaded_client)
        self.assertEqual(loaded_client['Name'], 'Persist Test')
        self.assertEqual(loaded_client['City'], 'Persist City')

        # Verify airline was loaded correctly
        loaded_airline = new_manager.GetRecordById(airline['ID'], 'Airline')
        self.assertIsNotNone(loaded_airline)
        self.assertEqual(loaded_airline['Company_Name'], 'Persist Airlines')

        # Verify flight was loaded correctly with datetime
        loaded_flights = new_manager.GetAllRecords('Flight')
        self.assertEqual(len(loaded_flights), 1)
        loaded_flight = loaded_flights[0]
        self.assertEqual(loaded_flight['Client_ID'], client['ID'])
        self.assertEqual(loaded_flight['Airline_ID'], airline['ID'])
        self.assertIsInstance(loaded_flight['Date'], datetime)
        self.assertEqual(loaded_flight['Date'], flight_date)
        self.assertEqual(loaded_flight['Start_City'], 'Start City')
        self.assertEqual(loaded_flight['End_City'], 'End City')


if __name__ == '__main__':
    unittest.main(verbosity=2) # Give detailed feedback