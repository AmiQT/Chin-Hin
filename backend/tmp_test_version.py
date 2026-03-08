import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

def test_version(version):
    print(f"\nTesting API version: {version}")
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=version
        )
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        print(f"✅ Success with {version}: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Failed with {version}: {e}")
        return False

versions = [
    "2024-10-21",
    "2024-08-01-preview",
    "2024-05-01-preview",
    "2024-02-01",
    "2023-05-15",
    "2025-10-03" # Try the one they gave again to be sure
]

for v in versions:
    if test_version(v):
        print(f"\nFINISH: Berjaya guna version: {v}")
        break
