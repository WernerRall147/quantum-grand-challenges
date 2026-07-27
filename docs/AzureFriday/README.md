# Azure Friday - Showcase Guidance

Runbook for presenting the **Quantum Advantage Evaluator** on Azure Friday (or any live
demo). Everything here is grounded in the real, deployed system.

**Last verified working:** 2026-07-22 - `POST /api/evaluate` returned
`QUANTUM_ADVANTAGE`, model `gpt-5.4-2026-03-05`, 6 references, ~2,100-char explanation
(full Azure AI Foundry agent path healthy).

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

## 2. Run of show (~15 minutes, demo-first)

| Time | Segment | What the viewer sees |
|---|---|---|
| 0:00 | **Hook** | "Should this be quantum?" Type a real problem, get an honest verdict with citations. |
| 3:00 | **The agent** | Azure AI Foundry agent + **model router** auto-picking a model (gpt-5.4, grok, etc.) live. |
| 6:00 | **Grounding** | RAG over Cosmos DB + AI Search; the daily **Azure Functions** arXiv ingester keeps it fresh. |
| 9:00 | **The platform** | Azure Container Apps + **managed identity** (no keys) + GitHub Actions deploy. |
| 12:00 | **Payoff** | Generate **Q#** + a **Bicep** template for the right Azure workspace. |
| 14:00 | **Takeaway** | "This is how you build any grounded, tool-using Azure agent." |

---

## 3. Azure services to name-check

Azure AI Foundry (agents, model router, Code Interpreter + MCP tools) - Azure Container
Apps - Cosmos DB - Azure AI Search - Azure Functions (timer trigger) - Managed Identity -
Azure Quantum (resource estimation) - GitHub Actions.

---

## 4. Pre-show smoke test (run ~15 min before recording)

```powershell
$base = "https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io"
# 1) health - expect: status=ok
Invoke-RestMethod "$base/"
# 2) core demo - expect: verdict + model_used + references populated
Invoke-RestMethod "$base/api/evaluate" -Method POST -ContentType application/json `
  -Body '{"problem":"Simulate the FeMoco cofactor for nitrogen fixation","generate_code":false}'
```

Also open the site and click through one evaluation:
**https://wernerrall147.github.io/quantum-grand-challenges/**

If the site shows **DEMO MODE**, the backend call failed - see section 6.

---

## 5. Sample prompts that demo well

| Prompt | Expected verdict | Why it's a good demo |
|---|---|---|
| "Simulate the FeMoco cofactor for nitrogen fixation catalysis" | `QUANTUM_ADVANTAGE` | Troyer's flagship chemistry example; rich, cited answer. |
| "Factor a 2048-bit RSA integer" | `QUANTUM_ADVANTAGE` | Shor - the clean utility case. |
| "Optimize a portfolio of 500 assets (mean-variance)" | `HPC_PREFERRED` | Shows the agent *declining* quantum - the honesty angle. |
| "Train an image classifier on 10M photos" | `AI_ML_PREFERRED` | Shows all three verdict classes on screen. |

The portfolio/AI prompts are the money shot: the agent talks you *out* of quantum.

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
  (RG `qgc-evaluator`); RAG over Cosmos `qgccosmoseval` + AI Search `qgcsearcheval`;
  daily arXiv ingester on Azure Functions.
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
