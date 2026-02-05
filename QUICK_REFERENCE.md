# Quick Reference - Job Search Automation

This file is the “cheat sheet” for your n8n + Adzuna pipeline.

---

## Core Commands

### Start / Stop / Restart n8n

```bash
cd ~/job-hunt/n8n-data

# Start in background
docker compose up -d

# Stop
docker compose down

# Restart
docker compose restart

# Check running containers
docker ps

# View n8n logs (live)
docker compose logs -f n8n

# Last 50 log lines
docker compose logs --tail=50 n8n
```

---

## Output & Monitoring

### Check CSV output

```bash
# View last 20 jobs
tail -20 ~/job-hunt/logs/applications.csv

# Count total rows
wc -l ~/job-hunt/logs/applications.csv

# CA jobs
grep ",ca," ~/job-hunt/logs/applications.csv | wc -l

# IN jobs
grep ",in," ~/job-hunt/logs/applications.csv | wc -l

# Open in Numbers/Excel (macOS)
open ~/job-hunt/logs/applications.csv
```

---

## Permissions (macOS / Linux)

If you see “file not writable” or permission errors:

```bash
cd ~/job-hunt
sudo chown -R 1000:1000 logs
sudo chmod 777 logs
docker compose restart
```

Verify:

```bash
ls -la logs/
# Expect: drwxrwxrwx ... logs
```

Windows users usually don’t need this.

---

## Error → Fix Table

| Error | Quick Fix |
|-------|-----------|
| **Cannot connect to Docker daemon** | Start Docker Desktop (Mac/Win) or `sudo systemctl start docker` (Linux). |
| **Port 5678 already in use** | `sudo lsof -i :5678` → `sudo kill -9 <PID>` then restart Docker. |
| **Cannot find module 'fs'** | Ensure `NODE_FUNCTION_ALLOW_BUILTIN=fs` is set in `docker-compose.yml` environment and restart. |
| **File not writable / Forbidden** | Run the permission fix above and ensure `N8N_RESTRICT_FILE_ACCESS_TO=/files` in `docker-compose.yml`. |
| **Adzuna 401 Unauthorized** | Check `.env` (correct `Adzuna_App_ID` / `Adzuna_App_Key`, no spaces), then `docker compose restart`. |
| **Adzuna 403 Rate limit** | You hit 250 calls/day; reduce number of searches or increase interval. |
| **Only 3 jobs every time** | Confirm **Generate Searches → Adzuna Job Finder** connection is direct (no disabled nodes in between). |
| **Empty results (count: 0)** | Simplify `search_query`, or try a larger city. |
| **CSV header repeats** | Expected after re-importing workflow (static data reset). Remove extra header rows manually once. |
| **Duplicate jobs over days** | Ensure “Dedupe Jobs” node is enabled and still wired in the chain. |

---

## File Locations

| Item | Path |
|------|------|
| CSV output | `~/job-hunt/logs/applications.csv` |
| n8n config | `~/job-hunt/n8n-data/docker-compose.yml` |
| Environment vars | `~/job-hunt/n8n-data/.env` |
| Workflow JSON (local) | `~/job-hunt/workflow.json` (or wherever you saved it) |
| n8n internal data | Docker volume `n8n_data` |
| n8n logs | `docker compose logs n8n` |

---

## Workflow Node Order (Expected)

1. **Every 5h (5/day)** – Schedule trigger.
2. **Generate Searches** – Emits 7 search items (CA/IN).
3. **Adzuna Job Finder** – Calls Adzuna API (7 calls, 3s apart).
4. **Extract Top 3 Jobs** – Flattens API results to 21 job items.
5. **Dedupe Jobs** – Drops jobs seen in last 30 days.
6. **Filter Valid Jobs** – Keeps Java/C++ backend roles only.
7. **Build CSV Text** – Creates CSV string with header-once logic.
8. **Convert to File** – Converts text to binary file.
9. **Write to Disk** – Appends to `/files/applications.csv`.

---

## Expected Items Per Node (Manual Run)

When you click **Execute workflow**:

| Node | Expected items |
|------|----------------|
| Generate Searches | 7 |
| Adzuna Job Finder | 7 (each with `results`) |
| Extract Top 3 Jobs | 21 |
| Dedupe Jobs | 3–21 (depends on history) |
| Filter Valid Jobs | ~8–15 |
| Build CSV Text | 1 |
| Convert to File | 1 |
| Write to Disk | 1 |

If any node shows `0` items unexpectedly, click the previous node and inspect its output.

---

## API Usage Math

Adzuna free tier: **250 calls/day**.

Current setup:

- 7 searches per run  
- Every 5 hours → ~5 runs/day  
- 7 × 5 = **35 calls/day** (safe).

Scaling examples:

- 20 searches × 5 runs = 100 calls/day (safe).  
- 50 searches × 5 runs = 250 calls/day (max).  
- 50 searches × 10 runs = 500 calls/day (over limit).

---

## Filter Quick Tweaks (Filter Valid Jobs node)

### Allow more tech stacks

Inside the filter code:

```javascript
const allowTech = [
  'java', 'spring', 'spring boot', 'kotlin', 'jvm',
  'c++', 'cpp',
  'python', 'go', 'golang', 'rust'  // add or remove as needed
];
```

### Block specific companies

```javascript
const denyCompany = ['tcs', 'infosys', 'wipro', 'cognizant'];

if (company && denyCompany.some(c => company.includes(c))) continue;
```

(Place this after computing `company` and after tech checks.)

### Relax filters temporarily (debugging)

```javascript
// Temporarily disable deny lists:
const denyTitle = [];
const denyTech = [];
```

Run once to see raw jobs, then tighten again.

---

## Diagnostics

### No jobs in CSV after 24 hours

1. Confirm workflow is **Active** in n8n (Published).
2. Check logs:

```bash
docker compose logs n8n | grep "Workflow"
```

3. Look for errors:

```bash
docker compose logs n8n | grep -i error
```

4. Execute workflow manually once and walk through node outputs.

### Too many PHP / frontend roles

Add more to `denyTech`:

```javascript
const denyTech = [
  'php', '.net', 'c#', 'cobol', 'micro focus',
  'javascript', 'typescript', 'react', 'angular', 'vue', 'frontend', 'front-end'
];
```

---

## Performance Benchmarks (for sanity check)

With current settings:

- Execution time: ~30 seconds per run.
- Jobs logged per run: 8–12.
- Jobs logged per day: 40–60.
- Jobs logged per week: 280–420.
- CSV growth: ~3KB/day (~90KB/month).
- API calls: 35/day.

If you see very different numbers, inspect filters/dedupe.

---

## Backup & Restore

### Backup

```bash
# In n8n UI: export workflow (Download JSON)

# Backup CSV
mkdir -p ~/job-hunt/backups
cp ~/job-hunt/logs/applications.csv ~/job-hunt/backups/applications_$(date +%Y%m%d).csv
```

### Restore After Breakage

```bash
# Stop n8n
cd ~/job-hunt/n8n-data
docker compose down

# (Optional) remove volume if totally corrupted
# docker volume rm n8n_data

# Start fresh
docker compose up -d

# Import workflow JSON in n8n UI
# Copy backup CSV back to logs if needed
cp ~/job-hunt/backups/applications_YYYYMMDD.csv ~/job-hunt/logs/applications.csv
```

---

## When to Ask for Help

Ask for help if:

- Same error persists after trying fixes here.
- Workflow runs but outputs 0 jobs for multiple runs.
- CSV is full of irrelevant roles even after filter tuning.
- n8n crashes or refuses to start.

Include when asking:

1. Full error message.
2. Output of: `docker compose logs --tail=50 n8n`.
3. Which node fails.
4. OS + Docker Desktop version.

---

## Weekly Success Pattern

- **Week 1:** Setup, test, filter tuning, let it run.
- **Week 2:** 300+ jobs collected, start applying.
- **Week 3:** Scale searches and optionally export to Sheets or add scoring.
