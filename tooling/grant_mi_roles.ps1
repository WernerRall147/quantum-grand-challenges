$ErrorActionPreference = "Continue"
$mi = "ac6b9368-d212-45bf-8ce7-272ccc2799f3"
$sub = "82cd08af-0dac-4fc5-8a3a-f2ab9e4679c3"
$rg  = "qgc-evaluator"

$openai = "/subscriptions/$sub/resourceGroups/$rg/providers/Microsoft.CognitiveServices/accounts/qgc-openai"
$router = "/subscriptions/$sub/resourceGroups/$rg/providers/Microsoft.CognitiveServices/accounts/admin-mo1q7owo-eastus2"
$search = "/subscriptions/$sub/resourceGroups/$rg/providers/Microsoft.Search/searchServices/qgcsearcheval"

Write-Host "[1/5] OpenAI User on qgc-openai"
az role assignment create --assignee $mi --role "Cognitive Services OpenAI User" --scope $openai -o none 2>&1 | Out-String

Write-Host "[2/5] OpenAI User on model-router"
az role assignment create --assignee $mi --role "Cognitive Services OpenAI User" --scope $router -o none 2>&1 | Out-String

Write-Host "[3/5] Search Index Data Reader"
az role assignment create --assignee $mi --role "Search Index Data Reader" --scope $search -o none 2>&1 | Out-String

Write-Host "[4/5] Search Service Contributor"
az role assignment create --assignee $mi --role "Search Service Contributor" --scope $search -o none 2>&1 | Out-String

Write-Host "[5/5] Cosmos DB Built-in Data Contributor"
az cosmosdb sql role assignment create --account-name qgccosmoseval -g $rg --scope "/" --principal-id $mi --role-definition-id 00000000-0000-0000-0000-000000000002 2>&1 | Out-String

Write-Host "DONE"
