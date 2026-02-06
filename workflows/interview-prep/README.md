# Interview Prep Tracker (LeetCode + Google Sheets + n8n + Claude)

An interview-prep tracking system that:
- Organizes problems in Google Sheets (single source of truth)
- Sends a daily curated set of problems (Workflow 1)
- Provides Claude tutoring/review for “In Progress” problems (Workflow 2)
- Auto-fills `Date_Completed` when you mark a problem `Completed` (Workflow 3)

This repo favors **reliability**: we store problem statements in the sheet (foundation), so n8n doesn’t need brittle scraping.

---

## Key idea: Sheet is the source of truth

We keep a Google Sheet tab `Questions` with at least:

- `Company`
- `Problem_Name`
- `Difficulty`
- `Pattern`
- `LeetCode_Link`
- `Statement` (or `Problem_Description`)
- `Status` (Not Started / In Progress / Completed)
- `Date_Completed`
- `Notes`
- `Last_Reviewed` (throttle for follow-up reviews)

n8n reads/writes this sheet via the Google Sheets node operations. [web:256]

---

## Docker persistence (local n8n)

We run n8n locally using Docker Compose with persistence:

```yaml
services:
  n8n:
    volumes:
      - n8n_:/home/node/.n8n
      - ./logs:/files

volumes:
  n8n_:
    driver: local
	
Persisting  /home/node/.n8n  is what keeps workflows, credentials, and settings across restarts. web:690web:693
Note: if your PC is off, scheduled triggers won’t run during downtime (they don’t “catch up” automatically). web:672web:677
Foundation: Problem statements in the sheet
Claude tutoring works best when it always receives the full problem statement.
We backfill  Statement / Problem_Description  using LeetCode’s GraphQL endpoint  https://leetcode.com/graphql . web:406
LeetCode sometimes places Cloudflare protections on the endpoint (403 “Enable JavaScript and cookies…”), so the backfill script includes rate limiting and retries. web:612
Workflows
Workflow 1 — Daily problem set
Goal: Send a daily set of problems (e.g., 3) filtered by company/difficulty and update the sheet.
Typical actions:
	•	Read  Questions 
	•	Filter:  Company = Amazon ,  Status = Not Started 
	•	Pick N by difficulty
	•	Email you the list
	•	Update selected rows to  In Progress  (optional)
(Workflow JSON stored under  n8n-workflows/ .)
Workflow 2 — Claude Tutor (no scraping)
Goal: For a single “In Progress” problem, send tutoring + store the review in  Notes .
Design constraints learned during troubleshooting:
	•	Avoid brittle node references like  $('Some Node')  in Code nodes; it can error if a referenced node wasn’t executed.
	•	HTTP Request nodes often return only response data, so you must explicitly merge/carry the original row forward. web:704web:700
Recommended approach:
	•	 Read In Progress  →  Filter Single Problem  →  Claude Explanation (HTTP)  →  Merge  →  Edit Fields  →  Combine Notes  →  Update Row  →  Gmail 
 Edit Fields (Set)  is used to shape fields without losing required inputs. web:510
Throttle edge case:
	•	Add  Last_Reviewed  and use a knob (2 days now, 1 day later) so you don’t spam yourself if you’re stuck.
	•	Append to  Notes  so you keep history across follow-ups.
Workflow 3 — Auto-fill completion date
Goal: You update  Status = Completed  from your phone or laptop; n8n fills  Date_Completed  automatically.
Schedule (hourly):
	•	Read  Questions 
	•	Filter  Status == Completed AND Date_Completed empty 
	•	Set  Date_Completed = today 
	•	Update row (match on  LeetCode_Link )
Google Sheets updates are done with “Update Row” + match column. web:256
What to do daily (habit loop)
	1.	Morning: Workflow 1 suggests problems
	2.	When stuck: set  Status = In Progress  and let Workflow 2 tutor
	3.	After solving: set  Status = Completed  (phone or laptop); Workflow 3 fills the date
Files in this folder
	•	 DETAILS.md  — Full setup + internals + troubleshooting
	•	 QUICK_REFERENCE.md  — Commands/snippets/checklists
