from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .models import User


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


@csrf_protect
def patient_login(request):
    if request.method == "POST":
        identifier = request.POST.get("username")
        password = request.POST.get("password")

        if not identifier or not password:
            return JsonResponse(
                {"error": "Please provide both email/username and password."},
                status=400
            )

        user = authenticate_by_identifier(request, identifier, password)

        if user is not None and getattr(user, "role", None) == "PATIENT":
            login(request, user)
            return JsonResponse({"success": True, "redirect": "/patient_portal.html"})
        
        return JsonResponse(
            {"error": "Invalid email/username or password. Please try again."},
            status=401
        )

    return redirect("/patient-login.html")


@csrf_protect
def doctor_login(request):
    if request.method == "POST":
        identifier = request.POST.get("username")
        password = request.POST.get("password")

        if not identifier or not password:
            return JsonResponse(
                {"error": "Please provide both email/username and password."},
                status=400
            )

        user = authenticate_by_identifier(request, identifier, password)

        if user is not None and getattr(user, "role", None) == "DOCTOR":
            login(request, user)
            return JsonResponse({"success": True, "redirect": "/doctor-dashboard.html"})
        
        return JsonResponse(
            {"error": "Invalid email/username or password. Please try again."},
            status=401
        )

    return redirect("/doctor-login.html")


@csrf_protect
def admin_login(request):
    if request.method == "POST":
        identifier = request.POST.get("username")
        password = request.POST.get("password")

        if not identifier or not password:
            return JsonResponse(
                {"error": "Please provide both email/username and password."},
                status=400
            )

        user = authenticate_by_identifier(request, identifier, password)

        if user is not None and getattr(user, "role", None) == "ADMIN":
            login(request, user)
            return JsonResponse({"success": True, "redirect": "/index.html"})
        
        return JsonResponse(
            {"error": "Invalid email/username or password. Please try again."},
            status=401
        )

    return redirect("/admin-login.html")


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