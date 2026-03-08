import azure.ai.projects
from azure.ai.projects import models

print(f"Azure AI Projects version: {azure.ai.projects.__version__ if hasattr(azure.ai.projects, '__version__') else 'unknown'}")

def find_class(module, class_name, path=""):
    if hasattr(module, class_name):
        print(f"Found {class_name} at {path}")
    if hasattr(module, "__path__") and path.count(".") < 2:
        for attr in dir(module):
            if not attr.startswith("_"):
                try:
                    sub_module = getattr(module, attr)
                    find_class(sub_module, class_name, f"{path}.{attr}")
                except:
                    pass

print("Searching for ToolSet...")
find_class(azure.ai.projects, "ToolSet", "azure.ai.projects")
print("Searching for FunctionTool...")
find_class(azure.ai.projects, "FunctionTool", "azure.ai.projects")
print("Searching for AgentRole...")
find_class(azure.ai.projects, "AgentRole", "azure.ai.projects")
