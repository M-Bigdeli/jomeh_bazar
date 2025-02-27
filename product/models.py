from django.conf import settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.html import mark_safe

import os
from uuid import uuid4
from PIL.ImageOps import expand as expand_image_PIL
from PIL.Image import open as image_open_PIL
from .utils import update_products_list_navbar
from customer.models import Customer


class Category(MPTTModel):
    """
    Represents a hierarchical category structure using MPTT (Modified Preorder Tree Traversal).

    Attributes:
    - name (str): The name of the category.
    - slug (str): A unique identifier used for URLs.
    - parent (TreeForeignKey): A self-referential foreign key defining the parent-child relationship.
    - is_clothing (bool): Indicates whether the category contains clothing items.

    Methods:
    - save(): Removes size attributes from products if the category is not clothing.
    - delete(): Deletes the category and updates the product list in the navbar.
    """
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=60, unique=True, null=False, blank=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_clothing = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            if not self.is_clothing:
                a = Product.objects.filter(category=self.pk)
                for i in a:
                    Size.objects.filter(product=i).delete()
        super().save(*args, **kwargs)
        update_products_list_navbar()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        update_products_list_navbar()


class Color(models.Model):
    """
    Represents a product color.

    Attributes:
    - name (str): The name of the color.
    - hex_code (str): The hexadecimal code representing the color.
    """
    name = models.CharField(max_length=70)
    hex_code = models.CharField(max_length=7, blank=False, null=False)

    def __str__(self):
        return self.name


class Size(models.Model):
    """
    Represents the available sizes for a product.

    Attributes:
    - SIZES (list): A predefined list of available sizes, including numerical values.
    - product (ForeignKey): A reference to the associated product.
    - size (PositiveSmallIntegerField): The selected size for the product.
    - price_difference (int): An optional price adjustment based on size.

    Methods:
    - save(): Ensures sizes are only assigned to clothing products.
    """
    SIZES = [
        (1, "فری سایز"),
        (2, "S"),
        (3, "M"),
        (4, "L"),
        (5, "XL"),
        (6, "XXL"),
        (7, "3XL"),
        (8, "4XL"),
        (9, "5XL"),
    ]
    for i in range(10, 150):
        SIZES.append((i, str(i - 9)))
    SIZES = tuple(SIZES)

    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='sizes')
    size = models.PositiveSmallIntegerField(choices=SIZES, verbose_name="Size")
    price_difference = models.IntegerField(default=0, null=False, blank=False)

    class Meta:
        ordering = ['size']

    def save(self, *args, **kwargs):
        if self.product.category.is_clothing:
            super().save(*args, **kwargs)


class Product(models.Model):
    """
    Represents a product in the system.

    Attributes:
    - name (str): The name of the product.
    - category (ForeignKey): A reference to the product's category.
    - slug (str): A unique slug used for URLs.
    - price (int): The base price of the product.
    - discount (int): A percentage discount applied to the price.
    - description (TextField): A detailed description of the product.
    - stock (int): The number of items available in stock.
    - color (ManyToManyField): A many-to-many relationship with colors.
    - created_at (DateTimeField): The timestamp when the product was created.

    Methods:
    - save(): Ensures each clothing product has at least one size.
    - get_discounted_price(): Returns the final price after applying a discount.
    - get_description_lines(): Splits the description into a list of lines.
    """
    name = models.CharField(max_length=210)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    price = models.PositiveBigIntegerField()
    discount = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)], null=False, blank=False)
    description = models.TextField()
    stock = models.PositiveIntegerField()
    color = models.ManyToManyField(Color, related_name="product", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.id
        super().save(*args, **kwargs)
        if self.category.is_clothing:
            if not self.sizes.exists():
                Size.objects.create(size=1, product=self)

    def get_discounted_price(self):
        """
        Calculate the final price after applying the discount.

        Returns:
        - float: The discounted price if a discount is applied, otherwise the original price.
        """
        if self.discount > 0:
            return self.price * (1 - self.discount / 100)
        return self.price

    def get_description_lines(self):
        """
        Splits the product description into separate lines.

        Returns:
        - list: A list of description lines.
        """
        return self.description.split('\n')


class ProductImage(models.Model):
    # ForeignKey linking this image to a product
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_upload_to = "product_images/"
    image = models.ImageField(upload_to=image_upload_to)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        # Default ordering by the 'order' field
        ordering = ['order']

    def save(self, *args, **kwargs):
        def rename_product_image():
            # Generate a unique filename for the image
            filename = str(uuid4())
            filename += str(self.image.width) + "_" + str(self.image.height) + "-" + str(self.image.width)
            filename = f"{filename}.png"
            self.image.name = filename

            # Save the instance
            super(self.__class__, self).save(*args, **kwargs)

            # Construct the file path and open the image
            filename = str(settings.MEDIA_ROOT) + "/" + str(self._meta.get_field('image').upload_to) + filename
            img = image_open_PIL(filename)

            # Convert image to RGBA
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            width, height = img.size

            # Calculate padding to make the image square
            if height > width:
                padding = int((height - width) / 2)
                padding = (padding, 0, padding, 0)
            elif width > height:
                padding = int((width - height) / 2)
                padding = (0, padding, 0, padding)
            else:
                padding = (0, 0, 0, 0)

            # Add padding to make the image square
            img = expand_image_PIL(img, padding, (255, 255, 255, 0))
            img.save(filename, format="PNG")

        if self.pk:
            # Handle existing image replacement
            old_image = ProductImage.objects.get(pk=self.pk).image
            if not old_image == self.image:
                if os.path.isfile(old_image.path):
                    os.remove(old_image.path)
                    rename_product_image()
            else:
                # Handle new image upload
                super().save(*args, **kwargs)

        else:
            rename_product_image()

    # Override delete method to remove the associated image file from storage.
    def delete(self, *args, **kwargs):
        if self.image:
            image_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)
        super().delete(*args, **kwargs)

    # Generate an HTML preview of the image for use in the admin panel.
    def image_preview(self):
        if self.image:
            return mark_safe(
                f'<a href="{self.image.url}"><img src="{self.image.url}" width="100" height="100" style="object-fit:contain;"/></a>')
        return ""

    image_preview.short_description = "Preview"


# Signal to delete the image file from storage when a ProductImage instance is deleted.
@receiver(post_delete, sender=ProductImage)
def delete_product_image_file(sender, instance, **kwargs):
    if instance.image:
        if default_storage.exists(instance.image.name):
            default_storage.delete(instance.image.name)


# Signal to set the order of the image automatically based on the last image of the product.
@receiver(pre_save, sender=ProductImage)
def set_image_order(sender, instance, **kwargs):
    if not instance.order:
        last_order = ProductImage.objects.filter(product=instance.product).order_by('order').last()
        if last_order:
            instance.order = last_order.order + 1
        else:
            instance.order = 1


class ProductAttribute(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name="attribute_values")
    value = models.CharField(max_length=1000)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(blank=True, max_length=100)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'customer')
