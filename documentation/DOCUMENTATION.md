# Documentation

## 1) Overview of the Problem

Healthcare data quality failures are costly and often silent. Errors in patient, encounter, and billing data can lead to downstream issues in care quality, reporting, and analytics. Traditional rule-based data quality systems require manual rule authoring and frequent maintenance as schemas and data distributions drift. With LLM we can actively look for data quality issues.

This project evaluates a multi-agent, LLM-based data quality system that can:

- profile table schema and sampled data,
- propose SQL-based quality checks,
- execute checks with read-only guardrails,
- summarize findings with traceable logs and reports.

Core research focus:

- Can LLM-generated checks detect injected corruptions reliably?
- What profiling level (P05/P10/P20/P50) gives a strong recall/cost trade-off?
- How do Gemini model variants compare by precision, recall, F1, and tokens?

---

## 2) Description of the Dataset Used (Input Features, Outcome, Dimensions)

### Source

- Kaggle Healthcare Dataset (synthetic healthcare-style records):
  - https://www.kaggle.com/datasets/prasad22/healthcare-dataset

### Dataset Size and Structure

| Attribute | Value |
|---|---|
| File | `healthcare_dataset.csv` |
| File size | ~8.0 MB |
| Rows | 55,500 |
| Columns | 15 |
| Storage in pipeline | SQLite table `healthcare_dataset` |
| Raw dtype mix (CSV/pandas) | 12 `object`, 2 `int64`, 1 `float64` |

### Columns and Data Types

| Column | Data type | Practical type |
|---|---|---|
| `Name` | object | text (person name) |
| `Age` | int64 | integer numeric |
| `Gender` | object | categorical text |
| `Blood Type` | object | categorical text |
| `Medical Condition` | object | categorical text |
| `Date of Admission` | object | date-like text |
| `Doctor` | object | text |
| `Hospital` | object | text |
| `Insurance Provider` | object | categorical text |
| `Billing Amount` | float64 | decimal numeric |
| `Room Number` | int64 | integer numeric |
| `Admission Type` | object | categorical text |
| `Discharge Date` | object | date-like text |
| `Medication` | object | categorical text |
| `Test Results` | object | categorical text |

### Outcome / Labels for Evaluation

- Synthetic corruptions are injected into a working DB.
- Ground truth is logged to:
  - `runs/lab-ground-truth-<timestamp>.json`
- Evaluation computes TP/FP/FN, precision, recall, and F1 from detected row IDs versus corruption ground truth (delta vs baseline mode supported).

### Corruption Modes

- `auto` (simple): nulls, truncation, numeric outliers, future dates, duplicates.
- `complex_auto` (complex): temporal inversion, datetime shift, code drift, unit mismatch, ID fragmentation, enum encoding drift.

### Run Coverage by Model (Simple vs Complex)

The table below summarizes how many benchmark runs were executed per model in each scenario, based on `final-summary-output/manual-summary-aggregated.csv`.

| Model | Simple runs | Complex runs | Total runs |
|---|---:|---:|---:|
| `gemini-2.5-flash` | 23 | 21 | 44 |
| `gemini-2.5-pro` | 17 | 17 | 34 |
| `gemini-3-flash-preview` | 12 | 12 | 24 |
| `gemini-3.1-flash-lite-preview` | 14 | 14 | 28 |
| `gemini-3.1-pro-preview` | 14 | 16 | 30 |

---

## 3) How to Run the Code (Dependencies, Setup, Commands)

### Dependencies

- Python 3.11+
- Google API key (`GOOGLE_API_KEY`) with Gemini access
- Packages from repo:
  - `pip install -e .`

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# set GOOGLE_API_KEY and DQ_DB_URL in .env
```

### Ingest and Corrupt Data

```bash
dq-lab ingest --csv ./healthcare_dataset.csv

# simple corruption
dq-lab corrupt --table healthcare_dataset --strategy auto --fraction 0.08

# complex corruption
dq-lab corrupt --table healthcare_dataset --strategy complex_auto --fraction 0.05
```

### Run Data Quality Agent

```bash
python -m data_quality_agent.run_job --tables healthcare_dataset
```

### Evaluate Against Ground Truth

```bash
dq-eval \
  --run-id dq-<RUN_ID> \
  --ground-truth runs/lab-ground-truth-<timestamp>.json \
  --db-url sqlite:///./runs/db/healthcare_work.sqlite \
  --baseline-db-url sqlite:///./runs/db/healthcare_clean.sqlite
```

### Manual Benchmark Sessions

```bash
dq-manual setup --csv ./healthcare_dataset.csv \
  --base-db-url sqlite:///./runs/db/healthcare_clean.sqlite \
  --work-db-url sqlite:///./runs/db/healthcare_work.sqlite

dq-manual run-session --session simple \
  --models gemini-2.5-flash,gemini-2.5-pro \
  --profiles P05,P10,P20

dq-manual run-session --session complex \
  --models gemini-2.5-flash,gemini-2.5-pro \
  --profiles P05,P10,P20

dq-manual summarize --pattern "manual-session-*.json"
```

---

## 4) Decisions Made Along the Way (and Trade-offs)

### A. Sequential multi-agent pipeline vs single monolithic prompt

- Decision: use profiler -> planner -> executor -> supervisor.
- Trade-off: more latency/token overhead, but clearer observability, better modular debugging, and cleaner reporting.

### B. Profiling budget sweeps (P05/P10/P20/P50) instead of full-table prompting

- Decision: test multiple profile levels for cost/quality optimization.
- Trade-off: lower token cost and faster runs, but reduced visibility into rare patterns at smaller profile sizes.

### C. Read-only SQL guardrails

- Decision: hard block mutating SQL (INSERT/UPDATE/DELETE/DROP).
- Trade-off: safer execution against live data, but less flexibility for custom diagnostics.

### D. Baseline-delta evaluation

- Decision: score against `delta_rowids` relative to clean baseline DB.
- Trade-off: better precision accounting for synthetic experiments, but requires maintaining both clean and corrupted DBs.

### E. Model breadth and quota management

- Decision: compare Gemini 2.5 and 3.x variants under manual low-quota sessions.
- Trade-off: broad model insight, but higher operational complexity (retries, API quota windows, occasional transient server failures).

---

## 5) Example Output (What It Does)

The system produces:

- run-level event logs (`runs/<run_id>.jsonl`),
- markdown and HTML reports (`runs/<run_id>.md`, `runs/<run_id>.html`),
- evaluation reports (`runs/<run_id>-evaluation.md/json`),
- benchmark summaries (`runs/manual-benchmark-summary-*.md/json`).

### Benchmark Visuals (from `final-summary-output`)

#### Delta F1 Heatmaps

![Simple Delta F1 Heatmap](final-summary-output/manual-summary-f1-heatmap-simple.png)

![Complex Delta F1 Heatmap](final-summary-output/manual-summary-f1-heatmap-complex.png)

#### Recall vs Token Cost

![Simple Recall vs Tokens](final-summary-output/manual-summary-recall-vs-tokens-simple.png)

![Complex Recall vs Tokens](final-summary-output/manual-summary-recall-vs-tokens-complex.png)

#### Profile Curves by Model

![Simple Delta F1 by Profile](final-summary-output/manual-summary-f1-lines-simple.png)

![Complex Delta F1 by Profile](final-summary-output/manual-summary-f1-lines-complex.png)

---

## 6) Citations (Data, Code, Papers)

### Data

- Prasad. Healthcare Dataset. Kaggle.
  - https://www.kaggle.com/datasets/prasad22/healthcare-dataset

### Frameworks and Tooling

- Google Agent Development Kit (ADK):
  - https://google.github.io/adk-docs/
- Google Gemini API:
  - https://ai.google.dev/
- SQLite:
  - https://www.sqlite.org/

---

## 7) Conclusion and Results Analysis

Using the aggregated benchmark table in `final-summary-output/manual-summary-aggregated.csv`, we observe:

### A. The system is effective, but performance depends on issue complexity

- **Simple scenario:** consistently higher and more stable F1 across models/profiles.
- **Complex scenario:** stronger variance across profiles and models, with some cells showing near-perfect detection and others dropping substantially.

### B. Best-performing configurations (from current runs)

- **Simple (best robust result):**
  - `gemini-3.1-flash-lite-preview @ P20`
  - `delta_precision_mean = 0.9795`, `delta_recall_mean = 0.9179`, `delta_f1_mean = 0.9414`, `run_count = 4`
- **Complex (best robust result):**
  - `gemini-3.1-flash-lite-preview @ P50`
  - `delta_precision_mean = 1.0000`, `delta_recall_mean = 1.0000`, `delta_f1_mean = 1.0000`, `run_count = 3`

### C. Cost-quality pattern

- Increasing profile size does **not always** improve quality monotonically.
- In several cells, P20 or P50 improves recall/F1, but some models plateau earlier.
- Token usage can vary significantly by model and prompt trajectory even under the same profile level, so model/profile should be selected jointly.

### D. Practical recommendation from this benchmark

- For **simple issues**, use a mid/high profile where recall plateaus with strong precision (currently P20 is strongest overall in robust runs).
- For **complex issues**, include P50 for at least one confirmation pass because semantic/temporal checks show higher variance at lower profiles.
- Require a minimum `run_count` threshold (e.g., 3+) before making final model-profile claims.

### E. Limitations and next validation step

- Some high-scoring cells still have lower run counts than ideal for publication-grade claims.
- Final recommendation should be based on additional seeds and reported with variance (mean ± std/CI), not point estimates only.
- This project demonstrates that LLM-generated guardrails can work well, but rigorous selection requires repeated runs and explicit stability criteria.
- This project only used Gemini models, other models from OpenAI and Anthropic as well as open source models can be used to test.
