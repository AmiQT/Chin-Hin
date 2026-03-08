import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

def test_config(endpoint, version):
    print(f"--- Testing Endpoint: {endpoint} | Version: {version} ---")
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=endpoint,
            api_version=version
        )
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        print(f"SUCCESS: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

base_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
# Clean endpoint of trailing slashes
if base_endpoint.endswith('/'):
    base_endpoint = base_endpoint[:-1]

test_endpoints = [
    base_endpoint,
    f"{base_endpoint}/openai"
]

test_versions = [
    "2024-08-01-preview",
    "2024-10-21",
    "2024-05-01-preview",
    "2023-12-01-preview",
    "2024-02-01",
    "2025-10-03"
]

found = False
for ep in test_endpoints:
    for v in test_versions:
        if test_config(ep, v):
            print(f"\nFOUND WORKING CONFIG!")
            print(f"Endpoint: {ep}")
            print(f"Version: {v}")
            found = True
            break
    if found:
        break

if not found:
    print("\nNo working config found with provided endpoints and common versions.")
