from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.http import FileResponse
from pathlib import Path
from django.middleware.csrf import get_token
from .models import User
from .security import clear_login_failures, login_is_rate_limited, record_login_failure


def authenticate_by_identifier(request, identifier, password):
    user = authenticate(request, username=identifier, password=password)
    if user is not None:
        return user

    UserModel = get_user_model()
    user_by_email = UserModel.objects.filter(email__iexact=identifier).first()
    if user_by_email is not None:
        return authenticate(request, username=user_by_email.username, password=password)

    return None


def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({"csrfToken": token})


def home(request):
    return redirect("/index.html")


def _role_login(request, role, redirect_url):
    identifier = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

    if not identifier or not password:
        return JsonResponse({"error": "Invalid email/username or password."}, status=401)

    if login_is_rate_limited(request, identifier):
        record_login_failure(request, identifier, reason="rate_limited")
        return JsonResponse({"error": "Too many failed attempts. Try again later."}, status=429)

    user = authenticate_by_identifier(request, identifier, password)
    allowed_roles = role if isinstance(role, (set, tuple, list)) else {role}
    if user is None or getattr(user, "role", None) not in allowed_roles:
        record_login_failure(request, identifier)
        return JsonResponse({"error": "Invalid email/username or password."}, status=401)

    clear_login_failures(request, identifier)
    login(request, user)
    from api.audit import record_audit_event
    record_audit_event(request, 'LOGIN_SUCCESS', user=user)
    destination = redirect_url.get(user.role, redirect_url) if isinstance(redirect_url, dict) else redirect_url
    return JsonResponse({"success": True, "redirect": destination})


@csrf_protect
def patient_login(request):
    if request.method == "POST":
        return _role_login(request, "PATIENT", "/patient/dashboard/")

    return redirect("/patient-login.html")


@csrf_protect
def doctor_login(request):
    if request.method == "POST":
        return _role_login(request, {"DOCTOR", "PHC"}, {
            "DOCTOR": "/doctor-dashboard.html",
            "PHC": "/phc/dashboard/",
        })

    return redirect("/doctor-login.html")


@csrf_protect
def asha_login(request):
    if request.method == "POST":
        return _role_login(request, "ASHA", "/asha/dashboard/")
    return redirect("/Asha%20login.html")


@csrf_protect
def admin_login(request):
    if request.method == "POST":
        return _role_login(request, {"ADMIN", "HOSPITAL_ADMIN"}, {
            "ADMIN": "/admin/dashboard/",
            "HOSPITAL_ADMIN": "/hospital/dashboard/",
        })

    return redirect("/admin-login.html")


@csrf_protect
def hospital_admin_login(request):
    if request.method == "POST":
        return _role_login(request, "HOSPITAL_ADMIN", "/hospital/dashboard/")
    return FileResponse((Path(__file__).resolve().parent.parent / "hospital admin.html").open("rb"))


@csrf_protect
def patient_signup(request):

    if request.method == "POST":

        try:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")

            # USERNAME VALIDATION
            if not username:
                return render(
                    request,
                    "patient/signup.html",
                    {"error": "Username is required"}
                )

            if User.objects.filter(username=username).exists():
                return render(
                    request,
                    "patient/signup.html",
                    {"error": "Username already exists"}
                )

            # EMAIL VALIDATION
            if not email:
                return render(
                    request,
                    "patient/signup.html",
                    {"error": "Email is required"}
                )

            try:
                validate_email(email)

            except ValidationError:
                return render(
                    request,
                    "patient/signup.html",
                    {"error": "Please enter a valid email address"}
                )

            if User.objects.filter(email=email).exists():
                return render(
                    request,
                    "patient/signup.html",
                    {"error": "Email already exists"}
                )

            # PASSWORD VALIDATION
            if not password:
                return render(
                    request,
                    "patient/signup.html",
                    {"error": "Password is required"}
                )

            try:
                validate_password(password)

            except ValidationError as error:
                return render(
                    request,
                    "patient/signup.html",
                    {"error": error.messages}
                )

            # CREATE ACCOUNT
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role="PATIENT"
            )

            return redirect("patient_login")

        # Database-related error
        except IntegrityError:
            return render(
                request,
                "patient/signup.html",
                {"error": "Unable to create account. Please try again."}
            )

        # Any unexpected error
        except Exception:
            return render(
                request,
                "patient/signup.html",
                {"error": "Something went wrong. Please try again later."}
            )

    return render(request, "patient/signup.html")