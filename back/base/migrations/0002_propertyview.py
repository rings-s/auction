# Generated by Django 5.1.4 on 2025-03-21 19:44

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_type', models.CharField(choices=[('OCEAN', 'إطلالة على المحيط'), ('MOUNTAIN', 'إطلالة على الجبل'), ('CITY', 'إطلالة على المدينة'), ('FOREST', 'إطلالة على الغابة'), ('LAKE', 'إطلالة على البحيرة'), ('CUSTOM', 'إطلالة مخصصة')], max_length=20, verbose_name='نوع الإطلالة')),
                ('size_sqm', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='المساحة (متر مربع)')),
                ('location', models.CharField(max_length=255, verbose_name='الموقع')),
                ('address', models.TextField(verbose_name='العنوان')),
                ('elevation', models.PositiveIntegerField(blank=True, null=True, verbose_name='الارتفاع')),
                ('view_direction', models.CharField(blank=True, max_length=50, verbose_name='اتجاه الإطلالة')),
                ('legal_description', models.TextField(verbose_name='الوصف القانوني')),
                ('condition', models.TextField(verbose_name='الحالة')),
                ('historical_views', models.JSONField(blank=True, default=dict, verbose_name='الإطلالات التاريخية')),
                ('images', models.JSONField(blank=True, default=list, verbose_name='الصور')),
                ('auction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='property_view', to='base.auction', verbose_name='المزاد')),
            ],
            options={
                'verbose_name': 'عرض العقار',
                'verbose_name_plural': 'عروض العقارات',
                'ordering': ['-id'],
                'indexes': [models.Index(fields=['view_type'], name='base_proper_view_ty_60b15c_idx'), models.Index(fields=['location'], name='base_proper_locatio_81513c_idx')],
            },
        ),
    ]
