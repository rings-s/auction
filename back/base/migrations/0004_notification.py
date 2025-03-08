# Generated by Django 5.1.4 on 2025-02-27 15:08

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_contracttermrevision_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('BID', 'Bid Notification'), ('OUTBID', 'Outbid Notification'), ('AUCTION_END', 'Auction Ended'), ('AUCTION_WIN', 'Auction Won'), ('PAYMENT', 'Payment Notification'), ('CONTRACT', 'Contract Notification'), ('SYSTEM', 'System Notification')], max_length=20)),
                ('read', models.BooleanField(default=False)),
                ('displayed', models.BooleanField(default=False)),
                ('related_object_id', models.UUIDField(blank=True, null=True)),
                ('related_object_type', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', 'read'], name='base_notifi_user_id_39281e_idx'), models.Index(fields=['user', 'notification_type'], name='base_notifi_user_id_2afeba_idx'), models.Index(fields=['created_at'], name='base_notifi_created_81a211_idx')],
            },
        ),
    ]
