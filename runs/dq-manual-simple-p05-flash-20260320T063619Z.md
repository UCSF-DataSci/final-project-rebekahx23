# Data Quality Report - dq-manual-simple-p05-flash-20260320T063619Z

Generated at: 2026-03-20 06:37:08 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P05-FLASH`
- Event log: `runs/dq-manual-simple-p05-flash-20260320T063619Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 1 |
| High | 1 |
| Medium | 0 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| CRITICAL | FAIL | healthcare_dataset | admission_discharge_date_order_validity | 1140 |
| HIGH | FAIL | healthcare_dataset | admission_date_not_in_future | 1140 |

## Detailed Findings
### 1. [CRITICAL/FAIL] admission_discharge_date_order_validity (healthcare_dataset)
- Why this matters: The discharge date must always be on or after the admission date. Records where the discharge date precedes the admission date indicate a severe data integrity issue, impacting patient timeline and billing accuracy. This was explicitly observed in the profiling summary.
- Issue count: **1140**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND date(date_of_admission) IS NOT NULL AND date(discharge_date) IS NOT NULL AND julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "jOhN hARTmAN",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-01-27"
  },
  {
    "name": "JOhN eLlis",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-06-30"
  },
  {
    "name": "JOsepH SmIth",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-05-14"
  }
]
```

### 2. [HIGH/FAIL] admission_date_not_in_future (healthcare_dataset)
- Why this matters: An admission date cannot realistically be in the future. Such entries likely represent data entry errors or unhandled placeholder values, compromising the accuracy of patient records and operational planning. A future date ('2099-12-31') was found in the sample.
- Issue count: **1140**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND date(date_of_admission) IS NOT NULL AND julianday(date_of_admission) > julianday(CURRENT_DATE);
```

Example rows:
```json
[
  {
    "name": "jOhN hARTmAN",
    "date_of_admission": "2099-12-31"
  },
  {
    "name": "JOhN eLlis",
    "date_of_admission": "2099-12-31"
  },
  {
    "name": "JOsepH SmIth",
    "date_of_admission": "2099-12-31"
  }
]
```

## Supervisor Narrative
**Data Quality Report: `healthcare_dataset`**

**Overall Verdict: Red**

This run identified critical and high-severity data integrity issues in the `healthcare_dataset`, particularly concerning admission and discharge dates. Immediate attention is required to rectify these problems to ensure data reliability.

**Top Critical/High Issues:**

*   **Critical Issue: `admission_discharge_date_order_validity`**
    *   **Description:** For 1140 records, the `discharge_date` is reported to occur before the `date_of_admission`. This is a severe logical inconsistency, indicating fundamental data entry errors or corruption.
    *   **Impact:** Compromises patient treatment timelines, billing accuracy, and overall data trustworthiness.

*   **High Issue: `admission_date_not_in_future`**
    *   **Description:** 1140 records contain `date_of_admission` values that are in the future. These are likely data entry errors or unhandled placeholder values.
    *   **Impact:** Distorts active patient counts, invalidates historical analyses, and suggests poor data validation at ingestion.

**Test Coverage Notes:**
This data quality run focused primarily on date-related integrity checks (`admission_discharge_date_order_validity` and `admission_date_not_in_future`). While these critical tests were executed and revealed significant issues, the overall test coverage is limited. Other potential data quality concerns identified during profiling, such as inconsistent casing in `name` and `hospital` fields, and the need for `billing_amount` validation, were not explicitly covered by automated tests in this run.

**Suggested Production Guardrails (SQL checks to schedule with each data load):**

To prevent recurrence and improve the reliability of the `healthcare_dataset`, the following SQL checks should be implemented as automated guardrails during each data ingestion or update process:

1.  **Ensure Discharge Date is Not Before Admission Date (Critical):**
    ```sql
    SELECT name, date_of_admission, discharge_date
    FROM healthcare_dataset
    WHERE date_of_admission IS NOT NULL
      AND discharge_date IS NOT NULL
      AND date(date_of_admission) IS NOT NULL
      AND date(discharge_date) IS NOT NULL
      AND julianday(discharge_date) < julianday(date_of_admission);
    ```
    *Action:* Flag any records returned by this query for immediate correction and halt load if issues exceed a defined threshold.

2.  **Prevent Future Admission Dates (High):**
    ```sql
    SELECT name, date_of_admission
    FROM healthcare_dataset
    WHERE date_of_admission IS NOT NULL
      AND date(date_of_admission) IS NOT NULL
      AND julianday(date_of_admission) > julianday(CURRENT_DATE);
    ```
    *Action:* Flag any records returned by this query and investigate data entry processes. Consider rejecting records with future dates.

3.  **Standardize `name` Casing (Moderate - Future Enhancement):**
    *   Implement a process to standardize the casing of the `name` column, e.g., to Title Case upon ingestion.
    *   *Example (conceptual, actual implementation may vary by SQL dialect):* `UPDATE healthcare_dataset SET name = INITCAP(name);` or a custom function.

4.  **Standardize `hospital` Names (Moderate - Future Enhancement):**
    *   Develop and apply a robust cleaning routine to standardize hospital names, removing or consistentizing organizational designators.
    *   *Example (conceptual):* `UPDATE healthcare_dataset SET hospital = REGEXP_REPLACE(hospital, '( PLC| LLC| and| Inc)', '', 'g');`

5.  **Validate `billing_amount` for Negative Values (Low - Future Enhancement):**
    ```sql
    SELECT name, billing_amount
    FROM healthcare_dataset
    WHERE billing_amount < 0;
    ```
    *Action:* Investigate and correct any negative billing amounts.

These guardrails will help enforce data integrity and improve the overall quality of the `healthcare_dataset` going forward.
