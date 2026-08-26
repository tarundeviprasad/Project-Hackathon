from rest_framework import serializers
from .models import Patient, Facility, Appointment, HealthTimelineRecord, MedicineStock, SOSAlert

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

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