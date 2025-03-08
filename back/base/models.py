from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid
from datetime import timedelta
from django.utils import timezone
from accounts.models import CustomUser



class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created' and 'modified' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class Category(TimeStampedModel):
    """
    Model for auction categories
    """
    CATEGORY_CHOICES = (
        ('REALESTATE', 'Real Estate'),
        ('VEHICLE', 'Vehicle'),
        ('MACHINERY', 'Machinery'),
        ('FACTORY', 'Factory'),
        ('HEAVYVEHICLE', 'Heavy Vehicle'),
    )
    
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.get_name_display()


class Subcategory(TimeStampedModel):
    """
    Model for auction subcategories
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = 'Subcategories'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        return f"{self.category.get_name_display()} > {self.name}"


class AuctionTimer(TimeStampedModel):
    """
    Model for managing auction timers and duration
    """
    DURATION_CHOICES = (
        ('1D', '1 Day'),
        ('3D', '3 Days'),
        ('5D', '5 Days'),
        ('7D', '7 Days'),
        ('14D', '14 Days'),
        ('30D', '30 Days'),
        ('CUSTOM', 'Custom Duration'),
    )

    auction = models.OneToOneField(
        'Auction',
        on_delete=models.CASCADE,
        related_name='timer'
    )
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES)
    custom_duration = models.DurationField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_extended = models.BooleanField(default=False)
    extension_count = models.PositiveIntegerField(default=0)
    last_extension = models.DateTimeField(null=True, blank=True)
    auto_extend = models.BooleanField(default=True)
    extension_threshold = models.DurationField(
        default=timedelta(minutes=5),
        help_text='Time threshold before end to trigger extension'
    )
    extension_duration = models.DurationField(
        default=timedelta(minutes=5),
        help_text='Duration to extend when threshold is met'
    )

    class Meta:
        indexes = [
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['is_extended']),
        ]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError(_('End time must be after start time'))
        if self.duration == 'CUSTOM' and not self.custom_duration:
            raise ValidationError(_('Custom duration is required for custom timer'))

    def get_remaining_time(self):
        """
        Get remaining time as a dictionary with days, hours, minutes, seconds
        """
        now = timezone.now()
        if now >= self.end_time:
            return {
                'days': 0,
                'hours': 0,
                'minutes': 0,
                'seconds': 0,
                'total_seconds': 0
            }

        remaining = self.end_time - now
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds // 60) % 60
        seconds = remaining.seconds % 60

        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': remaining.total_seconds()
        }

    def extend_timer(self, duration=None):
        """
        Extend the auction timer
        """
        if duration is None:
            duration = self.extension_duration

        self.end_time = self.end_time + duration
        self.is_extended = True
        self.extension_count += 1
        self.last_extension = timezone.now()
        self.save()


class Auction(TimeStampedModel):
    """
    Base model for all auction types.
    """
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('ENDED', 'Ended'),
        ('CANCELLED', 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='auctions')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='auctions', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    seller = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='auctions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    current_price = models.DecimalField(max_digits=15, decimal_places=2)
    reserve_price = models.DecimalField(max_digits=15, decimal_places=2)
    minimum_bid_increment = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    currency = models.CharField(max_length=3, default='USD')
    main_image = models.ImageField(upload_to='auction_images/', null=True, blank=True)
    image_1 = models.ImageField(upload_to='auction_images/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='auction_images/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='auction_images/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='auction_images/', null=True, blank=True)
    image_5 = models.ImageField(upload_to='auction_images/', null=True, blank=True)

    def __str__(self):
        return self.title
        
    class Meta:
        indexes = [
            models.Index(fields=['status', 'start_time', 'end_time']),
            models.Index(fields=['seller', 'status']),
        ]
        ordering = ['-created_at']

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError(_('End time must be after start time'))
        if self.current_price < 0:
            raise ValidationError(_('Current price cannot be negative'))
        if self.reserve_price < 0:
            raise ValidationError(_('Reserve price cannot be negative'))


class RealEstate(TimeStampedModel):
    """
    Model for real estate property auctions.
    """
    PROPERTY_TYPE_CHOICES = (
        ('RESIDENTIAL', 'Residential'),
        ('COMMERCIAL', 'Commercial'),
        ('INDUSTRIAL', 'Industrial'),
        ('LAND', 'Land'),
    )

    auction = models.OneToOneField(Auction, on_delete=models.CASCADE)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    size_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    address = models.TextField()
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    year_built = models.PositiveIntegerField()
    zoning_info = models.TextField()
    legal_description = models.TextField()
    property_condition = models.TextField()
    historical_value = models.JSONField()  # Store historical price data
    property_image_1 = models.ImageField(upload_to='property_images/', null=True, blank=True)
    property_image_2 = models.ImageField(upload_to='property_images/', null=True, blank=True)
    property_image_3 = models.ImageField(upload_to='property_images/', null=True, blank=True)
    property_image_4 = models.ImageField(upload_to='property_images/', null=True, blank=True)
    property_image_5 = models.ImageField(upload_to='property_images/', null=True, blank=True)


class Vehicle(TimeStampedModel):
    """
    Model for vehicle auctions.
    """
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField()
    condition = models.CharField(max_length=50)
    vin = models.CharField(max_length=17, unique=True)
    engine_type = models.CharField(max_length=50)
    transmission = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    registration_number = models.CharField(max_length=50)
    service_history = models.JSONField()  # Store service history records
    vehicle_image_1 = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)
    vehicle_image_2 = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)
    vehicle_image_3 = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)
    vehicle_image_4 = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)
    vehicle_image_5 = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)


class Machinery(TimeStampedModel):
    """
    Model for industrial machinery auctions.
    """
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    machine_type = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    year_manufactured = models.PositiveIntegerField()
    operating_hours = models.PositiveIntegerField()
    power_requirements = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.CharField(max_length=100)
    maintenance_history = models.JSONField()
    safety_certificates = models.JSONField()
    technical_specifications = models.JSONField()
    machinery_image_1 = models.ImageField(upload_to='machinery_images/', null=True, blank=True)
    machinery_image_2 = models.ImageField(upload_to='machinery_images/', null=True, blank=True)
    machinery_image_3 = models.ImageField(upload_to='machinery_images/', null=True, blank=True)
    machinery_image_4 = models.ImageField(upload_to='machinery_images/', null=True, blank=True)
    machinery_image_5 = models.ImageField(upload_to='machinery_images/', null=True, blank=True)


class Factory(TimeStampedModel):
    """
    Model for factory auctions.
    """
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    total_area_sqm = models.DecimalField(max_digits=12, decimal_places=2)
    built_up_area_sqm = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)
    address = models.TextField()
    production_capacity = models.TextField()
    power_capacity = models.CharField(max_length=100)
    water_supply = models.CharField(max_length=100)
    waste_management = models.TextField()
    environmental_certificates = models.JSONField()
    infrastructure_details = models.JSONField()
    utility_connections = models.JSONField()
    factory_image_1 = models.ImageField(upload_to='factory_images/', null=True, blank=True)
    factory_image_2 = models.ImageField(upload_to='factory_images/', null=True, blank=True)
    factory_image_3 = models.ImageField(upload_to='factory_images/', null=True, blank=True)
    factory_image_4 = models.ImageField(upload_to='factory_images/', null=True, blank=True)
    factory_image_5 = models.ImageField(upload_to='factory_images/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Factory'
        verbose_name_plural = 'Factories'

    def __str__(self):
        return f"Factory at {self.location}"
    
    

class HeavyVehicleAuction(TimeStampedModel):
    """
    Model for heavy vehicle auctions.
    """
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    load_capacity = models.DecimalField(max_digits=10, decimal_places=2)
    operating_hours = models.PositiveIntegerField()
    engine_power = models.CharField(max_length=50)
    registration_number = models.CharField(max_length=50)
    compliance_certificates = models.JSONField()
    maintenance_history = models.JSONField()
    heavy_vehicle_image_1 = models.ImageField(upload_to='heavy_vehicle_images/', null=True, blank=True)
    heavy_vehicle_image_2 = models.ImageField(upload_to='heavy_vehicle_images/', null=True, blank=True)
    heavy_vehicle_image_3 = models.ImageField(upload_to='heavy_vehicle_images/', null=True, blank=True)
    heavy_vehicle_image_4 = models.ImageField(upload_to='heavy_vehicle_images/', null=True, blank=True)
    heavy_vehicle_image_5 = models.ImageField(upload_to='heavy_vehicle_images/', null=True, blank=True)


class Bid(TimeStampedModel):
    """
    Model for tracking bids on auctions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    auto_bid_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='PLACED')
    ip_address = models.GenericIPAddressField()

    class Meta:
        indexes = [
            models.Index(fields=['auction', 'bidder', 'status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-amount']

    def clean(self):
        if self.amount <= self.auction.current_price:
            raise ValidationError(_('Bid amount must be greater than current price'))



class Transaction(TimeStampedModel):
    """
    Model for tracking auction transactions and payments
    """
    TRANSACTION_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('DISPUTED', 'Disputed'),
    )

    PAYMENT_TYPE_CHOICES = (
        ('DEPOSIT', 'Security Deposit'),
        ('FULL', 'Full Payment'),
        ('PARTIAL', 'Partial Payment'),
        ('REFUND', 'Refund'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('CREDIT_CARD', 'Credit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('ESCROW', 'Escrow'),
        ('STRIPE', 'Stripe'),
        ('PAYPAL', 'PayPal'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name='transactions')
    winner = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='won_auctions')
    winning_bid = models.ForeignKey('Bid', on_delete=models.CASCADE)
    
    # Payment fields
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    
    # Payment processing details
    reference_number = models.CharField(max_length=100, unique=True)
    payment_proof = models.FileField(upload_to='payment_proofs/', null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # External payment IDs
    stripe_payment_id = models.CharField(max_length=100, blank=True)
    paypal_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Optional escrow details
    escrow_agent = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='escrow_transactions'
    )

    # Additional fields
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'payment_type']),
            models.Index(fields=['auction', 'winner']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def clean(self):
        if self.amount <= 0:
            raise ValidationError(_('Transaction amount must be greater than zero'))
        if self.payment_method == 'ESCROW' and not self.escrow_agent:
            raise ValidationError(_('Escrow agent is required for escrow payments'))
        
    def process_payment(self):
        """
        Process the payment based on the selected payment method
        """
        if self.payment_method == 'STRIPE':
            return self._process_stripe_payment()
        elif self.payment_method == 'PAYPAL':
            return self._process_paypal_payment()
        return False

    def _process_stripe_payment(self):
        """
        Process Stripe payment
        Implementation will depend on your Stripe configuration
        """
        try:
            # Stripe payment processing implementation
            self.status = 'PROCESSING'
            self.save()
            return True
        except Exception as e:
            self.status = 'FAILED'
            self.notes = f"Payment failed: {str(e)}"
            self.save()
            return False

    def _process_paypal_payment(self):
        """
        Process PayPal payment
        Implementation will depend on your PayPal configuration
        """
        try:
            # PayPal payment processing implementation
            self.status = 'PROCESSING'
            self.save()
            return True
        except Exception as e:
            self.status = 'FAILED'
            self.notes = f"Payment failed: {str(e)}"
            self.save()
            return False

    def process_refund(self):
        """
        Process refund based on the original payment method
        """
        if self.status != 'COMPLETED':
            raise ValidationError(_('Can only refund completed transactions'))
        
        try:
            # Implementation of refund logic based on payment method
            self.status = 'REFUNDED'
            self.save()
            return True
        except Exception as e:
            self.notes = f"Refund failed: {str(e)}"
            self.save()
            return False



class Document(TimeStampedModel):
    """
    Model for managing documents related to auctions and transactions.
    """
    DOCUMENT_TYPE_CHOICES = (
        ('CONTRACT', 'Contract Document'),
        ('LEGAL', 'Legal Document'),
        ('CERTIFICATE', 'Certificate'),
        ('INSPECTION', 'Inspection Report'),
        ('OWNERSHIP', 'Ownership Record'),
        ('SIGNATURE', 'Signature'),
        ('OTHER', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='auction_documents/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    verification_status = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        'accounts.CustomUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='verified_documents'
    )
    typed_signature = models.TextField(blank=True, help_text="Typed signature content")
    signer_role = models.CharField(
        max_length=20, 
        choices=(
            ('SELLER', 'Seller'),
            ('BUYER', 'Buyer')
        ),
        blank=True,
        null=True,
        help_text="Role of the person signing"
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['document_type', 'verification_status']),
            models.Index(fields=['auction', 'document_type']),
        ]
        ordering = ['-created_at']



class Contract(TimeStampedModel):
    """
    Model for managing contracts between sellers and buyers
    """
    CONTRACT_STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING_SELLER', 'Pending Seller Approval'),
        ('PENDING_BUYER', 'Pending Buyer Approval'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('DISPUTED', 'Disputed'),
    )

    CONTRACT_TYPE_CHOICES = (
        ('SALE', 'Sale Contract'),
        ('LEASE', 'Lease Contract'),
        ('CONDITIONAL', 'Conditional Sale'),
        ('INSTALLMENT', 'Installment Sale'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.OneToOneField(
        'Auction',
        on_delete=models.PROTECT,
        related_name='contract'
    )
    seller = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.PROTECT,
        related_name='seller_contracts'
    )
    buyer = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.PROTECT,
        related_name='buyer_contracts'
    )
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS_CHOICES, default='DRAFT')
    contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    contract_number = models.CharField(max_length=50, unique=True)
    
    # Legal Representatives
    seller_legal_rep = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seller_legal_contracts'
    )
    buyer_legal_rep = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='buyer_legal_contracts'
    )

    # Signatures are now handled through the Document model
    seller_signature_date = models.DateTimeField(null=True, blank=True)
    buyer_signature_date = models.DateTimeField(null=True, blank=True)
    
    # Audit Fields
    reviewed_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_contracts'
    )
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'contract_type']),
            models.Index(fields=['seller', 'buyer']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Contract {self.contract_number} - {self.get_status_display()}"

    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError(_('End date must be after start date'))
        if self.deposit_amount > self.contract_value:
            raise ValidationError(_('Deposit amount cannot be greater than contract value'))

    def get_current_terms(self, terms_type=None):
        """
        Get the most recent version of specified terms type or all terms
        """
        revisions = self.revisions
        if terms_type:
            revisions = revisions.filter(terms_type=terms_type)
        return revisions.order_by('-created_at').first()

    def get_signatures(self):
        """
        Get contract signatures from Document model
        """
        return self.auction.documents.filter(document_type='SIGNATURE')


class ContractTermRevision(TimeStampedModel):
    """
    Model for tracking revisions to contract terms
    """
    TERM_TYPE_CHOICES = (
        ('GENERAL', 'Terms and Conditions'),
        ('PAYMENT', 'Payment Terms'),
        ('DELIVERY', 'Delivery Terms'),
        ('WARRANTY', 'Warranty Terms'),
        ('SPECIAL', 'Special Conditions')
    )

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='revisions'
    )
    terms_type = models.CharField(max_length=20, choices=TERM_TYPE_CHOICES)
    terms_content = models.TextField()
    previous_terms = models.TextField(blank=True)
    revision_reason = models.TextField()
    revised_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.PROTECT,
        related_name='contract_revisions'
    )
    approved_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_revisions'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    version_number = models.PositiveIntegerField(default=1)
    is_current_version = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contract', 'terms_type', 'is_current_version']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Contract Term Revision'
        verbose_name_plural = 'Contract Term Revisions'

    def __str__(self):
        return f"{self.get_terms_type_display()} v{self.version_number} - {self.contract.contract_number}"

    def save(self, *args, **kwargs):
        # Set all other revisions of this type to not current
        if self.is_current_version:
            ContractTermRevision.objects.filter(
                contract=self.contract,
                terms_type=self.terms_type,
                is_current_version=True
            ).exclude(pk=self.pk).update(is_current_version=False)
        
        # Set version number
        if not self.pk:  # If this is a new revision
            latest_version = ContractTermRevision.objects.filter(
                contract=self.contract,
                terms_type=self.terms_type
            ).order_by('-version_number').first()
            
            if latest_version:
                self.version_number = latest_version.version_number + 1

        super().save(*args, **kwargs)
        
          
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    room_id = models.CharField(max_length=100)  # This could be a foreign key to a Room model
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.email}: {self.content[:20]}"
    
    
class PaymentMethod(TimeStampedModel):
    """
    Model for managing user payment methods
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=Transaction.PAYMENT_METHOD_CHOICES)
    details = models.JSONField()  # Store payment method details (e.g., card details, bank account)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'method_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.method_type} for {self.user}"
    
    
    


class Notification(models.Model):
    """
    Model for user notifications
    """
    NOTIFICATION_TYPES = (
        ('BID', 'Bid Notification'),
        ('OUTBID', 'Outbid Notification'),
        ('AUCTION_END', 'Auction Ended'),
        ('AUCTION_WIN', 'Auction Won'),
        ('PAYMENT', 'Payment Notification'),
        ('CONTRACT', 'Contract Notification'),
        ('SYSTEM', 'System Notification'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    read = models.BooleanField(default=False)
    displayed = models.BooleanField(default=False)
    related_object_id = models.UUIDField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read']),
            models.Index(fields=['user', 'notification_type']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.email}"