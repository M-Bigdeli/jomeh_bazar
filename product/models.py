from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.utils.html import mark_safe

import os
from uuid import uuid4
from PIL import Image, ImageOps


class Product(models.Model):
    name = models.CharField(max_length=210)
    price = models.PositiveBigIntegerField()
    description = models.TextField()
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_upload_to = "product_images/"
    image = models.ImageField(upload_to=image_upload_to)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        def rename_product_image():
            filename = str(uuid4())
            filename += str(self.image.width) + "_" + str(self.image.height) + "-" + str(self.image.width)
            filename = f"{filename}.png"
            self.image.name = filename
            print(filename)

            super(self.__class__, self).save(*args, **kwargs)

            filename = str(settings.MEDIA_ROOT) + "/" + str(self._meta.get_field('image').upload_to) + filename
            print(filename)
            img = Image.open(filename)
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            width, height = img.size

            if height > width:
                padding = int((height - width) / 2)
                padding = (padding, 0, padding, 0)
            elif width > height:
                padding = int((width - height) / 2)
                padding = (0, padding, 0,padding)
            else:
                padding = (0, 0, 0, 0)

            img = ImageOps.expand(img, padding, (255, 255, 255, 0))
            img.save(filename, format="PNG")

        if self.pk:
            old_image = ProductImage.objects.get(pk=self.pk).image
            if not old_image == self.image:
                if os.path.isfile(old_image.path):
                    os.remove(old_image.path)
                    rename_product_image()
            else:
                super().save(*args, **kwargs)

        else:
            rename_product_image()

    def delete(self, *args, **kwargs):
        if self.image:
            image_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)
        super().delete(*args, **kwargs)

    def image_preview(self):
        if self.image:
            return mark_safe(
                f'<a href="{self.image.url}"><img src="{self.image.url}" width="100" height="100" style="object-fit:contain;"/></a>')
        return ""

    image_preview.short_description = "Preview"


@receiver(post_delete, sender=ProductImage)
def delete_product_image_file(sender, instance, **kwargs):
    if instance.image:
        if default_storage.exists(instance.image.name):
            default_storage.delete(instance.image.name)


@receiver(pre_save, sender=ProductImage)
def set_image_order(sender, instance, **kwargs):
    if not instance.order:  # اگر order مشخص نباشد
        last_order = ProductImage.objects.filter(product=instance.product).order_by('order').last()
        if last_order:
            instance.order = last_order.order + 1  # افزایش مقدار order از عدد آخر
        else:
            instance.order = 1  # اگر هیچ عکسی وجود نداشت،
