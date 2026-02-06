# Workflows

This folder contains automation workflows, grouped by domain, along with setup notes, configs, and troubleshooting.

## Structure

- `interview-prep/` — LeetCode interview prep tracker (Google Sheets + n8n + Claude)

## Conventions

- Workflow JSON exports live under each workflow folder in `n8n-workflows/`.
- Keep secrets out of JSON; use n8n Credentials or environment variables.
