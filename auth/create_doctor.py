from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import User


@login_required
def create_doctor(request):

    # Only admin can create doctor accounts
    if request.user.role != "ADMIN":
        return HttpResponseForbidden(
            "You are not allowed to create doctor accounts."
        )

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check if username already exists
        if User.objects.filter(username=username).exists():

            return render(
                request,
                "admin/create_doctor.html",
                {"error": "Username already exists"}
            )

        # Create doctor account
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="DOCTOR"
        )

        # Return to admin dashboard
        return redirect("admin_dashboard")

    return render(request, "admin/create_doctor.html")