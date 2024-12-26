from django.urls import path

from . import views

app_name = 'customer'
urlpatterns = [
    path("register/", views.register, name="register"),
    path("reset-session/<str:rote>", views.reset_session, name="reset_session"),
    path("login/", views.log_in, name="log_in"),
    path("forget-password/", views.forget_password, name="forget_password"),
    path("change-forgotten-password/", views.change_forgotten_password, name="change_forgotten_password"),
    path("logout/", views.log_out, name="log_out"),
    path("", views.account, name="account"),
    path("change-name", views.change_name, name="change_name"),
    path("change-change_phone_number", views.change_phone_number, name="change_phone_number"),
    path("change-password", views.change_password, name="change_password"),
    path("delete-address", views.delete_address, name="delete_address"),
    path("edit-address", views.edit_address, name="edit_address"),
    path("add-address", views.add_address, name="add_address"),
]
