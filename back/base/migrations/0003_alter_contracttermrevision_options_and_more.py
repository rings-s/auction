# Generated by Django 5.1.4 on 2025-02-25 08:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_message_paymentmethod'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contracttermrevision',
            options={'ordering': ['-created_at'], 'verbose_name': 'Contract Term Revision', 'verbose_name_plural': 'Contract Term Revisions'},
        ),
        migrations.RemoveIndex(
            model_name='contracttermrevision',
            name='base_contra_contrac_8aa373_idx',
        ),
        migrations.RemoveField(
            model_name='contracttermrevision',
            name='new_terms',
        ),
        migrations.AlterField(
            model_name='contract',
            name='buyer_legal_rep',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='buyer_legal_contracts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contract',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_contracts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contract',
            name='seller_legal_rep',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seller_legal_contracts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contracttermrevision',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_revisions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contracttermrevision',
            name='previous_terms',
            field=models.TextField(blank=True),
        ),
        migrations.AddIndex(
            model_name='contracttermrevision',
            index=models.Index(fields=['contract', 'terms_type', 'is_current_version'], name='base_contra_contrac_59b732_idx'),
        ),
        migrations.AddIndex(
            model_name='contracttermrevision',
            index=models.Index(fields=['created_at'], name='base_contra_created_35689d_idx'),
        ),
    ]
