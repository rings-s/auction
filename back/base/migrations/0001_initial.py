# Generated by Django 5.1.4 on 2025-02-24 12:59

import datetime
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('reserve_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('minimum_bid_increment', models.DecimalField(decimal_places=2, max_digits=15)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('ACTIVE', 'Active'), ('ENDED', 'Ended'), ('CANCELLED', 'Cancelled')], default='DRAFT', max_length=10)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auctions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('auto_bid_limit', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('status', models.CharField(default='PLACED', max_length=20)),
                ('ip_address', models.GenericIPAddressField()),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='base.auction')),
                ('bidder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-amount'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.FileField(blank=True, null=True, upload_to='category_icons/')),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='base.category')),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='auction',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='auctions', to='base.category'),
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('contract_type', models.CharField(choices=[('SALE', 'Sale Contract'), ('LEASE', 'Lease Contract'), ('CONDITIONAL', 'Conditional Sale'), ('INSTALLMENT', 'Installment Sale')], max_length=20)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('PENDING_SELLER', 'Pending Seller Approval'), ('PENDING_BUYER', 'Pending Buyer Approval'), ('ACTIVE', 'Active'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'), ('DISPUTED', 'Disputed')], default='DRAFT', max_length=20)),
                ('contract_value', models.DecimalField(decimal_places=2, max_digits=15)),
                ('deposit_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('contract_number', models.CharField(max_length=50, unique=True)),
                ('seller_signature_date', models.DateTimeField(blank=True, null=True)),
                ('buyer_signature_date', models.DateTimeField(blank=True, null=True)),
                ('review_date', models.DateTimeField(blank=True, null=True)),
                ('review_notes', models.TextField(blank=True)),
                ('auction', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='contract', to='base.auction')),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='buyer_contracts', to=settings.AUTH_USER_MODEL)),
                ('buyer_legal_rep', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='buyer_legal_contracts', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_contracts', to=settings.AUTH_USER_MODEL)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='seller_contracts', to=settings.AUTH_USER_MODEL)),
                ('seller_legal_rep', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seller_legal_contracts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ContractTermRevision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('terms_type', models.CharField(choices=[('GENERAL', 'Terms and Conditions'), ('PAYMENT', 'Payment Terms'), ('DELIVERY', 'Delivery Terms'), ('WARRANTY', 'Warranty Terms'), ('SPECIAL', 'Special Conditions')], max_length=20)),
                ('terms_content', models.TextField()),
                ('version_number', models.PositiveIntegerField(default=1)),
                ('is_current_version', models.BooleanField(default=True)),
                ('previous_terms', models.TextField()),
                ('new_terms', models.TextField()),
                ('revision_reason', models.TextField()),
                ('approval_date', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_revisions', to=settings.AUTH_USER_MODEL)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revisions', to='base.contract')),
                ('revised_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contract_revisions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('document_type', models.CharField(choices=[('CONTRACT', 'Contract Document'), ('LEGAL', 'Legal Document'), ('CERTIFICATE', 'Certificate'), ('INSPECTION', 'Inspection Report'), ('OWNERSHIP', 'Ownership Record'), ('SIGNATURE', 'Signature'), ('OTHER', 'Other')], max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('file', models.FileField(upload_to='auction_documents/')),
                ('description', models.TextField(blank=True)),
                ('verification_status', models.BooleanField(default=False)),
                ('typed_signature', models.TextField(blank=True, help_text='Typed signature content')),
                ('signer_role', models.CharField(blank=True, choices=[('SELLER', 'Seller'), ('BUYER', 'Buyer')], help_text='Role of the person signing', max_length=20, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='base.auction')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Factory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('total_area_sqm', models.DecimalField(decimal_places=2, max_digits=12)),
                ('built_up_area_sqm', models.DecimalField(decimal_places=2, max_digits=12)),
                ('location', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('production_capacity', models.TextField()),
                ('power_capacity', models.CharField(max_length=100)),
                ('water_supply', models.CharField(max_length=100)),
                ('waste_management', models.TextField()),
                ('environmental_certificates', models.JSONField()),
                ('infrastructure_details', models.JSONField()),
                ('utility_connections', models.JSONField()),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.auction')),
            ],
            options={
                'verbose_name': 'Factory',
                'verbose_name_plural': 'Factories',
            },
        ),
        migrations.CreateModel(
            name='HeavyVehicleAuction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('vehicle_type', models.CharField(max_length=100)),
                ('make', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('year', models.PositiveIntegerField()),
                ('load_capacity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('operating_hours', models.PositiveIntegerField()),
                ('engine_power', models.CharField(max_length=50)),
                ('registration_number', models.CharField(max_length=50)),
                ('compliance_certificates', models.JSONField()),
                ('maintenance_history', models.JSONField()),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.auction')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Machinery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('machine_type', models.CharField(max_length=100)),
                ('manufacturer', models.CharField(max_length=100)),
                ('model_number', models.CharField(max_length=100)),
                ('year_manufactured', models.PositiveIntegerField()),
                ('operating_hours', models.PositiveIntegerField()),
                ('power_requirements', models.CharField(max_length=100)),
                ('dimensions', models.CharField(max_length=100)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=10)),
                ('capacity', models.CharField(max_length=100)),
                ('maintenance_history', models.JSONField()),
                ('safety_certificates', models.JSONField()),
                ('technical_specifications', models.JSONField()),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.auction')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RealEstate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('property_type', models.CharField(choices=[('RESIDENTIAL', 'Residential'), ('COMMERCIAL', 'Commercial'), ('INDUSTRIAL', 'Industrial'), ('LAND', 'Land')], max_length=20)),
                ('size_sqm', models.DecimalField(decimal_places=2, max_digits=10)),
                ('location', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('bedrooms', models.PositiveIntegerField(blank=True, null=True)),
                ('bathrooms', models.PositiveIntegerField(blank=True, null=True)),
                ('year_built', models.PositiveIntegerField()),
                ('zoning_info', models.TextField()),
                ('legal_description', models.TextField()),
                ('property_condition', models.TextField()),
                ('historical_value', models.JSONField()),
                ('auction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='base.auction')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('payment_type', models.CharField(choices=[('DEPOSIT', 'Security Deposit'), ('FULL', 'Full Payment'), ('PARTIAL', 'Partial Payment'), ('REFUND', 'Refund')], max_length=20)),
                ('payment_method', models.CharField(choices=[('CREDIT_CARD', 'Credit Card'), ('BANK_TRANSFER', 'Bank Transfer'), ('ESCROW', 'Escrow'), ('STRIPE', 'Stripe'), ('PAYPAL', 'PayPal')], max_length=20)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('REFUNDED', 'Refunded'), ('DISPUTED', 'Disputed')], default='PENDING', max_length=20)),
                ('reference_number', models.CharField(max_length=100, unique=True)),
                ('payment_proof', models.FileField(blank=True, null=True, upload_to='payment_proofs/')),
                ('payment_date', models.DateTimeField(blank=True, null=True)),
                ('stripe_payment_id', models.CharField(blank=True, max_length=100)),
                ('paypal_transaction_id', models.CharField(blank=True, max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='base.auction')),
                ('escrow_agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='escrow_transactions', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='won_auctions', to=settings.AUTH_USER_MODEL)),
                ('winning_bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.bid')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('make', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('year', models.PositiveIntegerField()),
                ('mileage', models.PositiveIntegerField()),
                ('condition', models.CharField(max_length=50)),
                ('vin', models.CharField(max_length=17, unique=True)),
                ('engine_type', models.CharField(max_length=50)),
                ('transmission', models.CharField(max_length=50)),
                ('fuel_type', models.CharField(max_length=50)),
                ('color', models.CharField(max_length=50)),
                ('registration_number', models.CharField(max_length=50)),
                ('service_history', models.JSONField()),
                ('auction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='base.auction')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuctionTimer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('duration', models.CharField(choices=[('1D', '1 Day'), ('3D', '3 Days'), ('5D', '5 Days'), ('7D', '7 Days'), ('14D', '14 Days'), ('30D', '30 Days'), ('CUSTOM', 'Custom Duration')], max_length=10)),
                ('custom_duration', models.DurationField(blank=True, null=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_extended', models.BooleanField(default=False)),
                ('extension_count', models.PositiveIntegerField(default=0)),
                ('last_extension', models.DateTimeField(blank=True, null=True)),
                ('auto_extend', models.BooleanField(default=True)),
                ('extension_threshold', models.DurationField(default=datetime.timedelta(seconds=300), help_text='Time threshold before end to trigger extension')),
                ('extension_duration', models.DurationField(default=datetime.timedelta(seconds=300), help_text='Duration to extend when threshold is met')),
                ('auction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='timer', to='base.auction')),
            ],
            options={
                'indexes': [models.Index(fields=['start_time', 'end_time'], name='base_auctio_start_t_b1f0d7_idx'), models.Index(fields=['is_extended'], name='base_auctio_is_exte_a0c3ee_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='bid',
            index=models.Index(fields=['auction', 'bidder', 'status'], name='base_bid_auction_8421cb_idx'),
        ),
        migrations.AddIndex(
            model_name='bid',
            index=models.Index(fields=['created_at'], name='base_bid_created_2afa3d_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['slug'], name='base_catego_slug_c507a5_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['parent', 'is_active'], name='base_catego_parent__08aa61_idx'),
        ),
        migrations.AddIndex(
            model_name='auction',
            index=models.Index(fields=['status', 'start_time', 'end_time'], name='base_auctio_status_4c50d0_idx'),
        ),
        migrations.AddIndex(
            model_name='auction',
            index=models.Index(fields=['seller', 'status'], name='base_auctio_seller__01dab2_idx'),
        ),
        migrations.AddIndex(
            model_name='contract',
            index=models.Index(fields=['status', 'contract_type'], name='base_contra_status_be822c_idx'),
        ),
        migrations.AddIndex(
            model_name='contract',
            index=models.Index(fields=['seller', 'buyer'], name='base_contra_seller__11aef9_idx'),
        ),
        migrations.AddIndex(
            model_name='contract',
            index=models.Index(fields=['created_at'], name='base_contra_created_2386b4_idx'),
        ),
        migrations.AddIndex(
            model_name='contracttermrevision',
            index=models.Index(fields=['contract', 'created_at'], name='base_contra_contrac_8aa373_idx'),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['document_type', 'verification_status'], name='base_docume_documen_858d94_idx'),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['auction', 'document_type'], name='base_docume_auction_9c4c6d_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['status', 'payment_type'], name='base_transa_status_4a20fa_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['auction', 'winner'], name='base_transa_auction_a628c3_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['reference_number'], name='base_transa_referen_366095_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['payment_method'], name='base_transa_payment_6e9591_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['created_at'], name='base_transa_created_2b1acb_idx'),
        ),
    ]
