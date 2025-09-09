# Database Documentation: database

- Type: `postgresql` · Generated: `2025-09-09 14:55:53`

## Executive Summary

Database Analysis Summary:
- Database: database (postgresql)
- Total Tables: 6
- Total Columns: 51
- Total Constraints: 18
- Total Indexes: 15
- Total Triggers: 3
- Total Relationships: 6
- Schemas Analyzed: 1

This database contains 6 tables with 51 columns across 1 schema(s).
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
| Indexes | 15 |
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

> This table stores the individual billable services or procedures performed during a patient's healthcare visit. Each record represents a single line item on a medical claim, detailing the specific procedure, its cost, and the date it was provided. The table's primary purpose is to itemize all charges for billing and insurance reimbursement.

Each claim line item is associated with a specific patient visit or `encounter`, allowing the system to group all charges related to that single interaction. The presence of `procedure_code` and `modifier` columns indicates this table is a core component of a revenue cycle management or medical billing system, capturing the necessary details to generate claims for insurance companies and statements for patients.

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
| claim\_line\_pkey | primary | id | Yes | Yes | No |  |  |
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

> This table acts as a central record for patient-provider interactions within a healthcare setting, storing details for each visit or encounter. It documents who the patient was, which provider they saw, where the encounter took place, and on what date. This table links patients, providers, and healthcare organizations together for a specific event and serves as the foundational record for subsequent activities, such as medical billing, as indicated by its relationship with claim lines. The presence of 'encounter_type' and 'status' fields suggests it supports a structured workflow for managing different kinds of patient visits from scheduling through completion.

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
| encounter\_pkey | primary | id | Yes | Yes | No |  |  |
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

> This table serves as a master directory of healthcare organizations, such as hospitals, clinics, or labs. It stores foundational business information for each entity, including its name, type, location, and tax identifier. This master list is essential for tracking where patient care is delivered and which organizations employ or are affiliated with providers.

In business terms, this table connects patient encounters to the specific facility where they occurred. It also links healthcare providers to the organizations they are affiliated with, establishing a network of care locations and personnel.

The inclusion of a `tax_id` suggests the system supports financial processes like billing or insurance claims. The `type` column enables the system to differentiate between various kinds of facilities (e.g., hospitals vs. private clinics), which is crucial for reporting and operational management within a healthcare network.

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

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| organization\_pkey | primary | id | Yes | Yes | No |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| organization\_update\_timestamp | before | update | Yes | Trigger function: update\_timestamp |

###### Trigger: organization_update_timestamp

> **AI Analysis:** This trigger automatically updates the `updated_at` timestamp to the current time whenever an organization's record is modified. It exists to maintain an accurate and reliable audit trail, ensuring that there is always a record of when an organization's data was last changed.

Business Rule: When an organization's information is updated, the system must automatically record the date and time of the modification.

Implications: This trigger is crucial for data governance and auditing, as it guarantees the `updated_at` field is always accurate and reflects the true modification time. The performance impact is negligible, as updating a timestamp is a very lightweight and common database operation.

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

> This table serves as a master patient index, storing the core demographic, contact, and insurance information for each individual within a healthcare system. It acts as the central source of truth for patient identity.

This table is the primary reference for patient information, linking a unique patient to all of their related medical activities, such as the specific visits or treatments detailed in the `encounter` table.

The structure supports key administrative and clinical functions, enabling staff to quickly find and verify patient records by name or date of birth for scheduling, treatment, and billing purposes.

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
| patient\_pkey | primary | id | Yes | Yes | No |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| patient\_update\_timestamp | before | update | Yes | Trigger function: update\_timestamp |

###### Trigger: patient_update_timestamp

> **AI Analysis:** This trigger automatically updates a timestamp each time a patient's record is modified, ensuring an accurate and current record of the last change. This serves as a simple but effective audit mechanism to track when patient data was last updated.

The trigger implements the business rule: "Whenever a patient's information is changed, the system must automatically record the date and time of that modification."

This automation is critical for data integrity and auditing, providing a reliable timestamp for the last modification of any patient record. It introduces a minor performance overhead on all update operations, which is a standard trade-off for maintaining an auditable data history.

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

> This table is a master directory of individual healthcare providers, storing their professional details, credentials like the National Provider Identifier (NPI), and contact information. It serves as a central reference for identifying and managing the clinicians who deliver care within the system.

In business terms, this table connects each provider to the specific patient `encounters` they conduct and also links them to the larger healthcare `organizations` they are affiliated with. The presence of columns like `specialty` and `provider_type` indicates the system uses this data to manage provider roles, facilitate patient scheduling, and likely support billing and reporting functions.

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
| provider\_pkey | primary | id | Yes | Yes | No |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| provider\_update\_timestamp | before | update | Yes | Trigger function: update\_timestamp |

###### Trigger: provider_update_timestamp

> **AI Analysis:** This trigger automatically updates the `updated_at` timestamp to the current time whenever a provider's record is modified. Its purpose is to maintain a reliable audit trail, ensuring there is always an accurate record of when a provider's data was last changed. This supports data governance and helps track the freshness of provider information.

Business Rule: When any information for a provider is updated, the record's "last updated" timestamp must be automatically set to the current date and time.

Implications: The trigger enforces data consistency by ensuring the `updated_at` field is always accurate, which is crucial for auditing and tracking data history. The performance impact is negligible for single-row updates but could be a minor consideration during very large bulk update operations.

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

> This table serves as a junction table to manage the many-to-many relationship between healthcare providers and healthcare organizations. It connects the `provider` table with the `organization` table, allowing the system to track which providers are affiliated with which specific hospitals or clinics. The inclusion of `role` and `start_date` columns indicates the table's purpose is to maintain a record of a provider's employment or credentialing history, detailing their specific position and the beginning of their tenure at each organization.

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

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| provider\_organization\_pkey | primary | organization\_id, provider\_id | Yes | Yes | No |  |  |

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

> **AI Analysis:** This procedure retrieves a consolidated summary for a specific patient, including their demographic details, total number of encounters, and the date of their most recent visit. It also calculates the cumulative financial charges associated with all their medical encounters, providing a combined clinical and financial overview.
Operation Type: Data aggregation and reporting
Role in Business Processes: This procedure is designed to populate a patient summary view or dashboard within a healthcare application. It allows clinical or administrative staff to quickly access a high-level overview of a patient's activity and financial history in a single request.

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

> **AI Analysis:** This procedure calculates and returns key financial and operational performance metrics for a specific healthcare provider. It summarizes a provider's total patient encounters, the total revenue generated from those encounters, and the average charge per encounter, providing a snapshot of their activity.
Reporting and business calculation
The procedure likely supports a provider performance dashboard or a financial reporting module within a practice management application. It provides a consolidated view of a provider's productivity and financial contribution, enabling performance analysis and business intelligence.

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

> **AI Analysis:** This procedure is a trigger function that automatically updates a record's timestamp whenever it is modified. Its business purpose is to maintain an accurate audit trail, ensuring that every change to a record is logged with the current time for data integrity and compliance purposes.

Data Auditing

This function supports all business processes that modify data by enforcing a consistent data governance policy. It provides a reliable "last modified" date for any record it is attached to, which is critical for tracking the history of patient, provider, or claim information.

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

Found 15 indexes across all tables:
claim_line.claim_line_pkey (primary)
claim_line.idx_claim_line_code (index)
claim_line.idx_claim_line_encounter (index)
encounter.encounter_pkey (primary)
encounter.idx_encounter_date (index)
encounter.idx_encounter_patient (index)
encounter.idx_encounter_provider (index)
organization.organization_pkey (primary)
patient.idx_patient_dob (index)
patient.idx_patient_last_name (index)
...

| Index Type | Count |
| --- | --- |
| index | 8 |
| primary | 6 |
| unique | 1 |

| Key | Value |
| --- | ----- |
| Unique Indexes | 7 |
| Primary Indexes | 6 |
| Clustered Indexes | 0 |
| Estimated Index Storage | 0.00 B |

## Performance Insights

- Database has 6 relationships indicating good normalization
- Found 15 indexes for query optimization
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
This table stores the individual billable services or procedures performed during a patient's healthcare visit. Each record represents a single line item on a medical claim, detailing the specific procedure, its cost, and the date it was provided. The table's primary purpose is to itemize all charges for billing and insurance reimbursement.

Each claim line item is associated with a specific patient visit or `encounter`, allowing the system to group all charges related to that single interaction. The presence of `procedure_code` and `modifier` columns indicates this table is a core component of a revenue cycle management or medical billing system, capturing the necessary details to generate claims for insurance companies and statements for patients.

Relationships:
This table references encounter.

Technical Details:
Columns: 8 (id(integer), encounter_id(integer), procedure_code(varchar), procedure_description(text), charge_amount(decimal)...)
Primary Keys: id
Foreign Keys: encounter_id
Constraints: 3
Indexes: 3
Triggers: 0
Row Count: 47
Size: 65,536 bytes

### encounter

Table: encounter
Schema: healthcare
Type: table

AI Analysis:
This table acts as a central record for patient-provider interactions within a healthcare setting, storing details for each visit or encounter. It documents who the patient was, which provider they saw, where the encounter took place, and on what date. This table links patients, providers, and healthcare organizations together for a specific event and serves as the foundational record for subsequent activities, such as medical billing, as indicated by its relationship with claim lines. The presence of 'encounter_type' and 'status' fields suggests it supports a structured workflow for managing different kinds of patient visits from scheduling through completion.

Relationships:
This table references organization, references patient, references provider. and is referenced by claim_line.

Technical Details:
Columns: 9 (id(integer), patient_id(integer), provider_id(integer), organization_id(integer), encounter_date(date)...)
Primary Keys: id
Foreign Keys: patient_id, provider_id, organization_id
Constraints: 6
Indexes: 4
Triggers: 0
Row Count: 29
Size: 81,920 bytes

### organization

Table: organization
Schema: healthcare
Type: table

AI Analysis:
This table serves as a master directory of healthcare organizations, such as hospitals, clinics, or labs. It stores foundational business information for each entity, including its name, type, location, and tax identifier. This master list is essential for tracking where patient care is delivered and which organizations employ or are affiliated with providers.

In business terms, this table connects patient encounters to the specific facility where they occurred. It also links healthcare providers to the organizations they are affiliated with, establishing a network of care locations and personnel.

The inclusion of a `tax_id` suggests the system supports financial processes like billing or insurance claims. The `type` column enables the system to differentiate between various kinds of facilities (e.g., hospitals vs. private clinics), which is crucial for reporting and operational management within a healthcare network.

Relationships:
and is referenced by encounter, referenced by provider_organization.

Technical Details:
Columns: 9 (id(integer), name(varchar), type(varchar), address(text), phone(varchar)...)
Primary Keys: id
Foreign Keys: None
Constraints: 2
Indexes: 1
Triggers: 1
Row Count: 20
Size: 32,768 bytes

### patient

Table: patient
Schema: healthcare
Type: table

AI Analysis:
This table serves as a master patient index, storing the core demographic, contact, and insurance information for each individual within a healthcare system. It acts as the central source of truth for patient identity.

This table is the primary reference for patient information, linking a unique patient to all of their related medical activities, such as the specific visits or treatments detailed in the `encounter` table.

The structure supports key administrative and clinical functions, enabling staff to quickly find and verify patient records by name or date of birth for scheduling, treatment, and billing purposes.

Relationships:
and is referenced by encounter.

Technical Details:
Columns: 11 (id(integer), first_name(varchar), last_name(varchar), date_of_birth(date), gender(char)...)
Primary Keys: id
Foreign Keys: None
Constraints: 2
Indexes: 3
Triggers: 1
Row Count: 22
Size: 65,536 bytes

### provider

Table: provider
Schema: healthcare
Type: table

AI Analysis:
This table is a master directory of individual healthcare providers, storing their professional details, credentials like the National Provider Identifier (NPI), and contact information. It serves as a central reference for identifying and managing the clinicians who deliver care within the system.

In business terms, this table connects each provider to the specific patient `encounters` they conduct and also links them to the larger healthcare `organizations` they are affiliated with. The presence of columns like `specialty` and `provider_type` indicates the system uses this data to manage provider roles, facilitate patient scheduling, and likely support billing and reporting functions.

Relationships:
and is referenced by encounter, referenced by provider_organization.

Technical Details:
Columns: 10 (id(integer), name(varchar), provider_type(varchar), specialty(varchar), npi(varchar)...)
Primary Keys: id
Foreign Keys: None
Constraints: 2
Indexes: 3
Triggers: 1
Row Count: 22
Size: 65,536 bytes

### provider_organization

Table: provider_organization
Schema: healthcare
Type: table

AI Analysis:
This table serves as a junction table to manage the many-to-many relationship between healthcare providers and healthcare organizations. It connects the `provider` table with the `organization` table, allowing the system to track which providers are affiliated with which specific hospitals or clinics. The inclusion of `role` and `start_date` columns indicates the table's purpose is to maintain a record of a provider's employment or credentialing history, detailing their specific position and the beginning of their tenure at each organization.

Relationships:
This table references organization, references provider.

Technical Details:
Columns: 4 (provider_id(integer), organization_id(integer), role(varchar), start_date(date))
Primary Keys: provider_id, organization_id
Foreign Keys: provider_id, organization_id
Constraints: 3
Indexes: 1
Triggers: 0
Row Count: 28
Size: 24,576 bytes
