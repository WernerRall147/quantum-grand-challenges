# Azure Friday - Showcase Guidance

Runbook for presenting the **Quantum Advantage Evaluator** on Azure Friday (or any live
demo). Everything here is grounded in the real, deployed system.

**Last verified working:** 2026-08-14 - all five demo prompts returned the correct
verdict against the live API, model `gpt-5.6-terra-2026-07-09` via the model router,
5-7 references and ~2,000-character explanations.

**Latency, measured from the scheduled probe:** median 51.5s, mean 51.1s, min 36.0s,
max 78.5s. A direct run of all five prompts on 2026-08-18 saw 42.8s to 90.1s, so treat
90s as the number to rehearse against, not 78s. Plan the narration around ~50s and be
ready for 90.
See section 5 for the verified verdict table.

**Recording:** virtual, via **StreamYard**. Target length is **10-12 minutes** total, of
which **6-8 minutes is live demo**, the rest conversational Q&A with Scott. The
invitation email says 12-16 minutes and the production deck says 10-12; build to the
shorter number. A **storyboard is due one week before the recording** (draft in
[storyboard.md](storyboard.md)), and there is a 30-minute prep call about a week before.
Show notes are due 1-2 business days after recording. Post-production takes about two
weeks; episodes publish Thursdays at 5:00 PM PT.

---

## 1. The pitch (episode description)

> **The AI agent that talks you *out* of quantum computing - building an honest advisor on Azure AI Foundry.**
>
> It started with one ChatGPT question in August 2025: *"What are the 20 hardest problems
> in science, and could Q# help solve them?"* A year and ~300 commits later, that
> brainstorm is a live, honest AI advisor running on Azure - and I'll show exactly how
> it's built.
>
> Everyone's asking "should this run on a quantum computer?" and most answers are hype.
> This agent gives an honest verdict - quantum, AI/ML, or Azure HPC - then generates the
> code and infrastructure to actually run it.

Full pitch + shorter variant live in the chat thread; this folder is the *operational*
runbook.

---

## 2. Run of show (10-12 min total, 6-8 min demo)

The demo is the middle of the episode, not the whole of it. Budget 6-8 minutes and let
Scott carry the rest. Full beat sheet and submission draft in
[storyboard.md](storyboard.md).

### Demo beat sheet

A call takes about 51s and has been measured at 90s. Azure Friday's own prep guidance is
to have a completed item to transition to rather than watch something finish, so **run
beat 1 live and pre-load beat 2 in a second tab**. One live call proves it is real; two
spends up to two and a half minutes of a six minute demo on a spinner.

| Beat | Time | On screen | Notes |
|---|---|---|---|
| 1. The yes | 0:00-2:00 | Type the FeMoco prompt, hit Evaluate | **Live.** Fill the wait by walking Troyer's six filters, which the audience needs anyway. Lands on `QUANTUM_ADVANTAGE`, 0.9, QPE, with citations. |
| 2. The no | 2:00-3:30 | Portfolio optimisation, 500 assets | **Pre-loaded.** Say plainly you ran it earlier. Why a quadratic speedup dies under QEC overhead. Lands on `HPC_PREFERRED`. The memorable beat. |
| 3. The payoff | 3:30-5:00 | Generated **Q#** and a **Bicep** template | It does not just judge, it hands you the workspace. |
| 4. The platform | 5:00-6:30 | Architecture, one slide | Container Apps, **managed identity** (no keys), AI Search, model router, GitHub Actions. |

If you are short on time, cut beat 3 before beat 2. The agent declining quantum is the
differentiator; code generation is table stakes.

### Latency

Not a cold start. `minReplicas` is 1, so the app never scales to zero and that time is
model inference. Pre-warming will not shorten it, which is why beat 2 is pre-baked.

Figures come from the scheduled probe, which has run every 30 minutes since 2026-08-14
with no failures. Re-read them before recording rather than trusting this line.

---

## 3. Azure services to name-check

Azure AI Foundry (agents, model router, Code Interpreter + MCP tools) - Azure Container
Apps - Azure AI Search - Azure Functions (timer trigger) - Managed Identity -
Azure Quantum (resource estimation) - GitHub Actions.

> Cosmos DB was retired in #156. The knowledge base is now served from files committed
> to the repo, with AI Search for retrieval. Do not name-check Cosmos DB on air.

---

## 4. Pre-show smoke test (run ~15 min before recording)

```powershell
$base = "https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io"
# 1) health - expect: status=ok
Invoke-RestMethod "$base/"
# 2) core demo - expect: verdict + model_used + references populated
# Median 51.5s, max seen 90.1s. Past ~120s is worth investigating before you go live.
Invoke-RestMethod "$base/api/evaluate" -Method POST -ContentType application/json `
  -Body '{"problem":"I need to find the ground state energy of the FeMoco nitrogenase cofactor for catalyst design","generate_code":false}'
```

Also open the site and click through one evaluation:
**https://wernerrall147.github.io/quantum-grand-challenges/**

If the site shows **DEMO MODE**, the backend call failed - see section 6.

A scheduled probe already does this every 30 minutes
(`.github/workflows/uptime-evaluator-api.yml`). It posts the FeMoco prompt, asserts the
verdict is `QUANTUM_ADVANTAGE`, records latency, and opens a GitHub issue labelled
`uptime` if it fails. Check that no such issue is open before you record.

---

## 5. Sample prompts that demo well

All five verified against the live API on 2026-08-14. Use these exact wordings; the
router reads the problem text, so paraphrasing can change the answer.

| Prompt | Verdict | Platform | Why it's a good demo |
|---|---|---|---|
| "I need to find the ground state energy of the FeMoco nitrogenase cofactor for catalyst design" | `QUANTUM_ADVANTAGE` | QUANTUM | Troyer's flagship chemistry example; rich, cited answer. |
| "Factor a 2048-bit RSA integer to test post-quantum readiness" | `QUANTUM_ADVANTAGE` | QUANTUM | Shor - the clean utility case, and structural rather than naturally quantum. |
| "Optimize a portfolio of 500 assets using mean-variance optimisation" | `HPC_PREFERRED` | HPC | The agent *declining* quantum. The honesty angle. |
| "Train an image classifier on 10 million medical photos" | `AI_ML_PREFERRED` | AI_ML | Third verdict class on screen. |
| "Simulate turbulent airflow over an aircraft wing using CFD" | `HPC_PREFERRED` | HPC | Spare, in case a prompt misbehaves. |

The portfolio and AI prompts are the money shot: the agent talks you *out* of quantum.

> These two were wrong until #159. The router was accepting any top retrieval hit as
> proof of quantum advantage, so portfolio optimisation matched "Probabilistic Sampling
> (Quantum Supremacy)" and came back `QUANTUM_ADVANTAGE` at 0.9 confidence. **Re-verify
> all five after any change to the router, the algorithm zoo, or the search index.**

---

## 6. If the demo breaks (known risk + fast fixes)

**Known risk:** the Container App's managed identity has had its data-plane role silently
stripped once (a governance/policy job in the subscription may recur). Symptom: the site
shows **DEMO MODE**; `POST /api/evaluate` returns **500** with
`PermissionDeniedError: 403`.

Set subscription context first:
```powershell
az account set --subscription 82cd08af-0dac-4fc5-8a3a-f2ab9e4679c3
```

**Fix A - already the default since 2026-08-19.** The live config is `QGC_USE_AGENT=0`,
plain chat-completions on the model router, chosen on measured latency (~28s median
against ~52s for the agent path). A 403 on the agents data plane therefore no longer
takes the demo down. Confirm the setting is still in place:
```powershell
az containerapp update -n qgc-eval-api -g qgc-evaluator --set-env-vars QGC_USE_AGENT=0
```

**Fix B - only if you deliberately want the agent path back** (Code Interpreter and the
Learn MCP tool): re-grant the agents data-plane role, wait ~5-15 min for propagation,
then flip. Expect responses to take roughly twice as long.
```powershell
az role assignment create `
  --assignee-object-id ac6b9368-d212-45bf-8ce7-272ccc2799f3 `
  --assignee-principal-type ServicePrincipal `
  --role "Cognitive Services User" `
  --scope "/subscriptions/82cd08af-0dac-4fc5-8a3a-f2ab9e4679c3/resourceGroups/qgc-evaluator/providers/Microsoft.CognitiveServices/accounts/admin-mo1q7owo-eastus2"
# after propagation:
az containerapp update -n qgc-eval-api -g qgc-evaluator --set-env-vars QGC_USE_AGENT=1
```

**Last-resort backup:** pre-record a clean run of each sample prompt, and keep a local
run ready (`python agents/orchestrator/evaluate.py "your problem"`) so the demo survives
a total cloud outage.

### Other failure modes seen in production

| Symptom | Cause | Action |
|---|---|---|
| HTTP 500, `ModuleNotFoundError` in logs | an unpinned dependency drifted on rebuild | `agents/api/requirements.txt` is now pinned exactly. Redeploy a known-good image tag. |
| A wall of raw JSON where the explanation should be | the model fenced its answer and the parse fell through | Fixed in #162. If it recurs, the verdict is still correct; only the prose is affected. |
| A confident `QUANTUM_ADVANTAGE` on an obviously classical problem | the router trusted an irrelevant retrieval hit | Fixed in #159. Re-run all five prompts in section 5. |

> A recurring lesson: a green status is not evidence. The ingester reported success for
> 17 days while every write was rejected, the deploy workflow reported success while
> `/api/evaluate` returned 500, and the uptime probe itself was registered as active
> while being unparseable YAML. Confirm the actual response, not the status.

---

## 7. Key facts and talking points

- **Origin:** began as a ChatGPT brainstorm on **2025-08-14** ("top 20 hardest problems,
  can Q# help?"); first commit the same day. ~300 commits since. See
  [../planning/original-chatgpt-conversation.md](../planning/original-chatgpt-conversation.md).
- **Honesty angle:** 20 problems implemented; **11 honestly downgraded** (I/O, quadratic-
  only, QEC overhead), 9 active. The agent applies **6 utility-scale filters**
  and **DiVincenzo** hardware-readiness criteria - it is designed to *not* over-claim.
- **Architecture:** the verdict comes from a deterministic router in code, not from the
  model; the model writes the explanation and citations, and every citation is resolved
  before it is shown. Requests run on Foundry's model router via chat-completions.
  The Foundry agent `quantum-advantage-orchestrator` on project `qgc-eval-proj`
  (account `admin-mo1q7owo-eastus2`, East US 2) with Code Interpreter and the Microsoft
  Learn MCP stays provisioned but is off by default, on measured latency. API on
  Container App `qgc-eval-api`
  (RG `qgc-evaluator`, `minReplicas` 1 so it never scales to zero); knowledge base served
  from files committed to the repo, with AI Search `qgcsearcheval` for retrieval; daily
  arXiv ingester on Azure Functions writing to AI Search.
- **The verdict is not the model's.** A deterministic router owns verdict, confidence and
  platform; the model writes the explanation and stress-tests the decision. If it
  disagrees, that is recorded in `model_dissent` rather than changing the answer. This is
  worth saying on air: it is why the same question gives the same answer twice.
- **Published:** methodology paper, DOI `10.5281/zenodo.19222021`.

---

## 8. Resources

- Live site: https://wernerrall147.github.io/quantum-grand-challenges/
- API base: https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io
- Repo: https://github.com/WernerRall147/quantum-grand-challenges
- API endpoints: `GET /` (health), `POST /api/evaluate`, `POST /api/generate-code`,
  `POST /api/generate-bicep`, `GET /api/algorithms`, `GET /api/reference-problems`

> Note: this runbook references resource names and role names only - no secrets. Keep
> keys in Key Vault / managed identity, never in this doc.

---

## 9. Pre-recording checklist

Ahead of the day:

- [x] Reply to Jazz with the chosen recording slot
- [ ] **Submit the storyboard.** Draft ready in [storyboard.md](storyboard.md); fill in
      the booked slot and paste into the form when the link arrives. **Due one week
      before the recording.**
- [ ] Attend the 30-minute prep call (~1 week prior)
- [ ] Full timed dry run on the real environment, including one deliberate "no"
- [ ] Pre-run beat 2 and leave it open in a second tab
- [ ] Record a fallback video of each prompt in section 5

Machine setup, the day before (from the production prep doc):

- [ ] Display 1920x1080, solid colour background
- [ ] Default browser opens to `about:blank`
- [ ] Hide the date in the taskbar, Quiet Hours on
- [ ] Sign out of Outlook, Teams and any messaging client
- [ ] Nothing confidential on the desktop or in open tabs
- [ ] Browser zoom set so the verdict and filters are legible at 1080p

On the day:

- [ ] No open GitHub issue labelled `uptime`
- [ ] Run the section 4 smoke test ~15 minutes before
- [ ] Re-run all five prompts in section 5 and confirm the verdicts match
- [ ] Site loads and does not show DEMO MODE

After the recording:

- [ ] Submit show notes within 1-2 business days
