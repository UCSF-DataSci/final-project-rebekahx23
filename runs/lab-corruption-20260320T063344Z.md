# Local Corruption Report (20260320T063344Z)

Table: `healthcare_dataset`

- nullify on `name` -> 1110 rows (row_ids captured: 1110)
- truncate on `name` -> 1087 rows (row_ids captured: 1087)
- numeric_outlier on `age` -> 1110 rows (row_ids captured: 1110)
- future_date on `date_of_admission` -> 1110 rows (row_ids captured: 1110)
- duplicate_rows on `(row)` -> 1110 rows (row_ids captured: 1110)

- Ground truth JSON: `runs/lab-ground-truth-20260320T063344Z.json`
