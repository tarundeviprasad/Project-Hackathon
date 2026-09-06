from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, get_user_model
from django.core.cache import cache
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime, date
import random
import hashlib

from .models import (
    Patient, Facility, Appointment, HealthTimelineRecord, MedicineStock,
    SOSAlert, Consultation, Referral, FollowUp, DoctorProfile,
)
from .serializers import (
    PatientSerializer, FacilitySerializer, AppointmentSerializer,
    HealthTimelineRecordSerializer, MedicineStockSerializer, SOSAlertSerializer,
    ConsultationSerializer, ReferralSerializer, FollowUpSerializer,
    DoctorProfileSerializer,
)
from .audit import record_audit_event


def _failed_login_key(request, identifier):
    raw_key = f'{request.META.get("REMOTE_ADDR", "unknown")}:{identifier.lower()}'
    return f'api-login-failures:{hashlib.sha256(raw_key.encode()).hexdigest()}'


def _authorized_patient(request, patient_id):
    patient = Patient.objects.filter(patient_id=patient_id).first()
    if not patient:
        return None, Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role != 'ADMIN' and patient.user_id != request.user.id:
        record_audit_event(
            request,
            'UNAUTHORIZED_ACCESS',
            user=request.user,
            target=patient,
            success=False,
        )
        return None, Response(
            {'error': 'You are not allowed to access this patient record.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    return patient, None


def _doctor_queryset(request):
    if request.user.role == 'ADMIN':
        return Patient.objects.all()
    if request.user.role != 'DOCTOR':
        return Patient.objects.none()
    return Patient.objects.filter(
        Q(appointments__doctor=request.user)
        | Q(appointments__doctor_name__iexact=request.user.username)
        | Q(consultations__doctor=request.user)
        | Q(referrals__receiving_doctor=request.user)
        | Q(referrals__referring_doctor=request.user)
        | Q(follow_ups__doctor=request.user)
    ).distinct()


def _can_access_patient(request, patient):
    if request.user.role == 'ADMIN':
        return True
    if request.user.role == 'PATIENT':
        return patient.user_id == request.user.id
    return _doctor_queryset(request).filter(pk=patient.pk).exists()


def _get_patient_from_request(request, patient_id=None):
    if patient_id:
        patient = Patient.objects.filter(patient_id=patient_id).first()
    elif request.user.role == 'PATIENT':
        patient = getattr(request.user, 'patient_profile', None)
    else:
        patient = None
    if not patient:
        return None, Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
    if not _can_access_patient(request, patient):
        record_audit_event(request, 'UNAUTHORIZED_ACCESS', target=patient, success=False)
        return None, Response({'error': 'You are not allowed to access this patient.'}, status=status.HTTP_403_FORBIDDEN)
    return patient, None

# 1. Patient Registration API 
@api_view(['POST'])
@permission_classes([AllowAny])
def register_patient(request):
    data = request.data
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    
    if not full_name or not phone:
        return Response({'error': 'Full name and mobile number are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Generate Unique Patient ID like AC-2026-8821
    year = datetime.now().year
    random_digits = random.randint(1000, 9999)
    patient_id = f"AC-{year}-{random_digits}"

    patient = Patient.objects.create(
        patient_id=patient_id,
        full_name=full_name,
        dob=data.get('dob') or None,
        gender=data.get('gender', 'None'),
        phone=phone,
        email=data.get('email', ''),
        address=data.get('address', ''),
        village=data.get('village', ''),
        district=data.get('district', ''),
        preferred_language=data.get('language', 'en')
    )

    # Seed a default timeline entry for the new patient
    HealthTimelineRecord.objects.create(
        patient=patient,
        record_type='CONSULTATION',
        title='PHC Consultation',
        status='Completed',
        event_date=date.today(),
        facility_name=f"PHC {patient.village or 'Primary'}",
        doctor_name='Dr. Priya Sharma',
        health_issue='General Health Checkup',
        diagnosis='Baseline parameters recorded'
    )

    record_audit_event(request, 'PATIENT_CREATED', target=patient)

    return Response({
        'message': 'Patient registered successfully',
        'patient': PatientSerializer(patient).data
    }, status=status.HTTP_201_CREATED)


# 2. Authentication: Django session authentication
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def login_view(request):
    identifier = request.data.get('identifier', '').strip()
    password = request.data.get('password', '')
    if not identifier or not password:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    failure_key = _failed_login_key(request, identifier)
    failures = cache.get(failure_key, 0)
    if failures >= 5:
        record_audit_event(request, 'LOGIN_FAILURE', success=False, metadata={'reason': 'rate_limited'})
        return Response({'error': 'Too many failed attempts. Try again later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    user = authenticate(request, username=identifier, password=password)
    if user is None:
        account = get_user_model().objects.filter(email__iexact=identifier).first()
        if account:
            user = authenticate(request, username=account.username, password=password)

    if user is None or not user.is_active:
        cache.set(failure_key, failures + 1, timeout=900)
        record_audit_event(request, 'LOGIN_FAILURE', success=False)
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    cache.delete(failure_key)
    login(request, user)
    patient = getattr(user, 'patient_profile', None)
    record_audit_event(request, 'LOGIN_SUCCESS', user=user)
    response = {'user': {'id': user.id, 'role': user.role, 'username': user.username}}
    if patient:
        response['patient'] = PatientSerializer(patient).data
    return Response(response, status=status.HTTP_200_OK)


# 3. Patient Dashboard Snapshot
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_dashboard(request, patient_id):
    patient, error = _authorized_patient(request, patient_id)
    if error:
        return error
    record_audit_event(request, 'PATIENT_VIEWED', target=patient)

    next_apt = Appointment.objects.filter(patient=patient, status='Scheduled').order_by('appointment_time').first()
    records_count = HealthTimelineRecord.objects.filter(patient=patient).count()
    active_referrals = HealthTimelineRecord.objects.filter(patient=patient, record_type='REFERRAL', status='Pending').count()

    return Response({
        'patient': PatientSerializer(patient).data,
        'snapshot': {
            'blood_group': patient.blood_group,
            'next_appointment': next_apt.appointment_time.strftime('%I:%M %p') if next_apt else None,
            'active_referrals': active_referrals,
            'records_count': records_count,
            'queue_token': next_apt.queue_number if next_apt else None,
            'patients_ahead': next_apt.patients_ahead if next_apt else None
        }
    })


# 4. Digital Health Records Timeline & Stats
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_health_records(request, patient_id):
    patient, error = _authorized_patient(request, patient_id)
    if error:
        return error
    record_audit_event(request, 'PATIENT_VIEWED', target=patient)

    records = HealthTimelineRecord.objects.filter(patient=patient)
    
    stats = {
        'total_consultations': records.filter(record_type='CONSULTATION').count(),
        'active_prescriptions': records.exclude(prescription__isnull=True).exclude(prescription='').count(),
        'lab_reports': records.filter(record_type='LAB_TEST').count(),
        'active_referrals': records.filter(record_type='REFERRAL', status='Pending').count()
    }

    return Response({
        'patient': PatientSerializer(patient).data,
        'stats': stats,
        'timeline': HealthTimelineRecordSerializer(records, many=True).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_patient_dashboard(request):
    patient = getattr(request.user, 'patient_profile', None)
    if not patient:
        return Response({'error': 'Patient profile unavailable.'}, status=status.HTTP_404_NOT_FOUND)
    return get_patient_dashboard(request, patient.patient_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_health_records(request):
    patient = getattr(request.user, 'patient_profile', None)
    if not patient:
        return Response({'error': 'Patient profile unavailable.'}, status=status.HTTP_404_NOT_FOUND)
    return get_health_records(request, patient.patient_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_worklist(request):
    if request.user.role not in {'DOCTOR', 'ADMIN'}:
        record_audit_event(request, 'PERMISSION_DENIED', user=request.user, success=False)
        return Response({'error': 'Doctor access required.'}, status=status.HTTP_403_FORBIDDEN)

    appointment_queryset = Appointment.objects.select_related('patient').filter(status='Scheduled')
    consultation_queryset = Consultation.objects.select_related('patient', 'doctor').filter(
        status__in=['Draft', 'In Progress']
    )
    referral_queryset = Referral.objects.select_related('patient', 'referring_doctor', 'receiving_doctor').filter(
        status='Pending'
    )
    if request.user.role == 'DOCTOR':
        appointment_queryset = appointment_queryset.filter(
            Q(doctor=request.user) | Q(doctor_name__iexact=request.user.username)
        )
        consultation_queryset = consultation_queryset.filter(doctor=request.user)
        referral_queryset = referral_queryset.filter(
            Q(receiving_doctor=request.user) | Q(referring_doctor=request.user)
        )
    appointments = appointment_queryset.order_by('appointment_time')[:50]
    consultations = consultation_queryset[:50]
    referrals = referral_queryset[:50]

    return Response({
        'referrals': [
            {
                'id': referral.id,
                'patient_id': referral.patient.patient_id,
                'patient_name': referral.patient.full_name,
                'title': 'Clinical referral',
                'status': referral.status,
                'event_date': referral.created_at.date(),
                'reason': referral.reason,
            }
            for referral in referrals
        ],
        'consultations': [
            {
                'id': consultation.id,
                'patient_id': consultation.patient.patient_id,
                'patient_name': consultation.patient.full_name,
                'title': 'Clinical consultation',
                'status': consultation.status,
                'event_date': consultation.created_at.date(),
            }
            for consultation in consultations
        ],
        'appointments': [
            {
                'id': appointment.id,
                'patient_id': appointment.patient.patient_id,
                'patient_name': appointment.patient.full_name,
                'doctor_name': appointment.doctor_name,
                'appointment_time': appointment.appointment_time,
                'status': appointment.status,
            }
            for appointment in appointments
        ],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_patients(request):
    if request.user.role == 'PATIENT':
        patients = Patient.objects.filter(user=request.user)
    elif request.user.role in {'DOCTOR', 'ADMIN'}:
        patients = _doctor_queryset(request)
    else:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    return Response(PatientSerializer(patients, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_doctors(request):
    profiles = DoctorProfile.objects.select_related('user', 'facility').filter(user__is_active=True)
    return Response(DoctorProfileSerializer(profiles, many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def appointments_api(request):
    if request.method == 'GET':
        if request.user.role == 'PATIENT':
            appointments = Appointment.objects.filter(patient__user=request.user)
        elif request.user.role == 'DOCTOR':
            appointments = Appointment.objects.filter(doctor=request.user)
        elif request.user.role == 'ADMIN':
            appointments = Appointment.objects.all()
        else:
            return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(AppointmentSerializer(appointments, many=True).data)

    if request.user.role not in {'PATIENT', 'ADMIN'}:
        return Response({'error': 'Only patients or admins can create appointments.'}, status=status.HTTP_403_FORBIDDEN)
    patient, error = _get_patient_from_request(request, request.data.get('patient_id'))
    if error:
        return error
    doctor = None
    doctor_id = request.data.get('doctor_id')
    if doctor_id:
        doctor = get_user_model().objects.filter(id=doctor_id, role='DOCTOR', is_active=True).first()
        if not doctor:
            return Response({'error': 'Doctor not found.'}, status=status.HTTP_400_BAD_REQUEST)
    appointment_time = parse_datetime(str(request.data.get('appointment_time', '')))
    if appointment_time is None:
        return Response({'error': 'A valid appointment_time is required.'}, status=status.HTTP_400_BAD_REQUEST)
    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        doctor_name=request.data.get('doctor_name') or (doctor.username if doctor else 'Unassigned'),
        facility_id=request.data.get('facility_id') or None,
        appointment_time=appointment_time,
        queue_number=request.data.get('queue_number', 'A-17'),
        patients_ahead=request.data.get('patients_ahead', 0),
    )
    return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def consultations_api(request, consultation_id=None):
    if request.method == 'GET':
        if request.user.role == 'PATIENT':
            queryset = Consultation.objects.filter(patient__user=request.user)
        elif request.user.role == 'DOCTOR':
            queryset = Consultation.objects.filter(doctor=request.user)
        elif request.user.role == 'ADMIN':
            queryset = Consultation.objects.all()
        else:
            return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
        if consultation_id:
            consultation = queryset.filter(id=consultation_id).first()
            if not consultation:
                return Response({'error': 'Consultation not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(ConsultationSerializer(consultation).data)
        return Response(ConsultationSerializer(queryset, many=True).data)

    consultation = Consultation.objects.filter(id=consultation_id).first() if consultation_id else None
    if request.method == 'POST':
        if request.user.role not in {'DOCTOR', 'ADMIN'}:
            return Response({'error': 'Doctor access required.'}, status=status.HTTP_403_FORBIDDEN)
        patient, error = _get_patient_from_request(request, request.data.get('patient_id'))
        if error:
            return error
        doctor = request.user if request.user.role == 'DOCTOR' else get_user_model().objects.filter(
            id=request.data.get('doctor_id'), role='DOCTOR'
        ).first()
        if not doctor:
            return Response({'error': 'Doctor not found.'}, status=status.HTTP_400_BAD_REQUEST)
        consultation = Consultation.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_id=request.data.get('appointment_id') or None,
            facility_id=request.data.get('facility_id') or None,
            status=request.data.get('status', 'Draft'),
            symptoms=request.data.get('symptoms', ''),
            diagnosis=request.data.get('diagnosis', ''),
            treatment=request.data.get('treatment', ''),
            prescription=request.data.get('prescription', ''),
            notes=request.data.get('notes', ''),
            started_at=timezone.now(),
        )
        HealthTimelineRecord.objects.create(
            patient=patient,
            record_type='CONSULTATION',
            title='Clinical consultation',
            status='Completed' if consultation.status == 'Completed' else 'Upcoming',
            event_date=timezone.localdate(),
            facility_name=consultation.facility.name if consultation.facility else 'Assigned facility',
            doctor_name=doctor.username,
            health_issue=consultation.symptoms,
            diagnosis=consultation.diagnosis,
            prescription=consultation.prescription,
        )
        return Response(ConsultationSerializer(consultation).data, status=status.HTTP_201_CREATED)

    if not consultation:
        return Response({'error': 'Consultation not found.'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.role == 'DOCTOR' and consultation.doctor_id != request.user.id:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    if request.user.role == 'PATIENT' and consultation.patient.user_id != request.user.id:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PATCH':
        allowed = {'status', 'symptoms', 'diagnosis', 'treatment', 'prescription', 'notes'}
        for field in allowed:
            if field in request.data:
                setattr(consultation, field, request.data[field])
        if request.data.get('status') == 'Completed':
            consultation.completed_at = timezone.now()
        consultation.save()
        return Response(ConsultationSerializer(consultation).data)
    if request.user.role != 'ADMIN':
        return Response({'error': 'Only admins can delete consultations.'}, status=status.HTTP_403_FORBIDDEN)
    consultation.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def referrals_api(request, referral_id=None):
    if request.method == 'GET':
        if request.user.role == 'PATIENT':
            queryset = Referral.objects.filter(patient__user=request.user)
        elif request.user.role == 'DOCTOR':
            queryset = Referral.objects.filter(Q(referring_doctor=request.user) | Q(receiving_doctor=request.user)).distinct()
        elif request.user.role == 'ADMIN':
            queryset = Referral.objects.all()
        else:
            return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
        if referral_id:
            referral = queryset.filter(id=referral_id).first()
            if not referral:
                return Response({'error': 'Referral not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(ReferralSerializer(referral).data)
        return Response(ReferralSerializer(queryset, many=True).data)

    referral = Referral.objects.filter(id=referral_id).first() if referral_id else None
    if request.method == 'POST':
        if request.user.role not in {'DOCTOR', 'ADMIN'}:
            return Response({'error': 'Doctor access required.'}, status=status.HTTP_403_FORBIDDEN)
        patient, error = _get_patient_from_request(request, request.data.get('patient_id'))
        if error:
            return error
        referring_doctor = request.user if request.user.role == 'DOCTOR' else get_user_model().objects.filter(
            id=request.data.get('referring_doctor_id'), role='DOCTOR'
        ).first()
        if not referring_doctor:
            return Response({'error': 'Referring doctor not found.'}, status=status.HTTP_400_BAD_REQUEST)
        referral = Referral.objects.create(
            patient=patient,
            referring_doctor=referring_doctor,
            receiving_doctor_id=request.data.get('receiving_doctor_id') or None,
            referring_facility_id=request.data.get('referring_facility_id') or None,
            receiving_facility_id=request.data.get('receiving_facility_id') or None,
            reason=request.data.get('reason', ''),
            notes=request.data.get('notes', ''),
        )
        HealthTimelineRecord.objects.create(
            patient=patient,
            record_type='REFERRAL',
            title='Clinical referral',
            status='Pending',
            event_date=timezone.localdate(),
            facility_name=referral.referring_facility.name if referral.referring_facility else 'Assigned facility',
            doctor_name=referring_doctor.username,
            referral_reason=referral.reason,
            referral_target=referral.receiving_facility.name if referral.receiving_facility else '',
        )
        return Response(ReferralSerializer(referral).data, status=status.HTTP_201_CREATED)

    if not referral:
        return Response({'error': 'Referral not found.'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.role == 'DOCTOR' and request.user.id not in {referral.referring_doctor_id, referral.receiving_doctor_id}:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PATCH':
        if request.user.role not in {'DOCTOR', 'ADMIN'}:
            return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
        if 'status' in request.data:
            referral.status = request.data['status']
        if 'notes' in request.data:
            referral.notes = request.data['notes']
        referral.save()
        return Response(ReferralSerializer(referral).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def followups_api(request):
    if request.method == 'GET':
        if request.user.role == 'PATIENT':
            queryset = FollowUp.objects.filter(patient__user=request.user)
        elif request.user.role == 'DOCTOR':
            queryset = FollowUp.objects.filter(doctor=request.user)
        elif request.user.role == 'ADMIN':
            queryset = FollowUp.objects.all()
        else:
            return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(FollowUpSerializer(queryset, many=True).data)

    if request.user.role not in {'DOCTOR', 'ADMIN'}:
        return Response({'error': 'Doctor access required.'}, status=status.HTTP_403_FORBIDDEN)
    patient, error = _get_patient_from_request(request, request.data.get('patient_id'))
    if error:
        return error
    doctor = request.user if request.user.role == 'DOCTOR' else get_user_model().objects.filter(
        id=request.data.get('doctor_id'), role='DOCTOR'
    ).first()
    if not doctor:
        return Response({'error': 'Doctor not found.'}, status=status.HTTP_400_BAD_REQUEST)
    scheduled_for = parse_datetime(str(request.data.get('scheduled_for', '')))
    if scheduled_for is None:
        return Response({'error': 'A valid scheduled_for is required.'}, status=status.HTTP_400_BAD_REQUEST)
    followup = FollowUp.objects.create(
        patient=patient,
        doctor=doctor,
        consultation_id=request.data.get('consultation_id') or None,
        referral_id=request.data.get('referral_id') or None,
        scheduled_for=scheduled_for,
        purpose=request.data.get('purpose', ''),
        notes=request.data.get('notes', ''),
    )
    return Response(FollowUpSerializer(followup).data, status=status.HTTP_201_CREATED)


# 5. Symptom Checker Engine
@api_view(['POST'])
@permission_classes([AllowAny])
def check_symptoms(request):
    symptoms = request.data.get('symptoms', '').lower()
    
    is_emergency = any(kw in symptoms for kw in ['chest pain', 'unconscious', 'severe bleeding', 'breathing problem'])
    is_fever = 'fever' in symptoms or 'temperature' in symptoms

    if is_emergency:
        return Response({
            'risk_level': 'HIGH',
            'recommendation': 'Immediate emergency department / specialist referral recommended.',
            'action': 'DISPATCH_EMERGENCY'
        })
    elif is_fever:
        return Response({
            'risk_level': 'MODERATE',
            'recommendation': 'Visit Primary Health Centre for complete blood count (CBC) and doctor consultation.',
            'action': 'BOOK_PHC'
        })
    return Response({
        'risk_level': 'LOW',
        'recommendation': 'Routine consultation advised. Keep hydrated and observe symptoms.',
        'action': 'ROUTINE_CARE'
    })


# 6. Medicine Availability Search
@api_view(['GET'])
@permission_classes([AllowAny])
def search_medicines(request):
    query = request.GET.get('q', '').strip()
    
    if not MedicineStock.objects.exists():
        fac, _ = Facility.objects.get_or_create(name="CHC Bilaspur", facility_type="CHC")
        MedicineStock.objects.create(name="Paracetamol", dosage="500mg", facility=fac, is_available=True)
        MedicineStock.objects.create(name="Ferrous Sulphate", dosage="200mg", facility=fac, is_available=True)
        MedicineStock.objects.create(name="Amoxicillin", dosage="250mg", facility=fac, is_available=False)

    if query:
        medicines = MedicineStock.objects.filter(name__icontains=query)
    else:
        medicines = MedicineStock.objects.all()

    return Response(MedicineStockSerializer(medicines, many=True).data)


# 7. Emergency SOS Locator
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_sos(request):
    lat = request.data.get('latitude')
    lng = request.data.get('longitude')
    phone = request.data.get('phone', '')

    patient = getattr(request.user, 'patient_profile', None)
    if request.user.role == 'PATIENT' and patient is None:
        return Response({'error': 'Patient profile unavailable.'}, status=status.HTTP_403_FORBIDDEN)

    alert = SOSAlert.objects.create(patient=patient, latitude=lat, longitude=lng, phone=phone)
    
    nearest = Facility.objects.all()[:3]
    return Response({
        'status': 'SOS_DISPATCHED',
        'alert_id': alert.id,
        'nearest_facilities': FacilitySerializer(nearest, many=True).data
    }, status=status.HTTP_201_CREATED)