from django.urls import path
from . import views

urlpatterns = [
    # Auth & Registration
    path('auth/register', views.register_patient, name='register_patient'),
    path('auth/login', views.login_view, name='login'),
    path('admin/hospital-admins', views.hospital_admins_api, name='hospital_admin_list_create'),

    # Patient Dashboard & Digital Health Records
    path('patient/me/dashboard', views.get_my_patient_dashboard, name='my_patient_dashboard'),
    path('patient/me/records', views.get_my_health_records, name='my_patient_records'),
    path('patient/<str:patient_id>/dashboard', views.get_patient_dashboard, name='patient_dashboard'),
    path('patient/<str:patient_id>/records', views.get_health_records, name='patient_health_records'),
    path('patients', views.list_patients, name='patient_list'),
    path('doctors', views.list_doctors, name='doctor_list'),
    path('facilities', views.list_facilities, name='facility_list'),
    path('appointments', views.appointments_api, name='appointment_list_create'),
    path('consultations', views.consultations_api, name='consultation_list_create'),
    path('consultations/<int:consultation_id>', views.consultations_api, name='consultation_detail'),
    path('referrals', views.referrals_api, name='referral_list_create'),
    path('referrals/<int:referral_id>', views.referrals_api, name='referral_detail'),
    path('follow-ups', views.followups_api, name='followup_list_create'),

    # Doctor worklist
    path('doctor/worklist', views.get_doctor_worklist, name='doctor_worklist'),
    path('asha/me/dashboard', views.get_asha_dashboard, name='asha_dashboard'),
    path('phc/me/dashboard', views.get_phc_dashboard, name='phc_dashboard'),
    path('hospital/me/dashboard', views.get_hospital_dashboard, name='hospital_dashboard'),

    # Interactive Patient Services
    path('symptom-check', views.check_symptoms, name='check_symptoms'),
    path('medicines', views.search_medicines, name='search_medicines'),
    path('emergency/sos', views.trigger_sos, name='trigger_sos'),
]