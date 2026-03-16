#!/usr/bin/env bash
set -euo pipefail

# Base dir for resume-tailoring project (change if needed)
BASE_DIR="${1:-$HOME/job-hunt/resume-tailoring}"

echo "Setting up resume-tailoring project in: $BASE_DIR"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR"

# Create folders
mkdir -p outputs archive templates

# Copy template and docs if they exist next to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

copy_if_exists() {
  local src="$1"
  local dest="$2"
  if [ -f "$SCRIPT_DIR/$src" ]; then
    cp "$SCRIPT_DIR/$src" "$dest"
    echo "Copied $src -> $dest"
  else
    echo "(skip) $src not found next to setup.sh"
  fi
}

# Main docs
copy_if_exists "README_resume_tailoring.md" "README.md"
copy_if_exists "QUICK_REFERENCE_resume_tailoring.md" "QUICK_REFERENCE.md"
copy_if_exists "DETAILS_resume_tailoring.md" "DETAILS.md"

# Job template
copy_if_exists "current_job.template.md" "templates/current_job.template.md"

# Helper script
copy_if_exists "run.sh" "run.sh"
if [ -f "run.sh" ]; then
  chmod +x run.sh
fi

# Gitignore
copy_if_exists ".gitignore_resume_tailoring" ".gitignore"

# Create placeholder files if missing
for f in instructions.md master_resume.md project_inventory.md sample_tailored_resume_apple_backend.md current_job.md; do
  if [ ! -f "$f" ]; then
    echo "(placeholder) Creating $f"
    printf "# %s\n\nTODO: Fill this file with content.\n" "$f" > "$f"
  fi
done

# Virtualenv hint
if [ ! -d ".venv" ]; then
  echo
  echo "No .venv found. To create one, run:"
  echo "  cd $BASE_DIR"
  echo "  python3 -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install anthropic python-dotenv"
fi

echo
echo "Setup complete. Next steps:"
echo "  1) Edit master_resume.md, project_inventory.md, instructions.md"
echo "  2) Put a real job into current_job.md (or use templates/current_job.template.md)"
echo "  3) Run: ./run.sh"
