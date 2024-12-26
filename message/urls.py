from django.urls import path

from . import views

app_name = 'message'

urlpatterns = [
    path("delete/", views.delete_message, name="delete_message"),
]
