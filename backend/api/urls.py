from django.urls import path
from . import views

urlpatterns = [
    # Auth & Registration
    path('auth/register', views.register_patient, name='register_patient'),
    path('auth/login', views.login_view, name='login'),

    # Patient Dashboard & Digital Health Records
    path('patient/<str:patient_id>/dashboard', views.get_patient_dashboard, name='patient_dashboard'),
    path('patient/<str:patient_id>/records', views.get_health_records, name='patient_health_records'),

    # Interactive Patient Services
    path('symptom-check', views.check_symptoms, name='check_symptoms'),
    path('medicines', views.search_medicines, name='search_medicines'),
    path('emergency/sos', views.trigger_sos, name='trigger_sos'),
]