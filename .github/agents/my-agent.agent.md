---
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

name:
description:
---

# My Agent

Describe what your agent does here.





Pasted text(31).txt
Document
fix this smartly

Uploaded image
fix

Your flow is still fundamentally wrong in one place:

You are making Gemini do:

scraping

filtering

ranking

orchestration

notifications

inside one visual chain.

That creates:

hallucinated jobs

repeated jobs

broken apply links

unstable execution

The fix is:

split deterministic nodes from AI nodes
Your current graph is:

Resume
→ AI scoring
→ AI filtering
→ AI CV generation
→ AI tracking
→ AI notification
That is unstable.

FIXED VERSION
You need THIS architecture instead:

Validated Jobs JSON
        ↓
Deterministic Filter
        ↓
Gemini Score Node
        ↓
Deterministic Dedup Node
        ↓
Resume Tailor Node
        ↓
Google Sheets Append
        ↓
Telegram Notification
WHAT TO REMOVE
REMOVE:
❌ “Target Companies” node

Hardcoding companies inside prompts is bad.

Instead:

store target companies in Google Sheets
OR

static JSON

REMOVE:
❌ “Score Job Relevance” directly from raw internet

Gemini should NEVER receive:

search internet for aerospace jobs
Instead:

{
  "company": "Agnikul",
  "role": "CFD Intern",
  "description": "...",
  "apply_url": "..."
}
THE MAIN FIX
Your system is missing:

deterministic ingestion layer
Without that:
Gemini invents jobs.

CORRECT FLOW DESIGN
NODE 1 — VALIDATED JOBS INPUT
This MUST come from:

Lever API

Greenhouse API

Ashby API

controlled scraper

NOT Gemini.

Input example:

[
  {
    "company": "Agnikul",
    "role": "CFD Intern",
    "apply_url": "https://boards.greenhouse.io/...",
    "location": "Chennai",
    "description": "..."
  }
]
NODE 2 — FILTER NODE (NON-AI)
Use rule logic:

if fresher:
    +15

if india:
    +10

if aerospace:
    +20

if senior:
    reject
This should NOT be prompt-based.

NODE 3 — GEMINI SCORE
ONLY scoring.

Prompt:

You are evaluating aerospace jobs for Aman Rai.

Rules:
- prioritize UAV
- prioritize CFD
- prioritize CAD
- prioritize simulation
- prioritize fresher-friendly roles
- reject senior roles
- reject unrelated software jobs

Return STRICT JSON:

{
  "score": number,
  "category": "",
  "missing_skills": [],
  "reason": ""
}
NOT paragraphs.

NODE 4 — DEDUPLICATION
You currently don't have this.

That is why jobs repeat forever.

Add:

job_hash
Formula:

sha256(company + role + apply_url)
Store hashes in:

Google Sheets
OR

SQLite

Reject duplicates BEFORE Gemini.

NODE 5 — RESUME TAILOR
Current problem:
AI likely rewrites entire resume.

Wrong.

Correct:
ONLY modify:

summary

skill ordering

project ordering

NEVER:

fake experience

fake projects

fake metrics

NODE 6 — GOOGLE SHEETS UPDATE
You should have ONLY these sheets:

Applications
| Date | Company | Role | Apply URL | Score | Status |

Skills
| Skill | Missing Count | Priority |

Resume Versions
| Resume Name | Role | Drive Link |

NODE 7 — TELEGRAM
Your current Telegram output is too verbose.

Correct output:

🚀 2 New Aerospace Jobs

1. Agnikul — CFD Intern
Score: 84
Apply:
https://boards.greenhouse.io/...

2. NewSpace — UAV Engineer
Score: 79
Apply:
https://jobs.lever.co/...
NOT giant AI essays.

YOUR BIGGEST BUG
This node:

“Generate Tailored Content”
is overloaded.

Split into:

Resume Tailor

Cover Letter

Skill Extractor

Separate responsibilities.

ADD THIS NODE
NODE — URL VALIDATOR
Reject:

linkedin homepage
company homepage
search pages
Allow ONLY:

jobs.lever.co
greenhouse.io
ashbyhq.com
This single node fixes:

fake apply links

broken navigation

YOUR FINAL GRAPH SHOULD LOOK LIKE THIS
Validated Jobs Feed
        ↓
URL Validator
        ↓
Deduplication
        ↓
Rule-Based Filter
        ↓
Gemini Scoring
        ↓
Resume Tailor
        ↓
Cover Letter Generator
        ↓
Google Sheets Update
        ↓
Telegram Notification
MOST IMPORTANT DESIGN CHANGE
Your current system is:

AI-first
It should become:

data-first
Meaning:

deterministic inputs

AI only for enhancement

NOT orchestration.

CRITICAL THING YOU MISSED
You need:

source attribution
Every job must store:

{
  "source": "greenhouse",
  "source_url": "...",
  "apply_url": "...",
  "scraped_at": "..."
}
Otherwise debugging becomes impossible.

FINAL ADVICE
Right now:

80% of your problems
come from:

letting Gemini think too much.

Reduce Gemini responsibility.

Use Gemini ONLY for:

scoring

tailoring

summarizing

Everything else:

deterministic logic

validated feeds

strict schemas

That is how you stabilize this system.


Uploaded image

Pasted text(33).txt
Document
fix this 

Your workflow is still too AI-heavy and still missing:

deterministic validation

deduplication

real job ingestion

command-based Telegram interaction

Right now your graph is basically:

AI → AI → AI → AI
That causes:

repeated links

hallucinated jobs

unstable outputs

random formatting

bad apply URLs

The fix is:

convert this into a pipeline system
WHAT IS WRONG IN YOUR CURRENT FLOW
BAD NODE
“Generate Tailored Content”
This node is doing:

resume generation

cover letter generation

learning task generation

file writing

inside one prompt.

That is unstable.

Split it.

FIXED ARCHITECTURE
FINAL FLOW
Validated Jobs Feed
        ↓
URL Validator
        ↓
Deduplication
        ↓
Rule-Based Filter
        ↓
Gemini Job Scorer
        ↓
Resume Tailor
        ↓
Cover Letter Generator
        ↓
Skill Gap Extractor
        ↓
Google Sheets Update
        ↓
Telegram Notification
REMOVE THESE NODES
REMOVE:
❌ Target Companies node

Store target companies in:

Google Sheet
OR

static JSON config

NOT prompt input.

REMOVE:
❌ Generate Tailored Content

Split into:

Resume Tailor

Cover Letter

Skill Tasks

ADD THESE NODES
NODE 1 — URL VALIDATOR
This is CRITICAL.

Prompt:

Validate ONLY ATS apply links.

ALLOW:
- jobs.lever.co
- greenhouse.io
- ashbyhq.com
- workable.com

REJECT:
- company homepage
- linkedin feed
- search result pages
- login pages

Return valid jobs JSON only.
This fixes:

broken links

homepage spam

fake applications

NODE 2 — DEDUPLICATION
You currently have NONE.

That is why:

same jobs repeat

notifications repeat

Logic:

hash = sha256(company + role + location)
Store hashes in:

Google Sheet
OR

local JSON

Reject duplicates BEFORE Gemini.

NODE 3 — RULE FILTER
This should NOT use AI.

Use deterministic logic:

if "senior" in role:
    reject

if "5+ years" in description:
    reject

if "india" not in location:
    penalty

if "CFD" in description:
    bonus
This massively reduces hallucination.

NODE 4 — GEMINI JOB SCORER
ONLY scoring.

NOT web searching.

Prompt:

You are evaluating aerospace jobs.

Prioritize:
- UAV
- CFD
- CAD
- simulation
- fresher-friendly
- aerospace manufacturing

Penalize:
- senior roles
- unrelated software jobs

Return STRICT JSON:
{
  "score": 0,
  "reason": "",
  "missing_skills": []
}
VERY IMPORTANT:

STRICT JSON ONLY
NO MARKDOWN
NO EXPLANATION
Otherwise your workflow breaks.

NODE 5 — RESUME TAILOR
ONLY:

reorder skills

optimize ATS keywords

improve summary

NEVER:

create fake experience

invent projects

hallucinate tools

Prompt:

Optimize the resume for ATS.

ONLY:
- reorder existing skills
- improve wording
- optimize summary

DO NOT:
- invent projects
- invent internships
- invent metrics
NODE 6 — COVER LETTER
Separate node.

Prompt:

Generate concise aerospace-specific cover letter.

Requirements:
- technical
- honest
- fresher-friendly
- no corporate fluff
- under 250 words
NODE 7 — SKILL TASK GENERATOR
Separate node.

Prompt:

Analyze missing skills from selected jobs.

Generate ONE:
- 30-60 min task
- free resource
- practical proof task

Return JSON:
{
 "skill":"",
 "task":"",
 "resource":"",
 "proof_required":""
}
YOUR BIGGEST FIX
Right now:

Gemini is thinking too much.
Gemini should NEVER:

scrape

discover jobs

decide URLs

deduplicate

Gemini should ONLY:

classify

summarize

tailor

TELEGRAM FIX
You said:

I want trigger directly from Telegram

Correct architecture:

Telegram
   ↓
Webhook
   ↓
Google Workflow
   ↓
Pipeline executes
   ↓
Telegram response
REQUIRED COMMANDS
Implement:

Command	Action
/jobs	fetch latest jobs
/apply	show top matches
/skills	today's skill
/resume	latest tailored resume
/status	applications summary
/refresh	rerun workflow
IMPORTANT FIX
Your current workflow is:

batch-output based
You need:

command-triggered execution
Otherwise:

you manually rerun every time

no interaction

no automation

GOOGLE-WORKFLOW-SPECIFIC FIX
Since Google workflow only supports:

feeds

ports

outputs

assistants

DO THIS:

KEEP AI NODES SMALL
BAD:

Generate all career content
GOOD:

Score jobs
Generate resume summary
Generate skill task
Small prompts = stable outputs.

YOUR FINAL MINIMAL MVP
INPUT
Validated Jobs JSON

↓

NODE 1
URL Validator

↓

NODE 2
Deduplication

↓

NODE 3
Rule Filter

↓

NODE 4
Gemini Scoring

↓

NODE 5
Resume Tailor

↓

NODE 6
Cover Letter

↓

NODE 7
Skill Task

↓

NODE 8
Google Sheets Append

↓

NODE 9
Telegram Notify

MOST IMPORTANT CHANGE
STOP building:

autonomous AI agent
START building:

deterministic aerospace productivity system
That is the architecture that will actually work reliably. 



Uploaded image

Pasted text(34).txt
Document
fix

The error is happening because your workflow still expects:

validated_jobs_json
BUT you are not feeding actual JSON into it.

So the whole pipeline blocks at:

Provide JSON list of scraped job URLs
That means:

your workflow is still designed as manual-input driven
instead of:

autonomous pipeline driven
REAL FIX
You need to remove:

ask_user_validated_jobs_json
ENTIRELY.

Because:

Telegram should trigger workflow

backend should fetch jobs

workflow should RECEIVE jobs automatically

NOT ask user.

FIX YOUR FLOW LIKE THIS
DELETE THESE INPUT NODES
❌ Validated Jobs Json
❌ Target Companies

Keep ONLY:

User Profile
Telegram Command
WHY IT IS FAILING
Your current flow:

User
 ↓
Paste jobs JSON manually
 ↓
Workflow starts
But your desired flow is:

Telegram command
 ↓
Backend fetches jobs
 ↓
Workflow processes automatically
Completely different architecture.

CORRECT GOOGLE-WORKFLOW DESIGN
FLOW
Telegram Command
      ↓
Fetch Jobs
      ↓
Validate Jobs
      ↓
Deduplicate
      ↓
Score Jobs
      ↓
Resume
      ↓
Cover Letter
      ↓
Skill Task
      ↓
Google Sheets
      ↓
Telegram Reply
ADD NEW NODE
NODE:
Fetch Jobs
Place this FIRST.

NODE TITLE
Fetch Aerospace Jobs
PROMPT
Paste EXACTLY:

Objective:
Fetch recent aerospace-related jobs from structured ATS-compatible sources.

ONLY include:
- Greenhouse
- Lever
- Ashby
- Wellfound

Focus:
- UAV
- CFD
- CAD
- Aerospace
- Simulation
- Manufacturing

Prioritize:
- India
- Remote
- Fresher-friendly

REJECT:
- senior roles
- unrelated software jobs
- expired jobs
- company homepage links

Return STRICT JSON ONLY:

[
 {
   "company":"",
   "role":"",
   "location":"",
   "apply_url":"",
   "source":""
 }
]

IMPORTANT:
- apply_url must be direct ATS apply link
- no markdown
- no explanation
- no duplicate links
THEN CONNECT
Fetch Jobs
   ↓
Filter And Validate Jobs
FIX FILTER NODE
Your current prompt is too vague.

Replace with:

Objective:
Validate and filter aerospace jobs.

Rules:
1. Remove duplicates
2. Keep ONLY ATS apply links
3. Reject homepage URLs
4. Reject expired jobs
5. Reject senior roles
6. Reject non-aerospace jobs

VALID DOMAINS:
- jobs.lever.co
- greenhouse.io
- ashbyhq.com
- workable.com

Return STRICT JSON ONLY:

[
 {
   "company":"",
   "role":"",
   "location":"",
   "apply_url":""
 }
]
FIX SCORE NODE
Your current score node does NOT enforce strict schema strongly enough.

Replace with:

You are an aerospace job scoring engine.

Evaluate:
- UAV relevance
- CFD relevance
- CAD relevance
- simulation relevance
- fresher suitability

Penalize:
- software-only jobs
- senior jobs
- unrelated industries

Return STRICT JSON ONLY:

[
 {
   "company":"",
   "role":"",
   "score":0,
   "reason":"",
   "missing_skills":[]
 }
]

NO MARKDOWN
NO EXTRA TEXT
BIGGEST FIX
REMOVE:
Ask user for current CV
inside Resume node.

You already uploaded CV asset.

The node should use:

Aman_Rai_CV_13-03-2026.pdf
directly.

FIX RESUME NODE
Replace with:

Objective:
Optimize the uploaded CV for the highest-scored aerospace role.

ONLY:
- reorder existing skills
- improve ATS wording
- refine professional summary

DO NOT:
- invent experience
- invent projects
- invent certifications

Use uploaded CV asset as source.

Return:
{
 "summary":"",
 "skills":[]
}
FIX TELEGRAM NODE
Current issue:
It behaves like chatbot memory.

BAD.

You need deterministic command handling.

REPLACE TELEGRAM PROMPT WITH:
You are a Telegram command processor.

Supported commands:
- /jobs
- /skills
- /resume
- /status
- /refresh

Rules:
- respond concisely
- no conversational filler
- use tracking sheet data
- return actionable information only

Examples:

/jobs
→ latest top aerospace jobs

/skills
→ today's skill task

/status
→ application summary
MOST IMPORTANT FIX
STOP ASKING USER FOR DATA MID-WORKFLOW
Your current flow still behaves like:

interactive chatbot
You need:

pipeline automation
FINAL NODE STRUCTURE
Telegram Command
      ↓
Fetch Aerospace Jobs
      ↓
Filter & Validate
      ↓
Score Jobs
      ↓
Tailor Resume
      ↓
Generate Cover Letter
      ↓
Generate Skill Task
      ↓
Update Google Sheet
      ↓
Telegram Response
      ↓
Dashboard
REMOVE THIS COMPLETELY
❌ “Chat with user if clarification needed”

inside automation nodes.

That breaks automation.

CRITICAL GOOGLE WORKFLOW LIMITATION
Google workflow agents are BAD at:

long memory

persistent context

deterministic state

So:

every node must produce STRICT STRUCTURED OUTPUT
NOT conversational text.

FINAL IMPORTANT CHANGE
Your current system:

AI-powered workflow
Your target system:

deterministic workflow with AI assistance
That architectural shift is what fixes reliability. 


DEVELOPER MODE



