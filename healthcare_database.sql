CREATE DATABASE IF NOT EXISTS healthcare_db;

USE healthcare_db;

CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    phone VARCHAR(20),
    address VARCHAR(255),
    village VARCHAR(100),
    district VARCHAR(100)
);

CREATE TABLE health_facilities (
    facility_id INT AUTO_INCREMENT PRIMARY KEY,
    facility_name VARCHAR(150) NOT NULL,
    facility_type VARCHAR(100),
    address VARCHAR(255),
    village VARCHAR(100),
    district VARCHAR(100),
    contact VARCHAR(20)
);

CREATE TABLE medicines (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(150) NOT NULL,
    medicine_type VARCHAR(100),
    dosage_form VARCHAR(100)
);

CREATE TABLE doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    phone VARCHAR(20),
    facility_id INT,
    availability_status VARCHAR(50),
    FOREIGN KEY (facility_id)
        REFERENCES health_facilities(facility_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE health_issues (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    symptoms VARCHAR(500),
    description TEXT,
    severity VARCHAR(50),
    reported_date DATE,
    triage_level VARCHAR(50),
    emergency_flag BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    facility_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    appointment_type VARCHAR(100),
    queue_number INT,
    status VARCHAR(50),
    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)
        REFERENCES doctors(doctor_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (facility_id)
        REFERENCES health_facilities(facility_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE consultations (
    consultation_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    issue_id INT,
    consultation_date DATETIME NOT NULL,
    notes TEXT,
    FOREIGN KEY (appointment_id)
        REFERENCES appointments(appointment_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)
        REFERENCES doctors(doctor_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (issue_id)
        REFERENCES health_issues(issue_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE diagnoses (
    diagnosis_id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id INT NOT NULL,
    diagnosis_name VARCHAR(150) NOT NULL,
    diagnosis_details TEXT,
    FOREIGN KEY (consultation_id)
        REFERENCES consultations(consultation_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE facility_medicines (
    facility_medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    facility_id INT NOT NULL,
    medicine_id INT NOT NULL,
    quantity INT DEFAULT 0,
    availability_status VARCHAR(50),
    FOREIGN KEY (facility_id)
        REFERENCES health_facilities(facility_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (medicine_id)
        REFERENCES medicines(medicine_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id INT NOT NULL,
    medicine_id INT NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    duration VARCHAR(100),
    FOREIGN KEY (consultation_id)
        REFERENCES consultations(consultation_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (medicine_id)
        REFERENCES medicines(medicine_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE lab_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    consultation_id INT,
    facility_id INT,
    test_name VARCHAR(150) NOT NULL,
    test_date DATE,
    result TEXT,
    report_status VARCHAR(50),
    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (consultation_id)
        REFERENCES consultations(consultation_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    FOREIGN KEY (facility_id)
        REFERENCES health_facilities(facility_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE referrals (
    referral_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    from_facility_id INT,
    to_facility_id INT,
    doctor_id INT,
    reason TEXT,
    referral_date DATE,
    status VARCHAR(50),
    completion_date DATE,
    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (from_facility_id)
        REFERENCES health_facilities(facility_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    FOREIGN KEY (to_facility_id)
        REFERENCES health_facilities(facility_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    FOREIGN KEY (doctor_id)
        REFERENCES doctors(doctor_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE follow_ups (
    follow_up_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    consultation_id INT,
    follow_up_date DATE,
    risk_level VARCHAR(50),
    status VARCHAR(50),
    notes TEXT,
    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (consultation_id)
        REFERENCES consultations(consultation_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE teleconsultations (
    teleconsultation_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_id INT,
    start_time DATETIME,
    end_time DATETIME,
    status VARCHAR(50),
    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)
        REFERENCES doctors(doctor_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (appointment_id)
        REFERENCES appointments(appointment_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);