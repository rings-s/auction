import os
import django
from django.utils import timezone
from datetime import timedelta
import uuid

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')  # Replace with your project name
django.setup()

from accounts.models import CustomUser  # Assuming you have a CustomUser model
from base.models import (  # Replace 'your_app' with your actual app name
    Property, Auction, Document, Bid, Contract, Payment, Transaction,
    MessageThread, Message, ThreadParticipant, Notification
)

def create_dummy_data():
    # Clear existing data (optional, comment out to append)
    Property.objects.all().delete()
    Auction.objects.all().delete()

    # Fetch existing users (minimum 3 users required)
    try:
        users = list(CustomUser.objects.all()[:3])  # Take first 3 users
        if len(users) < 3:
            raise ValueError("يرجى التأكد من وجود 3 مستخدمين على الأقل في قاعدة البيانات.")
    except CustomUser.DoesNotExist:
        print("لم يتم العثور على مستخدمين. يرجى إنشاء مستخدمين أولاً.")
        return

    # Assign roles
    owner = users[0]    # المالك الأساسي
    bidder = users[1]   # المزايد
    auctioneer = users[2]  # منظم المزاد (reused as verifier)

    # Properties (Arabic data)
    now = timezone.now()
    properties_data = [
        {
            'property_number': 'PROP-001',
            'title': 'فيلا فاخرة في الرياض',
            'property_type': 'villa',
            'description': 'فيلا حديثة في حي الملقا',
            'owner': owner,
            'status': 'active',
            'address': 'حي الملقا، الرياض',
            'city': 'الرياض',
            'district': 'الملقا',
            'area': 450.50,
            'bedrooms': 5,
            'bathrooms': 4,
            'estimated_value': 2500000.00,
            'asking_price': 2600000.00,
            'year_built': 2022,
            'condition': 'excellent',
            'is_published': True,
            'publish_date': now - timedelta(days=2)
        },
        {
            'property_number': 'PROP-002',
            'title': 'شقة في جدة',
            'property_type': 'apartment',
            'description': 'شقة مطلة على البحر',
            'owner': owner,
            'status': 'pending_approval',
            'address': 'طريق الكورنيش، جدة',
            'city': 'جدة',
            'district': 'الحمراء',
            'area': 180.00,
            'bedrooms': 3,
            'bathrooms': 2,
            'estimated_value': 850000.00,
            'asking_price': 900000.00,
            'year_built': 2021,
            'condition': 'very_good',
            'is_published': False
        }
    ]
    properties = {}
    for prop_data in properties_data:
        property = Property.objects.create(**prop_data)
        properties[prop_data['title']] = property

    # Auctions
    auctions_data = [
        {
            'uuid': uuid.uuid4(),
            'related_property': properties['فيلا فاخرة في الرياض'],
            'title': 'مزاد فيلا الرياض',
            'description': 'مزاد على فيلا فاخرة',
            'auction_type': 'online',
            'status': 'active',
            'created_by': owner,
            'auctioneer': auctioneer,
            'start_date': now - timedelta(days=1),
            'end_date': now + timedelta(days=4),
            'starting_price': 2400000.00,
            'reserve_price': 2300000.00,
            'min_bid_increment': 50000.00,
            'is_published': True,
            'publish_date': now - timedelta(days=1)
        }
    ]
    auctions = {}
    for auction_data in auctions_data:
        auction = Auction.objects.create(**auction_data)
        auctions[auction_data['title']] = auction

    # Bids
    Bid.objects.create(
        auction=auctions['مزاد فيلا الرياض'],
        bidder=bidder,
        bid_amount=2450000.00,
        status='accepted'
    )

    # Documents
    Document.objects.create(
        document_number='DOC-001',
        title='صك ملكية الفيلا',
        document_type='deed',
        description='صك ملكية رسمي',
        related_property=properties['فيلا فاخرة في الرياض'],
        uploaded_by=owner,
        verification_status='verified',
        verified_by=auctioneer
    )

    # Contract
    contract = Contract.objects.create(
        contract_number='CONT-001',
        title='عقد بيع الفيلا',
        auction=auctions['مزاد فيلا الرياض'],
        related_property=properties['فيلا فاخرة في الرياض'],
        buyer=bidder,
        seller=owner,
        status='pending_buyer',
        contract_date=now.date(),
        contract_amount=2450000.00,
        deposit_amount=500000.00,
        payment_method='bank_transfer',
        payment_terms='الدفع خلال 7 أيام'
    )

    # Payment
    Payment.objects.create(
        payment_number='PAY-001',
        contract=contract,
        payer=bidder,
        payee=owner,
        payment_type='deposit',
        payment_method='bank_transfer',
        amount=500000.00,
        payment_date=now,
        status='completed'
    )

    # Transaction
    Transaction.objects.create(
        transaction_number='TXN-001',
        transaction_type='deposit',
        description='دفعة عربون الفيلا',
        amount=500000.00,
        from_user=bidder,
        to_user=owner,
        payment=Payment.objects.get(payment_number='PAY-001'),
        transaction_date=now,
        status='completed'
    )

    # Message Thread
    thread = MessageThread.objects.create(
        subject='استفسار حول الفيلا',
        thread_type='inquiry',
        related_property=properties['فيلا فاخرة في الرياض']
    )
    ThreadParticipant.objects.create(thread=thread, user=owner, role='owner')
    ThreadParticipant.objects.create(thread=thread, user=bidder, role='member')

    # Messages
    Message.objects.create(
        thread=thread,
        sender=bidder,
        content='هل يمكن زيارة الفيلا قبل المزاد؟',
        message_type='inquiry'
    )
    Message.objects.create(
        thread=thread,
        sender=owner,
        content='نعم، يمكن التنسيق لزيارة يوم الخميس',
        message_type='reply'
    )

    # Notification
    Notification.objects.create(
        recipient=bidder,
        notification_type='new_bid',
        title='مزايدة جديدة',
        content='تم تسجيل مزايدتك على فيلا الرياض بنجاح',
        related_auction=auctions['مزاد فيلا الرياض'],
        sent_at=now
    )

    print("تم إنشاء البيانات الوهمية باللغة العربية بنجاح!")

if __name__ == '__main__':
    create_dummy_data()
