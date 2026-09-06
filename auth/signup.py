from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from .models import User

from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import datetime
import random
from api.models import Patient


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

        # Create the login and patient profile together so ownership is explicit.
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role="PATIENT"
            )
            patient_id = None
            while patient_id is None or Patient.objects.filter(patient_id=patient_id).exists():
                patient_id = f"AC-{datetime.now().year}-{random.randint(1000, 9999)}"
            Patient.objects.create(
                user=user,
                patient_id=patient_id,
                full_name=request.POST.get('full_name', username),
                dob=request.POST.get('dob') or None,
                gender=request.POST.get('gender') or 'None',
                phone=request.POST.get('phone', ''),
                email=email,
                village=request.POST.get('village', ''),
                district=request.POST.get('district', ''),
                preferred_language=request.POST.get('language', 'en'),
            )

        return redirect("patient_login")

    return render(request, "patient/signup.html")