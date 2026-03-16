# Resume Tailoring Project

## Purpose
 Tailor Arvind Allawadi's resume for Senior Java Backend Engineer roles, especially backend, platform, and distributed-systems positions.

## Core Files
- `instructions.md` — operating rules and anti-hallucination constraints
- `master_resume.md` — canonical factual resume source
- `project_inventory.md` — reusable evidence blocks and project details
- `sample_tailored_resume_apple_backend.md` — style reference only, not a source of new facts
- `current_job.md` — the active job to tailor against

## Standard Workflow
1. Read `instructions.md`
2. Read `master_resume.md`
3. Read `project_inventory.md`
4. Read `current_job.md`
5. Use `sample_tailored_resume_apple_backend.md` only as a style reference
6. Generate a tailored resume grounded only in supported facts

## Hard Rules
- Never invent achievements, metrics, tools, team scope, or architecture
- Only use facts supported by the source files
- If a requirement is not evidenced, mark it as a gap
- Reorder and emphasize existing evidence instead of creating new content
- Preserve employers, dates, and factual scope
- Prefer backend, platform, distributed-systems, API, reliability, and performance evidence when relevant
- Default positioning: Senior Java Backend Engineer. Use broader titles only when the JD is clearly not Java-centered.

## Default Output
Unless asked otherwise, output:
1. Fit assessment
2. Tailored summary
3. Tailored skills
4. Tailored experience
5. Optional short cover letter
6. Missing keywords / gaps

If the user explicitly asks for resume-only output, return only the final Markdown resume.