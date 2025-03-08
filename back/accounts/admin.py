from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import Permission
from django.utils import timezone
import random
from .models import Role, UserProfile, CustomUser


class RolePermissionInline(admin.TabularInline):
    model = Role.permissions.through
    extra = 1
    verbose_name = _("Permission")
    verbose_name_plural = _("Permissions")
    # Using raw_id_fields instead of autocomplete_fields
    raw_id_fields = ['permission']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_name_display', 'user_count', 'created_at', 'updated_at')
    list_filter = ('name', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [RolePermissionInline]
    exclude = ('permissions',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(user_count=Count('users'))
        return queryset
    
    def user_count(self, obj):
        return obj.user_count
    user_count.short_description = _('Users')
    user_count.admin_order_field = 'user_count'
    
    def get_name_display(self, obj):
        """Return the human-readable name"""
        return obj.get_name_display()
    get_name_display.short_description = _('Role Name')


class RoleFilter(SimpleListFilter):
    title = _('Role')
    parameter_name = 'role'
    
    def lookups(self, request, model_admin):
        return Role.ROLE_CHOICES
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(roles__name=self.value())
        return queryset


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_name', 'company_name', 'credit_limit', 'rating')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'company_name', 'company_registration', 'tax_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        (_('Company Information'), {
            'fields': ('company_name', 'company_registration', 'tax_id', 'address')
        }),
        (_('Financial Information'), {
            'fields': ('credit_limit', 'rating')
        }),
        (_('Additional Information'), {
            'fields': ('bio',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _('Email')
    user_email.admin_order_field = 'user__email'
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_name.short_description = _('Name')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = _('Profile')
    verbose_name_plural = _('Profile')
    fk_name = 'user'
    fieldsets = (
        (_('Company Information'), {
            'fields': ('company_name', 'company_registration', 'tax_id', 'address')
        }),
        (_('Role and Bio'), {
            'fields': ('bio',)
        }),
        (_('Financial Information'), {
            'fields': ('credit_limit', 'rating'),
            'classes': ('collapse',)
        }),
    )


class UserRolesInline(admin.TabularInline):
    model = CustomUser.roles.through
    extra = 1
    verbose_name = _("Role")
    verbose_name_plural = _("Roles")
    

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    inlines = (UserProfileInline, UserRolesInline)
    list_display = ('email', 'first_name', 'last_name', 'display_role', 'is_verified', 
                   'is_active', 'date_joined', 'last_login')
    list_filter = ('is_active', 'is_verified', 'is_staff', RoleFilter, 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'profile__company_name')
    ordering = ('-date_joined',)
    readonly_fields = ['date_joined', 'last_login', 'display_verification_status']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'avatar')}),
        (_('Verification'), {'fields': ('is_verified', 'display_verification_status', 'verification_code', 'verification_code_created')}),
        (_('Password Reset'), {'fields': ('reset_code', 'reset_code_created'), 'classes': ('collapse',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    actions = ['verify_users', 'reset_verification_code', 'deactivate_users', 'activate_users']
    
    def get_queryset(self, request):
        """Prefetch related profile and roles data"""
        return super().get_queryset(request).select_related('profile').prefetch_related('roles')
    
    def display_role(self, obj):
        primary_role = obj.primary_role
        if primary_role:
            # Find the role object in the prefetched roles
            for role in obj.roles.all():
                if role.name == primary_role:
                    return format_html('<span style="color: {};">{}</span>',
                                      self._get_role_color(role.name),
                                      role.get_name_display())
        return "-"
    display_role.short_description = _('Primary Role')
    
    def _get_role_color(self, role_name):
        """Return color code for roles for better visual distinction"""
        colors = {
            Role.ADMIN: '#DC3545',      # Red
            Role.SELLER: '#28A745',     # Green
            Role.BUYER: '#007BFF',      # Blue
            Role.INSPECTOR: '#FFC107',  # Yellow
            Role.LEGAL: '#6C757D',      # Gray
        }
        return colors.get(role_name, '#000000')
    
    def display_verification_status(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified on {}</span>', 
                              obj.verification_code_created)
        elif obj.verification_code:
            return format_html('<span style="color: orange;">⏱ Pending verification - code sent on {}</span>', 
                              obj.verification_code_created)
        return format_html('<span style="color: red;">✗ Not verified</span>')
    display_verification_status.short_description = _('Verification Status')
    
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, _(f'{updated} users were successfully verified.'))
    verify_users.short_description = _("Mark selected users as verified")
    
    def reset_verification_code(self, request, queryset):
        updated = 0
        for user in queryset:
            user.verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user.verification_code_created = timezone.now()
            user.save()
            updated += 1
            
        self.message_user(request, _(f'Verification codes reset for {updated} users.'))
    reset_verification_code.short_description = _("Reset verification codes")
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f'{updated} users were successfully deactivated.'))
    deactivate_users.short_description = _("Deactivate selected users")
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f'{updated} users were successfully activated.'))
    activate_users.short_description = _("Activate selected users")
    
    def save_model(self, request, obj, form, change):
        """
        Handle custom user creation/modification logic
        """
        if not change and not obj.is_superuser:
            # For new non-superuser accounts, generate verification code
            obj.verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            obj.verification_code_created = timezone.now()
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """
        Create UserProfile if it doesn't exist when saving the inline formset
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, UserProfile):
                if not instance.pk:  # If this is a new profile
                    instance.created_at = timezone.now()
            instance.save()
        formset.save_m2m()
        
        # For deleted instances
        for deleted_object in formset.deleted_objects:
            deleted_object.delete()
   

admin.site.register(Permission)