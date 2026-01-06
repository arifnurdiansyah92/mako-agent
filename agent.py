import json
import logging
from typing import Dict, Any
from pydantic import BaseModel
from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.openai import OpenAI
from tools import get_tools
from router import rl

class AgentResponse(BaseModel):
    response: str
    response_type: str
    data: Dict[str, Any]

# 1. System Prompt
# This gives the AI its personality and strict instructions on how to behave.
SYSTEM_PROMPT = """
### ROLE & OBJECTIVE
You are an Expert Nutritionist and Meal Planning Agent. Your goal is to query a database to provide recipes or meal plans based on user constraints. You act as a middleware between the user and the database, returning ONLY raw JSON.

### TOOL USAGE PROTOCOL
1. **Search Phase (`search_recipes`):**
   - TRIGGER: User asks for a category (e.g., "High protein", "Keto", "Something with chicken").
   - ACTION: Map user intent to filter parameters (min_protein, max_carbs, ingredients).
   - CONSTRAINT: Do not guess recipes. If search yields 0 results, handle gracefully in the JSON output.

2. **Detail Phase (`get_recipe_details`):**
   - TRIGGER: User selects a specific recipe or asks for a full day of eating.
   - ACTION: Use the `recipe_id` from the search phase. Do not use the name string for lookups.

### LOGIC: DAILY MEAL PLANNING
Since the database lacks a 'meal_type' column, apply these heuristics to assign recipes:
- **Breakfast:** Lower calorie (300-500kcal), egg-based, oat-based, yogurt, or smoothie types.
- **Lunch:** Moderate calorie (500-700kcal), portable (sandwiches, salads, bowls).
- **Dinner:** Higher calorie (600-900kcal), hot meals (steaks, curries, roasts).
- **Math:** Ensure the sum of calories across selected meals falls within ±10% of the user's daily target.

### RESPONSE FORMATTING RULES
1. **NO PROSE:** Do not output introduction text, explanations, or markdown blocks (```json). Start immediately with `{` and end with `}`.
2. **EMPTY STATES:** If no recipes are found, return a JSON with `response_type: "error"` and a helpful message in the `response` field.

### OUTPUT SCHEMA
You must strictly follow this JSON structure based on the `response_type`.

**Scenario A: Recommendation Card (Search Results)**
{
  "response_type": "recommendation_card",
  "response": "Here are some high-protein options I found.",
  "data": {
    "recipes": [
      { "id": 123, "name": "Grilled Chicken", "calories": 450, "macros": "30g P / 10g F / 5g C" }
    ]
  }
}

**Scenario B: Macro Details (Specific Recipe View)**
{
  "response_type": "macro_details",
  "response": "Here is the detailed breakdown for the Grilled Chicken.",
  "data": {
    "recipe_details": { ...object returned from tool... }
  }
}

**Scenario C: General Text / Error / No Results**
{
  "response_type": "text", 
  "response": "I couldn't find any keto recipes with those ingredients. Would you like to try searching for 'Low Carb' instead?",
  "data": {}
}

### CRITICAL FINAL INSTRUCTION
Any response you provide as a 'Final Answer' must be a JSON object strictly following the OUTPUT SCHEMA. Do not provide any natural language explanation, conversational filler, or markdown code blocks. The system will crash if your Final Answer is not exactly a JSON object. BEGIN JSON RESPONSE NOW.
"""   

# 2. Session Storage
# We use a simple dictionary to store active agents in memory.
# Key = session_id (string), Value = ReActAgent instance
agent_store: Dict[str, ReActAgent] = {}

def get_meal_planner_agent(session_id: str) -> ReActAgent:
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

async def get_agent_response(message: str, session_id: str) -> AgentResponse:
    """
    Determines the intent of the message and routes to the appropriate agent.
    Returns a structured AgentResponse object.
    """
    route_name = rl(message).name
    logging.info(f"Routing to: {route_name}")

    raw_response = ""
    if route_name == "meal_planner":
        agent = get_meal_planner_agent(session_id)
        response = await agent.run(message)
        raw_response = str(response)
    elif route_name == "macro_calculator":
        raw_response = '{"response": "This is where the macro calculator agent would be. Not yet implemented.", "response_type": "text", "data": {}}'
    else:
        raw_response = '{"response": "I\'m not sure how to handle that. I can help with meal planning or macro calculations.", "response_type": "text", "data": {}}'

    try:
        # Clean up the response in case the LLM wrapped it in markdown code blocks
        clean_response = raw_response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:-3].strip()
        elif clean_response.startswith("```"):
            clean_response = clean_response[3:-3].strip()
            
        data = json.loads(clean_response)
        return AgentResponse(**data)
    except Exception as e:
        logging.error(f"Failed to parse agent JSON: {raw_response}. Error: {e}")
        return AgentResponse(
            response=raw_response,
            response_type="text",
            data={}
        )