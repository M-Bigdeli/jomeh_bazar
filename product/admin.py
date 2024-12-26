from django.contrib import admin
from .models import Product, ProductImage
from django import forms


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('image_preview',)
    fields = ('image_preview', 'image', 'order')
    ordering = ('order',)


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            'price': forms.NumberInput(attrs={'step': 10000, 'value': 10000, }),
            'stock': forms.NumberInput(attrs={'value': 10, }),
        }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'stock', 'price')
    inlines = [ProductImageInline]
