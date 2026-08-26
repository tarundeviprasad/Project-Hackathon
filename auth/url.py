from django.urls import path
from . import login
from .logout import user_logout
from .create_doctor import create_doctor

urlpatterns = [

    path(
        "patient/login/",
        login.patient_login,
        name="patient_login"
    ),

    path(
        "doctor/login/",
        login.doctor_login,
        name="doctor_login"
    ),

    path(
        "admin/login/",
        login.admin_login,
        name="admin_login"
    ),

    path(
        "admin/create-doctor/",
        create_doctor,
        name="create_doctor"
    ),

    path(
        "logout/",
        user_logout,
        name="logout"
    ),

    path(
        "",
        login.home,
        name="home"
    ),

]