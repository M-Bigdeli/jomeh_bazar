from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from .models import Product
from jomeh_bazar.utils import create_message

def products(request):
    products = Product.objects.all()
    return render(request, "product/product.html", {'products': products})
