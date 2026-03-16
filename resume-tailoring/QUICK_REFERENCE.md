# QUICK_REFERENCE.md

Use this file for day-to-day operation.
For full setup and explanations, see `README.md`.
For architecture, debugging history, and design decisions, see `DETAILS.md`.

---

## 1) Activate and run

```bash
cd ~/job-hunt/resume-tailoring
source .venv/bin/activate
python3 tailor_resume.py
```

This reads `current_job.md` by default.

---

## 2) Run a specific archived job

```bash
cd ~/job-hunt/resume-tailoring
source .venv/bin/activate
python3 tailor_resume.py archive/coupang_staff_backend_engineer_hyderabad_5270413334.md
```

Use this when you want to tailor for a specific stored job without replacing `current_job.md`.

---

## 3) Make an archived job the active one

```bash
cd ~/job-hunt/resume-tailoring
cp archive/coupang_staff_backend_engineer_hyderabad_5270413334.md current_job.md
python3 tailor_resume.py
```

This is the normal workflow.

---

## 4) Output modes

Default is resume-only.

```bash
OUTPUT_MODE=resume python3 tailor_resume.py
```

Analysis only:

```bash
OUTPUT_MODE=analysis python3 tailor_resume.py
```

Both resume and analysis:

```bash
OUTPUT_MODE=both python3 tailor_resume.py
```

---

## 5) Required files

These files must exist:

```text
tailor_resume.py
instructions.md
master_resume.md
project_inventory.md
sample_tailored_resume_apple_backend.md
current_job.md
.env
```

If one is missing, the script will fail.

---

## 6) Required folders

Recommended:

```bash
mkdir -p outputs archive templates
```

---

## 7) Install dependencies

```bash
cd ~/job-hunt/resume-tailoring
python3 -m venv .venv
source .venv/bin/activate
pip install anthropic python-dotenv
```

Optional:

```bash
pip freeze > requirements.txt
```

---

## 8) `.env` template

```env
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-opus-4-1-20250805
ANTHROPIC_MAX_TOKENS=5000
ANTHROPIC_TEMPERATURE=0.2
USE_PROMPT_CACHING=false
OUTPUT_MODE=resume
```

---

## 9) Minimal `current_job.md` header

```md
- Company: Coupang
- Role: Staff Backend Engineer
- Location: Hyderabad, Telangana, India
- Job ID: 5270413334
- Source: Adzuna
- Source Job Key: adzuna|id|5270413334
- Posted At: 2025-06-27T03:10:29Z
- Canonical JD URL: https://www.coupang.jobs/en/jobs/6667711/staff-backend-engineer/
- Job URL: https://www.adzuna.in/details/5270413334?utm_medium=api&utm_source=f06a12e2
- Search URL:
- Work Model: Unknown
- Category: IT Jobs
```

---

## 10) Where outputs go

Generated files are saved in:

```text
outputs/
```

Filename format:

```text
{company}_{role}_{OUTPUT_MODE}_{timestamp}.md
```

Example:

```text
coupang_staff_backend_engineer_resume_20260316_001500.md
```

---

## 11) Most common problems

### Problem: script hangs
Use a file path or `current_job.md`. Do not rely on accidental stdin input.

### Problem: model not found
Update `ANTHROPIC_MODEL` in `.env`.

### Problem: output is too wordy
Use:

```bash
OUTPUT_MODE=resume python3 tailor_resume.py
```

### Problem: output invents things
Tighten `master_resume.md`, `project_inventory.md`, and `instructions.md`.

### Problem: weird filenames
Make sure `current_job.md` includes clean `Company` and `Role` fields.

---

## 12) Safe workflow

1. Save the cleaned JD in `archive/`
2. Copy it to `current_job.md`
3. Run the script
4. Review the output manually
5. Apply only after checking accuracy

---

## 13) Before applying, verify

- Company is correct
- Role is correct
- Location is correct
- No fake leadership claims
- No fake domain expertise
- No fake work authorization
- Metrics still match source evidence
- Skills are truthful

---

## 14) Best practice

Use `resume` mode for production.
Use `analysis` mode only when you want to inspect fit, gaps, or prompt behavior.
