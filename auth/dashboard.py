@login_required
def patient_dashboard(request):
    if request.user.role != "PATIENT":
        return HttpResponseForbidden("Access denied")
    return render(request, "patient/dashboard.html")


@login_required
def doctor_dashboard(request):
    if request.user.role != "DOCTOR":
        return HttpResponseForbidden("Access denied")
    return render(request, "doctor/dashboard.html")


@login_required
def admin_dashboard(request):
    if request.user.role != "ADMIN":
        return HttpResponseForbidden("Access denied")
    return render(request, "admin/dashboard.html")