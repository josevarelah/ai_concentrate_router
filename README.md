# AI Model Router

**Intelligent prompt routing to LLM models via Concentrate API**

Built a full-stack production system that classifies user prompts and routes them to optimal models based on task complexity and user preferences (cost, quality, or latency).

---

## What Was Built

### Backend (FastAPI + Python)
- **Intelligent Classification**: Uses cheap model (gemini-2.5-flash) to analyze prompts → determines task type (coding/reasoning/summarization/creative) and complexity (low/medium/high)
- **Rule-Based Routing**: Maps classification + user preference to optimal model across 3 tiers (premium/standard/economy)
- **Unified API Integration**: Single Concentrate client works across OpenAI, Anthropic, Google, IBM, xAI models
- **Production Patterns**: Async throughout, proper error handling, type safety (Pydantic), CORS, graceful fallbacks


### Frontend (React + TypeScript)
- **Clean UI**: Textarea for prompts, preference selector, submit with loading states
- **Transparent Results**: Shows AI response, model used, and routing explanation
- **Type-Safe**: Full TypeScript with interfaces matching backend contracts
- **Minimal Dependencies**: React, Vite
### Architecture
```
User Input → Classification (cheap model) → Routing (rules) → Completion (selected model) → Response + metadata
```

---

## Key Design Tradeoffs

### 1. **LLM-Based Classification vs Heuristics**
**Chose:** LLM-based classification using gemini-2.5-flash

**Pros:**
- Much more accurate task/complexity detection
- Handles nuance and edge cases naturally
- No regex patterns to maintain

**Cons:**
- Adds latency (extra API call)
- Costs $0.0003 per classification
- Could fail and need fallback

**Verdict:** Better routing quality outweighs small latency/cost overhead.

---

### 2. **Rule-Based Routing vs ML Model**
**Chose:** Hardcoded rules (complexity → tier, task overrides, preference selection)

**Pros:**
- Completely predictable and debuggable
- No training data or retraining needed
- Transparency (can explain every decision)
- Zero inference overhead

**Cons:**
- Can't learn from usage patterns
- Manual updates required for new models
- Might miss optimal routes that ML would find

**Verdict:** Rules are simple, clear, and performant. Can add ML later if needed.

---

### 3. **Single Tier vs User-Specified Model**
**Chose:** Automatic tier selection

**Pros:**
- Simple UX - users just pick cost/quality/latency
- Backend controls model strategy
- Can optimize routing without frontend changes

**Cons:**
- Users can't force specific models
- Less control for advanced use cases

**Verdict:** Good default. Could add "advanced mode" later for manual model selection.

---

### 4. **Cost Optimization**
**Current:** Economy tier uses ibm-granite-micro ($0.017/$0.11) for cost preference

**Tradeoff:** 
- Saves 99% vs premium models
- But granite-micro may have lower quality than gpt-4o-mini
- Risk: users dissatisfied with "cheap" outputs

**Alternative considered:** Always use at least gpt-4o-mini for acceptable baseline quality

**Verdict:** Users explicitly chose "cost" preference, so ultra-cheap is appropriate. Those wanting quality can select that preference.

---

## Suggestions for Concentrate AI

### API Improvements

**1. Standardize Response Format**
- **Issue:** Different models return slightly different JSON structures
- **Impact:** Requires complex parsing logic with fallbacks
- **Suggestion:** Enforce consistent `{"output": [{"content": [{"type": "text", "text": "..."}]}]}` across all models

**2. Batch Classification**
- **Need:** Classify multiple prompts in one request
- **Use case:** When user enters multiple questions or comparing outputs
- **Suggestion:** Support array input:
  ```json
  {
    "prompts": ["prompt1", "prompt2", "prompt3"],
    "model": "gemini-2.5-flash"
  }
  ```
- **Benefit:** Reduce latency and cost for bulk operations

**3. Cost Estimation Before Execution**
- **Need:** Show users estimated cost before calling expensive models
- **Suggestion:** Add `estimate=true` parameter that returns token count + cost projection without executing
- **Benefit:** Users can make informed cost/quality decisions


## Running the Project

**Backend:**
```bash
cd backend
pip install -r requirements.txt
echo "CONCENTRATE_API_KEY=sk-cn-your-key" > .env
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`

---

## Tech Stack Summary

- **Backend:** FastAPI, Python 3.11+, Pydantic, httpx, asyncio
- **Frontend:** React 18, TypeScript, Vite
- **API:** Concentrate AI (unified LLM access)
