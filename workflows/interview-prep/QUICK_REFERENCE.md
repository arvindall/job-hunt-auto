# Interview Prep Tracker — Quick Reference

## Docker (n8n local)

```bash
docker compose up -d
docker compose logs -f n8n
docker compose restart n8n
Persistence checklist:
	•	 /home/node/.n8n  mapped to named volume (required for keeping workflows/creds). web:690web:693
LeetCode GraphQL test
Endpoint:
	•	 https://leetcode.com/graphql  web:406
Test with curl (example slug:  two-sum ):
curl -s https://leetcode.com/graphql \
  -H 'content-type: application/json' \
  -H 'user-agent: Mozilla/5.0' \
  --data-raw '{
    "query": "query getQuestionDetail($titleSlug: String!) { question(titleSlug: $titleSlug) { title content } }",
    "variables": { "titleSlug": "two-sum" }
  }' | head
If you see Cloudflare/403 HTML, slow down, retry later, or run from another network. web:612
Workflow 2 (Tutor) checklist
	•	Sheet columns exist:  Statement ,  Status ,  Notes ,  Last_Reviewed 
	•	Filter logic uses  REVIEW_GAP_DAYS  knob (2 → 1 later)
	•	Claude outputs HTML
	•	Merge node used after Claude so  $json  contains both row + review
	•	Update Row matches on  LeetCode_Link  and updates  Notes  +  Last_Reviewed 
Reminder: HTTP node doesn’t retain input → Merge is required. web:704
Workflow 3 (Auto Date Completed) checklist
	•	You set  Status = Completed 
	•	 Date_Completed  empty
	•	Hourly schedule runs
	•	Update Row matches by  LeetCode_Link 
Google Sheets Update Row uses match column + mapped values. web:256
Handy patterns
“Append Notes with timestamp” (Code node snippet)
const today = new Date().toISOString().slice(0, 10);
const prev = ($json.Notes || '').trim();
const review = ($json.review_html || '').trim();

const header = `\n\n===== Review ${today} =====\n`;
return [{ json: { ...$json, Notes: (prev ? prev + header : header) + review, Last_Reviewed: today } }];