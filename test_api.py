#!/usr/bin/env python3
"""
Test script for Measurement API
"""

import requests
import json
from datetime import datetime
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoints"""
    print("\n=== Testing Health Endpoints ===")
    
    # Health check
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Database health check
    response = requests.get(f"{BASE_URL}/health/db")
    print(f"\nDatabase health check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_create_measurement():
    """Test creating a measurement"""
    print("\n=== Testing Create Measurement ===")
    
    measurement_data = {
        "vehicle_id": str(uuid4()),
        "area_id": str(uuid4()),
        "local_time": datetime.now().isoformat(),
        "measured_at": int(datetime.now().timestamp()),
        "data_path": "/data/measurements/2024/01/measurement_001"
    }
    
    # Bulk-at-root: wrap single measurement in list
    response = requests.post(
        f"{BASE_URL}/measurements/",
        json={"measurements": [measurement_data]}
    )
    
    print(f"Create measurement: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 201:
        data = response.json().get("data")
        if isinstance(data, list) and data:
            return data[0].get("id")
    return None


def test_get_measurement(measurement_id):
    """Test getting a measurement by ID"""
    print(f"\n=== Testing Get Measurement (ID: {measurement_id}) ===")
    
    response = requests.get(f"{BASE_URL}/measurements/{measurement_id}")
    
    print(f"Get measurement: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_list_measurements():
    """Test listing measurements"""
    print("\n=== Testing List Measurements ===")
    
    params = {
        "page": 1,
        "per_page": 10
    }
    
    response = requests.get(f"{BASE_URL}/measurements/", params=params)
    
    print(f"List measurements: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_update_measurement(measurement_id):
    """Test updating a measurement"""
    print(f"\n=== Testing Update Measurement (ID: {measurement_id}) ===")
    
    update_data = {
        "data_path": "/data/measurements/2024/01/measurement_001_updated"
    }
    
    response = requests.put(
        f"{BASE_URL}/measurements/{measurement_id}",
        json=update_data
    )
    
    print(f"Update measurement: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_bulk_create():
    """Test bulk creating measurements"""
    print("\n=== Testing Bulk Create Measurements ===")
    
    vehicle_id = str(uuid4())
    area_id = str(uuid4())
    
    measurements = []
    for i in range(3):
        measurements.append({
            "vehicle_id": vehicle_id,
            "area_id": area_id,
            "local_time": datetime.now().isoformat(),
            "measured_at": int(datetime.now().timestamp()) + i,
            "data_path": f"/data/measurements/2024/01/measurement_bulk_{i:03d}"
        })
    
    bulk_data = {
        "measurements": measurements
    }
    
    response = requests.post(
        f"{BASE_URL}/measurements/",
        json=bulk_data
    )
    
    print(f"Bulk create measurements: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_delete_measurement(measurement_id):
    """Test deleting a measurement"""
    print(f"\n=== Testing Delete Measurement (ID: {measurement_id}) ===")
    
    response = requests.delete(f"{BASE_URL}/measurements/{measurement_id}")
    
    print(f"Delete measurement: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def main():
    """Run all tests"""
    print("Starting API tests...")
    
    # Test health endpoints
    test_health()
    
    # Test CRUD operations
    measurement_id = test_create_measurement()
    
    if measurement_id:
        test_get_measurement(measurement_id)
        test_update_measurement(measurement_id)
    
    # Test list
    test_list_measurements()
    
    # Test bulk create
    test_bulk_create()
    
    # Test delete
    if measurement_id:
        test_delete_measurement(measurement_id)
    
    print("\n=== Tests completed ===")


if __name__ == "__main__":
    main()
