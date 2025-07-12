# core/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

User = get_user_model()

from base.models import BaseModel, Property, Location

# -------------------------------------------------------------------------
# Streamlined Financial Management
# -------------------------------------------------------------------------

class FinancialTransaction(BaseModel):
    """Streamlined financial transaction tracking"""
    
    TRANSACTION_TYPES = [
        ('rent_payment', _('Rent Payment')),
        ('security_deposit', _('Security Deposit')),
        ('maintenance_cost', _('Maintenance Cost')),
        ('auction_payment', _('Auction Payment')),
        ('commission', _('Commission')),
        ('utility_bill', _('Utility Bill')),
        ('insurance', _('Insurance')),
        ('tax_payment', _('Tax Payment')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('overdue', _('Overdue')),
    ]

    # Core fields
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Parties
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    payee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    
    # Related objects
    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    
    # Key dates
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    
    # Essential info
    description = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Financial Transaction')
        verbose_name_plural = _('Financial Transactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['related_property', 'due_date']),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - ${self.amount}"

    @property
    def is_overdue(self):
        return self.due_date and timezone.now().date() > self.due_date and self.status == 'pending'

class PropertyExpense(BaseModel):
    """Simplified expense tracking"""
    
    CATEGORIES = [
        ('maintenance', _('Maintenance')),
        ('utilities', _('Utilities')),
        ('insurance', _('Insurance')),
        ('taxes', _('Taxes')),
        ('management', _('Management')),
        ('marketing', _('Marketing')),
        ('legal', _('Legal')),
        ('other', _('Other')),
    ]

    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=15, choices=CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    vendor_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    expense_date = models.DateField()
    invoice_number = models.CharField(max_length=100, blank=True)
    is_recurring = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Property Expense')
        verbose_name_plural = _('Property Expenses')
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.related_property.title} - {self.get_category_display()}: ${self.amount}"

# -------------------------------------------------------------------------
# Rental Property Management
# -------------------------------------------------------------------------

class RentalProperty(BaseModel):
    """Extends base Property for rental features"""
    
    RENTAL_TYPES = [
        ('long_term', _('Long-term Rental')),
        ('short_term', _('Short-term Rental')),
        ('vacation', _('Vacation Rental')),
        ('commercial', _('Commercial Rental')),
    ]

    # Link to base property
    base_property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='rental_details')
    
    # Essential rental info
    rental_type = models.CharField(max_length=15, choices=RENTAL_TYPES, default='long_term')
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Basic details
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    furnished = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    
    # Availability
    available_date = models.DateField(null=True, blank=True)
    is_currently_rented = models.BooleanField(default=False)
    
    # Management
    property_manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role__in': ['property_manager', 'landlord']},
        related_name='managed_properties'
    )

    class Meta:
        verbose_name = _('Rental Property')
        verbose_name_plural = _('Rental Properties')

    def __str__(self):
        return f"Rental: {self.base_property.title}"

    @property
    def monthly_yield(self):
        """Calculate monthly rental yield"""
        if self.base_property.market_value and self.base_property.market_value > 0:
            return (self.monthly_rent / self.base_property.market_value) * 100
        return 0

class Lease(BaseModel):
    """Streamlined lease management"""
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('terminated', _('Terminated')),
    ]

    # Core lease info
    lease_number = models.CharField(max_length=50, unique=True, blank=True)
    rental_property = models.ForeignKey(RentalProperty, on_delete=models.CASCADE, related_name='leases')
    
    # Parties
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_leases', 
                              limit_choices_to={'role': 'tenant'})
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='landlord_leases',
                                limit_choices_to={'role': 'landlord'})
    
    # Essential terms
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment terms
    rent_due_day = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(31)])
    late_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Digital signatures
    tenant_signed = models.BooleanField(default=False)
    landlord_signed = models.BooleanField(default=False)
    signing_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Lease Agreement')
        verbose_name_plural = _('Lease Agreements')
        ordering = ['-start_date']

    def __str__(self):
        return f"Lease {self.lease_number} - {self.rental_property.base_property.title}"

    def save(self, *args, **kwargs):
        if not self.lease_number:
            from datetime import datetime
            year = datetime.now().year
            count = Lease.objects.filter(created_at__year=year).count() + 1
            self.lease_number = f"LEASE-{year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date

    @property
    def days_remaining(self):
        if self.end_date:
            today = timezone.now().date()
            return (self.end_date - today).days if today <= self.end_date else 0
        return 0

# -------------------------------------------------------------------------
# Maintenance Management
# -------------------------------------------------------------------------

class MaintenanceRequest(BaseModel):
    """Streamlined maintenance requests"""
    
    PRIORITY_LEVELS = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('emergency', _('Emergency')),
    ]
    
    STATUS_CHOICES = [
        ('submitted', _('Submitted')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    CATEGORIES = [
        ('plumbing', _('Plumbing')),
        ('electrical', _('Electrical')),
        ('hvac', _('HVAC')),
        ('appliances', _('Appliances')),
        ('structural', _('Structural')),
        ('other', _('Other')),
    ]

    # Request details
    request_number = models.CharField(max_length=50, unique=True, blank=True)
    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='maintenance_requests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=15, choices=CATEGORIES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='submitted')
    
    # People
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_requests')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   limit_choices_to={'role__in': ['maintenance_staff', 'vendor']},
                                   related_name='assigned_maintenance')
    
    # Dates
    requested_date = models.DateField(auto_now_add=True)
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    
    # Cost
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Work details
    work_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Maintenance Request')
        verbose_name_plural = _('Maintenance Requests')
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.request_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.request_number:
            from datetime import datetime
            year = datetime.now().year
            count = MaintenanceRequest.objects.filter(created_at__year=year).count() + 1
            self.request_number = f"MR-{year}-{count:05d}"
        super().save(*args, **kwargs)

class Vendor(BaseModel):
    """Essential vendor information"""
    
    VENDOR_TYPES = [
        ('contractor', _('General Contractor')),
        ('plumber', _('Plumber')),
        ('electrician', _('Electrician')),
        ('hvac', _('HVAC Technician')),
        ('landscaper', _('Landscaper')),
        ('cleaner', _('Cleaning Service')),
        ('other', _('Other')),
    ]

    # Basic info
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    vendor_type = models.CharField(max_length=15, choices=VENDOR_TYPES)
    
    # Contact
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    # Business details
    license_number = models.CharField(max_length=100, blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Performance
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True,
                                validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_active = models.BooleanField(default=True)
    is_preferred = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')
        ordering = ['company_name']

    def __str__(self):
        return f"{self.company_name} ({self.get_vendor_type_display()})"

# -------------------------------------------------------------------------
# Contract Management
# -------------------------------------------------------------------------

class ContractTemplate(BaseModel):
    """Simple contract templates"""
    
    CONTRACT_TYPES = [
        ('lease_agreement', _('Lease Agreement')),
        ('maintenance_contract', _('Maintenance Contract')),
        ('vendor_agreement', _('Vendor Agreement')),
        ('other', _('Other')),
    ]

    name = models.CharField(max_length=255)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    template_content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Contract Template')
        verbose_name_plural = _('Contract Templates')

    def __str__(self):
        return f"{self.name} ({self.get_contract_type_display()})"

class Contract(BaseModel):
    """Digital contracts"""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending Signature')),
        ('signed', _('Fully Signed')),
        ('expired', _('Expired')),
    ]

    # Basic info
    contract_number = models.CharField(max_length=50, unique=True, blank=True)
    title = models.CharField(max_length=255)
    template = models.ForeignKey(ContractTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Parties
    primary_party = models.ForeignKey(User, on_delete=models.CASCADE, related_name='primary_contracts')
    secondary_party = models.ForeignKey(User, on_delete=models.CASCADE, related_name='secondary_contracts')
    
    # Content
    content = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    
    # Signatures
    primary_signed = models.BooleanField(default=False)
    secondary_signed = models.BooleanField(default=False)
    signed_date = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='contracts', null=True, blank=True)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='contracts', null=True, blank=True)

    class Meta:
        verbose_name = _('Contract')
        verbose_name_plural = _('Contracts')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contract_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.contract_number:
            from datetime import datetime
            year = datetime.now().year
            count = Contract.objects.filter(created_at__year=year).count() + 1
            self.contract_number = f"CONTRACT-{year}-{count:05d}"
        super().save(*args, **kwargs)

    @property
    def is_fully_signed(self):
        return self.primary_signed and self.secondary_signed

# -------------------------------------------------------------------------
# Dashboard Analytics
# -------------------------------------------------------------------------

class PropertyAnalytics(BaseModel):
    """Property performance analytics"""
    
    base_property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='analytics')
    
    # Financial metrics
    total_income_ytd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses_ytd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_income_ytd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Occupancy metrics
    occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    vacancy_days_ytd = models.PositiveIntegerField(default=0)
    
    # Maintenance metrics
    maintenance_requests_ytd = models.PositiveIntegerField(default=0)
    maintenance_cost_ytd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Performance scores
    roi_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    performance_score = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Last updated
    last_calculated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Property Analytics')
        verbose_name_plural = _('Property Analytics')

    def __str__(self):
        return f"Analytics: {self.base_property.title}"

    def calculate_metrics(self):
        """Calculate property performance metrics"""
        current_year = timezone.now().year
        
        # Calculate YTD financial metrics
        transactions = self.base_property.transactions.filter(created_at__year=current_year)
        income_transactions = transactions.filter(transaction_type__in=['rent_payment', 'security_deposit'])
        expense_transactions = transactions.filter(transaction_type__in=['maintenance_cost', 'utility_bill'])
        
        self.total_income_ytd = income_transactions.aggregate(
            total=models.Sum('amount'))['total'] or 0
        self.total_expenses_ytd = expense_transactions.aggregate(
            total=models.Sum('amount'))['total'] or 0
        self.net_income_ytd = self.total_income_ytd - self.total_expenses_ytd
        
        # Calculate ROI
        if self.base_property.market_value and self.base_property.market_value > 0:
            annual_income = self.total_income_ytd * (12 / timezone.now().month)
            self.roi_percentage = (annual_income / self.base_property.market_value) * 100
        
        # Calculate maintenance metrics
        maintenance_requests = self.base_property.maintenance_requests.filter(created_at__year=current_year)
        self.maintenance_requests_ytd = maintenance_requests.count()
        self.maintenance_cost_ytd = maintenance_requests.aggregate(
            total=models.Sum('actual_cost'))['total'] or 0
        
        # Calculate performance score (simplified)
        score = 50  # Base score
        if self.roi_percentage > 8:
            score += 20
        if self.occupancy_rate > 90:
            score += 20
        if self.maintenance_cost_ytd < (self.total_income_ytd * 0.1):  # Less than 10% of income
            score += 10
        
        self.performance_score = min(score, 100)
        self.save()