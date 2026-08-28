# Azure Friday - Showcase Guidance

Runbook for presenting the **Quantum Advantage Evaluator** on Azure Friday (or any live
demo). Everything here is grounded in the real, deployed system.

**Last verified working:** 2026-08-26 - all five demo prompts returned the correct
verdict against the live API, model `gpt-5.6-luna-2026-07-09` via the model router,
5-7 references, `used_agent: false`. Code generation verified the same day: 2,981 chars
of Q#, compiled, 4 clean Pareto rows.

**Latency, three full runs of all five prompts on 2026-08-24 (15 calls):** median 38.0s,
mean 38.0s, min 28.9s, max 58.9s. Rehearse against **60s**.

> Three runs, not one. The per-run medians were 33.2s, 39.2s and 34.1s, so the middle of
> the distribution is stable and 38s is a fair number to plan narration around. The worst
> single call is what moved: 46.4s after ten samples, 58.9s after fifteen. The median is
> what you plan for; the max is what catches you out live, and it needs more samples to
> find. Quoting the first five calls alone would have given 33.2s and a false sense of it.

> Earlier revisions of this file quoted a 51.5s median and told you to rehearse
> against 90s. Those were measured on the **Foundry agent** path. Production moved to
> chat-completions on 2026-08-19 (`QGC_USE_AGENT=0`), which is roughly 35% faster, so
> the old figures overstated the gap you need to fill by about half.

See section 5 for the verified verdict table.

**Recording:** virtual, via **StreamYard**. Target length is **11-13 minutes** total, of
which **6-9 minutes is live demo**, the rest conversational Q&A with Scott. Chris's prep
mail is the authoritative number and the most recent; the invitation email's 12-16 and an
earlier 10-12 in this file both predate it. A **storyboard is due one week before the recording** (draft in
[storyboard.md](storyboard.md)), and there is a 30-minute prep call about a week before.
Show notes are due 1-2 business days after recording. Post-production takes about two
weeks; episodes publish Thursdays at 5:00 PM PT.

---

## 1. The pitch (episode description)

> **The AI agent that talks you *out* of quantum computing - building an honest advisor on Azure AI Foundry.**
>
> It started with one ChatGPT question in August 2025: *"What are the 20 hardest problems
> in science, and could Q# help solve them?"* A year and ~380 commits later, that
> brainstorm is a live, honest AI advisor running on Azure - and I'll show exactly how
> it's built.
>
> Everyone's asking "should this run on a quantum computer?" and most answers are hype.
> This agent gives an honest verdict - quantum, AI/ML, or Azure HPC - then generates the
> code and infrastructure to actually run it.

Full pitch + shorter variant live in the chat thread; this folder is the *operational*
runbook.

---

## 2. Run of show (11-13 min total, 6-9 min demo)

**The beat sheet lives in [script.md](script.md).** It used to be duplicated here, and the
two copies drifted into describing different demos - this file opened live with FeMoco,
the storyboard opened live with portfolio optimisation. One source now.

The short version: **portfolio optimisation runs live** because it is the shortest call
and it delivers the episode's title. FeMoco and code generation are **pre-executed**
because that path is 58-79s. Bicep is cut - Chris asked for no feature parade.

> **Q# generation was broken in production until 2026-08-26** and nothing reported it. The
> image did not contain `tooling/estimator_config.py`, which `generate.py` imports, so
> generation raised, `/api/evaluate` caught the exception and returned `qsharp_code: ""`,
> and the site renders that field only when it is non-empty. HTTP 200 throughout. Six
> stacked faults in total; the last was the estimator resolving `Main()` when the callable
> is `Main.Main()`. Generated Q# is now compiled inside the request and retried with the
> compiler error on failure, and `verify_demo_prompts.py` covers the whole path.

### Latency

Not a cold start. `minReplicas` is 1, so the app never scales to zero and that time is
model inference. Pre-warming will not shorten it, which is why beat 2 is pre-baked.

Figures come from the scheduled probe, which has run every 30 minutes since 2026-08-14
with no failures. Re-read them before recording rather than trusting this line.

---

## 3. Azure services to name-check

Azure AI Foundry (**model router**) - Azure Container Apps - Azure AI Search - Azure
Functions (timer trigger) - Managed Identity - Azure Quantum (resource estimation) -
GitHub Actions.

> Do not name-check Foundry **agents**, Code Interpreter or the Learn MCP tool. All three
> exist on `qgc-eval-proj` but `QGC_USE_AGENT=0`, so none of them are in the request path.
> If asked, the honest line is "we built it, measured it at 1.8x the latency for no
> quality gain, and left it off".

> Cosmos DB was retired in #156. The knowledge base is now served from files committed
> to the repo, with AI Search for retrieval. Do not name-check Cosmos DB on air.

---

## 4. Pre-show smoke test (run ~15 min before recording)

One command. It reads the five prompts straight out of section 5 below, so it checks the
exact text you will type on air rather than a copy that can drift:

```powershell
python tooling/verify_demo_prompts.py
```

Exit code 0 means every prompt returned its expected verdict. Non-zero means **do not
record against it** - the output names which prompt drifted. Takes about three minutes.
Median 38.0s per call, max seen 58.9s; past ~90s is worth investigating before you go live.

> **This now covers code generation.** It used to post `generate_code: false` only, which
> is exactly how Q# generation stayed dead without anyone noticing - a totally broken
> generator passed the smoke test. The tool now also runs the FeMoco prompt with code
> generation on and fails on empty Q#, a compile error, a failed estimate or any errored
> Pareto row. Pass `--no-codegen` to skip it if you only want the verdicts.

If you would rather poke it by hand:

```powershell
$base = "https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io"
Invoke-RestMethod "$base/"   # expect: status=ok
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

All five verified against the live API on 2026-08-24, on the chat-completions path that
production actually runs. Use these exact wordings; the
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
> all five after any change to the router, the algorithm zoo, or the search index** -
> `python tooling/verify_demo_prompts.py`. That instruction was here before and went
> unactioned through a whole model-path change, which is why it is now one command.
>
> The tool parses this table. If you edit it, keep the shape
> `| "prompt" | ` + "`VERDICT`" + ` | ... |` or the tool will fail rather than quietly check nothing.

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
| *Generate code* ticked, verdict fine, no code block appears | the generator raised and the API returned an empty string | The site now shows a red failure panel with the error rather than rendering nothing. Check the panel text; a `ModuleNotFoundError` means a file the generator needs is missing from the image - see `agents/tests/test_container_contents.py`. |

> A recurring lesson: a green status is not evidence. The ingester reported success for
> 17 days while every write was rejected, the deploy workflow reported success while
> `/api/evaluate` returned 500, and the uptime probe itself was registered as active
> while being unparseable YAML. Confirm the actual response, not the status.

---

## 7. Key facts and talking points

- **Origin:** began as a ChatGPT brainstorm on **2025-08-14** ("top 20 hardest problems,
  can Q# help?"); first commit the same day. ~380 commits since. See
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
- **Published:** methodology paper, DOI `10.5281/zenodo.19222020`.

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
