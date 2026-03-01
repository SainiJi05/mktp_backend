from django.contrib import admin

from apps.accounts.models import Address, BankDetails, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "role", "is_active", "is_verified", "date_joined")
    list_filter = ("role", "is_active", "is_verified")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "city", "state", "postal_code", "is_default")
    list_filter = ("city", "state", "is_default")
    search_fields = ("user__email", "name", "city", "state", "postal_code")


@admin.register(BankDetails)
class BankDetailsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "account_holder_name", "account_number", "ifsc_code", "upi_id", "updated_at")
    search_fields = ("user__email", "account_holder_name", "account_number", "ifsc_code", "upi_id")
    ordering = ("-updated_at",)
