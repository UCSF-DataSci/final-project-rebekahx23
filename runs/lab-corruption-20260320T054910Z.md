# Local Corruption Report (20260320T054910Z)

Table: `healthcare_dataset`

- temporal_inversion on `date_of_admission->discharge_date` -> 555 rows (row_ids captured: 555) details={"start_column": "date_of_admission", "end_column": "discharge_date"}
- datetime_shift on `date_of_admission` -> 555 rows (row_ids captured: 555) details={"shift_hours": 8}
- enum_encoding_drift on `gender` -> 555 rows (row_ids captured: 555)

- Ground truth JSON: `runs/lab-ground-truth-20260320T054910Z.json`
