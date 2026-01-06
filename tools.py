import json
import os
from typing import Optional
from sqlalchemy import text
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.tools import FunctionTool
from database import get_db_connection

# --- RAG Setup ---
KNOWLEDGE_DIR = "knowledge"
query_engine = None

if os.path.exists(KNOWLEDGE_DIR) and any(os.scandir(KNOWLEDGE_DIR)):
    try:
        documents = SimpleDirectoryReader(KNOWLEDGE_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
    except Exception as e:
        print(f"Error initializing RAG: {e}")

def search_recipes(
    min_protein: Optional[int] = None, 
    max_calories: Optional[int] = None,
    max_fat: Optional[int] = None,
    max_carbs: Optional[int] = None,
    limit: int = 5
) -> str:
    """
    Search for recipes. 
    Returns a list of: [ID] Name (Macros).
    """
    query_parts = ["SELECT id, name, calories, protein, fat, carbs FROM recipes WHERE 1=1"]
    params = {}
    
    if min_protein:
        query_parts.append("AND protein >= :min_protein")
        params["min_protein"] = min_protein
    if max_calories:
        query_parts.append("AND calories <= :max_calories")
        params["max_calories"] = max_calories
    if max_fat:
        query_parts.append("AND fat <= :max_fat")
        params["max_fat"] = max_fat
    if max_carbs:
        query_parts.append("AND carbs <= :max_carbs")
        params["max_carbs"] = max_carbs
        
    query_parts.append(f"LIMIT {limit}")
    final_query = text(" ".join(query_parts))
    
    try:
        with get_db_connection() as conn:
            result = conn.execute(final_query, params).fetchall()
            
        if not result:
            return "No recipes found matching those criteria."
        
        recipes_list = []
        for row in result:
            # Map the tuple by index. 
            # row structure based on your logs: (id, name, cal, prot, fat, carb)
            recipes_list.append({
                "id": row[0],
                "name": row[1],
                "calories": row[2],
                # Explicitly cast Decimal to float (or int) for JSON serialization
                "macros": {
                    "protein": float(row[3]),
                    "fat": float(row[4]),
                    "carbs": float(row[5])
                }
            })
        print("Tools Called")
        print(json.dumps(recipes_list))
        return json.dumps(recipes_list)
        
    except Exception as e:
        return f"Database Error: {str(e)}"

def get_recipe_details(
    recipe_id: Optional[int] = None, 
    recipe_name: Optional[str] = None
) -> str:
    """
    Get details for a specific recipe.
    You MUST provide either `recipe_id` (preferred) or `recipe_name`.
    """
    try:
        with get_db_connection() as conn:
            # 1. Determine lookup method
            if recipe_id:
                query = text("SELECT id, name, calories, protein, fat, carbs, image_url FROM recipes WHERE id = :val")
                param = {"val": recipe_id}
            elif recipe_name:
                # We use ILIKE for case-insensitive matching if they search by name
                query = text("SELECT id, name, calories, protein, fat, carbs, image_url FROM recipes WHERE name ILIKE :val")
                param = {"val": recipe_name.strip()}
            else:
                return "Error: You must provide either a recipe_id or a recipe_name."

            # 2. Execute Metadata Query
            recipe = conn.execute(query, param).fetchone()
            
            if not recipe:
                return "Recipe not found."
            
            # Found the ID (in case we searched by name)
            target_id = recipe[0]
            
            # 3. Get Ingredients
            ing_query = text("""
                SELECT i.name, ri.amount 
                FROM recipe_ingredients ri 
                JOIN ingredients i ON ri.ingredient_id = i.id 
                WHERE ri.recipe_id = :rid
            """)
            ingredients_rows = conn.execute(ing_query, {"rid": target_id}).fetchall()
            ingredients_list = [f"{row[1]} {row[0]}" for row in ingredients_rows]
            
            # 4. Get Steps
            steps_query = text("""
                SELECT step_number, description 
                FROM recipe_steps 
                WHERE recipe_id = :rid 
                ORDER BY step_number ASC
            """)
            steps_rows = conn.execute(steps_query, {"rid": target_id}).fetchall()
            steps_list = [f"{row[0]}. {row[1]}" for row in steps_rows]
            
            return json.dumps({
                "id": target_id,
                "name": recipe[1],
                "image": recipe[6],
                "macros": {
                    "calories": recipe[2], "protein": float(recipe[3]),
                    "fat": float(recipe[4]), "carbs": float(recipe[5])
                },
                "ingredients": ingredients_list,
                "instructions": steps_list
            }, indent=2)

    except Exception as e:
        return f"Database Error: {str(e)}"

def search_calorie_rules(query: str) -> str:
    """
    Search for calorie calculation rules (BMR, TDEE, Mifflin-St Jeor).
    Use this to find formulas for personal calorie needs.
    """
    if not query_engine:
        return "Calorie calculation rules are currently unavailable (Knowledge base empty)."
    
    response = query_engine.query(f"Find calorie calculation formulas and rules for: {query}")
    return str(response)

def search_macro_rules(query: str) -> str:
    """
    Search for macro-nutrient distribution rules (Protein, Fats, Carbs ratios).
    Use this to find how to divide calories into macros.
    """
    if not query_engine:
        return "Macro distribution rules are currently unavailable (Knowledge base empty)."
    
    response = query_engine.query(f"Find macro-nutrient distribution ratios and rules for: {query}")
    return str(response)

def get_tools():
    return [
        FunctionTool.from_defaults(search_recipes),
        FunctionTool.from_defaults(get_recipe_details),
        FunctionTool.from_defaults(search_calorie_rules),
        FunctionTool.from_defaults(search_macro_rules),
    ]