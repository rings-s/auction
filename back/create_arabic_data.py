#!/usr/bin/env python3
"""
Create comprehensive Arabic test data for the auction system
"""
import os
import sys
import django
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

from accounts.models import CustomUser, UserProfile
from base.models import *
from django.contrib.contenttypes.models import ContentType

# Arabic test data
ARABIC_CITIES = [
    'الرياض', 'جدة', 'مكة المكرمة', 'المدينة المنورة', 'الدمام', 'الخبر', 'الطائف', 
    'بريدة', 'تبوك', 'حائل', 'أبها', 'الأحساء', 'نجران', 'جازان', 'ينبع', 'عرعر'
]

ARABIC_STATES = [
    'منطقة الرياض', 'منطقة مكة المكرمة', 'المنطقة الشرقية', 'منطقة المدينة المنورة',
    'منطقة القصيم', 'منطقة تبوك', 'منطقة حائل', 'منطقة عسير', 'منطقة الأحساء',
    'منطقة نجران', 'منطقة جازان', 'منطقة الباحة', 'منطقة عرعر', 'منطقة الجوف'
]

ARABIC_FIRST_NAMES = [
    'أحمد', 'محمد', 'عبدالله', 'عبدالرحمن', 'خالد', 'سعد', 'فهد', 'عبدالعزيز',
    'طلال', 'وليد', 'ماجد', 'نواف', 'بندر', 'تركي', 'فيصل', 'سلطان', 'راشد',
    'فاطمة', 'عائشة', 'خديجة', 'مريم', 'زينب', 'نورا', 'سارة', 'هند', 'أمل',
    'منال', 'رانيا', 'ريم', 'لينا', 'دانا', 'جواهر', 'أسماء'
]

ARABIC_LAST_NAMES = [
    'العبدالله', 'المحمد', 'الأحمد', 'السعد', 'الخالد', 'الفهد', 'العتيبي',
    'الشمري', 'القحطاني', 'الغامدي', 'الحربي', 'المطيري', 'العنزي', 'الدوسري',
    'الزهراني', 'الثقفي', 'الأسمري', 'العمري', 'الجهني', 'البقمي', 'الرشيدي'
]

ARABIC_PROPERTY_TYPES = [
    ('villa', 'فيلا'),
    ('apartment', 'شقة'),
    ('office', 'مكتب'),
    ('shop', 'متجر'),
    ('warehouse', 'مستودع'),
    ('land', 'قطعة أرض'),
    ('building', 'مبنى'),
    ('compound', 'مجمع'),
]

ARABIC_PROPERTY_DESCRIPTIONS = [
    'فيلا فاخرة بتشطيبات عالية الجودة',
    'شقة واسعة في موقع مميز',
    'مكتب تجاري في منطقة الأعمال',
    'متجر في شارع تجاري حيوي',
    'مستودع واسع للتخزين والتوزيع',
    'قطعة أرض للاستثمار العقاري',
    'مبنى تجاري متكامل الخدمات',
    'مجمع سكني بمرافق حديثة'
]

ARABIC_ROOM_NAMES = [
    'غرفة المعيشة', 'غرفة النوم الرئيسية', 'غرفة النوم الثانية', 'غرفة النوم الثالثة',
    'المطبخ', 'الحمام الرئيسي', 'حمام الضيوف', 'مجلس الرجال', 'مجلس النساء',
    'غرفة الطعام', 'المكتبة', 'غرفة التخزين', 'الحديقة', 'السطح', 'الباركينج'
]

def create_arabic_users():
    """Create Arabic test users with different roles"""
    print("👥 إنشاء المستخدمين العرب...")
    
    users_data = []
    roles = list(dict(CustomUser.ROLE_CHOICES).keys())
    
    for i in range(15):  # Create 15 Arabic users
        first_name = random.choice(ARABIC_FIRST_NAMES)
        last_name = random.choice(ARABIC_LAST_NAMES)
        role = random.choice(roles)
        
        email = f"user{i+1}@arabic.auction.com"
        
        user_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'is_verified': True,
            'is_active': True,
        }
        
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults=user_data
        )
        
        if created:
            user.set_password('ArabicTest123!')
            user.save()
            
            # Create UserProfile with Arabic data
            profile_data = {
                'identity_type': random.choice(['national_identity', 'residency']),
                'identity_number': f"1{random.randint(100000000, 999999999)}",
                'bio': f"مرحباً، أنا {first_name} {last_name} وأعمل في مجال العقارات",
                'company_name': f"شركة {first_name} {last_name} العقارية",
                'address': f"حي {random.choice(['النخيل', 'الملك فهد', 'العليا', 'الورود', 'السلام'])}",
                'city': random.choice(ARABIC_CITIES),
                'state': random.choice(ARABIC_STATES),
                'country': 'المملكة العربية السعودية',
                'postal_code': f"{random.randint(10000, 99999)}",
                'credit_limit': Decimal(random.randint(10000, 500000)),
                'rating': Decimal(random.uniform(3.0, 5.0)).quantize(Decimal('0.01')),
            }
            
            for key, value in profile_data.items():
                setattr(user.profile, key, value)
            user.profile.save()
            
            print(f"✅ تم إنشاء المستخدم: {first_name} {last_name} ({email}) - {role}")
        
        # Add to users_data regardless of whether created or existed
        users_data.append({
            'user': user,
            'email': email,
            'name': f"{first_name} {last_name}",
            'role': user.role
        })
    
    return users_data

def create_arabic_locations():
    """Create Arabic locations"""
    print("\n📍 إنشاء المواقع العربية...")
    
    locations = []
    
    for i, city in enumerate(ARABIC_CITIES[:10]):  # Create 10 locations
        state = ARABIC_STATES[i % len(ARABIC_STATES)]
        
        location_data = {
            'city': city,
            'state': state,
            'country': 'المملكة العربية السعودية',
            'postal_code': f"{random.randint(10000, 99999)}",
            'latitude': Decimal(random.uniform(20.0, 32.0)).quantize(Decimal('0.000001')),
            'longitude': Decimal(random.uniform(34.0, 50.0)).quantize(Decimal('0.000001')),
        }
        
        location, created = Location.objects.get_or_create(
            city=city,
            state=state,
            country='المملكة العربية السعودية',
            defaults=location_data
        )
        
        if created:
            print(f"✅ تم إنشاء الموقع: {city}, {state}")
        
        # Add to locations regardless of whether created or existed
        locations.append(location)
    
    return locations

def create_arabic_properties(users_data, locations):
    """Create Arabic properties"""
    print("\n🏠 إنشاء العقارات العربية...")
    
    properties = []
    
    for i in range(20):  # Create 20 properties
        # Find suitable owners or fallback to any user
        suitable_owners = [u['user'] for u in users_data if u['role'] in ['owner', 'agent', 'administrator']]
        if not suitable_owners:
            suitable_owners = [u['user'] for u in users_data]  # Fallback to any user
        
        owner = random.choice(suitable_owners)
        location = random.choice(locations)
        prop_type, prop_type_ar = random.choice(ARABIC_PROPERTY_TYPES)
        
        property_data = {
            'owner': owner,
            'title': f"{prop_type_ar} في {location.city}",
            'slug': f"property-{i+1}-{prop_type}",
            'description': random.choice(ARABIC_PROPERTY_DESCRIPTIONS) + f" في منطقة {location.city} المميزة.",
            'property_type': prop_type,
            'building_type': random.choice(['residential', 'commercial', 'industrial']),
            'status': 'available',
            'deed_number': f"DEED-{random.randint(100000, 999999)}",
            'size_sqm': Decimal(random.randint(100, 1000)),
            'floors': random.randint(1, 5),
            'year_built': random.randint(1980, 2023),
            'location': location,
            'address': f"حي {random.choice(['النخيل', 'الملك فهد', 'العليا', 'الورود', 'السلام'])}، {location.city}",
            'market_value': Decimal(random.randint(200000, 5000000)),
            'minimum_bid': Decimal(random.randint(100000, 3000000)),
            'features': {
                'bedrooms': random.randint(1, 8),
                'bathrooms': random.randint(1, 5),
                'parking': random.choice(['yes', 'no']),
                'garden': random.choice(['yes', 'no']),
                'furnished': random.choice(['yes', 'no', 'semi']),
            },
            'amenities': {
                'swimming_pool': random.choice([True, False]),
                'gym': random.choice([True, False]),
                'security': random.choice([True, False]),
                'elevator': random.choice([True, False]),
            },
            'is_published': True,
            'is_featured': random.choice([True, False]),
        }
        
        property_obj, created = Property.objects.get_or_create(
            slug=property_data['slug'],
            defaults=property_data
        )
        
        if created:
            properties.append(property_obj)
            print(f"✅ تم إنشاء العقار: {property_obj.title}")
            
            # Create rooms for property
            create_arabic_rooms(property_obj)
    
    return properties

def create_arabic_rooms(property_obj):
    """Create Arabic rooms for a property"""
    num_rooms = random.randint(3, 8)
    
    for i in range(num_rooms):
        room_name = random.choice(ARABIC_ROOM_NAMES)
        
        room_data = {
            'property': property_obj,
            'name': room_name,
            'room_type': random.choice(['bedroom', 'bathroom', 'kitchen', 'living_room', 'office']),
            'area_sqm': Decimal(random.uniform(10.0, 50.0)).quantize(Decimal('0.01')),
            'floor': random.randint(0, 3),
            'description': f"غرفة {room_name} مؤثثة بالكامل",
            'features': {
                'furnished': random.choice([True, False]),
                'air_conditioning': random.choice([True, False]),
            },
            'has_window': random.choice([True, False]),
            'has_bathroom': room_name in ['غرفة النوم الرئيسية', 'مجلس الرجال'],
        }
        
        Room.objects.create(**room_data)

def create_arabic_auctions(properties, users_data):
    """Create Arabic auctions"""
    print("\n🔨 إنشاء المزادات العربية...")
    
    auctions = []
    
    for i in range(10):  # Create 10 auctions
        property_obj = random.choice(properties)
        # Find suitable auctioneers or fallback to any user
        suitable_auctioneers = [u['user'] for u in users_data if u['role'] in ['auctioneer', 'administrator']]
        if not suitable_auctioneers:
            suitable_auctioneers = [u['user'] for u in users_data]  # Fallback to any user
        
        auctioneer = random.choice(suitable_auctioneers)
        
        start_time = timezone.now() + timedelta(days=random.randint(1, 30))
        end_time = start_time + timedelta(hours=random.randint(2, 48))
        
        auction_data = {
            'related_property': property_obj,
            'title': f"مزاد {property_obj.title}",
            'slug': f"auction-{i+1}-{property_obj.slug}",
            'description': f"مزاد علني لبيع {property_obj.title} في {property_obj.location.city}. فرصة استثمارية ممتازة.",
            'auction_type': random.choice(['public', 'private', 'sealed_bid']),
            'starting_bid': property_obj.market_value * Decimal('0.7'),  # Start at 70% of property value
            'current_bid': property_obj.market_value * Decimal('0.7'),
            'minimum_increment': Decimal(random.choice([1000, 5000, 10000])),
            'start_date': start_time,
            'end_date': end_time,
            'registration_deadline': start_time - timedelta(hours=24),
            'status': random.choice(['upcoming', 'active', 'ended']),
            'minimum_participants': random.randint(2, 10),
            'auto_extend_minutes': random.choice([5, 10, 15]),
            'max_extensions': random.randint(3, 10),
            'is_published': True,
        }
        
        auction, created = Auction.objects.get_or_create(
            slug=auction_data['slug'],
            defaults=auction_data
        )
        
        if created:
            auctions.append(auction)
            print(f"✅ تم إنشاء المزاد: {auction.title}")
            
            # Create bids for auction
            if auction.status in ['active', 'ended']:
                create_arabic_bids(auction, users_data)
    
    return auctions

def create_arabic_bids(auction, users_data):
    """Create Arabic bids for an auction"""
    num_bids = random.randint(2, 10)
    current_bid = auction.starting_bid
    
    for i in range(num_bids):
        bidder = random.choice([u['user'] for u in users_data])
            
        current_bid += auction.minimum_increment
        
        bid_data = {
            'auction': auction,
            'bidder': bidder,
            'bid_amount': current_bid,
            'max_bid_amount': current_bid + auction.minimum_increment,
            'bid_time': auction.start_date + timedelta(minutes=random.randint(1, 120)),
            'status': 'active',
            'notes': f'مزايدة من {bidder.first_name} {bidder.last_name}',
            'ip_address': f"192.168.1.{random.randint(1, 254)}",
            'is_verified': True,
        }
        
        Bid.objects.create(**bid_data)
    
    # Update auction current bid
    auction.current_bid = current_bid
    auction.bid_count = num_bids
    auction.last_bid_time = auction.start_date + timedelta(minutes=random.randint(1, 120))
    auction.save()

def create_arabic_maintenance_data(properties, users_data):
    """Create Arabic maintenance and rental data"""
    print("\n🔧 إنشاء بيانات الصيانة والإيجار...")
    
    # Create maintenance categories
    maintenance_categories = [
        'صيانة السантري', 'صيانة الكهرباء', 'صيانة التكييف', 'صيانة النجارة',
        'صيانة الدهان', 'صيانة الحدائق', 'تنظيف عام', 'إصلاحات طارئة'
    ]
    
    for cat_name in maintenance_categories:
        MaintenanceCategory.objects.get_or_create(
            name=cat_name,
            defaults={'description': f"جميع أعمال {cat_name} للعقارات"}
        )
    
    # Create worker categories  
    worker_categories = [
        'سباك', 'كهربائي', 'فني تكييف', 'نجار', 'دهان', 'بستاني', 'عامل نظافة'
    ]
    
    for cat_name in worker_categories:
        WorkerCategory.objects.get_or_create(
            name=cat_name,
            defaults={'description': f"فئة {cat_name}"}
        )
    
    # Create workers
    worker_names = [
        'أحمد محمد - سباك', 'خالد عبدالله - كهربائي', 'سعد الأحمد - فني تكييف',
        'محمد العتيبي - نجار', 'فهد الحربي - دهان', 'عبدالرحمن القحطاني - بستاني'
    ]
    
    for i, worker_name in enumerate(worker_names):
        full_name = worker_name.split(' - ')[0]
        specialty = worker_name.split(' - ')[1]
        name_parts = full_name.split(' ')
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        Worker.objects.get_or_create(
            email=f"worker{i+1}@maintenance.com",
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'phone': f"+966555{random.randint(100000, 999999)}",
                'hourly_rate': Decimal(random.randint(50, 200)),
                'rating': Decimal(random.uniform(3.5, 5.0)).quantize(Decimal('0.1')),
                'is_available': True,
                'employment_type': 'full_time',
                'status': 'active',
                'skill_level': random.choice(['beginner', 'intermediate', 'advanced', 'expert']),
                'national_id': f"1{random.randint(100000000, 999999999)}",
            }
        )
    
    # Create rental properties
    for property_obj in properties[:5]:  # Convert 5 properties to rental
        rental_data = {
            'base_property': property_obj,
            'monthly_rent': Decimal(random.randint(2000, 15000)),
            'security_deposit': Decimal(random.randint(5000, 30000)),
            'rental_status': random.choice(['available', 'occupied', 'maintenance']),
            'rental_type': random.choice(['short_term', 'long_term', 'monthly']),
            'furnished': random.choice(['fully_furnished', 'unfurnished', 'semi_furnished']),
            'utilities_included': random.choice([True, False]),
            'pets_allowed': random.choice([True, False]),
            'smoking_allowed': False,
            'minimum_lease_period': random.randint(3, 12),
            'maximum_lease_period': random.randint(12, 36),
            'parking_spaces': random.randint(0, 3),
        }
        
        RentalProperty.objects.get_or_create(
            base_property=property_obj,
            defaults=rental_data
        )

def create_arabic_messages(users_data):
    """Create Arabic messages"""
    print("\n💬 إنشاء الرسائل العربية...")
    
    message_subjects = [
        'استفسار حول العقار', 'طلب معاينة العقار', 'عرض شراء', 'طلب معلومات إضافية',
        'موعد زيارة', 'استفسار عن المزاد', 'طلب تقييم عقاري', 'شكوى صيانة'
    ]
    
    message_contents = [
        'السلام عليكم، أرغب في الاستفسار حول هذا العقار المعروض.',
        'هل يمكن ترتيب موعد لمعاينة العقار في أقرب وقت ممكن؟',
        'أود تقديم عرض شراء لهذا العقار، يرجى التواصل معي.',
        'أرجو تزويدي بمعلومات إضافية حول العقار والمنطقة.',
        'متى يمكن زيارة العقار؟ أنا متاح في أي وقت هذا الأسبوع.',
        'كيف يمكنني المشاركة في المزاد؟ وما هي الشروط المطلوبة؟',
        'أحتاج تقييم عقاري احترافي لهذه الوحدة السكنية.',
        'هناك مشكلة في السباكة تحتاج إلى صيانة عاجلة.'
    ]
    
    for i in range(20):  # Create 20 messages
        sender = random.choice([u['user'] for u in users_data])
        recipients_list = [u['user'] for u in users_data if u['user'] != sender]
        recipient = random.choice(recipients_list)
        
        message_data = {
            'sender': sender,
            'recipient': recipient,
            'subject': random.choice(message_subjects),
            'content': random.choice(message_contents),
            'is_read': random.choice([True, False]),
        }
        
        Message.objects.create(**message_data)

def create_arabic_bank_accounts(users_data):
    """Create Arabic bank accounts"""
    print("\n🏦 إنشاء الحسابات البنكية العربية...")
    
    saudi_banks = [
        'البنك الأهلي السعودي', 'بنك الرياض', 'البنك السعودي للاستثمار',
        'البنك السعودي الفرنسي', 'بنك الراجحي', 'البنك العربي الوطني',
        'بنك ساب', 'البنك السعودي الهولندي'
    ]
    
    for user_data in users_data[:10]:  # Create bank accounts for first 10 users
        user = user_data['user']
        
        bank_data = {
            'user': user,
            'bank_name': random.choice(saudi_banks),
            'account_number': f"SA{random.randint(1000000000000000000000, 9999999999999999999999)}",
            'account_holder_name': f"{user.first_name} {user.last_name}",
            'branch_name': f"فرع {random.choice(ARABIC_CITIES)}",
            'swift_code': f"RIBL{random.randint(1000, 9999)}",
            'is_primary': True,
            'is_active': True,
        }
        
        BankAccount.objects.get_or_create(
            user=user,
            account_number=bank_data['account_number'],
            defaults=bank_data
        )

def main():
    """Main function to create all Arabic test data"""
    print("🚀 بدء إنشاء البيانات التجريبية العربية")
    print("=" * 60)
    
    try:
        # Create users
        users_data = create_arabic_users()
        
        # Create locations
        locations = create_arabic_locations()
        
        # Create properties
        properties = create_arabic_properties(users_data, locations)
        
        # Create auctions
        auctions = create_arabic_auctions(properties, users_data)
        
        # Create maintenance data
        create_arabic_maintenance_data(properties, users_data)
        
        # Create messages
        create_arabic_messages(users_data)
        
        # Create bank accounts
        create_arabic_bank_accounts(users_data)
        
        print("\n" + "=" * 60)
        print("✅ تم إنشاء البيانات التجريبية العربية بنجاح!")
        print(f"👥 المستخدمين: {len(users_data)}")
        print(f"📍 المواقع: {len(locations)}")
        print(f"🏠 العقارات: {len(properties)}")
        print(f"🔨 المزادات: {len(auctions) if 'auctions' in locals() else 0}")
        print("=" * 60)
        
        # Print some sample data
        print("\n📊 عينة من البيانات المنشأة:")
        print("\n👥 عينة من المستخدمين:")
        for user_data in users_data[:3]:
            print(f"   - {user_data['name']} ({user_data['email']}) - {user_data['role']}")
            
        print("\n🏠 عينة من العقارات:")
        for prop in properties[:3]:
            print(f"   - {prop.title} ({prop.price} ريال)")
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()