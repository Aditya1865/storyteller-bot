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

model = genai.GenerativeModel(
    model_name='gemini-pro-latest',
    system_instruction=storyteller_prompt
)

# --- 3. The Storytelling Function (MODIFIED for Streaming) ---

def tell_story_stream(prompt):
    """
    Sends the user's prompt to the model and yields the response in chunks.
    """
    try:
        chat = model.start_chat()
        # NEW: Added stream=True
        response_stream = chat.send_message(prompt, stream=True)
        
        # NEW: Yield each chunk of text as it arrives
        for chunk in response_stream:
            yield chunk.text
            
    except Exception as e:
        # Yield the error message as part of the stream
        yield f"An error occurred while generating the story: {e}"

# --- 4. The Web App Interface (Streamlit) ---

# --- Sidebar ---
with st.sidebar:
    st.title("📚 StorySaga-bot")
    
    # NEW: Add a header image. 
    # Replace this with your own image URL or local file path
    # You can find a URL by right-clicking an image online and "Copy Image Address"
    try:
        st.image("https://i.imgur.com/KxP2sB3.png", use_column_width=True)
    except:
        st.write("*(Image could not be loaded)*")

    st.write("Tell me what kind of story you want to hear, and I will write it for you.")

    # NEW: The text_area now uses session_state
    user_prompt = st.text_area(
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

    st.info("You can change the app's theme (light/dark) in the ☰ menu at the top-right!")


# --- Main Page ---
st.title("Your Custom-Generated Story")

# We use a placeholder to show a message until the first story is generated
story_placeholder = st.empty()

if button_clicked:
    if user_prompt:
        # If there's a prompt, clear the placeholder and stream the new story
        story_placeholder.empty()
        
        # NEW: Use st.write_stream to display the "typing" effect
        with st.spinner("The StorySaga is writing..."):
            story_placeholder.write_stream(tell_story_stream(user_prompt))
        
        # NEW: Add a fun celebration!
        st.balloons()
            
    else:
        # If the prompt is empty
        st.warning("Please enter a prompt for your story.")
else:
    # This is the default message
    story_placeholder.write("Your story will appear here once you enter a prompt and click the button in the sidebar.")
