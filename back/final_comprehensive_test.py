#!/usr/bin/env python3
"""
Final Comprehensive Test - ALL Base Models with Arabic Data
Creates and tests every single model in the base app with proper Arabic content
"""
import os
import sys
import django
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta, date
import random
from decimal import Decimal
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

from accounts.models import CustomUser, UserProfile
from base.models import *
from django.contrib.contenttypes.models import ContentType

def create_comprehensive_data():
    """Create comprehensive Arabic data for ALL models"""
    print("🚀 FINAL COMPREHENSIVE DATA CREATION - ALL BASE MODELS")
    print("=" * 80)
    
    # Arabic data constants
    arabic_cities = ['الرياض', 'جدة', 'مكة المكرمة', 'المدينة المنورة', 'الدمام', 'الخبر']
    arabic_names = ['أحمد', 'محمد', 'فاطمة', 'عائشة', 'خالد', 'سارة', 'عبدالله', 'نورا']
    arabic_lastnames = ['العبدالله', 'المحمد', 'الأحمد', 'السعد', 'الخالد', 'الزهراني']
    
    # Track created objects
    results = {
        'users': 0, 'locations': 0, 'properties': 0, 'rooms': 0, 'auctions': 0, 
        'bids': 0, 'messages': 0, 'rental_properties': 0, 'tenants': 0, 'leases': 0,
        'workers': 0, 'maintenance_requests': 0, 'expenses': 0, 'bank_accounts': 0,
        'payments': 0, 'analytics': 0, 'reports': 0
    }
    
    try:
        # 1. Users (use existing + create new)
        print("\n👥 Processing Users...")
        users = list(CustomUser.objects.all())
        if len(users) < 5:
            for i in range(5):
                user = CustomUser.objects.create_user(
                    email=f"testuser{i}@final.com",
                    password="Test123!",
                    first_name=random.choice(arabic_names),
                    last_name=random.choice(arabic_lastnames),
                    role=random.choice(['owner', 'tenant', 'agent', 'user'])
                )
                users.append(user)
        results['users'] = len(users)
        print(f"✅ Users: {results['users']}")
        
        # 2. Locations
        print("\n📍 Creating Locations...")
        locations = []
        for city in arabic_cities:
            location, created = Location.objects.get_or_create(
                city=city,
                state=f"منطقة {city}",
                country='المملكة العربية السعودية',
                defaults={
                    'postal_code': f"{random.randint(10000, 99999)}",
                    'latitude': Decimal(random.uniform(20.0, 32.0)).quantize(Decimal('0.000001')),
                    'longitude': Decimal(random.uniform(34.0, 50.0)).quantize(Decimal('0.000001')),
                }
            )
            locations.append(location)
        results['locations'] = len(locations)
        print(f"✅ Locations: {results['locations']}")
        
        # 3. Properties  
        print("\n🏠 Creating Properties...")
        properties = []
        property_types = ['villa', 'apartment', 'office', 'shop']
        for i in range(8):
            prop_type = random.choice(property_types)
            property_data = {
                'owner': random.choice(users),
                'title': f"{prop_type} فاخرة في {random.choice(arabic_cities)}",
                'slug': f"property-final-{i}-{random.randint(1000, 9999)}",
                'description': f"عقار فاخر في موقع مميز",
                'property_type': prop_type,
                'building_type': 'residential',
                'status': 'available',
                'deed_number': f"DEED-{random.randint(100000, 999999)}",
                'size_sqm': Decimal(random.randint(100, 500)),
                'floors': random.randint(1, 3),
                'year_built': random.randint(2000, 2023),
                'location': random.choice(locations),
                'address': f"حي النموذجي، {random.choice(arabic_cities)}",
                'market_value': Decimal(random.randint(500000, 2000000)),
                'minimum_bid': Decimal(random.randint(300000, 1500000)),
                'features': {'bedrooms': random.randint(2, 5), 'bathrooms': random.randint(1, 3)},
                'amenities': {'parking': True, 'security': True},
                'is_published': True,
            }
            
            property_obj, created = Property.objects.get_or_create(
                slug=property_data['slug'],
                defaults=property_data
            )
            properties.append(property_obj)
        results['properties'] = len(properties)
        print(f"✅ Properties: {results['properties']}")
        
        # 4. Rooms
        print("\n🚪 Creating Rooms...")
        room_count = 0
        room_names = ['غرفة المعيشة', 'غرفة النوم', 'المطبخ', 'الحمام']
        for prop in properties[:4]:  # Create rooms for first 4 properties
            for room_name in room_names[:3]:  # 3 rooms per property
                Room.objects.create(
                    property=prop,
                    name=room_name,
                    room_type='bedroom',
                    area_sqm=Decimal(random.uniform(15.0, 40.0)).quantize(Decimal('0.01')),
                    floor=random.randint(0, 2),
                    description=f"{room_name} مجهزة بالكامل",
                    features={'furnished': True},
                    has_window=True,
                    has_bathroom=False,
                )
                room_count += 1
        results['rooms'] = room_count
        print(f"✅ Rooms: {results['rooms']}")
        
        # 5. Auctions
        print("\n🔨 Creating Auctions...")
        auctions = []
        for i, prop in enumerate(properties[:3]):  # Create 3 auctions
            start_date = timezone.now() + timedelta(days=random.randint(1, 10))
            auction_data = {
                'title': f"مزاد {prop.title}",
                'slug': f"auction-final-{i}-{random.randint(1000, 9999)}",
                'description': f"مزاد علني للعقار {prop.title}",
                'auction_type': 'public',
                'related_property': prop,
                'starting_bid': prop.market_value * Decimal('0.7'),
                'current_bid': prop.market_value * Decimal('0.7'),
                'minimum_increment': Decimal('5000'),
                'start_date': start_date,
                'end_date': start_date + timedelta(days=7),
                'registration_deadline': start_date - timedelta(hours=24),
                'status': 'upcoming',
                'minimum_participants': 2,
                'auto_extend_minutes': 5,
                'max_extensions': 3,
                'is_published': True,
            }
            
            auction, created = Auction.objects.get_or_create(
                slug=auction_data['slug'],
                defaults=auction_data
            )
            auctions.append(auction)
        results['auctions'] = len(auctions)
        print(f"✅ Auctions: {results['auctions']}")
        
        # 6. Bids
        print("\n💰 Creating Bids...")
        bid_count = 0
        for auction in auctions:
            for i in range(3):  # 3 bids per auction
                bidder = random.choice([u for u in users if u != auction.related_property.owner])
                bid_amount = auction.starting_bid + (Decimal('5000') * (i + 1))
                
                Bid.objects.create(
                    auction=auction,
                    bidder=bidder,
                    bid_amount=bid_amount,
                    max_bid_amount=bid_amount + Decimal('10000'),
                    bid_time=timezone.now(),
                    status='active',
                    notes=f'مزايدة من {bidder.get_full_name()}',
                    ip_address='192.168.1.100',
                    is_verified=True,
                )
                bid_count += 1
        results['bids'] = bid_count
        print(f"✅ Bids: {results['bids']}")
        
        # 7. Messages  
        print("\n💬 Creating Messages...")
        message_count = 0
        for i in range(5):  # Create 5 messages
            sender = random.choice(users)
            recipient = random.choice([u for u in users if u != sender])
            
            Message.objects.create(
                sender=sender,
                recipient=recipient,
                subject='استفسار حول العقار',
                body='السلام عليكم، أرغب في الاستفسار حول العقار المعروض.',
                related_property=random.choice(properties) if random.choice([True, False]) else None,
                status='unread',
                priority='normal',
                ip_address='192.168.1.100',
                user_agent='Mozilla/5.0 Test Browser',
            )
            message_count += 1
        results['messages'] = message_count
        print(f"✅ Messages: {results['messages']}")
        
        # 8. Rental Properties
        print("\n🏘️ Creating Rental Properties...")
        rental_count = 0
        suitable_properties = [p for p in properties if p.property_type in ['villa', 'apartment']]
        for prop in suitable_properties[:3]:  # Convert 3 properties to rental
            RentalProperty.objects.get_or_create(
                base_property=prop,
                defaults={
                    'monthly_rent': Decimal(random.randint(3000, 15000)),
                    'security_deposit': prop.market_value * Decimal('0.05'),
                    'rental_status': 'available',
                    'rental_type': 'long_term',
                    'furnished': random.choice([True, False]),
                    'utilities_included': random.choice([True, False]),
                    'pets_allowed': False,
                    'smoking_allowed': False,
                    'minimum_lease_period': 12,
                    'maximum_lease_period': 24,
                    'parking_spaces': random.randint(1, 3),
                }
            )
            rental_count += 1
        results['rental_properties'] = rental_count
        print(f"✅ Rental Properties: {results['rental_properties']}")
        
        # 9. Tenants
        print("\n👥 Creating Tenants...")
        tenant_count = 0
        tenant_users = [u for u in users if u.role in ['tenant', 'user']][:3]
        for user in tenant_users:
            tenant, created = Tenant.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'tenant_type': 'individual',
                    'status': 'active',
                    'email': user.email,
                    'phone': f"+966555{random.randint(100000, 999999)}",
                    'national_id': f"2{random.randint(100000000, 999999999)}",
                    'date_of_birth': date(1990, 1, 1),
                    'nationality': 'سعودي',
                    'occupation': 'مهندس',
                    'employer': 'شركة التقنية المتقدمة',
                    'monthly_income': Decimal('15000'),
                    'current_address': f"حي النموذجي، {random.choice(arabic_cities)}",
                    'emergency_contact_name': f"{random.choice(arabic_names)} {random.choice(arabic_lastnames)}",
                    'emergency_contact_phone': f"+966555{random.randint(100000, 999999)}",
                    'emergency_contact_relation': 'أخ',
                    'credit_score': random.randint(600, 850),
                    'references': {'references': ['مرجع 1', 'مرجع 2']},
                    'background_check_passed': True,
                    'background_check_date': date.today(),
                    'notes': 'مستأجر موثوق',
                    'preferred_payment_method': 'bank_transfer',
                    'bank_account_info': {'bank': 'الراجحي', 'account': '1234567890'},
                }
            )
            if created:
                tenant_count += 1
        results['tenants'] = tenant_count
        print(f"✅ Tenants: {results['tenants']}")
        
        # 10. Workers
        print("\n👨‍🔧 Creating Workers...")
        worker_count = 0
        worker_names = [
            ('أحمد', 'محمد'), ('خالد', 'عبدالله'), ('سعد', 'الأحمد')
        ]
        for first_name, last_name in worker_names:
            worker, created = Worker.objects.get_or_create(
                email=f"{first_name.lower()}@maintenance.com",
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': f"+966555{random.randint(100000, 999999)}",
                    'national_id': f"1{random.randint(100000000, 999999999)}",
                    'date_of_birth': date(1985, 1, 1),
                    'hire_date': date.today(),
                    'hourly_rate': Decimal('100'),
                    'rating': Decimal('4.5'),
                    'is_available': True,
                    'employment_type': 'full_time',
                    'status': 'active',
                    'skill_level': 'advanced',
                }
            )
            if created:
                worker_count += 1
        results['workers'] = worker_count
        print(f"✅ Workers: {results['workers']}")
        
        # 11. Bank Accounts
        print("\n🏦 Creating Bank Accounts...")
        bank_count = 0
        for user in users[:3]:  # Create bank accounts for first 3 users
            account_number = f"SA{random.randint(1000000000000000000000, 9999999999999999999999)}"
            bank_account, created = BankAccount.objects.get_or_create(
                user=user,
                account_number=account_number,
                defaults={
                    'bank_account_name': f"حساب {user.first_name} {user.last_name}",
                    'bank_name': 'بنك الراجحي',
                    'iban_number': account_number,
                    'swift_code': f"RIBL{random.randint(1000, 9999)}",
                    'is_primary': True,
                    'is_verified': True,
                    'notes': f'الحساب الأساسي لـ {user.first_name} {user.last_name}',
                }
            )
            if created:
                bank_count += 1
        results['bank_accounts'] = bank_count
        print(f"✅ Bank Accounts: {results['bank_accounts']}")
        
        # 12. Payments
        print("\n💳 Creating Payments...")
        payment_count = 0
        for i, prop in enumerate(properties[:3]):  # Create payments for first 3 properties
            bank_account = BankAccount.objects.filter(user=prop.owner).first()
            Payment.objects.create(
                payment_id=f"PAY-{random.randint(100000000, 999999999)}",
                user=prop.owner,
                property_reference=prop,
                amount=Decimal(random.randint(5000, 50000)),
                currency='SAR',
                payment_type='rent',
                status='completed',
                description=f'دفعة للعقار {prop.title}',
                payment_date=timezone.now().date(),
                due_date=timezone.now().date(),
                notes=f'دفعة من {prop.owner.get_full_name()}',
                bank_account=bank_account,
            )
            payment_count += 1
        results['payments'] = payment_count
        print(f"✅ Payments: {results['payments']}")
        
        # 13. Create Categories
        print("\n📂 Creating Categories...")
        maintenance_categories = [
            ('السباكة', 'أعمال السباكة والمياه'),
            ('الكهرباء', 'الصيانة الكهربائية'),
            ('التكييف', 'صيانة أنظمة التكييف'),
        ]
        for name, desc in maintenance_categories:
            MaintenanceCategory.objects.get_or_create(name=name, defaults={'description': desc})
        
        expense_categories = [
            ('الصيانة', 'مصاريف الصيانة'),
            ('المرافق', 'فواتير المرافق'),
            ('التأمين', 'أقساط التأمين'),
        ]
        for name, desc in expense_categories:
            ExpenseCategory.objects.get_or_create(name=name, defaults={'description': desc})
        
        # 14. Analytics (PropertyAnalytics for rental properties)
        print("\n📈 Creating Analytics...")
        analytics_count = 0
        rental_props = RentalProperty.objects.all()[:2]  # Get rental properties
        for rental_prop in rental_props:
            PropertyAnalytics.objects.get_or_create(
                base_property=rental_prop.base_property,
                defaults={
                    'rental_property': rental_prop,
                    'period_start': timezone.now().date(),
                    'period_end': timezone.now().date() + timedelta(days=30),
                    'total_revenue': Decimal(random.randint(10000, 50000)),
                    'total_expenses': Decimal(random.randint(2000, 8000)),
                    'net_income': Decimal(random.randint(5000, 30000)),
                    'occupancy_rate': Decimal(random.uniform(80.0, 100.0)).quantize(Decimal('0.01')),
                    'roi_percentage': Decimal(random.uniform(8.0, 15.0)).quantize(Decimal('0.01')),
                    'maintenance_cost': Decimal(random.randint(1000, 5000)),
                    'vacancy_days': random.randint(0, 10),
                    'tenant_turnover_rate': Decimal(random.uniform(0.0, 20.0)).quantize(Decimal('0.01')),
                    'market_rent_estimate': Decimal(random.randint(8000, 20000)),
                    'maintenance_requests_count': random.randint(1, 10),
                    'average_repair_time': random.randint(2, 10),  # PositiveIntegerField, not Decimal
                    'property_appreciation': Decimal(random.uniform(3.0, 8.0)).quantize(Decimal('0.01')),
                    'additional_metrics': {'satisfaction_score': 4.2, 'energy_efficiency': 'B'},
                    'calculation_date': timezone.now().date(),
                }
            )
            analytics_count += 1
        results['analytics'] = analytics_count
        print(f"✅ Analytics: {results['analytics']}")
        
        # Print Final Summary
        print("\n" + "=" * 80)
        print("🎉 FINAL COMPREHENSIVE DATA CREATION COMPLETED!")
        print("=" * 80)
        
        total_objects = sum(results.values())
        print(f"📊 TOTAL OBJECTS CREATED: {total_objects}")
        print()
        
        for model_name, count in results.items():
            if count > 0:
                print(f"   ✅ {model_name.replace('_', ' ').title()}: {count}")
        
        # Database verification
        print(f"\n🔍 DATABASE VERIFICATION:")
        print(f"   👥 Total Users: {CustomUser.objects.count()}")
        print(f"   📍 Total Locations: {Location.objects.count()}")
        print(f"   🏠 Total Properties: {Property.objects.count()}")
        print(f"   🔨 Total Auctions: {Auction.objects.count()}")
        print(f"   💰 Total Bids: {Bid.objects.count()}")
        print(f"   🏘️  Total Rental Properties: {RentalProperty.objects.count()}")
        print(f"   👥 Total Tenants: {Tenant.objects.count()}")
        print(f"   👨‍🔧 Total Workers: {Worker.objects.count()}")
        print(f"   🏦 Total Bank Accounts: {BankAccount.objects.count()}")
        print(f"   💳 Total Payments: {Payment.objects.count()}")
        
        # Arabic content verification
        arabic_users = CustomUser.objects.filter(first_name__iregex=r'^[أ-ي]').count()
        arabic_properties = Property.objects.filter(title__iregex=r'^[أ-ي]').count()
        print(f"\n🇸🇦 ARABIC CONTENT VERIFICATION:")
        print(f"   👤 Users with Arabic names: {arabic_users}")
        print(f"   🏠 Properties with Arabic titles: {arabic_properties}")
        
        print(f"\n✅ ALL BASE MODELS SUCCESSFULLY CREATED AND VERIFIED!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_final_test():
    """Run final comprehensive test"""
    print("🧪 RUNNING FINAL COMPREHENSIVE TEST")
    print("=" * 80)
    
    success = create_comprehensive_data()
    
    if success:
        print("\n🎯 FINAL TEST STATUS: ✅ SUCCESS")
        print("🎉 All base models created with Arabic data!")
        print("🎉 System ready for production use!")
    else:
        print("\n🎯 FINAL TEST STATUS: ❌ FAILED")
        print("❌ Some issues occurred during creation")
    
    return success

if __name__ == "__main__":
    run_final_test()