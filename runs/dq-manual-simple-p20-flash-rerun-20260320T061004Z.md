# Data Quality Report - dq-manual-simple-p20-flash-rerun-20260320T061004Z

Generated at: 2026-03-20 06:10:42 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P20-FLASH-RERUN`
- Event log: `runs/dq-manual-simple-p20-flash-rerun-20260320T061004Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | test_age_outliers | 1139 |
| MEDIUM | FAIL | healthcare_dataset | test_admission_after_discharge | 1135 |

## Detailed Findings
### 1. [CRITICAL/FAIL] test_age_outliers (healthcare_dataset)
- Why this matters: The profiling identified extreme outliers in the age column (e.g., 32000), indicating a lack of basic range validation for human lifespan.
- Issue count: **1139**
- Output truncated: **yes**

```sql
SELECT 
  name, 
  age 
FROM healthcare_dataset 
WHERE age < 0 OR age > 120;
```

Example rows:
```json
[
  {
    "name": "ChRISTopher BerG",
    "age": 39000
  },
  {
    "name": "aaRon MARtiNeZ",
    "age": 29000
  },
  {
    "name": "NicOlE RodriGUEz",
    "age": 25000
  }
]
```

### 2. [MEDIUM/FAIL] test_admission_after_discharge (healthcare_dataset)
- Why this matters: Validates logical consistency between admission and discharge dates. A discharge date occurring before an admission date is a data integrity error.
- Issue count: **1135**
- Output truncated: **yes**

```sql
SELECT 
  name, 
  date_of_admission, 
  discharge_date 
FROM healthcare_dataset 
WHERE date(date_of_admission) > date(discharge_date);
```

Example rows:
```json
[
  {
    "name": "ChRISTopher BerG",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2021-06-22"
  },
  {
    "name": "bRADlEY coMbS",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2021-06-06"
  },
  {
    "name": "JAMEs Ross",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2024-01-22"
  }
]
```

## Supervisor Narrative
Overall Verdict: RED. The healthcare_dataset contains over 1,100 critical age outliers (up to 52,500) and 1,135 logical date errors (placeholder '2099-12-31' for admission). Immediate intervention is required to fix input validation and clean existing records.
