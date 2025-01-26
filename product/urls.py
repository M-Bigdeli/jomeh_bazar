from django.urls import path

from . import views

app_name = 'product'
urlpatterns = [
    path("", views.products, name="products"),
    path("<slug:category_slug>/", views.products, name="products_category"),
    path("<slug:category_slug>/<slug:product_slug>/", views.product_details, name="product_details"),
]
