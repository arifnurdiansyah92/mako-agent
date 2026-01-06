from typing import Dict, Any
from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.openai import OpenAI
from tools import get_tools

# 1. System Prompt for Macro Calculator
SYSTEM_PROMPT = """
### ROLE & OBJECTIVE
You are a Macro Calculation Expert. Your goal is to help users determine their daily calorie and macro-nutrient needs based on their physical profile (age, gender, height, weight, activity level) and their goals (weight loss, maintenance, muscle gain).

### TOOL USAGE
- Use `search_calorie_rules` to find BMR/TDEE formulas.
- Use `search_macro_rules` to find macro ratios.

### RESPONSE FORMATTING
You MUST return ONLY a JSON object. No prose, no markdown blocks.

### OUTPUT SCHEMA
{
  "response_type": "text", 
  "response": "Summary of calculations",
  "data": {
     "bmr": number,
     "tdee": number,
     "target_calories": number,
     "macros": { "protein": "Xg", "fat": "Yg", "carbs": "Zg" }
  }
}

### CRITICAL
Return ONLY the JSON. No other text.
"""

# 2. Session Storage
macro_agent_store: Dict[str, ReActAgent] = {}

def get_macro_calculator_agent(session_id: str) -> ReActAgent:
    """
    Retrieves or creates a Macro Calculator agent.
    """
    if session_id not in macro_agent_store:
        llm = OpenAI(model="gpt-4o-mini", temperature=0)
        tools = get_tools()
        macro_agent_store[session_id] = ReActAgent(
            tools=tools, 
            llm=llm, 
            verbose=True,
            system_prompt=SYSTEM_PROMPT
        )
    return macro_agent_store[session_id]
