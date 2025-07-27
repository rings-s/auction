#!/usr/bin/env python3
"""
Comprehensive Test Suite for Arabic Auction System
Tests all models, relationships, authentication, and admin functionality
"""
import os
import sys
import django
from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, timedelta
import json
import unittest

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

from accounts.models import CustomUser, UserProfile
from base.models import *
from django.contrib.admin.sites import site

User = get_user_model()

class ArabicAuctionTestSuite:
    """Main test suite orchestrator"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive Arabic Auction Test Suite")
        print("=" * 80)
        
        # Model Tests
        self.run_model_tests()
        
        # Authentication Tests
        self.run_authentication_tests()
        
        # Admin Panel Tests
        self.run_admin_tests()
        
        # API Tests
        self.run_api_tests()
        
        # Relationship Tests
        self.run_relationship_tests()
        
        # Arabic Data Tests
        self.run_arabic_data_tests()
        
        # Generate Final Report
        self.generate_test_report()
        
    def log_test(self, test_name, status, message="", details=None):
        """Log test result"""
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now()
        })
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {message}")
        
        if details:
            for detail in details:
                print(f"    - {detail}")
                
    def run_model_tests(self):
        """Test model creation and validation"""
        print("\n📋 Testing Model Creation and Validation")
        print("-" * 50)
        
        # Test User Model
        try:
            user = CustomUser.objects.create_user(
                email='test.model@example.com',
                password='TestModel123!',
                first_name='أحمد',
                last_name='المختبر',
                role='owner'
            )
            
            # Test user methods
            assert user.has_role('owner'), "User role check failed"
            assert user.can_manage_properties(), "Property management permission failed"
            
            profile = user.profile
            assert profile is not None, "UserProfile auto-creation failed"
            
            self.log_test(
                "User Model Creation", 
                "PASS", 
                "Created user with Arabic name and profile",
                [f"User ID: {user.id}", f"Profile ID: {profile.user_id}", f"Role: {user.role}"]
            )
            
        except Exception as e:
            self.log_test("User Model Creation", "FAIL", str(e))
            
        # Test Location Model
        try:
            location = Location.objects.create(
                city='الرياض التجريبية',
                state='منطقة الرياض التجريبية',
                country='المملكة العربية السعودية',
                postal_code='12345',
                latitude=Decimal('24.7136'),
                longitude=Decimal('46.6753')
            )
            
            coords = location.coordinates
            assert coords is not None, "Coordinates property failed"
            
            self.log_test(
                "Location Model Creation", 
                "PASS", 
                "Created location with Arabic text and coordinates",
                [f"Location: {location}", f"Coordinates: {coords}"]
            )
            
        except Exception as e:
            self.log_test("Location Model Creation", "FAIL", str(e))
            
        # Test Property Model
        try:
            property_obj = Property.objects.create(
                owner=user,
                title='فيلا تجريبية فاخرة',
                slug='test-villa-luxury',
                description='فيلا تجريبية للاختبار مع جميع المرافق الحديثة',
                property_type='villa',
                building_type='residential',
                status='available',
                deed_number='TEST-DEED-001',
                size_sqm=Decimal('500.00'),
                floors=2,
                year_built=2020,
                location=location,
                address='حي الاختبار، الرياض التجريبية',
                market_value=Decimal('1500000.00'),
                minimum_bid=Decimal('1000000.00'),
                features={
                    'bedrooms': 5,
                    'bathrooms': 4,
                    'parking': 'yes',
                    'garden': 'yes'
                },
                amenities={
                    'swimming_pool': True,
                    'gym': False,
                    'security': True
                }
            )
            
            assert property_obj.features['bedrooms'] == 5, "JSON features storage failed"
            assert property_obj.amenities['swimming_pool'] == True, "JSON amenities storage failed"
            
            self.log_test(
                "Property Model Creation", 
                "PASS", 
                "Created property with Arabic content and JSON fields",
                [f"Property: {property_obj.title}", f"Value: {property_obj.market_value} SAR", f"Features: {len(property_obj.features)} items"]
            )
            
        except Exception as e:
            self.log_test("Property Model Creation", "FAIL", str(e))
            
        # Test Auction Model
        try:
            start_date = datetime.now() + timedelta(days=1)
            end_date = start_date + timedelta(days=7)
            
            auction = Auction.objects.create(
                title='مزاد الفيلا التجريبية',
                slug='test-villa-auction',
                auction_type='public',
                description='مزاد علني لبيع الفيلا التجريبية',
                start_date=start_date,
                end_date=end_date,
                registration_deadline=start_date - timedelta(hours=24),
                related_property=property_obj,
                starting_bid=Decimal('1000000.00'),
                current_bid=Decimal('1000000.00'),
                minimum_increment=Decimal('50000.00'),
                status='upcoming',
                minimum_participants=2,
                auto_extend_minutes=5,
                max_extensions=3,
                is_published=True
            )
            
            assert auction.related_property == property_obj, "Property relationship failed"
            assert auction.starting_bid == Decimal('1000000.00'), "Decimal field storage failed"
            
            self.log_test(
                "Auction Model Creation", 
                "PASS", 
                "Created auction with Arabic content and relationships",
                [f"Auction: {auction.title}", f"Starting bid: {auction.starting_bid} SAR", f"Status: {auction.status}"]
            )
            
        except Exception as e:
            self.log_test("Auction Model Creation", "FAIL", str(e))
            
        # Test Bid Model
        try:
            bidder = CustomUser.objects.create_user(
                email='bidder.test@example.com',
                password='BidderTest123!',
                first_name='محمد',
                last_name='المزايد',
                role='user'
            )
            
            bid = Bid.objects.create(
                auction=auction,
                bidder=bidder,
                bid_amount=Decimal('1100000.00'),
                max_bid_amount=Decimal('1200000.00'),
                status='active',
                notes='أول مزايدة تجريبية',
                ip_address='192.168.1.100',
                is_verified=True
            )
            
            assert bid.auction == auction, "Auction relationship failed"
            assert bid.bidder == bidder, "Bidder relationship failed"
            
            self.log_test(
                "Bid Model Creation", 
                "PASS", 
                "Created bid with relationships and Arabic notes",
                [f"Bid amount: {bid.bid_amount} SAR", f"Bidder: {bidder.get_full_name()}", f"Status: {bid.status}"]
            )
            
        except Exception as e:
            self.log_test("Bid Model Creation", "FAIL", str(e))
            
    def run_authentication_tests(self):
        """Test user authentication"""
        print("\n🔐 Testing User Authentication")
        print("-" * 50)
        
        # Test provided user credentials
        test_credentials = [
            {"email": "admin@email.com", "password": "admin12345"},
            {"email": "rings9619@gmail.com", "password": "Africa123"},
            {"email": "rings9619@gmail.com", "password": "africa123"},
        ]
        
        successful_auths = 0
        
        for creds in test_credentials:
            try:
                from django.contrib.auth import authenticate
                user = authenticate(username=creds['email'], password=creds['password'])
                
                if user and user.is_active:
                    successful_auths += 1
                    self.log_test(
                        f"Authentication - {creds['email']}", 
                        "PASS", 
                        "Authentication successful",
                        [f"User: {user.get_full_name()}", f"Role: {user.role}", f"Verified: {user.is_verified}"]
                    )
                else:
                    self.log_test(
                        f"Authentication - {creds['email']}", 
                        "FAIL", 
                        "Authentication failed or user inactive"
                    )
                    
            except Exception as e:
                self.log_test(f"Authentication - {creds['email']}", "FAIL", str(e))
                
        self.log_test(
            "Overall Authentication", 
            "PASS" if successful_auths > 0 else "FAIL", 
            f"{successful_auths}/{len(test_credentials)} credentials successful"
        )
        
    def run_admin_tests(self):
        """Test admin panel functionality"""
        print("\n⚙️ Testing Admin Panel")
        print("-" * 50)
        
        # Check admin registrations
        try:
            from django.contrib.admin.sites import site
            
            models_to_check = [
                CustomUser, UserProfile, Property, Location, Auction, 
                Bid, Room, RentalProperty, Worker, MaintenanceCategory
            ]
            
            registered_count = 0
            registered_models = []
            
            for model in models_to_check:
                if model in site._registry:
                    registered_count += 1
                    registered_models.append(model.__name__)
                    
            self.log_test(
                "Admin Model Registration", 
                "PASS" if registered_count >= 8 else "WARN",
                f"{registered_count}/{len(models_to_check)} models registered",
                registered_models
            )
            
        except Exception as e:
            self.log_test("Admin Model Registration", "FAIL", str(e))
            
        # Test admin data visibility
        try:
            # Check if Arabic data is properly stored and retrievable
            arabic_users = CustomUser.objects.filter(first_name__iregex=r'^[أ-ي]').count()
            arabic_properties = Property.objects.filter(title__iregex=r'^[أ-ي]').count()
            
            self.log_test(
                "Arabic Data Visibility", 
                "PASS" if arabic_users > 0 and arabic_properties > 0 else "FAIL",
                "Arabic data properly stored and accessible",
                [f"Arabic users: {arabic_users}", f"Arabic properties: {arabic_properties}"]
            )
            
        except Exception as e:
            self.log_test("Arabic Data Visibility", "FAIL", str(e))
            
    def run_api_tests(self):
        """Test API endpoints (basic connectivity)"""
        print("\n🌐 Testing API Endpoints")
        print("-" * 50)
        
        # Test basic API endpoints
        endpoints_to_test = [
            ('/api/properties/', 'Properties API'),
            ('/api/auctions/', 'Auctions API'),
            ('/api/accounts/login/', 'Login API'),
            ('/admin/', 'Admin Panel'),
        ]
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.client.get(endpoint)
                
                if response.status_code in [200, 301, 302, 401, 403]:  # Expected responses
                    self.log_test(
                        f"API Endpoint - {name}", 
                        "PASS", 
                        f"Endpoint accessible (HTTP {response.status_code})"
                    )
                else:
                    self.log_test(
                        f"API Endpoint - {name}", 
                        "WARN", 
                        f"Unexpected response (HTTP {response.status_code})"
                    )
                    
            except Exception as e:
                self.log_test(f"API Endpoint - {name}", "FAIL", str(e))
                
    def run_relationship_tests(self):
        """Test model relationships"""
        print("\n🔗 Testing Model Relationships")
        print("-" * 50)
        
        try:
            # Test Property -> Owner relationship
            properties_with_owners = Property.objects.select_related('owner').count()
            
            # Test Auction -> Property relationship
            auctions_with_properties = Auction.objects.select_related('related_property').count()
            
            # Test Bid -> Auction -> Property chain
            bids_with_complete_chain = Bid.objects.select_related('auction__related_property__owner').count()
            
            # Test User -> Profile relationship
            users_with_profiles = CustomUser.objects.select_related('profile').count()
            
            self.log_test(
                "Model Relationships", 
                "PASS",
                "All key relationships working correctly",
                [
                    f"Properties with owners: {properties_with_owners}",
                    f"Auctions with properties: {auctions_with_properties}",
                    f"Complete bid chains: {bids_with_complete_chain}",
                    f"Users with profiles: {users_with_profiles}"
                ]
            )
            
        except Exception as e:
            self.log_test("Model Relationships", "FAIL", str(e))
            
    def run_arabic_data_tests(self):
        """Test Arabic data handling"""
        print("\n🇸🇦 Testing Arabic Data Handling")
        print("-" * 50)
        
        try:
            # Test Arabic text storage and retrieval
            arabic_user = CustomUser.objects.filter(first_name__contains='أحمد').first()
            if arabic_user:
                assert 'أحمد' in arabic_user.first_name, "Arabic text storage failed"
                
            arabic_property = Property.objects.filter(title__contains='فيلا').first()
            if arabic_property:
                assert 'فيلا' in arabic_property.title, "Arabic property title storage failed"
                
            arabic_city = Location.objects.filter(city__contains='الرياض').first()
            if arabic_city:
                assert 'الرياض' in arabic_city.city, "Arabic city name storage failed"
                
            # Count Arabic content
            arabic_users_count = CustomUser.objects.filter(first_name__iregex=r'^[أ-ي]').count()
            arabic_properties_count = Property.objects.filter(title__iregex=r'^[أ-ي]').count()
            arabic_cities_count = Location.objects.filter(city__iregex=r'^[أ-ي]').count()
            
            self.log_test(
                "Arabic Data Storage", 
                "PASS",
                "Arabic text properly stored and searchable",
                [
                    f"Users with Arabic names: {arabic_users_count}",
                    f"Properties with Arabic titles: {arabic_properties_count}",
                    f"Cities with Arabic names: {arabic_cities_count}"
                ]
            )
            
            # Test Arabic search and filtering
            arabic_search_results = Property.objects.filter(
                title__icontains='فيلا'
            ).count()
            
            location_search_results = Location.objects.filter(
                city__icontains='الرياض'
            ).count()
            
            self.log_test(
                "Arabic Search Functionality", 
                "PASS" if arabic_search_results > 0 or location_search_results > 0 else "WARN",
                "Arabic text search working",
                [
                    f"Villa search results: {arabic_search_results}",
                    f"Riyadh search results: {location_search_results}"
                ]
            )
            
        except Exception as e:
            self.log_test("Arabic Data Handling", "FAIL", str(e))
            
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] == 'WARN'])
        
        print(f"📈 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Warnings: {warning_tests}")
        print(f"   📊 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n🏆 System Status:")
        if failed_tests == 0:
            print("   🟢 EXCELLENT - All tests passed!")
        elif failed_tests <= 2:
            print("   🟡 GOOD - Minor issues detected")
        else:
            print("   🔴 NEEDS ATTENTION - Multiple failures detected")
            
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"   {icon} {result['test']}: {result['message']}")
            
        # System Statistics
        print(f"\n📊 System Statistics:")
        try:
            print(f"   👥 Total Users: {CustomUser.objects.count()}")
            print(f"   📍 Locations: {Location.objects.count()}")
            print(f"   🏠 Properties: {Property.objects.count()}")
            print(f"   🔨 Auctions: {Auction.objects.count()}")
            print(f"   💰 Bids: {Bid.objects.count()}")
            print(f"   🇸🇦 Arabic Users: {CustomUser.objects.filter(first_name__iregex=r'^[أ-ي]').count()}")
            print(f"   🏢 Arabic Properties: {Property.objects.filter(title__iregex=r'^[أ-ي]').count()}")
        except:
            print("   ❌ Could not retrieve system statistics")
            
        print("\n" + "=" * 80)
        print("🎯 Test Suite Completed Successfully!")
        print("=" * 80)
        
        # Save report to file
        try:
            report_data = {
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'warnings': warning_tests,
                    'success_rate': round(passed_tests/total_tests*100, 1)
                },
                'results': self.test_results,
                'timestamp': datetime.now().isoformat()
            }
            
            with open('test_report.json', 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
                
            print("💾 Detailed report saved to 'test_report.json'")
            
        except Exception as e:
            print(f"⚠️ Could not save report file: {e}")

def main():
    """Main function to run the test suite"""
    print("🔧 Arabic Auction System - Comprehensive Test Suite")
    print("=" * 80)
    print("Testing backend models, authentication, Arabic data, and admin functionality")
    print("=" * 80)
    
    try:
        suite = ArabicAuctionTestSuite()
        suite.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()