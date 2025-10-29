import streamlit as st
import google.generativeai as genai
import sys

# --- 1. Configuration and API Key ---

st.set_page_config(
    page_title="StorySaga-bot",
    page_icon="📚",
    layout="wide"  # Use the full width of the page
)

# --- NEW: Function to update the prompt text from a button ---
def set_prompt_text(text):
    """
    This function will be called when an example button is clicked.
    It updates the session state for the text_area.
    """
    st.session_state.prompt_text = text

# --- NEW: Initialize session state for the text area ---
# This is so we can programmatically change its value
if 'prompt_text' not in st.session_state:
    st.session_state.prompt_text = ""

# --- NEW: Initialize Session State for History ---
# We will store a list of {"prompt": ..., "story": ...} dictionaries
if "history" not in st.session_state:
    st.session_state.history = []


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
with st.sidebar:
    st.title("📚 StorySaga-bot")
    st.write("Tell me what kind of story you want to hear, and I will write it for you.")

    # --- MODIFIED: The text_area now uses session_state ---
    user_prompt_input = st.text_area(
        "Your Story Prompt:", 
        height=150, 
        key="prompt_text"  # Binds this to st.session_state.prompt_text
    )

    button_clicked = st.button("Tell Me a Story")
    
    st.divider() # Adds a nice horizontal line

    # --- NEW: Example Prompts ---
    st.write("Or try an example:")
    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "A shy dragon...", 
            on_click=set_prompt_text, 
            args=["A shy dragon who is afraid of heights."]
        )
        st.button(
            "A Mars detective...", 
            on_click=set_prompt_text, 
            args=["A detective on Mars solving a case in a domed city."]
        )
    with col2:
        st.button(
            "A magic library...", 
            on_click=set_prompt_text, 
            args=["A library where the books whisper secrets to the right person."]
        )
        st.button(
            "A lost robot...", 
            on_click=set_prompt_text, 
            args=["The last robot on Earth searching for a single green plant."]
        )

    st.divider() # Adds another horizontal line
    
    # --- Clear History Button ---
    if st.button("Clear Story History"):
        st.session_state.history = [] # Clears the history
        st.session_state.prompt_text = "" # Clears the text box
        st.rerun() # Refreshes the app

    st.info(" You can change the app's theme (light/dark) in the ☰ menu at the top-right!")


# --- Main Page (History) ---
st.title("Your Story")

# --- Logic to generate new story ---
if button_clicked:
    # We read the prompt from the session state, which is linked to the text box
    user_prompt = st.session_state.prompt_text
    
    if user_prompt:
        with st.spinner("Thinking of a story for you..."):
            story = tell_story(user_prompt)
            
            # Add the new story to the start of the history list
            st.session_state.history.insert(0, {"prompt": user_prompt, "story": story})
            
            # --- NEW: Clear the text box after submitting ---
            st.session_state.prompt_text = ""
            
        # We need to rerun to clear the text box immediately
        st.rerun() 
            
    else:
        # If the prompt is empty, show warning in the sidebar
        st.sidebar.warning("Please enter a prompt for your story.")

# --- Display the History ---
if not st.session_state.history:
    st.write("Your stories will appear here once you enter a prompt and click the button in the sidebar.")
else:
    # Loop through the history and display each item
    for i, entry in enumerate(st.session_state.history):
        st.subheader(f"Story #{len(st.session_state.history) - i}")
        
        # The user's prompt is the title of the expander
        with st.expander(f"**Prompt:** {entry['prompt'][:60]}..."):
            st.markdown(entry["story"])
