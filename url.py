from django.urls import path
from . import views

urlpatterns = [

    path(
        "doctor/login/",
        views.doctor_login,
        name="doctor_login"
    ),

    path(
        "admin/login/",
        views.admin_login,
        name="admin_login"
    ),

    path(
        "logout/",
        views.user_logout,
        name="logout"
    ),

]