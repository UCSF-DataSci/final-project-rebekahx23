# Data Quality Report - dq-manual-complex-p10-pro-20260320T054327Z

Generated at: 2026-03-20 05:44:45 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P10-PRO`
- Event log: `runs/dq-manual-complex-p10-pro-20260320T054327Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 1 |
| High | 0 |
| Medium | 1 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission | 555 |
| MEDIUM | FAIL | healthcare_dataset | hospital_name_trailing_patterns | 10378 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: The discharge date cannot be before the admission date. This indicates a critical data entry error that invalidates the patient's stay record and corrupts metrics like length of stay. The date columns are stored as TEXT and must be converted for comparison.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT
  name,
  date_of_admission,
  discharge_date
FROM healthcare_dataset
WHERE
  date(discharge_date) < date(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "CHrisTInA MARtinez",
    "date_of_admission": "2021-12-28",
    "discharge_date": "2021-12-27"
  },
  {
    "name": "JOsEph fOstER",
    "date_of_admission": "2019-09-11",
    "discharge_date": "2019-09-10"
  },
  {
    "name": "mIcHael anDeRson",
    "date_of_admission": "2019-08-16",
    "discharge_date": "2019-08-15"
  }
]
```

### 2. [MEDIUM/FAIL] hospital_name_trailing_patterns (healthcare_dataset)
- Why this matters: Hospital names ending with patterns like a trailing comma or conjunction (e.g., ', and') suggest that the data was improperly parsed or truncated. This can lead to incorrect grouping and analysis of hospital data.
- Issue count: **10378**
- Output truncated: **yes**

```sql
SELECT
  hospital
FROM healthcare_dataset
WHERE
  RTRIM(hospital) LIKE '%,'
  OR LOWER(RTRIM(hospital)) LIKE '% and';
```

Example rows:
```json
[
  {
    "hospital": "Hernandez Rogers and Vang,"
  },
  {
    "hospital": "Powell Robinson and Valdez,"
  },
  {
    "hospital": "Sons Rich and"
  }
]
```

## Supervisor Narrative
Executive Summary: Data Quality Run on `healthcare_dataset`

*   **Overall Verdict**: **Red**
    *   *Rationale*: A critical test failed, indicating severe data integrity issues that will impact downstream analysis and reporting. The dataset in its current state is not reliable.

*   **Top Issues**
    *   **(Critical)** `discharge_before_admission`: 1 test failed with 555 records where the patient's discharge date is recorded as being before their admission date. This represents a fundamental flaw in the patient stay records.
    *   **(Medium)** `hospital_name_trailing_patterns`: 1 test failed with 10,378 records where hospital names have trailing conjunctions or commas (e.g., "Sons Watson and", "Hernandez Rogers and Vang,"). This suggests a systemic data parsing or extraction error.

*   **Test Coverage Notes**
    *   This run focused on critical logical validation (date sequencing) and common parsing errors based on initial data profiling.
    *   Further quality risks were identified during profiling but not tested in this run, including inconsistent casing in `name` and `doctor` columns, and the storage of dates as TEXT instead of native DATE types. We recommend adding tests for these in subsequent runs.

*   **Suggested Production Guardrails**
    *   To prevent these issues in future data loads, the following SQL checks should be integrated into your production pipeline and configured to halt the process if they return any rows:
    1.  **Check for Invalid Discharge Dates**:
        ```sql
        SELECT
          name,
          date_of_admission,
          discharge_date
        FROM healthcare_dataset
        WHERE
          date(discharge_date) < date(date_of_admission);
        ```
    2.  **Check for Malformed Hospital Names**:
        ```sql
        SELECT
          hospital
        FROM healthcare_dataset
        WHERE
          RTRIM(hospital) LIKE '%,'
          OR LOWER(RTRIM(hospital)) LIKE '% and';
        ```
