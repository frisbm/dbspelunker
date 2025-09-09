# Database Documentation: database

- Type: `postgresql` · Generated: `2025-09-09 14:28:54`

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

> This table stores the individual line items for a healthcare claim, detailing each specific service or procedure provided to a patient. Each record captures the procedure performed, its associated charge, and the date of service, which is essential for itemizing charges for insurance billing. The table links these individual services back to a specific patient visit or encounter, providing a detailed breakdown of a bill.

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
| claim\_line | encounter\_id | encounter | id | claim\_line\_encounter\_id\_fkey | CASCADE |  | one\_to\_many |

###### Relationship Summary
This table references encounter.

##### Table: healthcare.encounter
- Type: `table` · Rows: `29` · Size: `80.00 KB`

> This table stores records of patient visits or interactions with healthcare providers, often called "encounters." It captures who was seen (patient), who provided the service (provider), where it happened (organization), and when (encounter_date). This table acts as a central transactional record, linking patients to the specific care they receive.

Each encounter is associated with a patient, a provider, and a healthcare organization. Importantly, information from an encounter is used to generate `claim_line` records, indicating that these visits are the basis for medical billing and insurance claims.

The structure suggests this table is fundamental to both clinical and administrative workflows. It not only documents the history of patient care but also directly feeds the revenue cycle by providing the necessary details for billing for services rendered.

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
| claim\_line | encounter\_id | encounter | id | claim\_line\_encounter\_id\_fkey | CASCADE |  | one\_to\_many |
| encounter | organization\_id | organization | id | encounter\_organization\_id\_fkey | RESTRICT |  | one\_to\_many |
| encounter | patient\_id | patient | id | encounter\_patient\_id\_fkey | CASCADE |  | one\_to\_many |
| encounter | provider\_id | provider | id | encounter\_provider\_id\_fkey | RESTRICT |  | one\_to\_many |

###### Relationship Summary
This table references organization, references patient, references provider. and is referenced by claim_line.

##### Table: healthcare.organization
- Type: `table` · Rows: `20` · Size: `32.00 KB`

> This table acts as a central directory for healthcare organizations, such as hospitals, clinics, or labs. It stores essential business details like names, contact information, and tax IDs for these entities.

The table provides context to other parts of the system; for example, it links to patient `encounter` records to identify the facility where care was provided and connects to providers to show their organizational affiliations. Its purpose is to be a single source of truth for organization data, ensuring consistency for activities like patient scheduling, billing, and reporting on provider affiliations.

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

> **AI Analysis:** This trigger automatically updates the `updated_at` timestamp field to the current time whenever any information for an organization is changed. This ensures a reliable and automated audit trail for data modifications, providing a clear history of when each record was last updated.

Business Rule: The "last modified" timestamp for an organization's record must always reflect the time of the most recent change.

Implications: This trigger is crucial for data governance and auditing, as it guarantees a consistent and accurate timestamp for all updates. The performance impact is negligible as it's a very lightweight and common database operation.

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
| encounter | organization\_id | organization | id | encounter\_organization\_id\_fkey | RESTRICT |  | one\_to\_many |
| provider\_organization | organization\_id | organization | id | provider\_organization\_organization\_id\_fkey | CASCADE |  | one\_to\_many |

###### Relationship Summary
and is referenced by encounter, referenced by provider_organization.

##### Table: healthcare.patient
- Type: `table` · Rows: `22` · Size: `64.00 KB`

> This table acts as a central patient registry, storing core demographic, contact, and insurance information for individuals receiving care. It functions as a master data table, providing a unique and authoritative record for each patient within the healthcare system. This patient record is the foundation for tracking a patient's complete history, as it links to related records such as clinical encounters or visits. The presence of an insurance identifier and indexes on last name and date of birth suggests the table is optimized for key administrative and clinical workflows, including patient look-up, registration, and billing.

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

> **AI Analysis:** This trigger automatically updates a timestamp on a patient's record each time it is modified, creating a reliable audit log. This provides the exact time of the last change for any patient's data, which is essential for data governance, compliance tracking, and troubleshooting.

Business Rule: The system must automatically record the date and time of the last modification for every patient record.

Implications: This enforces a consistent and non-repudiable audit trail for patient data modifications, which is critical for compliance and data integrity. The performance impact is generally negligible but could become a factor in extremely high-volume update scenarios.

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
| encounter | patient\_id | patient | id | encounter\_patient\_id\_fkey | CASCADE |  | one\_to\_many |

###### Relationship Summary
and is referenced by encounter.

##### Table: healthcare.provider
- Type: `table` · Rows: `22` · Size: `64.00 KB`

> This table is a master directory of healthcare providers, storing their identifying information, contact details, and professional classifications like specialty. It serves as a central reference list for uniquely identifying each practitioner or facility, as confirmed by the unique National Provider Identifier (NPI) field. This provider information is used to link a specific provider to a patient encounter (such as an appointment) and to associate them with the larger healthcare organizations they work for.

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

> **AI Analysis:** This trigger automatically updates the `updated_at` timestamp to the current time whenever a provider's record is modified. Its purpose is to maintain an accurate and reliable audit trail, ensuring the system always knows precisely when a provider's information was last changed. This is crucial for data governance and tracking the currency of provider data.

Business Rule: The trigger enforces the rule that any modification to a provider's record must be timestamped with the exact time of the change.

Implications: This automation guarantees data consistency for the `updated_at` field, providing a reliable audit log for when provider data is altered. The performance impact is negligible as this is a standard, lightweight database operation.

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
| encounter | provider\_id | provider | id | encounter\_provider\_id\_fkey | RESTRICT |  | one\_to\_many |
| provider\_organization | provider\_id | provider | id | provider\_organization\_provider\_id\_fkey | CASCADE |  | one\_to\_many |

###### Relationship Summary
and is referenced by encounter, referenced by provider_organization.

##### Table: healthcare.provider_organization
- Type: `table` · Rows: `28` · Size: `24.00 KB`

> This table serves as a junction or linking table that establishes the relationship between individual healthcare providers and the organizations they work for or are affiliated with. It records the specific details of this affiliation, such as the provider's role (e.g., Cardiologist, Surgeon) and the date their relationship with the organization began. This structure allows a single provider to be associated with multiple organizations and an organization to have many affiliated providers, effectively managing their professional network and employment history.

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
| provider\_organization | organization\_id | organization | id | provider\_organization\_organization\_id\_fkey | CASCADE |  | one\_to\_many |
| provider\_organization | provider\_id | provider | id | provider\_organization\_provider\_id\_fkey | CASCADE |  | one\_to\_many |

###### Relationship Summary
This table references organization, references provider.

#### Stored Procedures

| Name | Returns | Language | Deterministic | Created | Modified |
| --- | --- | --- | --- | --- | --- |
| get\_patient\_summary | record | plpgsql | No |  |  |
| get\_provider\_statistics | record | plpgsql | No |  |  |
| update\_timestamp | trigger | plpgsql | No |  |  |

##### Procedure: get_patient_summary

> **AI Analysis:** This procedure provides a consolidated summary for a specific patient by retrieving their name, date of birth, total number of medical encounters, and the date of their most recent visit. It also calculates the cumulative financial charges from all their past services, offering a quick snapshot of their clinical and billing history. This function is a reporting and business calculation operation. It is likely used to populate a patient dashboard or a "patient-at-a-glance" view in an Electronic Health Record (EHR) or Practice Management System, supporting administrative and clinical workflows like patient check-in or pre-appointment review.

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

> **AI Analysis:** This procedure calculates and summarizes key performance indicators for a single healthcare provider. It aggregates operational and financial data to report on the provider's total number of patient encounters, the total revenue they have generated through billed charges, and their average revenue per encounter. This is a reporting and business calculation operation. The procedure's role is to provide data for provider performance reviews, financial analysis, and operational dashboards, allowing management to assess individual provider productivity and financial impact.

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

> **AI Analysis:** This procedure automatically updates a record's timestamp to the current time whenever a row is modified. Its business purpose is to maintain an accurate audit trail for data changes, ensuring data integrity and providing a history of when records in the healthcare system were last updated.
Data maintenance and auditing.
This function enforces a critical data governance rule by automatically logging the time of any data modification. This supports compliance requirements, change tracking, and provides a reliable history for records such as patient details, encounters, or claims.

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
| claim\_line | encounter\_id | encounter | id | claim\_line\_encounter\_id\_fkey | CASCADE |  | one\_to\_many |
| encounter | organization\_id | organization | id | encounter\_organization\_id\_fkey | RESTRICT |  | one\_to\_many |
| encounter | patient\_id | patient | id | encounter\_patient\_id\_fkey | CASCADE |  | one\_to\_many |
| encounter | provider\_id | provider | id | encounter\_provider\_id\_fkey | RESTRICT |  | one\_to\_many |
| provider\_organization | organization\_id | organization | id | provider\_organization\_organization\_id\_fkey | CASCADE |  | one\_to\_many |
| provider\_organization | provider\_id | provider | id | provider\_organization\_provider\_id\_fkey | CASCADE |  | one\_to\_many |

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
This table stores the individual line items for a healthcare claim, detailing each specific service or procedure provided to a patient. Each record captures the procedure performed, its associated charge, and the date of service, which is essential for itemizing charges for insurance billing. The table links these individual services back to a specific patient visit or encounter, providing a detailed breakdown of a bill.

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
This table stores records of patient visits or interactions with healthcare providers, often called "encounters." It captures who was seen (patient), who provided the service (provider), where it happened (organization), and when (encounter_date). This table acts as a central transactional record, linking patients to the specific care they receive.

Each encounter is associated with a patient, a provider, and a healthcare organization. Importantly, information from an encounter is used to generate `claim_line` records, indicating that these visits are the basis for medical billing and insurance claims.

The structure suggests this table is fundamental to both clinical and administrative workflows. It not only documents the history of patient care but also directly feeds the revenue cycle by providing the necessary details for billing for services rendered.

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
This table acts as a central directory for healthcare organizations, such as hospitals, clinics, or labs. It stores essential business details like names, contact information, and tax IDs for these entities.

The table provides context to other parts of the system; for example, it links to patient `encounter` records to identify the facility where care was provided and connects to providers to show their organizational affiliations. Its purpose is to be a single source of truth for organization data, ensuring consistency for activities like patient scheduling, billing, and reporting on provider affiliations.

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
This table acts as a central patient registry, storing core demographic, contact, and insurance information for individuals receiving care. It functions as a master data table, providing a unique and authoritative record for each patient within the healthcare system. This patient record is the foundation for tracking a patient's complete history, as it links to related records such as clinical encounters or visits. The presence of an insurance identifier and indexes on last name and date of birth suggests the table is optimized for key administrative and clinical workflows, including patient look-up, registration, and billing.

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
This table is a master directory of healthcare providers, storing their identifying information, contact details, and professional classifications like specialty. It serves as a central reference list for uniquely identifying each practitioner or facility, as confirmed by the unique National Provider Identifier (NPI) field. This provider information is used to link a specific provider to a patient encounter (such as an appointment) and to associate them with the larger healthcare organizations they work for.

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
This table serves as a junction or linking table that establishes the relationship between individual healthcare providers and the organizations they work for or are affiliated with. It records the specific details of this affiliation, such as the provider's role (e.g., Cardiologist, Surgeon) and the date their relationship with the organization began. This structure allows a single provider to be associated with multiple organizations and an organization to have many affiliated providers, effectively managing their professional network and employment history.

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
