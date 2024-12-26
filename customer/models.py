from django.db import models
from django.contrib.auth.models import AbstractUser


class Customer(AbstractUser):
    # The username in this model is used as a phone number.
    is_active = models.BooleanField(default=True)


class Address(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    postal_code = models.BigIntegerField()
