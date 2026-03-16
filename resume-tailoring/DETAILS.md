# DETAILS.md

This file explains how the resume-tailoring project works, why it is structured this way, what problems came up during development, and how to debug them.

If you just want to run the project, use `README.md`.
If you only want commands, use `QUICK_REFERENCE.md`.

---

## 1) What this project does

This project tailors a resume to a target job description using Claude/Anthropic.

Inputs:
- `master_resume.md`
- `project_inventory.md`
- `instructions.md`
- `sample_tailored_resume_apple_backend.md`
- `current_job.md` or an explicitly passed job file

Output:
- A saved tailored markdown file in `outputs/`
- Printed output in the terminal

The system is local-first and file-based by design.
That makes it easy to inspect, version, hand off, and debug.

---

## 2) Why the project is file-based

This project does not depend on a GUI or hidden state.
Everything important lives in markdown files and one Python script.

Benefits:
- Easy to hand off to another person
- Easy for an AI tool to inspect and extend
- Easy to reproduce a result later
- Easy to compare prompt changes over time

This is much safer than burying logic in a UI or relying on memory.

---

## 3) Core design principles

### Canonical truth
`master_resume.md` is the factual source of truth.

### Supporting evidence
`project_inventory.md` contains deeper project notes, stronger wording candidates, and additional context that may not fit neatly into the resume.

### Style-only sample
`sample_tailored_resume_apple_backend.md` is a style guide only.
It must not introduce new facts.

### Active job file
`current_job.md` is the currently selected target job.

### Archived jobs
`archive/` stores cleaned job descriptions for reuse.

### Safe default output
`OUTPUT_MODE=resume` is the default production mode because it minimizes unnecessary narrative and reduces hallucination risk.

---

## 4) Current recommended structure

```text
resume-tailoring/
├── .env
├── README.md
├── QUICK_REFERENCE.md
├── DETAILS.md
├── tailor_resume.py
├── current_job.md
├── instructions.md
├── master_resume.md
├── project_inventory.md
├── sample_tailored_resume_apple_backend.md
├── outputs/
├── archive/
└── templates/
```

### Why this structure works

- Root folder stays clean
- Only one active job is used at a time
- Old jobs remain reusable
- Outputs are separated from sources
- Templates are easy to copy

---

## 5) How the script works

High-level flow:

1. Load environment variables from `.env`
2. Read the source prompt files
3. Read the job description
4. Build system prompt + user prompt
5. Call Anthropic
6. Save response to `outputs/`
7. Print response
8. Print token usage to stderr if available

The project uses a single-file runner on purpose.
That keeps behavior transparent and makes debugging straightforward.

---

## 6) Important files

### `instructions.md`
Contains tailoring rules and safety guardrails.

Typical examples:
- reorder bullets for relevance
- prefer strongest relevant evidence
- be honest about gaps
- never invent facts
- do not infer unsupported leadership scope
- do not infer unsupported domain expertise
- do not infer unsupported work authorization

### `master_resume.md`
This should be conservative and factual.
If a claim is not safe, it should not live here.

### `project_inventory.md`
This is where richer context can live:
- project details
- alternate bullet phrasings
- extra technologies
- stronger wording candidates
- context that supports tailoring

### `current_job.md`
This should contain:
- structured metadata header
- cleaned summary
- responsibilities
- qualifications
- ATS keywords
- raw JD text

---

## 7) Why resume-only became the default

Originally, it is tempting to ask the model for:
- fit score
- recommendation
- keyword table
- cover letter
- tailored resume

That looks useful, but in practice it increases risk.

Why:
- analysis sections invite speculation
- gap explanations often drift beyond the evidence
- cover letters encourage unsupported narrative
- the actual useful artifact is the tailored resume

So the safer production pattern is:
- default to `resume`
- keep `analysis` optional
- keep `both` for inspection only

---

## 8) Pain points we hit and why the current version is better

### Pain point 1: output drift / hallucination

Problem:
The model sometimes overreached with phrases like:
- multi-tenant ownership
- staff-level leadership
- remote-Canada readiness
- domain expertise not explicitly shown

Cause:
The prompt asked for broad fit analysis, and the model tried to sound helpful.

Fix:
We tightened the prompt with explicit guardrails:
- do not invent facts
- do not invent technologies
- do not invent ownership
- do not invent leadership scope
- do not invent domain expertise
- do not invent work authorization

Result:
The tailored resume stays closer to the actual evidence.

---

### Pain point 2: too much analysis, not enough usable output

Problem:
A long response with fit scores, gap analysis, cover letter, and keyword coverage is not the main artifact you need when applying.

Cause:
The prompt mixed evaluation and production output in one request.

Fix:
Added `OUTPUT_MODE`:
- `resume`
- `analysis`
- `both`

Result:
Production runs are clean and recruiter-ready.

---

### Pain point 3: stdin behavior can be confusing

Problem:
Scripts that read stdin too eagerly can appear to hang in interactive usage.

Cause:
If stdin logic is not handled carefully, the script may wait for input instead of reading the default file.

Fix:
Use this order:
1. explicit CLI file path
2. stdin only when content is actually piped
3. fallback to `current_job.md`

Result:
Normal interactive runs behave predictably.

---

### Pain point 4: bad or stale model names

Problem:
Anthropic can return a model not found error if the configured model ID is outdated.

Cause:
Hardcoded or stale model names.

Fix:
Move model name into `.env` and keep it configurable.

Result:
You can update the model without changing code.

---

### Pain point 5: inconsistent job files

Problem:
Aggregator data can be messy, company names can be misspelled, and role titles can be inconsistent.

Examples:
- `Coupand` vs `Coupang`
- weird punctuation in titles
- noisy or partial JD text

Fix:
Normalize the job file manually:
- use the official company name
- use the official title where possible
- keep the raw JD below a cleaned summary
- prefer official careers URL as canonical

Result:
Cleaner filenames, better tailoring, easier reuse.

---

### Pain point 6: root-folder clutter

Problem:
Without structure, job files, templates, and outputs get mixed together.

Fix:
Use:
- `current_job.md` for the active job
- `archive/` for real saved jobs
- `templates/` for blank templates
- `outputs/` for generated results

Result:
The repo stays understandable.

---

## 9) Why the job header format matters

The script extracts fields using simple pattern matching:

```python
- Company: ...
- Role: ...
```

If the header format is inconsistent, these things can break:
- output filename generation
- company/role extraction
- future automations built on top of the same file format

So keep the top metadata section clean and consistent.

---

## 10) Recommended `current_job.md` structure

```md
- Company:
- Role:
- Location:
- Job ID:
- Source:
- Source Job Key:
- Posted At:
- Canonical JD URL:
- Job URL:
- Search URL:
- Work Model:
- Category:

# Job Summary

# Responsibilities

# Basic Qualifications

# Preferred Qualifications

# ATS Keywords

# Raw JD
```

This gives both humans and AI tools enough structure.

---

## 11) Why sample resume is style-only

A sample tailored resume is helpful for:
- tone
- bullet density
- section ordering
- formatting style

But it is dangerous as a factual source.

If the model treats a sample as evidence, it can copy:
- claims not present in the real resume
- extra metrics
- stronger scope than actually supported

So the sample must stay style-only.

---

## 12) Recommended `.gitignore`

```gitignore
.env
.env.local
.venv/
__pycache__/
*.pyc
.DS_Store
```

Optional:
- Ignore `outputs/` if you do not want generated resumes tracked
- Keep `archive/` in git if you want a job-history record

---

## 13) Recommended operating habits

### Good habit
Archive every cleaned job file before using it.

### Good habit
Treat `master_resume.md` as conservative and stable.

### Good habit
Use `project_inventory.md` for deeper evidence and phrasing options.

### Good habit
Review every generated resume manually before use.

### Good habit
If a bullet feels slightly too strong, rewrite it down, not up.

---

## 14) Debug checklist

If something breaks, check in this order:

1. Is `.env` present?
2. Is `ANTHROPIC_API_KEY` set?
3. Is the model valid?
4. Does `current_job.md` exist?
5. Do the required source files exist?
6. Is the virtual environment activated?
7. Did the script write into `outputs/`?
8. Did the prompt ask for too much?
9. Is the job header malformed?
10. Did the job file use a wrong company or role label?

This catches most failures quickly.

---

## 15) Hand-off guide for a non-technical user

If someone else is using this project, they only need to know five things:

1. Put the target job into `current_job.md`
2. Activate the virtual environment
3. Run `python3 tailor_resume.py`
4. Open the newest file in `outputs/`
5. Review it before applying

They do not need to edit the Python code for normal usage.

---

## 16) What not to change casually

Do not casually rewrite:
- `tailor_resume.py`
- `instructions.md`
- `master_resume.md`

These three files control most of the system’s behavior and quality.

If you change them:
- test on one known archived job
- compare the new output with an older output
- confirm nothing got more inflated

---

## 17) Future improvements

Possible improvements later:
- `requirements.txt`
- `Makefile`
- shell helper script
- schema validation for `current_job.md`
- automatic archive copying
- diff view between runs
- optional JSON metadata output
- automatic linting of resume claims

These are nice-to-have, not required.

---

## 18) Final rule

The purpose of this project is not to make the resume sound grander.
It is to make the resume more relevant while staying accurate.

If you must choose between impressive and true, choose true.
