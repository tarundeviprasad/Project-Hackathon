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
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime, date
import random
import hashlib
import logging

logger = logging.getLogger(__name__)

from .models import (
    Patient, Facility, Appointment, HealthTimelineRecord, MedicineStock,
    SOSAlert, Consultation, Referral, FollowUp, DoctorProfile,
    HospitalAdminProfile, HospitalStaff, Equipment, BedResource, ASHAProfile, PHCProfile,
    DigitalTriageAssessment,
)
from .serializers import (
    PatientSerializer, FacilitySerializer, AppointmentSerializer,
    HealthTimelineRecordSerializer, MedicineStockSerializer, SOSAlertSerializer,
    ConsultationSerializer, ReferralSerializer, FollowUpSerializer,
    DoctorProfileSerializer, DigitalTriageAssessmentSerializer,
)
from .audit import record_audit_event


def _failed_login_key(request, identifier):
    raw_key = f'{request.META.get("REMOTE_ADDR", "unknown")}:{identifier.lower()}'
    return f'api-login-failures:{hashlib.sha256(raw_key.encode()).hexdigest()}'


def ensure_patient_profile_for_user(user, request=None):
    if getattr(user, 'role', None) != 'PATIENT':
        return getattr(user, 'patient_profile', None)

    patient = getattr(user, 'patient_profile', None)
    if patient:
        return patient

    full_name = (user.get_full_name() or user.username or 'Patient').strip() or 'Patient'
    patient_id = None
    while patient_id is None or Patient.objects.filter(patient_id=patient_id).exists():
        patient_id = f"AC-{datetime.now().year}-{random.randint(1000, 9999)}"

    patient = Patient.objects.create(
        user=user,
        patient_id=patient_id,
        full_name=full_name,
        dob=None,
        gender='None',
        phone='',
        email=user.email or '',
        address='',
        village='',
        district='',
        blood_group='Not Added',
        allergies='No allergies recorded',
        active_conditions='No active conditions',
        preferred_language='en',
    )

    if request is not None:
        record_audit_event(request, 'PATIENT_CREATED', target=patient, success=True)
    return patient


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
    if request.user.role == 'PHC':
        profile = PHCProfile.objects.filter(user=request.user).first()
        return bool(profile and profile.assigned_patients.filter(pk=patient.pk).exists())
    return _doctor_queryset(request).filter(pk=patient.pk).exists()


def _get_patient_from_request(request, patient_id=None):
    if patient_id:
        patient = Patient.objects.filter(patient_id=patient_id).first()
    elif request.user.role == 'PATIENT':
        patient = ensure_patient_profile_for_user(request.user, request=request)
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

    if getattr(request.user, 'role', None) == 'ASHA':
        profile = ASHAProfile.objects.filter(user=request.user).first()
        if profile:
            profile.assigned_patients.add(patient)
    elif getattr(request.user, 'role', None) == 'PHC':
        profile = PHCProfile.objects.filter(user=request.user).first()
        if profile:
            profile.assigned_patients.add(patient)

    # Seed a default timeline entry for the new patient
    HealthTimelineRecord.objects.create(
        patient=patient,
        record_type='CONSULTATION',
        title='PHC Consultation',
        status='Completed',
        event_date=date.today(),
        facility_name=f"PHC {patient.village or 'Primary'}",
        doctor_name='',
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
    patient = ensure_patient_profile_for_user(user, request=request)
    record_audit_event(request, 'LOGIN_SUCCESS', user=user)
    response = {'user': {'id': user.id, 'role': user.role, 'username': user.username}}
    response['patient'] = PatientSerializer(patient).data
    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def hospital_admins_api(request):
    if request.user.role != 'ADMIN':
        record_audit_event(request, 'PERMISSION_DENIED', user=request.user, success=False)
        return Response({'error': 'System administrator access required.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        profiles = HospitalAdminProfile.objects.select_related('user', 'facility').order_by('-created_at')
        return Response([
            {
                'id': profile.id,
                'hospital_name': profile.facility.name,
                'location': profile.facility.latitude,
                'address': profile.address,
                'admin_name': profile.admin_name,
                'username': profile.user.username,
                'email': profile.user.email,
                'phone': profile.phone,
                'is_active': profile.user.is_active,
                'created_at': profile.created_at,
            }
            for profile in profiles
        ])

    data = request.data
    username = str(data.get('username', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = data.get('password', '')
    password_confirm = data.get('password_confirm', '')
    admin_name = str(data.get('admin_name', '')).strip()
    hospital_name = str(data.get('hospital_name', '')).strip()
    phone = str(data.get('phone', '')).strip()
    address = str(data.get('address', '')).strip()
    errors = {}

    if not hospital_name:
        errors['hospital_name'] = 'Hospital name is required.'
    if not admin_name:
        errors['admin_name'] = 'Administrator name is required.'
    if not username:
        errors['username'] = 'Username is required.'
    elif get_user_model().objects.filter(username__iexact=username).exists():
        errors['username'] = 'Username already exists.'
    if not email:
        errors['email'] = 'Email is required.'
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = 'Enter a valid email address.'
        if get_user_model().objects.filter(email__iexact=email).exists():
            errors['email'] = 'Email already exists.'
    if password != password_confirm:
        errors['password_confirm'] = 'Passwords do not match.'
    try:
        validate_password(password)
    except ValidationError as error:
        errors['password'] = error.messages
    if not phone:
        errors['phone'] = 'Phone number is required.'
    if errors:
        return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        facility, _ = Facility.objects.get_or_create(name=hospital_name, defaults={'facility_type': 'Hospital'})
        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=admin_name,
            role='HOSPITAL_ADMIN',
        )
        profile = HospitalAdminProfile.objects.create(
            user=user,
            facility=facility,
            admin_name=admin_name,
            phone=phone,
            address=address,
        )
    record_audit_event(request, 'HOSPITAL_ADMIN_CREATED', user=request.user, target=user)
    return Response({
        'message': 'Hospital administrator account created successfully.',
        'hospital_admin': {
            'id': profile.id,
            'hospital_name': facility.name,
            'admin_name': profile.admin_name,
            'username': user.username,
            'email': user.email,
            'phone': profile.phone,
            'address': profile.address,
        },
    }, status=status.HTTP_201_CREATED)


# 3. Patient Dashboard Snapshot
def _get_patient_dashboard(request, patient_id):
    patient, error = _authorized_patient(request, patient_id)
    if error:
        return error
    record_audit_event(request, 'PATIENT_VIEWED', target=patient)

    next_apt = Appointment.objects.filter(patient=patient, status='Scheduled').order_by('appointment_time').first()
    records_count = HealthTimelineRecord.objects.filter(patient=patient).count()
    active_referrals = HealthTimelineRecord.objects.filter(patient=patient, record_type='REFERRAL', status='Pending').count()

    doctor = None
    appointment_doctor = Appointment.objects.filter(
        patient=patient,
        doctor__isnull=False,
    ).select_related('doctor', 'facility').order_by('appointment_time').first()
    consultation_doctor = Consultation.objects.filter(
        patient=patient,
    ).select_related('doctor', 'facility').order_by('-created_at').first()
    referral_doctor = Referral.objects.filter(
        patient=patient,
    ).select_related('receiving_doctor', 'receiving_facility', 'referring_doctor').order_by('-created_at').first()
    if appointment_doctor:
        doctor = appointment_doctor.doctor
        doctor_facility = appointment_doctor.facility
    elif consultation_doctor:
        doctor = consultation_doctor.doctor
        doctor_facility = consultation_doctor.facility
    elif referral_doctor:
        doctor = referral_doctor.receiving_doctor or referral_doctor.referring_doctor
        doctor_facility = referral_doctor.receiving_facility or referral_doctor.referring_facility

    doctor_details = None
    if doctor:
        doctor_profile = getattr(doctor, 'doctor_profile', None)
        doctor_details = {
            'name': doctor.get_full_name().strip() or doctor.username,
            'specialty': doctor_profile.specialty if doctor_profile else 'Doctor',
            'facility_name': doctor_facility.name if doctor_facility else (
                doctor_profile.facility.name if doctor_profile and doctor_profile.facility else None
            ),
            'phone': doctor.phone if hasattr(doctor, 'phone') else '',
            'email': doctor.email,
        }

    return Response({
        'patient': PatientSerializer(patient).data,
        'doctor': doctor_details,
        'snapshot': {
            'blood_group': patient.blood_group,
            'next_appointment': next_apt.appointment_time.strftime('%I:%M %p') if next_apt else None,
            'active_referrals': active_referrals,
            'records_count': records_count,
            'queue_token': next_apt.queue_number if next_apt else None,
            'patients_ahead': next_apt.patients_ahead if next_apt else None
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_dashboard(request, patient_id):
    return _get_patient_dashboard(request, patient_id)


# 4. Digital Health Records Timeline & Stats
def _get_health_records(request, patient_id):
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
def get_health_records(request, patient_id):
    return _get_health_records(request, patient_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_patient_dashboard(request):
    patient = ensure_patient_profile_for_user(request.user, request=request)
    return _get_patient_dashboard(request, patient.patient_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_health_records(request):
    patient = ensure_patient_profile_for_user(request.user, request=request)
    return _get_health_records(request, patient.patient_id)


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
        'doctor': {
            'name': request.user.get_full_name().strip() or request.user.username,
            'username': request.user.username,
            'email': request.user.email,
            'specialty': getattr(getattr(request.user, 'doctor_profile', None), 'specialty', 'Doctor'),
        },
        'stats': {
            'appointments': appointment_queryset.count(),
            'consultations': consultation_queryset.count(),
            'patients': _doctor_queryset(request).count(),
            'referrals': referral_queryset.count(),
        },
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
def get_asha_dashboard(request):
    if request.user.role != 'ASHA':
        record_audit_event(request, 'PERMISSION_DENIED', user=request.user, success=False)
        return Response({'error': 'ASHA access required.'}, status=status.HTTP_403_FORBIDDEN)

    profile = ASHAProfile.objects.filter(user=request.user).prefetch_related('assigned_patients').first()
    if not profile:
        return Response({'error': 'ASHA profile unavailable.'}, status=status.HTTP_404_NOT_FOUND)

    assigned_patients = profile.assigned_patients.all()
    patient_ids = assigned_patients.values_list('id', flat=True)
    followups = FollowUp.objects.filter(patient_id__in=patient_ids).select_related('patient').order_by('scheduled_for')[:20]
    pending_referrals = Referral.objects.filter(patient_id__in=patient_ids, status='Pending').select_related('patient')[:20]
    return Response({
        'worker': {
            'name': request.user.get_full_name().strip() or request.user.username,
            'username': request.user.username,
            'email': request.user.email,
            'worker_id': profile.worker_id,
            'area': profile.area,
        },
        'stats': {
            'patients_registered': assigned_patients.count(),
            'followups_due': FollowUp.objects.filter(patient_id__in=patient_ids, status='Scheduled').count(),
            'active_referrals': Referral.objects.filter(patient_id__in=patient_ids, status='Pending').count(),
            'households_covered': assigned_patients.count() * 12,
        },
        'patients': PatientSerializer(assigned_patients.order_by('full_name'), many=True).data,
        'followups': [
            {
                'id': followup.id,
                'patient_name': followup.patient.full_name,
                'purpose': followup.purpose,
                'scheduled_for': followup.scheduled_for.isoformat(),
                'status': followup.status,
            }
            for followup in followups
        ],
        'tasks': [
            {'title': 'Follow up referral', 'detail': f'{referral.patient.full_name}: {referral.reason}'}
            for referral in pending_referrals
        ],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_phc_dashboard(request):
    if request.user.role != 'PHC':
        record_audit_event(request, 'PERMISSION_DENIED', user=request.user, success=False)
        return Response({'error': 'PHC access required.'}, status=status.HTTP_403_FORBIDDEN)

    profile = PHCProfile.objects.filter(user=request.user).select_related('facility').prefetch_related('assigned_patients').first()
    user_name = request.user.get_full_name().strip() or request.user.username

    if not profile:
        return Response({
            'phc': {
                'name': 'PHC Centre',
                'centre_id': 'PHC-UNASSIGNED',
                'facility_id': None,
                'user_name': user_name,
            },
            'stats': {
                'patients': 0,
                'appointments': 0,
                'waiting': 0,
                'active_referrals': 0,
            },
            'patients': [],
            'appointments': [],
            'referrals': [],
            'notifications': [],
            'staff': [],
            'inventory': [],
            'labs': [],
            'asha': [],
            'analytics': [],
        })

    patients = profile.assigned_patients.all()
    patient_ids = patients.values_list('id', flat=True)
    appointments = Appointment.objects.filter(patient_id__in=patient_ids).order_by('appointment_time')
    referrals = Referral.objects.filter(
        Q(referring_phc=request.user) | Q(patient_id__in=patient_ids)
    ).select_related('patient', 'receiving_doctor', 'receiving_facility').order_by('-created_at')
    facility_medicines = MedicineStock.objects.filter(facility=profile.facility).order_by('name')
    facility_labs = HealthTimelineRecord.objects.filter(patient_id__in=patient_ids, record_type='LAB_TEST').order_by('-event_date')[:20]
    facility_doctors = DoctorProfile.objects.filter(facility=profile.facility).select_related('user')
    asha_workers = ASHAProfile.objects.filter(assigned_patients__in=patients).select_related('user').distinct()
    return Response({
        'phc': {
            'name': profile.facility.name,
            'centre_id': profile.centre_id,
            'facility_id': profile.facility_id,
            'user_name': user_name,
        },
        'stats': {
            'patients': patients.count(),
            'appointments': appointments.filter(status='Scheduled').count(),
            'waiting': appointments.filter(status='Scheduled').count(),
            'active_referrals': referrals.filter(status='Pending').count(),
        },
        'patients': PatientSerializer(patients.order_by('full_name'), many=True).data,
        'appointments': AppointmentSerializer(appointments[:50], many=True).data,
        'referrals': ReferralSerializer(referrals[:50], many=True).data,
        'notifications': [
            {'title': 'Referral requires review', 'detail': referral.reason, 'status': referral.status}
            for referral in referrals.filter(status='Pending')[:5]
        ],
        'staff': DoctorProfileSerializer(facility_doctors, many=True).data,
        'inventory': MedicineStockSerializer(facility_medicines, many=True).data,
        'labs': HealthTimelineRecordSerializer(facility_labs, many=True).data,
        'asha': [
            {'name': worker.user.get_full_name() or worker.user.username, 'worker_id': worker.worker_id, 'area': worker.area}
            for worker in asha_workers
        ],
        'analytics': [
            {'label': 'Scheduled appointments', 'value': appointments.filter(status='Scheduled').count()},
            {'label': 'Completed consultations', 'value': Consultation.objects.filter(patient_id__in=patient_ids, status='Completed').count()},
        ],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_hospital_dashboard(request):
    if request.user.role != 'HOSPITAL_ADMIN':
        record_audit_event(request, 'PERMISSION_DENIED', user=request.user, success=False)
        return Response({'error': 'Hospital administrator access required.'}, status=status.HTTP_403_FORBIDDEN)
    profile = HospitalAdminProfile.objects.filter(user=request.user).select_related('facility').first()
    if not profile:
        return Response({'error': 'Hospital administrator profile unavailable.'}, status=status.HTTP_404_NOT_FOUND)

    facility = profile.facility
    patients = Patient.objects.filter(
        Q(appointments__facility=facility)
        | Q(consultations__facility=facility)
        | Q(referrals__referring_facility=facility)
        | Q(referrals__receiving_facility=facility)
    ).distinct()
    appointments = Appointment.objects.filter(facility=facility).select_related('patient', 'doctor').order_by('appointment_time')
    referrals = Referral.objects.filter(
        Q(referring_facility=facility) | Q(receiving_facility=facility)
    ).select_related('patient', 'receiving_doctor').order_by('-created_at')
    doctors = DoctorProfile.objects.filter(facility=facility).select_related('user')
    staff = HospitalStaff.objects.filter(facility=facility).order_by('name')
    equipment = Equipment.objects.filter(facility=facility).order_by('name')
    beds = BedResource.objects.filter(facility=facility).order_by('name')
    medicines = MedicineStock.objects.filter(facility=facility).order_by('name')
    return Response({
        'hospital': {
            'name': facility.name,
            'facility_id': facility.id,
            'facility_type': facility.facility_type,
            'admin_name': profile.admin_name,
            'admin_email': profile.user.email,
            'phone': profile.phone,
            'address': profile.address,
        },
        'stats': {
            'patients': patients.count(),
            'doctors': doctors.count(),
            'appointments': appointments.filter(status='Scheduled').count(),
            'pending_referrals': referrals.filter(status='Pending').count(),
        },
        'patients': PatientSerializer(patients.order_by('full_name')[:100], many=True).data,
        'appointments': AppointmentSerializer(appointments[:100], many=True).data,
        'referrals': ReferralSerializer(referrals[:100], many=True).data,
        'doctors': DoctorProfileSerializer(doctors, many=True).data,
        'staff': list(staff.values('id', 'name', 'staff_id', 'role', 'department', 'status', 'contact')),
        'equipment': list(equipment.values('id', 'name', 'quantity', 'category')),
        'beds': list(beds.values('id', 'name', 'total', 'occupied')),
        'medicines': list(medicines.values('id', 'name', 'medicine_id', 'category', 'quantity', 'unit', 'reorder_level', 'expiry_date')),
    })


def _hospital_facility(request):
    if request.user.role != 'HOSPITAL_ADMIN':
        return None, Response({'error': 'Hospital administrator access required.'}, status=status.HTTP_403_FORBIDDEN)
    profile = HospitalAdminProfile.objects.filter(user=request.user).select_related('facility').first()
    if not profile:
        return None, Response({'error': 'Hospital administrator profile unavailable.'}, status=status.HTTP_404_NOT_FOUND)
    return profile.facility, None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hospital_staff_api(request):
    facility, error = _hospital_facility(request)
    if error:
        return error
    required = ('name', 'staff_id', 'role', 'department', 'status', 'contact')
    missing = [field for field in required if not str(request.data.get(field, '')).strip()]
    if missing:
        return Response({'error': f'Missing fields: {", ".join(missing)}'}, status=status.HTTP_400_BAD_REQUEST)
    if HospitalStaff.objects.filter(facility=facility, staff_id=request.data['staff_id'].strip()).exists():
        return Response({'error': 'That staff ID already exists at this hospital.'}, status=status.HTTP_400_BAD_REQUEST)
    staff = HospitalStaff.objects.create(
        facility=facility, name=request.data['name'].strip(), staff_id=request.data['staff_id'].strip(),
        role=request.data['role'].strip(), department=request.data['department'].strip(),
        status=request.data['status'].strip(), contact=request.data['contact'].strip(),
    )
    return Response({'id': staff.id, 'message': 'Staff member saved.'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hospital_equipment_api(request):
    facility, error = _hospital_facility(request)
    if error:
        return error
    name = str(request.data.get('name', '')).strip()
    category = str(request.data.get('category', 'basic')).strip()
    try:
        quantity = int(request.data.get('quantity', 0))
    except (TypeError, ValueError):
        quantity = 0
    if not name or quantity < 1 or category not in dict(Equipment.CATEGORY_CHOICES):
        return Response({'error': 'Name, positive quantity, and valid category are required.'}, status=status.HTTP_400_BAD_REQUEST)
    equipment = Equipment.objects.create(facility=facility, name=name, quantity=quantity, category=category)
    return Response({'id': equipment.id, 'message': 'Equipment saved.'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hospital_medicines_api(request):
    facility, error = _hospital_facility(request)
    if error:
        return error
    try:
        quantity = int(request.data.get('quantity', 0))
        reorder_level = int(request.data.get('reorder_level', 0))
    except (TypeError, ValueError):
        quantity = reorder_level = 0
    name = str(request.data.get('name', '')).strip()
    medicine_id = str(request.data.get('medicine_id', '')).strip()
    expiry_date = request.data.get('expiry_date') or None
    if not name or not medicine_id or quantity < 0 or reorder_level < 1 or not expiry_date:
        return Response({'error': 'Medicine name, ID, stock, reorder level, and expiry date are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if MedicineStock.objects.filter(facility=facility, medicine_id=medicine_id).exists():
        return Response({'error': 'That medicine ID already exists at this hospital.'}, status=status.HTTP_400_BAD_REQUEST)
    medicine = MedicineStock.objects.create(
        facility=facility, name=name, medicine_id=medicine_id, category=str(request.data.get('category', '')).strip(),
        quantity=quantity, unit=str(request.data.get('unit', 'Tablets')).strip() or 'Tablets',
        reorder_level=reorder_level, expiry_date=expiry_date, is_available=quantity > 0,
    )
    return Response({'id': medicine.id, 'message': 'Medicine saved.'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_patients(request):
    if request.user.role == 'PATIENT':
        patients = Patient.objects.filter(user=request.user)
    elif request.user.role in {'DOCTOR', 'ADMIN'}:
        patients = _doctor_queryset(request)
    elif request.user.role == 'PHC':
        profile = PHCProfile.objects.filter(user=request.user).first()
        patients = profile.assigned_patients.all() if profile else Patient.objects.none()
    else:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    query = request.GET.get('search', '').strip()
    if query:
        patients = patients.filter(
            Q(full_name__icontains=query)
            | Q(patient_id__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
        )
    return Response(PatientSerializer(patients, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_doctors(request):
    profiles = DoctorProfile.objects.select_related('user', 'facility').filter(user__is_active=True)
    return Response(DoctorProfileSerializer(profiles, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_facilities(request):
    return Response(FacilitySerializer(Facility.objects.order_by('name'), many=True).data)


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
        elif request.user.role == 'PHC':
            profile = PHCProfile.objects.filter(user=request.user).first()
            appointments = Appointment.objects.filter(patient__in=profile.assigned_patients.all()) if profile else Appointment.objects.none()
        else:
            return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(AppointmentSerializer(appointments, many=True).data)

    if request.user.role not in {'PATIENT', 'ADMIN'}:
        return Response({'error': 'Only patients or admins can create appointments.'}, status=status.HTTP_403_FORBIDDEN)

    payload = request.data.copy()
    logger.info(
        'APPOINTMENT_CREATE_REQUEST user=%s user_id=%s username=%s email=%s is_authenticated=%s payload=%s',
        request.user,
        getattr(request.user, 'id', None),
        getattr(request.user, 'username', None),
        getattr(request.user, 'email', None),
        getattr(request.user, 'is_authenticated', False),
        payload,
    )

    patient, error = _get_patient_from_request(request, request.data.get('patient_id'))
    if error:
        logger.warning('APPOINTMENT_CREATE_PATIENT_LOOKUP_FAILED user=%s user_id=%s patient_id=%s error=%s', request.user, getattr(request.user, 'id', None), request.data.get('patient_id'), error.data)
        return error

    doctor = None
    doctor_id = request.data.get('doctor_id')
    if doctor_id:
        doctor = get_user_model().objects.filter(id=doctor_id, role='DOCTOR', is_active=True).first()
        logger.info('APPOINTMENT_CREATE_DOCTOR_LOOKUP doctor_id=%s result=%s', doctor_id, doctor.id if doctor else None)
        if not doctor:
            logger.warning('APPOINTMENT_CREATE_DOCTOR_NOT_FOUND doctor_id=%s user=%s', doctor_id, getattr(request.user, 'id', None))
            return Response({'error': 'Doctor not found.'}, status=status.HTTP_400_BAD_REQUEST)

    appointment_time = parse_datetime(str(request.data.get('appointment_time', '')))
    logger.info('APPOINTMENT_CREATE_TIME_RAW=%s parsed=%s', request.data.get('appointment_time'), appointment_time)
    if appointment_time is None:
        logger.warning('APPOINTMENT_CREATE_INVALID_TIME user=%s payload=%s', request.user, payload)
        return Response({'error': 'A valid appointment_time is required.'}, status=status.HTTP_400_BAD_REQUEST)

    reason = str(request.data.get('reason', '') or '').strip() or 'General consultation'
    duplicate = Appointment.objects.filter(
        patient=patient,
        doctor=doctor,
        appointment_time=appointment_time,
        status__in=['Scheduled', 'Completed'],
    ).exists()
    logger.info('APPOINTMENT_CREATE_DUPLICATE_CHECK patient=%s doctor=%s appointment_time=%s duplicate=%s', getattr(patient, 'id', None), getattr(doctor, 'id', None), appointment_time, duplicate)
    if duplicate:
        return Response({'error': 'An appointment for this doctor and time already exists.'}, status=status.HTTP_409_CONFLICT)

    try:
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            doctor_name=request.data.get('doctor_name') or (doctor.username if doctor else 'Unassigned'),
            facility_id=request.data.get('facility_id') or None,
            appointment_time=appointment_time,
            reason=reason,
            queue_number=request.data.get('queue_number', 'A-17'),
            patients_ahead=request.data.get('patients_ahead', 0),
        )
        logger.info(
            'APPOINTMENT_CREATE_SUCCESS user=%s patient=%s doctor=%s id=%s reason=%s',
            getattr(request.user, 'id', None),
            getattr(patient, 'id', None),
            getattr(doctor, 'id', None),
            appointment.id,
            appointment.reason,
        )
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
    except Exception:
        logger.exception(
            'APPOINTMENT_CREATE_DB_ERROR user=%s patient=%s doctor=%s payload=%s',
            getattr(request.user, 'id', None),
            getattr(patient, 'id', None),
            getattr(doctor, 'id', None),
            payload,
        )
        return Response({'error': 'Unable to create appointment due to a server-side validation or database error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        elif request.user.role == 'PHC':
            queryset = Referral.objects.filter(
                Q(referring_phc=request.user) | Q(patient__phc_centres__user=request.user)
            ).distinct()
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
        if request.user.role not in {'DOCTOR', 'PHC', 'ADMIN'}:
            return Response({'error': 'Doctor or PHC access required.'}, status=status.HTTP_403_FORBIDDEN)
        patient, error = _get_patient_from_request(request, request.data.get('patient_id'))
        if error:
            return error
        referring_doctor = request.user if request.user.role == 'DOCTOR' else None
        referring_phc = request.user if request.user.role == 'PHC' else None
        if request.user.role == 'PHC':
            profile = PHCProfile.objects.filter(user=request.user).first()
            if not profile or not profile.assigned_patients.filter(pk=patient.pk).exists():
                return Response({'error': 'Patient is not assigned to this PHC.'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role == 'ADMIN':
            referring_doctor = get_user_model().objects.filter(
                id=request.data.get('referring_doctor_id'), role='DOCTOR'
            ).first()
            if not referring_doctor:
                return Response({'error': 'Referring doctor not found.'}, status=status.HTTP_400_BAD_REQUEST)
        referral = Referral.objects.create(
            patient=patient,
            referring_doctor=referring_doctor,
            referring_phc=referring_phc,
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
            doctor_name=(referring_doctor.username if referring_doctor else request.user.username),
            referral_reason=referral.reason,
            referral_target=referral.receiving_facility.name if referral.receiving_facility else '',
        )
        return Response(ReferralSerializer(referral).data, status=status.HTTP_201_CREATED)

    if not referral:
        return Response({'error': 'Referral not found.'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.role == 'DOCTOR' and request.user.id not in {referral.referring_doctor_id, referral.receiving_doctor_id}:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    if request.user.role == 'PHC' and referral.referring_phc_id != request.user.id:
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
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def patient_triage_assessment(request, patient_id=None):
    if request.method == 'GET':
        if patient_id:
            patient, error = _get_patient_from_request(request, patient_id)
            if error:
                return error
        else:
            patient = getattr(request.user, 'patient_profile', None)
            if not patient:
                return Response({'error': 'Patient profile unavailable.'}, status=status.HTTP_404_NOT_FOUND)
        screenings = DigitalTriageAssessment.objects.filter(patient=patient).order_by('-created_at')
        return Response({
            'patient': PatientSerializer(patient).data,
            'history': DigitalTriageAssessmentSerializer(screenings, many=True).data,
        })

    if request.user.role != 'PATIENT':
        return Response({'error': 'Patient access required.'}, status=status.HTTP_403_FORBIDDEN)

    patient = getattr(request.user, 'patient_profile', None)
    if not patient:
        return Response({'error': 'Patient profile unavailable.'}, status=status.HTTP_404_NOT_FOUND)

    main_symptom = str(request.data.get('main_symptom', '')).strip()
    duration = str(request.data.get('duration', '')).strip()
    additional_symptoms = request.data.get('additional_symptoms') or []
    follow_up_answers = request.data.get('follow_up_answers') or []

    if not main_symptom:
        return Response({'error': 'Main symptom is required.'}, status=status.HTTP_400_BAD_REQUEST)

    combined = f"{main_symptom} {' '.join(additional_symptoms or [])} {' '.join(follow_up_answers or [])}".lower()
    emergency_keywords = ['chest pain', 'difficulty breathing', 'breathlessness', 'shortness of breath', 'loss of consciousness', 'unconscious', 'severe bleeding', 'crushing pain', 'confusion']
    medium_keywords = ['fever', 'vomiting', 'diarrhea', 'dizziness', 'palpitations', 'persistent', 'week', 'severe']

    if any(keyword in combined for keyword in emergency_keywords):
        priority = 'EMERGENCY'
        recommendation = 'Immediate medical attention is recommended. Please seek urgent care or emergency services now.'
    elif any(keyword in combined for keyword in medium_keywords) or duration.lower().find('week') >= 0:
        priority = 'MEDIUM'
        recommendation = 'Please schedule a PHC/doctor consultation promptly for evaluation.'
    else:
        priority = 'LOW'
        recommendation = 'Your symptoms appear stable, but continue monitoring and seek care if they worsen.'

    triage = DigitalTriageAssessment.objects.create(
        patient=patient,
        main_symptom=main_symptom,
        duration=duration,
        additional_symptoms=list(additional_symptoms),
        follow_up_answers=list(follow_up_answers),
        priority=priority,
        recommendation=recommendation,
        source='patient_portal',
    )

    try:
        HealthTimelineRecord.objects.create(
            patient=patient,
            record_type='CONSULTATION',
            title='Digital Triage Assessment',
            status='Completed',
            event_date=timezone.localdate(),
            facility_name='Patient Portal',
            doctor_name='Digital Triage',
            health_issue=main_symptom,
            diagnosis=f'Triage priority: {priority}',
            risk_level=priority,
            prescription=recommendation,
        )
    except Exception:
        pass

    return Response(DigitalTriageAssessmentSerializer(triage).data, status=status.HTTP_201_CREATED)


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