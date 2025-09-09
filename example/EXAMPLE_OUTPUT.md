# Database Documentation: database

- Type: `postgresql` · Generated: `2025-09-09 14:00:46`

## Executive Summary

Database Analysis Summary:
- Database: database (postgresql)
- Total Tables: 6
- Total Columns: 51
- Total Constraints: 12
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

##### Table: healthcare.provider
- Type: `table` · Rows: `-1` · Size: `64.00 KB`

> This table acts as a master directory for healthcare providers, storing their professional details, contact information, and unique National Provider Identifier (NPI). It serves as a central reference within the system, linking individual providers to the specific patient encounters they conduct and the larger healthcare organizations they are affiliated with. The structure, particularly the unique NPI and the index on specialty, indicates its purpose is to manage a network of providers and efficiently look them up for scheduling, billing, or reporting.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare.provider\_id\_seq'::regclass) | Yes | No |  |  |
| name | char | No |  | No | No |  |  |
| provider\_type | char | Yes |  | No | No |  |  |
| specialty | char | Yes |  | No | No |  |  |
| npi | char | Yes |  | No | No |  |  |
| address | text | Yes |  | No | No |  |  |
| phone | char | Yes |  | No | No |  |  |
| email | char | Yes |  | No | No |  |  |
| created\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |
| updated\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| provider\_pkey | primary\_key | id |  |  |

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

> **AI Analysis:** This trigger automatically updates a provider's record with the current timestamp whenever any of their information is changed. Its purpose is to maintain an accurate and reliable audit trail, ensuring the system always knows precisely when a provider's data was last modified. This supports data governance, helps track the freshness of provider information for directories or claims, and aids in troubleshooting data discrepancies.

Business Rule Implemented:
The trigger enforces the business rule that "The date and time of the last modification must be recorded for every provider record update."

Notable Implications:
This trigger ensures high data consistency by automating a critical auditing task, creating a reliable log of changes without relying on application logic. The performance impact is negligible, as updating a timestamp is a very lightweight operation that adds minimal overhead to database update transactions.

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
| provider\_organization | provider\_id | provider | id | provider\_organization\_provider\_id\_fkey |  |  | one\_to\_many |
| encounter | provider\_id | provider | id | encounter\_provider\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
and is referenced by provider_organization, referenced by encounter.

##### Table: healthcare.provider_organization
- Type: `table` · Rows: `-1` · Size: `24.00 KB`

> This table serves as a bridge, linking individual healthcare providers to the healthcare organizations they work for or are affiliated with. It connects the `provider` and `organization` tables to resolve a many-to-many relationship, allowing a single provider to be associated with multiple organizations (e.g., a doctor with privileges at several hospitals). The table's purpose is to maintain a record of these professional affiliations, including the provider's specific role and the start date of their association, which is essential for credentialing, network management, and tracking employment history.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| provider\_id | integer | No |  | Yes | Yes | fk→provider(id) |  |
| organization\_id | integer | No |  | Yes | Yes | fk→organization(id) |  |
| role | char | Yes |  | No | No |  |  |
| start\_date | date | Yes | CURRENT\_DATE | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| provider\_organization\_pkey | primary\_key | provider\_id, organization\_id |  |  |
| provider\_organization\_organization\_id\_fkey | foreign\_key | organization\_id | ref organization(id) |  |
| provider\_organization\_provider\_id\_fkey | foreign\_key | provider\_id | ref provider(id) |  |

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| provider\_organization | organization\_id | organization | id | provider\_organization\_organization\_id\_fkey |  |  | one\_to\_many |
| provider\_organization | provider\_id | provider | id | provider\_organization\_provider\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
This table references organization, references provider.

##### Table: healthcare.organization
- Type: `table` · Rows: `-1` · Size: `32.00 KB`

> This table acts as a master directory of healthcare organizations, such as hospitals or clinics, storing their core identifying and contact information. It provides the institutional context for patient encounters and establishes the affiliation between healthcare providers and the facilities where they work. The table is essential for managing the network of care locations and business entities within the healthcare system.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare.organization\_id\_seq'::regclass) | Yes | No |  |  |
| name | char | No |  | No | No |  |  |
| type | char | Yes |  | No | No |  |  |
| address | text | Yes |  | No | No |  |  |
| phone | char | Yes |  | No | No |  |  |
| website | char | Yes |  | No | No |  |  |
| tax\_id | char | Yes |  | No | No |  |  |
| created\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |
| updated\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| organization\_pkey | primary\_key | id |  |  |

###### Triggers
| Name | Timing | Event | Enabled | Description |
| --- | --- | --- | --- | --- |
| organization\_update\_timestamp | before | update | Yes | Trigger function: update\_timestamp |

###### Trigger: organization_update_timestamp

> **AI Analysis:** This trigger automatically updates a timestamp field every time a record in the organization table is modified. Its purpose is to maintain an accurate and automated audit trail, ensuring that the system always knows when an organization's information was last changed.

Business Rule: Enforces the rule that all modifications to an organization's record must be timestamped to track data currency and maintain a modification history.

Implications: This mechanism is crucial for data governance and auditing, providing a reliable log of when data was last updated without requiring manual intervention. The performance impact is minimal, as updating a timestamp is a very lightweight operation.

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
| provider\_organization | organization\_id | organization | id | provider\_organization\_organization\_id\_fkey |  |  | one\_to\_many |
| encounter | organization\_id | organization | id | encounter\_organization\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
and is referenced by provider_organization, referenced by encounter.

##### Table: healthcare.patient
- Type: `table` · Rows: `-1` · Size: `64.00 KB`

> This table stores core demographic, contact, and insurance information for individuals, acting as a master patient registry for a healthcare system. It serves as the single source of truth for patient identity, providing a unique record that is referenced by other clinical tables. Each patient can be linked to one or more medical visits or interactions, as tracked in the `encounter` table, allowing the business to maintain a comprehensive history for each person. The structure is optimized for looking up patients by last name and date of birth, which are common workflows in a clinical setting.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare.patient\_id\_seq'::regclass) | Yes | No |  |  |
| first\_name | char | No |  | No | No |  |  |
| last\_name | char | No |  | No | No |  |  |
| date\_of\_birth | date | No |  | No | No |  |  |
| gender | char | Yes |  | No | No |  |  |
| address | text | Yes |  | No | No |  |  |
| phone | char | Yes |  | No | No |  |  |
| email | char | Yes |  | No | No |  |  |
| insurance\_id | char | Yes |  | No | No |  |  |
| created\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |
| updated\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| patient\_pkey | primary\_key | id |  |  |

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

> **AI Analysis:** This trigger automatically updates a timestamp column every time a patient's record is modified. Its purpose is to maintain an accurate and reliable audit trail, ensuring that the system always knows when a patient's information was last changed.

Business Rule: The trigger enforces the rule that "The date and time of the last modification must be recorded for every patient record update."

Implications: This provides a crucial, automated audit log for data changes, which is essential for data integrity, troubleshooting, and regulatory compliance in a healthcare setting. The performance impact is typically negligible.

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
| encounter | patient\_id | patient | id | encounter\_patient\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
and is referenced by encounter.

##### Table: healthcare.encounter
- Type: `table` · Rows: `-1` · Size: `80.00 KB`

> This table records specific healthcare interactions, or "encounters," between a patient and a provider at a healthcare facility. It acts as a central log for patient visits, capturing key details like the date, type, and status of the interaction.

The table links a `patient` to the `provider` they saw and the `organization` (e.g., hospital or clinic) where the visit occurred. It also serves as the foundational record for individual `claim_line` items, meaning each encounter is the basis for subsequent billing or insurance claims.

The table's purpose is to track patient care events for both clinical and administrative needs. Its direct relationship to the `claim_line` table confirms its critical role in the revenue cycle, as each encounter represents a potentially billable event.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare.encounter\_id\_seq'::regclass) | Yes | No |  |  |
| patient\_id | integer | No |  | No | Yes | fk→patient(id) |  |
| provider\_id | integer | No |  | No | Yes | fk→provider(id) |  |
| organization\_id | integer | No |  | No | Yes | fk→organization(id) |  |
| encounter\_date | date | No | CURRENT\_DATE | No | No |  |  |
| encounter\_type | char | Yes |  | No | No |  |  |
| status | char | Yes |  | No | No |  |  |
| notes | text | Yes |  | No | No |  |  |
| created\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| encounter\_pkey | primary\_key | id |  |  |
| encounter\_organization\_id\_fkey | foreign\_key | organization\_id | ref organization(id) |  |
| encounter\_patient\_id\_fkey | foreign\_key | patient\_id | ref patient(id) |  |
| encounter\_provider\_id\_fkey | foreign\_key | provider\_id | ref provider(id) |  |

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| idx\_encounter\_date | index | encounter\_date | No | No | No |  |  |
| idx\_encounter\_patient | index | patient\_id | No | No | No |  |  |
| idx\_encounter\_provider | index | provider\_id | No | No | No |  |  |

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| encounter | organization\_id | organization | id | encounter\_organization\_id\_fkey |  |  | one\_to\_many |
| encounter | patient\_id | patient | id | encounter\_patient\_id\_fkey |  |  | one\_to\_many |
| encounter | provider\_id | provider | id | encounter\_provider\_id\_fkey |  |  | one\_to\_many |
| claim\_line | encounter\_id | encounter | id | claim\_line\_encounter\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
This table references organization, references patient, references provider. and is referenced by claim_line.

##### Table: healthcare.claim_line
- Type: `table` · Rows: `-1` · Size: `64.00 KB`

> The `claim_line` table stores the individual, itemized services and procedures performed during a patient's healthcare encounter. Each record represents a single billable line item on a medical claim, detailing the specific procedure, its cost, and the date it was provided. This table is fundamental for generating detailed patient bills and insurance claims.

This table is related to the `encounter` table, meaning each specific service or charge is associated with a particular patient visit or hospital stay. This allows the system to group all charges related to a single healthcare event.

The presence of columns like `procedure_code`, `charge_amount`, and `modifier` strongly indicates this table's purpose is for medical billing and insurance claim submission. The structure allows for a detailed, auditable breakdown of all billable activities that occurred during a patient's interaction with the healthcare provider.

###### Columns
| Column | Type | Nullable | Default | PK | FK | Details | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | integer | No | nextval('healthcare.claim\_line\_id\_seq'::regclass) | Yes | No |  |  |
| encounter\_id | integer | No |  | No | Yes | fk→encounter(id) |  |
| procedure\_code | char | No |  | No | No |  |  |
| procedure\_description | text | No |  | No | No |  |  |
| charge\_amount | decimal | No |  | No | No |  |  |
| service\_date | date | No |  | No | No |  |  |
| modifier | char | Yes |  | No | No |  |  |
| created\_at | timestamp | Yes | CURRENT\_TIMESTAMP | No | No |  |  |

###### Constraints
| Name | Type | Columns | Details | Description |
| --- | --- | --- | --- | --- |
| claim\_line\_pkey | primary\_key | id |  |  |
| claim\_line\_encounter\_id\_fkey | foreign\_key | encounter\_id | ref encounter(id) |  |

###### Indexes
| Name | Type | Columns | Unique | Primary | Clustered | Size | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| idx\_claim\_line\_code | index | procedure\_code | No | No | No |  |  |
| idx\_claim\_line\_encounter | index | encounter\_id | No | No | No |  |  |

###### Related Tables
| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claim\_line | encounter\_id | encounter | id | claim\_line\_encounter\_id\_fkey |  |  | one\_to\_many |

###### Relationship Summary
This table references encounter.

#### Stored Procedures

| Name | Returns | Language | Deterministic | Created | Modified |
| --- | --- | --- | --- | --- | --- |
| get\_patient\_summary | record | plpgsql | No |  |  |
| get\_provider\_statistics | record | plpgsql | No |  |  |
| update\_timestamp | trigger | plpgsql | No |  |  |

##### Procedure: get_patient_summary

> **AI Analysis:** This procedure retrieves a consolidated summary for a specific patient, identified by their ID. It calculates key metrics such as the total number of medical encounters, the date of their most recent visit, and the cumulative sum of all charges billed to them. The business purpose is to provide a quick, at-a-glance overview of a patient's history and financial status for administrative or clinical staff.
Reporting / Data Aggregation
This procedure serves as a backend function to populate a patient summary view or dashboard within a healthcare application. It supports business processes like patient check-in, clinical chart review, or billing inquiries by providing a standardized and efficient way to access essential patient information.

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

> **AI Analysis:** This procedure retrieves a performance and financial summary for a specific healthcare provider identified by their ID. It calculates the provider's total number of patient encounters, the total revenue generated from associated claims, and the resulting average revenue per encounter.
Reporting and business calculation
This function serves as a data source for performance dashboards or financial reports, enabling business users to analyze a provider's productivity and financial contribution to the organization.

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

> **AI Analysis:** This procedure automatically updates a record's "last modified" timestamp whenever that record is changed. Its business purpose is to maintain an accurate and reliable audit trail for data governance, ensuring data integrity and supporting compliance requirements for tracking changes to sensitive healthcare information.
Data maintenance and auditing
The procedure enforces a critical data governance rule by automatically logging the time of any data modification. This provides a foundational layer for auditing, change tracking, and ensuring data currency across records like patient, encounter, or claim data.

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
provider_organization.organization_id → organization.id
provider_organization.provider_id → provider.id
encounter.organization_id → organization.id
encounter.patient_id → patient.id
encounter.provider_id → provider.id
claim_line.encounter_id → encounter.id

| From | Column | To | Column | Constraint | On Delete | On Update | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| provider\_organization | organization\_id | organization | id | provider\_organization\_organization\_id\_fkey |  |  | one\_to\_many |
| provider\_organization | provider\_id | provider | id | provider\_organization\_provider\_id\_fkey |  |  | one\_to\_many |
| encounter | organization\_id | organization | id | encounter\_organization\_id\_fkey |  |  | one\_to\_many |
| encounter | patient\_id | patient | id | encounter\_patient\_id\_fkey |  |  | one\_to\_many |
| encounter | provider\_id | provider | id | encounter\_provider\_id\_fkey |  |  | one\_to\_many |
| claim\_line | encounter\_id | encounter | id | claim\_line\_encounter\_id\_fkey |  |  | one\_to\_many |

## Indexes

Found 9 indexes across all tables:
provider.idx_provider_specialty (index)
provider.provider_npi_key (unique)
patient.idx_patient_dob (index)
patient.idx_patient_last_name (index)
encounter.idx_encounter_date (index)
encounter.idx_encounter_patient (index)
encounter.idx_encounter_provider (index)
claim_line.idx_claim_line_code (index)
claim_line.idx_claim_line_encounter (index)

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

### provider

Table: provider
Schema: healthcare
Type: table

AI Analysis:
This table acts as a master directory for healthcare providers, storing their professional details, contact information, and unique National Provider Identifier (NPI). It serves as a central reference within the system, linking individual providers to the specific patient encounters they conduct and the larger healthcare organizations they are affiliated with. The structure, particularly the unique NPI and the index on specialty, indicates its purpose is to manage a network of providers and efficiently look them up for scheduling, billing, or reporting.

Relationships:
and is referenced by provider_organization, referenced by encounter.

Technical Details:
Columns: 10 (id(integer), name(char), provider_type(char), specialty(char), npi(char)...)
Primary Keys: id
Foreign Keys: None
Constraints: 1
Indexes: 2
Triggers: 1
Row Count: -1
Size: 65,536 bytes

### provider_organization

Table: provider_organization
Schema: healthcare
Type: table

AI Analysis:
This table serves as a bridge, linking individual healthcare providers to the healthcare organizations they work for or are affiliated with. It connects the `provider` and `organization` tables to resolve a many-to-many relationship, allowing a single provider to be associated with multiple organizations (e.g., a doctor with privileges at several hospitals). The table's purpose is to maintain a record of these professional affiliations, including the provider's specific role and the start date of their association, which is essential for credentialing, network management, and tracking employment history.

Relationships:
This table references organization, references provider.

Technical Details:
Columns: 4 (provider_id(integer), organization_id(integer), role(char), start_date(date))
Primary Keys: provider_id, organization_id
Foreign Keys: provider_id, organization_id
Constraints: 3
Indexes: 0
Triggers: 0
Row Count: -1
Size: 24,576 bytes

### organization

Table: organization
Schema: healthcare
Type: table

AI Analysis:
This table acts as a master directory of healthcare organizations, such as hospitals or clinics, storing their core identifying and contact information. It provides the institutional context for patient encounters and establishes the affiliation between healthcare providers and the facilities where they work. The table is essential for managing the network of care locations and business entities within the healthcare system.

Relationships:
and is referenced by provider_organization, referenced by encounter.

Technical Details:
Columns: 9 (id(integer), name(char), type(char), address(text), phone(char)...)
Primary Keys: id
Foreign Keys: None
Constraints: 1
Indexes: 0
Triggers: 1
Row Count: -1
Size: 32,768 bytes

### patient

Table: patient
Schema: healthcare
Type: table

AI Analysis:
This table stores core demographic, contact, and insurance information for individuals, acting as a master patient registry for a healthcare system. It serves as the single source of truth for patient identity, providing a unique record that is referenced by other clinical tables. Each patient can be linked to one or more medical visits or interactions, as tracked in the `encounter` table, allowing the business to maintain a comprehensive history for each person. The structure is optimized for looking up patients by last name and date of birth, which are common workflows in a clinical setting.

Relationships:
and is referenced by encounter.

Technical Details:
Columns: 11 (id(integer), first_name(char), last_name(char), date_of_birth(date), gender(char)...)
Primary Keys: id
Foreign Keys: None
Constraints: 1
Indexes: 2
Triggers: 1
Row Count: -1
Size: 65,536 bytes

### encounter

Table: encounter
Schema: healthcare
Type: table

AI Analysis:
This table records specific healthcare interactions, or "encounters," between a patient and a provider at a healthcare facility. It acts as a central log for patient visits, capturing key details like the date, type, and status of the interaction.

The table links a `patient` to the `provider` they saw and the `organization` (e.g., hospital or clinic) where the visit occurred. It also serves as the foundational record for individual `claim_line` items, meaning each encounter is the basis for subsequent billing or insurance claims.

The table's purpose is to track patient care events for both clinical and administrative needs. Its direct relationship to the `claim_line` table confirms its critical role in the revenue cycle, as each encounter represents a potentially billable event.

Relationships:
This table references organization, references patient, references provider. and is referenced by claim_line.

Technical Details:
Columns: 9 (id(integer), patient_id(integer), provider_id(integer), organization_id(integer), encounter_date(date)...)
Primary Keys: id
Foreign Keys: patient_id, provider_id, organization_id
Constraints: 4
Indexes: 3
Triggers: 0
Row Count: -1
Size: 81,920 bytes

### claim_line

Table: claim_line
Schema: healthcare
Type: table

AI Analysis:
The `claim_line` table stores the individual, itemized services and procedures performed during a patient's healthcare encounter. Each record represents a single billable line item on a medical claim, detailing the specific procedure, its cost, and the date it was provided. This table is fundamental for generating detailed patient bills and insurance claims.

This table is related to the `encounter` table, meaning each specific service or charge is associated with a particular patient visit or hospital stay. This allows the system to group all charges related to a single healthcare event.

The presence of columns like `procedure_code`, `charge_amount`, and `modifier` strongly indicates this table's purpose is for medical billing and insurance claim submission. The structure allows for a detailed, auditable breakdown of all billable activities that occurred during a patient's interaction with the healthcare provider.

Relationships:
This table references encounter.

Technical Details:
Columns: 8 (id(integer), encounter_id(integer), procedure_code(char), procedure_description(text), charge_amount(decimal)...)
Primary Keys: id
Foreign Keys: encounter_id
Constraints: 2
Indexes: 2
Triggers: 0
Row Count: -1
Size: 65,536 bytes
