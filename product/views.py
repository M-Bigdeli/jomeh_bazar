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
    """
    Handles product listing based on category, stock availability, search query,
    and sorting preferences.

    This view retrieves products based on the provided category slug. It supports
    filtering by stock availability, searching by product name or description,
    and sorting by price and stock status. Pagination is applied to display products efficiently.
    """

    context = dict()

    # Retrieve category and its related categories if a category slug is provided
    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return redirect(reverse("product:products"))

        context['category'] = category

        # Retrieve products from the selected category and all its descendant categories
        descendants = category.get_descendants(include_self=True)
        products = Product.objects.filter(category__in=descendants)

        # Gather category-related information for navigation and filtering
        context['category_ancestors'] = category.get_ancestors(include_self=True).reverse()
        context['category_siblings'] = category.get_siblings(include_self=True)
        context['category_children'] = Category.objects.filter(parent=category)
    else:
        # Retrieve all products if no specific category is provided
        products = Product.objects.all()
        context['category_siblings'] = Category.objects.filter(parent=None)

    # Filter products based on stock availability if requested
    if request.GET.get('in_stock'):
        products = products.filter(stock__gt=0)

    # Apply search filter based on product name or description
    query = request.GET.get('q', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # Annotate products with a boolean field to indicate stock availability
    products = products.annotate(
        is_in_stock=Case(
            When(stock__gt=0, then=True),
            default=False,
            output_field=BooleanField(),
        )
    )

    # Sort products based on user preference, prioritizing in-stock items
    sort_by = request.GET.get('sort_by')
    if sort_by == "cheapest":
        products = products.order_by('-is_in_stock', 'price')
    elif sort_by == "most_expensive":
        products = products.order_by('-is_in_stock', '-price')
    else:
        products = products.order_by('-is_in_stock', '-created_at')

    # Apply pagination to manage product display
    page = request.GET.get('page', 1)
    context['page_obj'] = Paginator(products, 24).get_page(page)

    # Render the product list template with the filtered and sorted products
    return render(request, "product/product.html", context)


def product_details(request, category_slug, product_slug):
    """
    Handles the retrieval and display of a specific product's details.

    This view fetches a product based on the provided category and product slug.
    If the product exists, it determines whether it is in stock and renders
    the appropriate template accordingly.
    """

    try:
        # Retrieve the product matching the given category and product slug
        product = Product.objects.get(slug=product_slug, category__slug=category_slug)
    except Product.DoesNotExist:
        # Deny access if the product does not exist
        raise PermissionDenied

    # Render different templates based on product stock availability
    if product.stock > 0:
        return render(request, "product/product_details.html", {"product": product})
    else:
        return render(request, "product/product_details_unavailable.html", {"product": product})
