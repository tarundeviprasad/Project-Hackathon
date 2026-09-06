from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import User
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from api.audit import record_audit_event


@login_required
def create_doctor(request):

    # Only admin can create doctor accounts
    if request.user.role != "ADMIN":
        record_audit_event(request, 'PERMISSION_DENIED', user=request.user, success=False)
        return HttpResponseForbidden(
            "You are not allowed to create doctor accounts."
        )

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            return render(request, "admin/create_doctor.html", {"error": "All fields are required"})

        try:
            validate_email(email)
            validate_password(password)
        except ValidationError as error:
            return render(request, "admin/create_doctor.html", {"error": error.messages})

        # Check if username already exists
        if User.objects.filter(username=username).exists():

            return render(
                request,
                "admin/create_doctor.html",
                {"error": "Username already exists"}
            )

        # Create doctor account
        doctor = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="DOCTOR"
        )
        record_audit_event(request, 'DOCTOR_CREATED', user=request.user, target=doctor)

        # Return to admin dashboard
        return redirect("admin_dashboard")

    return render(request, "admin/create_doctor.html")