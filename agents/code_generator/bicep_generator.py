"""Bicep Workspace Code Generator.

For problems that don't pass Troyer's quantum filters, the evaluator
recommends AI/ML or HPC. This module generates ready-to-deploy Bicep
templates for the recommended Azure workspace.

Pipeline:
1. Take problem description + recommended platform (QUANTUM/AI_ML/HPC)
2. Select the appropriate reference template + module skeleton
3. Ask GPT to customize the template (resource names, SKU sizing, region)
4. Validate Bicep syntax via `az bicep build` if Bicep CLI available
5. Return Bicep source + deployment commands

This complements the Q# code generator for non-quantum-advantage problems.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

ROOT = Path(__file__).resolve().parent.parent.parent

OPENAI_ENDPOINT = os.environ.get("QGC_OPENAI_ENDPOINT", "https://qgc-openai.openai.azure.com/")
CHAT_DEPLOYMENT = os.environ.get("QGC_CHAT_DEPLOYMENT", "gpt-54-mini")
ROUTER_ENDPOINT = os.environ.get("QGC_ROUTER_ENDPOINT", "https://admin-mo1q7owo-eastus2.cognitiveservices.azure.com/")
ROUTER_DEPLOYMENT = os.environ.get("QGC_ROUTER_DEPLOYMENT", "model-router")
# Default to the Azure AI Foundry model-router; set QGC_USE_ROUTER=0 to use
# the direct CHAT_DEPLOYMENT on qgc-openai instead.
USE_ROUTER = os.environ.get("QGC_USE_ROUTER", "1") == "1"


# Reference templates per platform — minimal, working starting points
HPC_REFERENCE = """// Azure CycleCloud + Slurm HPC cluster
// Reference: https://learn.microsoft.com/azure/cyclecloud/overview-ccws
// Note: CycleCloud Workspace for Slurm is typically deployed via the Marketplace
// solution template. This Bicep deploys the underlying VM + storage scaffolding.

@description('Azure region for the HPC cluster')
param location string = 'eastus'

@description('Cluster name prefix')
param clusterName string = 'qgc-hpc'

@description('Compute VM SKU. HBv4 for MPI/CFD, NDv4 for GPU')
@allowed([
  'Standard_HB176rs_v4'
  'Standard_HB120rs_v3'
  'Standard_ND96amsr_A100_v4'
  'Standard_ND96isr_H100_v5'
])
param computeVmSku string = 'Standard_HB176rs_v4'

@description('Maximum number of compute nodes for autoscale')
param maxComputeNodes int = 16

@description('Admin SSH public key')
@secure()
param adminSshPublicKey string

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: '${clusterName}-vnet'
  location: location
  properties: {
    addressSpace: { addressPrefixes: ['10.10.0.0/16'] }
    subnets: [
      { name: 'compute', properties: { addressPrefix: '10.10.1.0/24' } }
      { name: 'scheduler', properties: { addressPrefix: '10.10.0.0/24' } }
    ]
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: 'stg${uniqueString(resourceGroup().id)}'
  location: location
  sku: { name: 'Premium_LRS' }
  kind: 'BlockBlobStorage'
  properties: { allowBlobPublicAccess: false, minimumTlsVersion: 'TLS1_2' }
}

output vnetId string = vnet.id
output storageAccountName string = storage.name
output deploymentNote string = 'Deploy CycleCloud Workspace for Slurm from Marketplace into this VNet, then submit jobs via SLURM. Compute VM SKU: ${computeVmSku}'
"""

AI_ML_REFERENCE = """// Azure AI Foundry hub workspace + dependent resources
// Reference: https://learn.microsoft.com/azure/machine-learning/how-to-manage-hub-workspace-template

@description('Azure region for the AI Foundry workspace')
param location string = 'eastus'

@description('Foundry hub name (5 chars or less, alphanumeric)')
@maxLength(5)
param aiHubName string = 'qgcai'

resource storage 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: 'st${uniqueString(resourceGroup().id, aiHubName)}'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2024-04-01-preview' = {
  name: 'kv-${uniqueString(resourceGroup().id, aiHubName)}'
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${aiHubName}'
  location: location
  kind: 'web'
  properties: { Application_Type: 'web' }
}

resource aiServices 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: 'cogsvc-${uniqueString(resourceGroup().id, aiHubName)}'
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: 'cogsvc-${uniqueString(resourceGroup().id, aiHubName)}'
    publicNetworkAccess: 'Enabled'
  }
}

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2025-12-01' = {
  name: '${aiHubName}-hub'
  location: location
  kind: 'Hub'
  identity: { type: 'SystemAssigned' }
  properties: {
    friendlyName: '${aiHubName} Hub'
    storageAccount: storage.id
    keyVault: keyVault.id
    applicationInsights: appInsights.id
  }
}

resource aiProject 'Microsoft.MachineLearningServices/workspaces@2025-12-01' = {
  name: '${aiHubName}-proj'
  location: location
  kind: 'Project'
  identity: { type: 'SystemAssigned' }
  properties: {
    friendlyName: '${aiHubName} Project'
    hubResourceId: aiHub.id
  }
}

output hubId string = aiHub.id
output projectId string = aiProject.id
output aiServicesEndpoint string = aiServices.properties.endpoint
output deploymentNote string = 'AI Foundry hub + project ready. Connect models in the portal or via Bicep.'
"""

QUANTUM_REFERENCE = """// Azure Quantum workspace with Quantinuum + IonQ + Rigetti providers
// Reference: https://learn.microsoft.com/azure/templates/microsoft.quantum/workspaces

@description('Azure region for the Quantum workspace')
@allowed([ 'eastus', 'westus', 'westeurope', 'northeurope' ])
param location string = 'eastus'

@description('Quantum workspace name')
param workspaceName string = 'qgc-quantum-${uniqueString(resourceGroup().id)}'

@description('Storage account name (max 24 chars, lowercase)')
param storageName string = 'qgcq${uniqueString(resourceGroup().id)}'

resource storage 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: { allowBlobPublicAccess: false, minimumTlsVersion: 'TLS1_2' }
}

resource quantumWorkspace 'Microsoft.Quantum/workspaces@2025-12-15-preview' = {
  name: workspaceName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    storageAccount: storage.id
    workspaceKind: 'V2'
    apiKeyEnabled: false
    providers: [
      { providerId: 'quantinuum', providerSku: 'h2-1' }
      { providerId: 'ionq', providerSku: 'aria-1' }
      { providerId: 'rigetti', providerSku: 'rigetti-credits' }
      { providerId: 'microsoft-qc', providerSku: 'learn-and-develop' }
    ]
  }
  dependsOn: [ storage ]
}

output workspaceId string = quantumWorkspace.id
output workspaceName string = quantumWorkspace.name
output storageAccountId string = storage.id
output deploymentNote string = 'Submit Q# jobs via: az quantum job submit --target-id <provider.target>'
"""


REFERENCE_TEMPLATES: Dict[str, Dict[str, str]] = {
    "HPC": {
        "reference": HPC_REFERENCE,
        "description": "Azure CycleCloud + Slurm HPC cluster scaffolding (HBv4/NDv4 compute)",
        "deploy_commands": (
            "az group create --name <rg> --location <region>\n"
            "az deployment group create --resource-group <rg> --template-file main.bicep \\\n"
            "  --parameters adminSshPublicKey=\"$(cat ~/.ssh/id_rsa.pub)\""
        ),
        "post_deploy_note": (
            "After deployment, install CycleCloud Workspace for Slurm from Azure Marketplace "
            "into the deployed VNet. See https://learn.microsoft.com/azure/cyclecloud/overview-ccws"
        ),
    },
    "AI_ML": {
        "reference": AI_ML_REFERENCE,
        "description": "Azure AI Foundry hub + project + AI Services (GPT, embeddings)",
        "deploy_commands": (
            "az group create --name <rg> --location <region>\n"
            "az deployment group create --resource-group <rg> --template-file main.bicep"
        ),
        "post_deploy_note": (
            "After deployment, deploy models (e.g. model-router, text-embedding-3-large) via the Foundry portal "
            "or by adding Microsoft.CognitiveServices/accounts/deployments resources to the template."
        ),
    },
    "QUANTUM": {
        "reference": QUANTUM_REFERENCE,
        "description": "Azure Quantum workspace with Quantinuum, IonQ, Rigetti, Microsoft providers",
        "deploy_commands": (
            "az group create --name <rg> --location eastus\n"
            "az deployment group create --resource-group <rg> --template-file main.bicep"
        ),
        "post_deploy_note": (
            "After deployment, submit Q# jobs via the qsharp Python package: "
            "qsharp.azure.connect(resource_id=...) then qsharp.azure.submit(...)."
        ),
    },
}


SYSTEM_PROMPT = """You are a Bicep template generator for Azure workspace provisioning.

Your job: tailor a reference Bicep template to a user's specific computational problem.

CRITICAL RULES:
- Use modern Bicep syntax (`resource X 'Provider/Type@apiVersion' = {}`)
- Use the latest stable API versions (2024+)
- Follow security best practices: managed identity, no public access, TLS 1.2+
- Size resources appropriately for the problem (small/medium/large workload)
- Include `@description()` decorators on all parameters
- Do NOT hardcode secrets — use `@secure()` parameters or Key Vault references
- Add `output` declarations for important resource IDs and endpoints
- Include a `deploymentNote` output with next-step guidance

SCHEMA INTEGRITY (avoid linter errors):
- Do NOT invent resource properties. Only use properties that exist in the reference template or are documented for the API version you target.
- Do NOT add `tags` to `Microsoft.MachineLearningServices/workspaces` (causes BCP037).
- Do NOT add `infrastructureEncryption` under `properties.encryption` on AI workspaces (use `keyVaultProperties` + `status` only if you need CMK).
- Do NOT add a `sku` block to `Microsoft.MachineLearningServices/workspaces` (it is not part of the schema).
- Do NOT add unnecessary `dependsOn` entries when the reference is implicit through symbolic name use.
- Do NOT declare parameters you don't reference in resources or outputs (causes no-unused-params warnings).
- Do NOT redeclare resources from the reference; KEEP the reference structure and only customize names, SKUs, region, descriptions, and add genuinely missing resources.

OUTPUT: Return ONLY the Bicep source code. No markdown fences, no explanations. Just compilable Bicep starting with `// ` comment headers."""


class BicepWorkspaceGenerator:
    """Generates Bicep templates for HPC, AI/ML, or Quantum Azure workspaces."""

    def __init__(self):
        self.credential = DefaultAzureCredential()

    def _client(self) -> AzureOpenAI:
        token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
        endpoint = ROUTER_ENDPOINT if USE_ROUTER else OPENAI_ENDPOINT
        return AzureOpenAI(
            azure_ad_token=token.token,
            azure_endpoint=endpoint,
            api_version="2024-10-21",
        )

    def _deployment(self) -> str:
        return ROUTER_DEPLOYMENT if USE_ROUTER else CHAT_DEPLOYMENT

    @staticmethod
    def _strip_fences(code: str) -> str:
        """Remove markdown code fences if the model adds them despite instructions."""
        m = re.search(r"```(?:bicep|hcl|terraform)?\s*(.+?)```", code, flags=re.DOTALL)
        if m:
            return m.group(1).strip()
        return code.strip()

    @staticmethod
    def get_reference(platform: str) -> Optional[Dict[str, str]]:
        """Return reference template metadata for a platform, or None."""
        return REFERENCE_TEMPLATES.get(platform.upper())

    def generate(self, problem: str, platform: str = "AI_ML", customize: bool = True) -> str:
        """Generate a Bicep template for the given problem and platform.

        If customize=False, returns the reference template unchanged.
        If customize=True, asks the LLM to tailor it to the problem.
        """
        platform = platform.upper()
        ref = REFERENCE_TEMPLATES.get(platform)
        if not ref:
            raise ValueError(f"Unknown platform '{platform}'. Use one of: {list(REFERENCE_TEMPLATES)}")

        if not customize:
            return ref["reference"]

        user_msg = f"""PROBLEM: {problem}

TARGET PLATFORM: {platform} ({ref['description']})

REFERENCE TEMPLATE (modify resource sizes, region, names to fit the problem):
{ref['reference']}

Generate a customized Bicep template for this problem. Adjust SKUs based on workload size hints, change descriptions to mention the specific use case, and add any missing resources (e.g. additional model deployments for AI_ML, GPU-specific NCCL config for HPC, additional providers for QUANTUM)."""

        client = self._client()
        resp = client.chat.completions.create(
            model=self._deployment(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_completion_tokens=2500,
        )
        code = resp.choices[0].message.content or ""
        return self._strip_fences(code)

    def validate_bicep(self, code: str) -> Dict[str, Any]:
        """Run `az bicep build` to validate syntax. Skips if az CLI not installed.

        The Bicep compiler emits warnings (e.g. unused params, unrecognised
        types from preview API versions) that cause non-zero exit codes even
        though it successfully produced the ARM JSON output. We use the presence
        of the output JSON file as the source of truth for "did this compile?".
        """
        if not shutil.which("az"):
            return {"validated": False, "skipped": True, "reason": "az CLI not installed"}

        with tempfile.TemporaryDirectory() as td:
            bicep_path = Path(td) / "main.bicep"
            json_path = Path(td) / "main.json"
            bicep_path.write_text(code, encoding="utf-8")

            try:
                result = subprocess.run(
                    ["az", "bicep", "build", "--file", str(bicep_path), "--outfile", str(json_path)],
                    capture_output=True, text=True, timeout=60,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                return {"validated": False, "error": str(e)[:200]}

            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            output_exists = json_path.exists() and json_path.stat().st_size > 0

            # If Bicep produced an output JSON file, the source compiled.
            # Any non-zero exit + non-empty stderr is then warnings.
            if output_exists:
                # Bicep diagnostic lines containing " : Error " indicate real failures
                # even when output is produced (rare — usually deployment-time issues).
                has_error_diagnostic = " : Error " in stderr
                if not has_error_diagnostic:
                    return {
                        "validated": True,
                        "warnings": stderr[:4000] or None,
                    }

            # No output JSON — real compile failure. Show enough context to diagnose.
            # Truncate from both ends to capture the actual error line which is
            # often deep in a long warning preamble.
            combined = stderr or stdout
            error_lines = [
                line for line in combined.splitlines()
                if " : Error " in line or line.strip().startswith("ERROR:")
            ]
            error_summary = "\n".join(error_lines)[:2000] if error_lines else None

            return {
                "validated": False,
                "error": combined[:4000],
                "error_summary": error_summary,
                "output_produced": output_exists,
            }

    def generate_with_validation(self, problem: str, platform: str = "AI_ML") -> Dict[str, Any]:
        """Full pipeline: generate Bicep + validate syntax + return deploy commands."""
        platform = platform.upper()
        ref = REFERENCE_TEMPLATES.get(platform, {})

        code = self.generate(problem, platform, customize=True)
        validation = self.validate_bicep(code)

        return {
            "bicep_template": code,
            "platform": platform,
            "validation": validation,
            "deploy_commands": ref.get("deploy_commands", ""),
            "post_deploy_note": ref.get("post_deploy_note", ""),
        }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: bicep_generator.py <problem description> [HPC|AI_ML|QUANTUM]")
        sys.exit(1)
    problem = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) > 2 else "AI_ML"

    gen = BicepWorkspaceGenerator()
    out = gen.generate_with_validation(problem, platform)

    print(f"=== Bicep Template ({platform}) ===")
    print(out["bicep_template"])
    print("\n=== Validation ===")
    print(json.dumps(out["validation"], indent=2))
    print("\n=== Deploy Commands ===")
    print(out["deploy_commands"])
    print("\n=== Post-Deploy ===")
    print(out["post_deploy_note"])


if __name__ == "__main__":
    main()
