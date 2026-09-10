from rest_framework import serializers
from .models import (
    Patient, Facility, Appointment, HealthTimelineRecord, MedicineStock,
    SOSAlert, Consultation, Referral, FollowUp, DoctorProfile,
)

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ('user',)

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_gender = serializers.CharField(source='patient.gender', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    
    class Meta:
        model = Appointment
        fields = (
            'id', 'patient', 'doctor', 'doctor_name', 'facility', 'appointment_time',
            'queue_number', 'patients_ahead', 'status', 'facility_name',
            'patient_name', 'patient_gender', 'patient_phone',
        )

class HealthTimelineRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthTimelineRecord
        fields = '__all__'

class MedicineStockSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source='facility.name', read_only=True)

    class Meta:
        model = MedicineStock
        fields = '__all__'

class SOSAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSAlert
        fields = '__all__'


class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = '__all__'


class ReferralSerializer(serializers.ModelSerializer):
    referring_phc_name = serializers.CharField(source='referring_phc.username', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    receiving_facility_name = serializers.CharField(source='receiving_facility.name', read_only=True)
    receiving_doctor_name = serializers.CharField(source='receiving_doctor.username', read_only=True)

    class Meta:
        model = Referral
        fields = (
            'id', 'patient', 'referring_doctor', 'referring_phc',
            'receiving_doctor', 'referring_facility', 'receiving_facility',
            'reason', 'status', 'notes', 'created_at', 'updated_at',
            'referring_phc_name', 'patient_name', 'receiving_facility_name',
            'receiving_doctor_name',
        )


class FollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUp
        fields = '__all__'


class DoctorProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.SerializerMethodField()
    facility_name = serializers.CharField(source='facility.name', read_only=True)

    class Meta:
        model = DoctorProfile
        fields = ('id', 'user', 'username', 'name', 'specialty', 'facility', 'facility_name', 'experience_years', 'rating', 'consultation_fee', 'bio')

    def get_name(self, obj):
        full_name = obj.user.get_full_name().strip()
        return full_name or obj.user.username