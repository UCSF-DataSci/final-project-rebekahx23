# Data Quality Report - dq-manual-simple-p20-pro-20260320T050445Z

Generated at: 2026-03-20 05:06:02 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P20-PRO`
- Event log: `runs/dq-manual-simple-p20-pro-20260320T050445Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission | 1133 |
| CRITICAL | FAIL | healthcare_dataset | unrealistic_patient_age | 1129 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: The data profile noted that a patient's discharge date was recorded before their admission date. This is a logical impossibility that violates the integrity of the patient's timeline. This test identifies all records where this fundamental chronological order is broken.
- Issue count: **1133**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "Jeffrey tuRNER",
    "age": 85,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Obesity",
    "date_of_admission": "2099-12-31",
    "doctor": "Matthew Carter",
    "hospital": "Kim Rosario, and Hammond",
    "insurance_provider": "Aetna",
    "billing_amount": 39957.94062222976,
    "room_number": 211,
    "admission_type": "Urgent",
    "discharge_date": "2020-06-01",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  },
  {
    "name": "jEssiCa GoNzAleS",
    "age": 57,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Hypertension",
    "date_of_admission": "2099-12-31",
    "doctor": "Kimberly Gonzalez",
    "hospital": "Jones and Jones, Turner",
    "insurance_provider": "Cigna",
    "billing_amount": 20545.871762829884,
    "room_number": 198,
    "admission_type": "Urgent",
    "discharge_date": "2023-09-16",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  },
  {
    "name": "dr. MATthEW wilkinS",
    "age": 80,
    "gender": "Male",
    "blood_type": "A-",
    "medical_condition": "Cancer",
    "date_of_admission": "2099-12-31",
    "doctor": "Seth Nelson",
    "hospital": "PLC Anderson",
    "insurance_provider": "Blue Cross",
    "billing_amount": 22401.550353437575,
    "room_number": 242,
    "admission_type": "Elective",
    "discharge_date": "2021-07-24",
    "medication": "Lipitor",
    "test_results": "Inconclusive"
  }
]
```

### 2. [CRITICAL/FAIL] unrealistic_patient_age (healthcare_dataset)
- Why this matters: The data profile identified an extreme outlier age of 27500, which is not a valid human age. This test checks for any ages outside the plausible human range of 0 to 120 years to detect significant data entry errors or corruption.
- Issue count: **1129**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE age IS NOT NULL AND (age < 0 OR age > 120);
```

Example rows:
```json
[
  {
    "name": "EMILY JOHNSOn",
    "age": 28000,
    "gender": "Male",
    "blood_type": "A+",
    "medical_condition": "Asthma",
    "date_of_admission": "2023-12-20",
    "doctor": "Taylor Newton",
    "hospital": "Nunez-Humphrey",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 48145.11095104189,
    "room_number": 389,
    "admission_type": "Urgent",
    "discharge_date": "2023-12-24",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  },
  {
    "name": "dANIEL schmIdt",
    "age": 41500,
    "gender": "Male",
    "blood_type": "B+",
    "medical_condition": "Asthma",
    "date_of_admission": "2022-11-15",
    "doctor": "Denise Galloway",
    "hospital": "Hammond Ltd",
    "insurance_provider": "Cigna",
    "billing_amount": 23762.203579059587,
    "room_number": 465,
    "admission_type": "Elective",
    "discharge_date": "2022-11-22",
    "medication": "Penicillin",
    "test_results": "Normal"
  },
  {
    "name": "ChAd MorEnO",
    "age": 43500,
    "gender": "Male",
    "blood_type": "AB+",
    "medical_condition": "Hypertension",
    "date_of_admission": "2020-08-26",
    "doctor": "Connie Boyd",
    "hospital": "Inc Skinner",
    "insurance_provider": "Aetna",
    "billing_amount": 46814.011195111656,
    "room_number": 134,
    "admission_type": "Urgent",
    "discharge_date": "2020-08-27",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  }
]
```

## Supervisor Narrative
**Overall Verdict: Red**

This data quality run on the `healthcare_dataset` has surfaced critical integrity issues that require immediate attention. The overall health of the dataset is poor, and it should not be used for production analytics or decision-making in its current state.

**Top Critical Issues:**
- `unrealistic_patient_age` (Critical): A significant number of records (1,129) were found with patient ages outside the plausible human range of 0-120 years. This indicates a systemic issue with data entry or data corruption.
- `discharge_before_admission` (Critical): We found 1,133 instances where a patient's discharge date is chronologically before their admission date. This is a logical impossibility and severely compromises the integrity of patient timelines.

**Test Coverage Notes:**
The tests were focused on the most severe data anomalies identified during profiling. While we have confirmed critical issues related to data accuracy and integrity, we have not yet addressed lower-severity issues like inconsistent string formatting in `name` and `hospital` columns, which could impact record linkage and entity resolution.

**Suggested Production Guardrails:**
To prevent these critical issues from recurring in production, we recommend implementing the following SQL checks as blocking guardrails in your data loading pipeline. These should be run with each new data batch:

1.  **Block loads with unrealistic ages:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE age IS NOT NULL AND (age < 0 OR age > 120);
    ```
2.  **Block loads with impossible timelines:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE julianday(discharge_date) < julianday(date_of_admission);
    ```
If either of these queries returns a count greater than zero, the data load should be immediately halted and an alert triggered for manual review.
