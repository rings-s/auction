#!/usr/bin/env python3
"""
Test authentication with provided user credentials
"""
import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import CustomUser
import json

def test_user_credentials():
    """Test user authentication credentials"""
    print("🔐 Testing User Authentication")
    print("=" * 50)
    
    # Test credentials provided by user
    test_users = [
        {"email": "admin@email.com", "password": "admin12345"},
        {"email": "rings9619@gmail.com", "password": "Africa123"},
        {"email": "rings9619@gmail.com", "password": "africa123"},
    ]
    
    for user_data in test_users:
        print(f"\n🧪 Testing: {user_data['email']} with password: {user_data['password']}")
        
        # Test Django authenticate
        user = authenticate(username=user_data['email'], password=user_data['password'])
        
        if user:
            print(f"✅ Django authentication successful!")
            print(f"   - User: {user.get_full_name()}")
            print(f"   - Role: {user.role}")
            print(f"   - Verified: {user.is_verified}")
            print(f"   - Active: {user.is_active}")
            
            # Store successful credentials for Django auth
            return {
                'email': user_data['email'],
                'password': user_data['password'],
                'user_info': {
                    'id': user.id,
                    'role': user.role,
                    'name': user.get_full_name()
                }
            }
        else:
            print(f"❌ Django authentication failed")
            
            # Check if user exists
            try:
                db_user = CustomUser.objects.get(email=user_data['email'])
                print(f"   - User exists in database")
                print(f"   - User active: {db_user.is_active}")
                print(f"   - User verified: {db_user.is_verified}")
            except CustomUser.DoesNotExist:
                print(f"   - User does not exist in database")
    
    return None

def test_create_additional_users():
    """Create additional test users if needed"""
    print("\n👥 Creating Additional Test Users")
    print("=" * 50)
    
    additional_users = [
        {
            'email': 'test.admin@auction.com',
            'password': 'TestAdmin123!',
            'first_name': 'Ahmed',
            'last_name': 'المدير',
            'role': 'administrator',
        },
        {
            'email': 'test.auctioneer@auction.com', 
            'password': 'TestAuctioneer123!',
            'first_name': 'محمد',
            'last_name': 'المزايد',
            'role': 'auctioneer',
        }
    ]
    
    created_users = []
    
    for user_data in additional_users:
        try:
            user, created = CustomUser.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'], 
                    'role': user_data['role'],
                    'is_verified': True,
                    'is_active': True,
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                print(f"✅ Created user: {user.email} (role: {user.role})")
                created_users.append({
                    'email': user_data['email'],
                    'password': user_data['password'],
                    'role': user_data['role']
                })
            else:
                print(f"⚠️  User already exists: {user.email}")
                
        except Exception as e:
            print(f"❌ Error creating user {user_data['email']}: {e}")
    
    return created_users

if __name__ == "__main__":
    print("🚀 Starting Authentication Tests")
    print("=" * 60)
    
    # Test existing user credentials
    successful_auth = test_user_credentials()
    
    if successful_auth:
        print(f"\n🎉 Successfully authenticated: {successful_auth['email']}")
        
        # Save successful credentials to file
        with open('successful_auth.json', 'w') as f:
            json.dump(successful_auth, f, indent=2)
        print("💾 Saved successful authentication details to 'successful_auth.json'")
    
    # Create additional test users
    new_users = test_create_additional_users()
    
    if new_users:
        print(f"\n📝 Created {len(new_users)} new test users")
        
        # Save new user credentials
        with open('new_test_users.json', 'w') as f:
            json.dump(new_users, f, indent=2)
        print("💾 Saved new user credentials to 'new_test_users.json'")
    
    print("\n✅ Authentication tests completed!")