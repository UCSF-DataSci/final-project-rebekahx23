# Data Quality Report - dq-manual-complex-p10-pro-20260320T061835Z

Generated at: 2026-03-20 06:20:15 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P10-PRO`
- Event log: `runs/dq-manual-complex-p10-pro-20260320T061835Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 0 |
| Low | 1 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| HIGH | FAIL | healthcare_dataset | discharge_before_admission | 555 |
| LOW | FAIL | healthcare_dataset | unrounded_billing_amount | 55500 |

## Detailed Findings
### 1. [HIGH/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: Ensures that the discharge date is not earlier than the admission date. Violating rows indicate a logical inconsistency or data entry error that invalidates patient timelines.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE date(discharge_date) < date(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "ChRISTopher mccLAiN",
    "age": 67,
    "gender": "Female",
    "blood_type": "O-",
    "medical_condition": "Arthritis",
    "date_of_admission": "2023-05-17",
    "doctor": "Maria Tran",
    "hospital": "Thomas-Huber",
    "insurance_provider": "Medicare",
    "billing_amount": 27309.436760697274,
    "room_number": 293,
    "admission_type": "Elective",
    "discharge_date": "2023-05-16",
    "medication": "Aspirin",
    "test_results": "Abnormal"
  },
  {
    "name": "jEssiCa GoNzAleS",
    "age": 57,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Hypertension",
    "date_of_admission": "2023-08-28",
    "doctor": "Kimberly Gonzalez",
    "hospital": "Jones and Jones, Turner",
    "insurance_provider": "Cigna",
    "billing_amount": 20545.871762829884,
    "room_number": 198,
    "admission_type": "Urgent",
    "discharge_date": "2023-08-27",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  },
  {
    "name": "lIsA LeWis",
    "age": 83,
    "gender": "Male",
    "blood_type": "O-",
    "medical_condition": "Asthma",
    "date_of_admission": "2021-11-13",
    "doctor": "Kevin Brown",
    "hospital": "Tran, and Ferrell Garcia",
    "insurance_provider": "Aetna",
    "billing_amount": 18198.058517853886,
    "room_number": 308,
    "admission_type": "Urgent",
    "discharge_date": "2021-11-12",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  }
]
```

### 2. [LOW/FAIL] unrounded_billing_amount (healthcare_dataset)
- Why this matters: Billing amounts represent currency and should ideally be rounded to 2 decimal places. This test flags high-precision floating point amounts that require standard financial rounding.
- Issue count: **55500**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE billing_amount != ROUND(billing_amount, 2);
```

Example rows:
```json
[
  {
    "name": "Bobby JacksOn",
    "age": 30,
    "gender": "Male",
    "blood_type": "B-",
    "medical_condition": "Cancer",
    "date_of_admission": "2024-01-31",
    "doctor": "Matthew Smith",
    "hospital": "Sons and Miller",
    "insurance_provider": "Blue Cross",
    "billing_amount": 18856.281305978155,
    "room_number": 328,
    "admission_type": "Urgent",
    "discharge_date": "2024-02-02",
    "medication": "Paracetamol",
    "test_results": "Normal"
  },
  {
    "name": "LesLie TErRy",
    "age": 62,
    "gender": "Male",
    "blood_type": "A+",
    "medical_condition": "Obesity",
    "date_of_admission": "2019-08-20",
    "doctor": "Samantha Davies",
    "hospital": "Kim Inc",
    "insurance_provider": "Medicare",
    "billing_amount": 33643.327286577885,
    "room_number": 265,
    "admission_type": "Emergency",
    "discharge_date": "2019-08-26",
    "medication": "Ibuprofen",
    "test_results": "Inconclusive"
  },
  {
    "name": "DaNnY sMitH",
    "age": 76,
    "gender": "Female",
    "blood_type": "A-",
    "medical_condition": "Obesity",
    "date_of_admission": "2022-09-22",
    "doctor": "Tiffany Mitchell",
    "hospital": "Cook PLC",
    "insurance_provider": "Aetna",
    "billing_amount": 27955.096078842456,
    "room_number": 205,
    "admission_type": "Emergency",
    "discharge_date": "2022-10-07",
    "medication": "Aspirin",
    "test_results": "Normal"
  }
]
```

## Supervisor Narrative
## Data Quality Supervisor Report: `healthcare_dataset`

**Overall Verdict:** 🔴 **RED**
The dataset contains critical logical inconsistencies in its temporal patient data that must be resolved before downstream consumption.

**Top Critical/High Issues:**
1. **Invalid Patient Timelines (High Severity):** 
   - **Test:** `discharge_before_admission`
   - **Finding:** 555 rows have a `discharge_date` occurring prior to the `date_of_admission`. 
   - **Impact:** This invalidates metrics tracking length of stay, patient timelines, and capacity planning. It strongly indicates data entry errors or reversed date mappings in the source system.

**Other Notable Findings:**
2. **Financial Precision (Low Severity):**
   - **Test:** `unrounded_billing_amount`
   - **Finding:** 55,500 rows contain `billing_amount` values with high-precision floating points rather than standard currency formats.
   - **Impact:** Could lead to visual reporting issues or slight inconsistencies in financial aggregation. 

3. **Inconsistent Casing (Profiler Observation):**
   - The `name` column features severely inconsistent capitalization and unstructured titles/suffixes (e.g., "mR. robert pItts"). This requires standardization for robust patient matching.

**Test Coverage Notes:**
- **Logic & Consistency:** Covered temporal dependencies between admission and discharge dates.
- **Financial Standards:** Verified currency rounding rules for the billing amounts.
- **Gap:** No tests currently enforce string casing formats on textual features or validate that blood types conform strictly to a predefined list.

**Suggested Production Guardrails:**
To prevent corrupted records from impacting analytics layers, the following SQL checks should be scheduled in the data pipeline:

1. **Length of Stay Check (Blocking/Quarantine):**
   ```sql
   -- Reject or quarantine rows where discharge precedes admission
   SELECT * FROM healthcare_dataset 
   WHERE date(discharge_date) < date(date_of_admission);
   ```

2. **Billing Rounding (Transform / Soft Check):**
   ```sql
   -- Flag rows needing rounding or apply a standard transformation
   SELECT * FROM healthcare_dataset 
   WHERE billing_amount != ROUND(billing_amount, 2);
   ```
   *Recommendation:* Inject a transformation step (`ROUND(billing_amount, 2)`) during the load process rather than purely testing.
