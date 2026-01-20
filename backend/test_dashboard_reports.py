#!/usr/bin/env python3
"""
Sample API calls for testing Dashboard and Reports endpoints
"""

import requests
import json
from datetime import date, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMGU3YWY3Ny0wN2UzLTQ0OTItYjFlNy02MjI4YTkyNGI4MGEiLCJleHAiOjE3NjkwMjU1NDd9.fJMXSKNhi1AaDXhpJUPUvBNol907kk-iFO0UZMV4n3k"  # Get this from /auth/login

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def test_dashboard():
    """Test all dashboard endpoints"""
    print("\n" + "="*80)
    print("DASHBOARD TESTS")
    print("="*80)
    
    # 1. Main dashboard
    print("\n1. GET /dashboard/")
    response = requests.get(f"{BASE_URL}/dashboard/", headers=HEADERS)
    print(json.dumps(response.json(), indent=2))
    
    # 2. Inventory health
    print("\n2. GET /dashboard/inventory-health")
    response = requests.get(f"{BASE_URL}/dashboard/inventory-health", headers=HEADERS)
    print(json.dumps(response.json(), indent=2))
    
    # 3. Stock distribution
    print("\n3. GET /dashboard/stock-distribution")
    response = requests.get(f"{BASE_URL}/dashboard/stock-distribution", headers=HEADERS)
    print(json.dumps(response.json(), indent=2))


def test_reports():
    """Test all reports endpoints"""
    print("\n" + "="*80)
    print("REPORTS TESTS")
    print("="*80)
    
    # 1. Inventory report
    print("\n1. GET /reports/inventory (JSON format)")
    response = requests.get(
        f"{BASE_URL}/reports/inventory?format=json",
        headers=HEADERS
    )
    print(json.dumps(response.json(), indent=2))
    
    # 2. Consumption report (last 30 days)
    print("\n2. GET /reports/consumption (last 30 days)")
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    response = requests.get(
        f"{BASE_URL}/reports/consumption?start_date={start_date}&end_date={end_date}",
        headers=HEADERS
    )
    print(json.dumps(response.json(), indent=2))
    
    # 3. Financial report
    print("\n3. GET /reports/financial")
    response = requests.get(
        f"{BASE_URL}/reports/financial",
        headers=HEADERS
    )
    print(json.dumps(response.json(), indent=2))
    
    # 4. ABC analysis
    print("\n4. GET /reports/abc-analysis")
    response = requests.get(
        f"{BASE_URL}/reports/abc-analysis",
        headers=HEADERS
    )
    print(json.dumps(response.json(), indent=2))
    
    # 5. VED analysis
    print("\n5. GET /reports/ved-analysis")
    response = requests.get(
        f"{BASE_URL}/reports/ved-analysis",
        headers=HEADERS
    )
    print(json.dumps(response.json(), indent=2))
    
    # 6. Expiry report (90 days)
    print("\n6. GET /reports/expiry (90 days threshold)")
    response = requests.get(
        f"{BASE_URL}/reports/expiry?days=90",
        headers=HEADERS
    )
    print(json.dumps(response.json(), indent=2))
    
    # 7. Expiry report (30 days) - urgent
    print("\n7. GET /reports/expiry (30 days threshold - urgent)")
    response = requests.get(
        f"{BASE_URL}/reports/expiry?days=30",
        headers=HEADERS
    )
    print(json.dumps(response.json(), indent=2))
    
    # 8. Stock valuation
    print("\n8. GET /reports/stock-valuation")
    response = requests.get(
        f"{BASE_URL}/reports/stock-valuation",
        headers=HEADERS
    )
    print(json.dumps(response.json(), indent=2))


def test_admin_multi_hospital():
    """Test accessing other hospital data as admin"""
    print("\n" + "="*80)
    print("ADMIN MULTI-HOSPITAL ACCESS TESTS")
    print("="*80)
    
    # Get dashboard for specific hospital
    hospital_id = "HOSP002"  # Change to actual hospital ID
    
    print(f"\n1. GET /dashboard/ for hospital {hospital_id}")
    response = requests.get(
        f"{BASE_URL}/dashboard/?hospital_id={hospital_id}",
        headers=HEADERS
    )
    print(json.dumps(response.json(), indent=2))
    
    print(f"\n2. GET /reports/inventory for hospital {hospital_id}")
    response = requests.get(
        f"{BASE_URL}/reports/inventory?hospital_id={hospital_id}&format=json",
        headers=HEADERS
    )
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    print("\n" + "="*80)
    print("AUSHADHI DASHBOARD & REPORTS API - TEST SCRIPT")
    print("="*80)
    
    print("\n⚠️  Before running these tests:")
    print("1. Update TOKEN variable with your JWT token")
    print("2. Make sure the API server is running on http://localhost:8000")
    print("3. Ensure you have inventory data in the database")
    print("\nYou can get a token by:")
    print("  POST /api/v1/auth/login?email=admin@gmail.com&password=admin@123")
    
    print("\n" + "-"*80)
    print("Ready to test? Update the TOKEN variable and uncomment the functions below")
    print("-"*80)
    
    # Uncomment to run tests
    test_dashboard()
    test_reports()
    test_admin_multi_hospital()
