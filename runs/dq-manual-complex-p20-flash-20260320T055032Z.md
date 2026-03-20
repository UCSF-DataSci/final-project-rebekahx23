# Data Quality Report - dq-manual-complex-p20-flash-20260320T055032Z

Generated at: 2026-03-20 05:51:18 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P20-FLASH`
- Event log: `runs/dq-manual-complex-p20-flash-20260320T055032Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | billing_amount_must_be_non_negative | 108 |
| HIGH | FAIL | healthcare_dataset | discharge_date_after_admission_date | 555 |

## Detailed Findings
### 1. [CRITICAL/FAIL] billing_amount_must_be_non_negative (healthcare_dataset)
- Why this matters: Billing amounts should always be non-negative. A negative value indicates a data entry error or a fundamental issue in financial record-keeping, which can severely impact financial analysis and reporting.
- Issue count: **108**
- Output truncated: **no**

```sql
SELECT name, billing_amount FROM healthcare_dataset WHERE billing_amount < 0
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

### 2. [HIGH/FAIL] discharge_date_after_admission_date (healthcare_dataset)
- Why this matters: The discharge date must logically be on or after the admission date. A discharge date occurring before the admission date indicates a critical logical inconsistency, affecting length-of-stay calculations and patient journey analysis.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND julianday(discharge_date) < julianday(date_of_admission)
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

## Supervisor Narrative
**Data Quality Report: healthcare_dataset**

**Overall Verdict: Red** 🔴

The `healthcare_dataset` exhibits significant data quality issues, with critical and high-severity tests failing during this run. Immediate action is required to address these inconsistencies.

**Highest-Risk Findings:**

*   **Critical Severity:** The `billing_amount_must_be_non_negative` test failed, identifying **108 instances** where the `billing_amount` was a negative value. This is a severe data integrity issue that can profoundly impact financial reporting and analysis.
*   **High Severity:** The `discharge_date_after_admission_date` test failed, uncovering **555 cases** where the `discharge_date` occurred before the `date_of_admission`. This represents a critical logical inconsistency, compromising the accuracy of patient journey analysis and length-of-stay calculations.

**Test Coverage Notes:**

This data quality run included 2 tests focusing on critical data integrity and logical consistency. While these tests identified significant issues, the overall test coverage for the `healthcare_dataset` remains limited. The initial profiling also highlighted potential issues in text fields like `name`, `doctor`, and `hospital` due to inconsistent formatting and naming conventions. Future data quality efforts should expand to cover these areas for a more comprehensive assessment.

**Suggested Production Guardrails:**

To prevent the recurrence of these critical and high-severity issues, the following SQL checks should be implemented and scheduled before each data load into the `healthcare_dataset` table:

1.  **Billing Amount Non-Negativity Check:**
    ```sql
    ALTER TABLE healthcare_dataset
    ADD CONSTRAINT chk_billing_amount_non_negative
    CHECK (billing_amount >= 0);
    ```
    *Alternatively, for pre-load validation:*
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE billing_amount < 0;
    -- If count > 0, reject/flag the load.
    ```

2.  **Discharge Date Logic Check:**
    ```sql
    ALTER TABLE healthcare_dataset
    ADD CONSTRAINT chk_discharge_date_after_admission_date
    CHECK (julianday(discharge_date) >= julianday(date_of_admission));
    ```
    *Alternatively, for pre-load validation:*
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND julianday(discharge_date) < julianday(date_of_admission);
    -- If count > 0, reject/flag the load.
    ```

Implementing these guardrails will significantly improve the data quality and reliability of the `healthcare_dataset`.
