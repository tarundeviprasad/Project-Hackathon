from django.shortcuts import render, redirect
from .models import User


def patient_signup(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check whether username already exists
        if User.objects.filter(username=username).exists():

            return render(
                request,
                "patient/signup.html",
                {
                    "error": "Username already exists"
                }
            )

        # Create new patient account
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="PATIENT"
        )

        # After successful signup, go to login page
        return redirect("patient_login")

    # If user simply opens the signup page
    return render(request, "patient/signup.html")