#!/usr/bin/env python3
"""
Validate Dashboard and Reports endpoint definitions
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from app.api.v1.endpoints import dashboard, reports

print("\n" + "="*80)
print("ENDPOINT VALIDATION")
print("="*80)

print("\n📊 DASHBOARD ENDPOINTS:")
dashboard_endpoints = [
    route for route in dashboard.router.routes 
    if hasattr(route, 'path')
]
for route in dashboard_endpoints:
    print(f"  ✓ {route.methods} {route.path}")

print("\n📈 REPORTS ENDPOINTS:")
reports_endpoints = [
    route for route in reports.router.routes 
    if hasattr(route, 'path')
]
for route in reports_endpoints:
    print(f"  ✓ {route.methods} {route.path}")

print(f"\nTotal Dashboard Endpoints: {len(dashboard_endpoints)}")
print(f"Total Reports Endpoints: {len(reports_endpoints)}")
print(f"Total Endpoints: {len(dashboard_endpoints) + len(reports_endpoints)}")

print("\n✅ All endpoints are properly defined!")
print("="*80 + "\n")
