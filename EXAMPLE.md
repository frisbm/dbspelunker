# Database Documentation: flume

- Type: `postgresql` · Generated: `2025-09-08 18:01:11`

## Executive Summary

Database Analysis Summary:
- Database: flume (postgresql)
- Total Tables: 5
- Total Columns: 48
- Total Constraints: 10
- Total Indexes: 9
- Total Triggers: 7
- Total Relationships: 5
- Schemas Analyzed: 1

This database contains 5 tables with 48 columns across 1 schema(s).
The analysis identified 5 foreign key relationships between tables.

## Database Overview

| Key | Value |
| --- | ----- |
| Name | flume |
| Type | postgresql |
| Version |  |
| Total Tables | 5 |
| Total Views | 0 |
| Stored Procedures | 6 |
| Indexes | 9 |
| Triggers | 7 |
| Database Size |  |
| Character Set |  |
| Collation |  |

## Table of Contents

- [Database Overview](#database-overview)
- [Schemas](#schemas)
- [Relationships](#relationships)
- [Indexes](#indexes)
- [Performance Insights](#performance-insights)
- [Security Considerations](#security-considerations)
- [Recommendations](#recommendations)
- [Table Documentation](#table-documentation)
- [Stored Procedures](#stored-procedures)

## Schemas

### Schema: healthcare_test
| Key | Value |
| --- | ----- |
| Tables | 5 |
| Views | 0 |
| Stored Procedures | 6 |
| Relationships | 5 |

#### Tables

##### Table: healthcare_test.doctors
- Type: `table` · Rows: `-1` · Size: `80.00 KB`

> This table is a master directory of physicians, storing their core demographic, contact, and professional credential information for a healthcare organization. It serves as the central record for each doctor, tracking details like their medical specialty, unique license number, and employment status. This table is referenced by other parts of the system to manage both administrative and clinical relationships, such as assigning doctors to specific clinic locations and linking them to the patients under their care. The presence of an `is_active` flag and `hire_date` suggests the table is also used for operational and HR purposes to manage the physician roster.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare\_test.doctors\_id\_seq'::regclass) | Yes | No |  |  |
| first\_name | char | No |  | No | No |  |  |
| last\_name | char | No |  | No | No |  |  |
| specialty | char | Yes |  | No | No |  |  |
| license\_number | char | No |  | No | No |  |  |
| email | char | Yes |  | No | No |  |  |
| phone | char | Yes |  | No | No |  |  |
| hire\_date | date | Yes | CURRENT\_DATE | No | No |  |  |
| is\_active | boolean | Yes | true | No | No |  |  |
| created\_at | timestamp | Yes | now() | No | No |  |  |
| updated\_at | timestamp | Yes | now() | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| doctors\_pkey | primary\_key | id |  |  |

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| doctors\_license\_number\_key | unique | license\_number | Yes | No | No |  |  |
| idx\_doctors\_license | index | license\_number | No | No | No |  |  |
| idx\_doctors\_specialty | index | specialty | No | No | No |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| doctor\_license\_validation | before | insert | Yes | Trigger function: validate\_doctor\_license |
| update\_doctors\_timestamp | before | update | Yes | Trigger function: update\_modified\_at\_column |

###### Trigger: doctor_license_validation

> **AI Analysis:** This trigger ensures that a doctor's license is validated before their information is added to or updated in the database. It serves as an automated checkpoint to enforce compliance and data accuracy for physician records. The primary business purpose is to prevent unlicensed or improperly documented doctors from being entered into the system, safeguarding patient safety and meeting regulatory requirements.

Business Rule/Process: A doctor's record cannot be created or modified in the system unless their license information passes a predefined validation check.

Implications: This trigger is crucial for data integrity, ensuring that every doctor record meets a minimum licensing standard. However, because it executes on every insert and update, the performance of the validation function is critical; a slow or failing validation process could prevent or delay the entry and management of doctor records.

**Definition:**
```sql
CREATE TRIGGER doctor_license_validation
BEFORE
  INSERT
    OR
  UPDATE
    ON healthcare_test.doctors
   FOR EACH ROW EXECUTE
FUNCTION healthcare_test.validate_doctor_license()
```

###### Trigger: update_doctors_timestamp

> **AI Analysis:** This trigger automatically records the date and time whenever a doctor's record is modified. Its purpose is to maintain an accurate and automated audit trail, ensuring that all changes to a doctor's information are time-stamped for data governance and tracking.

Business Rule: Implements the rule that every modification to a doctor's profile must be time-stamped to track the "last updated" time. This automates a key step in the data maintenance process, removing the need for applications to manage this timestamp manually.

Implications: The trigger enhances data integrity and auditability by guaranteeing that a "last modified" timestamp is always current and accurate. While the performance impact is generally negligible, it adds a small, consistent overhead to every update operation on the doctors table.

**Definition:**
```sql
CREATE TRIGGER update_doctors_timestamp
BEFORE
  UPDATE
    ON healthcare_test.doctors
   FOR EACH ROW EXECUTE
FUNCTION healthcare_test.update_modified_at_column()
```

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| doctor\_clinic\_assignments | doctor\_id | doctors | id | doctor\_clinic\_assignments\_doctor\_id\_fkey |  |  | one\_to\_many |
| patient\_doctor\_relationships | doctor\_id | doctors | id | patient\_doctor\_relationships\_doctor\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
and is referenced by doctor_clinic_assignments, referenced by patient_doctor_relationships.

##### Table: healthcare_test.clinics
- Type: `table` · Rows: `-1` · Size: `32.00 KB`

> The `clinics` table is a master list of healthcare facilities, storing their names and contact details. It acts as a foundational reference, allowing the system to associate doctors with the specific clinics they work at and to record the location where a patient's relationship with a doctor is established. This structure is essential for managing staff assignments and patient records across a network of different physical locations.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare\_test.clinics\_id\_seq'::regclass) | Yes | No |  |  |
| name | char | No |  | No | No |  |  |
| address | text | Yes |  | No | No |  |  |
| phone | char | Yes |  | No | No |  |  |
| email | char | Yes |  | No | No |  |  |
| created\_at | timestamp | Yes | now() | No | No |  |  |
| updated\_at | timestamp | Yes | now() | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| clinics\_pkey | primary\_key | id |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| update\_clinics\_timestamp | before | update | Yes | Trigger function: update\_modified\_at\_column |

###### Trigger: update_clinics_timestamp

> **AI Analysis:** This trigger automatically updates the `updated_at` timestamp to the current time whenever a clinic's record is modified. Its purpose is to maintain an accurate audit trail, ensuring there is always a reliable record of when a clinic's information was last changed. This is crucial for tracking data currency and for synchronization with other systems.

Business Rule: "Whenever a clinic's information is updated, the 'last modified' timestamp for that clinic must be automatically recorded."

Implications: The trigger ensures data integrity by keeping the `updated_at` field accurate, which provides a reliable, system-managed audit log for data modifications. The performance impact is minimal as it is a very common and lightweight operation that fires only on updates.

**Definition:**
```sql
CREATE TRIGGER update_clinics_timestamp
BEFORE
  UPDATE
    ON healthcare_test.clinics
   FOR EACH ROW EXECUTE
FUNCTION healthcare_test.update_modified_at_column()
```

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| doctor\_clinic\_assignments | clinic\_id | clinics | id | doctor\_clinic\_assignments\_clinic\_id\_fkey |  |  | one\_to\_many |
| patient\_doctor\_relationships | clinic\_id | clinics | id | patient\_doctor\_relationships\_clinic\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
and is referenced by doctor_clinic_assignments, referenced by patient_doctor_relationships.

##### Table: healthcare_test.patients
- Type: `table` · Rows: `-1` · Size: `80.00 KB`

> This table acts as a central patient registry, storing core demographic, contact, and identification information for individuals within a healthcare system. It uses a unique medical record number to identify each person, serving as the master record for patient identity. The table's primary business purpose is to be the authoritative source for patient data, allowing other system components, like the `patient_doctor_relationships` table, to link medical activities and provider assignments to a specific patient.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare\_test.patients\_id\_seq'::regclass) | Yes | No |  |  |
| first\_name | char | No |  | No | No |  |  |
| last\_name | char | No |  | No | No |  |  |
| date\_of\_birth | date | Yes |  | No | No |  |  |
| gender | char | Yes |  | No | No |  |  |
| email | char | Yes |  | No | No |  |  |
| phone | char | Yes |  | No | No |  |  |
| emergency\_contact | char | Yes |  | No | No |  |  |
| emergency\_phone | char | Yes |  | No | No |  |  |
| medical\_record\_number | char | Yes |  | No | No |  |  |
| created\_at | timestamp | Yes | now() | No | No |  |  |
| updated\_at | timestamp | Yes | now() | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| patients\_pkey | primary\_key | id |  |  |

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| idx\_patients\_dob | index | date\_of\_birth | No | No | No |  |  |
| idx\_patients\_mrn | index | medical\_record\_number | No | No | No |  |  |
| patients\_medical\_record\_number\_key | unique | medical\_record\_number | Yes | No | No |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| patient\_audit\_trigger | after | insert | Yes | Trigger function: patient\_audit\_log |
| update\_patients\_timestamp | before | update | Yes | Trigger function: update\_modified\_at\_column |

###### Trigger: patient_audit_trigger

> **AI Analysis:** This trigger automatically creates an audit log for every new patient record created, as well as any updates or deletions to existing patient records. Its purpose is to maintain a complete, historical record of all changes to sensitive patient data. This is essential for security monitoring, data governance, and meeting regulatory compliance requirements like HIPAA.

Business Rule/Process:
The trigger implements a mandatory data auditing policy: "Every creation, modification, or deletion of a patient record must be logged."

Implications:
This trigger is critical for creating a reliable audit trail, enhancing data security and ensuring regulatory compliance. However, because it executes for every single row modification, it adds overhead to all insert, update, and delete operations on the patients table, which could impact performance during bulk data processing.

**Definition:**
```sql
CREATE TRIGGER patient_audit_trigger AFTER
  INSERT
    OR
  DELETE
    OR
  UPDATE
    ON healthcare_test.patients
   FOR EACH ROW EXECUTE
FUNCTION healthcare_test.patient_audit_log()
```

###### Trigger: update_patients_timestamp

> **AI Analysis:** This trigger automatically updates a timestamp field every time a patient's record is modified. It serves as an automated auditing mechanism to track when patient data was last changed. This ensures data currency is always recorded, which is vital for compliance, troubleshooting, and data synchronization processes.

The business rule implemented is: "The system must automatically record the date and time of the last modification for every patient record."

This trigger is crucial for maintaining a data audit trail, which supports data integrity and compliance requirements (e.g., HIPAA). While the performance impact is generally negligible, it adds a small overhead to every update operation on the table, which could be a factor in very large bulk updates.

**Definition:**
```sql
CREATE TRIGGER update_patients_timestamp
BEFORE
  UPDATE
    ON healthcare_test.patients
   FOR EACH ROW EXECUTE
FUNCTION healthcare_test.update_modified_at_column()
```

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| patient\_doctor\_relationships | patient\_id | patients | id | patient\_doctor\_relationships\_patient\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
and is referenced by patient_doctor_relationships.

##### Table: healthcare_test.doctor_clinic_assignments
- Type: `table` · Rows: `-1` · Size: `56.00 KB`

> This table tracks the work assignments of doctors to specific clinics, serving as a historical and current record of their professional affiliations. It stores the time period of the assignment, the doctor's specific role at that clinic, and whether the assignment is currently active. This table functions as a bridge between the 'doctors' and 'clinics' tables, managing the business reality that a doctor can work at multiple clinics and a clinic can employ many doctors. The date range and active status fields are crucial for managing scheduling and understanding a doctor's availability and work history across different locations.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare\_test.doctor\_clinic\_assignments\_id\_seq'::regclass) | Yes | No |  |  |
| doctor\_id | integer | No |  | No | Yes | fk→doctors(id) |  |
| clinic\_id | integer | No |  | No | Yes | fk→clinics(id) |  |
| start\_date | date | Yes | CURRENT\_DATE | No | No |  |  |
| end\_date | date | Yes |  | No | No |  |  |
| is\_active | boolean | Yes | true | No | No |  |  |
| role | char | Yes | 'attending'::character varying | No | No |  |  |
| created\_at | timestamp | Yes | now() | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| doctor\_clinic\_assignments\_pkey | primary\_key | id |  |  |
| doctor\_clinic\_assignments\_clinic\_id\_fkey | foreign\_key | clinic\_id | ref clinics(id) |  |
| doctor\_clinic\_assignments\_doctor\_id\_fkey | foreign\_key | doctor\_id | ref doctors(id) |  |

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| doctor\_clinic\_assignments\_doctor\_id\_clinic\_id\_start\_date\_key | unique | doctor\_id, clinic\_id, start\_date | Yes | No | No |  |  |
| idx\_doctor\_clinic\_active | index | doctor\_id, clinic\_id | No | No | No |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| clinic\_capacity\_doctor\_trigger | after | insert | Yes | Trigger function: manage\_clinic\_capacity |

###### Trigger: clinic_capacity_doctor_trigger

> **AI Analysis:** This trigger automatically updates a clinic's capacity information whenever a doctor's assignment to that clinic is created, modified, or removed. Its purpose is to ensure that clinic capacity metrics, such as doctor count or service availability, are always kept current and accurately reflect real-time staffing levels. This automation is crucial for systems that rely on up-to-date capacity data for patient scheduling or resource planning.

Business Rule: A clinic's capacity data must be recalculated and updated immediately following any change to its roster of assigned doctors. This automates the "Clinic Staffing and Capacity Management" process.

Implications: This trigger enforces data consistency between doctor assignments and clinic capacity metrics. However, because it executes for every individual row change (insert, update, or delete), it could introduce performance overhead, potentially slowing down bulk updates to the doctor assignment table.

**Definition:**
```sql
CREATE TRIGGER clinic_capacity_doctor_trigger AFTER
  INSERT
    OR
  DELETE
    OR
  UPDATE
    ON healthcare_test.doctor_clinic_assignments
   FOR EACH ROW EXECUTE
FUNCTION healthcare_test.manage_clinic_capacity()
```

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| doctor\_clinic\_assignments | clinic\_id | clinics | id | doctor\_clinic\_assignments\_clinic\_id\_fkey |  |  | one\_to\_many |
| doctor\_clinic\_assignments | doctor\_id | doctors | id | doctor\_clinic\_assignments\_doctor\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
This table references clinics, references doctors.

##### Table: healthcare_test.patient_doctor_relationships
- Type: `table` · Rows: `-1` · Size: `48.00 KB`

> This table serves as a central record for managing the professional associations between patients and doctors within a healthcare system. It stores key details for each specific relationship, such as its type (e.g., primary care, specialist), its duration, and its current active status. The table functions as a crucial link between the patients, doctors, and clinics tables, defining exactly which doctor is associated with which patient at a specific clinic, thereby enabling the tracking of care assignments over time. The inclusion of start/end dates and an active status flag highlights its business purpose in maintaining a complete history of patient care relationships for continuity and administrative reporting.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare\_test.patient\_doctor\_relationships\_id\_seq'::regclass) | Yes | No |  |  |
| patient\_id | integer | No |  | No | Yes | fk→patients(id) |  |
| doctor\_id | integer | No |  | No | Yes | fk→doctors(id) |  |
| clinic\_id | integer | No |  | No | Yes | fk→clinics(id) |  |
| relationship\_type | char | Yes | 'primary\_care'::character varying | No | No |  |  |
| started\_at | timestamp | Yes | now() | No | No |  |  |
| ended\_at | timestamp | Yes |  | No | No |  |  |
| is\_active | boolean | Yes | true | No | No |  |  |
| notes | text | Yes |  | No | No |  |  |
| created\_at | timestamp | Yes | now() | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| patient\_doctor\_relationships\_pkey | primary\_key | id |  |  |
| patient\_doctor\_relationships\_clinic\_id\_fkey | foreign\_key | clinic\_id | ref clinics(id) |  |
| patient\_doctor\_relationships\_doctor\_id\_fkey | foreign\_key | doctor\_id | ref doctors(id) |  |
| patient\_doctor\_relationships\_patient\_id\_fkey | foreign\_key | patient\_id | ref patients(id) |  |

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| idx\_patient\_doctor\_active | index | patient\_id, doctor\_id | No | No | No |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| clinic\_capacity\_patient\_trigger | after | insert | Yes | Trigger function: manage\_clinic\_capacity |

###### Trigger: clinic_capacity_patient_trigger

> **AI Analysis:** This trigger automatically updates a clinic's capacity information whenever a patient-doctor relationship is created, modified, or removed. It ensures that metrics reflecting patient load are always accurate, supporting operational decisions like new patient intake and resource allocation.

Business Rule: A clinic's patient count and available capacity must be recalculated in real-time as patient assignments change. This automates the process of tracking clinic utilization.

Implications: The trigger enforces data consistency between the patient roster and any related clinic capacity data. However, because it executes on every insert, update, and delete, it may introduce performance overhead on a high-transaction table, potentially slowing down patient assignment operations.

**Definition:**
```sql
CREATE TRIGGER clinic_capacity_patient_trigger AFTER
  INSERT
    OR
  DELETE
    OR
  UPDATE
    ON healthcare_test.patient_doctor_relationships
   FOR EACH ROW EXECUTE
FUNCTION healthcare_test.manage_clinic_capacity()
```

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| patient\_doctor\_relationships | clinic\_id | clinics | id | patient\_doctor\_relationships\_clinic\_id\_fkey |  |  | one\_to\_many |
| patient\_doctor\_relationships | doctor\_id | doctors | id | patient\_doctor\_relationships\_doctor\_id\_fkey |  |  | one\_to\_many |
| patient\_doctor\_relationships | patient\_id | patients | id | patient\_doctor\_relationships\_patient\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
This table references clinics, references doctors, references patients.

#### Stored Procedures

| Name | Returns | Language | Deterministic | Created | Modified |
| --- | --- | --- | --- | --- | --- |
| get\_doctor\_patient\_summary | record | plpgsql | No |  |  |
| get\_patient\_care\_team | record | plpgsql | No |  |  |
| manage\_clinic\_capacity | trigger | plpgsql | No |  |  |
| patient\_audit\_log | trigger | plpgsql | No |  |  |
| update\_modified\_at\_column | trigger | plpgsql | No |  |  |
| validate\_doctor\_license | trigger | plpgsql | No |  |  |

##### Procedure: get_doctor_patient_summary

> **AI Analysis:** This procedure generates a consolidated summary report for a specific doctor's professional activities. It calculates key metrics such as their total active patient count, a breakdown of primary care versus specialist patients, and a list of associated clinics. The purpose is to provide a quick, high-level overview for practice management, performance analysis, or administrative dashboards.
Reporting and data aggregation.
This procedure serves as a data source for a reporting feature, likely a doctor's profile or dashboard screen in a healthcare management application. It centralizes the business logic for calculating a doctor's key performance indicators (KPIs), ensuring consistent reporting across the system.

**Definition:**
```sql
CREATE OR REPLACE
FUNCTION healthcare_test.get_doctor_patient_summary(p_doctor_id integer) RETURNS table(doctor_name text, specialty CHARACTER varying, total_active_patients integer, total_clinics integer, primary_care_patients integer, specialist_patients integer, newest_patient_date timestamp WITHOUT TIME ZONE, oldest_patient_date timestamp WITHOUT TIME ZONE, clinic_list text) LANGUAGE PLPGSQL AS $function$
DECLARE
    v_doctor_name TEXT;
    v_specialty VARCHAR;
BEGIN
    -- Get doctor basic info
    SELECT CONCAT(first_name, ' ', last_name), doctors.specialty
    INTO v_doctor_name, v_specialty
    FROM doctors
    WHERE id = p_doctor_id;
    IF v_doctor_name IS NULL THEN
        RAISE EXCEPTION 'Doctor with ID % not found', p_doctor_id;
    END IF;
    RETURN QUERY
    SELECT
        v_doctor_name as doctor_name,
        v_specialty as specialty,
        COUNT(DISTINCT pdr.patient_id)::INTEGER as total_active_patients,
        COUNT(DISTINCT pdr.clinic_id)::INTEGER as total_clinics,
        COUNT(CASE WHEN pdr.relationship_type = 'primary_care' THEN 1 END)::INTEGER as primary_care_patients,
        COUNT(CASE WHEN pdr.relationship_type != 'primary_care' THEN 1 END)::INTEGER as specialist_patients,
        MAX(pdr.started_at) as newest_patient_date,
        MIN(pdr.started_at) as oldest_patient_date,
        STRING_AGG(DISTINCT c.name, ', ') as clinic_list
    FROM patient_doctor_relationships pdr
    JOIN clinics c ON pdr.clinic_id = c.id
    WHERE pdr.doctor_id = p_doctor_id
    AND pdr.is_active = TRUE
    GROUP BY v_doctor_name, v_specialty;
    -- Log the access
    RAISE NOTICE 'Doctor summary accessed for doctor: % (ID: %)', v_doctor_name, p_doctor_id;
END;
$function$
```

##### Procedure: get_patient_care_team

> **AI Analysis:** This procedure retrieves a detailed list of a patient's current care team, including all active doctors, their specialties, and their associated clinics. Its business purpose is to provide a consolidated, up-to-date report of a patient's healthcare providers and their contact information for reference by staff, clinicians, or the patient themselves.
This is a data retrieval and reporting operation.
The procedure acts as a key function for patient information systems, enabling care coordination by clearly outlining all active relationships between a patient and their doctors. The filtering for active relationships and the audit log suggest it's a critical component for displaying current, sensitive patient data in a regulated healthcare application.

**Definition:**
```sql
CREATE OR REPLACE
FUNCTION healthcare_test.get_patient_care_team(p_patient_id integer) RETURNS table(patient_name text, doctor_name text, doctor_specialty CHARACTER varying, clinic_name CHARACTER varying, relationship_type CHARACTER varying, doctor_phone CHARACTER varying, clinic_phone CHARACTER varying, clinic_address text, relationship_start timestamp WITHOUT TIME ZONE) LANGUAGE PLPGSQL AS $function$
BEGIN
    RETURN QUERY
    SELECT
        CONCAT(p.first_name, ' ', p.last_name) as patient_name,
        CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
        d.specialty as doctor_specialty,
        c.name as clinic_name,
        pdr.relationship_type,
        d.phone as doctor_phone,
        c.phone as clinic_phone,
        c.address as clinic_address,
        pdr.started_at as relationship_start
    FROM patients p
    JOIN patient_doctor_relationships pdr ON p.id = pdr.patient_id
    JOIN doctors d ON pdr.doctor_id = d.id
    JOIN clinics c ON pdr.clinic_id = c.id
    WHERE p.id = p_patient_id
    AND pdr.is_active = TRUE
    AND d.is_active = TRUE
    ORDER BY pdr.started_at DESC;
    -- Log the access for audit purposes
    RAISE NOTICE 'Patient care team accessed for patient ID: %', p_patient_id;
END;
$function$
```

##### Procedure: manage_clinic_capacity

> **AI Analysis:** This procedure automatically monitors and validates a clinic's operational capacity in response to changes in patient or doctor assignments. Its business purpose is to alert administrators when a clinic's patient load exceeds a defined threshold, helping to manage resources and maintain service quality.
This is a business rule validation and operational monitoring procedure.
It serves as an automated backend process to enforce capacity-related business rules, providing real-time alerts to support clinic resource management and prevent overloading facilities.

**Definition:**
```sql
CREATE OR REPLACE
FUNCTION healthcare_test.manage_clinic_capacity() RETURNS TRIGGER LANGUAGE PLPGSQL AS $function$
DECLARE
    patient_count INTEGER;
    doctor_count INTEGER;
    target_clinic_id INTEGER;
BEGIN
    -- Determine which clinic to check based on operation
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        target_clinic_id = NEW.clinic_id;
    ELSE
        target_clinic_id = OLD.clinic_id;
    END IF;
    -- Calculate current metrics for the clinic
    SELECT COUNT(*) INTO patient_count
    FROM patient_doctor_relationships
    WHERE clinic_id = target_clinic_id AND is_active = TRUE;
    SELECT COUNT(*) INTO doctor_count
    FROM doctor_clinic_assignments
    WHERE clinic_id = target_clinic_id AND is_active = TRUE;
    -- Log capacity information
    RAISE NOTICE 'Clinic ID % now has % active patients and % active doctors',
        target_clinic_id, patient_count, doctor_count;
    -- Could implement capacity limits here
    IF patient_count > 100 THEN
        RAISE WARNING 'Clinic ID % approaching capacity with % patients',
            target_clinic_id, patient_count;
    END IF;
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$function$
```

##### Procedure: patient_audit_log

> **AI Analysis:** This procedure functions as an automated audit log, recording when sensitive patient information like name, date of birth, or medical record number is modified or when a patient record is deleted. Its business purpose is to enforce data governance and support security and regulatory compliance by creating a trail of changes to critical patient data.
Data Auditing
The procedure plays a crucial role in the application's security and compliance framework. It automatically enforces the business rule that all changes to protected patient information must be tracked, providing accountability and a record for potential security investigations or compliance audits.

**Definition:**
```sql
CREATE OR REPLACE
FUNCTION healthcare_test.patient_audit_log() RETURNS TRIGGER LANGUAGE PLPGSQL AS $function$
BEGIN
    -- Log sensitive patient data changes
    IF TG_OP = 'UPDATE' THEN
        -- Check if sensitive fields changed
        IF OLD.first_name != NEW.first_name OR
           OLD.last_name != NEW.last_name OR
           OLD.date_of_birth != NEW.date_of_birth OR
           COALESCE(OLD.medical_record_number, '') != COALESCE(NEW.medical_record_number, '') THEN
            -- In a real system, this would log to an audit table
            RAISE NOTICE 'Patient % % (ID: %) sensitive data modified by user %',
                OLD.first_name, OLD.last_name, OLD.id, current_user;
        END IF;
    END IF;
    IF TG_OP = 'DELETE' THEN
        RAISE NOTICE 'Patient % % (ID: %) deleted by user %',
            OLD.first_name, OLD.last_name, OLD.id, current_user;
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$function$
```

##### Procedure: update_modified_at_column

> **AI Analysis:** This procedure automatically updates a record's 'last modified' timestamp whenever a change is made to that record. Its business purpose is to maintain an accurate audit trail for data changes, which is essential for data integrity, compliance, and tracking the history of modifications to entities like patients, doctors, or clinics.
Data maintenance and auditing
This procedure enforces a fundamental data governance rule by ensuring all updates to key business records are timestamped, providing a reliable history of data modifications without requiring manual intervention from an application or user.

**Definition:**
```sql
CREATE OR REPLACE
FUNCTION healthcare_test.update_modified_at_column() RETURNS TRIGGER LANGUAGE PLPGSQL AS $function$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$function$
```

##### Procedure: validate_doctor_license

> **AI Analysis:** This procedure validates doctor credentialing information when a doctor's record is created or updated. It enforces business rules by checking that the medical license number conforms to a required format, ensuring data integrity and compliance for doctor records within the system.

Data validation

This procedure acts as an automated gatekeeper in the doctor onboarding or information management process. It enforces critical business rules at the database level to maintain the quality and accuracy of provider data.

**Definition:**
```sql
CREATE OR REPLACE
FUNCTION healthcare_test.validate_doctor_license() RETURNS TRIGGER LANGUAGE PLPGSQL AS $function$
BEGIN
    -- Validate license number format (simple example)
    IF NEW.license_number !~ '^[A-Z]{2}[0-9]{6}$' THEN
        RAISE EXCEPTION 'Invalid license number format. Expected: 2 letters + 6 digits (e.g., MD123456)';
    END IF;
    -- Validate specialty combinations
    IF NEW.specialty = 'Pediatrics' AND NEW.license_number NOT LIKE 'PD%' THEN
        -- In real system, might have specific license prefixes per specialty
        NULL; -- Allow for now, just an example
    END IF;
    RETURN NEW;
END;
$function$
```

## Relationships

Found 5 foreign key relationships:
doctor_clinic_assignments.clinic_id → clinics.id
doctor_clinic_assignments.doctor_id → doctors.id
patient_doctor_relationships.clinic_id → clinics.id
patient_doctor_relationships.doctor_id → doctors.id
patient_doctor_relationships.patient_id → patients.id

| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| doctor\_clinic\_assignments | clinic\_id | clinics | id | doctor\_clinic\_assignments\_clinic\_id\_fkey |  |  | one\_to\_many |
| doctor\_clinic\_assignments | doctor\_id | doctors | id | doctor\_clinic\_assignments\_doctor\_id\_fkey |  |  | one\_to\_many |
| patient\_doctor\_relationships | clinic\_id | clinics | id | patient\_doctor\_relationships\_clinic\_id\_fkey |  |  | one\_to\_many |
| patient\_doctor\_relationships | doctor\_id | doctors | id | patient\_doctor\_relationships\_doctor\_id\_fkey |  |  | one\_to\_many |
| patient\_doctor\_relationships | patient\_id | patients | id | patient\_doctor\_relationships\_patient\_id\_fkey |  |  | one\_to\_many |

## Indexes

Found 9 indexes across all tables:
doctors.doctors_license_number_key (unique)
doctors.idx_doctors_license (index)
doctors.idx_doctors_specialty (index)
patients.idx_patients_dob (index)
patients.idx_patients_mrn (index)
patients.patients_medical_record_number_key (unique)
doctor_clinic_assignments.doctor_clinic_assignments_doctor_id_clinic_id_start_date_key (unique)
doctor_clinic_assignments.idx_doctor_clinic_active (index)
patient_doctor_relationships.idx_patient_doctor_active (index)

| Index Type | Count |
| --- | --- |
| index | 6 |
| unique | 3 |

| Key | Value |
| --- | ----- |
| Unique Indexes | 3 |
| Primary Indexes | 0 |
| Clustered Indexes | 0 |
| Estimated Index Storage | 0.00 B |

## Performance Insights

- Database has 5 relationships indicating good normalization
- Found 9 indexes for query optimization
- Average 9.6 columns per table

## Security Considerations

_No security considerations were provided._

## Recommendations

- [ ] Review tables with no indexes for potential performance improvements
- [ ] Consider adding descriptions to tables and columns for better documentation
- [ ] Monitor foreign key constraint performance on large tables

## Table Documentation

### doctors

Table: doctors
Schema: healthcare_test
Type: table

AI Analysis:
This table is a master directory of physicians, storing their core demographic, contact, and professional credential information for a healthcare organization. It serves as the central record for each doctor, tracking details like their medical specialty, unique license number, and employment status. This table is referenced by other parts of the system to manage both administrative and clinical relationships, such as assigning doctors to specific clinic locations and linking them to the patients under their care. The presence of an `is_active` flag and `hire_date` suggests the table is also used for operational and HR purposes to manage the physician roster.

Relationships:
and is referenced by doctor_clinic_assignments, referenced by patient_doctor_relationships.

Technical Details:
Columns: 11 (id(integer), first_name(char), last_name(char), specialty(char), license_number(char)...)
Primary Keys: id
Foreign Keys: None
Constraints: 1
Indexes: 3
Triggers: 2
Row Count: -1
Size: 81,920 bytes

### clinics

Table: clinics
Schema: healthcare_test
Type: table

AI Analysis:
The `clinics` table is a master list of healthcare facilities, storing their names and contact details. It acts as a foundational reference, allowing the system to associate doctors with the specific clinics they work at and to record the location where a patient's relationship with a doctor is established. This structure is essential for managing staff assignments and patient records across a network of different physical locations.

Relationships:
and is referenced by doctor_clinic_assignments, referenced by patient_doctor_relationships.

Technical Details:
Columns: 7 (id(integer), name(char), address(text), phone(char), email(char)...)
Primary Keys: id
Foreign Keys: None
Constraints: 1
Indexes: 0
Triggers: 1
Row Count: -1
Size: 32,768 bytes

### patients

Table: patients
Schema: healthcare_test
Type: table

AI Analysis:
This table acts as a central patient registry, storing core demographic, contact, and identification information for individuals within a healthcare system. It uses a unique medical record number to identify each person, serving as the master record for patient identity. The table's primary business purpose is to be the authoritative source for patient data, allowing other system components, like the `patient_doctor_relationships` table, to link medical activities and provider assignments to a specific patient.

Relationships:
and is referenced by patient_doctor_relationships.

Technical Details:
Columns: 12 (id(integer), first_name(char), last_name(char), date_of_birth(date), gender(char)...)
Primary Keys: id
Foreign Keys: None
Constraints: 1
Indexes: 3
Triggers: 2
Row Count: -1
Size: 81,920 bytes

### doctor_clinic_assignments

Table: doctor_clinic_assignments
Schema: healthcare_test
Type: table

AI Analysis:
This table tracks the work assignments of doctors to specific clinics, serving as a historical and current record of their professional affiliations. It stores the time period of the assignment, the doctor's specific role at that clinic, and whether the assignment is currently active. This table functions as a bridge between the 'doctors' and 'clinics' tables, managing the business reality that a doctor can work at multiple clinics and a clinic can employ many doctors. The date range and active status fields are crucial for managing scheduling and understanding a doctor's availability and work history across different locations.

Relationships:
This table references clinics, references doctors.

Technical Details:
Columns: 8 (id(integer), doctor_id(integer), clinic_id(integer), start_date(date), end_date(date)...)
Primary Keys: id
Foreign Keys: doctor_id, clinic_id
Constraints: 3
Indexes: 2
Triggers: 1
Row Count: -1
Size: 57,344 bytes

### patient_doctor_relationships

Table: patient_doctor_relationships
Schema: healthcare_test
Type: table

AI Analysis:
This table serves as a central record for managing the professional associations between patients and doctors within a healthcare system. It stores key details for each specific relationship, such as its type (e.g., primary care, specialist), its duration, and its current active status. The table functions as a crucial link between the patients, doctors, and clinics tables, defining exactly which doctor is associated with which patient at a specific clinic, thereby enabling the tracking of care assignments over time. The inclusion of start/end dates and an active status flag highlights its business purpose in maintaining a complete history of patient care relationships for continuity and administrative reporting.

Relationships:
This table references clinics, references doctors, references patients.

Technical Details:
Columns: 10 (id(integer), patient_id(integer), doctor_id(integer), clinic_id(integer), relationship_type(char)...)
Primary Keys: id
Foreign Keys: patient_id, doctor_id, clinic_id
Constraints: 4
Indexes: 1
Triggers: 1
Row Count: -1
Size: 49,152 bytes
