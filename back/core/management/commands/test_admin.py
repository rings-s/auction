from django.core.management.base import BaseCommand
from django.contrib import admin
from django.urls import reverse
from core.models import *

class Command(BaseCommand):
    help = 'Test admin interface for core models'

    def handle(self, *args, **options):
        self.stdout.write('=== CORE ADMIN TEST ===')
        
        models = [
            FinancialTransaction, PropertyExpense, RentalProperty, Lease,
            MaintenanceRequest, Vendor, ContractTemplate, Contract, PropertyAnalytics
        ]
        
        for model in models:
            try:
                # Check registration
                is_registered = admin.site.is_registered(model)
                count = model.objects.count()
                
                # Try to generate admin URL
                model_name = model._meta.model_name
                url = reverse(f'admin:core_{model_name}_changelist')
                
                self.stdout.write(
                    f'✅ {model._meta.verbose_name_plural}: '
                    f'Registered={is_registered}, Count={count}, URL={url}'
                )
                
                # Show sample data
                if count > 0:
                    sample = model.objects.first()
                    self.stdout.write(f'   Sample: {str(sample)[:100]}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ {model.__name__}: {e}')
                )
        
        self.stdout.write()
        self.stdout.write('=== ADMIN REGISTRY SUMMARY ===')
        self.stdout.write(f'Total registered models: {len(admin.site._registry)}')
        
        core_models = [m for m in admin.site._registry if m._meta.app_label == 'core']
        self.stdout.write(f'Core models in admin: {len(core_models)}')
        
        self.stdout.write()
        self.stdout.write('Admin should be available at: http://localhost:8451/admin/')
        self.stdout.write('Core models should appear under "Core Management" section')