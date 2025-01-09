from django.urls import path

from . import views

app_name = 'product'
urlpatterns = [
    path("", views.products, name="products"),
    path("<slug:category_slug>/", views.products, name="products_category"),
]
