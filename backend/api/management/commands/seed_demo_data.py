from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.models import (
    Appointment,
    ASHAProfile,
    AuditLog,
    BedResource,
    Consultation,
    DigitalTriageAssessment,
    DoctorProfile,
    Equipment,
    Facility,
    FollowUp,
    HealthTimelineRecord,
    HospitalAdminProfile,
    HospitalStaff,
    MedicineStock,
    Patient,
    PHCProfile,
    Referral,
    SOSAlert,
)
from auth.models import User


class Command(BaseCommand):
    help = "Replace stale application data with connected fictional demo data."

    def handle(self, *args, **options):
        with transaction.atomic():
            self.clear_data()
            data = self.seed_data()
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        for label, value in data.items():
            self.stdout.write(f"{label}: {value}")

    def clear_data(self):
        AuditLog.objects.all().delete()
        SOSAlert.objects.all().delete()
        FollowUp.objects.all().delete()
        Consultation.objects.all().delete()
        Referral.objects.all().delete()
        DigitalTriageAssessment.objects.all().delete()
        HealthTimelineRecord.objects.all().delete()
        Appointment.objects.all().delete()
        HospitalStaff.objects.all().delete()
        Equipment.objects.all().delete()
        BedResource.objects.all().delete()
        MedicineStock.objects.all().delete()
        ASHAProfile.objects.all().delete()
        PHCProfile.objects.all().delete()
        HospitalAdminProfile.objects.all().delete()
        DoctorProfile.objects.all().delete()
        Patient.objects.all().delete()
        Facility.objects.all().delete()

        stale_usernames = {
            "testpatient", "doctor1", "admin1", "patient1", "signup_probe_user",
            "test_login_user", "vinay_1788205055654", "DOC1@gmail.com", "hOSadmin",
            "ASHA@gmail.com", "ASHA1@gmail.com", "PHC1@gmail.com", "navcheck",
            "dashboard-e2e-admin", "triage_redirect_probe",
        }
        User.objects.filter(username__in=stale_usernames, is_superuser=False).delete()

    def user(self, username, email, role, first_name, last_name="", password="DemoPass!2026"):
        account, _ = User.objects.get_or_create(username=username)
        account.email = email
        account.role = role
        account.first_name = first_name
        account.last_name = last_name
        account.is_active = True
        account.set_password(password)
        account.save()
        return account

    def seed_data(self):
        today = timezone.localdate()
        now = timezone.now()
        hospital = Facility.objects.create(
            name="Saanvi Multispeciality Hospital",
            facility_type="Hospital",
            latitude=17.4239,
            longitude=78.4738,
            phone="040-41002020",
            distance_km=2.4,
            has_specialist=True,
            match_score=98,
        )
        phc = Facility.objects.create(
            name="Nirmala Community Health Centre",
            facility_type="PHC",
            latitude=17.4512,
            longitude=78.3821,
            phone="040-41003030",
            distance_km=8.1,
            has_specialist=False,
            match_score=90,
        )
        outreach = Facility.objects.create(
            name="Kaveri Rural Health Unit",
            facility_type="CHC",
            latitude=17.2561,
            longitude=78.4120,
            phone="040-41004040",
            distance_km=14.7,
            has_specialist=False,
            match_score=84,
        )

        hospital_admin = self.user("demo.hospital", "hospital.demo@example.test", "HOSPITAL_ADMIN", "Meera", "Iyer")
        HospitalAdminProfile.objects.create(
            user=hospital_admin,
            facility=hospital,
            admin_name="Meera Iyer",
            phone="9000000001",
            address="Saanvi Nagar, Hyderabad",
        )
        system_admin = self.user("demo.admin", "admin.demo@example.test", "ADMIN", "Rohan", "Mehta")

        doctor_specs = [
            ("demo.dr.ananya", "ananya.doctor@example.test", "Ananya", "Sharma", "General Medicine", 9, "Primary and preventive care"),
            ("demo.dr.rahul", "rahul.doctor@example.test", "Rahul", "Verma", "Cardiology", 12, "Adult cardiac care"),
            ("demo.dr.priya", "priya.doctor@example.test", "Priya", "Reddy", "Neurology", 10, "Headache and stroke care"),
            ("demo.dr.arjun", "arjun.doctor@example.test", "Arjun", "Kumar", "Pediatrics", 8, "Child and adolescent health"),
            ("demo.dr.sneha", "sneha.doctor@example.test", "Sneha", "Rao", "Gynecology", 11, "Women's health and antenatal care"),
            ("demo.dr.kavya", "kavya.doctor@example.test", "Kavya", "Nair", "General Medicine", 7, "Chronic disease management"),
        ]
        doctors = []
        for index, (username, email, first, last, specialty, experience, bio) in enumerate(doctor_specs):
            doctor = self.user(username, email, "DOCTOR", first, last)
            doctors.append(doctor)
            DoctorProfile.objects.create(
                user=doctor,
                specialty=specialty,
                facility=hospital if index < 5 else phc,
                experience_years=experience,
                rating=Decimal("4.8") if index < 3 else Decimal("4.6"),
                consultation_fee=500 if specialty in {"Cardiology", "Neurology", "Gynecology"} else 350,
                bio=bio,
            )

        patient_specs = [
            ("ananya.sharma", "Ananya Sharma", "Female", "1994-02-18", "B+", "Kondapur", "Hyderabad", "9001001001", "ananya.patient@example.test", "Hindi"),
            ("rahul.verma", "Rahul Verma", "Male", "1988-07-09", "O+", "Miyapur", "Hyderabad", "9001001002", "rahul.patient@example.test", "English"),
            ("priya.reddy", "Priya Reddy", "Female", "1991-11-26", "A+", "Manikonda", "Hyderabad", "9001001003", "priya.patient@example.test", "Telugu"),
            ("arjun.kumar", "Arjun Kumar", "Male", "2012-05-14", "A-", "Uppal", "Hyderabad", "9001001004", "arjun.patient@example.test", "English"),
            ("sneha.rao", "Sneha Rao", "Female", "1985-03-30", "AB+", "Begumpet", "Hyderabad", "9001001005", "sneha.patient@example.test", "English"),
            ("kavya.nair", "Kavya Nair", "Female", "1997-09-12", "O-", "Kukatpally", "Hyderabad", "9001001006", "kavya.patient@example.test", "Malayalam"),
            ("vikram.patel", "Vikram Patel", "Male", "1979-12-05", "B+", "LB Nagar", "Hyderabad", "9001001007", "vikram.patient@example.test", "Hindi"),
            ("meera.joshi", "Meera Joshi", "Female", "2001-06-21", "A+", "Nallagandla", "Hyderabad", "9001001008", "meera.patient@example.test", "English"),
        ]
        patients = []
        for index, (username, full_name, gender, dob, blood_group, village, district, phone, email, language) in enumerate(patient_specs, start=1):
            account = self.user(username, email, "PATIENT", *full_name.split(" ", 1))
            patient = Patient.objects.create(
                user=account,
                patient_id=f"DEMO-{today.year}-{index:04d}",
                full_name=full_name,
                dob=date.fromisoformat(dob),
                gender=gender,
                phone=phone,
                email=email,
                address=f"{village}, Hyderabad",
                village=village,
                district=district,
                blood_group=blood_group,
                allergies="No known allergies" if index % 3 else "Penicillin",
                active_conditions="Routine monitoring" if index % 2 else "No active conditions",
                preferred_language=language[:2].lower() if language != "Malayalam" else "en",
            )
            patients.append(patient)

        phc_user = self.user("demo.phc", "phc.demo@example.test", "PHC", "Nandita", "Kiran")
        phc_profile = PHCProfile.objects.create(user=phc_user, facility=phc, centre_id="NIRMALA-PHC-01")
        phc_profile.assigned_patients.add(*patients[:5])
        asha_user = self.user("demo.asha", "asha.demo@example.test", "ASHA", "Lakshmi", "Devi")
        asha_profile = ASHAProfile.objects.create(user=asha_user, worker_id="ASHA-HYD-014", area="Kondapur and Miyapur")
        asha_profile.assigned_patients.add(*patients[:4])

        staff_specs = [
            ("Aditi Menon", "STF-001", "Nurse", "Emergency", "Active", "9002002001"),
            ("Suresh Babu", "STF-002", "Pharmacist", "Pharmacy", "Active", "9002002002"),
            ("Neha Kapoor", "STF-003", "Receptionist", "Front Desk", "Active", "9002002003"),
            ("Imran Shaikh", "STF-004", "Lab Technician", "Diagnostics", "Active", "9002002004"),
            ("Divya Thomas", "STF-005", "Nurse", "Pediatrics", "On Leave", "9002002005"),
            ("Mohan Rao", "STF-006", "Ward Manager", "Inpatient Care", "Active", "9002002006"),
        ]
        for name, staff_id, role, department, status, contact in staff_specs:
            HospitalStaff.objects.create(facility=hospital, name=name, staff_id=staff_id, role=role, department=department, status=status, contact=contact)

        for name, quantity, category in [
            ("Hospital Bed", 40, "basic"),
            ("Wheelchair", 12, "basic"),
            ("ECG Machine", 3, "advanced"),
            ("Patient Monitor", 8, "advanced"),
            ("Oxygen Concentrator", 10, "advanced"),
        ]:
            Equipment.objects.create(facility=hospital, name=name, quantity=quantity, category=category)

        for name, total, occupied in [
            ("General Ward", 24, 16),
            ("ICU", 8, 5),
            ("Pediatrics", 10, 6),
            ("Observation", 6, 2),
        ]:
            BedResource.objects.create(facility=hospital, name=name, total=total, occupied=occupied)

        medicines = [
            ("Paracetamol", "MED-DEMO-001", "Analgesic", 500, "Tablets", 50, 2030, 12, 31),
            ("Amoxicillin", "MED-DEMO-002", "Antibiotic", 180, "Capsules", 30, 2029, 8, 31),
            ("Metformin", "MED-DEMO-003", "Antidiabetic", 240, "Tablets", 40, 2030, 4, 30),
            ("Amlodipine", "MED-DEMO-004", "Cardiology", 120, "Tablets", 25, 2029, 11, 30),
            ("ORS Sachets", "MED-DEMO-005", "Rehydration", 75, "Sachets", 20, 2028, 9, 30),
            ("Ferrous Sulphate", "MED-DEMO-006", "Supplement", 210, "Tablets", 35, 2030, 6, 30),
        ]
        for name, medicine_id, category, quantity, unit, reorder, year, month, day in medicines:
            MedicineStock.objects.create(
                facility=hospital,
                name=name,
                medicine_id=medicine_id,
                category=category,
                unit=unit,
                dosage="As directed",
                quantity=quantity,
                reorder_level=reorder,
                expiry_date=date(year, month, day),
                is_available=quantity > 0,
            )
        for name, medicine_id, category, quantity, unit in [
            ("Paracetamol", "PHC-MED-001", "Analgesic", 90, "Tablets"),
            ("ORS Sachets", "PHC-MED-002", "Rehydration", 45, "Sachets"),
            ("Ferrous Sulphate", "PHC-MED-003", "Supplement", 65, "Tablets"),
        ]:
            MedicineStock.objects.create(
                facility=phc,
                name=name,
                medicine_id=medicine_id,
                category=category,
                unit=unit,
                dosage="As directed",
                quantity=quantity,
                reorder_level=15,
                expiry_date=date(2030, 12, 31),
                is_available=True,
            )

        appointment_specs = [
            (patients[0], doctors[0], -3, "Completed", "Annual wellness review"),
            (patients[1], doctors[1], -2, "Completed", "Blood pressure follow-up"),
            (patients[2], doctors[2], -1, "Completed", "Migraine evaluation"),
            (patients[3], doctors[3], 0, "Scheduled", "Child wellness visit"),
            (patients[4], doctors[4], 0, "Scheduled", "Antenatal consultation"),
            (patients[5], doctors[5], 1, "Scheduled", "Diabetes review"),
            (patients[6], doctors[1], 2, "Scheduled", "Cardiac consultation"),
            (patients[7], doctors[0], 4, "Scheduled", "General consultation"),
            (patients[0], doctors[4], 7, "Scheduled", "Preventive health review"),
            (patients[1], doctors[2], -7, "Cancelled", "Neurology consultation"),
        ]
        appointments = []
        for index, (patient, doctor, day_offset, status, reason) in enumerate(appointment_specs, start=1):
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                doctor_name=doctor.get_full_name() or doctor.username,
                facility=doctor.doctor_profile.facility,
                appointment_time=now + timedelta(days=day_offset, hours=(9 + index % 7) - now.hour),
                reason=reason,
                queue_number=f"Q-{index:03d}",
                patients_ahead=max(0, 4 - index),
                status=status,
            )
            appointments.append(appointment)

        consultations = []
        consultation_specs = [
            (patients[0], doctors[0], appointments[0], "Completed", "Routine wellness review", "Stable vitals; continue preventive care.", "Hydration and balanced diet."),
            (patients[1], doctors[1], appointments[1], "Completed", "Elevated blood pressure", "Mild hypertension under monitoring.", "Continue prescribed cardiac medication."),
            (patients[2], doctors[2], appointments[2], "Completed", "Recurrent migraine", "Migraine without acute neurological deficit.", "Maintain symptom diary and hydration."),
            (patients[3], doctors[3], appointments[3], "In Progress", "Routine pediatric review", "Growth monitoring in progress.", "Age-appropriate nutrition advice."),
        ]
        for patient, doctor, appointment, status, symptoms, diagnosis, treatment in consultation_specs:
            consultation = Consultation.objects.create(
                patient=patient,
                doctor=doctor,
                appointment=appointment,
                facility=doctor.doctor_profile.facility,
                status=status,
                symptoms=symptoms,
                diagnosis=diagnosis,
                treatment=treatment,
                prescription="Follow the clinician's instructions; review in 4 weeks.",
                notes="Fictional demonstration record.",
                started_at=now - timedelta(days=2),
                completed_at=now - timedelta(days=1) if status == "Completed" else None,
            )
            consultations.append(consultation)
            HealthTimelineRecord.objects.create(
                patient=patient,
                record_type="CONSULTATION",
                title="Specialist consultation",
                status="Completed" if status == "Completed" else "Upcoming",
                event_date=today + timedelta(days=-abs(appointment.appointment_time.date().toordinal() - today.toordinal()) if appointment.appointment_time.date() < today else 0),
                facility_name=doctor.doctor_profile.facility.name,
                doctor_name=doctor.get_full_name(),
                health_issue=symptoms,
                diagnosis=diagnosis,
                prescription=consultation.prescription,
            )

        for patient, title, test_name, result, event_offset in [
            (patients[0], "Routine blood panel", "Complete Blood Count", "Within reference range", -12),
            (patients[1], "Lipid profile", "Lipid Profile", "LDL mildly elevated", -9),
            (patients[4], "Antenatal screening", "Hemoglobin", "11.8 g/dL", -5),
            (patients[6], "Cardiac screening", "ECG", "Normal sinus rhythm", -4),
        ]:
            HealthTimelineRecord.objects.create(
                patient=patient,
                record_type="LAB_TEST",
                title=title,
                status="Available",
                event_date=today + timedelta(days=event_offset),
                facility_name=hospital.name,
                test_name=test_name,
                test_result=result,
                health_issue="Routine screening",
                risk_level="Low",
            )

        referral_specs = [
            (patients[1], doctors[0], doctors[1], phc, hospital, "Persistent elevated blood pressure requires cardiology review.", "Pending"),
            (patients[2], doctors[0], doctors[2], phc, hospital, "Recurrent headaches require neurology consultation.", "Accepted"),
            (patients[4], doctors[0], doctors[4], phc, hospital, "Antenatal review and specialist guidance.", "Pending"),
            (patients[6], doctors[1], doctors[2], hospital, hospital, "Neurological review for intermittent dizziness.", "Completed"),
            (patients[3], None, doctors[3], phc, hospital, "Pediatric growth monitoring referral.", "Pending"),
        ]
        referrals = []
        for patient, referring_doctor, receiving_doctor, referring_facility, receiving_facility, reason, status in referral_specs:
            referral = Referral.objects.create(
                patient=patient,
                referring_doctor=referring_doctor,
                referring_phc=phc_user if referring_doctor is None else None,
                receiving_doctor=receiving_doctor,
                referring_facility=referring_facility,
                receiving_facility=receiving_facility,
                reason=reason,
                status=status,
                notes="Fictional demo referral for portal workflow testing.",
            )
            referrals.append(referral)
            HealthTimelineRecord.objects.create(
                patient=patient,
                record_type="REFERRAL",
                title="Specialist referral",
                status="Pending" if status == "Pending" else "Completed",
                event_date=today - timedelta(days=2),
                facility_name=referring_facility.name,
                doctor_name=referring_doctor.get_full_name() if referring_doctor else phc_user.get_full_name(),
                referral_source=referring_facility.name,
                referral_target=receiving_facility.name,
                referral_reason=reason,
                risk_level="Medium",
            )

        for patient, doctor, consultation, referral, offset, purpose in [
            (patients[0], doctors[0], consultations[0], None, 14, "Review wellness goals"),
            (patients[1], doctors[1], consultations[1], referrals[0], 10, "Review blood pressure log"),
            (patients[2], doctors[2], consultations[2], referrals[1], 21, "Review headache diary"),
            (patients[4], doctors[4], None, referrals[2], 18, "Antenatal follow-up"),
        ]:
            followup = FollowUp.objects.create(
                patient=patient,
                doctor=doctor,
                consultation=consultation,
                referral=referral,
                scheduled_for=now + timedelta(days=offset),
                purpose=purpose,
                status="Scheduled",
                notes="Fictional demo follow-up.",
            )
            HealthTimelineRecord.objects.create(
                patient=patient,
                record_type="FOLLOW_UP",
                title="Scheduled follow-up",
                status="Upcoming",
                event_date=followup.scheduled_for.date(),
                facility_name=doctor.doctor_profile.facility.name,
                doctor_name=doctor.get_full_name(),
                followup_purpose=purpose,
            )

        for patient, symptom, priority, status in [
            (patients[0], "Occasional fatigue", "LOW", "RESOLVED"),
            (patients[1], "Headache and high readings", "MEDIUM", "REVIEWED"),
            (patients[4], "Pregnancy wellness check", "LOW", "NEW"),
            (patients[6], "Intermittent dizziness", "MEDIUM", "REVIEWED"),
            (patients[3], "Mild seasonal fever", "MEDIUM", "NEW"),
        ]:
            DigitalTriageAssessment.objects.create(
                patient=patient,
                main_symptom=symptom,
                duration="3 days",
                additional_symptoms=["Tiredness"],
                follow_up_answers=["No emergency warning signs"],
                priority=priority,
                recommendation="Routine clinical review is advised; seek urgent care if symptoms worsen.",
                status=status,
                source="patient_portal",
            )

        for action, target in [
            ("PATIENT_CREATED", patients[0]),
            ("PATIENT_CREATED", patients[1]),
            ("DOCTOR_CREATED", doctors[0]),
            ("DOCTOR_CREATED", doctors[1]),
            ("HOSPITAL_ADMIN_CREATED", hospital_admin),
            ("PATIENT_VIEWED", patients[2]),
            ("PATIENT_VIEWED", patients[4]),
        ]:
            AuditLog.objects.create(user=system_admin, action=action, target_type=target.__class__.__name__, target_id=str(target.pk), metadata={"source": "demo_seed"})

        return {
            "patients": Patient.objects.count(),
            "doctors": DoctorProfile.objects.count(),
            "facilities": Facility.objects.count(),
            "appointments": Appointment.objects.count(),
            "consultations": Consultation.objects.count(),
            "referrals": Referral.objects.count(),
            "follow_ups": FollowUp.objects.count(),
            "triage_assessments": DigitalTriageAssessment.objects.count(),
            "health_records": HealthTimelineRecord.objects.count(),
            "staff": HospitalStaff.objects.count(),
            "equipment": Equipment.objects.count(),
            "beds": BedResource.objects.count(),
            "medicines": MedicineStock.objects.count(),
        }
