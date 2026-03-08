import sys
import asyncio
import logging
from dotenv import load_dotenv
from app.agents.foundry_agent import get_foundry_manager

logging.basicConfig(level=logging.INFO)
load_dotenv()

def main():
    print("Starting Azure AI Foundry Agent Demo...")
    print("------------------------------------------")
    manager = get_foundry_manager()

    try:
        print("Step 1: Creating Managed Agent on Azure...")
        agent = manager.get_or_create_agent()
        print(f"Agent ID: {agent.id}")

        print("Step 2: Sending test message...")
        user_msg = "Hai! Berapa baki cuti Annual saya?"
        print(f"USER: {user_msg}")

        response = manager.process_message(
            thread_id="",
            message=user_msg,
            agent_id=agent.id
        )
        print(f"AGENT: {response}")
        print("------------------------------------------")
        print("SUCCESS! Agent is live on Azure AI Foundry.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
