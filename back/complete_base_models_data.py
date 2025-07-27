#!/usr/bin/env python3
"""
Complete Base Models Data Creation - ALL Models with Arabic Data
Ensures every model in base app is created with proper Arabic test data
"""
import os
import sys
import django
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta, date
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
    'منال', 'رانيا', 'ريم', 'لينا', 'دانا', 'جواهر', 'أسماء', 'لطيفة', 'عبير'
]

ARABIC_LAST_NAMES = [
    'العبدالله', 'المحمد', 'الأحمد', 'السعد', 'الخالد', 'الفهد', 'العتيبي',
    'الشمري', 'القحطاني', 'الغامدي', 'الحربي', 'المطيري', 'العنزي', 'الدوسري',
    'الزهراني', 'الثقفي', 'الأسمري', 'العمري', 'الجهني', 'البقمي', 'الرشيدي'
]

class CompleteBaseModelCreator:
    """Creates comprehensive Arabic data for ALL base models"""
    
    def __init__(self):
        self.users_data = []
        self.locations = []
        self.properties = []
        self.auctions = []
        self.bids = []
        self.rooms = []
        self.messages = []
        self.rental_properties = []
        self.tenants = []
        self.leases = []
        self.workers = []
        self.maintenance_requests = []
        self.expenses = []
        self.bank_accounts = []
        self.payments = []
        self.analytics = []
        self.reports = []
        
    def create_all_models(self):
        """Create all base models with Arabic data"""
        print("🚀 Creating Complete Base Models with Arabic Data")
        print("=" * 80)
        
        # Core Models
        self.create_users()
        self.create_locations()
        self.create_properties()
        self.create_rooms()
        self.create_auctions()
        self.create_bids()
        self.create_messages()
        
        # Property Management Models
        self.create_rental_properties()
        self.create_tenants()
        self.create_leases()
        
        # Maintenance Models
        self.create_maintenance_categories()
        self.create_worker_categories()
        self.create_workers()
        self.create_maintenance_requests()
        
        # Financial Models
        self.create_expense_categories()
        self.create_expenses()
        self.create_bank_accounts()
        self.create_payments()
        
        # Analytics and Reporting
        self.create_property_analytics()
        self.create_reports()
        self.create_dashboard_metrics()
        
        # Final Statistics
        self.print_creation_summary()
        
    def create_users(self):
        """Create Arabic users with different roles"""
        print("\n👥 Creating Arabic Users...")
        
        roles = list(dict(CustomUser.ROLE_CHOICES).keys())
        
        for i in range(20):
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
                'phone_number': f"+966555{random.randint(100000, 999999)}",
                'date_of_birth': date(random.randint(1970, 2000), random.randint(1, 12), random.randint(1, 28))
            }
            
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults=user_data
            )
            
            if created:
                user.set_password('ArabicTest123!')
                user.save()
                
                # Update UserProfile with Arabic data
                profile = user.profile
                profile.identity_type = random.choice(['national_identity', 'residency'])
                profile.identity_number = f"1{random.randint(100000000, 999999999)}"
                profile.bio = f"مرحباً، أنا {first_name} {last_name} وأعمل في مجال العقارات والمزادات"
                profile.company_name = f"شركة {first_name} {last_name} العقارية المحدودة"
                profile.address = f"حي {random.choice(['النخيل', 'الملك فهد', 'العليا', 'الورود', 'السلام', 'الياسمين'])}"
                profile.city = random.choice(ARABIC_CITIES)
                profile.state = random.choice(ARABIC_STATES)
                profile.country = 'المملكة العربية السعودية'
                profile.postal_code = f"{random.randint(10000, 99999)}"
                profile.credit_limit = Decimal(random.randint(50000, 1000000))
                profile.rating = Decimal(random.uniform(3.0, 5.0)).quantize(Decimal('0.01'))
                profile.save()
                
                print(f"✅ تم إنشاء المستخدم: {first_name} {last_name} ({role})")
            
            self.users_data.append({
                'user': user,
                'email': email,
                'name': f"{first_name} {last_name}",
                'role': user.role
            })
        
        print(f"📊 إجمالي المستخدمين: {len(self.users_data)}")
    
    def create_locations(self):
        """Create Arabic locations"""
        print("\n📍 Creating Arabic Locations...")
        
        for i, city in enumerate(ARABIC_CITIES):
            state = ARABIC_STATES[i % len(ARABIC_STATES)]
            
            location_data = {
                'city': city,
                'state': state,
                'country': 'المملكة العربية السعودية',
                'postal_code': f"{random.randint(10000, 99999)}",
                'latitude': Decimal(random.uniform(16.0, 32.0)).quantize(Decimal('0.000001')),
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
            
            self.locations.append(location)
        
        print(f"📊 إجمالي المواقع: {len(self.locations)}")
    
    def create_properties(self):
        """Create Arabic properties"""
        print("\n🏠 Creating Arabic Properties...")
        
        property_types = [
            ('villa', 'فيلا'),
            ('apartment', 'شقة'),
            ('office', 'مكتب'),
            ('shop', 'متجر'),
            ('warehouse', 'مستودع'),
            ('land', 'قطعة أرض'),
            ('building', 'مبنى'),
            ('compound', 'مجمع'),
        ]
        
        property_descriptions = [
            'عقار فاخر بتشطيبات عالية الجودة ومرافق متكاملة',
            'وحدة سكنية واسعة في موقع مميز وحيوي',
            'مكتب تجاري في منطقة الأعمال المركزية',
            'متجر في شارع تجاري رئيسي عالي الكثافة',
            'مستودع واسع للتخزين والتوزيع بمرافق حديثة',
            'قطعة أرض للاستثمار العقاري في منطقة نامية',
            'مبنى تجاري متكامل الخدمات والمرافق',
            'مجمع سكني بمرافق ترفيهية وخدمية حديثة'
        ]
        
        for i in range(30):
            owner = random.choice([u['user'] for u in self.users_data])
            location = random.choice(self.locations)
            prop_type, prop_type_ar = random.choice(property_types)
            
            property_data = {
                'owner': owner,
                'title': f"{prop_type_ar} فاخرة في {location.city}",
                'slug': f"property-{i+1}-{prop_type}-{random.randint(1000, 9999)}",
                'description': random.choice(property_descriptions) + f" في منطقة {location.city} المميزة.",
                'property_type': prop_type,
                'building_type': random.choice(['residential', 'commercial', 'industrial', 'mixed_use']),
                'status': random.choice(['available', 'sold', 'reserved', 'under_construction']),
                'deed_number': f"DEED-{random.randint(100000, 999999)}",
                'size_sqm': Decimal(random.randint(100, 2000)),
                'floors': random.randint(1, 8),
                'year_built': random.randint(1990, 2024),
                'location': location,
                'address': f"حي {random.choice(['النخيل', 'الملك فهد', 'العليا', 'الورود', 'السلام', 'الياسمين', 'النزهة'])}، {location.city}",
                'market_value': Decimal(random.randint(300000, 8000000)),
                'minimum_bid': Decimal(random.randint(200000, 5000000)),
                'features': {
                    'bedrooms': random.randint(1, 8),
                    'bathrooms': random.randint(1, 6),
                    'parking': random.choice(['yes', 'no']),
                    'garden': random.choice(['yes', 'no']),
                    'furnished': random.choice(['yes', 'no', 'semi']),
                    'balcony': random.choice(['yes', 'no']),
                    'storage': random.choice(['yes', 'no']),
                },
                'amenities': {
                    'swimming_pool': random.choice([True, False]),
                    'gym': random.choice([True, False]),
                    'security': random.choice([True, False]),
                    'elevator': random.choice([True, False]),
                    'central_ac': random.choice([True, False]),
                    'internet': random.choice([True, False]),
                },
                'is_published': True,
                'is_featured': random.choice([True, False]),
            }
            
            property_obj, created = Property.objects.get_or_create(
                slug=property_data['slug'],
                defaults=property_data
            )
            
            if created:
                self.properties.append(property_obj)
                print(f"✅ تم إنشاء العقار: {property_obj.title}")
        
        print(f"📊 إجمالي العقارات: {len(self.properties)}")
    
    def create_rooms(self):
        """Create Arabic rooms for properties"""
        print("\n🚪 Creating Arabic Rooms...")
        
        room_names = [
            'غرفة المعيشة الرئيسية', 'غرفة النوم الرئيسية', 'غرفة النوم الثانية', 'غرفة الأطفال',
            'المطبخ الرئيسي', 'الحمام الرئيسي', 'حمام الضيوف', 'مجلس الرجال', 'مجلس النساء',
            'غرفة الطعام', 'المكتبة', 'غرفة التخزين', 'الحديقة الداخلية', 'السطح', 'موقف السيارات',
            'غرفة الخادمة', 'غرفة الغسيل', 'المدخل الرئيسي', 'الصالون', 'غرفة اللعب'
        ]
        
        room_types = ['bedroom', 'bathroom', 'kitchen', 'living_room', 'office', 'storage', 'utility', 'outdoor']
        
        total_rooms = 0
        for property_obj in self.properties:
            num_rooms = random.randint(4, 12)
            
            for i in range(num_rooms):
                room_name = random.choice(room_names)
                
                room_data = {
                    'property': property_obj,
                    'name': room_name,
                    'room_type': random.choice(room_types),
                    'area_sqm': Decimal(random.uniform(8.0, 80.0)).quantize(Decimal('0.01')),
                    'floor': random.randint(0, property_obj.floors),
                    'description': f"{room_name} مجهزة بالكامل بأحدث المعايير",
                    'features': {
                        'furnished': random.choice([True, False]),
                        'air_conditioning': random.choice([True, False]),
                        'natural_light': random.choice([True, False]),
                        'built_in_storage': random.choice([True, False]),
                    },
                    'has_window': random.choice([True, False]),
                    'has_bathroom': room_name in ['غرفة النوم الرئيسية', 'مجلس الرجال', 'مجلس النساء'],
                }
                
                room = Room.objects.create(**room_data)
                self.rooms.append(room)
                total_rooms += 1
        
        print(f"✅ تم إنشاء {total_rooms} غرفة لجميع العقارات")
        print(f"📊 إجمالي الغرف: {len(self.rooms)}")
    
    def create_auctions(self):
        """Create Arabic auctions"""
        print("\n🔨 Creating Arabic Auctions...")
        
        for i in range(15):
            property_obj = random.choice(self.properties)
            
            start_date = timezone.now() + timedelta(days=random.randint(-10, 30))
            end_date = start_date + timedelta(hours=random.randint(6, 168))  # 6 hours to 1 week
            
            auction_data = {
                'title': f"مزاد {property_obj.title}",
                'slug': f"auction-{i+1}-{property_obj.slug}-{random.randint(100, 999)}",
                'description': f"مزاد علني لبيع {property_obj.title} في {property_obj.location.city}. فرصة استثمارية ممتازة للحصول على عقار مميز في موقع حيوي.",
                'auction_type': random.choice(['public', 'private', 'sealed_bid', 'online']),
                'related_property': property_obj,
                'starting_bid': property_obj.market_value * Decimal('0.6'),
                'current_bid': property_obj.market_value * Decimal(random.uniform(0.6, 0.9)),
                'minimum_increment': Decimal(random.choice([1000, 5000, 10000, 25000])),
                'start_date': start_date,
                'end_date': end_date,
                'registration_deadline': start_date - timedelta(hours=random.randint(12, 72)),
                'status': random.choice(['upcoming', 'active', 'ended', 'cancelled']),
                'minimum_participants': random.randint(2, 15),
                'auto_extend_minutes': random.choice([5, 10, 15, 30]),
                'max_extensions': random.randint(3, 10),
                'is_published': True,
                'is_featured': random.choice([True, False]),
            }
            
            auction, created = Auction.objects.get_or_create(
                slug=auction_data['slug'],
                defaults=auction_data
            )
            
            if created:
                self.auctions.append(auction)
                print(f"✅ تم إنشاء المزاد: {auction.title}")
        
        print(f"📊 إجمالي المزادات: {len(self.auctions)}")
    
    def create_bids(self):
        """Create Arabic bids"""
        print("\n💰 Creating Arabic Bids...")
        
        total_bids = 0
        for auction in self.auctions:
            if auction.status in ['active', 'ended']:
                num_bids = random.randint(3, 20)
                current_bid = auction.starting_bid
                
                for i in range(num_bids):
                    bidder = random.choice([u['user'] for u in self.users_data])
                    current_bid += auction.minimum_increment * random.randint(1, 3)
                    
                    bid_data = {
                        'auction': auction,
                        'bidder': bidder,
                        'bid_amount': current_bid,
                        'max_bid_amount': current_bid + auction.minimum_increment * random.randint(1, 5),
                        'bid_time': auction.start_date + timedelta(minutes=random.randint(1, 2880)),
                        'status': random.choice(['active', 'outbid', 'withdrawn']),
                        'notes': f'مزايدة من {bidder.first_name} {bidder.last_name} - {random.choice(["مزايدة جدية", "عرض تنافسي", "مزايدة استراتيجية"])}',
                        'ip_address': f"192.168.{random.randint(1, 10)}.{random.randint(1, 254)}",
                        'is_verified': random.choice([True, False]),
                    }
                    
                    bid = Bid.objects.create(**bid_data)
                    self.bids.append(bid)
                    total_bids += 1
                
                # Update auction current bid
                auction.current_bid = current_bid
                auction.bid_count = num_bids
                auction.last_bid_time = auction.start_date + timedelta(minutes=random.randint(1, 2880))
                auction.save()
        
        print(f"✅ تم إنشاء {total_bids} مزايدة")
        print(f"📊 إجمالي المزايدات: {len(self.bids)}")
    
    def create_messages(self):
        """Create Arabic messages"""
        print("\n💬 Creating Arabic Messages...")
        
        message_subjects = [
            'استفسار حول العقار المعروض',
            'طلب معاينة العقار',
            'عرض شراء مباشر',
            'طلب معلومات إضافية',
            'موعد زيارة العقار',
            'استفسار عن المزاد',
            'طلب تقييم عقاري',
            'شكوى خدمة عملاء',
            'طلب استشارة عقارية',
            'معلومات عن التمويل'
        ]
        
        message_contents = [
            'السلام عليكم ورحمة الله وبركاته، أرغب في الاستفسار حول هذا العقار المعروض للبيع.',
            'أتمنى أن تساعدوني في ترتيب موعد لمعاينة العقار في أقرب وقت ممكن.',
            'أود تقديم عرض شراء جدي لهذا العقار، يرجى التواصل معي لمناقشة التفاصيل.',
            'أرجو تزويدي بمعلومات إضافية حول العقار والمنطقة المحيطة به.',
            'متى يمكنني زيارة العقار؟ أنا متاح في أي وقت خلال الأسبوع القادم.',
            'كيف يمكنني المشاركة في المزاد؟ وما هي الشروط والمتطلبات؟',
            'أحتاج إلى تقييم عقاري احترافي لهذه الوحدة السكنية.',
            'لدي شكوى بخصوص الخدمة المقدمة، أرجو المتابعة والرد السريع.',
            'أحتاج استشارة عقارية بخصوص الاستثمار في هذه المنطقة.',
            'هل يمكنكم مساعدتي في الحصول على تمويل عقاري لشراء هذا العقار؟'
        ]
        
        for i in range(25):
            sender = random.choice([u['user'] for u in self.users_data])
            recipients_list = [u['user'] for u in self.users_data if u['user'] != sender]
            recipient = random.choice(recipients_list)
            
            message_data = {
                'sender': sender,
                'recipient': recipient,
                'subject': random.choice(message_subjects),
                'body': random.choice(message_contents),
                'related_property': random.choice(self.properties) if random.choice([True, False]) else None,
                'status': random.choice(['unread', 'read', 'archived', 'deleted']),
                'priority': random.choice(['low', 'normal', 'high', 'urgent']),
                'read_at': timezone.now() - timedelta(minutes=random.randint(1, 1440)) if random.choice([True, False]) else None,
                'ip_address': f"192.168.{random.randint(1, 10)}.{random.randint(1, 254)}",
                'user_agent': 'Mozilla/5.0 (compatible; AuctionBot/1.0)',
            }
            
            message = Message.objects.create(**message_data)
            self.messages.append(message)
        
        print(f"✅ تم إنشاء {len(self.messages)} رسالة")
        print(f"📊 إجمالي الرسائل: {len(self.messages)}")
    
    def create_rental_properties(self):
        """Create rental properties"""
        print("\n🏠 Creating Rental Properties...")
        
        suitable_properties = [p for p in self.properties if p.property_type in ['villa', 'apartment', 'office', 'shop']]
        
        for property_obj in suitable_properties[:10]:  # Convert 10 properties to rental
            rental_data = {
                'base_property': property_obj,
                'monthly_rent': Decimal(random.randint(2000, 25000)),
                'security_deposit': property_obj.market_value * Decimal('0.05'),  # 5% of property value
                'rental_status': random.choice(['available', 'occupied', 'maintenance', 'reserved']),
                'rental_type': random.choice(['short_term', 'long_term', 'monthly', 'yearly']),
                'furnished': random.choice([True, False]),
                'utilities_included': random.choice([True, False]),
                'pets_allowed': random.choice([True, False]),
                'smoking_allowed': random.choice([True, False]),
                'minimum_lease_period': random.randint(3, 12),
                'maximum_lease_period': random.randint(12, 60),
                'parking_spaces': random.randint(0, 4),
                'utilities_details': {
                    'electricity': random.choice([True, False]),
                    'water': random.choice([True, False]),
                    'internet': random.choice([True, False]),
                    'maintenance': random.choice([True, False]),
                }
            }
            
            rental_property, created = RentalProperty.objects.get_or_create(
                base_property=property_obj,
                defaults=rental_data
            )
            
            if created:
                self.rental_properties.append(rental_property)
                print(f"✅ تم إنشاء عقار إيجار: {property_obj.title} - {rental_property.monthly_rent} ريال/شهر")
        
        print(f"📊 إجمالي العقارات الإيجارية: {len(self.rental_properties)}")
    
    def create_tenants(self):
        """Create tenants"""
        print("\n👥 Creating Tenants...")
        
        tenant_users = [u['user'] for u in self.users_data if u['role'] in ['tenant', 'user']]
        
        for i, user in enumerate(tenant_users[:8]):
            tenant_data = {
                'user': user,
                'national_id': f"2{random.randint(100000000, 999999999)}",
                'phone_number': f"+966555{random.randint(100000, 999999)}",
                'emergency_contact': f"{random.choice(ARABIC_FIRST_NAMES)} {random.choice(ARABIC_LAST_NAMES)}",
                'emergency_phone': f"+966555{random.randint(100000, 999999)}",
                'monthly_income': Decimal(random.randint(5000, 50000)),
                'occupation': random.choice(['مهندس', 'طبيب', 'محاسب', 'مدرس', 'موظف حكومي', 'رجل أعمال']),
                'employer': f"شركة {random.choice(['التقنية', 'الخدمات', 'التجارة', 'الصناعة'])} المتقدمة",
                'previous_address': f"حي {random.choice(['الفيحاء', 'المرسلات', 'الربوة', 'السويدي'])}، {random.choice(ARABIC_CITIES)}",
                'rental_history': {
                    'previous_rentals': random.randint(0, 3),
                    'payment_history': random.choice(['excellent', 'good', 'fair']),
                    'references': random.randint(1, 3)
                },
                'status': random.choice(['active', 'inactive', 'pending', 'blacklisted']),
                'credit_score': random.randint(300, 850),
                'notes': f'مستأجر موثوق مع سجل دفع جيد'
            }
            
            tenant = Tenant.objects.create(**tenant_data)
            self.tenants.append(tenant)
            print(f"✅ تم إنشاء المستأجر: {user.get_full_name()}")
        
        print(f"📊 إجمالي المستأجرين: {len(self.tenants)}")
    
    def create_leases(self):
        """Create lease agreements"""
        print("\n📄 Creating Lease Agreements...")
        
        for i, rental_property in enumerate(self.rental_properties[:6]):
            if rental_property.rental_status == 'occupied' and self.tenants:
                tenant = random.choice(self.tenants)
                
                start_date = timezone.now().date() - timedelta(days=random.randint(30, 365))
                lease_period = random.randint(6, 24)  # months
                end_date = start_date + timedelta(days=lease_period * 30)
                
                lease_data = {
                    'rental_property': rental_property,
                    'tenant': tenant,
                    'start_date': start_date,
                    'end_date': end_date,
                    'monthly_rent': rental_property.monthly_rent,
                    'security_deposit': rental_property.security_deposit,
                    'lease_duration_months': lease_period,
                    'status': random.choice(['active', 'expired', 'terminated', 'pending']),
                    'payment_frequency': random.choice(['monthly', 'quarterly', 'semi_annually', 'annually']),
                    'auto_renewal': random.choice([True, False]),
                    'late_fee_amount': Decimal(random.randint(100, 500)),
                    'terms_conditions': {
                        'pets_allowed': rental_property.pets_allowed,
                        'smoking_allowed': rental_property.smoking_allowed,
                        'subletting_allowed': random.choice([True, False]),
                        'maintenance_responsibility': random.choice(['tenant', 'landlord', 'shared'])
                    },
                    'documents': {
                        'signed_contract': True,
                        'id_copy': True,
                        'salary_certificate': True,
                        'bank_guarantee': random.choice([True, False])
                    },
                    'notes': f'عقد إيجار مع {tenant.user.get_full_name()} لمدة {lease_period} شهر'
                }
                
                lease = Lease.objects.create(**lease_data)
                self.leases.append(lease)
                print(f"✅ تم إنشاء عقد إيجار: {rental_property.base_property.title} - {tenant.user.get_full_name()}")
        
        print(f"📊 إجمالي عقود الإيجار: {len(self.leases)}")
    
    def create_maintenance_categories(self):
        """Create maintenance categories"""
        print("\n🔧 Creating Maintenance Categories...")
        
        categories = [
            ('السباكة', 'جميع أعمال السباكة والمياه'),
            ('الكهرباء', 'الصيانة الكهربائية والإضاءة'),
            ('التكييف', 'صيانة أنظمة التكييف والتهوية'),
            ('النجارة', 'أعمال النجارة والأبواب والنوافذ'),
            ('الدهان', 'أعمال الدهان والديكور'),
            ('الحدائق', 'صيانة الحدائق والمساحات الخضراء'),
            ('التنظيف', 'خدمات التنظيف العامة'),
            ('الأمن والسلامة', 'صيانة أنظمة الأمن والسلامة'),
        ]
        
        for name, description in categories:
            category_data = {
                'name': name,
                'description': description,
                'is_emergency': random.choice([True, False]),
                'estimated_cost_range': {
                    'min': random.randint(100, 500),
                    'max': random.randint(1000, 5000)
                }
            }
            
            MaintenanceCategory.objects.get_or_create(
                name=name,
                defaults=category_data
            )
        
        print(f"✅ تم إنشاء {len(categories)} فئة صيانة")
    
    def create_worker_categories(self):
        """Create worker categories"""
        print("\n👷 Creating Worker Categories...")
        
        categories = [
            ('سباك', 'فني سباكة معتمد'),
            ('كهربائي', 'فني كهرباء مرخص'),
            ('فني تكييف', 'متخصص في صيانة المكيفات'),
            ('نجار', 'حرفي نجارة ماهر'),
            ('دهان', 'فني دهان محترف'),
            ('بستاني', 'خبير في صيانة الحدائق'),
            ('عامل نظافة', 'متخصص في خدمات النظافة'),
            ('فني أمان', 'متخصص في أنظمة الأمن'),
        ]
        
        for name, description in categories:
            WorkerCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
        
        print(f"✅ تم إنشاء {len(categories)} فئة عمالة")
    
    def create_workers(self):
        """Create workers"""
        print("\n👨‍🔧 Creating Workers...")
        
        worker_names = [
            ('أحمد', 'محمد', 'سباك'),
            ('خالد', 'عبدالله', 'كهربائي'),
            ('سعد', 'الأحمد', 'فني تكييف'),
            ('محمد', 'العتيبي', 'نجار'),
            ('فهد', 'الحربي', 'دهان'),
            ('عبدالرحمن', 'القحطاني', 'بستاني'),
            ('طارق', 'الزهراني', 'عامل نظافة'),
            ('وليد', 'الغامدي', 'فني أمان'),
        ]
        
        for first_name, last_name, specialty in worker_names:
            worker_data = {
                'first_name': first_name,
                'last_name': last_name,
                'phone': f"+966555{random.randint(100000, 999999)}",
                'email': f"{first_name.lower()}.{last_name.lower()}@maintenance.com",
                'national_id': f"1{random.randint(100000000, 999999999)}",
                'date_of_birth': date(random.randint(1980, 2000), random.randint(1, 12), random.randint(1, 28)),
                'hire_date': timezone.now().date() - timedelta(days=random.randint(30, 1095)),
                'hourly_rate': Decimal(random.randint(50, 300)),
                'rating': Decimal(random.uniform(3.5, 5.0)).quantize(Decimal('0.1')),
                'is_available': random.choice([True, False]),
                'employment_type': random.choice(['full_time', 'part_time', 'contract']),
                'status': random.choice(['active', 'inactive', 'on_leave']),
                'skill_level': random.choice(['beginner', 'intermediate', 'advanced', 'expert']),
                'certifications': [f'شهادة {specialty}', 'شهادة السلامة المهنية'],
                'languages_spoken': ['العربية', 'الإنجليزية'],
                'emergency_contact': f"{random.choice(ARABIC_FIRST_NAMES)} {random.choice(ARABIC_LAST_NAMES)}",
                'emergency_phone': f"+966555{random.randint(100000, 999999)}",
                'address': f"حي {random.choice(['الصناعي', 'العمال', 'الشرقي'])}، {random.choice(ARABIC_CITIES)}",
            }
            
            worker, created = Worker.objects.get_or_create(
                email=worker_data['email'],
                defaults=worker_data
            )
            
            if created:
                self.workers.append(worker)
                print(f"✅ تم إنشاء العامل: {first_name} {last_name} ({specialty})")
        
        print(f"📊 إجمالي العمال: {len(self.workers)}")
    
    def create_maintenance_requests(self):
        """Create maintenance requests"""
        print("\n🔧 Creating Maintenance Requests...")
        
        request_descriptions = [
            'تسرب في المياه في الحمام الرئيسي',
            'عطل في مكيف الهواء في غرفة النوم',
            'مشكلة في الإضاءة في المطبخ',
            'حاجة لإصلاح الباب الرئيسي',
            'صيانة دورية للمصاعد',
            'تنظيف وصيانة المسبح',
            'إصلاح الأجهزة الكهربائية',
            'صيانة نظام الأمان والكاميرات',
        ]
        
        for i, property_obj in enumerate(self.properties[:10]):
            maintenance_data = {
                'property': property_obj,
                'reported_by': property_obj.owner,
                'title': f"طلب صيانة - {property_obj.title}",
                'description': random.choice(request_descriptions),
                'priority': random.choice(['low', 'medium', 'high', 'urgent']),
                'status': random.choice(['pending', 'in_progress', 'completed', 'cancelled']),
                'estimated_cost': Decimal(random.randint(200, 5000)),
                'actual_cost': Decimal(random.randint(150, 4500)) if random.choice([True, False]) else None,
                'scheduled_date': timezone.now().date() + timedelta(days=random.randint(1, 30)),
                'completion_date': timezone.now().date() - timedelta(days=random.randint(1, 15)) if random.choice([True, False]) else None,
                'notes': 'طلب صيانة عاجل يتطلب معالجة سريعة',
                'is_emergency': random.choice([True, False]),
                'tenant_notified': random.choice([True, False]),
            }
            
            if self.workers:
                maintenance_data['assigned_to'] = random.choice(self.workers)
            
            maintenance_request = MaintenanceRequest.objects.create(**maintenance_data)
            self.maintenance_requests.append(maintenance_request)
            print(f"✅ تم إنشاء طلب صيانة: {maintenance_request.title}")
        
        print(f"📊 إجمالي طلبات الصيانة: {len(self.maintenance_requests)}")
    
    def create_expense_categories(self):
        """Create expense categories"""
        print("\n💸 Creating Expense Categories...")
        
        categories = [
            ('الصيانة', 'مصاريف الصيانة والإصلاحات'),
            ('المرافق', 'فواتير الكهرباء والماء والهاتف'),
            ('التأمين', 'أقساط التأمين على العقارات'),
            ('الضرائب', 'الرسوم الحكومية والضرائب'),
            ('الأمن', 'خدمات الأمن والحراسة'),
            ('التنظيف', 'خدمات النظافة والتطهير'),
            ('التسويق', 'مصاريف الإعلان والتسويق'),
            ('إدارية', 'المصاريف الإدارية والعمومية'),
        ]
        
        for name, description in categories:
            ExpenseCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
        
        print(f"✅ تم إنشاء {len(categories)} فئة مصروفات")
    
    def create_expenses(self):
        """Create expenses"""
        print("\n💰 Creating Expenses...")
        
        expense_categories = ExpenseCategory.objects.all()
        
        for i, property_obj in enumerate(self.properties[:12]):
            for j in range(random.randint(2, 8)):
                category = random.choice(expense_categories)
                
                expense_data = {
                    'property': property_obj,
                    'category': category,
                    'title': f"{category.name} - {property_obj.title}",
                    'description': f"مصروف {category.name} للعقار {property_obj.title}",
                    'amount': Decimal(random.randint(100, 10000)),
                    'date': timezone.now().date() - timedelta(days=random.randint(1, 365)),
                    'payment_method': random.choice(['cash', 'bank_transfer', 'check', 'credit_card']),
                    'vendor': f"شركة {random.choice(['الخدمات', 'الصيانة', 'التنظيف', 'الأمان'])} المتقدمة",
                    'invoice_number': f"INV-{random.randint(100000, 999999)}",
                    'is_recurring': random.choice([True, False]),
                    'status': random.choice(['pending', 'paid', 'overdue', 'cancelled']),
                    'notes': f'مصروف {category.name} شهري للعقار',
                }
                
                expense = Expense.objects.create(**expense_data)
                self.expenses.append(expense)
        
        print(f"✅ تم إنشاء {len(self.expenses)} مصروف")
        print(f"📊 إجمالي المصروفات: {len(self.expenses)}")
    
    def create_bank_accounts(self):
        """Create bank accounts"""
        print("\n🏦 Creating Bank Accounts...")
        
        saudi_banks = [
            'البنك الأهلي السعودي',
            'بنك الرياض',
            'البنك السعودي للاستثمار',
            'البنك السعودي الفرنسي',
            'بنك الراجحي',
            'البنك العربي الوطني',
            'بنك ساب',
            'البنك السعودي الهولندي'
        ]
        
        for user_data in self.users_data[:15]:
            user = user_data['user']
            
            bank_data = {
                'user': user,
                'bank_name': random.choice(saudi_banks),
                'account_number': f"SA{random.randint(1000000000000000000000, 9999999999999999999999)}",
                'account_holder_name': f"{user.first_name} {user.last_name}",
                'branch_name': f"فرع {random.choice(ARABIC_CITIES)}",
                'swift_code': f"RIBL{random.randint(1000, 9999)}",
                'account_type': random.choice(['checking', 'savings', 'business']),
                'currency': 'SAR',
                'balance': Decimal(random.randint(1000, 500000)),
                'is_primary': True,
                'is_active': True,
                'is_verified': random.choice([True, False]),
                'created_at': timezone.now() - timedelta(days=random.randint(30, 1095)),
            }
            
            bank_account, created = BankAccount.objects.get_or_create(
                user=user,
                account_number=bank_data['account_number'],
                defaults=bank_data
            )
            
            if created:
                self.bank_accounts.append(bank_account)
                print(f"✅ تم إنشاء حساب بنكي: {user.get_full_name()} - {bank_account.bank_name}")
        
        print(f"📊 إجمالي الحسابات البنكية: {len(self.bank_accounts)}")
    
    def create_payments(self):
        """Create payments"""
        print("\n💳 Creating Payments...")
        
        payment_purposes = [
            'إيداع أولي للمزاد',
            'دفعة شراء العقار',
            'رسوم خدمة',
            'عمولة الوسيط',
            'رسوم تقييم العقار',
            'تأمين العقار',
            'رسوم تسجيل الصك',
            'رسوم نقل الملكية'
        ]
        
        for i in range(20):
            user = random.choice([u['user'] for u in self.users_data])
            property_obj = random.choice(self.properties)
            
            payment_data = {
                'user': user,
                'property': property_obj,
                'amount': Decimal(random.randint(1000, 100000)),
                'currency': 'SAR',
                'payment_method': random.choice(['bank_transfer', 'credit_card', 'cash', 'check']),
                'payment_type': random.choice(['deposit', 'purchase', 'commission', 'fee']),
                'status': random.choice(['pending', 'completed', 'failed', 'refunded']),
                'transaction_id': f"TXN-{random.randint(100000000, 999999999)}",
                'reference_number': f"REF-{random.randint(100000, 999999)}",
                'description': random.choice(payment_purposes),
                'payment_date': timezone.now() - timedelta(days=random.randint(1, 180)),
                'notes': f'دفعة مالية من {user.get_full_name()} للعقار {property_obj.title}',
                'is_refundable': random.choice([True, False]),
                'gateway_response': {
                    'status': 'success',
                    'gateway': random.choice(['paypal', 'stripe', 'bank']),
                    'reference': f"GTW-{random.randint(100000, 999999)}"
                }
            }
            
            payment = Payment.objects.create(**payment_data)
            self.payments.append(payment)
        
        print(f"✅ تم إنشاء {len(self.payments)} عملية دفع")
        print(f"📊 إجمالي المدفوعات: {len(self.payments)}")
    
    def create_property_analytics(self):
        """Create property analytics"""
        print("\n📈 Creating Property Analytics...")
        
        for property_obj in self.properties[:8]:
            analytics_data = {
                'property': property_obj,
                'total_views': random.randint(50, 2000),
                'unique_visitors': random.randint(30, 1500),
                'inquiry_count': random.randint(5, 100),
                'favorite_count': random.randint(2, 50),
                'average_time_on_page': random.randint(60, 600),  # seconds
                'conversion_rate': Decimal(random.uniform(1.0, 15.0)).quantize(Decimal('0.01')),
                'bounce_rate': Decimal(random.uniform(20.0, 80.0)).quantize(Decimal('0.01')),
                'monthly_views_data': {
                    'jan': random.randint(10, 200),
                    'feb': random.randint(15, 250),
                    'mar': random.randint(20, 300),
                    'apr': random.randint(25, 350),
                },
                'visitor_demographics': {
                    'age_groups': {
                        '25-35': random.randint(20, 40),
                        '35-45': random.randint(30, 50),
                        '45-55': random.randint(15, 35),
                    },
                    'locations': {
                        'riyadh': random.randint(40, 60),
                        'jeddah': random.randint(20, 40),
                        'dammam': random.randint(10, 30),
                    }
                },
                'last_updated': timezone.now(),
            }
            
            analytics = PropertyAnalytics.objects.create(**analytics_data)
            self.analytics.append(analytics)
            print(f"✅ تم إنشاء تحليلات: {property_obj.title}")
        
        print(f"📊 إجمالي تحليلات العقارات: {len(self.analytics)}")
    
    def create_reports(self):
        """Create reports"""
        print("\n📋 Creating Reports...")
        
        report_types = [
            ('monthly_sales', 'تقرير المبيعات الشهرية'),
            ('property_performance', 'تقرير أداء العقارات'),
            ('auction_summary', 'ملخص المزادات'),
            ('maintenance_costs', 'تقرير تكاليف الصيانة'),
            ('rental_income', 'تقرير إيرادات الإيجار'),
            ('user_activity', 'تقرير نشاط المستخدمين'),
        ]
        
        for report_type, title in report_types:
            report_data = {
                'title': title,
                'report_type': report_type,
                'description': f"تقرير تفصيلي حول {title}",
                'generated_by': random.choice([u['user'] for u in self.users_data]),
                'date_range_start': timezone.now().date() - timedelta(days=30),
                'date_range_end': timezone.now().date(),
                'parameters': {
                    'include_charts': True,
                    'format': 'pdf',
                    'language': 'ar',
                    'currency': 'SAR'
                },
                'data': {
                    'total_records': random.randint(50, 500),
                    'summary': f"ملخص {title}",
                    'metrics': {
                        'total_value': random.randint(100000, 5000000),
                        'count': random.randint(10, 100),
                        'percentage': random.uniform(5.0, 95.0)
                    }
                },
                'status': random.choice(['pending', 'generated', 'failed', 'archived']),
                'file_path': f"/reports/{report_type}_{timezone.now().strftime('%Y%m%d')}.pdf",
                'is_public': random.choice([True, False]),
            }
            
            report = Report.objects.create(**report_data)
            
            # Add some properties to the report
            sample_properties = random.sample(self.properties, min(3, len(self.properties)))
            report.properties.set(sample_properties)
            
            self.reports.append(report)
            print(f"✅ تم إنشاء التقرير: {title}")
        
        print(f"📊 إجمالي التقارير: {len(self.reports)}")
    
    def create_dashboard_metrics(self):
        """Create dashboard metrics"""
        print("\n📊 Creating Dashboard Metrics...")
        
        metrics_data = {
            'total_properties': len(self.properties),
            'active_auctions': len([a for a in self.auctions if a.status == 'active']),
            'total_bids': len(self.bids),
            'total_users': len(self.users_data),
            'monthly_revenue': Decimal(random.randint(100000, 1000000)),
            'properties_sold': random.randint(5, 25),
            'conversion_rate': Decimal(random.uniform(5.0, 25.0)).quantize(Decimal('0.01')),
            'average_property_value': Decimal(random.randint(500000, 2000000)),
            'top_performing_properties': [p.id for p in self.properties[:5]],
            'recent_activity_count': random.randint(20, 100),
            'pending_maintenance_requests': len([m for m in self.maintenance_requests if m.status == 'pending']),
            'occupied_rental_units': len([r for r in self.rental_properties if r.rental_status == 'occupied']),
        }
        
        dashboard_metrics = DashboardMetrics.objects.create(
            metrics_data=metrics_data,
            calculation_date=timezone.now().date(),
            is_current=True
        )
        
        print("✅ تم إنشاء مقاييس لوحة التحكم")
    
    def print_creation_summary(self):
        """Print comprehensive creation summary"""
        print("\n" + "=" * 80)
        print("🎉 COMPREHENSIVE BASE MODELS CREATION COMPLETED!")
        print("=" * 80)
        
        print(f"📊 CREATION SUMMARY:")
        print(f"   👥 Users: {len(self.users_data)}")
        print(f"   📍 Locations: {len(self.locations)}")
        print(f"   🏠 Properties: {len(self.properties)}")
        print(f"   🚪 Rooms: {len(self.rooms)}")
        print(f"   🔨 Auctions: {len(self.auctions)}")
        print(f"   💰 Bids: {len(self.bids)}")
        print(f"   💬 Messages: {len(self.messages)}")
        print(f"   🏘️  Rental Properties: {len(self.rental_properties)}")
        print(f"   👥 Tenants: {len(self.tenants)}")
        print(f"   📄 Leases: {len(self.leases)}")
        print(f"   👨‍🔧 Workers: {len(self.workers)}")
        print(f"   🔧 Maintenance Requests: {len(self.maintenance_requests)}")
        print(f"   💸 Expenses: {len(self.expenses)}")
        print(f"   🏦 Bank Accounts: {len(self.bank_accounts)}")
        print(f"   💳 Payments: {len(self.payments)}")
        print(f"   📈 Property Analytics: {len(self.analytics)}")
        print(f"   📋 Reports: {len(self.reports)}")
        
        print(f"\n🇸🇦 ARABIC DATA HIGHLIGHTS:")
        arabic_users = len([u for u in self.users_data if any(c in u['name'] for c in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')])
        arabic_properties = len([p for p in self.properties if any(c in p.title for c in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')])
        print(f"   👤 Users with Arabic names: {arabic_users}")
        print(f"   🏠 Properties with Arabic titles: {arabic_properties}")
        print(f"   📍 Arabic cities: {len([l for l in self.locations if any(c in l.city for c in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي')])}")
        
        print(f"\n💰 FINANCIAL SUMMARY:")
        total_property_value = sum([p.market_value for p in self.properties])
        total_bids_value = sum([b.bid_amount for b in self.bids])
        total_payments = sum([p.amount for p in self.payments])
        print(f"   🏠 Total Property Value: {total_property_value:,.2f} SAR")
        print(f"   💰 Total Bids Value: {total_bids_value:,.2f} SAR") 
        print(f"   💳 Total Payments: {total_payments:,.2f} SAR")
        
        print(f"\n✅ ALL BASE MODELS SUCCESSFULLY CREATED WITH ARABIC DATA!")
        print("=" * 80)

def main():
    """Main function"""
    try:
        creator = CompleteBaseModelCreator()
        creator.create_all_models()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()