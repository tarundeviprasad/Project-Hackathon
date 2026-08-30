from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('None', 'Prefer not to say'),
    ]
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('te', 'Telugu'),
        ('mr', 'Marathi'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='patient_profile')
    patient_id = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=200)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='None')
    phone = models.CharField(max_length=15, db_index=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(blank=True, default='')
    village = models.CharField(max_length=150)
    district = models.CharField(max_length=150)
    blood_group = models.CharField(max_length=10, default='Not Added')
    allergies = models.CharField(max_length=255, default='No allergies recorded')
    active_conditions = models.CharField(max_length=255, default='No active conditions')
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_id} - {self.full_name}"


class Facility(models.Model):
    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=100, default='PHC')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    distance_km = models.FloatField(default=10.0)
    has_specialist = models.BooleanField(default=True)
    match_score = models.IntegerField(default=90)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor_name = models.CharField(max_length=150)
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True)
    appointment_time = models.DateTimeField()
    queue_number = models.CharField(max_length=20, default='A-17')
    patients_ahead = models.IntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

    def __str__(self):
        return f"{self.patient.full_name} with {self.doctor_name}"


class HealthTimelineRecord(models.Model):
    RECORD_TYPES = [
        ('CONSULTATION', 'PHC / Specialist Consultation'),
        ('LAB_TEST', 'Lab Test'),
        ('REFERRAL', 'Referral Created'),
        ('FOLLOW_UP', 'Follow-up Scheduled'),
    ]
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Available', 'Available'),
        ('Pending', 'Pending'),
        ('Upcoming', 'Upcoming'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='timeline_records')
    record_type = models.CharField(max_length=30, choices=RECORD_TYPES)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Completed')
    event_date = models.DateField()
    facility_name = models.CharField(max_length=200)
    
    doctor_name = models.CharField(max_length=150, blank=True, null=True)
    health_issue = models.CharField(max_length=255, blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    test_name = models.CharField(max_length=200, blank=True, null=True)
    test_result = models.CharField(max_length=255, blank=True, null=True)
    prescription = models.TextField(blank=True, null=True)
    referral_source = models.CharField(max_length=150, blank=True, null=True)
    referral_target = models.CharField(max_length=150, blank=True, null=True)
    referral_reason = models.TextField(blank=True, null=True)
    risk_level = models.CharField(max_length=50, default='Medium')
    followup_purpose = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.record_type} - {self.patient.full_name}"


class MedicineStock(models.Model):
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=50, default='500mg')
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='medicines')
    is_available = models.BooleanField(default=True)
    quantity = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.name} {self.dosage}"


class SOSAlert(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"SOS Alert ({self.latitude}, {self.longitude})"