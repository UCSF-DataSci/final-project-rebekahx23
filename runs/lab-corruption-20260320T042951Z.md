# Local Corruption Report (20260320T042951Z)

Table: `healthcare_dataset`

- temporal_inversion on `date_of_admission->gender` -> 0 rows (row_ids captured: 0) details={"start_column": "date_of_admission", "end_column": "gender"}
- datetime_shift on `date_of_admission` -> 555 rows (row_ids captured: 555) details={"shift_hours": 8}
- id_fragmentation on `insurance_provider` -> 333 rows (row_ids captured: 333)
- enum_encoding_drift on `gender` -> 555 rows (row_ids captured: 555)

- Ground truth JSON: `runs/lab-ground-truth-20260320T042951Z.json`
