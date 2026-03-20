# Data Quality Report - dq-manual-complex-p50-flash-20260320T055130Z

Generated at: 2026-03-20 05:52:25 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P50-FLASH`
- Event log: `runs/dq-manual-complex-p50-flash-20260320T055130Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | admission_discharge_date_logic_and_format | 555 |
| HIGH | FAIL | healthcare_dataset | gender_standardization_check | 555 |

## Detailed Findings
### 1. [CRITICAL/FAIL] admission_discharge_date_logic_and_format (healthcare_dataset)
- Why this matters: The `date_of_admission` and `discharge_date` columns are stored as text. This test identifies records where either date column cannot be parsed into a valid 'YYYY-MM-DD' date, or where the `discharge_date` logically occurs before the `date_of_admission`. Such inconsistencies are critical for accurate patient stay analysis.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE date(date_of_admission) IS NULL OR date(discharge_date) IS NULL OR julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "apRil SANTIAgO",
    "date_of_admission": "2021-01-30",
    "discharge_date": "2021-01-29"
  },
  {
    "name": "jEremY fRye",
    "date_of_admission": "2021-07-25",
    "discharge_date": "2021-07-24"
  },
  {
    "name": "mARissA mORa",
    "date_of_admission": "2022-05-17",
    "discharge_date": "2022-05-16"
  }
]
```

### 2. [HIGH/FAIL] gender_standardization_check (healthcare_dataset)
- Why this matters: The `gender` column exhibits inconsistent representations (e.g., 'Female', 'Male', 'F'). This test identifies records where the gender value is not one of the expected standardized full forms ('Female' or 'Male'), indicating a need for data standardization.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT name, gender FROM healthcare_dataset WHERE LOWER(gender) NOT IN ('female', 'male') AND gender IS NOT NULL;
```

Example rows:
```json
[
  {
    "name": "mr. KenNEth MoORE",
    "gender": "F"
  },
  {
    "name": "beThaNY MoOrE",
    "gender": "F"
  },
  {
    "name": "MariA JOHnStON",
    "gender": "M"
  }
]
```

## Supervisor Narrative
**Data Quality Report**

**Overall Verdict: RED** 🔴

**Summary of Findings:**
The data quality run identified significant issues across critical and high-severity checks. Out of 2 tests executed, both failed, indicating substantial data quality problems that require immediate attention.

**Top Critical/High Issues:**

*   **Critical Issue: `admission_discharge_date_logic_and_format` (555 issues)**
    *   **Description**: This test identified a high number of records (555) where the `date_of_admission` or `discharge_date` columns either contain invalid date formats (not 'YYYY-MM-DD') or, more critically, where the `discharge_date` occurs before the `date_of_admission`. This is a fundamental logical inconsistency that severely impacts the reliability of patient stay analysis and other time-sensitive metrics.
*   **High Issue: `gender_standardization_check` (555 issues)**
    *   **Description**: A substantial number of records (555) were found with inconsistent representations in the `gender` column. Values such as 'F' or 'M' are present instead of the expected standardized forms ('Female' or 'Male'). This inconsistency hinders accurate demographic analysis and reporting.

**Test Coverage Notes:**
The executed tests focused on two crucial aspects of data quality: the logical consistency and format of admission/discharge dates, and the standardization of gender representations. While the coverage is focused, the high number of issues found in both areas suggests a broad problem with data entry and validation for these fields. Further profiling might be needed to uncover other potential issues not covered by these specific checks.

**Suggested Production Guardrails (SQL checks to schedule with each data load):**

To prevent these issues from recurring, the following SQL checks should be implemented and scheduled as part of the data loading process. These checks can either block loads with invalid data or flag them for immediate correction.

1.  **For `admission_discharge_date_logic_and_format`:**
    ```sql
    -- Prevent discharge dates from being before admission dates or invalid date formats
    -- This assumes SQLite-compatible date functions. Adjust for other SQL dialects (e.g., TRY_CAST for PostgreSQL/SQL Server, TO_DATE for Oracle)
    SELECT COUNT(*)
    FROM healthcare_dataset
    WHERE
        date(date_of_admission) IS NULL OR
        date(discharge_date) IS NULL OR
        julianday(discharge_date) < julianday(date_of_admission);
    ```
    *   **Action if count > 0**: Fail the data load and alert for immediate data correction.

2.  **For `gender_standardization_check`:**
    ```sql
    -- Ensure gender values are standardized to 'Female' or 'Male'
    SELECT COUNT(*)
    FROM healthcare_dataset
    WHERE
        LOWER(gender) NOT IN ('female', 'male') AND gender IS NOT NULL;
    ```
    *   **Action if count > 0**: Fail the data load and alert for immediate data standardization, or implement a data transformation step to standardize values before loading.

Implementing these guardrails will help enforce data integrity at the point of ingestion and significantly improve the reliability of the `healthcare_dataset` table.
