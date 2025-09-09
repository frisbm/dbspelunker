BEGIN;

-- Drop existing schema if it exists
DROP SCHEMA IF EXISTS healthcare CASCADE;
CREATE SCHEMA healthcare;
SET search_path TO healthcare;

-- Create tables
CREATE TABLE patient (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F', 'O')),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    insurance_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE organization (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('hospital', 'clinic', 'lab', 'pharmacy', 'insurance')),
    address TEXT,
    phone VARCHAR(20),
    website VARCHAR(100),
    tax_id VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE provider (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    provider_type VARCHAR(20) CHECK (provider_type IN ('practitioner', 'facility')),
    specialty VARCHAR(50),
    npi VARCHAR(10) UNIQUE,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE provider_organization (
    provider_id INTEGER REFERENCES provider(id) ON DELETE CASCADE,
    organization_id INTEGER REFERENCES organization(id) ON DELETE CASCADE,
    role VARCHAR(50),
    start_date DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (provider_id, organization_id)
);

CREATE TABLE encounter (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patient(id) ON DELETE CASCADE,
    provider_id INTEGER NOT NULL REFERENCES provider(id) ON DELETE RESTRICT,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE RESTRICT,
    encounter_date DATE NOT NULL DEFAULT CURRENT_DATE,
    encounter_type VARCHAR(50) CHECK (encounter_type IN ('inpatient', 'outpatient', 'emergency', 'preventive')),
    status VARCHAR(20) CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE claim_line (
    id SERIAL PRIMARY KEY,
    encounter_id INTEGER NOT NULL REFERENCES encounter(id) ON DELETE CASCADE,
    procedure_code VARCHAR(10) NOT NULL,
    procedure_description TEXT NOT NULL,
    charge_amount DECIMAL(10,2) NOT NULL CHECK (charge_amount >= 0),
    service_date DATE NOT NULL,
    modifier VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_patient_last_name ON patient(last_name);
CREATE INDEX idx_patient_dob ON patient(date_of_birth);
CREATE INDEX idx_provider_specialty ON provider(specialty);
CREATE INDEX idx_encounter_date ON encounter(encounter_date);
CREATE INDEX idx_encounter_patient ON encounter(patient_id);
CREATE INDEX idx_encounter_provider ON encounter(provider_id);
CREATE INDEX idx_claim_line_encounter ON claim_line(encounter_id);
CREATE INDEX idx_claim_line_code ON claim_line(procedure_code);

-- Create audit triggers
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER patient_update_timestamp
    BEFORE UPDATE ON patient
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER provider_update_timestamp
    BEFORE UPDATE ON provider
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER organization_update_timestamp
    BEFORE UPDATE ON organization
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Create stored procedures
CREATE OR REPLACE FUNCTION get_patient_summary(p_patient_id INTEGER)
RETURNS TABLE (
    patient_name TEXT,
    patient_dob DATE,
    total_encounters INTEGER,
    last_encounter_date DATE,
    total_charges DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CONCAT(p.first_name, ' ', p.last_name)::TEXT,
        p.date_of_birth,
        COUNT(e.id)::INTEGER,
        MAX(e.encounter_date),
        COALESCE(SUM(cl.charge_amount), 0)::DECIMAL
    FROM patient p
    LEFT JOIN encounter e ON p.id = e.patient_id
    LEFT JOIN claim_line cl ON e.id = cl.encounter_id
    WHERE p.id = p_patient_id
    GROUP BY p.id, p.first_name, p.last_name, p.date_of_birth;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_provider_statistics(p_provider_id INTEGER)
RETURNS TABLE (
    provider_name TEXT,
    specialty TEXT,
    total_encounters INTEGER,
    total_revenue DECIMAL,
    avg_charge_per_encounter DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pr.name::TEXT,
        pr.specialty::TEXT,
        COUNT(DISTINCT e.id)::INTEGER,
        COALESCE(SUM(cl.charge_amount), 0)::DECIMAL,
        CASE 
            WHEN COUNT(DISTINCT e.id) > 0 
            THEN COALESCE(SUM(cl.charge_amount), 0) / COUNT(DISTINCT e.id)
            ELSE 0
        END::DECIMAL
    FROM provider pr
    LEFT JOIN encounter e ON pr.id = e.provider_id
    LEFT JOIN claim_line cl ON e.id = cl.encounter_id
    WHERE pr.id = p_provider_id
    GROUP BY pr.id, pr.name, pr.specialty;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data
-- Organizations
INSERT INTO organization (name, type, address, phone, website, tax_id) VALUES
('City General Hospital', 'hospital', '123 Main St, City, State 12345', '555-0100', 'www.citygeneral.com', '12-3456789'),
('Downtown Medical Clinic', 'clinic', '456 Oak Ave, City, State 12345', '555-0200', 'www.downtownmed.com', '23-4567890'),
('QuickLab Diagnostics', 'lab', '789 Pine St, City, State 12345', '555-0300', 'www.quicklab.com', '34-5678901'),
('Corner Pharmacy', 'pharmacy', '321 Elm St, City, State 12345', '555-0400', 'www.cornerpharm.com', '45-6789012'),
('HealthFirst Insurance', 'insurance', '654 Maple Dr, City, State 12345', '555-0500', 'www.healthfirst.com', '56-7890123'),
('Westside Family Practice', 'clinic', '987 Cedar Ln, City, State 12345', '555-0600', 'www.westsideFamily.com', '67-8901234'),
('Emergency Care Center', 'hospital', '147 Birch Rd, City, State 12345', '555-0700', 'www.emergencycare.com', '78-9012345'),
('Specialty Heart Clinic', 'clinic', '258 Spruce St, City, State 12345', '555-0800', 'www.heartclinic.com', '89-0123456'),
('Regional Lab Services', 'lab', '369 Willow Way, City, State 12345', '555-0900', 'www.regionallab.com', '90-1234567'),
('MedMart Pharmacy', 'pharmacy', '741 Poplar Ave, City, State 12345', '555-1000', 'www.medmart.com', '01-2345678'),
('University Medical Center', 'hospital', '852 University Blvd, City, State 12345', '555-1100', 'www.universitymed.com', '12-3456780'),
('Northside Urgent Care', 'clinic', '963 Northern Pike, City, State 12345', '555-1200', 'www.northsideurgent.com', '23-4567891'),
('Premier Diagnostics', 'lab', '174 Commerce St, City, State 12345', '555-1300', 'www.premierdiag.com', '34-5678902'),
('Community Pharmacy', 'pharmacy', '285 Community Dr, City, State 12345', '555-1400', 'www.communitypharm.com', '45-6789013'),
('Metro Health Insurance', 'insurance', '396 Metro Plaza, City, State 12345', '555-1500', 'www.metrohealth.com', '56-7890124'),
('Pediatric Care Associates', 'clinic', '417 Children Way, City, State 12345', '555-1600', 'www.pediatriccare.com', '67-8901235'),
('Central Medical Hospital', 'hospital', '528 Central Ave, City, State 12345', '555-1700', 'www.centralmedical.com', '78-9012346'),
('Express Lab', 'lab', '639 Express Ln, City, State 12345', '555-1800', 'www.expresslab.com', '89-0123457'),
('Family Pharmacy', 'pharmacy', '740 Family Circle, City, State 12345', '555-1900', 'www.familypharm.com', '90-1234568'),
('Seniors Health Clinic', 'clinic', '851 Retirement Rd, City, State 12345', '555-2000', 'www.seniorshealth.com', '01-2345679');

-- Providers
INSERT INTO provider (name, provider_type, specialty, npi, address, phone, email) VALUES
('Dr. Sarah Johnson', 'practitioner', 'Internal Medicine', '1234567890', '123 Medical Plaza, City, State 12345', '555-2100', 'sjohnson@medical.com'),
('Dr. Michael Chen', 'practitioner', 'Cardiology', '2345678901', '456 Heart Center, City, State 12345', '555-2200', 'mchen@cardio.com'),
('Dr. Emily Rodriguez', 'practitioner', 'Pediatrics', '3456789012', '789 Kids Clinic, City, State 12345', '555-2300', 'erodriguez@kids.com'),
('Dr. Robert Williams', 'practitioner', 'Orthopedics', '4567890123', '321 Bone Center, City, State 12345', '555-2400', 'rwilliams@ortho.com'),
('Dr. Lisa Thompson', 'practitioner', 'Emergency Medicine', '5678901234', '654 Emergency Dr, City, State 12345', '555-2500', 'lthompson@emergency.com'),
('QuickLab Central', 'facility', 'Laboratory Services', '6789012345', '789 Pine St, City, State 12345', '555-0300', 'info@quicklab.com'),
('Corner Pharmacy Main', 'facility', 'Pharmacy Services', '7890123456', '321 Elm St, City, State 12345', '555-0400', 'main@cornerpharm.com'),
('Dr. James Martinez', 'practitioner', 'Family Medicine', '8901234567', '987 Family Way, City, State 12345', '555-2600', 'jmartinez@family.com'),
('Dr. Amanda Davis', 'practitioner', 'Dermatology', '9012345678', '147 Skin Care Ln, City, State 12345', '555-2700', 'adavis@derm.com'),
('Dr. Kevin Brown', 'practitioner', 'Neurology', '0123456789', '258 Brain St, City, State 12345', '555-2800', 'kbrown@neuro.com'),
('Regional Lab Main', 'facility', 'Laboratory Services', '1234567891', '369 Willow Way, City, State 12345', '555-0900', 'main@regionallab.com'),
('MedMart Central', 'facility', 'Pharmacy Services', '2345678902', '741 Poplar Ave, City, State 12345', '555-1000', 'central@medmart.com'),
('Dr. Patricia Wilson', 'practitioner', 'Obstetrics/Gynecology', '3456789013', '852 Women Health Blvd, City, State 12345', '555-2900', 'pwilson@womens.com'),
('Dr. Christopher Lee', 'practitioner', 'Psychiatry', '4567890124', '963 Mental Health Pike, City, State 12345', '555-3000', 'clee@psych.com'),
('Dr. Jennifer Taylor', 'practitioner', 'Radiology', '5678901235', '174 Imaging St, City, State 12345', '555-3100', 'jtaylor@radiology.com'),
('Premier Lab Services', 'facility', 'Laboratory Services', '6789012346', '174 Commerce St, City, State 12345', '555-1300', 'services@premierdiag.com'),
('Community Pharmacy East', 'facility', 'Pharmacy Services', '7890123457', '285 Community Dr, City, State 12345', '555-1400', 'east@communitypharm.com'),
('Dr. Mark Anderson', 'practitioner', 'Gastroenterology', '8901234568', '396 Digestive Way, City, State 12345', '555-3200', 'manderson@gastro.com'),
('Dr. Susan White', 'practitioner', 'Endocrinology', '9012345679', '417 Hormone Ln, City, State 12345', '555-3300', 'swhite@endo.com'),
('Dr. David Miller', 'practitioner', 'Pulmonology', '0123456780', '528 Lung Center Ave, City, State 12345', '555-3400', 'dmiller@pulm.com'),
('Express Lab Services', 'facility', 'Laboratory Services', '1234567892', '639 Express Ln, City, State 12345', '555-1800', 'services@expresslab.com'),
('Family Pharmacy North', 'facility', 'Pharmacy Services', '2345678903', '740 Family Circle, City, State 12345', '555-1900', 'north@familypharm.com');

-- Provider-Organization relationships
INSERT INTO provider_organization (provider_id, organization_id, role, start_date) VALUES
(1, 1, 'Attending Physician', '2020-01-15'),
(1, 2, 'Consultant', '2021-06-01'),
(2, 1, 'Cardiologist', '2019-03-10'),
(2, 8, 'Chief of Cardiology', '2018-01-01'),
(3, 16, 'Pediatrician', '2021-09-01'),
(3, 2, 'Part-time Pediatrician', '2022-01-15'),
(4, 1, 'Orthopedic Surgeon', '2017-11-20'),
(4, 17, 'Consulting Surgeon', '2020-05-01'),
(5, 7, 'Emergency Physician', '2019-07-01'),
(5, 1, 'Emergency Consultant', '2021-01-01'),
(6, 3, 'Lab Director', '2018-01-01'),
(7, 4, 'Pharmacy Manager', '2019-01-01'),
(8, 6, 'Family Physician', '2020-03-01'),
(8, 12, 'Urgent Care Physician', '2021-01-01'),
(9, 2, 'Dermatologist', '2019-05-01'),
(10, 1, 'Neurologist', '2018-08-01'),
(11, 9, 'Lab Technician Supervisor', '2019-01-01'),
(12, 10, 'Pharmacy Manager', '2020-01-01'),
(13, 1, 'OB/GYN', '2017-12-01'),
(14, 12, 'Psychiatrist', '2020-06-01'),
(15, 1, 'Radiologist', '2018-04-01'),
(16, 13, 'Lab Director', '2019-01-01'),
(17, 14, 'Pharmacy Manager', '2018-01-01'),
(18, 1, 'Gastroenterologist', '2019-10-01'),
(19, 2, 'Endocrinologist', '2020-02-01'),
(20, 11, 'Pulmonologist', '2018-06-01'),
(21, 18, 'Lab Manager', '2020-01-01'),
(22, 19, 'Pharmacy Manager', '2019-01-01');

-- Patients
INSERT INTO patient (first_name, last_name, date_of_birth, gender, address, phone, email, insurance_id) VALUES
('John', 'Smith', '1985-03-15', 'M', '123 Oak St, City, State 12345', '555-4100', 'john.smith@email.com', 'INS001234567'),
('Mary', 'Johnson', '1990-07-22', 'F', '456 Pine Ave, City, State 12345', '555-4200', 'mary.johnson@email.com', 'INS002345678'),
('Robert', 'Brown', '1978-11-08', 'M', '789 Maple Dr, City, State 12345', '555-4300', 'robert.brown@email.com', 'INS003456789'),
('Jennifer', 'Davis', '1995-02-14', 'F', '321 Cedar Ln, City, State 12345', '555-4400', 'jennifer.davis@email.com', 'INS004567890'),
('Michael', 'Wilson', '1982-09-30', 'M', '654 Birch Rd, City, State 12345', '555-4500', 'michael.wilson@email.com', 'INS005678901'),
('Sarah', 'Miller', '1988-12-05', 'F', '987 Spruce St, City, State 12345', '555-4600', 'sarah.miller@email.com', 'INS006789012'),
('David', 'Anderson', '1975-04-18', 'M', '147 Willow Way, City, State 12345', '555-4700', 'david.anderson@email.com', 'INS007890123'),
('Lisa', 'Taylor', '1992-08-25', 'F', '258 Poplar Ave, City, State 12345', '555-4800', 'lisa.taylor@email.com', 'INS008901234'),
('James', 'Thomas', '1980-06-12', 'M', '369 Elm St, City, State 12345', '555-4900', 'james.thomas@email.com', 'INS009012345'),
('Patricia', 'Jackson', '1987-01-28', 'F', '741 Oak Ave, City, State 12345', '555-5000', 'patricia.jackson@email.com', 'INS010123456'),
('William', 'White', '1993-10-03', 'M', '852 Pine Dr, City, State 12345', '555-5100', 'william.white@email.com', 'INS011234567'),
('Linda', 'Harris', '1976-05-17', 'F', '963 Maple Ln, City, State 12345', '555-5200', 'linda.harris@email.com', 'INS012345678'),
('Richard', 'Martin', '1989-03-09', 'M', '174 Cedar St, City, State 12345', '555-5300', 'richard.martin@email.com', 'INS013456789'),
('Barbara', 'Garcia', '1984-12-21', 'F', '285 Birch Ave, City, State 12345', '555-5400', 'barbara.garcia@email.com', 'INS014567890'),
('Charles', 'Rodriguez', '1991-07-06', 'M', '396 Spruce Dr, City, State 12345', '555-5500', 'charles.rodriguez@email.com', 'INS015678901'),
('Susan', 'Lewis', '1979-09-13', 'F', '417 Willow St, City, State 12345', '555-5600', 'susan.lewis@email.com', 'INS016789012'),
('Joseph', 'Lee', '1986-11-26', 'M', '528 Poplar Ln, City, State 12345', '555-5700', 'joseph.lee@email.com', 'INS017890123'),
('Nancy', 'Walker', '1994-04-02', 'F', '639 Elm Dr, City, State 12345', '555-5800', 'nancy.walker@email.com', 'INS018901234'),
('Thomas', 'Hall', '1981-08-19', 'M', '740 Oak Ln, City, State 12345', '555-5900', 'thomas.hall@email.com', 'INS019012345'),
('Karen', 'Allen', '1996-01-07', 'F', '851 Pine St, City, State 12345', '555-6000', 'karen.allen@email.com', 'INS020123456'),
('Christopher', 'Young', '1977-06-24', 'M', '962 Maple Ave, City, State 12345', '555-6100', 'christopher.young@email.com', 'INS021234567'),
('Michelle', 'King', '1983-02-11', 'F', '173 Cedar Dr, City, State 12345', '555-6200', 'michelle.king@email.com', 'INS022345678');

-- Encounters
INSERT INTO encounter (patient_id, provider_id, organization_id, encounter_date, encounter_type, status, notes) VALUES
(1, 1, 1, '2024-01-15', 'outpatient', 'completed', 'Annual physical examination'),
(1, 2, 8, '2024-02-20', 'outpatient', 'completed', 'Cardiology consultation for chest pain'),
(2, 3, 16, '2024-01-10', 'outpatient', 'completed', 'Pediatric wellness visit'),
(3, 4, 1, '2024-01-25', 'inpatient', 'completed', 'Knee replacement surgery'),
(4, 5, 7, '2024-02-01', 'emergency', 'completed', 'Emergency room visit for abdominal pain'),
(5, 1, 2, '2024-01-30', 'outpatient', 'completed', 'Follow-up for diabetes management'),
(6, 8, 6, '2024-02-05', 'outpatient', 'completed', 'Family medicine consultation'),
(7, 9, 2, '2024-02-10', 'outpatient', 'completed', 'Dermatology appointment for skin rash'),
(8, 10, 1, '2024-02-15', 'outpatient', 'completed', 'Neurology consultation for headaches'),
(9, 13, 1, '2024-01-20', 'outpatient', 'completed', 'OB/GYN annual exam'),
(10, 14, 12, '2024-02-12', 'outpatient', 'completed', 'Psychiatry session'),
(11, 15, 1, '2024-01-28', 'outpatient', 'completed', 'Radiology - MRI scan'),
(12, 18, 1, '2024-02-08', 'outpatient', 'completed', 'Gastroenterology consultation'),
(13, 19, 2, '2024-02-18', 'outpatient', 'completed', 'Endocrinology follow-up'),
(14, 20, 11, '2024-01-22', 'outpatient', 'completed', 'Pulmonology consultation'),
(15, 1, 1, '2024-02-22', 'outpatient', 'completed', 'Internal medicine follow-up'),
(16, 2, 1, '2024-02-25', 'outpatient', 'completed', 'Cardiology follow-up'),
(17, 8, 12, '2024-02-28', 'outpatient', 'completed', 'Urgent care visit for flu'),
(18, 5, 7, '2024-03-01', 'emergency', 'completed', 'Emergency visit for allergic reaction'),
(19, 1, 2, '2024-03-05', 'outpatient', 'completed', 'Routine check-up'),
(20, 3, 16, '2024-03-08', 'outpatient', 'completed', 'Pediatric vaccination'),
(1, 6, 3, '2024-02-28', 'outpatient', 'completed', 'Laboratory testing'),
(2, 7, 4, '2024-03-01', 'outpatient', 'completed', 'Prescription pickup'),
(3, 11, 9, '2024-03-03', 'outpatient', 'completed', 'Blood work'),
(4, 12, 10, '2024-03-05', 'outpatient', 'completed', 'Medication consultation'),
(5, 16, 13, '2024-03-07', 'outpatient', 'completed', 'Lab results review'),
(6, 17, 14, '2024-03-10', 'outpatient', 'completed', 'Prescription refill'),
(7, 21, 18, '2024-03-12', 'outpatient', 'completed', 'Diagnostic testing'),
(8, 22, 19, '2024-03-15', 'outpatient', 'completed', 'Pharmacy consultation');

-- Claim Lines
INSERT INTO claim_line (encounter_id, procedure_code, procedure_description, charge_amount, service_date, modifier) VALUES
(1, '99213', 'Office visit - established patient, level 3', 165.00, '2024-01-15', NULL),
(1, '85025', 'Complete blood count with differential', 45.00, '2024-01-15', NULL),
(2, '99244', 'Office consultation - new patient, level 4', 285.00, '2024-02-20', NULL),
(2, '93000', 'Electrocardiogram, routine ECG', 85.00, '2024-02-20', NULL),
(3, '99382', 'Preventive medicine visit, new patient, age 12-17', 195.00, '2024-01-10', NULL),
(3, '90715', 'Tdap vaccine', 55.00, '2024-01-10', NULL),
(4, '27447', 'Total knee arthroplasty', 15500.00, '2024-01-25', NULL),
(4, '00400', 'Anesthesia for procedures on the knee', 450.00, '2024-01-25', NULL),
(5, '99283', 'Emergency department visit, level 3', 345.00, '2024-02-01', NULL),
(5, '74150', 'CT scan of abdomen without contrast', 650.00, '2024-02-01', NULL),
(6, '99214', 'Office visit - established patient, level 4', 215.00, '2024-01-30', NULL),
(6, '82947', 'Glucose blood test', 25.00, '2024-01-30', NULL),
(7, '99213', 'Office visit - established patient, level 3', 165.00, '2024-02-05', NULL),
(8, '99213', 'Office visit - established patient, level 3', 165.00, '2024-02-10', NULL),
(8, '11100', 'Skin biopsy', 125.00, '2024-02-10', NULL),
(9, '99214', 'Office visit - established patient, level 4', 215.00, '2024-02-15', NULL),
(9, '70553', 'MRI brain with and without contrast', 1250.00, '2024-02-15', NULL),
(10, '99395', 'Preventive medicine visit, established patient, age 18-39', 185.00, '2024-01-20', NULL),
(10, '87210', 'Cervical cytology screening', 85.00, '2024-01-20', NULL),
(11, '90834', 'Psychotherapy, 45 minutes', 150.00, '2024-02-12', NULL),
(12, '70551', 'MRI brain without contrast', 1150.00, '2024-01-28', NULL),
(13, '99244', 'Office consultation - new patient, level 4', 285.00, '2024-02-08', NULL),
(13, '91065', 'Breath hydrogen test', 185.00, '2024-02-08', NULL),
(14, '99214', 'Office visit - established patient, level 4', 215.00, '2024-02-18', NULL),
(14, '84443', 'Thyroid stimulating hormone test', 65.00, '2024-02-18', NULL),
(15, '99214', 'Office visit - established patient, level 4', 215.00, '2024-01-22', NULL),
(15, '94010', 'Spirometry test', 95.00, '2024-01-22', NULL),
(16, '99213', 'Office visit - established patient, level 3', 165.00, '2024-02-22', NULL),
(17, '99213', 'Office visit - established patient, level 3', 165.00, '2024-02-25', NULL),
(17, '93005', 'Electrocardiogram, tracing only', 55.00, '2024-02-25', NULL),
(18, '99212', 'Office visit - established patient, level 2', 125.00, '2024-02-28', NULL),
(18, '87804', 'Influenza test', 45.00, '2024-02-28', NULL),
(19, '99282', 'Emergency department visit, level 2', 245.00, '2024-03-01', NULL),
(19, '96365', 'IV infusion therapy', 125.00, '2024-03-01', NULL),
(20, '99213', 'Office visit - established patient, level 3', 165.00, '2024-03-05', NULL),
(21, '99381', 'Preventive medicine visit, new patient, age 12-17', 185.00, '2024-03-08', NULL),
(21, '90714', 'Tetanus and diphtheria vaccine', 45.00, '2024-03-08', NULL),
(22, '80053', 'Comprehensive metabolic panel', 55.00, '2024-02-28', NULL),
(23, '99070', 'Supplies and materials', 25.00, '2024-03-01', NULL),
(24, '85025', 'Complete blood count with differential', 45.00, '2024-03-03', NULL),
(24, '85014', 'Hematocrit', 15.00, '2024-03-03', NULL),
(25, '99211', 'Office visit - established patient, level 1', 85.00, '2024-03-05', NULL),
(26, '84153', 'PSA test', 75.00, '2024-03-07', NULL),
(27, '99070', 'Supplies and materials', 25.00, '2024-03-10', NULL),
(28, '36415', 'Venipuncture', 25.00, '2024-03-12', NULL),
(28, '80048', 'Basic metabolic panel', 45.00, '2024-03-12', NULL),
(29, '99211', 'Office visit - established patient, level 1', 85.00, '2024-03-15', NULL);

COMMIT;