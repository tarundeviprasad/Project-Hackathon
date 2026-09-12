from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import ASHAProfile, AuditLog, Appointment, Consultation, DoctorProfile, Facility, FollowUp, HospitalAdminProfile, Patient, PHCProfile, Referral


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

	def test_patient_can_submit_digital_triage_assessment(self):
		self.client.force_authenticate(self.patient_user)
		response = self.client.post('/api/v1/patient/me/triage', {
			'main_symptom': 'chest pain',
			'duration': '1–2 days',
			'additional_symptoms': ['dizziness', 'shortness of breath'],
			'follow_up_answers': ['palpitations', 'worse with activity'],
		}, format='json')
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['priority'], 'EMERGENCY')
		self.assertEqual(response.data['patient']['patient_id'], self.patient.patient_id)
		self.assertTrue(response.data['id'])

	def test_logged_in_patient_without_profile_can_book_appointment_using_authenticated_user(self):
		legacy_patient = User.objects.create_user(
			username='legacy-patient',
			email='legacy.patient@example.com',
			password='StrongPass123!',
			role='PATIENT',
		)
		self.client.force_authenticate(legacy_patient)
		response = self.client.post('/api/v1/appointments', {
			'doctor_id': self.doctor.id,
			'doctor_name': 'doctor-one',
			'appointment_time': '2026-09-15T10:30:00Z',
			'reason': 'headache',
		}, format='json')
		self.assertEqual(response.status_code, 201)
		patient = Patient.objects.get(user=legacy_patient)
		self.assertEqual(response.data['patient'], patient.id)
		self.assertTrue(Appointment.objects.filter(patient__user=legacy_patient).exists())
		self.assertEqual(patient.patient_id, Patient.objects.get(pk=response.data['patient']).patient_id)

	def test_doctor_api_uses_real_name_from_database_for_doctor_and_phc_facility(self):
		facility = Facility.objects.create(name='AarogyaConnect Primary Facility', facility_type='PHC')
		doctor = User.objects.create_user(
			username='rajesh.kumar',
			email='rajesh.kumar@example.com',
			password='StrongPass123!',
			first_name='Rajesh',
			last_name='Kumar',
			role='DOCTOR',
		)
		DoctorProfile.objects.create(user=doctor, facility=facility, specialty='General Physician', experience_years=8)
		response = self.client.get('/api/v1/doctors')
		self.assertEqual(response.status_code, 200)
		payload = next(item for item in response.data if item['user'] == doctor.id)
		self.assertEqual(payload['name'], 'Rajesh Kumar')
		self.assertEqual(payload['facility_name'], 'AarogyaConnect Primary Facility')
		self.assertEqual(payload['specialty'], 'General Physician')

	def test_patient_search_only_returns_matching_owned_patient(self):
		self.client.force_authenticate(self.patient_user)
		response = self.client.get('/api/v1/patients?search=Patient%20One')
		self.assertEqual(response.status_code, 200)
		self.assertEqual([item['patient_id'] for item in response.data], [self.patient.patient_id])

	def test_asha_login_redirects_to_asha_dashboard_and_is_not_doctor(self):
		asha = User.objects.create_user(username='asha-test', password='StrongPass123!', role='ASHA')
		response = self.client.post('/asha/login/', {'username': 'asha-test', 'password': 'StrongPass123!'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['redirect'], '/asha/dashboard/')
		self.client.force_login(asha)
		self.assertEqual(self.client.get('/asha/dashboard/').status_code, 200)
		self.assertEqual(self.client.get('/doctor-dashboard.html').status_code, 403)

	def test_asha_dashboard_returns_database_backed_empty_state(self):
		asha = User.objects.create_user(
			username='asha-dashboard', email='asha-dashboard@example.com',
			password='StrongPass123!', first_name='Asha Worker', role='ASHA',
		)
		ASHAProfile.objects.create(user=asha, worker_id='ASHA-TEST-001')
		self.client.force_login(asha)
		response = self.client.get('/api/v1/asha/me/dashboard')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['worker']['name'], 'Asha Worker')
		self.assertEqual(response.data['stats']['patients_registered'], 0)
		self.assertEqual(response.data['patients'], [])

	def test_non_asha_cannot_read_asha_dashboard_api(self):
		self.client.force_authenticate(self.patient_user)
		response = self.client.get('/api/v1/asha/me/dashboard')
		self.assertEqual(response.status_code, 403)

	def test_asha_patient_registration_assigns_patient_to_worker(self):
		asha = User.objects.create_user(username='asha-register', password='StrongPass123!', role='ASHA')
		profile = ASHAProfile.objects.create(user=asha, worker_id='ASHA-TEST-002')
		self.client.force_authenticate(asha)
		response = self.client.post('/api/v1/auth/register', {
			'full_name': 'Assigned Patient', 'phone': '9000000099',
			'village': 'Village', 'district': 'District',
		}, format='json')
		self.assertEqual(response.status_code, 201)
		self.assertTrue(profile.assigned_patients.filter(full_name='Assigned Patient').exists())

	def test_common_login_routes_phc_to_protected_phc_dashboard(self):
		phc = User.objects.create_user(username='phc-test', password='StrongPass123!', role='PHC')
		facility = Facility.objects.create(name='Test PHC', facility_type='PHC')
		PHCProfile.objects.create(user=phc, facility=facility, centre_id='PHC-TEST-001')
		response = self.client.post('/doctor/login/', {'username': 'phc-test', 'password': 'StrongPass123!'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['redirect'], '/phc/dashboard/')
		self.assertEqual(self.client.get('/phc/dashboard/').status_code, 200)
		self.assertEqual(self.client.get('/doctor-dashboard.html').status_code, 403)

	def test_phc_dashboard_api_returns_empty_database_state(self):
		phc = User.objects.create_user(username='phc-empty', password='StrongPass123!', role='PHC')
		facility = Facility.objects.create(name='Empty PHC', facility_type='PHC')
		PHCProfile.objects.create(user=phc, facility=facility, centre_id='PHC-EMPTY-001')
		self.client.force_login(phc)
		response = self.client.get('/api/v1/phc/me/dashboard')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['stats']['appointments'], 0)
		self.assertEqual(response.data['appointments'], [])

	def test_phc_dashboard_without_profile_returns_empty_safe_payload(self):
		phc = User.objects.create_user(username='phc-no-profile', password='StrongPass123!', role='PHC', first_name='PHC Worker')
		self.client.force_login(phc)
		response = self.client.get('/api/v1/phc/me/dashboard')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['stats']['patients'], 0)
		self.assertEqual(response.data['patients'], [])
		self.assertEqual(response.data['phc']['name'], 'PHC Centre')

	def test_phc_referral_is_visible_to_assigned_doctor_and_status_is_shared(self):
		phc = User.objects.create_user(username='phc-referrals', password='StrongPass123!', role='PHC')
		facility = Facility.objects.create(name='Referral PHC', facility_type='PHC')
		profile = PHCProfile.objects.create(user=phc, facility=facility, centre_id='PHC-TEST-002')
		profile.assigned_patients.add(self.patient)
		self.client.force_authenticate(phc)
		created = self.client.post('/api/v1/referrals', {
			'patient_id': self.patient.patient_id,
			'receiving_doctor_id': self.doctor.id,
			'receiving_facility_id': facility.id,
			'reason': 'Specialist review required',
		}, format='json')
		self.assertEqual(created.status_code, 201)
		referral_id = created.data['id']
		self.client.force_authenticate(self.doctor)
		self.assertTrue(any(item['id'] == referral_id for item in self.client.get('/api/v1/referrals').data))
		updated = self.client.patch(f'/api/v1/referrals/{referral_id}', {'status': 'Accepted'}, format='json')
		self.assertEqual(updated.status_code, 200)
		self.client.force_authenticate(phc)
		self.assertEqual(self.client.get(f'/api/v1/referrals/{referral_id}').data['status'], 'Accepted')

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

	def test_admin_can_create_hospital_admin_with_hashed_password(self):
		self.client.force_authenticate(self.admin)
		response = self.client.post('/api/v1/admin/hospital-admins', {
			'hospital_name': 'CityCare Hospital',
			'admin_name': 'Anita Rao',
			'username': 'citycare-admin',
			'email': 'anita@citycare.example',
			'phone': '9000000010',
			'address': 'Hyderabad',
			'password': 'StrongPass123!',
			'password_confirm': 'StrongPass123!',
		}, format='json')
		self.assertEqual(response.status_code, 201)
		user = User.objects.get(username='citycare-admin')
		self.assertEqual(user.role, 'HOSPITAL_ADMIN')
		self.assertTrue(user.check_password('StrongPass123!'))
		self.assertNotEqual(user.password, 'StrongPass123!')
		self.assertTrue(HospitalAdminProfile.objects.filter(user=user, admin_name='Anita Rao').exists())

	def test_hospital_admin_creation_rejects_duplicates_and_mismatched_passwords(self):
		self.client.force_authenticate(self.admin)
		payload = {
			'hospital_name': 'CityCare Hospital', 'admin_name': 'Anita Rao',
			'username': 'citycare-admin', 'email': 'anita@citycare.example',
			'phone': '9000000010', 'password': 'StrongPass123!',
			'password_confirm': 'StrongPass123!',
		}
		self.assertEqual(self.client.post('/api/v1/admin/hospital-admins', payload, format='json').status_code, 201)
		payload['email'] = 'another@citycare.example'
		payload['password_confirm'] = 'different-password'
		response = self.client.post('/api/v1/admin/hospital-admins', payload, format='json')
		self.assertEqual(response.status_code, 400)
		self.assertIn('username', response.data['errors'])
		self.assertIn('password_confirm', response.data['errors'])

	def test_hospital_admin_can_login_but_cannot_access_system_admin(self):
		user = User.objects.create_user(
			username='hospital-admin', email='hospital@example.com',
			password='StrongPass123!', role='HOSPITAL_ADMIN',
		)
		self.client.force_login(user)
		self.assertEqual(self.client.get('/System Admin Dashboard.html').status_code, 403)
		self.client.logout()
		response = self.client.post('/admin/login/', {
			'username': 'hospital-admin', 'password': 'StrongPass123!',
		})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['redirect'], '/hospital/dashboard/')

	def test_hospital_admin_dashboard_is_database_backed_and_role_protected(self):
		facility = Facility.objects.create(name='Dashboard Hospital', facility_type='Hospital')
		hospital_admin = User.objects.create_user(
			username='dashboard-hospital-admin', password='StrongPass123!', role='HOSPITAL_ADMIN'
		)
		HospitalAdminProfile.objects.create(
			user=hospital_admin, facility=facility, admin_name='Dashboard Admin', phone='9000000099'
		)
		self.client.force_login(hospital_admin)
		response = self.client.get('/api/v1/hospital/me/dashboard')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['hospital']['name'], 'Dashboard Hospital')
		self.assertEqual(response.data['stats']['patients'], 0)
		self.client.force_authenticate(self.patient_user)
		self.assertEqual(self.client.get('/api/v1/hospital/me/dashboard').status_code, 403)

	def test_hospital_admin_login_page_is_public_and_dashboard_redirects_to_it(self):
		login_page = self.client.get('/hospital-admin/login/')
		self.assertEqual(login_page.status_code, 200)
		self.assertContains(login_page, 'Hospital Login ID')
		response = self.client.get('/hospital admin.html')
		self.assertEqual(response.status_code, 302)
		self.assertTrue(response.url.startswith('/hospital-admin/login/'))

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

	def test_patient_dashboard_nav_has_correct_modules_and_no_referrals(self):
		self.client.force_login(self.patient_user)
		response = self.client.get('/patient_portal.html')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Appointments')
		self.assertContains(response, 'Health Records')
		self.assertContains(response, 'Medicines')
		self.assertContains(response, 'Digital Triage')
		self.assertNotContains(response, 'Referrals')
		self.assertContains(response, '/booking_an_appointment.html')
		self.assertContains(response, '/digital_health_record.html')
		self.assertContains(response, '/teleconsultation.html')
		self.assertContains(response, 'http://127.0.0.1:8001/')

	def test_patient_teleconsultation_page_is_served(self):
		self.client.force_login(self.patient_user)
		response = self.client.get('/teleconsultation.html')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Teleconsultation')

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

	def test_patient_can_book_appointment_with_reason_and_duplicate_check(self):
		self.client.force_authenticate(self.patient_user)
		payload = {
			'doctor_id': self.doctor.id,
			'appointment_time': '2026-09-10T10:30:00Z',
			'reason': 'Follow-up for recurring fever',
		}
		response = self.client.post('/api/v1/appointments', payload, format='json')
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['reason'], 'Follow-up for recurring fever')
		self.assertTrue(Appointment.objects.filter(patient=self.patient, doctor=self.doctor, reason='Follow-up for recurring fever').exists())

		duplicate = self.client.post('/api/v1/appointments', payload, format='json')
		self.assertEqual(duplicate.status_code, 409)
		self.assertIn('already exists', str(duplicate.data['error']).lower())

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
