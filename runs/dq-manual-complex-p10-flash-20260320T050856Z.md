# Data Quality Report - dq-manual-complex-p10-flash-20260320T050856Z

Generated at: 2026-03-20 05:09:39 UTC

## Executive Summary
- Overall verdict: **YELLOW**
- Total tests executed: **2**
- Passed: **1**
- Failed: **1**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P10-FLASH`
- Event log: `runs/dq-manual-complex-p10-flash-20260320T050856Z.jsonl`

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
| MEDIUM | FAIL | healthcare_dataset | name_inconsistent_casing | 55417 |

## Detailed Findings
### 1. [MEDIUM/FAIL] name_inconsistent_casing (healthcare_dataset)
- Why this matters: Inconsistent casing in patient names (e.g., 'MikE BURTon', 'cHRiSTOPhEr bUTLEr') hinders data standardization, unique patient identification, and efficient search operations. Standardizing names is crucial for data consistency and usability. This test identifies names that are neither entirely uppercase nor entirely lowercase, suggesting mixed or inconsistent casing.
- Issue count: **55417**
- Output truncated: **yes**

```sql
SELECT
  name
FROM healthcare_dataset
WHERE
  name IS NOT NULL AND
  name != UPPER(name) AND
  name != LOWER(name);
```

Example rows:
```json
[
  {
    "name": "Bobby JacksOn"
  },
  {
    "name": "LesLie TErRy"
  },
  {
    "name": "DaNnY sMitH"
  }
]
```

## Supervisor Narrative
**Overall Verdict:** YELLOW

**Top Critical/High Issues:**
*   None.

**Medium Severity Issues:**
*   **`name_inconsistent_casing`** (55417 issues): Patient names in the `healthcare_dataset` table exhibit inconsistent casing (e.g., "MikE BURTon", "cHRiSTOPhEr bUTLEr"), which significantly hinders data standardization, unique patient identification, and efficient search functionality.

**Test Coverage Notes:**
A total of 2 data quality tests were executed against the `healthcare_dataset` table.
*   The `discharge_before_admission` test (critical severity), designed to ensure that discharge dates logically occur on or after admission dates, passed with 0 issues. This indicates good adherence to temporal data integrity for this specific check.
*   The `name_inconsistent_casing` test (medium severity) identified 55417 instances where patient names had inconsistent casing. This highlights a pervasive issue with data entry or transformation for the `name` column.

**Suggested Production Guardrails (SQL checks to schedule each load):**
1.  **Guardrail for `discharge_date` consistency:**
    ```sql
    SELECT
      name,
      date_of_admission,
      discharge_date
    FROM healthcare_dataset
    WHERE
      date_of_admission IS NOT NULL AND
      discharge_date IS NOT NULL AND
      date_of_admission GLOB '____-__-__' AND
      discharge_date GLOB '____-__-__' AND
      julianday(discharge_date) < julianday(date_of_admission);
    ```
    *   *Action:* Implement an automated check to prevent or flag any records where the `discharge_date` is earlier than the `date_of_admission`.
2.  **Guardrail for `name` casing standardization:**
    ```sql
    SELECT
      name
    FROM healthcare_dataset
    WHERE
      name IS NOT NULL AND
      name != UPPER(name) AND
      name != LOWER(name);
    ```
    *   *Action:* Integrate a data cleansing step during ingestion or as a scheduled process to standardize the casing of patient names (e.g., convert to proper case or uppercase) to ensure consistency and improve data usability. This check can be run to monitor compliance post-standardization.
