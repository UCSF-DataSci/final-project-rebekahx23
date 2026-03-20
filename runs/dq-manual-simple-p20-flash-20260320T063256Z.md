# Data Quality Report - dq-manual-simple-p20-flash-20260320T063256Z

Generated at: 2026-03-20 06:33:38 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P20-FLASH`
- Event log: `runs/dq-manual-simple-p20-flash-20260320T063256Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | age_outlier_above_plausible_max | 1140 |
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission_date | 1133 |

## Detailed Findings
### 1. [CRITICAL/FAIL] age_outlier_above_plausible_max (healthcare_dataset)
- Why this matters: The `age` column contains values that are physically impossible for a human (e.g., 49000). This indicates a severe data entry error or corruption, rendering such records highly unreliable for analysis. A plausible maximum age is typically around 120-150 years.
- Issue count: **1140**
- Output truncated: **yes**

```sql
SELECT name, age FROM healthcare_dataset WHERE age > 150;
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
- Why this matters: A patient's discharge date must logically be on or after their admission date. Instances where the discharge date precedes the admission date indicate severe data integrity issues that invalidate the temporal sequence of care.
- Issue count: **1133**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE julianday(discharge_date) < julianday(date_of_admission);
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
**Data Quality Report for `healthcare_dataset`**

**Overall Verdict:** RED

**Top Critical Issues:**
*   **Discharge Date Before Admission Date (1133 issues):** A significant number of records show a logical inconsistency where the `discharge_date` occurs before the `date_of_admission`. This indicates severe data integrity problems, making the temporal sequence of patient care unreliable.
*   **Age Outliers Above Plausible Maximum (1140 issues):** A large number of records contain `age` values exceeding 150, which are physically impossible. This suggests critical data entry errors or corruption, severely impacting the reliability of age-related analysis.

**Test Coverage Notes:**
Two critical data quality tests were executed: `discharge_before_admission_date` and `age_outlier_above_plausible_max`, both of which identified severe issues.
However, several other risk areas identified during profiling were *not* explicitly covered by dedicated tests in this run. These include:
*   Inconsistent capitalization and presence of professional titles in `name` and `doctor` fields.
*   The presence of erroneous future dates (e.g., `2099-12-31`) in `date_of_admission` and `discharge_date` (beyond the logical inconsistency of discharge before admission).
*   Negative values in the `billing_amount` column.
*   Varying and complex formats for `hospital` names.

**Suggested Production Guardrails (SQL checks to schedule with each data load):**
To prevent recurrence of these critical issues, the following SQL checks should be implemented and run as part of the data loading process for `healthcare_dataset`:

1.  **Discharge Date Not Before Admission Date:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE julianday(discharge_date) < julianday(date_of_admission);
    ```
    *Expected result: 0 issues*

2.  **Plausible Age Maximum (e.g., <= 150):**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE age > 150;
    ```
    *Expected result: 0 issues*

3.  **Admission and Discharge Dates Not in the Future:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE date_of_admission > CURRENT_DATE OR discharge_date > CURRENT_DATE;
    ```
    *Expected result: 0 issues*

4.  **Positive Billing Amounts:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE billing_amount < 0;
    ```
    *Expected result: 0 issues*
