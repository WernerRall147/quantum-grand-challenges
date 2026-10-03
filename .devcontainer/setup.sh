#!/usr/bin/env bash
# Runs once when the dev container or Codespace is created. It installs what CI and the Copilot
# cloud agent install (.github/workflows/copilot-setup-steps.yml), so the three environments
# agree; tooling/test_agent_harness.py fails if the pip install lines drift apart.
set -euo pipefail
cd "$(dirname "$0")/.."

python -m pip install --upgrade pip
pip install numpy scipy matplotlib pandas pytest jsonschema pyyaml qdk==1.31.0 azure-identity openai azure-search-documents==11.6.0
pip install markdown
(cd website && npm ci --no-audit --no-fund)

python -c "from qdk import qsharp; qsharp.init(project_root='problems/01_hubbard/qsharp'); print('Q# compiles')"
echo "Ready. AGENTS.md lists the commands; the agent team is in .github/agents/."