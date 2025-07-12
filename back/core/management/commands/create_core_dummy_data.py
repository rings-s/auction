# core/management/commands/create_core_dummy_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
import random

# Import base models
from base.models import Property, Location

# Import accounts models
from accounts.models import UserProfile

# Import core models
from core.models import (
    FinancialTransaction, PropertyExpense,
    RentalProperty, Lease, MaintenanceRequest, Vendor,
    ContractTemplate, Contract, PropertyAnalytics
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates dummy Arabic data for core models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing core data...')
            self.clear_core_data()

        self.stdout.write('Creating dummy Arabic data for core models...')
        
        with transaction.atomic():
            # Create users first
            users = self.create_users()
            
            # Create properties (from base app)
            properties = self.get_or_create_properties()
            
            # Create enhanced user profiles (using accounts UserProfile)
            self.create_enhanced_profiles(users)
            
            # Create rental properties
            rental_properties = self.create_rental_properties(properties, users)
            
            # Create vendors
            vendors = self.create_vendors()
            
            # Create leases
            leases = self.create_leases(rental_properties, users)
            
            # Create financial transactions
            self.create_financial_transactions(users, properties)
            
            # Create property expenses
            self.create_property_expenses(properties, users)
            
            # Create maintenance requests
            self.create_maintenance_requests(properties, users, vendors)
            
            # Create contract templates
            templates = self.create_contract_templates(users)
            
            # Create contracts
            self.create_contracts(templates, users, properties, leases)
            
            # Create property analytics
            self.create_property_analytics(properties)

        self.stdout.write(
            self.style.SUCCESS('Successfully created dummy Arabic data for core models!')
        )

    def clear_core_data(self):
        """Clear existing core data"""
        PropertyAnalytics.objects.all().delete()
        Contract.objects.all().delete()
        ContractTemplate.objects.all().delete()
        MaintenanceRequest.objects.all().delete()
        PropertyExpense.objects.all().delete()
        FinancialTransaction.objects.all().delete()
        Lease.objects.all().delete()
        Vendor.objects.all().delete()
        RentalProperty.objects.all().delete()
        # Note: We don't delete UserProfile as it's used by accounts app
        # UserProfile enhanced fields will be cleared when users are recreated

    def create_users(self):
        """Create or get users with different roles"""
        users = {}
        
        # Create landlords
        for i in range(3):
            email = f'landlord{i+1}@example.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': ['أحمد', 'محمد', 'خالد'][i],
                    'last_name': ['العبدالله', 'المحمد', 'الأحمد'][i],
                    'role': 'landlord',
                    'is_verified': True,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users[f'landlord_{i+1}'] = user

        # Create property managers
        for i in range(2):
            email = f'manager{i+1}@example.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': ['سارة', 'فاطمة'][i],
                    'last_name': ['الزهراني', 'القحطاني'][i],
                    'role': 'property_manager',
                    'is_verified': True,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users[f'manager_{i+1}'] = user

        # Create tenants
        for i in range(5):
            email = f'tenant{i+1}@example.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': ['عبدالله', 'عمر', 'سلمان', 'ناصر', 'سعد'][i],
                    'last_name': ['الشمري', 'العتيبي', 'المطيري', 'الدوسري', 'الغامدي'][i],
                    'role': 'tenant',
                    'is_verified': True,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users[f'tenant_{i+1}'] = user

        # Create maintenance staff
        for i in range(2):
            email = f'maintenance{i+1}@example.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': ['يوسف', 'إبراهيم'][i],
                    'last_name': ['الحربي', 'البقمي'][i],
                    'role': 'maintenance_staff',
                    'is_verified': True,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users[f'maintenance_{i+1}'] = user

        return users

    def get_or_create_properties(self):
        """Get existing properties or create some basic ones"""
        properties = list(Property.objects.all()[:10])
        
        if len(properties) < 5:
            # Create some basic properties if none exist
            cities = ['الرياض', 'جدة', 'الدمام', 'مكة المكرمة', 'المدينة المنورة']
            states = ['منطقة الرياض', 'منطقة مكة المكرمة', 'المنطقة الشرقية', 'منطقة مكة المكرمة', 'منطقة المدينة المنورة']
            
            for i in range(5):
                location, _ = Location.objects.get_or_create(
                    city=cities[i],
                    state=states[i],
                    country='المملكة العربية السعودية'
                )
                
                property_obj, created = Property.objects.get_or_create(
                    title=f'عقار سكني رقم {i+1}',
                    defaults={
                        'property_type': 'residential',
                        'building_type': 'apartment',
                        'description': f'شقة سكنية فاخرة في {cities[i]} مكونة من 3 غرف نوم وصالة ومطبخ و2 حمام',
                        'size_sqm': Decimal(str(120 + i * 20)),
                        'location': location,
                        'address': f'حي الملك فهد، شارع الأمير محمد بن عبدالعزيز، {cities[i]}',
                        'market_value': Decimal(str(500000 + i * 100000)),
                        'deed_number': f'12345{i+1}67890',
                        'floors': 1,
                        'year_built': 2020 - i,
                        'is_published': True,
                    }
                )
                if created:
                    properties.append(property_obj)

        return properties

    def create_enhanced_profiles(self, users):
        """Create enhanced user profiles using accounts UserProfile"""
        for key, user in users.items():
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'identification_type': 'national_id',
                    'identification_number': f'1{random.randint(100000000, 999999999)}',
                    'identification_expiry': timezone.now().date() + timedelta(days=365*5),
                    'bank_account_name': f'{user.first_name} {user.last_name}',
                    'bank_account_number': f'SA{random.randint(1000000000000000, 9999999999999999)}',
                    'bank_name': random.choice(['البنك الأهلي السعودي', 'بنك الراجحي', 'بنك الرياض', 'بنك ساب']),
                    'emergency_contact_name': f'طوارئ {user.first_name}',
                    'emergency_contact_phone': f'05{random.randint(10000000, 99999999)}',
                    'identity_verified': True,
                    'bank_verified': random.choice([True, False]),
                    'tax_verified': random.choice([True, False]),
                }
            )

    def create_rental_properties(self, properties, users):
        """Create rental properties"""
        rental_properties = []
        landlords = [u for k, u in users.items() if 'landlord' in k]
        managers = [u for k, u in users.items() if 'manager' in k]
        
        for i, prop in enumerate(properties[:6]):
            rental_prop, created = RentalProperty.objects.get_or_create(
                base_property=prop,
                defaults={
                    'rental_type': random.choice(['long_term', 'short_term']),
                    'monthly_rent': Decimal(str(2000 + i * 500)),
                    'security_deposit': Decimal(str(4000 + i * 1000)),
                    'bedrooms': random.randint(1, 4),
                    'bathrooms': Decimal(str(random.randint(1, 3))),
                    'furnished': random.choice([True, False]),
                    'pets_allowed': random.choice([True, False]),
                    'available_date': timezone.now().date() + timedelta(days=random.randint(0, 60)),
                    'is_currently_rented': random.choice([True, False]),
                    'property_manager': random.choice(managers) if managers and random.choice([True, False]) else None,
                }
            )
            if created:
                rental_properties.append(rental_prop)

        return rental_properties

    def create_vendors(self):
        """Create vendor profiles"""
        vendors = []
        vendor_data = [
            {'name': 'شركة الصيانة المتقدمة', 'type': 'contractor', 'contact': 'أحمد الصيانة'},
            {'name': 'مؤسسة السباكة الحديثة', 'type': 'plumber', 'contact': 'محمد السباك'},
            {'name': 'شركة الكهرباء المتخصصة', 'type': 'electrician', 'contact': 'خالد الكهربائي'},
            {'name': 'مؤسسة التكييف والتبريد', 'type': 'hvac', 'contact': 'سالم التكييف'},
            {'name': 'شركة تنسيق الحدائق', 'type': 'landscaper', 'contact': 'عبدالله البستاني'},
            {'name': 'مؤسسة التنظيف الشامل', 'type': 'cleaner', 'contact': 'فاطمة التنظيف'},
        ]

        for data in vendor_data:
            vendor, created = Vendor.objects.get_or_create(
                company_name=data['name'],
                defaults={
                    'contact_person': data['contact'],
                    'vendor_type': data['type'],
                    'phone': f'05{random.randint(10000000, 99999999)}',
                    'email': f'{data["contact"].replace(" ", "").lower()}@example.com',
                    'license_number': f'LIC{random.randint(100000, 999999)}',
                    'hourly_rate': Decimal(str(random.randint(50, 200))),
                    'rating': Decimal(str(random.randint(35, 50) / 10)),
                    'is_active': True,
                    'is_preferred': random.choice([True, False]),
                }
            )
            if created:
                vendors.append(vendor)

        return vendors

    def create_leases(self, rental_properties, users):
        """Create lease agreements"""
        leases = []
        tenants = [u for k, u in users.items() if 'tenant' in k]
        landlords = [u for k, u in users.items() if 'landlord' in k]

        for i, rental_prop in enumerate(rental_properties[:4]):
            lease, created = Lease.objects.get_or_create(
                rental_property=rental_prop,
                tenant=random.choice(tenants),
                defaults={
                    'landlord': rental_prop.base_property.owner or random.choice(landlords),
                    'status': random.choice(['active', 'expired']),
                    'start_date': timezone.now().date() - timedelta(days=random.randint(30, 365)),
                    'end_date': timezone.now().date() + timedelta(days=random.randint(30, 365)),
                    'monthly_rent': rental_prop.monthly_rent,
                    'security_deposit': rental_prop.security_deposit,
                    'rent_due_day': random.randint(1, 28),
                    'late_fee': Decimal(str(random.randint(100, 500))),
                    'tenant_signed': True,
                    'landlord_signed': True,
                    'signing_date': timezone.now() - timedelta(days=random.randint(1, 30)),
                }
            )
            if created:
                leases.append(lease)

        return leases

    def create_financial_transactions(self, users, properties):
        """Create financial transactions"""
        transaction_types = ['rent_payment', 'security_deposit', 'maintenance_cost', 'utility_bill', 'insurance']
        statuses = ['completed', 'pending', 'failed']
        
        for i in range(20):
            payer = random.choice(list(users.values()))
            payee = random.choice(list(users.values()))
            while payee == payer:
                payee = random.choice(list(users.values()))

            FinancialTransaction.objects.create(
                transaction_type=random.choice(transaction_types),
                amount=Decimal(str(random.randint(500, 5000))),
                status=random.choice(statuses),
                payer=payer,
                payee=payee,
                related_property=random.choice(properties) if random.choice([True, False]) else None,
                due_date=timezone.now().date() + timedelta(days=random.randint(-30, 60)),
                paid_date=timezone.now().date() - timedelta(days=random.randint(0, 30)) if random.choice([True, False]) else None,
                description=f'دفعة {random.choice(["إيجار", "صيانة", "كهرباء", "ماء", "تأمين"])} - {i+1}',
                reference_number=f'REF-{random.randint(100000, 999999)}',
                notes=f'ملاحظات المعاملة رقم {i+1}',
            )

    def create_property_expenses(self, properties, users):
        """Create property expenses"""
        categories = ['maintenance', 'utilities', 'insurance', 'taxes', 'management']
        vendors = ['شركة الصيانة السريعة', 'مؤسسة المرافق', 'شركة التأمين', 'مصلحة الضرائب', 'إدارة العقارات']

        for i in range(15):
            PropertyExpense.objects.create(
                related_property=random.choice(properties),
                category=random.choice(categories),
                amount=Decimal(str(random.randint(200, 2000))),
                vendor_name=random.choice(vendors),
                description=f'مصروف {random.choice(["صيانة", "كهرباء", "ماء", "تأمين", "إدارة"])} - {i+1}',
                expense_date=timezone.now().date() - timedelta(days=random.randint(0, 90)),
                invoice_number=f'INV-{random.randint(100000, 999999)}',
                is_recurring=random.choice([True, False]),
                created_by=random.choice(list(users.values())),
            )

    def create_maintenance_requests(self, properties, users, vendors):
        """Create maintenance requests"""
        categories = ['plumbing', 'electrical', 'hvac', 'appliances', 'structural']
        priorities = ['low', 'medium', 'high', 'emergency']
        statuses = ['submitted', 'in_progress', 'completed', 'cancelled']
        
        titles = [
            'إصلاح تسريب في المطبخ',
            'صيانة مكيف الهواء',
            'إصلاح الإضاءة في الصالة',
            'تنظيف مجاري المياه',
            'صيانة الثلاجة',
            'إصلاح الباب الرئيسي',
            'صيانة السخان',
            'إصلاح النوافذ',
        ]

        for i in range(12):
            MaintenanceRequest.objects.create(
                related_property=random.choice(properties),
                title=random.choice(titles),
                description=f'وصف تفصيلي لطلب الصيانة رقم {i+1} - يتطلب إصلاح فوري',
                category=random.choice(categories),
                priority=random.choice(priorities),
                status=random.choice(statuses),
                requested_by=random.choice(list(users.values())),
                assigned_to=random.choice([None] + list(users.values())[:2]) if random.choice([True, False]) else None,
                scheduled_date=timezone.now().date() + timedelta(days=random.randint(1, 14)),
                completed_date=timezone.now().date() - timedelta(days=random.randint(0, 7)) if random.choice([True, False]) else None,
                estimated_cost=Decimal(str(random.randint(100, 1000))),
                actual_cost=Decimal(str(random.randint(100, 1000))) if random.choice([True, False]) else None,
                work_notes=f'ملاحظات العمل لطلب الصيانة رقم {i+1}',
            )

    def create_contract_templates(self, users):
        """Create contract templates"""
        templates = []
        template_data = [
            {
                'name': 'قالب عقد الإيجار السكني',
                'type': 'lease_agreement',
                'content': '''
عقد إيجار سكني

الطرف الأول (المؤجر): {{landlord_name}}
الطرف الثاني (المستأجر): {{tenant_name}}

العقار: {{property_address}}
مدة الإيجار: {{lease_duration}}
القيمة الإيجارية: {{monthly_rent}} ريال سعودي شهرياً

الشروط والأحكام:
1. يلتزم المستأجر بدفع الإيجار في الموعد المحدد
2. يحق للمؤجر زيارة العقار بموعد مسبق
3. المستأجر مسؤول عن الصيانة البسيطة
                '''
            },
            {
                'name': 'قالب عقد صيانة',
                'type': 'maintenance_contract',
                'content': '''
عقد صيانة العقارات

مقدم الخدمة: {{vendor_name}}
المالك: {{owner_name}}

نطاق الخدمة: {{service_scope}}
المدة: {{contract_duration}}
القيمة: {{contract_value}}

التزامات مقدم الخدمة:
1. الصيانة الدورية حسب الجدول المحدد
2. الاستجابة للطوارئ خلال 24 ساعة
3. استخدام قطع غيار أصلية
                '''
            }
        ]

        for data in template_data:
            template, created = ContractTemplate.objects.get_or_create(
                name=data['name'],
                defaults={
                    'contract_type': data['type'],
                    'template_content': data['content'],
                    'is_active': True,
                    'created_by': random.choice(list(users.values())),
                }
            )
            if created:
                templates.append(template)

        return templates

    def create_contracts(self, templates, users, properties, leases):
        """Create contracts"""
        statuses = ['draft', 'pending', 'signed', 'expired']
        
        for i in range(8):
            primary_party = random.choice(list(users.values()))
            secondary_party = random.choice(list(users.values()))
            while secondary_party == primary_party:
                secondary_party = random.choice(list(users.values()))

            Contract.objects.create(
                title=f'عقد رقم {i+1} - {random.choice(["إيجار", "صيانة", "خدمات"])}',
                template=random.choice(templates) if templates else None,
                primary_party=primary_party,
                secondary_party=secondary_party,
                content=f'محتوى العقد رقم {i+1} - نص العقد التفصيلي هنا',
                status=random.choice(statuses),
                effective_date=timezone.now().date() - timedelta(days=random.randint(0, 30)),
                expiration_date=timezone.now().date() + timedelta(days=random.randint(180, 730)),
                primary_signed=random.choice([True, False]),
                secondary_signed=random.choice([True, False]),
                signed_date=timezone.now() - timedelta(days=random.randint(0, 15)) if random.choice([True, False]) else None,
                related_property=random.choice(properties) if random.choice([True, False]) else None,
                lease=random.choice(leases) if leases and random.choice([True, False]) else None,
            )

    def create_property_analytics(self, properties):
        """Create property analytics"""
        for prop in properties[:5]:
            PropertyAnalytics.objects.get_or_create(
                base_property=prop,
                defaults={
                    'total_income_ytd': Decimal(str(random.randint(50000, 200000))),
                    'total_expenses_ytd': Decimal(str(random.randint(10000, 50000))),
                    'net_income_ytd': Decimal(str(random.randint(40000, 150000))),
                    'occupancy_rate': Decimal(str(random.randint(70, 100))),
                    'vacancy_days_ytd': random.randint(0, 90),
                    'maintenance_requests_ytd': random.randint(5, 25),
                    'maintenance_cost_ytd': Decimal(str(random.randint(2000, 15000))),
                    'roi_percentage': Decimal(str(random.randint(5, 15))),
                    'performance_score': random.randint(60, 95),
                }
            )