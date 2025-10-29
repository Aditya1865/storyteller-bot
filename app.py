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

If the user asks you to "continue" or "make it longer," you will continue the
most recent story you told.
"""

# Initialize the generative model
model = genai.GenerativeModel(
    model_name='gemini-pro-latest',
    system_instruction=storyteller_prompt
)

# --- 3. The Web App Interface (Streamlit) ---

# --- Sidebar ---
with st.sidebar:
    st.title("📚 StorySaga-bot")
    
    # Optional: Add your header image here
    # st.image("YOUR_IMAGE_URL_HERE", use_column_width=True)

    st.write("Welcome! I'm StorySaga, your personal AI storyteller.")
    st.write("Give me a prompt, or ask me to 'continue' the last story.")
    
    st.divider()
    
    # NEW: Add a "Clear Chat" button
    if st.button("Clear Story History"):
        st.session_state.messages = []  # Clear the chat history
        st.session_state.chat = model.start_chat(history=[]) # Start a new chat
        st.rerun() # Rerun the app to reflect the changes

    st.info("Pro Tip: You can change the app's theme (light/dark) in the ☰ menu at the top-right!")

# --- Main Page (Chat Interface) ---

st.title("Your StorySaga Chat")

# --- NEW: Initialize Chat History in Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- NEW: Initialize the Chat Model in Session State ---
# This keeps the model "aware" of the conversation
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# --- NEW: Display all past messages from history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- NEW: Get new prompt from user ---
if user_prompt := st.chat_input("What story should I tell?"):
    
    # 1. Add user's prompt to message history and display it
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    # 2. Get the bot's response
    try:
        # Use st.chat_message with "assistant" role
        with st.chat_message("assistant"):
            # Show a spinner while we wait for the first chunk
            with st.spinner("The StorySaga is writing..."):
                # Send prompt to the model (which has history) and stream response
                response_stream = st.session_state.chat.send_message(user_prompt, stream=True)
                
                # Use st.write_stream to display the "typing" effect
                full_response = st.write_stream(response_stream)
        
        # 3. Add the bot's full response to the message history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"An error occurred: {e}")
