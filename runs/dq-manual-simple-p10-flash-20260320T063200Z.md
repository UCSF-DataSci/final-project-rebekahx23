# Data Quality Report - dq-manual-simple-p10-flash-20260320T063200Z

Generated at: 2026-03-20 06:32:44 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P10-FLASH`
- Event log: `runs/dq-manual-simple-p10-flash-20260320T063200Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 2 |
| High | 0 |
| Medium | 0 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| CRITICAL | FAIL | healthcare_dataset | age_outlier | 1140 |
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission_date | 1133 |

## Detailed Findings
### 1. [CRITICAL/FAIL] age_outlier (healthcare_dataset)
- Why this matters: The `age` column contains values like `36500` which are far beyond a realistic human age and likely represent a data entry error (e.g., age recorded in days instead of years). Such outliers severely skew statistical analysis and demographic segmentation. This test identifies ages that are impossibly high (e.g., > 150) or negative, indicating a critical data quality issue.
- Issue count: **1140**
- Output truncated: **yes**

```sql
SELECT name, age FROM healthcare_dataset WHERE age IS NOT NULL AND (age < 0 OR age > 150);
```

Example rows:
```json
[
  {
    "name": "KAThEriNE SmiTH",
    "age": 23000
  },
  {
    "name": "kIm PenA",
    "age": 32000
  },
  {
    "name": "MiCH",
    "age": 43000
  }
]
```

### 2. [CRITICAL/FAIL] discharge_before_admission_date (healthcare_dataset)
- Why this matters: The `discharge_date` should logically always be on or after the `date_of_admission`. If `discharge_date` is earlier than `date_of_admission`, it indicates a critical data entry error or a logical inconsistency in the patient's record, which impacts patient stay calculations, billing, and overall reporting accuracy. This test assumes dates are in a format parsable by `julianday` (e.g., 'YYYY-MM-DD').
- Issue count: **1133**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "ChRISToPHEr BRiGhT",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2020-02-09"
  },
  {
    "name": "ANNE THOMPSoN",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2024-04-14"
  },
  {
    "name": "ANthONy reYEs",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-11-08"
  }
]
```

## Supervisor Narrative
**Data Quality Report: SIMPLE-P10-FLASH**

**Overall Verdict:** <span style="color:red">RED</span> - Critical data quality issues were identified that require immediate attention.

**Top Critical Issues:**
*   **`age_outlier` (healthcare_dataset):** 1140 instances of unrealistic patient ages (e.g., >150 or <0) were found. This indicates significant data entry errors that will severely impact any age-based analysis or demographic segmentation.
*   **`discharge_before_admission_date` (healthcare_dataset):** 1133 records were found where the discharge date was earlier than the admission date. This represents a critical logical inconsistency that will affect patient stay calculations, billing, and reporting accuracy.

**Test Coverage Notes:**
Two critical data quality tests were executed on the `healthcare_dataset` table, covering the `age` column for outliers and the logical consistency between `date_of_admission` and `discharge_date`. While these address fundamental data integrity, broader coverage for other identified potential risks, such as inconsistent casing and titles in the `name` field, and the `TEXT` data type for date columns, was not included in this run. Future quality runs should consider expanding test coverage to these areas for a more comprehensive assessment.

**Suggested Production Guardrails (SQL checks to schedule each load):**
To prevent recurrence of these critical issues, the following SQL checks should be implemented and scheduled to run with each data load:
1.  **Age Range Check:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE age IS NOT NULL AND (age < 0 OR age > 150);
    ```
    This check will identify any patient records with an `age` value that is less than 0 or greater than 150, flagging them as potential outliers.
2.  **Discharge Date Logic Check:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND julianday(discharge_date) < julianday(date_of_admission);
    ```
    This check ensures that the `discharge_date` is never earlier than the `date_of_admission`, assuming dates are stored in a format compatible with `julianday` (e.g., 'YYYY-MM-DD').
