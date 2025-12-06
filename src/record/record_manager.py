"""
Record Manager Module
Provides CRUD operations for Client, Airline, and Flight records
"""

import jsonlines
import os
from typing import List, Dict, Optional, Union
from datetime import datetime


class RecordManager:
    """Main class for managing all record operations"""
    
    def __init__(self, file_path: str = "src/record/record.jsonl"):
        """
        Initializes the Record Manager
        
        Args:
            file_path: Path to the JSONL file for storing records
        """
        self.file_path = file_path
        self.records: List[Dict] = []
        self.LoadRecords()
    
    def LoadRecords(self) -> None:
        """Load records from file system if exists"""  
        if os.path.exists(self.file_path):  
            try:  
                with jsonlines.open(self.file_path, 'r') as reader:  
                    self.records = [self.DeserializeRecord(r) for r in reader]  
            except Exception as e:  
                print(f"Error loading records: {e}")  
                self.records = []  
        else:  
            self.records = []
    
    def DeserializeRecord(self, record: Dict) -> Dict:  
        """  
        Convert serialized fields (like Date) into Python types (like datetime).  
        """  
        if record.get("Type") == "Flight":  
            date_val = record.get("Date")  
            if isinstance(date_val, str):  
                try:  
                    record["Date"] = datetime.fromisoformat(date_val)  
                except ValueError:  
                    # If parsing fails, leave it as string  
                    pass  
        return record  
  
    def SerializeRecord(self, record: Dict) -> Dict:  
        """  
        Convert Python types (like datetime) into JSON-serializable values.  
        """  
        record_copy = record.copy()  
        if record_copy.get("Type") == "Flight":  
            date_val = record_copy.get("Date")  
            if isinstance(date_val, datetime):  
                record_copy["Date"] = date_val.isoformat()  
        return record_copy

    def SaveRecords(self) -> bool:  
        """  
        Save records to file system  
          
        Returns:  
            bool: True if successful, False otherwise  
        """  
        try:  
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)  
            serializable_records = [self.SerializeRecord(r) for r in self.records]  
            with jsonlines.open(self.file_path, 'w') as writer:  
                writer.write_all(serializable_records)  
            return True  
        except Exception as e:  
            print(f"Error saving records: {e}")  
            return False
    
    def GenerateId(self, record_type: str) -> int:
        """
        Generate a unique ID for a record by incrementing the highest existing ID of the same type.
        
        Args:
            record_type: Type of record (Client, Airline, Flight)
            
        Returns:
            int: Unique ID
        """
        if not self.records:
            return 1
        
        # Get all IDs of the same type
        same_type_records = [r for r in self.records if r.get('Type') == record_type]
        if not same_type_records:
            return 1
        
        max_id = max(r.get('ID', 0) for r in same_type_records)
        return max_id + 1
    
    # CREATE operations
    def CreateClient(self, name: str, address_line1: str, address_line2: str,
                            address_line3: str, city: str, state: str, zip_code: str,
                            country: str, phone_number: str) -> Dict:
        """
        Create a new client record
        
        Args:
            name: Client name
            address_line1: Address line 1
            address_line2: Address line 2
            address_line3: Address line 3
            city: City
            state: State
            zip_code: Zip code
            country: Country
            phone_number: Phone number
            
        Returns:
            Dict: Created client record
        """
        record = {
            'ID': self.GenerateId('Client'),
            'Type': 'Client',
            'Name': name,
            'Address_Line_1': address_line1,
            'Address_Line_2': address_line2,
            'Address_Line_3': address_line3,
            'City': city,
            'State': state,
            'Zip_Code': zip_code,
            'Country': country,
            'Phone_Number': phone_number
        }
        self.records.append(record)
        self.SaveRecords()
        return record
    
    def CreateAirline(self, company_name: str) -> Dict:
        """
        Create a new airline record
        
        Args:
            company_name: Airline company name
            
        Returns:
            Dict: Created airline record
        """
        record = {
            'ID': self.GenerateId('Airline'),
            'Type': 'Airline',
            'Company_Name': company_name
        }
        self.records.append(record)
        self.SaveRecords()
        return record
    
    def CreateFlight(self, client_id: int, airline_id: int, date: datetime,  
                             start_city: str, end_city: str) -> Dict:  
        """  
        Create a new flight record  
          
        Args:  
            client_id: Client ID  
            airline_id: Airline ID  
            date: Flight date/time as a datetime object  
            start_city: Starting city  
            end_city: Destination city  
              
        Returns:  
            Dict: Created flight record  
        """  
        record = {  
            'Type': 'Flight',  
            'Client_ID': client_id,  
            'Airline_ID': airline_id,  
            'Date': date,
            'Start_City': start_city,  
            'End_City': end_city  
        }  
        self.records.append(record)  
        self.SaveRecords()  
        return record
    
    # READ operations
    def GetRecordById(self, record_id: int, record_type: str) -> Optional[Dict]:
        """
        Get a record by ID and type
        
        Args:
            record_id: Record ID
            record_type: Type of record (Client, Airline)
            
        Returns:
            Optional[Dict]: Record if found, None otherwise
        """
        for record in self.records:
            if record.get('ID') == record_id and record.get('Type') == record_type:
                return record
        return None
    
    def GetAllRecords(self, record_type: Optional[str] = None) -> List[Dict]:
        """
        Get all records, optionally filtered by type
        
        Args:
            record_type: Optional filter by record type
            
        Returns:
            List[Dict]: List of records
        """
        if record_type:
            return [r for r in self.records if r.get('Type') == record_type]
        return self.records.copy()
    
    def SearchRecords(self, search_term: str, record_type: Optional[str] = None) -> List[Dict]:
        """
        Search records by any field containing the search term
        
        Args:
            search_term: Term to search for
            record_type: Optional filter by record type
            
        Returns:
            List[Dict]: List of matching records
        """
        results = []
        search_lower = search_term.lower()
        
        for record in self.records:
            if record_type and record.get('Type') != record_type:
                continue
            
            # Search in all string fields
            for value in record.values():
                if isinstance(value, str) and search_lower in value.lower():
                    results.append(record)
                    break
                elif isinstance(value, int) and search_term == str(value):
                    results.append(record)
                    break
        return results
    
    # UPDATE operations
    def UpdateClient(self, record_id: int, **fields) -> Optional[Dict]:
        """
        Update a client record
        
        Args:
            record_id: Client ID
            **fields: Fields to update in key-value pairs
            
        Returns:
            Optional[Dict]: Updated record if found, None otherwise
        """
        record = self.GetRecordById(record_id, 'Client')
        if record:
            # Update allowed fields
            allowed_fields = ['Name', 'Address_Line_1', 'Address_Line_2', 'Address_Line_3',
                            'City', 'State', 'Zip_Code', 'Country', 'Phone_Number']
            for key, value in fields.items():
                if key in allowed_fields:
                    record[key] = value
            self.SaveRecords()
            return record
        return None
    
    def UpdateAirline(self, record_id: int, company_name: str) -> Optional[Dict]:
        """
        Update an airline record
        
        Args:
            record_id: Airline ID
            company_name: New company name
            
        Returns:
            Optional[Dict]: Updated record if found, None otherwise
        """
        record = self.GetRecordById(record_id, 'Airline')
        if record:
            record['Company_Name'] = company_name
            self.SaveRecords()
            return record
        return None
    
    def UpdateFlight(self, client_id: int, airline_id: int, **fields) -> Optional[Dict]:
        """
        Update a flight record
        
        Args:
            client_id: Client ID
            airline_id: Airline ID
            **fields: Fields to update in key-value pairs
            
        Returns:
            Optional[Dict]: Updated record if found, None otherwise
        """
        # Find flight record by Client_ID and Airline_ID
        for record in self.records:
            if (record.get('Type') == 'Flight' and 
                record.get('Client_ID') == client_id and 
                record.get('Airline_ID') == airline_id):
                
                allowed_fields = ['Date', 'Start_City', 'End_City']
                for key, value in fields.items():
                    if key in allowed_fields:
                        record[key] = value
                self.SaveRecords()
                return record
        return None
    
    # DELETE operations
    def DeleteRecord(self, record_id: int, record_type: str) -> bool:
        """
        Delete a record by ID and type. Cannot delete Flight records using this method as no unique flight ID exists.
        
        Args:
            record_id: Record ID
            record_type: Type of record (Client, Airline)
            
        Returns:
            bool: True if deleted, False if not found
        """
        for i, record in enumerate(self.records):
            if record.get('ID') == record_id and record.get('Type') == record_type:
                self.records.pop(i)
                self.SaveRecords()
                return True
        return False
    
    def DeleteFlight(self, client_id: int, airline_id: int) -> bool:
        """
        Delete a flight record by Client_ID and Airline_ID
        
        Args:
            client_id: Client ID
            airline_id: Airline ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        for i, record in enumerate(self.records):
            if (record.get('Type') == 'Flight' and 
                record.get('Client_ID') == client_id and 
                record.get('Airline_ID') == airline_id):
                self.records.pop(i)
                self.SaveRecords()
                return True
        return False
