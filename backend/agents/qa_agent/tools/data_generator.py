# backend/agents/qa_agent/tools/data_generator.py
"""
Generate test data for various scenarios
"""
import json
import random
import string
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TestDataGenerator:
    """Generate mock test data for testing"""
    
    def __init__(self):
        self.faker = None
        try:
            from faker import Faker
            self.faker = Faker()
        except ImportError:
            logger.warning("Faker not installed, using basic data generation")
    
    async def generate_test_data(self, schema: Dict, count: int = 10) -> Dict[str, List[Dict]]:
        """
        Generate test data based on schema
        
        Args:
            schema: Data schema with field definitions
            count: Number of records to generate
            
        Returns:
            Dictionary with generated data by entity
        """
        data = {}
        
        for entity_name, entity_schema in schema.items():
            data[entity_name] = []
            for _ in range(count):
                record = await self._generate_record(entity_schema)
                data[entity_name].append(record)
        
        return data
    
    async def _generate_record(self, schema: Dict) -> Dict:
        """Generate a single record based on schema"""
        record = {}
        
        for field_name, field_type in schema.items():
            record[field_name] = await self._generate_field_value(field_name, field_type)
        
        return record
    
    async def _generate_field_value(self, field_name: str, field_type: str) -> Any:
        """Generate value for a field based on its type"""
        
        # String types
        if field_type in ["string", "str", "text"]:
            return await self._generate_string(field_name)
        
        # Number types
        elif field_type in ["integer", "int", "number", "float"]:
            return random.randint(1, 1000)
        
        # Boolean
        elif field_type in ["boolean", "bool"]:
            return random.choice([True, False])
        
        # Date/Time
        elif field_type in ["date", "datetime", "timestamp"]:
            return (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        
        # Email
        elif "email" in field_name.lower():
            return f"test_{random.randint(1, 1000)}@example.com"
        
        # UUID
        elif field_type == "uuid":
            return f"test-uuid-{random.randint(1, 10000)}"
        
        # Foreign key reference
        elif field_type.startswith("reference:"):
            ref_table = field_type.split(":")[1]
            return random.randint(1, 100)
        
        # List/Array
        elif field_type.startswith("list["):
            inner_type = field_type[5:-1]
            return [await self._generate_field_value(field_name, inner_type) for _ in range(random.randint(1, 5))]
        
        # Default
        else:
            return f"test_{field_name}_{random.randint(1, 100)}"
    
    async def _generate_string(self, field_name: str) -> str:
        """Generate string values based on field name"""
        if self.faker:
            if "name" in field_name.lower():
                return self.faker.name()
            elif "email" in field_name.lower():
                return self.faker.email()
            elif "address" in field_name.lower():
                return self.faker.address()
            elif "phone" in field_name.lower():
                return self.faker.phone_number()
            elif "description" in field_name.lower():
                return self.faker.sentence()
            else:
                return self.faker.word()
        else:
            return f"test_{field_name}_{random.randint(1, 100)}"
    
    async def generate_edge_cases(self, schema: Dict) -> Dict[str, List[Dict]]:
        """Generate edge case test data"""
        edge_cases = {
            "empty": {},
            "null_values": {},
            "max_length": {},
            "invalid_types": {}
        }
        
        for entity_name, entity_schema in schema.items():
            # Empty record
            edge_cases["empty"][entity_name] = {}
            
            # Null values
            edge_cases["null_values"][entity_name] = {
                field: None for field in entity_schema.keys()
            }
            
            # Max length strings
            edge_cases["max_length"][entity_name] = {}
            for field_name, field_type in entity_schema.items():
                if field_type == "string":
                    edge_cases["max_length"][entity_name][field_name] = "A" * 1000
                else:
                    edge_cases["max_length"][entity_name][field_name] = await self._generate_field_value(field_name, field_type)
            
            # Invalid types
            edge_cases["invalid_types"][entity_name] = {}
            for field_name, field_type in entity_schema.items():
                if field_type == "string":
                    edge_cases["invalid_types"][entity_name][field_name] = 12345
                elif field_type == "integer":
                    edge_cases["invalid_types"][entity_name][field_name] = "not_a_number"
                elif field_type == "boolean":
                    edge_cases["invalid_types"][entity_name][field_name] = "not_a_boolean"
        
        return edge_cases
    
    async def generate_api_fixtures(self, endpoints: List[Dict]) -> Dict[str, Any]:
        """Generate API request/response fixtures"""
        fixtures = {}
        
        for endpoint in endpoints:
            method = endpoint.get("method", "GET")
            path = endpoint.get("path", "/")
            
            fixtures[f"{method}_{path.replace('/', '_')}"] = {
                "request": {
                    "method": method,
                    "path": path,
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer test-token"
                    },
                    "body": await self._generate_request_body(endpoint.get("schema", {}))
                },
                "response": {
                    "status_code": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": await self._generate_response_body(endpoint.get("response_schema", {}))
                }
            }
        
        return fixtures
    
    async def _generate_request_body(self, schema: Dict) -> Dict:
        """Generate request body based on schema"""
        if not schema:
            return {}
        
        return await self._generate_record(schema)
    
    async def _generate_response_body(self, schema: Dict) -> Dict:
        """Generate response body based on schema"""
        if not schema:
            return {"data": "mock_response"}
        
        return await self._generate_record(schema)
