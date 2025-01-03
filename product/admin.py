from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Product, ProductImage, Category, ProductAttribute, ProductAttributeValue
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


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    model = ProductAttribute
    list_display = ('name',)
    search_fields = ('name',)


# Custom admin configuration for the Product model to enhance functionality in the admin panel.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'category', 'stock', 'price')
    inlines = [ProductImageInline, ProductAttributeValueInline]

    # def category(self, obj):
    #     # این متد نام دسته‌بندی مرتبط با محصول را نمایش می‌دهد
    #     if obj.category:
    #         return obj.category.name
    #     else:
    #         return "No Category"
    #
    #
    # category.short_description = 'Category'


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)


