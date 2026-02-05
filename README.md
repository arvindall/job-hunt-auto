## 1. Minimal README to copy (short, complete)

Use this trimmed version as your actual `README.md` (it has all core steps, but no giant embedded JSON):

```markdown
# Automated Job Search Pipeline - Complete Setup Guide

> Budget 45–60 minutes for first-time setup.

## 1. What You're Building

A system that runs every 5 hours, searches Adzuna for Java/C++ backend jobs in Canada and India, deduplicates, and appends them to `applications.csv`.

---

## 2. Prerequisites

- Mac, Windows, or Linux computer
- Docker installed
- Adzuna developer account: https://developer.adzuna.com/signup

---

## 3. Directory Layout

```bash
mkdir -p ~/job-hunt/n8n-data
mkdir -p ~/job-hunt/logs
cd ~/job-hunt/n8n-data
```

---

## 4. Environment (.env)

Create `~/job-hunt/n8n-data/.env`:

```bash
Adzuna_App_ID=YOUR_APP_ID
Adzuna_App_Key=YOUR_APP_KEY
```

No spaces around `=`.

---

## 5. docker-compose.yml

In `~/job-hunt/n8n-data/docker-compose.yml`:

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n-job-hunt
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_RESTRICT_FILE_ACCESS_TO=/files
      - N8N_BLOCK_FILE_ACCESS_TO_N8N_FILES=false
      - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false
      - NODE_FUNCTION_ALLOW_BUILTIN=fs
    volumes:
      - n8n_/home/node/.n8n
      - ../logs:/files
    env_file:
      - .env

volumes:
  n8n_
    driver: local
```

---

## 6. Fix Permissions (Mac/Linux)

```bash
cd ~/job-hunt
sudo chown -R 1000:1000 logs
sudo chmod 777 logs
```

Windows: skip.

---

## 7. Start n8n

```bash
cd ~/job-hunt/n8n-data
docker compose up -d
```

Open http://localhost:5678, create an account.

If n8n doesn’t start, see QUICK_REFERENCE.md.

---

## 8. Import Workflow JSON

1. Save the separate `workflow.json` file from this repo (template).
2. In n8n: Workflows → Add workflow → ⋮ → Import from file → select `workflow.json`.
3. You should see a straight line of 9 nodes from “Every 5h (5/day)” to “Write to Disk”.

---

## 9. Test Run

1. Click **Execute workflow**.
2. Wait ~30s; all nodes should turn green.
3. Check CSV:

```bash
cat ~/job-hunt/logs/applications.csv
```

You should see a header and some rows with CA/IN jobs.

---

## 10. Activate Schedule

Click **Publish** in n8n. Workflow now runs every 5 hours while Docker is running.

---

## 11. Where Things Live

- Workflow: in n8n UI
- Config: `~/job-hunt/n8n-data/docker-compose.yml`, `.env`
- Output: `~/job-hunt/logs/applications.csv`
- Quick fixes: `QUICK_REFERENCE.md`


For full details and troubleshooting, see [DETAILS.md](DETAILS.md) and [QUICK_REFERENCE.md](QUICK_REFERENCE.md).