import os
import django
from django.utils import timezone
from datetime import timedelta
import uuid

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')  # Matches your project name
django.setup()

from accounts.models import CustomUser
from base.models import (
    Category, Subcategory, Auction, AuctionTimer, RealEstate, Vehicle, Machinery, Factory,
    HeavyVehicleAuction, Bid, Transaction, Document, Contract, ContractTermRevision,
    Message, PaymentMethod, Notification
)

def create_dummy_data():
    # Clear existing data in base models (optional, comment out to append)
    Category.objects.all().delete()
    Subcategory.objects.all().delete()
    Auction.objects.all().delete()

    # Fetch existing users (using all 3 available users)
    try:
        users = list(CustomUser.objects.all())  # Take all users (3 in this case)
        if len(users) < 3:
            raise ValueError("Please ensure at least 3 users exist in the database.")
    except CustomUser.DoesNotExist:
        print("No users found. Please create users first.")
        return

    # Assign roles to users (reusing them for multiple purposes)
    seller1 = users[0]  # ringo@email.com (primary seller)
    seller2 = users[1]  # user@example.com (secondary seller)
    buyer = users[2]   # rings9619@gmail.com (buyer, also reused as legal and inspector)

    # Categories (Arabic names)
    categories_data = [
        ('REALESTATE', 'عقارات'),
        ('VEHICLE', 'مركبات'),
        ('MACHINERY', 'آلات'),
        ('FACTORY', 'مصانع'),
        ('HEAVYVEHICLE', 'مركبات ثقيلة')
    ]
    categories = {}
    for name, display_name in categories_data:
        category, _ = Category.objects.get_or_create(
            name=name,
            defaults={'slug': name.lower()}
        )
        categories[name] = category

    # Subcategories (Arabic names)
    subcategories_data = [
        ('REALESTATE', 'سكني', 'residential'),
        ('REALESTATE', 'تجاري', 'commercial'),
        ('VEHICLE', 'سيدان', 'sedan'),
        ('VEHICLE', 'دفع رباعي', 'suv'),
        ('MACHINERY', 'إنشاءات', 'construction'),
        ('FACTORY', 'تصنيع', 'manufacturing'),
        ('HEAVYVEHICLE', 'شاحنات', 'trucks')
    ]
    subcategories = {}
    for cat_name, sub_name, slug in subcategories_data:
        subcategory, _ = Subcategory.objects.get_or_create(
            category=categories[cat_name],
            name=sub_name,
            slug=slug
        )
        subcategories[f"{cat_name}_{sub_name}"] = subcategory

    # Auctions (Arabic data)
    now = timezone.now()
    auctions_data = [
        {
            'category': 'REALESTATE', 'subcategory': 'سكني', 'title': 'فيلا في الرياض',
            'description': 'فيلا فاخرة في حي الراجحي', 'seller': seller1,
            'start_time': now - timedelta(days=1), 'end_time': now + timedelta(days=5),
            'current_price': 2000000, 'reserve_price': 1800000, 'minimum_bid_increment': 50000,
            'status': 'ACTIVE', 'currency': 'SAR'
        },
        {
            'category': 'VEHICLE', 'subcategory': 'سيدان', 'title': 'تويوتا كامري 2023',
            'description': 'سيدان جديدة في جدة', 'seller': seller2,
            'start_time': now - timedelta(days=2), 'end_time': now + timedelta(days=3),
            'current_price': 85000, 'reserve_price': 80000, 'minimum_bid_increment': 1000,
            'status': 'ACTIVE', 'currency': 'SAR'
        },
        {
            'category': 'MACHINERY', 'subcategory': 'إنشاءات', 'title': 'حفار كاتربيلر',
            'description': 'حفار ثقيل في الدمام', 'seller': seller1,
            'start_time': now - timedelta(days=3), 'end_time': now - timedelta(hours=1),
            'current_price': 450000, 'reserve_price': 400000, 'minimum_bid_increment': 10000,
            'status': 'ENDED', 'currency': 'SAR'
        },
        {
            'category': 'FACTORY', 'subcategory': 'تصنيع', 'title': 'مصنع نسيج في مكة',
            'description': 'مصنع يعمل بكامل طاقته', 'seller': seller2,
            'start_time': now + timedelta(days=1), 'end_time': now + timedelta(days=7),
            'current_price': 5000000, 'reserve_price': 4800000, 'minimum_bid_increment': 100000,
            'status': 'DRAFT', 'currency': 'SAR'
        },
        {
            'category': 'HEAVYVEHICLE', 'subcategory': 'شاحنات', 'title': 'شاحنة مرسيدس 2022',
            'description': 'شاحنة ثقيلة في المدينة', 'seller': seller1,
            'start_time': now - timedelta(days=5), 'end_time': now - timedelta(days=2),
            'current_price': 300000, 'reserve_price': 280000, 'minimum_bid_increment': 5000,
            'status': 'ENDED', 'currency': 'SAR'
        }
    ]
    auctions = {}
    for auction_data in auctions_data:
        auction = Auction.objects.create(
            id=uuid.uuid4(),
            category=categories[auction_data['category']],
            subcategory=subcategories[f"{auction_data['category']}_{auction_data['subcategory']}"],
            title=auction_data['title'],
            description=auction_data['description'],
            seller=auction_data['seller'],
            start_time=auction_data['start_time'],
            end_time=auction_data['end_time'],
            current_price=auction_data['current_price'],
            reserve_price=auction_data['reserve_price'],
            minimum_bid_increment=auction_data['minimum_bid_increment'],
            status=auction_data['status'],
            currency=auction_data['currency']
        )
        auctions[auction_data['title']] = auction
        AuctionTimer.objects.create(
            auction=auction,
            duration='5D',
            start_time=auction_data['start_time'],
            end_time=auction_data['end_time'],
            extension_threshold=timedelta(minutes=5),
            extension_duration=timedelta(minutes=5)
        )

    # Specific Auction Types (Arabic data where applicable)
    RealEstate.objects.create(
        auction=auctions['فيلا في الرياض'],
        property_type='RESIDENTIAL',
        size_sqm=500,
        location='الرياض',
        address='حي الراجحي، الرياض',
        bedrooms=5,
        bathrooms=4,
        year_built=2020,
        zoning_info='منطقة سكنية',
        legal_description='شهادة ملكية الفيلا',
        property_condition='ممتازة',
        historical_value={'2020': 1800000, '2023': 2000000}
    )
    Vehicle.objects.create(
        auction=auctions['تويوتا كامري 2023'],
        make='تويوتا',
        model='كامري',
        year=2023,
        mileage=0,
        condition='جديدة',
        vin='JTNB11HK5J1234567',
        engine_type='V6',
        transmission='أوتوماتيكي',
        fuel_type='بنزين',
        color='أبيض',
        registration_number='KSA-1234',
        service_history={'2023': 'فحص أولي'}
    )
    Machinery.objects.create(
        auction=auctions['حفار كاتربيلر'],
        machine_type='حفار',
        manufacturer='كاتربيلر',
        model_number='CAT320',
        year_manufactured=2021,
        operating_hours=500,
        power_requirements='220V',
        dimensions='10م × 3م × 3م',
        weight=22000,
        capacity='20 طن',
        maintenance_history={'2022': 'تغيير الزيت'},
        safety_certificates={'2023': 'صالح'},
        technical_specifications={'الطاقة': '200 حصان'}
    )
    Factory.objects.create(
        auction=auctions['مصنع نسيج في مكة'],
        total_area_sqm=10000,
        built_up_area_sqm=6000,
        location='مكة',
        address='المنطقة الصناعية، مكة',
        production_capacity='1000 وحدة/يوم',
        power_capacity='500 كيلوواط',
        water_supply='بلدي',
        waste_management='نظام إعادة التدوير',
        environmental_certificates={'2023': 'معتمد أخضر'},
        infrastructure_details={'المباني': 3},
        utility_connections={'كهرباء': True}
    )
    HeavyVehicleAuction.objects.create(
        auction=auctions['شاحنة مرسيدس 2022'],
        vehicle_type='شاحنة',
        make='مرسيدس',
        model='أكتروس',
        year=2022,
        load_capacity=15000,
        operating_hours=1200,
        engine_power='400 حصان',
        registration_number='KSA-5678',
        compliance_certificates={'2022': 'صالح'},
        maintenance_history={'2023': 'خدمة المحرك'}
    )

    # Bids
    bids_data = [
        ('فيلا في الرياض', buyer, 2050000, None),
        ('تويوتا كامري 2023', buyer, 87000, 90000),
        ('حفار كاتربيلر', buyer, 460000, None),
        ('شاحنة مرسيدس 2022', buyer, 310000, None)
    ]
    bids = {}
    for auction_title, bidder, amount, auto_bid_limit in bids_data:
        bid = Bid.objects.create(
            id=uuid.uuid4(),
            auction=auctions[auction_title],
            bidder=bidder,
            amount=amount,
            auto_bid_limit=auto_bid_limit,
            ip_address='192.168.1.1'
        )
        bids[auction_title] = bid

    # Transactions
    transactions_data = [
        ('حفار كاتربيلر', buyer, 'FULL', 'BANK_TRANSFER'),
        ('شاحنة مرسيدس 2022', buyer, 'FULL', 'ESCROW')
    ]
    transactions = {}
    for auction_title, winner, payment_type, payment_method in transactions_data:
        winning_bid = bids[auction_title]
        transaction = Transaction.objects.create(
            id=uuid.uuid4(),
            auction=auctions[auction_title],
            winner=winner,
            winning_bid=winning_bid,
            amount=winning_bid.amount,
            currency='SAR',
            payment_type=payment_type,
            payment_method=payment_method,
            status='COMPLETED' if payment_type == 'FULL' else 'PENDING',
            reference_number=f'TXN-{uuid.uuid4().hex[:8]}',
            payment_date=now if payment_type == 'FULL' else None,
            escrow_agent=seller1 if payment_method == 'ESCROW' else None  # Reuse seller1 as escrow
        )
        transactions[auction_title] = transaction

    # Documents
    Document.objects.create(
        id=uuid.uuid4(),
        auction=auctions['حفار كاتربيلر'],
        document_type='OWNERSHIP',
        title='شهادة ملكية',
        description='دليل الملكية',
        uploaded_by=seller1,
        verification_status=True,
        verified_by=buyer  # Reuse buyer as inspector
    )

    # Contract
    transaction = transactions['حفار كاتربيلر']
    contract = Contract.objects.create(
        id=uuid.uuid4(),
        auction=auctions['حفار كاتربيلر'],
        seller=seller1,
        buyer=buyer,
        contract_type='SALE',
        status='ACTIVE',
        contract_value=460000,
        deposit_amount=100000,
        start_date=now.date(),
        contract_number=f'CONT-{uuid.uuid4().hex[:8]}',
        seller_legal_rep=seller2,  # Reuse seller2 as legal
        buyer_signature_date=now
    )
    ContractTermRevision.objects.create(
        contract=contract,
        terms_type='GENERAL',
        terms_content='شروط البيع القياسية',
        revision_reason='الشروط الأولية',
        revised_by=seller2,  # Reuse seller2 as legal
        version_number=1,
        is_current_version=True
    )

    # Messages
    Message.objects.create(
        sender=seller1,
        room_id='auction_chat_1',
        content='هل الحفار لا يزال متاحًا؟'
    )
    Message.objects.create(
        sender=buyer,
        room_id='auction_chat_1',
        content='نعم، في حالة ممتازة'
    )

    # Payment Methods
    PaymentMethod.objects.create(
        user=buyer,
        method_type='BANK_TRANSFER',
        details={'bank': 'بنك الراجحي', 'account_number': '1234567890'}
    )

    # Notifications
    Notification.objects.create(
        id=uuid.uuid4(),
        user=buyer,
        message='لقد فزت بمزاد الحفار كاتربيلر!',
        notification_type='AUCTION_WIN',
        related_object_id=auctions['حفار كاتربيلر'].id,
        related_object_type='Auction'
    )
    Notification.objects.create(
        id=uuid.uuid4(),
        user=seller1,
        message='مزايدة جديدة على فيلتك في الرياض',
        notification_type='BID',
        related_object_id=auctions['فيلا في الرياض'].id,
        related_object_type='Auction'
    )

    print("Dummy Arabic data created successfully!")

if __name__ == '__main__':
    create_dummy_data()