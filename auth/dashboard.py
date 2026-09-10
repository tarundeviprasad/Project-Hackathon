from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


ROOT_HTML_DIR = Path(__file__).resolve().parent.parent


@login_required
def patient_dashboard(request):
    if request.user.role != "PATIENT":
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "patient_portal.html").open("rb"))


@login_required(login_url="/doctor-login.html")
def doctor_dashboard(request):
    if request.user.role != "DOCTOR":
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "doctor-dashboard.html").open("rb"))


@login_required(login_url="/doctor-login.html")
def doctor_referrals(request):
    if request.user.role not in {"DOCTOR", "ADMIN"}:
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "referral_doctor.html").open("rb"))


@login_required(login_url="/doctor-login.html")
def doctor_consultation(request):
    if request.user.role not in {"DOCTOR", "ADMIN"}:
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "Consultation.html").open("rb"))


@login_required(login_url="/doctor-login.html")
def doctor_appointments(request):
    if request.user.role not in {"DOCTOR", "ADMIN"}:
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "Appointment.html").open("rb"))


@login_required(login_url="/doctor-login.html")
def doctor_patients(request):
    if request.user.role not in {"DOCTOR", "ADMIN"}:
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "patient management doctor.html").open("rb"))


@login_required(login_url="/Asha%20login.html")
def asha_dashboard(request):
    if request.user.role != "ASHA":
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "Asha dashboard.html").open("rb"))


@login_required(login_url="/doctor-login.html")
def phc_dashboard(request):
    if request.user.role != "PHC":
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "phc_dashboard.html").open("rb"))


@login_required
def admin_dashboard(request):
    if request.user.role != "ADMIN":
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "System Admin Dashboard.html").open("rb"))


@login_required(login_url="/hospital-admin/login/")
def hospital_admin_dashboard(request):
    if request.user.role != "HOSPITAL_ADMIN":
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "Hospital dshboard.html").open("rb"))