from django.urls import path

from . import views

app_name = 'home'
urlpatterns = [
    path("delete-message/", views.delete_message, name="delete_message"),
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]