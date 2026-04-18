import os, sys, traceback
from azure.identity import DefaultAzureCredential
cred = DefaultAzureCredential()

print("=== Token acquisition ===")
try:
    t = cred.get_token("https://cognitiveservices.azure.com/.default")
    print("cognitiveservices token OK, expires", t.expires_on)
except Exception as e:
    traceback.print_exc()

print("=== OpenAI embedding ===")
try:
    from openai import AzureOpenAI
    t = cred.get_token("https://cognitiveservices.azure.com/.default")
    c = AzureOpenAI(azure_ad_token=t.token, azure_endpoint="https://qgc-openai.openai.azure.com/", api_version="2024-10-21")
    r = c.embeddings.create(input="hello", model="text-embedding-3-large")
    print("embedding OK, len=", len(r.data[0].embedding))
except Exception as e:
    print("EMBEDDING FAIL:", type(e).__name__, str(e)[:400])

print("=== Cosmos ===")
try:
    from azure.cosmos import CosmosClient
    cc = CosmosClient("https://qgccosmoseval.documents.azure.com:443/", credential=cred)
    dbs = [d["id"] for d in cc.list_databases()]
    print("cosmos dbs:", dbs)
except Exception as e:
    print("COSMOS FAIL:", type(e).__name__, str(e)[:400])

print("=== Search ===")
try:
    from azure.search.documents import SearchClient
    sc = SearchClient(endpoint="https://qgcsearcheval.search.windows.net", index_name="quantum-algorithms", credential=cred)
    results = list(sc.search(search_text="grover", top=1))
    print("search OK, hits=", len(results))
except Exception as e:
    print("SEARCH FAIL:", type(e).__name__, str(e)[:400])
