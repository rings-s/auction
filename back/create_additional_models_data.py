#!/usr/bin/env python3
"""
Create comprehensive Arabic data for additional models:
- Expenses
- Reports  
- MaintenanceRequests
- Leases
- DashboardMetrics
"""
import os
import sys
import django
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta, date
import random
from decimal import Decimal
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

from accounts.models import CustomUser
from base.models import *

def create_additional_models_data():
    """Create comprehensive Arabic data for additional models"""
    print("🚀 CREATING ADDITIONAL MODELS DATA")
    print("=" * 80)
    
    # Arabic data constants
    arabic_cities = ['الرياض', 'جدة', 'مكة المكرمة', 'المدينة المنورة', 'الدمام', 'الخبر']
    arabic_vendor_names = ['شركة البناء المتقدم', 'مؤسسة الصيانة الشاملة', 'شركة التقنية الحديثة', 'مكتب الهندسة المعمارية']
    
    # Track created objects
    results = {
        'expenses': 0, 'reports': 0, 'maintenance_requests': 0, 
        'leases': 0, 'dashboard_metrics': 0
    }
    
    try:
        # Get existing data
        users = list(CustomUser.objects.all())
        properties = list(Property.objects.all())
        rental_properties = list(RentalProperty.objects.all())
        tenants = list(Tenant.objects.all())
        workers = list(Worker.objects.all())
        categories = list(MaintenanceCategory.objects.all())
        expense_categories = list(ExpenseCategory.objects.all())
        bank_accounts = list(BankAccount.objects.all())
        
        print(f"📋 Available data: {len(users)} users, {len(properties)} properties, {len(rental_properties)} rentals")
        
        # 1. Create Expenses
        print("\n💰 Creating Expenses...")
        expense_count = 0
        
        expense_titles = [
            'صيانة السباكة', 'إصلاح التكييف', 'تغيير الإضاءة', 'دهان الشقة',
            'تنظيف المبنى', 'صيانة المصعد', 'إصلاح الكهرباء', 'تجديد المطبخ'
        ]
        
        for i in range(15):  # Create 15 expenses
            property_obj = random.choice(properties)
            creator = random.choice(users)
            category = random.choice(expense_categories) if expense_categories else None
            bank_account = random.choice(bank_accounts) if bank_accounts else None
            
            base_amount = Decimal(random.randint(500, 5000))
            tax_amount = base_amount * Decimal('0.15')  # 15% VAT
            total_amount = base_amount + tax_amount
            
            expense_data = {
                'expense_property': property_obj,
                'category': category,
                'created_by': creator,
                'approved_by': random.choice(users) if random.choice([True, False]) else None,
                'title': random.choice(expense_titles),
                'description': f'تكلفة {random.choice(expense_titles)} للعقار {property_obj.title}',
                'expense_type': random.choice(['maintenance', 'utilities', 'management', 'insurance', 'cleaning', 'security', 'other']),
                'status': random.choice(['pending', 'approved', 'paid', 'cancelled']),
                'approval_status': random.choice(['pending', 'approved', 'rejected']),
                'amount': base_amount,
                'tax_amount': tax_amount,
                'discount_amount': Decimal('0.00'),
                'total_amount': total_amount,
                'currency': 'SAR',
                'requires_approval': random.choice([True, False]),
                'payment_method': random.choice(['cash', 'check', 'bank_transfer', 'credit_card']),
                'payment_date': timezone.now().date() if random.choice([True, False]) else None,
                'payment_reference': f'PAY-{random.randint(100000, 999999)}',
                'bank_account': bank_account,
                'vendor_name': random.choice(arabic_vendor_names),
                'vendor_phone': f'+966555{random.randint(100000, 999999)}',
                'vendor_email': f'vendor{i}@company.com',
                'vendor_address': f'حي التجاري، {random.choice(arabic_cities)}',
                'vendor_tax_id': f'3{random.randint(100000000, 999999999)}',
                'vendor_registration': f'CR{random.randint(1000000, 9999999)}',
                'invoice_number': f'INV-{random.randint(10000, 99999)}',
                'invoice_date': timezone.now().date(),
                'receipt_number': f'REC-{random.randint(10000, 99999)}',
                'purchase_order_number': f'PO-{random.randint(10000, 99999)}',
                'expense_date': timezone.now().date(),
                'due_date': timezone.now().date() + timedelta(days=30),
                'is_recurring': random.choice([True, False]),
                'recurring_frequency': random.choice(['monthly', 'quarterly', 'semi_annually', 'annually']),
                'is_emergency': random.choice([True, False]),
                'is_tax_deductible': random.choice([True, False]),
                'is_capital_expense': random.choice([True, False]),
                'project_name': f'مشروع صيانة {property_obj.title}',
                'work_order_number': f'WO-{random.randint(10000, 99999)}',
                'service_quality_rating': random.randint(3, 5),
                'vendor_performance_rating': random.randint(3, 5),
                'notes': 'ملاحظات إضافية حول المصروف',
                'internal_notes': 'ملاحظات داخلية للفريق',
                'approval_notes': 'تمت الموافقة على المصروف',
                'rejection_reason': '',
            }
            
            try:
                expense = Expense.objects.create(**expense_data)
                expense_count += 1
                if expense_count <= 3:
                    print(f"   ✅ {expense.title} - {expense.total_amount} ريال")
            except Exception as e:
                print(f"   ❌ Error creating expense: {e}")
        
        results['expenses'] = expense_count
        print(f"✅ Total Expenses: {expense_count}")
        
        # 2. Create Reports
        print("\n📊 Creating Reports...")
        report_count = 0
        
        report_types = [
            ('monthly_revenue', 'تقرير الإيرادات الشهرية'),
            ('expense_summary', 'ملخص المصروفات'),
            ('maintenance_report', 'تقرير الصيانة'),
            ('occupancy_report', 'تقرير الإشغال'),
            ('financial_summary', 'الملخص المالي'),
        ]
        
        for report_type, title in report_types:
            creator = random.choice(users)
            start_date = timezone.now().date() - timedelta(days=30)
            end_date = timezone.now().date()
            
            # Generate sample report data
            if report_type == 'monthly_revenue':
                report_data = {
                    'total_revenue': float(Decimal(random.randint(50000, 200000))),
                    'rental_income': float(Decimal(random.randint(30000, 120000))),
                    'auction_revenue': float(Decimal(random.randint(10000, 50000))),
                    'properties_count': len(properties),
                    'occupancy_rate': round(random.uniform(80.0, 95.0), 2)
                }
            elif report_type == 'expense_summary':
                report_data = {
                    'total_expenses': float(Decimal(random.randint(15000, 80000))),
                    'maintenance_costs': float(Decimal(random.randint(8000, 40000))),
                    'utility_costs': float(Decimal(random.randint(5000, 25000))),
                    'categories': ['صيانة', 'مرافق', 'خدمات'],
                    'top_vendors': arabic_vendor_names[:3]
                }
            else:
                report_data = {
                    'summary': f'تقرير {title} للفترة من {start_date} إلى {end_date}',
                    'metrics': {
                        'count': random.randint(10, 50),
                        'value': float(Decimal(random.randint(10000, 100000)))
                    }
                }
            
            report_data_obj = {
                'title': title,
                'report_type': report_type,
                'status': random.choice(['generating', 'completed', 'failed']),
                'generated_by': creator,
                'period_start': start_date,
                'period_end': end_date,
                'report_data': report_data,
                'summary': f'تقرير شامل عن {title} للفترة المحددة مع جميع التفاصيل والإحصائيات',
                'generation_time': timedelta(seconds=random.randint(5, 120)),
                'error_message': '',
            }
            
            try:
                report = Report.objects.create(**report_data_obj)
                report_count += 1
                print(f"   ✅ {report.title}")
            except Exception as e:
                print(f"   ❌ Error creating report: {e}")
        
        results['reports'] = report_count
        print(f"✅ Total Reports: {report_count}")
        
        # 3. Create Maintenance Requests
        print("\n🔧 Creating Maintenance Requests...")
        maintenance_count = 0
        
        maintenance_titles = [
            'تسريب في السباكة', 'عطل في التكييف', 'مشكلة في الإضاءة', 'إصلاح الباب',
            'تنظيف المجاري', 'صيانة المصعد', 'إصلاح الكهرباء', 'تغيير الزجاج'
        ]
        
        for i in range(12):  # Create 12 maintenance requests
            property_obj = random.choice(properties)
            requester = random.choice(users)
            worker = random.choice(workers) if workers else None
            category = random.choice(categories) if categories else None
            
            request_data = {
                'maintenance_property': property_obj,
                'category': category,
                'title': random.choice(maintenance_titles),
                'description': f'يرجى إصلاح {random.choice(maintenance_titles)} في العقار {property_obj.title} في أقرب وقت ممكن',
                'request_type': random.choice(['emergency', 'routine', 'preventive', 'cosmetic']),
                'priority': random.choice(['low', 'medium', 'high', 'urgent']),
                'status': random.choice(['open', 'in_progress', 'completed', 'cancelled']),
                'specific_location': random.choice(['المطبخ', 'الحمام', 'غرفة المعيشة', 'غرفة النوم']),
                'floor_number': random.randint(0, 3),
                'room_number': f'غرفة {random.randint(1, 10)}',
                'requested_by': requester,
                'assigned_worker': worker,
                'reported_date': timezone.now(),
                'scheduled_date': timezone.now() + timedelta(days=random.randint(1, 7)),
                'due_date': timezone.now() + timedelta(days=random.randint(3, 14)),
                'estimated_cost': Decimal(random.randint(200, 2000)),
                'actual_cost': Decimal(random.randint(150, 2500)) if random.choice([True, False]) else None,
                'labor_cost': Decimal(random.randint(100, 800)),
                'materials_cost': Decimal(random.randint(50, 1200)),
                'contractor_name': f'مقاول الصيانة {i+1}',
                'contractor_phone': f'+966555{random.randint(100000, 999999)}',
                'contractor_email': f'contractor{i}@maintenance.com',
                'contractor_license': f'LIC-{random.randint(100000, 999999)}',
                'tenant_access_required': random.choice([True, False]),
                'tenant_notified': random.choice([True, False]),
                'emergency_repair': random.choice([True, False]),
                'warranty_work': random.choice([True, False]),
                'warranty_expires': timezone.now().date() + timedelta(days=365) if random.choice([True, False]) else None,
                'safety_precautions': 'يجب ارتداء معدات السلامة وإغلاق الكهرباء',
                'permits_required': random.choice([True, False]),
                'permit_numbers': {'permits': [f'PERM-{random.randint(1000, 9999)}']} if random.choice([True, False]) else {},
                'work_description': 'وصف تفصيلي للأعمال المطلوبة والخطوات المتبعة',
                'materials_used': {'materials': ['مواد البناء', 'أدوات الإصلاح']},
                'tools_required': {'tools': ['المفكات', 'المطارق', 'معدات القياس']},
                'notes': 'ملاحظات إضافية حول طلب الصيانة',
                'quality_rating': random.randint(3, 5),
                'tenant_satisfaction': random.randint(3, 5),
                'owner_satisfaction': random.randint(3, 5),
                'follow_up_required': random.choice([True, False]),
                'follow_up_date': timezone.now() + timedelta(days=7) if random.choice([True, False]) else None,
                'is_recurring': random.choice([True, False]),
                'recurrence_pattern': random.choice(['weekly', 'monthly', 'quarterly', 'none']),
            }
            
            try:
                maintenance = MaintenanceRequest.objects.create(**request_data)
                maintenance_count += 1
                if maintenance_count <= 3:
                    print(f"   ✅ {maintenance.title} - {maintenance.priority} - {maintenance.status}")
            except Exception as e:
                print(f"   ❌ Error creating maintenance request: {e}")
        
        results['maintenance_requests'] = maintenance_count
        print(f"✅ Total Maintenance Requests: {maintenance_count}")
        
        # 4. Create Leases
        print("\n📋 Creating Leases...")
        lease_count = 0
        
        for i in range(min(8, len(rental_properties))):  # Create leases for rental properties
            if not tenants:
                print("   ⚠️  No tenants available, skipping lease creation")
                break
                
            rental_prop = rental_properties[i]
            tenant = random.choice(tenants)
            
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=365)  # 1 year lease
            
            lease_data = {
                'tenant': tenant,
                'rental_property': rental_prop,
                'lease_number': f'LEASE-{random.randint(100000, 999999)}',
                'status': random.choice(['active', 'expired', 'terminated', 'pending']),
                'start_date': start_date,
                'end_date': end_date,
                'signed_date': start_date - timedelta(days=random.randint(1, 30)),
                'monthly_rent': rental_prop.monthly_rent,
                'security_deposit': rental_prop.security_deposit,
                'payment_frequency': 'monthly',
                'payment_due_day': random.randint(1, 28),
                'late_fee_amount': Decimal('500.00'),
                'late_fee_grace_period': 5,
                'terms_and_conditions': '''
شروط وأحكام عقد الإيجار:
1. يلتزم المستأجر بدفع الإيجار في الموعد المحدد
2. يُمنع إجراء تعديلات على العقار بدون إذن خطي
3. المحافظة على نظافة العقار وحسن استخدامه
4. عدم استخدام العقار لأغراض غير مصرح بها
                '''.strip(),
                'special_clauses': 'بنود خاصة: يُسمح بالحيوانات الأليفة مقابل وديعة إضافية',
                'renewal_option': random.choice([True, False]),
                'rent_increase_percentage': Decimal('5.00'),
                'utilities_included': {
                    'water': True,
                    'electricity': False,
                    'internet': True,
                    'maintenance': True
                },
                'tenant_responsibilities': {
                    'responsibilities': [
                        'دفع فواتير الكهرباء',
                        'المحافظة على نظافة العقار',
                        'الإبلاغ عن أي أضرار فوراً'
                    ]
                },
                'landlord_responsibilities': {
                    'responsibilities': [
                        'صيانة الأنظمة الأساسية',
                        'توفير الخدمات المتفق عليها',
                        'إصلاح الأعطال الكبيرة'
                    ]
                },
                'auto_renewal': random.choice([True, False]),
                'renewal_notice_period': 60,
            }
            
            try:
                lease = Lease.objects.create(**lease_data)
                lease_count += 1
                if lease_count <= 3:
                    print(f"   ✅ عقد إيجار {lease.lease_number} - {lease.monthly_rent} ريال/شهر")
            except Exception as e:
                print(f"   ❌ Error creating lease: {e}")
        
        results['leases'] = lease_count
        print(f"✅ Total Leases: {lease_count}")
        
        # 5. Create Dashboard Metrics
        print("\n📈 Creating Dashboard Metrics...")
        metrics_count = 0
        
        metric_types = [
            'revenue_summary',
            'property_performance', 
            'maintenance_overview',
            'tenant_analytics',
            'expense_tracking'
        ]
        
        for user in users[:10]:  # Create metrics for first 10 users
            for metric_type in metric_types:
                
                if metric_type == 'revenue_summary':
                    metric_data = {
                        'total_revenue': float(Decimal(random.randint(50000, 200000))),
                        'monthly_growth': round(random.uniform(-5.0, 15.0), 2),
                        'revenue_sources': {
                            'rental': float(Decimal(random.randint(30000, 120000))),
                            'sales': float(Decimal(random.randint(10000, 50000))),
                            'services': float(Decimal(random.randint(5000, 25000)))
                        }
                    }
                elif metric_type == 'property_performance':
                    metric_data = {
                        'total_properties': len(properties),
                        'occupied_properties': random.randint(int(len(properties) * 0.7), len(properties)),
                        'average_occupancy': round(random.uniform(75.0, 95.0), 2),
                        'top_performing_properties': [
                            {'name': 'فيلا الرياض', 'revenue': 45000},
                            {'name': 'شقة جدة', 'revenue': 38000}
                        ]
                    }
                elif metric_type == 'maintenance_overview':
                    metric_data = {
                        'pending_requests': random.randint(3, 15),
                        'completed_requests': random.randint(20, 50),
                        'average_completion_time': round(random.uniform(2.0, 8.0), 1),
                        'maintenance_costs': float(Decimal(random.randint(8000, 25000)))
                    }
                elif metric_type == 'tenant_analytics':
                    metric_data = {
                        'total_tenants': len(tenants),
                        'satisfaction_score': round(random.uniform(4.0, 5.0), 1),
                        'retention_rate': round(random.uniform(80.0, 95.0), 2),
                        'payment_punctuality': round(random.uniform(85.0, 98.0), 2)
                    }
                else:  # expense_tracking
                    metric_data = {
                        'monthly_expenses': float(Decimal(random.randint(15000, 60000))),
                        'expense_categories': {
                            'maintenance': float(Decimal(random.randint(8000, 25000))),
                            'utilities': float(Decimal(random.randint(3000, 12000))),
                            'services': float(Decimal(random.randint(2000, 8000)))
                        },
                        'cost_per_property': round(random.uniform(500.0, 2000.0), 2)
                    }
                
                dashboard_data = {
                    'user': user,
                    'metric_type': metric_type,
                    'metric_data': metric_data,
                    'last_updated': timezone.now(),
                    'expires_at': timezone.now() + timedelta(hours=24),
                    'calculation_time': timedelta(seconds=random.randint(1, 30)),
                    'cache_key': f'{metric_type}_{user.id}_{random.randint(1000, 9999)}',
                }
                
                try:
                    dashboard = DashboardMetrics.objects.create(**dashboard_data)
                    metrics_count += 1
                except Exception as e:
                    print(f"   ❌ Error creating dashboard metric: {e}")
        
        results['dashboard_metrics'] = metrics_count
        print(f"✅ Total Dashboard Metrics: {metrics_count}")
        
        # Print Final Summary
        print("\n" + "=" * 80)
        print("🎉 ADDITIONAL MODELS DATA CREATION COMPLETED!")
        print("=" * 80)
        
        total_objects = sum(results.values())
        print(f"📊 TOTAL ADDITIONAL OBJECTS CREATED: {total_objects}")
        print()
        
        for model_name, count in results.items():
            if count > 0:
                print(f"   ✅ {model_name.replace('_', ' ').title()}: {count}")
        
        print()
        print("✅ ALL ADDITIONAL MODELS SUCCESSFULLY CREATED!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_additional_models_data()