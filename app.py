import streamlit as st
import google.generativeai as genai
import sys

# --- 1. Configuration and API Key ---

st.set_page_config(
    page_title="StorySaga-bot",
    page_icon="📚",
    layout="wide"  # <-- NEW: Use the full width of the page
)

# Load the API key from Streamlit's secrets
try:
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

# --- Sidebar ---
# All controls are now moved to the sidebar
st.sidebar.title("📚 StorySaga-bot")
st.sidebar.write("Tell me what kind of story you want to hear, and I will write it for you.")

# Create a text input box in the sidebar
user_prompt = st.sidebar.text_area("Your Story Prompt:", height=150)

# Create a button in the sidebar
button_clicked = st.sidebar.button("Tell Me a Story")

# NEW: Add a note about the theme
st.sidebar.info("Pro Tip: You can change the app's theme (light/dark) in the ☰ menu at the top-right!")


# --- Main Page ---
# The main page is now just for the output
st.title("Your Custom-Generated Story")

# We use a placeholder to show a message until the first story is generated
story_placeholder = st.empty()
story_placeholder.write("Your story will appear here once you enter a prompt and click the button in the sidebar.")

# Check if the button in the sidebar was clicked
if button_clicked:
    if user_prompt:
        # If there's a prompt, show a "thinking" message
        with st.spinner("Thinking of a story for you..."):
            story = tell_story(user_prompt)
            # Replace the placeholder with the story
            story_placeholder.markdown(story)
    else:
        # If the prompt is empty
        st.warning("Please enter a prompt for your story.")
