from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Address


# =====================================================
# Account Admin
# =====================================================
class AccountAdmin(UserAdmin):

    list_display = (
        'email',
        'first_name',
        'last_name',
        'username',
        'phone_number',
        'city',
        'state',
        'is_active',
    )

    list_display_links = ('email', 'first_name', 'last_name')

    readonly_fields = ('last_login', 'date_joined')

    ordering = ('-date_joined',)

    list_filter = ('is_active', 'is_staff', 'is_admin')

    filter_horizontal = ()
    list_per_page = 20

    # 👉 Edit page layout in admin
    fieldsets = (
        ('Login Info', {
            'fields': ('email', 'password')
        }),

        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'username', 'phone_number')
        }),

        ('Address Info', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'country')
        }),

        ('Profile', {
            'fields': ('profile_picture',)
        }),

        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_admin', 'is_superadmin')
        }),

        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # 👉 Add user form layout
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'first_name',
                'last_name',
                'password1',
                'password2',
                'is_active',
                'is_staff',
            ),
        }),
    )


# =====================================================
# Address Admin
# =====================================================
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'phone', 'city', 'state', 'is_default')
    list_filter = ('city', 'state', 'is_default')
    search_fields = ('full_name', 'phone', 'city')


# =====================================================
# Register Models
# =====================================================
admin.site.register(Account, AccountAdmin)
admin.site.register(Address, AddressAdmin)