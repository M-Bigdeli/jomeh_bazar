from django.contrib import admin

from .models import Customer, Address


class AddressInline(admin.TabularInline):
    model = Address
    # By default 0 lines are created for adding addresses in the admin panel.
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # Add/Show address in Customer admin panel.
    inlines = [AddressInline]
    list_display = ('username', 'email', 'is_active')
    search_fields = ('username', 'email')
