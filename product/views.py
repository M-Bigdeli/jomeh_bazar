from django.db.models import QuerySet
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.template import loader
from django.core.paginator import Paginator

from .models import Product, Category
from message.utils import create_message


def products(request, category_slug=None):
    context = dict()
    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return redirect(reverse("product:products"))
        context['category'] = category
        products = Product.objects.filter(category=category)
        context['category_ancestors'] = category.get_ancestors(include_self=True)
        context['category_ancestors'].reverse()
        context['category_siblings'] = category.get_siblings(include_self=True)
        context['category_children'] = Category.objects.filter(parent=category)
    else:
        products = Product.objects.all()
        context['category_siblings'] = Category.objects.filter(parent=None)

    if request.GET.get('in_stock'):
        products = products.filter(stock__gte=1)

    sort_by = request.GET.get('sort_by')
    if sort_by == "cheapest":
        products = products.order_by('price')
    elif sort_by == "most_expensive":
        products = products.order_by('-price')

    page = request.GET.get('page', 1)
    context['page_obj'] = Paginator(products, 24).get_page(page)
    return render(request, "product/product.html", context)
