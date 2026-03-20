# Data Quality Report - dq-manual-simple-p20-flash-20260320T045919Z

Generated at: 2026-03-20 05:00:06 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P20-FLASH`
- Event log: `runs/dq-manual-simple-p20-flash-20260320T045919Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | admission_after_discharge_date | 1133 |
| HIGH | FAIL | healthcare_dataset | missing_patient_name | 1141 |

## Detailed Findings
### 1. [CRITICAL/FAIL] admission_after_discharge_date (healthcare_dataset)
- Why this matters: The admission date cannot logically occur after the discharge date. This indicates a severe data entry or processing error, making the entire patient stay record unreliable and potentially impacting billing, length-of-stay calculations, and patient care timelines.
- Issue count: **1133**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date, doctor, hospital FROM healthcare_dataset WHERE julianday(date_of_admission) > julianday(discharge_date);
```

Example rows:
```json
[
  {
    "name": "Jeffrey tuRNER",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2020-06-01",
    "doctor": "Matthew Carter",
    "hospital": "Kim Rosario, and Hammond"
  },
  {
    "name": "jEssiCa GoNzAleS",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-09-16",
    "doctor": "Kimberly Gonzalez",
    "hospital": "Jones and Jones, Turner"
  },
  {
    "name": "dr. MATthEW wilkinS",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2021-07-24",
    "doctor": "Seth Nelson",
    "hospital": "PLC Anderson"
  }
]
```

### 2. [HIGH/FAIL] missing_patient_name (healthcare_dataset)
- Why this matters: Patient records should always include a name for proper identification, tracking, and reporting. Missing names lead to incomplete data, difficulties in linking records, and potential patient safety issues.
- Issue count: **1141**
- Output truncated: **yes**

```sql
SELECT date_of_admission, discharge_date, doctor, hospital FROM healthcare_dataset WHERE name IS NULL OR TRIM(name) = '';
```

Example rows:
```json
[
  {
    "date_of_admission": "2020-01-21",
    "discharge_date": "2020-02-09",
    "doctor": "Gregory Smith",
    "hospital": "Williams-Davis"
  },
  {
    "date_of_admission": "2020-01-17",
    "discharge_date": "2020-02-10",
    "doctor": "Lynn Young",
    "hospital": "Poole Inc"
  },
  {
    "date_of_admission": "2020-05-08",
    "discharge_date": "2020-06-01",
    "doctor": "Jennifer Larson",
    "hospital": "Khan, and Rodriguez Fischer"
  }
]
```

## Supervisor Narrative
**Data Quality Report: healthcare_dataset**

**Overall Verdict: 🔴 Red**

All 2 executed data quality tests failed, indicating significant data integrity issues within the `healthcare_dataset` table. Immediate attention is required to address these critical and high-severity findings.

**Top Issues:**

*   **Critical: `admission_after_discharge_date` (1133 issues)**
    This is the most severe finding. There are 1133 instances where the `date_of_admission` is *after* the `discharge_date`. This logical inconsistency renders these patient records highly unreliable for any analysis, reporting, or operational processes such as billing, length-of-stay calculations, and patient care timelines. The sample data shows a recurring `date_of_admission` of '2099-12-31', strongly suggesting a placeholder or erroneous default value.

*   **High: `missing_patient_name` (1141 issues)**
    A substantial number of patient records (1141) are missing a `name`. This high-severity issue severely impacts the ability to uniquely identify, track, and report on patients, leading to incomplete data and potential patient safety concerns.

**Test Coverage Notes:**

This data quality run executed 2 tests, focusing on critical date logic and the completeness of patient identification. While these tests revealed significant issues, it's important to note that the coverage is specific to these identified risk areas. Further profiling and testing may uncover additional quality concerns within other columns (e.g., inconsistent casing in names/doctors, varied hospital naming conventions).

**Suggested Production Guardrails:**

To prevent these issues from recurring and to ensure data quality with each load, the following SQL checks should be scheduled:

1.  **Prevent Admission Date After Discharge Date (Critical):**
    This check should be run *before* or *during* each data load to ensure the temporal integrity of patient admission and discharge records. Records failing this check should either be rejected or flagged for immediate manual correction.

    ```sql
    SELECT name, date_of_admission, discharge_date, doctor, hospital
    FROM healthcare_dataset
    WHERE julianday(date_of_admission) > julianday(discharge_date);
    ```

2.  **Ensure Patient Name Completeness (High):**
    This check should be implemented to ensure that all new or updated patient records contain a valid name. Records with missing names should be flagged for correction or prevented from being inserted/updated until a name is provided.

    ```sql
    SELECT date_of_admission, discharge_date, doctor, hospital
    FROM healthcare_dataset
    WHERE name IS NULL OR TRIM(name) = '';
    ```
