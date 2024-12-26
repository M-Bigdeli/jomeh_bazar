from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login

from customer.models import Customer
from customer.forms import CustomerRegisterForm, CustomerLogInForm
from jomeh_bazar.utils import create_message


def delete_message(request):
    del request.session['message_text']
    del request.session['message_class']
    del request.session['message_icon']
    return HttpResponse("ok")
def index(request):
    return render(request, "home/index.html", {})


def about(request):
    return render(request, "home/about.html", {})


def contact(request):
    return render(request, "home/contact.html", {})
