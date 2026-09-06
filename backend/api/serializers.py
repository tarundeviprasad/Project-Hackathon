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
    
    class Meta:
        model = Appointment
        fields = '__all__'

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
    class Meta:
        model = Referral
        fields = '__all__'


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