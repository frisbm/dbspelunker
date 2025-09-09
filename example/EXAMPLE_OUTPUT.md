# Database Documentation: database

- Type: `postgresql` · Generated: `2025-09-09 14:41:00`

## Executive Summary

Database Analysis Summary:
- Database: database (postgresql)
- Total Tables: 6
- Total Columns: 51
- Total Constraints: 18
- Total Indexes: 9
- Total Triggers: 3
- Total Relationships: 6
- Schemas Analyzed: 2

This database contains 6 tables with 51 columns across 2 schema(s).
The analysis identified 6 foreign key relationships between tables.

## Database Overview

| Key | Value |
| --- | ----- |
| Name | database |
| Type | postgresql |
| Version |  |
| Total Tables | 6 |
| Total Views | 0 |
| Stored Procedures | 3 |
| Indexes | 9 |
| Triggers | 3 |
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

### Schema: healthcare
| Key | Value |
| --- | ----- |
| Tables | 6 |
| Views | 0 |
| Stored Procedures | 3 |
| Relationships | 6 |

#### Tables

##### Table: healthcare.claim_line
- Type: `table` · Rows: `47` · Size: `64.00 KB`

> This table stores the individual line items that make up a healthcare insurance claim or patient bill. Each row details a specific medical procedure or service rendered, including its official code, description, and the associated charge amount. It links these specific services to a broader patient encounter, effectively itemizing the costs incurred during a single visit or hospital stay for billing and reimbursement purposes.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare.claim\_line\_id\_seq'::regclass) | Yes | No |  |  |
| encounter\_id | integer | No |  | No | Yes | fk→encounter(id) |  |
| procedure\_code | varchar | No |  | No | No | len=10 |  |
| procedure\_description | text | No |  | No | No |  |  |
| charge\_amount | decimal | No |  | No | No | p=10, s=2 |  |
| service\_date | date | No |  | No | No |  |  |
| modifier | varchar | Yes |  | No | No | len=5 |  |
| created\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| claim\_line\_pkey | primary\_key | id |  |  |
| claim\_line\_encounter\_id\_fkey | foreign\_key | encounter\_id | ref encounter(id); on\_delete=CASCADE |  |
| claim\_line\_charge\_amount\_check | check | charge\_amount | check=(charge\_amount >= (0)::numeric) |  |

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| idx\_claim\_line\_code | index | procedure\_code | No | No | No |  |  |
| idx\_claim\_line\_encounter | index | encounter\_id | No | No | No |  |  |

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claim\_line | encounter\_id | encounter | id | claim\_line\_encounter\_id\_fkey | CASCADE |  | many\_to\_one |

###### Relationship Summary
This table references encounter.

##### Table: healthcare.encounter
- Type: `table` · Rows: `29` · Size: `80.00 KB`

> This table stores records of patient encounters, which are specific interactions between a patient and a healthcare provider at a medical facility. It captures essential information about each visit, such as the date, type of visit (e.g., check-up, emergency), and its current status. This table acts as a central transactional record, linking patients to the providers who treated them and the organizations where the care was delivered. Each encounter serves as the basis for subsequent billing activities, as indicated by its connection to the claim line table. The structure allows the business to track patient visit history, manage provider schedules, and initiate the revenue cycle for services rendered.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare.encounter\_id\_seq'::regclass) | Yes | No |  |  |
| patient\_id | integer | No |  | No | Yes | fk→patient(id) |  |
| provider\_id | integer | No |  | No | Yes | fk→provider(id) |  |
| organization\_id | integer | No |  | No | Yes | fk→organization(id) |  |
| encounter\_date | date | No | CURRENT\_DATE | No | No |  |  |
| encounter\_type | varchar | Yes |  | No | No | len=50 |  |
| status | varchar | Yes |  | No | No | len=20 |  |
| notes | text | Yes |  | No | No |  |  |
| created\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| encounter\_pkey | primary\_key | id |  |  |
| encounter\_organization\_id\_fkey | foreign\_key | organization\_id | ref organization(id); on\_delete=RESTRICT |  |
| encounter\_patient\_id\_fkey | foreign\_key | patient\_id | ref patient(id); on\_delete=CASCADE |  |
| encounter\_provider\_id\_fkey | foreign\_key | provider\_id | ref provider(id); on\_delete=RESTRICT |  |
| encounter\_encounter\_type\_check | check | encounter\_type | check=((encounter\_type)::text = ANY ((ARRAY['inpatient'::character varying, 'outpatient'::character varying, 'emergency'::character varying, 'preventive'::character varying])::text[])) |  |
| encounter\_status\_check | check | status | check=((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in\_progress'::character varying, 'completed'::character varying, 'cancelled'::character varying])::text[])) |  |

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| idx\_encounter\_date | index | encounter\_date | No | No | No |  |  |
| idx\_encounter\_patient | index | patient\_id | No | No | No |  |  |
| idx\_encounter\_provider | index | provider\_id | No | No | No |  |  |

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claim\_line | encounter\_id | encounter | id | claim\_line\_encounter\_id\_fkey | CASCADE |  | many\_to\_one |
| encounter | organization\_id | organization | id | encounter\_organization\_id\_fkey | RESTRICT |  | many\_to\_one |
| encounter | patient\_id | patient | id | encounter\_patient\_id\_fkey | CASCADE |  | many\_to\_one |
| encounter | provider\_id | provider | id | encounter\_provider\_id\_fkey | RESTRICT |  | many\_to\_one |

###### Relationship Summary
This table references organization, references patient, references provider. and is referenced by claim_line.

##### Table: healthcare.organization
- Type: `table` · Rows: `20` · Size: `32.00 KB`

> This table serves as a master directory of healthcare organizations, such as hospitals, clinics, or insurance companies, storing their core contact and identification details. It is used to associate patient encounters with the specific facility where care was delivered and to link healthcare providers to the organizations they are affiliated with. The presence of a `type` and `tax_id` suggests the data is used to differentiate between various kinds of facilities for administrative, billing, and reporting functions.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare.organization\_id\_seq'::regclass) | Yes | No |  |  |
| name | varchar | No |  | No | No | len=100 |  |
| type | varchar | Yes |  | No | No | len=50 |  |
| address | text | Yes |  | No | No |  |  |
| phone | varchar | Yes |  | No | No | len=20 |  |
| website | varchar | Yes |  | No | No | len=100 |  |
| tax\_id | varchar | Yes |  | No | No | len=20 |  |
| created\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |
| updated\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| organization\_pkey | primary\_key | id |  |  |
| organization\_type\_check | check | type | check=((type)::text = ANY ((ARRAY['hospital'::character varying, 'clinic'::character varying, 'lab'::character varying, 'pharmacy'::character varying, 'insurance'::character varying])::text[])) |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| organization\_update\_timestamp | before | update | Yes | Trigger function: update\_timestamp |

###### Trigger: organization_update_timestamp

> **AI Analysis:** This trigger automatically updates a timestamp to the current time whenever an organization's record is modified. It exists to maintain a reliable and automated audit trail, ensuring there is always an accurate record of when an organization's data was last changed.

Business Rule: The system must automatically record the date and time of the last modification for any given organization's record.

Implications: This mechanism is crucial for data governance and auditing, providing a consistent and tamper-proof way to track data currency without relying on application logic. The performance impact is negligible as it is a highly efficient, standard database practice.

**Definition:**
```sql
CREATE TRIGGER organization_update_timestamp
BEFORE
  UPDATE
    ON healthcare.organization
   FOR EACH ROW EXECUTE
FUNCTION healthcare.update_timestamp()
```

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| encounter | organization\_id | organization | id | encounter\_organization\_id\_fkey | RESTRICT |  | many\_to\_one |
| provider\_organization | organization\_id | organization | id | provider\_organization\_organization\_id\_fkey | CASCADE |  | many\_to\_many |

###### Relationship Summary
and is referenced by encounter, referenced by provider_organization.

##### Table: healthcare.patient
- Type: `table` · Rows: `22` · Size: `64.00 KB`

> This table acts as a master patient registry, storing fundamental demographic, contact, and insurance information for individuals receiving healthcare services. It serves as the central record for identifying patients within the system. This table provides the "who" for clinical events, linking each unique patient to their specific medical encounters, such as appointments or hospital visits, which are detailed in the related `encounter` table.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare.patient\_id\_seq'::regclass) | Yes | No |  |  |
| first\_name | varchar | No |  | No | No | len=50 |  |
| last\_name | varchar | No |  | No | No | len=50 |  |
| date\_of\_birth | date | No |  | No | No |  |  |
| gender | char | Yes |  | No | No | len=1 |  |
| address | text | Yes |  | No | No |  |  |
| phone | varchar | Yes |  | No | No | len=20 |  |
| email | varchar | Yes |  | No | No | len=100 |  |
| insurance\_id | varchar | Yes |  | No | No | len=50 |  |
| created\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |
| updated\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| patient\_pkey | primary\_key | id |  |  |
| patient\_gender\_check | check | gender | check=(gender = ANY (ARRAY['M'::bpchar, 'F'::bpchar, 'O'::bpchar])) |  |

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| idx\_patient\_dob | index | date\_of\_birth | No | No | No |  |  |
| idx\_patient\_last\_name | index | last\_name | No | No | No |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| patient\_update\_timestamp | before | update | Yes | Trigger function: update\_timestamp |

###### Trigger: patient_update_timestamp

> **AI Analysis:** This trigger automatically updates a timestamp on a patient's record whenever their information is changed. Its primary business purpose is to maintain an accurate and reliable audit trail, ensuring that the system always knows the exact time a patient's data was last modified. This supports data governance, compliance requirements, and troubleshooting by providing a clear history of data changes.

Business Rule: When any patient data is modified, the system must automatically record the timestamp of the change.

Implications: This trigger is crucial for data auditing and integrity, providing a reliable "last modified" date for every patient record. The performance impact is negligible for single-row updates but could become a minor factor in very large bulk update operations.

**Definition:**
```sql
CREATE TRIGGER patient_update_timestamp
BEFORE
  UPDATE
    ON healthcare.patient
   FOR EACH ROW EXECUTE
FUNCTION healthcare.update_timestamp()
```

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| encounter | patient\_id | patient | id | encounter\_patient\_id\_fkey | CASCADE |  | many\_to\_one |

###### Relationship Summary
and is referenced by encounter.

##### Table: healthcare.provider
- Type: `table` · Rows: `22` · Size: `64.00 KB`

> This table is a master directory of healthcare providers, storing their essential identification, contact, and professional details like medical specialty and National Provider Identifier (NPI). It serves as a core reference table, linking individual providers to specific patient encounters and associating them with the larger healthcare organizations they may belong to. The structure supports key business functions such as searching for providers by specialty and managing the network of clinicians and facilities involved in patient care.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare.provider\_id\_seq'::regclass) | Yes | No |  |  |
| name | varchar | No |  | No | No | len=100 |  |
| provider\_type | varchar | Yes |  | No | No | len=20 |  |
| specialty | varchar | Yes |  | No | No | len=50 |  |
| npi | varchar | Yes |  | No | No | len=10 |  |
| address | text | Yes |  | No | No |  |  |
| phone | varchar | Yes |  | No | No | len=20 |  |
| email | varchar | Yes |  | No | No | len=100 |  |
| created\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |
| updated\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| provider\_pkey | primary\_key | id |  |  |
| provider\_provider\_type\_check | check | provider\_type | check=((provider\_type)::text = ANY ((ARRAY['practitioner'::character varying, 'facility'::character varying])::text[])) |  |

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| idx\_provider\_specialty | index | specialty | No | No | No |  |  |
| provider\_npi\_key | unique | npi | Yes | No | No |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| provider\_update\_timestamp | before | update | Yes | Trigger function: update\_timestamp |

###### Trigger: provider_update_timestamp

> **AI Analysis:** This trigger automatically updates the `updated_at` timestamp to the current time whenever any information for a provider is changed. Its purpose is to maintain an accurate and reliable audit trail, making it easy to see when a provider's record was last modified. This is essential for data governance, tracking data freshness, and supporting compliance processes.

The business rule implemented is: "Every time a provider's record is modified, the 'last updated' timestamp must be automatically set to the current date and time."

This trigger improves data consistency by ensuring the `updated_at` field is always accurate without relying on the application to set it. It provides a simple, reliable audit mechanism for tracking changes to provider data with a negligible performance impact.

**Definition:**
```sql
CREATE TRIGGER provider_update_timestamp
BEFORE
  UPDATE
    ON healthcare.provider
   FOR EACH ROW EXECUTE
FUNCTION healthcare.update_timestamp()
```

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| encounter | provider\_id | provider | id | encounter\_provider\_id\_fkey | RESTRICT |  | many\_to\_one |
| provider\_organization | provider\_id | provider | id | provider\_organization\_provider\_id\_fkey | CASCADE |  | many\_to\_many |

###### Relationship Summary
and is referenced by encounter, referenced by provider_organization.

##### Table: healthcare.provider_organization
- Type: `table` · Rows: `28` · Size: `24.00 KB`

> This table serves as a junction or linking table to document the professional relationship between individual healthcare providers and healthcare organizations. It establishes a many-to-many relationship, allowing a single provider to be associated with multiple organizations and an organization to have many affiliated providers. The inclusion of `role` and `start_date` indicates its business purpose is to track a provider's specific job function and tenure within each organization, likely for credentialing, directory, and network management purposes.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| provider\_id | integer | No |  | Yes | Yes | fk→provider(id) |  |
| organization\_id | integer | No |  | Yes | Yes | fk→organization(id) |  |
| role | varchar | Yes |  | No | No | len=50 |  |
| start\_date | date | Yes | CURRENT\_DATE | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| provider\_organization\_pkey | primary\_key | provider\_id, organization\_id |  |  |
| provider\_organization\_organization\_id\_fkey | foreign\_key | organization\_id | ref organization(id); on\_delete=CASCADE |  |
| provider\_organization\_provider\_id\_fkey | foreign\_key | provider\_id | ref provider(id); on\_delete=CASCADE |  |

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| provider\_organization | organization\_id | organization | id | provider\_organization\_organization\_id\_fkey | CASCADE |  | many\_to\_many |
| provider\_organization | provider\_id | provider | id | provider\_organization\_provider\_id\_fkey | CASCADE |  | many\_to\_many |

###### Relationship Summary
This table references organization, references provider.

#### Stored Procedures

| Name | Returns | Language | Deterministic | Created | Modified |
| --- | --- | --- | --- | --- | --- |
| get\_patient\_summary | record | plpgsql | No |  |  |
| get\_provider\_statistics | record | plpgsql | No |  |  |
| update\_timestamp | trigger | plpgsql | No |  |  |

##### Procedure: get_patient_summary

> **AI Analysis:** This procedure retrieves a consolidated summary of a specific patient's clinical and financial history by calculating their total number of encounters, last visit date, and the sum of all associated charges. Its purpose is to provide a quick, high-level overview of a patient's activity, likely for display on a dashboard or patient lookup screen.
Data aggregation and reporting
This procedure serves as a key data source for a "patient-at-a-glance" feature within an application. It supports administrative, clinical, and billing workflows by providing a quick reference to a patient's engagement and financial status with the healthcare provider.

**Definition:**
```sql
CREATE OR REPLACE
FUNCTION healthcare.get_patient_summary(p_patient_id integer) RETURNS table(patient_name text, patient_dob date, total_encounters integer, last_encounter_date date, total_charges numeric) LANGUAGE PLPGSQL AS $function$
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
$function$
```

##### Procedure: get_provider_statistics

> **AI Analysis:** This procedure calculates key performance metrics for a specific healthcare provider based on their ID. It summarizes a provider's total patient encounters, the total revenue generated from associated claims, and the resulting average charge per encounter. This function serves as a business calculation and reporting tool, likely used in an administrative dashboard to support provider performance analysis, financial tracking, and operational oversight.

**Definition:**
```sql
CREATE OR REPLACE
FUNCTION healthcare.get_provider_statistics(p_provider_id integer) RETURNS table(provider_name text, specialty text, total_encounters integer, total_revenue numeric, avg_charge_per_encounter numeric) LANGUAGE PLPGSQL AS $function$
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
$function$
```

##### Procedure: update_timestamp

> **AI Analysis:** This procedure automatically updates a record's timestamp to the current time whenever a modification occurs. Its business purpose is to maintain a reliable audit trail for data changes within the healthcare system, ensuring data integrity and supporting compliance requirements.
Data maintenance and auditing
The procedure enforces a critical data governance policy by automatically time-stamping any change to a record. This provides an essential audit log for tracking modifications to sensitive information like patient, encounter, or claim data, which is fundamental for historical analysis and regulatory compliance.

**Definition:**
```sql
CREATE OR REPLACE
FUNCTION healthcare.update_timestamp() RETURNS TRIGGER LANGUAGE PLPGSQL AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
```

### Schema: public
| Key | Value |
| --- | ----- |
| Tables | 0 |
| Views | 0 |
| Stored Procedures | 0 |
| Relationships | 0 |

## Relationships

Found 6 foreign key relationships:
claim_line.encounter_id → encounter.id
encounter.organization_id → organization.id
encounter.patient_id → patient.id
encounter.provider_id → provider.id
provider_organization.organization_id → organization.id
provider_organization.provider_id → provider.id

| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claim\_line | encounter\_id | encounter | id | claim\_line\_encounter\_id\_fkey | CASCADE |  | many\_to\_one |
| encounter | organization\_id | organization | id | encounter\_organization\_id\_fkey | RESTRICT |  | many\_to\_one |
| encounter | patient\_id | patient | id | encounter\_patient\_id\_fkey | CASCADE |  | many\_to\_one |
| encounter | provider\_id | provider | id | encounter\_provider\_id\_fkey | RESTRICT |  | many\_to\_one |
| provider\_organization | organization\_id | organization | id | provider\_organization\_organization\_id\_fkey | CASCADE |  | many\_to\_many |
| provider\_organization | provider\_id | provider | id | provider\_organization\_provider\_id\_fkey | CASCADE |  | many\_to\_many |

## Indexes

Found 9 indexes across all tables:
claim_line.idx_claim_line_code (index)
claim_line.idx_claim_line_encounter (index)
encounter.idx_encounter_date (index)
encounter.idx_encounter_patient (index)
encounter.idx_encounter_provider (index)
patient.idx_patient_dob (index)
patient.idx_patient_last_name (index)
provider.idx_provider_specialty (index)
provider.provider_npi_key (unique)

| Index Type | Count |
| --- | --- |
| index | 8 |
| unique | 1 |

| Key | Value |
| --- | ----- |
| Unique Indexes | 1 |
| Primary Indexes | 0 |
| Clustered Indexes | 0 |
| Estimated Index Storage | 0.00 B |

## Performance Insights

- Database has 6 relationships indicating good normalization
- Found 9 indexes for query optimization
- Average 8.5 columns per table

## Security Considerations

_No security considerations were provided._

## Recommendations

- [ ] Review tables with no indexes for potential performance improvements
- [ ] Consider adding descriptions to tables and columns for better documentation
- [ ] Monitor foreign key constraint performance on large tables

## Table Documentation

### claim_line

Table: claim_line
Schema: healthcare
Type: table

AI Analysis:
This table stores the individual line items that make up a healthcare insurance claim or patient bill. Each row details a specific medical procedure or service rendered, including its official code, description, and the associated charge amount. It links these specific services to a broader patient encounter, effectively itemizing the costs incurred during a single visit or hospital stay for billing and reimbursement purposes.

Relationships:
This table references encounter.

Technical Details:
Columns: 8 (id(integer), encounter_id(integer), procedure_code(varchar), procedure_description(text), charge_amount(decimal)...)
Primary Keys: id
Foreign Keys: encounter_id
Constraints: 3
Indexes: 2
Triggers: 0
Row Count: 47
Size: 65,536 bytes

### encounter

Table: encounter
Schema: healthcare
Type: table

AI Analysis:
This table stores records of patient encounters, which are specific interactions between a patient and a healthcare provider at a medical facility. It captures essential information about each visit, such as the date, type of visit (e.g., check-up, emergency), and its current status. This table acts as a central transactional record, linking patients to the providers who treated them and the organizations where the care was delivered. Each encounter serves as the basis for subsequent billing activities, as indicated by its connection to the claim line table. The structure allows the business to track patient visit history, manage provider schedules, and initiate the revenue cycle for services rendered.

Relationships:
This table references organization, references patient, references provider. and is referenced by claim_line.

Technical Details:
Columns: 9 (id(integer), patient_id(integer), provider_id(integer), organization_id(integer), encounter_date(date)...)
Primary Keys: id
Foreign Keys: patient_id, provider_id, organization_id
Constraints: 6
Indexes: 3
Triggers: 0
Row Count: 29
Size: 81,920 bytes

### organization

Table: organization
Schema: healthcare
Type: table

AI Analysis:
This table serves as a master directory of healthcare organizations, such as hospitals, clinics, or insurance companies, storing their core contact and identification details. It is used to associate patient encounters with the specific facility where care was delivered and to link healthcare providers to the organizations they are affiliated with. The presence of a `type` and `tax_id` suggests the data is used to differentiate between various kinds of facilities for administrative, billing, and reporting functions.

Relationships:
and is referenced by encounter, referenced by provider_organization.

Technical Details:
Columns: 9 (id(integer), name(varchar), type(varchar), address(text), phone(varchar)...)
Primary Keys: id
Foreign Keys: None
Constraints: 2
Indexes: 0
Triggers: 1
Row Count: 20
Size: 32,768 bytes

### patient

Table: patient
Schema: healthcare
Type: table

AI Analysis:
This table acts as a master patient registry, storing fundamental demographic, contact, and insurance information for individuals receiving healthcare services. It serves as the central record for identifying patients within the system. This table provides the "who" for clinical events, linking each unique patient to their specific medical encounters, such as appointments or hospital visits, which are detailed in the related `encounter` table.

Relationships:
and is referenced by encounter.

Technical Details:
Columns: 11 (id(integer), first_name(varchar), last_name(varchar), date_of_birth(date), gender(char)...)
Primary Keys: id
Foreign Keys: None
Constraints: 2
Indexes: 2
Triggers: 1
Row Count: 22
Size: 65,536 bytes

### provider

Table: provider
Schema: healthcare
Type: table

AI Analysis:
This table is a master directory of healthcare providers, storing their essential identification, contact, and professional details like medical specialty and National Provider Identifier (NPI). It serves as a core reference table, linking individual providers to specific patient encounters and associating them with the larger healthcare organizations they may belong to. The structure supports key business functions such as searching for providers by specialty and managing the network of clinicians and facilities involved in patient care.

Relationships:
and is referenced by encounter, referenced by provider_organization.

Technical Details:
Columns: 10 (id(integer), name(varchar), provider_type(varchar), specialty(varchar), npi(varchar)...)
Primary Keys: id
Foreign Keys: None
Constraints: 2
Indexes: 2
Triggers: 1
Row Count: 22
Size: 65,536 bytes

### provider_organization

Table: provider_organization
Schema: healthcare
Type: table

AI Analysis:
This table serves as a junction or linking table to document the professional relationship between individual healthcare providers and healthcare organizations. It establishes a many-to-many relationship, allowing a single provider to be associated with multiple organizations and an organization to have many affiliated providers. The inclusion of `role` and `start_date` indicates its business purpose is to track a provider's specific job function and tenure within each organization, likely for credentialing, directory, and network management purposes.

Relationships:
This table references organization, references provider.

Technical Details:
Columns: 4 (provider_id(integer), organization_id(integer), role(varchar), start_date(date))
Primary Keys: provider_id, organization_id
Foreign Keys: provider_id, organization_id
Constraints: 3
Indexes: 0
Triggers: 0
Row Count: 28
Size: 24,576 bytes
