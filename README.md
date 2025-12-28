# Mako-Agent: Your AI-Powered Macro Coach

Mako-Agent is an intelligent nutritionist and meal planning assistant designed to help you achieve your diet and healthy lifestyle goals. Powered by Llama-Index and OpenAI, this agent provides personalized recipe recommendations based on your specific macro-nutrient requirements.

## Features

- **Personalized Recipe Search:** Find recipes based on your dietary needs, such as minimum protein, maximum calories, fat, or carbohydrates.
- **Detailed Recipe Information:** Get complete recipe details, including ingredients, step-by-step instructions, and macro-nutrient breakdowns.
- **Meal Planning:** Generate daily meal plans (Breakfast, Lunch, Dinner) that align with your calorie targets.
- **Interactive Chat Interface:** Communicate with the agent in a natural, conversational way to get the information you need.

## How It Works

The Mako-Agent uses a sophisticated AI model to understand your requests and interact with a recipe database. Here’s a high-level overview of the architecture:

[// TODO: Add an architectural diagram or flowchart here to visually explain the data flow and component interactions.]

- **Backend API:** A robust backend is built with FastAPI, providing endpoints for chat interactions and health checks.
- **AI Agent:** The core of the application is a `ReActAgent` from the Llama-Index library, which uses an OpenAI model (GPT-3.5-Turbo) to reason and act.
- **Tooling:** The agent is equipped with custom tools to:
    - `search_recipes`: Find recipes in the database that match specific criteria.
    - `get_recipe_details`: Retrieve detailed information for a chosen recipe.
- **Database:** A PostgreSQL database stores all the recipe data, including names, macros, ingredients, and instructions.

## Getting Started

Follow these steps to set up and run the Mako-Agent on your local machine.

### Prerequisites

- Python 3.8+
- An OpenAI API Key
- A running PostgreSQL database instance

### 1. Clone the Repository

```bash
git clone https://github.com/arifnurdiansyah92/mako-agent.git
cd mako-agent
```

### 2. Set Up the Environment

Create a virtual environment and install the required dependencies.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install -r requirements.txt
```
### 3. Configure Environment Variables

Create a `.env` file in the root of the project and add your database connection string and OpenAI API key. You can use the `.env.example` file as a template.

```
DB_CONNECTION_STRING="postgresql://user:password@host:port/database"
OPENAI_API_KEY="your-openai-api-key"
```

### 4. Set Up the Database

Ensure your PostgreSQL database is running and the schema matches the one expected by the application. You will need tables for `recipes`, `ingredients`, and `recipe_ingredients`.
You can use the provided `database.sql` file to set up the schema.

### 5. Run the Application

Start the FastAPI server using Uvicorn.

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be accessible at `http://localhost:8000`.

## API Endpoints

- **`POST /chat`**: The main endpoint for interacting with the agent. Send a JSON payload with your message and a `session_id`.
  - **Request Body:**
    ```json
    {
      "message": "Find me a high-protein recipe with at least 30g of protein.",
      "session_id": "user-123"
    }
    ```
  - **Response:**
    ```json
    {
      "response": "I found a few options for you: ..."
    }
    ```
- **`GET /health`**: A health check endpoint to verify that the API and database are running correctly.

## Example Usage

Once the server is running, you can use a tool like `curl` or any API client to interact with the agent:

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
           "message": "Can you suggest a meal with less than 500 calories?",
           "session_id": "test-session"
         }'
```

The agent will respond with a list of recipes that match your criteria, and you can then ask for the full details of a specific recipe.
