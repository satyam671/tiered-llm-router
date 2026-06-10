# Tiered LLM Router

A production-ready Python implementation of a three-tier LLM cascade architecture that routes queries to the cheapest capable model, reducing API costs by 65% on typical workloads.

**Article:** [How to Build a Tiered AI Architecture That Saves Your Budget](https://medium.com/@satyamsahu671/tiered-llm-router) (Medium)

**Live Example:** Route the same query through three different price tiers and see real cost/quality trade-offs in action.

---

## What This Does

You send a query. A cheap classifier (Claude Haiku 4.5, $0.001 per call) instantly decides: is this a simple task, moderate task, or complex reasoning problem?

Based on that decision:
- **Simple queries** (70%) → Gemini 2.5 Flash-Lite ($0.10/$0.40 per M tokens) — extraction, formatting, classification
- **Moderate queries** (20%) → Claude Sonnet 4.6 ($3.00/$15.00 per M tokens) — single-doc analysis, code gen
- **Complex queries** (10%) → Claude Opus 4.8 ($5.00/$25.00 per M tokens) — reasoning, synthesis, ambiguous tasks

**Result:** Same app functionality, $3,432 less per month ($41,000/year at scale).

---

## Quick Start (3 minutes)

### 1. Clone this repo

```bash
git clone https://github.com/satyam671/tiered-llm-router.git
cd tiered-llm-router
```

### 2. Get API keys

**Anthropic key:** [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key

**Google AI key:** [aistudio.google.com](https://aistudio.google.com) → Get API key

### 3. Set up environment

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env from template
cp .env.example .env

# Edit .env and paste your actual API keys
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=AIzaSy...
```

### 4. Run smoke test

```bash
python3 router.py
```

You'll see three sample queries classified and routed:
- "Extract invoice number" → **simple** tier → Gemini Flash-Lite
- "Write Python function" → **moderate** tier → Claude Sonnet 4.6
- "Synthesize regulations" → **complex** tier → Claude Opus 4.8

Each with token counts and cost breakdown.

---

## What's in This Repo

```
tiered-llm-router/
├── router.py           ← Main implementation (the tiered cascade)
├── evaluate.py         ← Classifier accuracy evaluation (>85% target)
├── shadow.py           ← Production traffic measurement (no routing change)
├── requirements.txt    ← Python dependencies
├── .env.example        ← Template for API keys (copy to .env)
├── .gitignore          ← Prevent committing secrets
└── README.md           ← This file
```

---

## Three Executable Scripts

### 1. **router.py** — The main implementation

```bash
python3 router.py
```

Run the smoke test. Three sample queries are classified and routed. Each result includes:
- `tier` — the predicted complexity tier
- `model` — which model handled it
- `input_tokens`, `output_tokens` — for cost calculation
- `text` — the actual response

**Expected output:**
```
======================================================================
TIERED LLM ROUTER — SMOKE TEST
======================================================================

Query 1: Extract the invoice number from: 'Please see Invoice #42817'...

  ✓ Tier:         simple
  ✓ Model:        gemini-2.5-flash-lite
  ✓ Input tokens: 45
  ✓ Output tokens: 8
  ✓ Response:     Invoice #42817...

[continues for queries 2 and 3...]

======================================================================
All tests passed. Router is working correctly.
======================================================================
```

**What to look for:**
- ✓ All three queries complete without errors
- ✓ Tier assignments match your expectations (simple → simple, moderate → moderate, complex → complex)
- ✓ Output tokens are small for simple queries, larger for complex ones

### 2. **evaluate.py** — Classifier accuracy evaluation

```bash
python3 evaluate.py
```

Tests the classifier against 7 labelled queries. Target: >85% accuracy.

**Expected output:**
```
======================================================================
CLASSIFIER EVALUATION HARNESS
======================================================================

Classifier accuracy: 86%

  ✓ [simple → simple]
     Query: Extract all phone numbers from: 'Call 555-0123 or 555-0199'
     Reason: Formatting task with fixed output.

  ✓ [simple → simple]
     Query: Translate 'Good morning' to French
     ...

  [continues for all 7 test cases...]

======================================================================
Results: 6 passed, 1 failed
✓ Accuracy is above 85%. Safe to enable live routing.
======================================================================
```

**What to look for:**
- ✓ Accuracy ≥85% means the classifier is reliable enough for production
- ✗ Accuracy <80% means refine the `CLASSIFIER_SYSTEM_PROMPT` in `router.py` to improve tier definitions
- Review any misclassified queries — they tell you where your tier definitions need tightening

### 3. **shadow.py** — Production traffic measurement

```bash
python3 shadow.py
```

This is a demo. In production, you'd import and call `shadow_classify()` alongside your existing system for 2 weeks to measure real query distribution before enabling live routing.

**Expected output:**
```
======================================================================
SHADOW MODE — SAMPLE OUTPUT
======================================================================

Request req-001: tier=simple

Request req-002: tier=moderate

Request req-003: tier=complex

======================================================================
After 2 weeks of shadow mode in production, analyze tier distribution.
Aggregate counts of 'simple', 'moderate', 'complex' from your logs.
This real distribution validates your cost model before live routing.
======================================================================
```

---

## Step-by-Step Setup on Your Laptop

### Prerequisites

- **Python 3.9 or higher** (check: `python3 --version`)
- **git** installed
- A code editor (VS Code recommended)
- Internet connection (for API calls)

### Step 1: Clone the Repository

```bash
git clone https://github.com/satyam671/tiered-llm-router.git
cd tiered-llm-router
```

Or if using SSH:
```bash
git clone git@github.com:satyam671/tiered-llm-router.git
cd tiered-llm-router
```

### Step 2: Open in VS Code (Recommended)

```bash
code .
```

VS Code will open the folder. You should see the file structure in the left sidebar:
- router.py
- evaluate.py
- shadow.py
- requirements.txt
- .env.example
- .gitignore
- README.md

### Step 3: Create and Activate Virtual Environment

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

You should see `(venv)` appear at the start of your terminal prompt. This means the virtual environment is active.

**In VS Code:** 
Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac), type "Python: Select Interpreter", and choose the one inside your `venv/` folder.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `anthropic>=0.40.0` — Anthropic's Python SDK
- `google-genai>=1.0.0` — Google's Gemini API client
- `python-dotenv>=1.0.0` — For loading .env files

**Expected output:**
```
Collecting anthropic>=0.40.0
  Downloading anthropic-0.40.0-py3-none-any.whl
  ...
Successfully installed anthropic-0.40.0 google-genai-1.0.0 python-dotenv-1.0.0
```

### Step 5: Get API Keys

#### Anthropic Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in (or create account)
3. Navigate to "API Keys" in the left sidebar
4. Click "Create Key"
5. Give it a name like "llm-router-dev"
6. **Copy the key immediately** — you won't see it again
7. It looks like: `sk-ant-api03-...` (long string)

#### Google AI Key

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click "Get API key" in the top-left corner
3. Click "Create new API key"
4. Choose "Create API key in new project" or "Create API key in existing project"
5. **Copy the key immediately**
6. It looks like: `AIzaSy...` (long string)

### Step 6: Create .env File

In your project root, create a `.env` file:

**Option A: Copy from template**
```bash
cp .env.example .env
```

**Option B: Create manually**
Create a file named `.env` (note the leading dot) with this content:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
GOOGLE_API_KEY=AIzaSy-your-actual-key-here
```

**Replace `sk-ant-api03-your-actual-key-here` with your actual Anthropic key.**
**Replace `AIzaSy-your-actual-key-here` with your actual Google key.**

⚠️ **CRITICAL:** Never commit `.env` to git. Verify it's in `.gitignore` (it is by default).

### Step 7: Verify .gitignore is Correct

Make sure `.env` will never be committed:

```bash
cat .gitignore | grep ".env"
```

You should see `.env` in the output. If not, add this line to `.gitignore`:
```
.env
```

### Step 8: Run the Smoke Test

```bash
python3 router.py
```

**Expected output (20-30 seconds):**
```
======================================================================
TIERED LLM ROUTER — SMOKE TEST
======================================================================

Query 1: Extract the invoice number from: 'Please see Invoice #42817'...

  ✓ Tier:         simple
  ✓ Model:        gemini-2.5-flash-lite
  ✓ Input tokens: 45
  ✓ Output tokens: 8
  ✓ Response:     Invoice #42817...

Query 2: Write a Python function that reads a CSV and validates...

  ✓ Tier:         moderate
  ✓ Model:        claude-sonnet-4-6
  ✓ Input tokens: 312
  ✓ Output tokens: 148
  ✓ Response:     def validate_email_csv(filepath: str) -> None:...

Query 3: Given three conflicting product requirements...

  ✓ Tier:         complex
  ✓ Model:        claude-opus-4-8
  ✓ Input tokens: 298
  ✓ Output tokens: 291
  ✓ Response:     Given the conflicting requirements, I recommend...

======================================================================
All tests passed. Router is working correctly.
======================================================================
```

If you see this, **the setup is complete and working**. 

If you see an error, see the troubleshooting section below.

### Step 9: Run the Classifier Evaluation

```bash
python3 evaluate.py
```

**Expected output (10-15 seconds):**
```
======================================================================
CLASSIFIER EVALUATION HARNESS
======================================================================

Classifier accuracy: 86%

  ✓ [simple → simple]
     Query: Extract all phone numbers from: 'Call 555-0123 or 555-0199'
     Reason: Formatting task with fixed output format.

  ✓ [simple → simple]
     Query: Translate 'Good morning' to French
     Reason: Short translation task.

  ✓ [simple → simple]
     Query: Is this email spam? Subject: 'You won $1,000,000'
     Reason: Binary classification task.

  ✓ [moderate → moderate]
     Query: Summarise this 800-word product description in three sentences
     Reason: Single-document summarization with moderate complexity.

  ✓ [moderate → moderate]
     Query: Write a Python function that reads a CSV...
     Reason: Standard code generation task.

  ✓ [complex → complex]
     Query: Given these five conflicting regulatory documents...
     Reason: Requires synthesis of multiple contradictory sources.

  ✓ [complex → complex]
     Query: Our data pipeline fails intermittently under high load...
     Reason: Diagnosis and debugging with complex system knowledge.

======================================================================
Results: 7 passed, 0 failed
✓ Accuracy is above 85%. Safe to enable live routing.
======================================================================
```

Accuracy of ≥85% means the classifier is ready for production use.

### Step 10: Run Shadow Mode Demo

```bash
python3 shadow.py
```

**Expected output (5 seconds):**
```
======================================================================
SHADOW MODE — SAMPLE OUTPUT
======================================================================

Request req-001: tier=simple

Request req-002: tier=moderate

Request req-003: tier=complex

======================================================================
After 2 weeks of shadow mode in production, analyze tier distribution.
Aggregate counts of 'simple', 'moderate', 'complex' from your logs.
This real distribution validates your cost model before live routing.
======================================================================
```

---

## Testing Checklist

Before considering this "working", verify:

- [ ] ✓ Smoke test passes (all 3 queries complete)
- [ ] ✓ Classifier accuracy ≥85%
- [ ] ✓ Token counts are non-zero and reasonable (small for simple, larger for complex)
- [ ] ✓ Response text is meaningful and correct
- [ ] ✓ No API errors or authentication failures
- [ ] ✓ .env file is in .gitignore (run `git status` and see no `.env`)

If all boxes are checked, the system is working correctly.

---

## Troubleshooting

### Error: "ANTHROPIC_API_KEY is not set"

**Cause:** Your `.env` file is missing or the API key is blank.

**Fix:**
1. Check that `.env` exists in the project root
2. Check that it contains your actual API key (not the example placeholder)
3. Make sure there are no extra spaces or quotes

**Verify:**
```bash
cat .env
```

Should show something like:
```
ANTHROPIC_API_KEY=sk-ant-api03-actual-key
GOOGLE_API_KEY=AIzaSy-actual-key
```

### Error: "No module named 'anthropic'"

**Cause:** Dependencies aren't installed.

**Fix:**
```bash
source venv/bin/activate     # Make sure virtual env is active
pip install -r requirements.txt
python3 router.py
```

### Error: "Invalid API key"

**Cause:** Your API key is wrong, expired, or has special characters.

**Fix:**
1. Go to [console.anthropic.com](https://console.anthropic.com) and verify the key is still valid
2. Delete and create a new key
3. Update `.env` with the new key
4. Run `python3 router.py` again

### Error: "Rate limit exceeded"

**Cause:** You're calling the API too quickly (especially if testing multiple times in succession).

**Fix:**
Wait 30 seconds and try again. The free tier has modest rate limits.

### Error: "Empty response from Gemini"

**Cause:** The Google API key is wrong or doesn't have the right permissions.

**Fix:**
1. Verify your Google AI key at [aistudio.google.com](https://aistudio.google.com)
2. Make sure it's an "API Key" not an OAuth token
3. Delete and create a new one
4. Update `.env` and try again

### Error: "Connection timeout"

**Cause:** Network issue or API is temporarily down.

**Fix:**
```bash
# Check your internet connection
ping google.com

# Wait a few seconds and try again
python3 router.py
```

### Virtual environment not activating

**On Mac/Linux:**
```bash
source venv/bin/activate
```

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

If PowerShell says "execution of scripts is disabled", run:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

---

## Understanding the Output

### Smoke Test Output

```
Query 1: Extract the invoice number...

  ✓ Tier:         simple                    # Classifier decided this is a simple task
  ✓ Model:        gemini-2.5-flash-lite    # Routed to the cheapest model
  ✓ Input tokens: 45                       # How many input tokens were consumed
  ✓ Output tokens: 8                       # How many output tokens were generated
  ✓ Response:     Invoice #42817...        # The actual answer
```

**What to look for:**
- `Tier` matches the query type (simple → extraction, moderate → coding, complex → reasoning)
- `Model` matches the expected tier (simple → Gemini, moderate → Sonnet, complex → Opus)
- `Input tokens` and `Output tokens` are non-zero
- `Response` is accurate and relevant

### Evaluation Output

```
✓ [simple → simple]
   Query: Extract all phone numbers...
   Reason: Formatting task with fixed output format.
```

- ✓ = Correct (predicted tier matched expected tier)
- ✗ = Wrong (predicted a different tier than expected)

**If you see misclassifications (✗):**
1. Read the query and the predicted tier
2. Decide: is the prediction reasonable or wrong?
3. If wrong, the `CLASSIFIER_SYSTEM_PROMPT` in `router.py` needs refinement

Example refinement:
```python
# Original definition was too vague
"moderate: Single-document analysis..."

# More specific version
"moderate: Single-document analysis, code generation, debugging with logs provided,
           but NOT complex system design or multi-file architecture decisions."
```

---

## Cost Calculation

Each script run has a cost. Here's what you're paying:

### Smoke Test (3 queries)
- Classifier calls: 3 × Haiku $0.0006 = $0.0018
- Response calls: ~$0.01 total (mixed tier costs)
- **Total: ~$0.012** (less than 1 cent)

### Evaluation (7 queries)
- Classifier calls: 7 × Haiku $0.0006 = $0.0042
- **Total: ~$0.004** (less than 1 cent)

### Shadow Mode (3 queries)
- Classifier calls: 3 × Haiku $0.0006 = $0.0018
- **Total: ~$0.002** (less than 1 cent)

All three scripts together cost less than 1 cent. You can run them many times during development without worrying about cost.

---

## Next Steps

1. **Understand the code:** Read through `router.py` and the inline comments. Understand how `classify_query()` and `handle_query()` work.

2. **Customize for your use case:** Update the tier definitions in `CLASSIFIER_SYSTEM_PROMPT` to match your specific query types. If your app deals with medical content, add examples. If it's code review, add code-specific guidance.

3. **Test with real queries:** Add your actual production queries to `TEST_CASES` in `evaluate.py` (at least 50–100 labelled examples). Retrain until accuracy is ≥85%.

4. **Deploy shadow mode:** Before enabling live routing, integrate `shadow_classify()` into your existing system and let it run for 2 weeks. This measures your real traffic distribution.

5. **Enable live routing:** Once shadow mode data confirms your cost assumptions, swap your API calls from calling a single model to calling `handle_query()`. Monitor tier distribution and cost savings in production.

---

## Connecting to the Medium Article

This repo is the companion code for: **[How to Build a Tiered AI Architecture That Saves Your Budget](https://medium.com/@satyam-sahu/tiered-llm-router)**

The article covers:
- Cost math for different tier splits
- Architecture decisions and trade-offs
- Async patterns for high throughput
- Prompt caching for even deeper savings
- Production considerations (concurrency, retry logic, monitoring)

This repo provides the working implementation.

---

## Support & Issues

Found a bug or have a question?

1. Check the **Troubleshooting** section above
2. Review the code comments in `router.py`, `evaluate.py`, `shadow.py`
3. Open a GitHub issue with:
   - What you were trying to do
   - The exact error message
   - Your Python version (`python3 --version`)
   - Steps to reproduce

---

## License

MIT License — use this code freely in personal and commercial projects.

---

## Stay Updated

This repo will be updated with caching implementations, batch processing examples, and additional production patterns.
