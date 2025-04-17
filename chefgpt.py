import os
import json
from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load environment variables from .env file
load_dotenv()

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-002", temperature=0.7)

# Define the prompt template for recipe generation
recipe_prompt = PromptTemplate(
    input_variables=["ingredients"],
    template=(
        "You are a professional Indian chef. Given the following ingredients: {ingredients}, "
        "provide a detailed Indian recipe including the dish name, ingredients with quantities, "
        "and step-by-step cooking instructions."
    )
)

# Define the prompt template for nutritional information
nutrition_prompt = PromptTemplate(
    input_variables=["recipe"],
    template=(
        "Given the following recipe, provide approximate nutritional information per serving, "
        "including calories, protein, fat, carbohydrates, fiber, and sodium:\n\n{recipe}"
    )
)

# Create LLMChain instances for recipe and nutrition
recipe_chain = LLMChain(llm=llm, prompt=recipe_prompt)
nutrition_chain = LLMChain(llm=llm, prompt=nutrition_prompt)

# --- File Paths ---
CHAT_HISTORY_FILE = "chat_history.json"
RECIPES_FILE = "saved_recipes.json"

# --- Helper Functions ---
def load_json(file_path, default):
    """Load JSON data from a file, or return default if file doesn't exist."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return default

def save_json(file_path, data):
    """Save data to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = load_json(CHAT_HISTORY_FILE, [])

if "saved_recipes" not in st.session_state:
    st.session_state.saved_recipes = load_json(RECIPES_FILE, [])

# --- Page Configuration ---
st.set_page_config(
    page_title="Chef-GPT",
    page_icon="🧑‍🍳",
    layout="centered",
)

# --- Sidebar Navigation ---
st.sidebar.title("🍴 Chef-GPT Menu")
page = st.sidebar.radio(
    "Navigate",
    ["🍳 Home", "📜 Recipes", "📝 Saved Chats", "📦 Ingredients"]
)

# --- Page Header ---
st.markdown("# Welcome to Chef-GPT 🧑‍🍳")
st.markdown("Your friendly AI assistant, always ready to chat!")
st.markdown("---")

# --- Home Page ---
if page == "🍳 Home":
    # --- Chatbot UI ---
    st.subheader("Chat with Chef-GPT")
    user_input = st.text_input("Enter ingredients (comma-separated):")

    if user_input:
        # Generate recipe
        recipe = recipe_chain.run({"ingredients": user_input})
        st.write("🍽 Recipe:")
        st.write(recipe)

        # Generate nutritional information
        nutrition_info = nutrition_chain.run({"recipe": recipe})
        st.write("📊 Nutritional Information:")
        st.write(nutrition_info)

        # Save chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "bot", "content": recipe})
        st.session_state.messages.append({"role": "bot", "content": nutrition_info})
        save_json(CHAT_HISTORY_FILE, st.session_state.messages)

elif page == "📜 Recipes":
    st.subheader("🍽 Your AI Recipes")

    with st.form("recipe_form"):
        recipe_name = st.text_input("Recipe Name")
        ingredients = st.text_area("Ingredients")
        instructions = st.text_area("Instructions")
        submitted = st.form_submit_button("Save Recipe")

        if submitted:
            if recipe_name and ingredients and instructions:
                new_recipe = {
                    "name": recipe_name,
                    "ingredients": ingredients,
                    "instructions": instructions
                }
                st.session_state.saved_recipes.append(new_recipe)
                save_json(RECIPES_FILE, st.session_state.saved_recipes)
                st.success("Recipe saved successfully!")
            else:
                st.error("Please fill in all fields.")

    st.markdown("---")
    st.subheader("📖 Saved Recipes")
    if st.session_state.saved_recipes:
        for idx, recipe in enumerate(st.session_state.saved_recipes):
            st.markdown(f"### {recipe['name']}")
            st.markdown(f"*Ingredients:*\n{recipe['ingredients']}")
            st.markdown(f"*Instructions:*\n{recipe['instructions']}")
            if st.button(f"Delete Recipe {idx+1}"):
                st.session_state.saved_recipes.pop(idx)
                save_json(RECIPES_FILE, st.session_state.saved_recipes)
                st.success("Recipe deleted.")
                st.experimental_rerun()
            st.markdown("---")
    else:
        st.info("No recipes saved yet.")

elif page == "📝 Saved Chats":
    st.subheader("💬 Saved Chats")
    if st.session_state.messages:
        for msg in st.session_state.messages:
            role = "🧑 You" if msg["role"] == "user" else "🤖 Chef-GPT"
            st.markdown(f"{role}:** {msg['content']}")
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            save_json(CHAT_HISTORY_FILE, st.session_state.messages)
            st.success("Chat history cleared.")
            st.experimental_rerun()
    else:
        st.info("No chat history available.")

elif page == "📦 Ingredients":
    st.subheader("🧂 Ingredient Manager")
    st.info("Feature coming soon: Manage your pantry and let Chef-GPT generate recipes based on available ingredients!")

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Chef-GPT. Powered by Streamlit + AI")
