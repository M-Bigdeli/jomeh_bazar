from django.contrib import admin

from .models import Customer, Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [AddressInline]
    list_display = ('username', 'email', 'is_active')
    search_fields = ('username', 'email')
