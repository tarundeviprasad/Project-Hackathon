from django.urls import path
from . import login
from . import dashboard
from .logout import user_logout
from .create_doctor import create_doctor


urlpatterns = [

    path(
        "csrf/",
        login.get_csrf_token,
        name="csrf_token"
    ),

    # =========================
    # PATIENT LOGIN
    # =========================
    path(
        "patient/login/",
        login.patient_login,
        name="patient_login"
    ),


    # =========================
    # DOCTOR LOGIN
    # =========================
    path(
        "doctor/login/",
        login.doctor_login,
        name="doctor_login"
    ),


    # =========================
    # ADMIN LOGIN
    # =========================
    path(
        "admin/login/",
        login.admin_login,
        name="admin_login"
    ),


    # =========================
    # PATIENT DASHBOARD
    # =========================
    path(
        "patient/dashboard/",
        dashboard.patient_dashboard,
        name="patient_dashboard"
    ),


    # =========================
    # DOCTOR DASHBOARD
    # =========================
    path(
        "doctor/dashboard/",
        dashboard.doctor_dashboard,
        name="doctor_dashboard"
    ),


    # =========================
    # ADMIN DASHBOARD
    # =========================
    path(
        "admin/dashboard/",
        dashboard.admin_dashboard,
        name="admin_dashboard"
    ),


    # =========================
    # ADMIN CREATES DOCTOR
    # =========================
    path(
        "admin/create-doctor/",
        create_doctor,
        name="create_doctor"
    ),


    # =========================
    # LOGOUT
    # =========================
    path(
        "logout/",
        user_logout,
        name="logout"
    ),


    # =========================
    # HOMEPAGE
    # =========================
    path(
        "",
        login.home,
        name="home"
    ),

]