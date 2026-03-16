# Resume Tailoring

A local, repeatable workflow for tailoring a resume to a specific job description using Claude/Anthropic.

This project is designed to be simple enough that a non-technical user can run it step by step, but structured enough that an AI tool can also understand, troubleshoot, and extend it with minimal guesswork.

The system takes:
1. A canonical master resume
2. Supporting project notes
3. A target job description
4. Instructions for safe tailoring

It produces:
- A tailored markdown resume
- Saved output files for each run
- A predictable file structure that is easy to debug

---

## Goal

The goal of this project is to generate high-quality, evidence-grounded tailored resumes for specific jobs without inventing experience, exaggerating scope, or adding unsupported claims.

This workflow is intentionally:
- Local-first
- File-based
- Reproducible
- Easy to inspect
- Easy to hand off to another person

---

## Philosophy

This project follows a few strict rules:

- The master resume is the source of truth.
- Supporting project notes can provide additional evidence and context.
- Sample tailored resumes are style references only.
- The tailored output must never invent facts.
- The active job description lives in `current_job.md`.
- Archived job descriptions should be stored separately for reuse.
- Generated outputs should be saved automatically.

This keeps the system safe, auditable, and easy to reason about.

---

## Folder Structure

Recommended structure:

```text
resume-tailoring/
├── .env
├── README.md
├── current_job.md
├── tailor_resume.py
├── instructions.md
├── master_resume.md
├── project_inventory.md
├── sample_tailored_resume_apple_backend.md
├── outputs/
├── archive/
└── templates/
```

### What each file does

- `tailor_resume.py`  
  Main script. Reads inputs, builds the prompt, calls Anthropic, prints the result, and saves it to `outputs/`.

- `current_job.md`  
  The currently active job description. This is the file the script reads by default.

- `archive/`  
  Stores cleaned historical job descriptions, one file per role.

- `templates/`  
  Stores reusable templates such as a blank `current_job.md`.

- `master_resume.md`  
  Canonical factual source. This should contain the safest, most accurate version of the resume.

- `project_inventory.md`  
  Extra supporting evidence, deeper project notes, stronger context, and material that may not fit cleanly in the master resume.

- `sample_tailored_resume_apple_backend.md`  
  Style reference only. Never use this file as a source of new facts.

- `instructions.md`  
  High-level tailoring behavior and guardrails.

- `.env`  
  Stores API key and runtime settings. Never commit this file.

- `outputs/`  
  Saved results from each script run.

---

## How the workflow works

### Step 1: Prepare the source files

Before you run anything, make sure these files are present and up to date:

- `master_resume.md`
- `project_inventory.md`
- `instructions.md`
- `sample_tailored_resume_apple_backend.md`

These should be treated as stable input files. Update them only when the source information genuinely changes.

### Step 2: Prepare the job description

Put the active target job into `current_job.md`.

This file should contain:
- Structured metadata at the top
- A clean summary
- Responsibilities
- Qualifications
- ATS keywords
- Raw JD text

Recommended header format:

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

### Step 3: Run the script

From inside the `resume-tailoring` directory:

```bash
python3 tailor_resume.py
```

This reads `current_job.md` by default.

You can also pass a file directly:

```bash
python3 tailor_resume.py archive/coupang_staff_backend_engineer_hyderabad_5270413334.md
```

You can also pipe content through stdin if needed, though file-based usage is easier to debug.

### Step 4: Review the output

The script:
- Prints the tailored output to the terminal
- Saves it into `outputs/`
- Adds company, role, output mode, and timestamp to the filename

Always review the output manually before using it.

---

## Setup Guide

### Prerequisites

Install:
- Python 3.10+
- `pip`
- An Anthropic API key

### 1) Clone or create the project folder

```bash
mkdir -p ~/job-hunt/resume-tailoring
cd ~/job-hunt/resume-tailoring
```

### 2) Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install anthropic python-dotenv
```

Optional:
```bash
pip freeze > requirements.txt
```

### 4) Create `.env`

```env
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-opus-4-1-20250805
ANTHROPIC_MAX_TOKENS=5000
ANTHROPIC_TEMPERATURE=0.2
USE_PROMPT_CACHING=false
OUTPUT_MODE=resume
```

### 5) Create folders

```bash
mkdir -p outputs archive templates
```
### 5.5) One-shot setup (optional)

If you downloaded `setup_resume_tailoring.sh` and the companion markdown files:

```bash
cd /path/to/downloaded/files
chmod +x setup_resume_tailoring.sh
./setup_resume_tailoring.sh
By default this will set up the project under:
~/job-hunt/resume-tailoring
You can override the base directory:
./setup_resume_tailoring.sh /some/other/path

### 6) Add the input files

Create or copy:
- `instructions.md`
- `master_resume.md`
- `project_inventory.md`
- `sample_tailored_resume_apple_backend.md`
- `current_job.md`

### 7) Test the script

```bash
python3 tailor_resume.py
```

If successful, you should see:
- Tailored output in the terminal
- A new markdown file in `outputs/`

---

## Running the tool

The easiest way to run the tailor is via `run.sh`:

```bash
cd ~/job-hunt/resume-tailoring
source .venv/bin/activate   # if not already active
./run.sh
```

This is equivalent to:

```bash
OUTPUT_MODE=resume python3 tailor_resume.py
```

You can pass a specific job file as an argument:

```bash
./run.sh archive/coupang_staff_backend_engineer_hyderabad_5270413334.md
```

### Other run modes

```bash
# Analysis only
OUTPUT

## Output Modes

The script supports:

- `resume`  
  Outputs only the final tailored resume

- `analysis`  
  Outputs fit assessment, summary, skills, experience, and gaps

- `both`  
  Outputs a compact analysis plus the final resume

Recommended default:

```env
OUTPUT_MODE=resume
```

This is the safest production mode because it reduces the chance of bloated analysis sections or unsupported narrative.

---

## Suggested Daily Workflow

### Normal use

1. Pick a job
2. Clean and save it into `archive/`
3. Copy it into `current_job.md`
4. Run the script
5. Review the output
6. Save or edit the final version
7. Apply manually

Example:

```bash
cp archive/coupang_staff_backend_engineer_hyderabad_5270413334.md current_job.md
python3 tailor_resume.py
```

### Re-running the same job

If you update the resume source files or instructions, just run the same job again.

### Comparing prompt changes

If you change `instructions.md`, `master_resume.md`, or prompt logic:
- Re-run the same job
- Compare the new output with the older file in `outputs/`

---

## Writing Good Job Files

A good `current_job.md` makes the tailoring output much better.

### Good practices

- Normalize company names, for example use `Coupang`, not `Coupand`
- Prefer the official careers page as canonical if aggregator text is messy
- Keep metadata at the top in `- Field: value` format
- Preserve raw JD text below the cleaned summary
- Add ATS keywords explicitly if they are obvious from the JD

### Why this matters

The script extracts metadata using simple line matching. If the metadata format is inconsistent, filenames and role labels can break.

---

## Common Pain Points and Fixes

### 1) The script hangs and seems to do nothing

Cause:
- The script may be waiting on stdin in some setups

Fix:
- Prefer running with `current_job.md` or an explicit file path
- Keep the logic that first checks command-line input, then only reads stdin when input is actually present

Why this was fixed:
- Interactive runs should not block forever just because stdin exists

---

### 2) Anthropic returns a 404 model error

Example symptom:
- `NotFoundError`
- model not found

Cause:
- Old or invalid model name

Fix:
- Use a current supported model name in `.env`
- Example:

```env
ANTHROPIC_MODEL=claude-opus-4-1-20250805
```

If you want a safer fallback, use the currently supported latest model naming approach for the Anthropic SDK version you installed.

---

### 3) The output invents things

Example:
- Claims staff leadership when the source does not prove it
- Claims multi-tenant ownership without evidence
- Claims domain expertise not present in the source files
- Claims work authorization or location flexibility not explicitly stated

Cause:
- Prompt too open-ended
- Resume evidence too loose
- Model trying to be “helpful”

Fix:
- Keep `master_resume.md` factual
- Add guardrails in the prompt:
  - do not invent facts
  - do not invent technologies
  - do not invent ownership
  - do not invent leadership scope
  - do not invent domain expertise
  - do not invent work authorization
- Use `OUTPUT_MODE=resume` for production

---

### 4) The script saves confusing filenames

Cause:
- Weak metadata extraction
- Missing `Company` or `Role` header in `current_job.md`

Fix:
- Always include:
  - `- Company:`
  - `- Role:`
- Use clean company and role names
- Let the script slugify them for filenames

---

### 5) The model produces too much analysis

Cause:
- Prompt asks for fit assessment, gaps, keyword table, cover letter, and resume all at once

Fix:
- Default to `OUTPUT_MODE=resume`
- Keep analysis optional, not default

This was an intentional design improvement because the actual tailored resume is the useful artifact, while free-form analysis is more likely to drift or overstate things.

---

### 6) The repo gets cluttered

Cause:
- Every job file, output, and experiment ends up in the root folder

Fix:
- Use:
  - `current_job.md` for the active file
  - `archive/` for saved jobs
  - `outputs/` for generated resumes
  - `templates/` for reusable blanks

---

### 7) Sensitive files get committed accidentally

Cause:
- Missing `.gitignore`

Fix:
Create a `.gitignore` like this:

```gitignore
.env
.env.local
.venv/
__pycache__/
*.pyc
.DS_Store
outputs/
```

Optional:
If you want to keep generated outputs in git, remove `outputs/` from `.gitignore`.

---

## Recommended Script Behavior

The script should do the following:

1. Load environment variables from `.env`
2. Read all source files
3. Read the active job file
4. Build a safe system prompt
5. Build a user prompt with:
   - source resume
   - project inventory
   - style reference
   - job description
   - output mode
6. Call Anthropic
7. Save the result to `outputs/`
8. Print the result
9. Print token usage to stderr if available

This makes the workflow easy to audit and easy to replicate.

---

## Recommended Prompt Rules

Keep these rules in the prompt:

- Use `master_resume.md` as the canonical factual source
- Use `project_inventory.md` for deeper supporting evidence
- Use sample resume only as a style reference
- Never invent facts, metrics, ownership, or seniority
- Be honest about gaps
- Tailor for relevance, not fiction
- Reorder bullets for the job
- Prefer the strongest directly relevant evidence

These rules matter more than clever wording.

---

## Example Commands

### Run default active job

```bash
python3 tailor_resume.py
```

### Run a specific archived job

```bash
python3 tailor_resume.py archive/coupang_staff_backend_engineer_hyderabad_5270413334.md
```

### Force resume-only mode

```bash
OUTPUT_MODE=resume python3 tailor_resume.py
```

### Run analysis mode

```bash
OUTPUT_MODE=analysis python3 tailor_resume.py
```

---

## What to check before applying

Before using any generated resume, manually verify:

- Company name is correct
- Role title is correct
- Location is correct
- No unsupported claims were added
- No fake domain expertise was introduced
- Metrics still match source evidence
- Bullets are relevant to the target job
- Skills section matches the actual source files

If anything looks slightly inflated, edit it down.

---

## Hand-off Notes for Another User

If another person is using this project:

### What they need to know

- They do not need to understand Python deeply
- They only need to update:
  - `current_job.md`
  - sometimes `master_resume.md`
  - sometimes `project_inventory.md`
- The rest of the workflow should stay stable

### Safe operating rule

If unsure whether something is true, do not add it to the source files.

### Best mental model

Think of this system as:
- a factual resume database
- plus a role-specific formatter
- plus a safety layer against hallucination

---

## Minimal Quick Start

If you are in a hurry:

```bash
cd ~/job-hunt/resume-tailoring
source .venv/bin/activate
cp archive/coupang_staff_backend_engineer_hyderabad_5270413334.md current_job.md
python3 tailor_resume.py
```

Then open the newest file in `outputs/`.

---

## Future Improvements

Potential improvements:
- Add `requirements.txt`
- Add `Makefile`
- Add a `run.sh`
- Add validation for missing files
- Add checks for malformed `current_job.md`
- Add a small diff tool to compare old vs new tailored resumes
- Add automatic archive-to-current copy helpers

---

## Ownership Checklist

If something breaks, check in this order:

1. Is `.env` present?
2. Is the Anthropic API key valid?
3. Is the model name valid?
4. Does `current_job.md` exist?
5. Do `master_resume.md`, `project_inventory.md`, and `instructions.md` exist?
6. Is the active virtual environment enabled?
7. Did the output file get written to `outputs/`?
8. Did the prompt ask for too much?

This solves most issues quickly.

---

## Final Rule

This tool should make the resume more relevant, not less truthful.

If forced to choose between “more impressive” and “more accurate,” always choose accuracy.