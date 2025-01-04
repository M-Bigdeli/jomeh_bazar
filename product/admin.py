from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Product, ProductImage, Category, ProductAttribute, ProductAttributeValue, Color, Size
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


# Registering ProductAttribute model in the admin panel and customizing its appearance and functionality.
@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    model = ProductAttribute
    list_display = ('name',)
    search_fields = ('name',)


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 0


class SizeInline(admin.TabularInline):
    class SizeInlineForm(forms.ModelForm):
        class Meta:
            model = Size
            fields = "__all__"
            widgets = {
                # Customizes the 'price difference' field to have a step size of 10,000 and a default value of 10,000.
                'price_difference': forms.NumberInput(attrs={'step': 10000, 'value': 0, }),
            }
    form = SizeInlineForm
    model = Size
    extra = 0
    ordering = ('size',)





# Custom admin configuration for the Product model to enhance functionality in the admin panel.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
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
    form = ProductAdminForm
    list_display = ('name', 'category', 'stock', 'price')
    inlines = [ProductImageInline, ProductAttributeValueInline, SizeInline]
    filter_horizontal = ('color',)


# Registering Category model with MPTTModelAdmin to support hierarchical data structure.
@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'slug', 'parent')
    search_fields = ('name', 'slug',)


# Custom form for the Color model to use a color picker for the hex_code field
class ColorAdminForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = "__all__"
        widgets = {
            'hex_code': forms.TextInput(attrs={'type': 'color'}),  # Color picker for hex_code
        }

# Admin configuration for the Color model
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    form = ColorAdminForm
    list_display = ('name', 'hex_code')
