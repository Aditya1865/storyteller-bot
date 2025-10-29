import streamlit as st
import google.generativeai as genai
import sys

# --- 1. Configuration and API Key ---

st.set_page_config(
    page_title="StorySaga-bot",
    page_icon="📚",
    layout="wide"  # Use the full width of the page
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
# The sidebar UI is unchanged, with one new button
with st.sidebar:
    st.title("📚 StorySaga-bot")
    st.write("Tell me what kind of story you want to hear, and I will write it for you.")

    # Create a text input box in the sidebar
    user_prompt = st.text_area("Your Story Prompt:", height=150)

    # Create a button in the sidebar
    button_clicked = st.button("Tell Me a Story")

    st.divider() # Adds a nice horizontal line
    
    # --- NEW: Clear History Button ---
    if st.button("Clear Story History"):
        st.session_state.history = [] # Clears the history
        st.rerun() # Refreshes the app

    st.info(" You can change the app's theme (light/dark) in the ☰ menu at the top-right!")


# --- NEW: Initialize Session State for History ---
# We will store a list of {"prompt": ..., "story": ...} dictionaries
if "history" not in st.session_state:
    st.session_state.history = []

# --- Main Page (MODIFIED for History) ---
st.title("Your StorySaga History")

# --- Logic to generate new story ---
if button_clicked:
    if user_prompt:
        with st.spinner("Thinking of a story for you..."):
            story = tell_story(user_prompt)
            # --- NEW: Add the new story to the start of the history list ---
            st.session_state.history.insert(0, {"prompt": user_prompt, "story": story})
    else:
        # If the prompt is empty, show warning in the sidebar
        st.sidebar.warning("Please enter a prompt for your story.")

# --- Display the History ---
# We check if the history list is empty
if not st.session_state.history:
    st.write("Your stories will appear here once you enter a prompt and click the button in the sidebar.")
else:
    # --- NEW: Loop through the history and display each item ---
    for i, entry in enumerate(st.session_state.history):
        st.subheader(f"Story #{len(st.session_state.history) - i}") # e.g., "Story #1"
        
        # We use st.expander to keep the UI clean
        # The user's prompt is the title of the expander
        with st.expander(f"**Prompt:** {entry['prompt'][:60]}..."):
            st.markdown(entry["story"])
