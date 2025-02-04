from django.db.models import QuerySet
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.template import loader
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.db.models import BooleanField, Case, When

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
        descendants = category.get_descendants(include_self=True)
        products = Product.objects.filter(category__in=descendants)
        context['category_ancestors'] = category.get_ancestors(include_self=True).reverse()
        context['category_siblings'] = category.get_siblings(include_self=True)
        context['category_children'] = Category.objects.filter(parent=category)
    else:
        products = Product.objects.all()
        context['category_siblings'] = Category.objects.filter(parent=None)

    if request.GET.get('in_stock'):
        products = products.filter(stock__gt=0)
    
    query = request.GET.get('q', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    products = products.annotate(
        is_in_stock=Case(
            When(stock__gt=0, then=True),
            default=False,
            output_field=BooleanField(),
        )
    )

    sort_by = request.GET.get('sort_by')
    if sort_by == "cheapest":
        products = products.order_by('-is_in_stock', 'price')
    elif sort_by == "most_expensive":
        products = products.order_by('-is_in_stock', '-price')
    else:
        products = products.order_by('-is_in_stock', '-created_at')

    page = request.GET.get('page', 1)
    context['page_obj'] = Paginator(products, 24).get_page(page)
    return render(request, "product/product.html", context)


def product_details(request, category_slug, product_slug):
    try:
        product = Product.objects.get(slug=product_slug, category__slug=category_slug)
    except Product.DoesNotExist:
        raise PermissionDenied

    if product.stock > 0:
        return render(request, "product/product_details.html", {"product": product})
    else:
        return render(request, "product/product_details_unavailable.html", {"product": product})
