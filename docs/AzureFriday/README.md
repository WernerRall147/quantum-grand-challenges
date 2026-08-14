# Azure Friday - Showcase Guidance

Runbook for presenting the **Quantum Advantage Evaluator** on Azure Friday (or any live
demo). Everything here is grounded in the real, deployed system.

**Last verified working:** 2026-08-14 - all five demo prompts returned the correct
verdict against the live API, model `gpt-5.6-terra-2026-07-09` via the model router,
6-7 references and ~2,000-character explanations. Latency 34.9-72.1s, typically ~46s.
See section 5 for the verified table.

**Recording:** virtual. Options offered were Wed 2 Sep 2:00 PM PT, Thu 3 Sep 12:00 PM PT,
Thu 3 Sep 2:00 PM PT. Format is 12-16 minutes total, of which **6-8 minutes is live demo**
and the rest is conversational Q&A with Scott. A **storyboard must be submitted in
advance**, and there is a 30-minute prep call about a week before. Post-production takes
about two weeks; episodes publish Thursdays at 5:00 PM PT.

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

## 2. Run of show (12-16 min total, 6-8 min demo)

The demo is the middle of the episode, not the whole of it. Budget 6-8 minutes and let
Scott carry the rest.

### Demo beat sheet

A call takes about 46 seconds and can reach 72. That is not dead air unless you let it
be: each beat below has something to say while the request is in flight.

| Beat | Time | On screen | What you say while it runs |
|---|---|---|---|
| 1. The yes | 0:00-1:30 | Type the FeMoco prompt, hit Evaluate | Walk through Troyer's 5 filters. Land on `QUANTUM_ADVANTAGE`, 0.9 confidence, QPE, with citations. |
| 2. The no | 1:30-3:00 | Portfolio optimisation, 500 assets | Explain why a quadratic speedup dies under error-correction overhead. Land on `HPC_PREFERRED`. This is the memorable beat. |
| 3. The payoff | 3:00-4:30 | Generated **Q#** and a **Bicep** template | It does not just judge, it hands you the workspace. |
| 4. The platform | 4:30-6:00 | Architecture | Container Apps, **managed identity** (no keys), AI Search, model router, GitHub Actions deploy. |

If you are short on time, cut beat 3 before beat 2. The agent declining quantum is the
differentiator; code generation is table stakes.

### Latency

Not a cold start. `minReplicas` is 1, so the app never scales to zero and that time is
model inference. Pre-warming will not shorten it. Either narrate over it as above, or
pre-run beat 2 and show the stored result while you talk.

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
# Takes ~46s. Anything past ~90s is worth investigating before you go live.
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

**Fix A - instant, reversible fallback (do this if you are minutes from recording):**
Switches the agent path to plain chat-completions on the model router (proven to work).
```powershell
az containerapp update -n qgc-eval-api -g qgc-evaluator --set-env-vars QGC_USE_AGENT=0
```

**Fix B - proper fix (restores the full agent path):** re-grant the agents data-plane
role, wait ~5-15 min for propagation, then flip back to the agent path.
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
  only, QEC overhead), 9 active. The agent applies **Troyer's 5 utility-scale filters**
  and **DiVincenzo** hardware-readiness criteria - it is designed to *not* over-claim.
- **Architecture:** agent `quantum-advantage-orchestrator` on Foundry project
  `qgc-eval-proj` (account `admin-mo1q7owo-eastus2`, East US 2), model router, tools
  (Code Interpreter + Microsoft Learn MCP); API on Container App `qgc-eval-api`
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

- [ ] Reply to Jazz with the chosen recording slot (slots are first-come)
- [ ] **Submit the storyboard** via the emailed form. This is a hard deliverable and is
      due in advance, not on the day
- [ ] Attend the 30-minute prep call (~1 week prior)
- [ ] Decide beat 2: live call, or pre-run and narrate
- [ ] Full timed dry run on the real environment, including one deliberate "no"
- [ ] Record a fallback video of each prompt in section 5

On the day:

- [ ] No open GitHub issue labelled `uptime`
- [ ] Run the section 4 smoke test ~15 minutes before
- [ ] Re-run all five prompts in section 5 and confirm the verdicts match
- [ ] Site loads and does not show DEMO MODE
