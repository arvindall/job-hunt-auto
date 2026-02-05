# Detailed Setup Guide - Automated Job Search Pipeline

This is the comprehensive version with every step explained.

For quick steps, see the main `README.md`.  
For instant fixes, see `QUICK_REFERENCE.md`.

---

## Overview

You're building a workflow automation that:

- Runs every 5 hours automatically.
- Searches queries across Canada (Toronto) and India (Hyderabad, Bengaluru).
- Fetches 3 jobs per search from Adzuna API (21 total per run).
- Filters for Java/C++/Python backend roles only.
- Deduplicates against previous runs (30-day memory).
- Appends to a CSV file on your Mac.

**Expected output:** 40–60 relevant jobs per day, 280–420 per week.

---

## Time Estimates (Realistic)

| Scenario | Time |
|----------|------|
| Best case (Docker already installed) | 15–20 min |
| Typical (first-time Docker, 1–2 issues) | 45–60 min |
| Complex (permissions, API issues) | 2–3 hours |

---

## Prerequisites

### Required

- Mac, Windows, or Linux computer that can stay running.
- Admin/sudo access.
- 10 GB free disk space.
- Stable internet.
- Adzuna developer account (free):
  - https://developer.adzuna.com/signup
  - Note your `app_id` and `app_key`.

### Optional

- Basic terminal familiarity.
- Text editor (TextMate, VS Code, nano).
- GitHub account for version control.

---

## Step 1: Install Docker

### macOS

```bash
# Download Docker Desktop
open https://www.docker.com/products/docker-desktop/

# Install the .dmg file (drag into Applications)
# Launch Docker Desktop from Applications
# Wait for "Docker Desktop is running" (whale icon in menu bar)

# Verify
docker --version
# Expect: Docker version 24.x.x or similar
```

If Docker doesn’t start:

- Check System Settings → Privacy & Security → allow Docker.
- Restart the Mac.
- Relaunch Docker Desktop.

### Windows

1. Download Docker Desktop `.exe` from the same link.
2. Run installer and follow prompts.
3. Restart if asked.
4. Launch Docker Desktop.
5. Verify with `docker --version` in Command Prompt.

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker

# Add yourself to docker group (optional convenience)
sudo usermod -aG docker $USER
# Log out and back in

docker --version
```

---

## Step 2: Create Project Structure

In Terminal on macOS:

```bash
# Create directories
mkdir -p ~/job-hunt/n8n-data
mkdir -p ~/job-hunt/logs

# Go to n8n config folder
cd ~/job-hunt/n8n-data
```

- `~/job-hunt/n8n-data` → Docker + n8n config.
- `~/job-hunt/logs` → CSV output (mounted into container).

---

## Step 3: Configure Environment (`.env`)

### Create `.env`

```bash
cd ~/job-hunt/n8n-data
mate .env
```

Paste:

```bash
Adzuna_App_ID=REPLACE_WITH_YOUR_APP_ID
Adzuna_App_Key=REPLACE_WITH_YOUR_APP_KEY
```

Replace with your actual values from https://developer.adzuna.com/dashboard.

Example final `.env`:

```bash
Adzuna_App_ID=a1b2c3d4
Adzuna_App_Key=abc123def456xyz789
```

**Important:**

- No spaces around `=`.
- No quotes.

---

## Step 4: Docker Compose (`docker-compose.yml`)

In the same folder:

```bash
cd ~/job-hunt/n8n-data
mate docker-compose.yml
```

Paste:

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

Save.

**What this does:**

- Exposes n8n at `http://localhost:5678`.
- Mounts `~/job-hunt/logs` as `/files` in container.
- Loads Adzuna credentials from `.env`.
- Allows the `fs` module so n8n can write files.

---

## Step 5: Fix Folder Permissions (macOS/Linux only)

```bash
cd ~/job-hunt

# Make logs folder owned by UID 1000 (n8n user in container)
sudo chown -R 1000:1000 logs

# Make it fully writable
sudo chmod 777 logs

# Verify
ls -la logs/
# Look for: drwxrwxrwx ... logs
```

Windows: no changes needed here.

---

## Step 6: Start n8n

```bash
cd ~/job-hunt/n8n-data

# Start container in background
docker compose up -d

# Verify container is running
docker ps
# Expect a line with "n8n-job-hunt" and "Up"
```

If n8n exits immediately:

```bash
docker compose logs n8n
```

Look for:

- `.env` missing or invalid.
- Port 5678 already in use.
- Other configuration errors.

### Open n8n UI

- Browser: http://localhost:5678
- First time:
  - Create account (email + password, stored locally).
  - Skip any onboarding.

If UI is blank:

- Try private/incognito window.
- Clear browser cache.
- Restart container: `docker compose restart`.

---

## Step 7: Workflow JSON (`workflow.json`)

Create the workflow file:

```bash
cd ~/job-hunt
mate workflow.json
```

Paste the following (entire block):

```json
{
  "name": "Job Search - Canada & India",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 5}]
        }
      },
      "id": "1",
      "name": "Every 5h (5/day)",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": 
    },
    {
      "parameters": {
        "jsCode": "const searches = [\n  { country: \"ca\", where: \"Toronto\", search_query: \"software engineer backend\" },\n  { country: \"ca\", where: \"Toronto\", search_query: \"senior backend engineer java\" },\n  { country: \"ca\", where: \"Toronto\", search_query: \"staff backend engineer java\" },\n  { country: \"in\", where: \"Hyderabad\", search_query: \"software engineer backend java\" },\n  { country: \"in\", where: \"Hyderabad\", search_query: \"senior backend engineer java\" },\n  { country: \"in\", where: \"Hyderabad\", search_query: \"staff backend engineer java\" },\n  { country: \"in\", where: \"Bengaluru\", search_query: \"java spring boot engineer backend\" }\n];\nreturn searches.map(s => ({ json: s }));"
      },
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": ,
      "id": "2",
      "name": "Generate Searches"
    },
    {
      "parameters": {
        "url": "={{ 'https://api.adzuna.com/v1/api/jobs/' + $json.country + '/search/1?app_id=' + $env.Adzuna_App_ID + '&app_key=' + $env.Adzuna_App_Key + '&results_per_page=3&what=' + encodeURIComponent($json.search_query) + '&where=' + encodeURIComponent($json.where) + '&sort_by=date' }}",
        "options": {
          "batching": {
            "batch": {
              "batchSize": 1,
              "batchInterval": 3000
            }
          }
        }
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.4,
      "position": ,
      "id": "3",
      "name": "Adzuna Job Finder"
    },
    {
      "parameters": {
        "jsCode": "const out = [];\nfor (const item of $input.all()) {\n  const body = item.json;\n  const results = body.results || [];\n  const country = item.json.country;\n  const where = item.json.where;\n  const search_query = item.json.search_query;\n  for (const r of results) {\n    out.push({\n      json: {\n        job_id: r.id,\n        job_url: r.redirect_url,\n        title: r.title,\n        company: r.company?.display_name,\n        location: r.location?.display_name,\n        created: r.created,\n        description: r.description,\n        country,\n        where,\n        search_query\n      }\n    });\n  }\n}\nreturn out;"
      },
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": ,
      "id": "4",
      "name": "Extract Top 3 Jobs"
    },
    {
      "parameters": {
        "jsCode": "const staticData = $getWorkflowStaticData('global');\nstaticData.seen ??= {};\nconst now = Date.now();\nconst TTL_DAYS = 30;\nconst ttlMs = TTL_DAYS * 24 * 60 * 60 * 1000;\nfor (const [k, ts] of Object.entries(staticData.seen)) {\n  if (typeof ts === 'number' && (now - ts) > ttlMs) delete staticData.seen[k];\n}\nconst out = [];\nfor (const item of $input.all()) {\n  const key = item.json.job_id || item.json.job_url;\n  if (!key) continue;\n  if (staticData.seen[key]) continue;\n  staticData.seen[key] = now;\n  out.push(item);\n}\nreturn out;"
      },
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": ,
      "id": "5",
      "name": "Dedupe Jobs"
    },
    {
      "parameters": {
        "jsCode": "const items = $input.all();\nconst denyTitle = ['intern', 'internship', 'junior', 'entry', 'student', 'co-op', 'coop', 'qa', 'tester', 'sdet', 'support', 'administrator', 'qe'];\nconst allowTech = ['java', 'spring', 'spring boot', 'kotlin', 'jvm', 'c++', 'cpp'];\nconst backendSignals = ['backend', 'back-end', 'server-side', 'api', 'microservices', 'distributed', 'platform'];\nconst denyTech = ['php', '.net', 'c#', 'cobol', 'micro focus'];\nfunction norm(s) { return (s || '').toLowerCase(); }\nconst out = [];\nfor (const it of items) {\n  const j = it.json;\n  if (!j.job_url || !j.title) continue;\n  const title = norm(j.title);\n  const desc = norm(j.description);\n  const q = norm(j.search_query);\n  const blob = `${title} ${desc} ${q}`;\n  if (denyTitle.some(w => blob.includes(w))) continue;\n  if (denyTech.some(w => blob.includes(w))) continue;\n  const hasTech = allowTech.some(t => blob.includes(t));\n  if (!hasTech) continue;\n  const hasBackend = backendSignals.some(s => blob.includes(s));\n  const genericSE = title.includes('software engineer') || title.includes('engineer');\n  if (!(hasBackend || (genericSE && backendSignals.some(s => q.includes(s))))) continue;\n  out.push(it);\n}\nreturn out;"
      },
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": ,
      "id": "6",
      "name": "Filter Valid Jobs"
    },
    {
      "parameters": {
        "jsCode": "const items = $input.all();\nif (!items.length) return [];\nconst staticData = $getWorkflowStaticData('global');\nstaticData.csvHeaderWritten ??= false;\nfunction esc(v) {\n  if (v === null || v === undefined) return '';\n  const s = String(v);\n  return /[\",\\n]/.test(s) ? `\"${s.replace(/\"/g, '\"\"')}\"` : s;\n}\nconst header = 'timestamp,country,where,search_query,job_url,title,company,location,status\\n';\nconst now = $now.setZone('America/Los_Angeles').toFormat(\"ccc yyyy-LL-dd HH:mm 'PST'\");\nconst lines = items.map(it => {\n  const j = it.json;\n  return [now, j.country ?? '', j.where ?? '', j.search_query ?? '', j.job_url ?? '', j.title ?? '', j.company ?? '', j.location ?? '', 'pending'].map(esc).join(',') + '\\n';\n}).join('');\nconst csv_text = (staticData.csvHeaderWritten ? '' : header) + lines;\nstaticData.csvHeaderWritten = true;\nreturn [{ json: { csv_text } }];"
      },
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": ,
      "id": "7",
      "name": "Build CSV Text"
    },
    {
      "parameters": {
        "operation": "toText",
        "sourceProperty": "csv_text",
        "options": {"fileName": "applications.csv"}
      },
      "type": "n8n-nodes-base.convertToFile",
      "typeVersion": 1.1,
      "position": ,
      "id": "8",
      "name": "Convert to File"
    },
    {
      "parameters": {
        "operation": "write",
        "fileName": "/files/applications.csv",
        "options": {"append": true}
      },
      "type": "n8n-nodes-base.readWriteFile",
      "typeVersion": 1.1,
      "position": ,
      "id": "9",
      "name": "Write to Disk"
    }
  ],
  "connections": {
    "Every 5h (5/day)": {"main": [[{"node": "Generate Searches", "type": "main", "index": 0}]]},
    "Generate Searches": {"main": [[{"node": "Adzuna Job Finder", "type": "main", "index": 0}]]},
    "Adzuna Job Finder": {"main": [[{"node": "Extract Top 3 Jobs", "type": "main", "index": 0}]]},
    "Extract Top 3 Jobs": {"main": [[{"node": "Dedupe Jobs", "type": "main", "index": 0}]]},
    "Dedupe Jobs": {"main": [[{"node": "Filter Valid Jobs", "type": "main", "index": 0}]]},
    "Filter Valid Jobs": {"main": [[{"node": "Build CSV Text", "type": "main", "index": 0}]]},
    "Build CSV Text": {"main": [[{"node": "Convert to File", "type": "main", "index": 0}]]},
    "Convert to File": {"main": [[{"node": "Write to Disk", "type": "main", "index": 0}]]}
  },
  "settings": {"executionOrder": "v1"}
}
```

Save.

---

## Step 8: Import Workflow into n8n

1. Open n8n (http://localhost:5678).
2. Click **Workflows** in left sidebar.
3. Click **Add workflow**.
4. Click **⋮ → Import from file**.
5. Select `~/job-hunt/workflow.json`.
6. Click **Import**.

You should see 9 nodes in a straight line.

---

## Step 9: Manual Test Run

1. Click **Execute workflow** (play icon).
2. Wait ~30 seconds.

Check each node’s output by clicking it:

- Generate Searches → 7 items.
- Adzuna Job Finder → 7 items (each with `results`).
- Extract Top 3 Jobs → 21 items.
- Dedupe Jobs → 3–21 items (depending on past runs).
- Filter Valid Jobs → 8–15 items.
- Build CSV Text → 1 item.
- Write to Disk → success.

Check CSV:

```bash
cat ~/job-hunt/logs/applications.csv
```

You should see header + rows with CA/IN jobs.

---

## Step 10: Activate Schedule

1. Click **Publish** in the workflow.
2. Workflow should show “Active”.

Now it runs every 5 hours while Docker is running.

---

## Customization & Troubleshooting

- For customization (cities, filters, schedule) and error fixes, see `QUICK_REFERENCE.md`.
- For a short version of setup, see the main `README.md`.
