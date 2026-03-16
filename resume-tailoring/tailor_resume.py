import os
import re
import sys
from pathlib import Path
from datetime import datetime

import anthropic
from dotenv import load_dotenv
SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")
BASE_DIR = SCRIPT_DIR

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-1-20250805")
MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "5000"))
TEMPERATURE = float(os.getenv("ANTHROPIC_TEMPERATURE", "0.2"))
USE_PROMPT_CACHING = os.getenv("USE_PROMPT_CACHING", "false").lower() in {"1", "true", "yes"}

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY not found in environment")

client = anthropic.Anthropic(api_key=api_key)


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return path.read_text(encoding="utf-8")


def load_job_text() -> str:
    if len(sys.argv) > 1:
        return read_text(Path(sys.argv[1]).resolve())

    if not sys.stdin.isatty():
        stdin_text = sys.stdin.read().strip()
        if stdin_text:
            return stdin_text

    return read_text(BASE_DIR / "current_job.md")



def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "job"


def extract_field(job_text: str, field_name: str, default: str = "job") -> str:
    pattern = rf"^-\s*{re.escape(field_name)}:\s*(.+)$"
    for line in job_text.splitlines():
        m = re.match(pattern, line.strip(), flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return default


instructions = read_text(BASE_DIR / "instructions.md")
master_resume = read_text(BASE_DIR / "master_resume.md")
project_inventory = read_text(BASE_DIR / "project_inventory.md")
sample_resume = read_text(BASE_DIR / "sample_tailored_resume_apple_backend.md")
job_text = load_job_text()

OUTPUT_MODE = os.getenv("OUTPUT_MODE", "resume").lower()
if OUTPUT_MODE not in {"resume", "analysis", "both"}:
    raise ValueError("OUTPUT_MODE must be one of: resume, analysis, both")

if OUTPUT_MODE == "resume":
    output_mode = """
Output ONLY the final tailored Markdown resume.

Requirements for resume output:
- No fit assessment
- No recommendation section
- No keyword coverage table
- No gaps section
- No cover letter
- No commentary before or after the resume
- No headings like "Tailored Resume" or "Analysis"
- Keep the output concise and recruiter-ready
""".strip()

elif OUTPUT_MODE == "analysis":
    output_mode = """
Return:
1. Fit assessment
2. Tailored summary
3. Tailored skills
4. Tailored experience
5. Missing keywords / gaps

Do not include a cover letter unless explicitly requested.
""".strip()
else:
    output_mode = """
Return:
1. Fit assessment
2. Final tailored Markdown resume
3. Missing keywords / gaps

Do not include a cover letter unless explicitly requested.
""".strip()


system_text = f"""
You are a resume tailoring assistant.

Follow these operating rules exactly:

{instructions}

Project file roles:
- master_resume.md = canonical factual source
- project_inventory.md = reusable evidence and deeper project notes
- sample_tailored_resume_apple_backend.md = style reference only, not a source of new facts

Never invent facts, metrics, technologies, scope, or achievements.
Only use evidence supported by the provided files.
""".strip()

user_text = f"""
Here are the project files.

# master_resume.md
{master_resume}

# project_inventory.md
{project_inventory}

# sample_tailored_resume_apple_backend.md
{sample_resume}

# current_job.md
{job_text}

Task:
Tailor Arvind Allawadi's resume for the role in current_job.md.

Requirements:
- Analyze the JD for skills, seniority, backend/platform/distributed-systems signals, and ATS keywords, then map them only to supported evidence from the source files
- Reorder bullets for relevance
- Prefer strongest Apple backend/platform evidence when relevant
- Be honest about gaps
- Do not invent facts, technologies, ownership, leadership scope, domain expertise, or work authorization
- {output_mode}
""".strip()

request = {
    "model": MODEL,
    "max_tokens": MAX_TOKENS,
    "temperature": TEMPERATURE,
    "messages": [{"role": "user", "content": user_text}],
}

if USE_PROMPT_CACHING:
    request["cache_control"] = {"type": "ephemeral"}
    request["system"] = [
        {
            "type": "text",
            "text": system_text,
            "cache_control": {"type": "ephemeral"},
        }
    ]
else:
    request["system"] = system_text

response = client.messages.create(**request)

parts = []
for block in response.content:
    if getattr(block, "type", None) == "text":
        parts.append(block.text)

output_text = "\n".join(parts).strip()

company = slugify(extract_field(job_text, "Company", "company"))
role = slugify(extract_field(job_text, "Role", "role"))
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_file = OUTPUT_DIR / f"{company}_{role}_{OUTPUT_MODE}_{timestamp}.md"
out_file.write_text(output_text, encoding="utf-8")

print(output_text)
print(f"\nSaved to: {out_file}", file=sys.stderr)

usage = getattr(response, "usage", None)
if usage:
    usage_bits = []
    for key in [
        "input_tokens",
        "output_tokens",
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
    ]:
        val = getattr(usage, key, None)
        if val is not None:
            usage_bits.append(f"{key}={val}")
    if usage_bits:
        print("Usage: " + ", ".join(usage_bits), file=sys.stderr)