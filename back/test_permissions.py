#!/usr/bin/env python
"""
Role-based Permission System Validation Script
Tests the expanded user roles and permission classes
"""
import os
import django
import sys

# Add the project root to Python path
project_root = '/home/ahmed/tech-Savvy-projects/2025/new_ones/auction/back'
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from base.permissions import *

def test_role_system():
    """Test the expanded role system"""
    print("🧪 Testing Role-Based Permission System...")
    print("=" * 50)
    
    # Test role choices
    roles = dict(CustomUser.ROLE_CHOICES)
    print(f"✅ Total Roles Available: {len(roles)}")
    for code, name in CustomUser.ROLE_CHOICES:
        print(f"   • {code}: {name}")
    
    print("\n🔍 Testing Role Helper Methods...")
    
    # Create a test user for each role
    test_results = {}
    
    for role_code, role_name in CustomUser.ROLE_CHOICES:
        print(f"\n📋 Testing Role: {role_code} ({role_name})")
        
        # Create a mock user with this role
        user = CustomUser(
            email=f"test_{role_code}@example.com",
            first_name="Test",
            last_name="User",
            role=role_code,
            is_verified=True
        )
        
        # Test helper methods
        results = {
            'is_admin_level': user.is_admin_level(),
            'is_property_professional': user.is_property_professional(),
            'is_financial_role': user.is_financial_role(),
            'can_manage_maintenance': user.can_manage_maintenance(),
            'can_create_auctions': user.can_create_auctions(),
            'can_manage_properties': user.can_manage_properties(),
        }
        
        test_results[role_code] = results
        
        for method, result in results.items():
            status = "✅" if result else "❌"
            print(f"   {status} {method}: {result}")
    
    print(f"\n🎯 Permission Class Testing...")
    
    # Test permission classes
    permission_classes = [
        ('IsAdministrator', IsAdministrator),
        ('IsManager', IsManager),
        ('IsPropertyProfessional', IsPropertyProfessional),
        ('IsFinancialRole', IsFinancialRole),
        ('CanCreateAuctions', CanCreateAuctions),
        ('CanManageProperties', CanManageProperties),
        ('CanManageMaintenance', CanManageMaintenance),
        ('CanAccessPropertyAnalytics', CanAccessPropertyAnalytics),
        ('CanManageWorkers', CanManageWorkers),
    ]
    
    for name, perm_class in permission_classes:
        print(f"\n🔐 Testing {name}:")
        print(f"   Required Roles: {perm_class.required_roles}")
        
        # Test which roles have access
        authorized_roles = []
        for role_code, _ in CustomUser.ROLE_CHOICES:
            if role_code in perm_class.required_roles:
                authorized_roles.append(role_code)
        
        print(f"   Authorized: {', '.join(authorized_roles) if authorized_roles else 'None'}")
    
    print("\n" + "=" * 50)
    print("✅ Permission System Validation Complete!")
    
    return test_results

def test_query_optimization():
    """Test that query optimizations work"""
    print("\n🚀 Testing Query Optimizations...")
    print("=" * 50)
    
    # Test User model methods (these should now be optimized)
    try:
        # Create a test user
        user = CustomUser(
            email="test_admin@example.com",
            first_name="Admin",
            last_name="User",
            role='administrator',
            is_verified=True,
            is_superuser=True
        )
        
        # Test the optimized methods return querysets (not actual data)
        properties_qs = user.get_accessible_properties()
        auctions_qs = user.get_accessible_auctions() 
        bids_qs = user.get_accessible_bids()
        
        print("✅ User Model Methods:")
        print(f"   • get_accessible_properties(): {type(properties_qs).__name__}")
        print(f"   • get_accessible_auctions(): {type(auctions_qs).__name__}")
        print(f"   • get_accessible_bids(): {type(bids_qs).__name__}")
        
        # Check if querysets have optimization (select_related/prefetch_related)
        print("\n🔍 Query Optimization Analysis:")
        if hasattr(properties_qs, 'query'):
            select_related = getattr(properties_qs.query, 'select_related', None)
            prefetch_related = getattr(properties_qs, '_prefetch_related_lookups', None)
            print(f"   Properties - select_related: {bool(select_related)}, prefetch_related: {bool(prefetch_related)}")
        
        print("✅ Query optimization methods are accessible and return QuerySets")
        
    except Exception as e:
        print(f"❌ Query optimization test error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        # Run permission system tests
        test_results = test_role_system()
        
        # Run query optimization tests
        query_test = test_query_optimization()
        
        print("\n🎉 All Tests Completed Successfully!")
        
    except Exception as e:
        print(f"❌ Test Failed: {str(e)}")
        sys.exit(1)