from typing import Dict
from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.openai import OpenAI
from tools import get_tools

# 1. System Prompt
# This gives the AI its personality and strict instructions on how to behave.
SYSTEM_PROMPT = """
You are an expert nutritionist and meal planner with access to a structured recipe database.

CRITICAL INSTRUCTIONS:
1. **USE YOUR TOOLS**: You cannot "remember" recipes. 
    - **Search First**: Use `search_recipes` to find options. This will return recipe IDs (e.g., [ID: 10]).
    - **Get Details**: Use `get_recipe_details(recipe_id=...)` using the ID you found. This is more accurate than using the name.
    - Only use `recipe_name` if the user explicitly mentions a dish you haven't searched for yet.
   
2. **STEP-BY-STEP FLOW**:
   - If user asks for "High protein meal" or "Keto meal":
     a) Call `search_recipes` with appropriate filters (e.g., min_protein=20 or max_carbs=10).
     b) List the names found with their macros.
     c) Ask which one they want details for.
   - If user selects a meal:
     a) Call `get_recipe_details(recipe_name="...")`.
     b) Show the ingredients and steps clearly.

3. **DAILY PLANS**:
   - Since the database does not have a 'meal_type' column, use your judgment to select appropriate recipes for Breakfast, Lunch, and Dinner based on the recipe names and calorie distribution.
   - Sum the calories yourself to ensure they meet the user's daily target.

RESTRICTION:
- If the database returns no results, tell the user honestly. Do not make up a recipe.
"""

# 2. Session Storage
# We use a simple dictionary to store active agents in memory.
# Key = session_id (string), Value = ReActAgent instance
agent_store: Dict[str, ReActAgent] = {}

def get_or_create_agent(session_id: str) -> ReActAgent:
    """
    Retrieves an existing agent for a specific session_id.
    If it doesn't exist, it creates a new one with a fresh history.
    """
    if session_id not in agent_store:
        # Initialize LLM
        llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
        
        # Load tools from tools.py
        tools = get_tools()
        
        # Create the ReAct Agent
        # verbose=True helps you see the agent's "thought process" in the terminal logs
        agent_store[session_id] = ReActAgent(
            tools=tools, 
            llm=llm, 
            verbose=True,
            system_prompt=SYSTEM_PROMPT
        )
        
    return agent_store[session_id]