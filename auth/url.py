from django.urls import path
from . import login
from .logout import user_logout

urlpatterns = [

    # PATIENT LOGIN
    path(
        "patient/login/",
        login.patient_login,
        name="patient_login"
    ),

    # DOCTOR LOGIN
    path(
        "doctor/login/",
        login.doctor_login,
        name="doctor_login"
    ),

    # ADMIN LOGIN
    path(
        "admin/login/",
        login.admin_login,
        name="admin_login"
    ),

    # LOGOUT FOR EVERYONE
    path(
        "logout/",
        user_logout,
        name="logout"
    ),

    # HOMEPAGE
    path(
        "",
        login.home,
        name="home"
    ),

]