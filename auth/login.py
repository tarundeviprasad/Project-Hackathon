from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
''' 
login authentication code for 
doctor ,patient, and admin
'''
#HOMEPAGE
def home(request):
    return render(request, "home.html")

# PATIENT LOGIN
def patient_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.role == "PATIENT":

            login(request, user)

            return redirect("patient_dashboard")

        else:
            return render(
                request,
                "patient/login.html",
                {"error": "Invalid patient username or password"}
            )

    return render(request, "patient/login.html")


# DOCTOR LOGIN
def doctor_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.role == "DOCTOR":

            login(request, user)

            return redirect("doctor_dashboard")

        else:
            return render(
                request,
                "doctor/login.html",
                {"error": "Invalid doctor username or password"}
            )

    return render(request, "doctor/login.html")


# ADMIN LOGIN
def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.role == "ADMIN":

            login(request, user)

            return redirect("admin_dashboard")

        else:
            return render(
                request,
                "admin/login.html",
                {"error": "Invalid admin username or password"}
            )

    return render(request, "admin/login.html")