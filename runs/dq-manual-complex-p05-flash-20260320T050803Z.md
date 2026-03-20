# Data Quality Report - dq-manual-complex-p05-flash-20260320T050803Z

Generated at: 2026-03-20 05:08:44 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P05-FLASH`
- Event log: `runs/dq-manual-complex-p05-flash-20260320T050803Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission | 555 |
| HIGH | FAIL | healthcare_dataset | negative_billing_amount | 108 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: The discharge date for a patient cannot logically occur before their admission date. This indicates a severe data entry error or logical inconsistency that impacts patient timelines and billing, as highlighted by the 'johN becKEr' example in the profile.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "adrIENNE bEll",
    "date_of_admission": "2022-09-19",
    "discharge_date": "2022-09-18"
  },
  {
    "name": "DIAnE brAnch",
    "date_of_admission": "2020-05-30",
    "discharge_date": "2020-05-29"
  },
  {
    "name": "TrACy BUrke",
    "date_of_admission": "2020-12-05",
    "discharge_date": "2020-12-04"
  }
]
```

### 2. [HIGH/FAIL] negative_billing_amount (healthcare_dataset)
- Why this matters: Billing amounts should logically be non-negative. A negative billing amount suggests a data entry error, a processing error, or an unexpected financial transaction that needs immediate investigation.
- Issue count: **108**
- Output truncated: **no**

```sql
SELECT name, billing_amount FROM healthcare_dataset WHERE billing_amount IS NOT NULL AND billing_amount < 0;
```

Example rows:
```json
[
  {
    "name": "ashLEy ERIcKSoN",
    "billing_amount": -502.50781270094785
  },
  {
    "name": "CHRisTOPHer wEiss",
    "billing_amount": -1018.2453712282881
  },
  {
    "name": "AsHley WaRnER",
    "billing_amount": -306.3649251412676
  }
]
```

## Supervisor Narrative
**Data Quality Report: COMPLEX-P05-FLASH**

**Overall Verdict: 🔴 Red**

The data quality run identified significant critical and high-severity issues. Immediate attention is required to address these data inconsistencies.

**Top Critical and High Issues:**

*   **Critical Failure: `discharge_before_admission`**
    *   **Issues Found:** 555
    *   **Description:** The discharge date for a patient occurred before their admission date. This is a severe logical error impacting patient timelines and billing accuracy.
    *   **Example Rows:** `{'name': 'adrIENNE bEll', 'date_of_admission': '2022-09-19', 'discharge_date': '2022-09-18'}`
*   **High Failure: `negative_billing_amount`**
    *   **Issues Found:** 108
    *   **Description:** Billing amounts should always be non-negative. Negative values indicate data entry errors or unexpected financial processing issues.
    *   **Example Rows:** `{'name': 'ashLEy ERIcKSoN', 'billing_amount': -502.50781270094785}`

**Test Coverage Notes:**

All 2 planned data quality tests were successfully executed, covering critical aspects of date consistency and financial data integrity.

**Suggested Production Guardrails (SQL checks to schedule with each data load):**

To prevent these issues from recurring, implement the following SQL checks as automated guardrails before or during each data load into the `healthcare_dataset` table:

1.  **Check for Discharge Date Before Admission Date:**
    ```sql
    SELECT name, date_of_admission, discharge_date
    FROM healthcare_dataset
    WHERE date_of_admission IS NOT NULL
      AND discharge_date IS NOT NULL
      AND julianday(discharge_date) < julianday(date_of_admission);
    ```

2.  **Check for Negative Billing Amounts:**
    ```sql
    SELECT name, billing_amount
    FROM healthcare_dataset
    WHERE billing_amount IS NOT NULL
      AND billing_amount < 0;
    ```
