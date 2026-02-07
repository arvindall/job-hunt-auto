
***

# Interview Prep Tracker — Technical Deep Dive

Lessons learned from building + troubleshooting.

---

## 1) LeetCode GraphQL Foundation (Problem Statements)

**Why**: Claude tutoring needs full context → store `Problem Description` back in sheet (no live scraping)?

**Cloudflare blocks**: 403 "Enable JS/cookies" → slow down, retry, VPN. [web:612]

### Endpoint
- `https://leetcode.com/graphql` [web:406]
- Query: `getQuestionDetail(titleSlug: "two-sum")` → `{ title, content }`

### Setup Script (`fetch_leetcode_descriptions.py`)
```python
# Parses LeetCode_Link → titleSlug ("two-sum")
# GraphQL POST → clean HTML → write to Sheet `Problem_Description` column
# Rate limit: 1 req/sec (Cloudflare protection)
```

---

## 2) Google Sheet schema and design choices

### Why store `Problem Description` in the sheet?
- Workflow 2 becomes “no scraping, reliable”: Claude always gets full context.
- You can run tutoring offline from LeetCode availability (assuming the sheet is filled).

### Key columns
- `Status`: drives automation state machine
- `Notes`: stores Claude reviews (append-only history)
- `Last_Reviewed`: throttle knob (don’t spam yourself daily unless you want to)
- `Date_Completed`: auto-filled by Workflow 3

---

## 3) Workflow 2 Architecture (Claude Tutor) — Stable Version

### Node Order (Stable)
```
Read In Progress → Filter Single → Claude Explanation (HTTP) → Merge → Edit Fields → Combined Notes → Update Row → Gmail
```

### Key Fixes

**HTTP Request loses input**:
```
HTTP Request → response only (no original sheet row)
```
**Fix**: Merge node (Input 1: Filter Single, Input 2: Claude). [web:704] [web:700]

**Node reference errors** (`$('Node Name')`):
```
"Cannot assign to read only property 'name' of object 'Error: Referenced node doesn't exist'"
```
**Fix**: Merge → use `$json` only (no `$()`). [web:499] [web:507]

**Edit Fields (Set) node**:
- Add `review_html`, `problem_name`, etc.
- `Keep Only Set = OFF` (preserve other fields). [web:510]

**Combined Notes Code** (append + timestamp):
```javascript
const today = new Date().toISOString().slice(0, 10);
const prev = ($json.Notes || '').trim();
const review = ($json.review_html || '').trim();
const header = `\n\n===== Review ${today} =====\n`;
return [{ json: { ...$json, Notes: (prev ? prev + header : header) + review, Last_Reviewed: today } }];
```

---

## 4) Throttling (Edge Case: "Stuck Across Days")

### Requirement
If a problem stays `In Progress` for multiple days, we don't want to spam you daily unless you choose.

### Solution
Add `Last_Reviewed` + a knob `REVIEW_GAP_DAYS`:
- Start with **2 days** (current choice)
- Later ramp to **1 day**

**Filter rule**:
```
Candidate if Status == In Progress AND (Last_Reviewed blank OR older than REVIEW_GAP_DAYS)
```

**When a review is generated, update**:
```
Last_Reviewed = today
```

### Notes Appending
Instead of overwriting `Notes`, append with a dated divider:
```
===== Review 2026-02-06 =====
[Claude's review content]

===== Review 2026-02-08 =====
[Another review]
```

This gives you history without losing context.

---

## 5) Email Formatting Lessons (Gmail)

### Key Point
Markdown formatting (like triple backticks) won't render unless you convert it to HTML or have Claude output HTML.

**Solution**: Claude outputs HTML directly, then Gmail sends HTML.

**Gmail node settings**:
```
Message Type = HTML
```

**Claude prompt pattern**:
```
"Return valid HTML with <h3> for headers, <code> for inline code, and <pre><code> for blocks..."
```

---

## 6) Docker Persistence + Local Reliability

### Persistence
Mapping `/home/node/.n8n` to a named volume is what preserves workflows + credentials across restarts. [web:690] [web:693]

```yaml
volumes:
  - n8n_:/home/node/.n8n  # ✅ Workflows + creds persist here
```

### Downtime Behavior
If your machine is off, scheduled triggers won't execute during that window. The system resumes when n8n is back up (no automatic catch-up). [web:672] [web:677]

---

## 7) Common Troubleshooting

### A) "Referenced node doesn't exist"

**Error message**:
```
Cannot assign to read only property 'name' of object 'Error: Referenced node doesn't exist'
```

**Cause**:
- Using `$('Node Name')` references in Code nodes where the referenced node didn't run, or name mismatch.
- Node execution paths changed (e.g., conditional branching).

**Fix**:
1. Avoid cross-node references like `$('Claude Explanation').first()`.
2. Use **Merge node** to combine data streams.
3. Downstream nodes should only reference `$json` (the merged output).

---

### B) "No output data returned" on Google Sheets Update Row

**Symptom**:
Google Sheets Update Row node completes but shows "No output data returned".

**Cause**:
- Match column didn't find any rows.
- Common reasons:
  - `LeetCode_Link` has extra spaces or different formatting
  - Column header spelling/case mismatch
  - Row doesn't exist in sheet

**Fix**:
1. Ensure `matchColumn` is exactly `LeetCode_Link` (case-sensitive).
2. Add `.trim()` to the link in Edit Fields before updating:
   ```javascript
   link: $json.LeetCode_Link.trim()
   ```
3. Verify the row exists in the sheet with the same link value.
4. Check column headers exist: `Notes`, `Last_Reviewed`, etc.

Google Sheets node behavior depends on the selected operation and match settings. [web:256]

---

### C) "HTTP Request loses my input fields"

**Problem**:
```
Before HTTP: { problem_name: "Two Sum", link: "...", ... }
After HTTP:  { response: "Claude output" }  // Original fields gone!
```

**Cause**:
HTTP Request nodes typically output only the response, not your original input.

**Fix**:
Use **Merge node** to reattach the original fields. [web:704] [web:700]

```
Merge Node:
  Input 1: Filter Single Problem (original sheet row)
  Input 2: Claude Explanation HTTP (Claude response)
  
Output: { ...original fields, ...claude response }
```

---

### D) Cloudflare Blocks GraphQL Backfill

**Error**:
```
403 Forbidden: "Enable JavaScript and cookies to continue"
```

**Cause**:
LeetCode's Cloudflare protection detects automated requests. [web:612]

**Fix**:
1. **Slow down**: Reduce to 1 request every 1-2 seconds.
2. **Retry logic**: Catch 403/429 and retry with exponential backoff.
3. **Network change**: Use VPN or different network.
4. **Headers**: Add realistic User-Agent and headers.

---

### E) Gmail Shows Plain Text (No Formatting)

**Problem**:
Email arrives without any formatting, code blocks appear as plain text.

**Cause**:
- Gmail node set to "Text" instead of "HTML".
- Claude output is Markdown, not HTML.

**Fix**:
1. Set Gmail node: `Message Type = HTML`.
2. Update Claude prompt:
   ```
   "Return valid HTML with <h3> for section headers, <code> for inline code, 
   and <pre><code> for code blocks. Do not use Markdown."
   ```

---

### F) PC Off → Missed Schedules

**Behavior**:
Scheduled triggers (e.g., 8 AM daily email) don't run if n8n is stopped.

**Expected**: This is normal behavior. [web:672]

**Solution**:
- Keep n8n running if you need scheduled triggers.
- Consider cloud hosting (n8n Cloud, self-hosted VPS) for 24/7 availability.
- Workflows resume normally when n8n restarts (no automatic catch-up).

