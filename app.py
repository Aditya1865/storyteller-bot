import streamlit as st
import google.generativeai as genai
import sys

# --- 1. Configuration and API Key ---

# Set the page title and icon
st.set_page_config(
    page_title="Storyteller-bot",
    page_icon="📚"
)

# Load the API key from Streamlit's secrets
try:
    # This is the secure way to add your key in Streamlit
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
    if not GOOGLE_API_KEY:
        st.error("GEMINI_API_KEY not found in Streamlit secrets.")
        sys.exit()
    
    genai.configure(api_key=GOOGLE_API_KEY)

except KeyError:
    st.error("ERROR: 'GEMINI_API_KEY' not found.")
    st.info("Please add it to your Streamlit secrets (Settings > Secrets).")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred during configuration: {e}")
    st.stop()

# --- 2. Model Initialization ---

# This is the "system instruction" or "pre-prompt"
storyteller_prompt = """
You are a master storyteller. Your only purpose is to tell engaging, creative, 
and well-structured stories based on the user's request. 
You must not break character. Do not provide commentary, definitions, or 
any text that is not part of the story itself. 
You must always respond with a story.
"""

# Initialize the generative model
model = genai.GenerativeModel(
    model_name='gemini-pro-latest',  # Using the model we know works
    system_instruction=storyteller_prompt
)

# --- 3. The Storytelling Function ---

def tell_story(prompt):
    """
    Sends the user's prompt to the model and returns the story.
    """
    try:
        chat = model.start_chat()
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the story: {e}"

# --- 4. The Web App Interface (Streamlit) ---

# Title of the web app
st.title("📚 Gemini Storyteller Bot")
st.write("Tell me what kind of story you want to hear, and I will write it for you.")

# Create a text input box
user_prompt = st.text_area("Your Story Prompt:", height=150)

# Create a button
if st.button("Tell Me a Story"):
    if user_prompt:
        # If there's a prompt, show a "thinking" message
        with st.spinner("Thinking of a story for you..."):
            # Generate the story
            story = tell_story(user_prompt)
            # Display the story
            st.markdown(story)
    else:
        # If the prompt is empty
        st.warning("Please enter a prompt for your story.")
