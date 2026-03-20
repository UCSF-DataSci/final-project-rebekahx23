# Data Quality Report - dq-manual-simple-p50-flash-20260320T062856Z

Generated at: 2026-03-20 06:29:19 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P50-FLASH`
- Event log: `runs/dq-manual-simple-p50-flash-20260320T062856Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | detect_invalid_age_outliers | 1135 |
| HIGH | FAIL | healthcare_dataset | validate_admission_discharge_sequence | 1134 |

## Detailed Findings
### 1. [CRITICAL/FAIL] detect_invalid_age_outliers (healthcare_dataset)
- Why this matters: The 'age' column contains values that exceed any reasonable human lifespan (e.g., > 120), likely representing data corruption or placeholder codes.
- Issue count: **1135**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE age < 0 OR age > 120;
```

Example rows:
```json
[
  {
    "name": "LArry rodgeRs",
    "age": 21500,
    "gender": "Female",
    "blood_type": "B-",
    "medical_condition": "Hypertension",
    "date_of_admission": "2022-08-03",
    "doctor": "Eric Kelly",
    "hospital": "and Mason Smith Chase,",
    "insurance_provider": "Cigna",
    "billing_amount": 5517.393642223992,
    "room_number": 113,
    "admission_type": "Elective",
    "discharge_date": "2022-08-10",
    "medication": "Aspirin",
    "test_results": "Inconclusive"
  },
  {
    "name": "johN THoMaS",
    "age": 47000,
    "gender": "Female",
    "blood_type": "A+",
    "medical_condition": "Arthritis",
    "date_of_admission": "2021-11-13",
    "doctor": "Mark Padilla",
    "hospital": "Simpson-Mccall",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 29850.879728183794,
    "room_number": 131,
    "admission_type": "Emergency",
    "discharge_date": "2021-12-07",
    "medication": "Paracetamol",
    "test_results": "Inconclusive"
  },
  {
    "name": "apRil SANTIAgO",
    "age": 26500,
    "gender": "Female",
    "blood_type": "B-",
    "medical_condition": "Diabetes",
    "date_of_admission": "2021-01-30",
    "doctor": "Jacob Rich",
    "hospital": "Jones-Scott",
    "insurance_provider": "Cigna",
    "billing_amount": 2305.139139538494,
    "room_number": 249,
    "admission_type": "Emergency",
    "discharge_date": "2021-02-04",
    "medication": "Penicillin",
    "test_results": "Inconclusive"
  }
]
```

### 2. [HIGH/FAIL] validate_admission_discharge_sequence (healthcare_dataset)
- Why this matters: Ensures that the discharge date is not chronologically before the date of admission, which is logically impossible for a medical record.
- Issue count: **1134**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE date(discharge_date) < date(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "COURTNey HOdGes",
    "age": 57,
    "gender": "Male",
    "blood_type": "AB-",
    "medical_condition": "Obesity",
    "date_of_admission": "2099-12-31",
    "doctor": "Brenda Lopez",
    "hospital": "Meyer-Hill",
    "insurance_provider": "Medicare",
    "billing_amount": 40693.35422395354,
    "room_number": 430,
    "admission_type": "Emergency",
    "discharge_date": "2021-12-09",
    "medication": "Aspirin",
    "test_results": "Abnormal"
  },
  {
    "name": "nATAliE sTANtoN",
    "age": 80,
    "gender": "Male",
    "blood_type": "B+",
    "medical_condition": "Asthma",
    "date_of_admission": "2099-12-31",
    "doctor": "Tara Moreno",
    "hospital": "Perry Little, and Moore",
    "insurance_provider": "Medicare",
    "billing_amount": 29221.340207679114,
    "room_number": 208,
    "admission_type": "Emergency",
    "discharge_date": "2020-09-17",
    "medication": "Paracetamol",
    "test_results": "Inconclusive"
  },
  {
    "name": "miCHAeL TayloR",
    "age": 29,
    "gender": "Male",
    "blood_type": "O-",
    "medical_condition": "Asthma",
    "date_of_admission": "2099-12-31",
    "doctor": "Erica Mccormick",
    "hospital": "Donaldson-Frey",
    "insurance_provider": "Medicare",
    "billing_amount": 41939.11993669633,
    "room_number": 453,
    "admission_type": "Elective",
    "discharge_date": "2020-03-26",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  }
]
```

## Supervisor Narrative
The data quality audit of the `healthcare_dataset` resulted in a **red (failed)** verdict due to significant data corruption.

### **Summary of Findings**
| Test Name | Severity | Status | Issue Count | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `detect_invalid_age_outliers` | Critical | Fail | 1,135 | 'age' values exceed reasonable human lifespan (> 120). |
| `validate_admission_discharge_sequence` | High | Fail | 1,134 | Discharge date is chronologically before the admission date. |

### **Highest-Risk Observations**
*   **Age Data Corruption:** A substantial number of records contain non-human ages (e.g., `21500`, `51500`), confirming systemic data quality issues.
*   **Logical Date Errors:** A widespread issue exists where `2099-12-31` is used as a placeholder in the `date_of_admission` field, causing downstream logical failures where the discharge date incorrectly precedes the admission date.

### **Production Guardrails (SQL Checks)**
To prevent further data ingestion of corrupted records, the following SQL checks should be integrated into the ETL pipeline:

1.  **Age Validation:**
    `SELECT COUNT(*) FROM healthcare_dataset WHERE age < 0 OR age > 120;`
2.  **Date Sequence Validation:**
    `SELECT COUNT(*) FROM healthcare_dataset WHERE date(discharge_date) < date(date_of_admission);`
3.  **Placeholder Date Detection:**
    `SELECT COUNT(*) FROM healthcare_dataset WHERE date_of_admission = '2099-12-31';`

**Recommendations:** Immediate data sanitization is required for the `age` column. The `2099-12-31` placeholder should be identified, and records with this value should be either re-evaluated, purged, or marked as missing data to maintain longitudinal data integrity.
