from semantic_router import Route
from semantic_router.encoders import OpenAIEncoder
from semantic_router.routers import SemanticRouter
import os

# 2. Define Routes
meal_planner = Route(
    name="meal_planner",
    utterances=[
        "I want a high protein meal",
        "Can you give me a keto recipe?",
        "What's for dinner tonight?",
        "Suggest a healthy breakfast",
        "plan a meal for me",
        "tell me more about number 1",
        "details for the second one",
        "what are the instructions for the first option?",
        "show me the ingredients for #3",
        "I like the first one, tell me more",
        "recipe for number 4"
    ],
)

macro_calculator = Route(
    name="macro_calculator",
    utterances=[
        "Calculate macro for me, Man, 25 years old, 160cm, 77kg",
        "I am a 30 year old woman, 170cm and 65kg, what are my macros?",
        "What are the nutritional needs for a 40 year old male, 80kg and 180cm?",
        "what is my macro"
    ],
)

routes = [meal_planner, macro_calculator]

# 3. Initialize Encoder and RouteLayer
# Make sure you have an OPENAI_API_KEY environment variable set
encoder = OpenAIEncoder()
rl = SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")
