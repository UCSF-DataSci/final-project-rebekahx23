# Data Quality Report - dq-manual-complex-p20-pro-20260320T054458Z

Generated at: 2026-03-20 05:46:21 UTC

## Executive Summary
- Overall verdict: **YELLOW**
- Total tests executed: **2**
- Passed: **1**
- Failed: **1**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P20-PRO`
- Event log: `runs/dq-manual-complex-p20-pro-20260320T054458Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 1 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| MEDIUM | FAIL | healthcare_dataset | name_or_doctor_contains_prefix_or_suffix | 2870 |

## Detailed Findings
### 1. [MEDIUM/FAIL] name_or_doctor_contains_prefix_or_suffix (healthcare_dataset)
- Why this matters: The profile noted prefixes (Mr., Dr.) and suffixes (MD, DDS) in the `name` and `doctor` columns. These non-name components complicate data integration and entity resolution. This test flags records containing common prefixes or suffixes, highlighting the need for data cleaning and standardization to ensure reliable record matching.
- Issue count: **2870**
- Output truncated: **yes**

```sql
SELECT
  *
FROM
  healthcare_dataset
WHERE
  LOWER(name) LIKE 'mr. %'
  OR LOWER(name) LIKE 'dr. %'
  OR LOWER(name) LIKE LOWER('% md')
  OR LOWER(name) LIKE LOWER('% dds')
  OR LOWER(doctor) LIKE 'mr. %'
  OR LOWER(doctor) LIKE 'dr. %'
  OR LOWER(doctor) LIKE LOWER('% md')
  OR LOWER(doctor) LIKE LOWER('% dds')
```

Example rows:
```json
[
  {
    "name": "dR. EilEEn thomPsoN",
    "age": 59,
    "gender": "Male",
    "blood_type": "A+",
    "medical_condition": "Asthma",
    "date_of_admission": "2021-08-02",
    "doctor": "Donna Martinez MD",
    "hospital": "and Sons Smith",
    "insurance_provider": "Aetna",
    "billing_amount": 25250.052428216135,
    "room_number": 119,
    "admission_type": "Urgent",
    "discharge_date": "2021-08-12",
    "medication": "Lipitor",
    "test_results": "Inconclusive"
  },
  {
    "name": "mr. KenNEth MoORE",
    "age": 34,
    "gender": "Female",
    "blood_type": "A+",
    "medical_condition": "Diabetes",
    "date_of_admission": "2022-06-21",
    "doctor": "James Ellis",
    "hospital": "Serrano-Dixon",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 18834.80134117836,
    "room_number": 157,
    "admission_type": "Emergency",
    "discharge_date": "2022-06-30",
    "medication": "Lipitor",
    "test_results": "Abnormal"
  },
  {
    "name": "Mr. eRiC Lane",
    "age": 49,
    "gender": "Female",
    "blood_type": "A-",
    "medical_condition": "Asthma",
    "date_of_admission": "2022-06-24",
    "doctor": "Matthew Thomas",
    "hospital": "and Howell Brooks, Rogers",
    "insurance_provider": "Cigna",
    "billing_amount": 25966.328610220968,
    "room_number": 418,
    "admission_type": "Elective",
    "discharge_date": "2022-07-18",
    "medication": "Paracetamol",
    "test_results": "Normal"
  }
]
```

## Supervisor Narrative
# Data Quality Report: healthcare_dataset

**Overall Verdict:** 🟡 Yellow - Caution

While no high-severity issues were found, a significant medium-severity issue was detected, indicating a need for data cleaning and standardization.

### Top Issues

*   **Medium Severity: Prefixes and Suffixes in Names**
    *   **Test:** `name_or_doctor_contains_prefix_or_suffix`
    *   **Table:** `healthcare_dataset`
    *   **Problem:** 2,870 rows in the `name` and `doctor` columns contain prefixes (e.g., "Mr.", "Dr.") or suffixes (e.g., "MD", "DDS").
    *   **Impact:** This complicates record matching and integration. For instance, a doctor might be listed as "Dr. Jane Doe" in one record and "Jane Doe MD" in another, leading to analytical errors.
    *   **Recommendation:** Implement a cleaning step to parse and remove these prefixes/suffixes from the name and doctor fields.

### Test Coverage Notes

*   **2 tests executed** on the `healthcare_dataset` table.
*   ✅ The high-severity test for **invalid date formats passed**, confirming that all admission and discharge dates are correctly formatted.
*   ❌ The medium-severity test for **name and doctor prefixes/suffixes failed**, highlighting the primary quality issue in this run.

### Suggested Production Guardrails

To maintain data quality, the following SQL check should be scheduled to run with each data load:

1.  **Detect Prefixes/Suffixes in Names and Doctors:** This check will prevent un-parsed name formats from entering the table.
    ```sql
    SELECT
      *
    FROM
      healthcare_dataset
    WHERE
      LOWER(name) LIKE 'mr. %'
      OR LOWER(name) LIKE 'dr. %'
      OR LOWER(name) LIKE LOWER('% md')
      OR LOWER(name) LIKE LOWER('% dds')
      OR LOWER(doctor) LIKE 'mr. %'
      OR LOWER(doctor) LIKE 'dr. %'
      OR LOWER(doctor) LIKE LOWER('% md')
      OR LOWER(doctor) LIKE LOWER('% dds')
    ```
