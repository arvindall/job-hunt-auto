
***

# Interview Prep Tracker — Details

This doc contains the “why” and the troubleshooting history we learned while building the system.

---

## 1) LeetCode problem statement backfill (GraphQL)

We backfill problem statements into the sheet to avoid scraping.

### Endpoint
- `https://leetcode.com/graphql` [web:406]

### Example query
Use the `titleSlug` parsed from a LeetCode URL, then request `title` + `content`. (We store cleaned text or HTML in the sheet.)

LeetCode can temporarily block automated traffic via Cloudflare (403). If you see “Enable JavaScript and cookies to continue,” slow down requests, retry later, or run from a different network. [web:612]

### Rate limiting
Use ~1 req/sec (or slower) and retry on 429/403. (This is a practical stability choice; the exact number depends on your experience with throttling.)

---

## 2) Google Sheet schema and design choices

### Why store `Statement` in the sheet?
- Workflow 2 becomes “no scraping, reliable”: Claude always gets full context.
- You can run tutoring offline from LeetCode availability (assuming the sheet is filled).

### Key columns
- `Status`: drives automation state machine
- `Notes`: stores Claude reviews (append-only history)
- `Last_Reviewed`: throttle knob (don’t spam yourself daily unless you want to)
- `Date_Completed`: auto-filled by Workflow 3

---

## 3) Workflow 2 architecture (Claude Tutor) — stable version

### Problem we hit
- Expressions like `$('Claude Explanation').first()` can throw “Referenced node doesn’t exist” if the node wasn’t executed in the run path (or names changed).
- HTTP Request output can lose original input context unless merged back.

### Fix
Use a **Merge node** to combine:
- Branch A: the selected sheet row (from `Filter Single In Progress Problem`)
- Branch B: Claude response (from `Claude Explanation` HTTP request)

Then downstream nodes use only the merged `$json`, avoiding cross-node references.

This aligns with the known behavior that the HTTP node doesn’t retain input data, so you should merge results back to original input. [web:704]

### Edit Fields node
Use Edit Fields (Set) to normalize names like:
- `problem_name`
- `difficulty`
- `link`
- `review_html` (Claude output)

Edit Fields can overwrite or add fields and can keep other input fields depending on settings. [web:510]

---

## 4) Throttling (edge case: “stuck across days”)

### Requirement
If a problem stays `In Progress` for multiple days, we don’t want to spam you daily unless you choose.

### Solution
Add `Last_Reviewed` + a knob `REVIEW_GAP_DAYS`:
- Start with 2 days (your current choice)
- Later ramp to 1 day

Filter rule:
- Candidate if `Status == In Progress` AND (`Last_Reviewed` blank OR older than REVIEW_GAP_DAYS)

When a review is generated, update:
- `Last_Reviewed = today`

### Notes appending
Instead of overwriting `Notes`, append with a dated divider:
===== Review 2026-02-06 ===== 
===== Review 2026-02-08 ===== 

This gives you history without losing context.

---

## 5) Email formatting lessons (Gmail)

### Key point
Markdown formatting (like triple backticks) won’t render unless you convert it to HTML or have Claude output HTML.

We chose: **Claude outputs HTML** directly, then Gmail sends HTML.

---

## 6) Docker persistence + local reliability

### Persistence
Mapping `/home/node/.n8n` to a named volume is what preserves workflows + credentials across restarts. [web:690][web:693]

### Downtime behavior
If your machine is off, scheduled triggers won’t execute during that window. The system resumes when n8n is back up. [web:672][web:677]

---

## 7) Common troubleshooting

### A) “Referenced node doesn’t exist”
Cause:
- Using `$()` node references in paths where the referenced node didn’t run, or name mismatch.

Fix:
- Avoid cross-node references inside Code nodes.
- Merge Claude response + sheet row, then use only `$json`.

### B) “No output data returned” on Google Sheets Update Row
Cause:
- Match column didn’t find any rows (commonly because `LeetCode_Link` differs, extra spaces, or wrong header).

Fix:
- Ensure `matchColumn` is exactly `LeetCode_Link`.
- `.trim()` the link in your pipeline before updating.
- Confirm the row exists in the sheet with the same link.

Google Sheets node behavior depends on the selected operation and match settings. [web:256]

### C) “HTTP Request loses my input fields”
Cause:
- HTTP Request nodes typically output the response (not your original input).

Fix:
- Use Merge to reattach the original fields. [web:704][web:700]

