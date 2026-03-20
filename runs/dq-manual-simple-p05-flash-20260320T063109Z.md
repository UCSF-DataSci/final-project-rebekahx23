# Data Quality Report - dq-manual-simple-p05-flash-20260320T063109Z

Generated at: 2026-03-20 06:31:48 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P05-FLASH`
- Event log: `runs/dq-manual-simple-p05-flash-20260320T063109Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | age_exceeds_plausible_human_lifespan | 1140 |
| CRITICAL | FAIL | healthcare_dataset | admission_or_discharge_date_invalid | 1133 |

## Detailed Findings
### 1. [CRITICAL/FAIL] age_exceeds_plausible_human_lifespan (healthcare_dataset)
- Why this matters: The 'age' column contains values that exceed the plausible human lifespan (e.g., 35000 years). This indicates severe data entry errors that will drastically skew statistical analysis and render the data unreliable for age-related insights.
- Issue count: **1140**
- Output truncated: **yes**

```sql
SELECT name, age, date_of_admission FROM healthcare_dataset WHERE age > 120;
```

Example rows:
```json
[
  {
    "name": "KAThEriNE SmiTH",
    "age": 23000,
    "date_of_admission": "2021-06-09"
  },
  {
    "name": "kIm PenA",
    "age": 32000,
    "date_of_admission": "2020-08-11"
  },
  {
    "name": "MiCH",
    "age": 43000,
    "date_of_admission": "2022-06-03"
  }
]
```

### 2. [CRITICAL/FAIL] admission_or_discharge_date_invalid (healthcare_dataset)
- Why this matters: Records exist where the 'date_of_admission' is set in the future, which is logically impossible. Additionally, some records show a 'discharge_date' that occurs before the 'date_of_admission', indicating a fundamental logical inconsistency in the patient journey timeline. Both issues point to critical data entry errors.
- Issue count: **1133**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE julianday(date_of_admission) > julianday('now') OR julianday(discharge_date) < julianday(date_of_admission);
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
**Data Quality Report**

**Overall Verdict: 🔴 RED**

This run indicates severe data quality issues in the `healthcare_dataset` table, with all executed critical tests failing. Immediate action is required to rectify these fundamental data inconsistencies.

**Highest-Risk Findings:**

1.  **age_exceeds_plausible_human_lifespan** (Critical): 1140 issues found. Patient ages exceed a plausible human lifespan, suggesting severe data entry errors that will skew analysis.
2.  **admission_or_discharge_date_invalid** (Critical): 1133 issues found. Logically impossible admission or discharge dates (e.g., admission in the future, discharge before admission) highlight fundamental data inconsistencies in patient timelines.

**Test Coverage Notes:**

A total of 2 tests were executed, and both failed, indicating a complete failure of the critical data quality checks implemented in this run. This limited set of tests focused on critical validation rules and revealed significant underlying problems. Further, comprehensive testing across all columns is recommended once these critical issues are addressed.

**Suggested Production Guardrails (SQL checks to schedule each load):**

To prevent these critical issues from recurring, implement the following SQL checks to run prior to or during each data load:

1.  **Age Validity Check:**
    ```sql
    SELECT name, age, date_of_admission FROM healthcare_dataset WHERE age > 120;
    ```
2.  **Admission/Discharge Date Consistency Check:**
    ```sql
    SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE julianday(date_of_admission) > julianday('now') OR julianday(discharge_date) < julianday(date_of_admission);
    ```
These checks should block data loads that contain records violating these critical business rules until the issues are resolved.
