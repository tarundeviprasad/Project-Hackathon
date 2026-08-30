from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from .models import User

from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


@csrf_protect
def patient_signup(request):

    if request.method == "POST":

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

        # CREATE PATIENT ACCOUNT
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="PATIENT"
        )

        return redirect("patient_login")

    return render(request, "patient/signup.html")