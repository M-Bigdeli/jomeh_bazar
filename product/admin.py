from django.contrib import admin
from .models import Product, ProductImage
from django import forms


# Inline model to manage product images directly from the product admin page.
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    # Number of empty forms displayed for adding new images.
    extra = 1
    # Makes the image preview field read-only.
    readonly_fields = ('image_preview',)
    fields = ('image_preview', 'image', 'order')
    # Orders images by their 'order' field in ascending order.
    ordering = ('order',)


# Custom form for the Product model to provide additional configurations for form fields.
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            # Customizes the 'price' field to have a step size of 10,000 and a default value of 10,000.
            'price': forms.NumberInput(attrs={'step': 10000, 'value': 10000, }),
            # Customizes the 'stock' field to have a default value of 10.
            'stock': forms.NumberInput(attrs={'value': 10, }),
        }


# Custom admin configuration for the Product model to enhance functionality in the admin panel.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'stock', 'price')
    # Adds an inline interface to manage associated ProductImage instances.
    inlines = [ProductImageInline]
