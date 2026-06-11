"""Provision (create/update) the Quantum Advantage Evaluator as a Foundry agent.

This creates a *prompt agent* version in the Foundry project (model-router +
Tools) so the evaluator can use Foundry Agent Service tools. The agent's
instructions are the shared SYSTEM_PROMPT, so its behavior matches the direct
chat-completions path.

Why this exists
---------------
The live evaluator (agents/orchestrator/evaluate.py) calls the raw
chat-completions API, which has no concept of Tools. Foundry "Tools"
(FileSearch/RAG, Code Interpreter, MCP, Function, OpenAPI, ...) attach to an
*agent* that runs a model deployed in a project. model-router 2025-11-18
(already deployed on admin-mo1q7owo-eastus2 / eastus2) supports Foundry Agent
Service and every tool type, so the cost-optimized routing carries over.

Auth
----
Uses DefaultAzureCredential. In this repo the `az` CLI is logged in as the
qgc-agent-sp service principal, which has been granted "Azure AI Developer"
on the project and "Cognitive Services OpenAI User" on the account. CI can
instead set AZURE_CLIENT_ID / AZURE_CLIENT_SECRET / AZURE_TENANT_ID.

Usage
-----
    python tooling/provision_foundry_agent.py            # create/update agent
    python tooling/provision_foundry_agent.py --smoke    # + run one test eval
    python tooling/provision_foundry_agent.py --list     # list agent versions
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    CodeInterpreterTool,
    MCPTool,
)

from agents.orchestrator.instructions import SYSTEM_PROMPT

# --- Config (env-overridable) ------------------------------------------------
PROJECT_ENDPOINT = os.environ.get(
    "QGC_PROJECT_ENDPOINT",
    "https://admin-mo1q7owo-eastus2.services.ai.azure.com/api/projects/qgc-eval-proj",
)
MODEL_DEPLOYMENT = os.environ.get("QGC_ROUTER_DEPLOYMENT", "model-router")
AGENT_NAME = os.environ.get("QGC_AGENT_NAME", "quantum-advantage-orchestrator")

# Microsoft Learn public MCP server: lets the agent fetch real
# learn.microsoft.com citations, which the SYSTEM_PROMPT explicitly asks for.
LEARN_MCP_URL = os.environ.get("QGC_LEARN_MCP_URL", "https://learn.microsoft.com/api/mcp")


def _build_tools():
    """Starter tool set. Both are zero-infra and reliable.

    - Code Interpreter: sandboxed Python for the quantitative reasoning this
      evaluator does (T-gate counts, qubit widths, crossover points).
    - MCP -> Microsoft Learn: real, current learn.microsoft.com references.

    RAG over the existing Azure AI Search KB (qgcsearcheval) is the natural
    next tool; it needs a project connection and is added via AzureAISearchTool.
    """
    return [
        CodeInterpreterTool(),
        MCPTool(
            server_label="microsoft_learn",
            server_url=LEARN_MCP_URL,
            require_approval="never",
        ),
    ]


def _client() -> AIProjectClient:
    return AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())


def create_or_update():
    project = _client()
    definition = PromptAgentDefinition(
        model=MODEL_DEPLOYMENT,
        instructions=SYSTEM_PROMPT,
        tools=_build_tools(),
    )
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=definition,
        description="Quantum Advantage Evaluator (model-router + Tools).",
    )
    version = getattr(agent, "version", None) or getattr(agent, "id", "?")
    print(f"OK agent='{AGENT_NAME}' version='{version}' model='{MODEL_DEPLOYMENT}'")
    print(f"   project={PROJECT_ENDPOINT}")
    print(f"   tools={[t.__class__.__name__ for t in _build_tools()]}")
    return agent


def list_versions():
    project = _client()
    print(f"Versions of agent '{AGENT_NAME}':")
    for v in project.agents.list_versions(agent_name=AGENT_NAME):
        print("  -", getattr(v, "version", v))


def smoke_test():
    """Send one evaluation through the agent and print the response text."""
    project = _client()
    client = project.get_openai_client()
    prompt = (
        "Evaluate this quantum computing problem: simulate the ground-state "
        "energy of the FeMoco nitrogenase cofactor for catalysis research. "
        "Respond with the JSON described in your instructions."
    )
    response = client.responses.create(
        input=prompt,
        extra_body={"agent_reference": {"type": "agent_reference", "name": AGENT_NAME}},
    )
    text = getattr(response, "output_text", None)
    if not text:
        text = str(response)
    print("=== AGENT RESPONSE (first 1200 chars) ===")
    print(text[:1200])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="run one test evaluation through the agent")
    parser.add_argument("--list", action="store_true", help="list agent versions")
    args = parser.parse_args()

    if args.list:
        list_versions()
        return
    create_or_update()
    if args.smoke:
        smoke_test()


if __name__ == "__main__":
    main()
