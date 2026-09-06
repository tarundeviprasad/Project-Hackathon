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


@login_required
def doctor_dashboard(request):
    if request.user.role != "DOCTOR":
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "doctor-dashboard.html").open("rb"))


@login_required
def doctor_referrals(request):
    if request.user.role not in {"DOCTOR", "ADMIN"}:
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "referral_doctor.html").open("rb"))


@login_required
def admin_dashboard(request):
    if request.user.role != "ADMIN":
        return HttpResponseForbidden("Access denied")
    return FileResponse((ROOT_HTML_DIR / "System Admin Dashboard.html").open("rb"))