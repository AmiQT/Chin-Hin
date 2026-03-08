import azure.ai.projects
from azure.ai.projects import AIProjectClient
import inspect

print(f"Azure AI Projects version: {azure.ai.projects.__version__}")

print("\n--- AIProjectClient.agents methods ---")
for name, member in inspect.getmembers(AIProjectClient.agents):
    if not name.startswith("_"):
        print(f"agents.{name}")

print("\n--- AIProjectClient methods ---")
for name, member in inspect.getmembers(AIProjectClient):
    if not name.startswith("_"):
        print(f"client.{name}")
        
print("\n--- Listing items in azure.ai.projects.models ---")
from azure.ai.projects import models
for attr in dir(models):
    if "Tool" in attr:
        print(f"Model attr: {attr}")
