from pathlib import Path

from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path
from auth.dashboard import (
    admin_dashboard,
    asha_dashboard,
    doctor_appointments,
    doctor_consultation,
    doctor_dashboard,
    doctor_patients,
    doctor_referrals,
    patient_dashboard,
    phc_dashboard,
    hospital_admin_dashboard,
)

ROOT_HTML_DIR = Path(__file__).resolve().parent.parent.parent


def serve_html(request, filename):
    file_path = ROOT_HTML_DIR / filename
    if file_path.exists() and file_path.suffix.lower() == '.html':
        return FileResponse(file_path.open('rb'))
    raise Http404(f'{filename} not found')


urlpatterns = [
    path('', include('auth.urls')),
    path('index.html', lambda request: serve_html(request, 'index.html')),
    path('patient-login.html', lambda request: serve_html(request, 'patient-login.html')),
    path('doctor-login.html', lambda request: serve_html(request, 'doctor-login.html')),
    path('admin-login.html', lambda request: serve_html(request, 'admin-login.html')),
    path('patient_portal.html', patient_dashboard, name='patient_dashboard_page'),
    path('doctor-dashboard.html', doctor_dashboard, name='doctor_dashboard_page'),
    path('Appointment.html', doctor_appointments, name='doctor_appointments_page'),
    path('Consultation.html', doctor_consultation, name='doctor_consultation_page'),
    path('patient management doctor.html', doctor_patients, name='doctor_patients_page'),
    path('referral_doctor.html', doctor_referrals, name='doctor_referrals_page'),
    path('Asha login.html', lambda request: serve_html(request, 'Asha login.html')),
    path('asha/dashboard/', asha_dashboard, name='asha_dashboard_page'),
    path('phc/dashboard/', phc_dashboard, name='phc_dashboard_page'),
    path('System Admin Dashboard.html', admin_dashboard, name='admin_dashboard_page'),
    path('hospital admin.html', hospital_admin_dashboard, name='hospital_admin_dashboard_page'),
    path('hospital/dashboard/', hospital_admin_dashboard, name='hospital_dashboard_page'),
    path('booking_an_appointment.html', lambda request: serve_html(request, 'booking_an_appointment.html')),
    path('digital_health_record.html', lambda request: serve_html(request, 'digital_health_record.html')),
    path('symptom_checker.html', lambda request: serve_html(request, 'symptom_checker.html')),
    path('admin-login.html', lambda request: serve_html(request, 'admin-login.html')),
    path('registrationofpatient.html', lambda request: serve_html(request, 'registrationofpatient.html')),
    path('loginpage.html', lambda request: serve_html(request, 'loginpage.html')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
]