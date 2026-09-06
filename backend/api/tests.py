from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import AuditLog, Appointment, Consultation, FollowUp, Patient, Referral


User = get_user_model()


class HealthcareSecurityTests(TestCase):
	def setUp(self):
		cache.clear()
		self.client = APIClient()
		self.patient_user = User.objects.create_user(
			username='patient-one', password='StrongPass123!', role='PATIENT'
		)
		self.other_user = User.objects.create_user(
			username='patient-two', password='StrongPass123!', role='PATIENT'
		)
		self.doctor = User.objects.create_user(
			username='doctor-one', password='StrongPass123!', role='DOCTOR'
		)
		self.admin = User.objects.create_user(
			username='admin-one', password='StrongPass123!', role='ADMIN'
		)
		self.patient = Patient.objects.create(
			user=self.patient_user,
			patient_id='AC-2026-1001',
			full_name='Patient One',
			phone='9000000001',
			village='Village One',
			district='District One',
		)
		self.other_patient = Patient.objects.create(
			user=self.other_user,
			patient_id='AC-2026-1002',
			full_name='Patient Two',
			phone='9000000002',
			village='Village Two',
			district='District Two',
		)

	def test_unauthenticated_user_cannot_access_patient_api(self):
		response = self.client.get(f'/api/v1/patient/{self.patient.patient_id}/records')
		self.assertIn(response.status_code, (401, 403))

	def test_patient_can_access_own_record(self):
		self.client.force_authenticate(self.patient_user)
		response = self.client.get(f'/api/v1/patient/{self.patient.patient_id}/records')
		self.assertEqual(response.status_code, 200)

	def test_api_login_creates_session_for_protected_api(self):
		response = self.client.post('/api/v1/auth/login', {
			'identifier': 'patient-one',
			'password': 'StrongPass123!',
		}, format='json')
		self.assertEqual(response.status_code, 200)
		self.assertIn('sessionid', response.cookies)
		records_response = self.client.get(f'/api/v1/patient/{self.patient.patient_id}/records')
		self.assertEqual(records_response.status_code, 200)

	def test_patient_cannot_access_another_patient_record(self):
		self.client.force_authenticate(self.patient_user)
		response = self.client.get(f'/api/v1/patient/{self.other_patient.patient_id}/records')
		self.assertEqual(response.status_code, 403)
		self.assertTrue(AuditLog.objects.filter(action='UNAUTHORIZED_ACCESS', success=False).exists())

	def test_doctor_cannot_create_doctor_account(self):
		self.client.force_login(self.doctor)
		response = self.client.post('/admin/create-doctor/', {
			'username': 'new-doctor',
			'email': 'new-doctor@example.com',
			'password': 'StrongPass123!',
		})
		self.assertEqual(response.status_code, 403)
		self.assertTrue(AuditLog.objects.filter(action='PERMISSION_DENIED', success=False).exists())

	def test_doctor_cannot_read_unassigned_patient_record(self):
		self.client.force_authenticate(self.doctor)
		response = self.client.get(f'/api/v1/patient/{self.patient.patient_id}/records')
		self.assertEqual(response.status_code, 403)

	def test_patient_cannot_modify_records(self):
		self.client.force_authenticate(self.patient_user)
		response = self.client.post(f'/api/v1/patient/{self.patient.patient_id}/records', {})
		self.assertEqual(response.status_code, 405)

	def test_admin_can_access_patient_dashboard(self):
		self.client.force_authenticate(self.admin)
		response = self.client.get(f'/api/v1/patient/{self.patient.patient_id}/dashboard')
		self.assertEqual(response.status_code, 200)

	def test_admin_can_create_doctor_account(self):
		self.client.force_login(self.admin)
		response = self.client.post('/admin/create-doctor/', {
			'username': 'new-doctor',
			'email': 'new-doctor@example.com',
			'password': 'StrongPass123!',
		})
		self.assertEqual(response.status_code, 302)
		self.assertTrue(User.objects.filter(username='new-doctor', role='DOCTOR').exists())
		self.assertTrue(AuditLog.objects.filter(action='DOCTOR_CREATED', user=self.admin).exists())

	def test_failed_login_attempts_are_throttled(self):
		for _ in range(5):
			response = self.client.post('/patient/login/', {
				'username': 'patient-one',
				'password': 'wrong-password',
			})
			self.assertEqual(response.status_code, 401)
		response = self.client.post('/patient/login/', {
			'username': 'patient-one',
			'password': 'wrong-password',
		})
		self.assertEqual(response.status_code, 429)

	@override_settings(SESSION_COOKIE_SECURE=True)
	def test_successful_login_creates_secure_session(self):
		response = self.client.post('/patient/login/', {
			'username': 'patient-one',
			'password': 'StrongPass123!',
		})
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.cookies['sessionid']['secure'])
		self.assertTrue(response.cookies['sessionid']['httponly'])
		self.assertTrue(AuditLog.objects.filter(action='LOGIN_SUCCESS', user=self.patient_user).exists())

	def test_login_failure_is_audited(self):
		self.client.post('/patient/login/', {'username': 'patient-one', 'password': 'wrong-password'})
		self.assertTrue(AuditLog.objects.filter(action='LOGIN_FAILURE', success=False).exists())

	def test_logout_is_post_only_and_audited(self):
		self.client.force_login(self.patient_user)
		self.assertEqual(self.client.get('/logout/').status_code, 405)
		response = self.client.post('/logout/')
		self.assertEqual(response.status_code, 200)
		self.assertTrue(AuditLog.objects.filter(action='LOGOUT', user=self.patient_user).exists())

	def test_csrf_protects_web_login(self):
		csrf_client = APIClient(enforce_csrf_checks=True)
		response = csrf_client.post('/patient/login/', {
			'username': 'patient-one',
			'password': 'StrongPass123!',
		})
		self.assertEqual(response.status_code, 403)

	def test_patient_signup_creates_linked_profile(self):
		response = self.client.post('/patient/signup/', {
			'username': 'new-patient',
			'email': 'new-patient@example.com',
			'password': 'StrongPass123!',
			'full_name': 'New Patient',
			'phone': '9000000003',
			'village': 'Village Three',
			'district': 'District Three',
		})
		self.assertEqual(response.status_code, 302)
		new_user = User.objects.get(username='new-patient')
		self.assertTrue(Patient.objects.filter(user=new_user, full_name='New Patient').exists())

	def test_patient_portal_requires_authenticated_patient(self):
		self.assertEqual(self.client.get('/patient_portal.html').status_code, 302)
		self.client.force_login(self.patient_user)
		response = self.client.get('/patient_portal.html')
		self.assertEqual(response.status_code, 200)

	def test_patient_can_create_and_read_appointment(self):
		self.client.force_authenticate(self.patient_user)
		response = self.client.post('/api/v1/appointments', {
			'patient_id': self.patient.patient_id,
			'doctor_id': self.doctor.id,
			'appointment_time': '2026-09-10T10:30:00Z',
		}, format='json')
		self.assertEqual(response.status_code, 201)
		self.assertTrue(Appointment.objects.filter(patient=self.patient, doctor=self.doctor).exists())
		self.assertEqual(self.client.get('/api/v1/appointments').status_code, 200)

	def test_doctor_can_create_consultation_and_followup(self):
		self.client.force_authenticate(self.doctor)
		Appointment.objects.create(
			patient=self.patient,
			doctor=self.doctor,
			doctor_name=self.doctor.username,
			appointment_time='2026-09-10T10:30:00Z',
		)
		response = self.client.post('/api/v1/consultations', {
			'patient_id': self.patient.patient_id,
			'symptoms': 'Fever',
			'diagnosis': 'Viral infection',
			'status': 'Completed',
		}, format='json')
		self.assertEqual(response.status_code, 201)
		consultation = Consultation.objects.get(patient=self.patient, doctor=self.doctor)
		followup_response = self.client.post('/api/v1/follow-ups', {
			'patient_id': self.patient.patient_id,
			'consultation_id': consultation.id,
			'scheduled_for': '2026-09-20T10:30:00Z',
			'purpose': 'Review response to treatment',
		}, format='json')
		self.assertEqual(followup_response.status_code, 201)
		self.assertTrue(FollowUp.objects.filter(consultation=consultation).exists())

	def test_doctor_can_create_and_update_referral(self):
		self.client.force_authenticate(self.doctor)
		Appointment.objects.create(
			patient=self.patient,
			doctor=self.doctor,
			doctor_name=self.doctor.username,
			appointment_time='2026-09-10T10:30:00Z',
		)
		response = self.client.post('/api/v1/referrals', {
			'patient_id': self.patient.patient_id,
			'reason': 'Specialist review required',
		}, format='json')
		self.assertEqual(response.status_code, 201)
		referral = Referral.objects.get(patient=self.patient, referring_doctor=self.doctor)
		update = self.client.patch(f'/api/v1/referrals/{referral.id}', {'status': 'Accepted'}, format='json')
		self.assertEqual(update.status_code, 200)
		referral.refresh_from_db()
		self.assertEqual(referral.status, 'Accepted')

# Create your tests here.
