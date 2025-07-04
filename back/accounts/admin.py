from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import CustomUser, UserProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = _('Profile')
    fk_name = 'user'

    fieldsets = (
        (_('Personal Information'), {'fields': ('bio',)}),
        (_('Company Details'), {'fields': ('company_name', 'company_registration', 'tax_id', 'license_number', 'license_expiry')}),
        (_('Address'), {'fields': ('address', 'city', 'state', 'postal_code', 'country')}),
        (_('Financial'), {'fields': ('credit_limit', 'rating'), 'classes': ('collapse',)}),
        (_('Preferences'), {'fields': ('preferred_locations', 'property_preferences'), 'classes': ('collapse',)}),
    )

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    inlines = (UserProfileInline,)

    list_display = ('email', 'get_full_name', 'role', 'is_verified', 'is_active', 'is_staff', 'date_joined', 'last_login')
    list_filter = ('role', 'is_active', 'is_verified', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number', 'uuid')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'uuid', 'display_avatar')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'display_avatar', 'avatar')}),
        (_('Role'), {'fields': ('role',)}),
        (_('Verification'), {'fields': ('is_verified', 'verification_code', 'verification_code_created')}),
        (_('Password Reset'), {'fields': ('reset_code', 'reset_code_created')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'), 'classes': ('collapse',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'uuid')}),
    )

    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')}),
    )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = _('Full Name')

    def display_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 50%; object-fit: cover;"/>', obj.avatar.url)
        return _('No avatar uploaded')
    display_avatar.short_description = _('Avatar Preview')

    actions = ['mark_verified', 'mark_unverified', 'reset_verification_code']

    def mark_verified(self, request, queryset):
        updated = queryset.update(is_verified=True, verification_code=None, verification_code_created=None)
        self.message_user(request, _(f"{updated} users marked as verified."))
    mark_verified.short_description = _("Mark selected users as verified")

    def mark_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, _(f"{updated} users marked as unverified."))
    mark_unverified.short_description = _("Mark selected users as unverified")

    def reset_verification_code(self, request, queryset):
        count = 0
        for user in queryset:
            if not user.is_verified:
                user.generate_verification_code()
                count += 1
        self.message_user(request, _(f"Generated new verification codes for {count} users."))
    reset_verification_code.short_description = _("Reset verification codes for unverified users")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'company_name', 'city', 'country')
    search_fields = ('user__email', 'company_name', 'city', 'country')
    list_filter = ('country', 'city')
    readonly_fields = ('user',)

    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Personal'), {'fields': ('bio',)}),
        (_('Company'), {'fields': ('company_name', 'company_registration', 'tax_id')}),
        (_('Professional'), {'fields': ('license_number', 'license_expiry')}),
        (_('Address'), {'fields': ('address', 'city', 'state', 'postal_code', 'country')}),
        (_('Financial'), {'fields': ('credit_limit', 'rating')}),
        (_('Preferences'), {'fields': ('preferred_locations', 'property_preferences')}),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _('User Email')
    user_email.admin_order_field = 'user__email'