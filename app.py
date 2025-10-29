import streamlit as st
import google.generativeai as genai
import sys
import time

# --- 1. Configuration and API Key ---

st.set_page_config(
    page_title="StorySaga-bot",
    page_icon="📚",
    layout="wide"  # Use the full width of the page
)

# --- Helper Functions ---
def set_prompt_text(text):
    """
    This function will be called when an example button is clicked.
    It updates the session state for the text_area.
    """
    st.session_state.prompt_text = text

# --- Callback function for the main button ---
def run_story_generation():
    """
    This function runs when the "Tell Me a Story" button is clicked.
    It runs *before* the page rerenders.
    """
    # 1. Read all values from session state
    user_prompt = st.session_state.prompt_text
    selected_genre = st.session_state.selected_genre
    selected_length = st.session_state.selected_length
    
    if user_prompt:
        # 2. Build the final prompt
        final_prompt = f"Tell me a {selected_length}-length story"
        if selected_genre != "(No Genre)":
            final_prompt += f" in the {selected_genre} genre"
        final_prompt += f" about: {user_prompt}"

        # 3. Generate the story
        st.session_state.loading = True
        
        story = tell_story(final_prompt)
        
        # 4. Add to history
        st.session_state.history.insert(0, {
            "prompt": user_prompt, 
            "story": story,
            "genre": selected_genre,
            "length": selected_length 
        })
        
        # 5. Clear the text box
        st.session_state.prompt_text = ""
        st.session_state.loading = False
    else:
        # The main page logic will handle the warning.
        pass

# --- Session State Initialization ---
if 'prompt_text' not in st.session_state:
    st.session_state.prompt_text = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "loading" not in st.session_state:
    st.session_state.loading = False
if "selected_length" not in st.session_state:
    st.session_state.selected_length = "Medium"
if "selected_genre" not in st.session_state:
    st.session_state.selected_genre = "(No Genre)"

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
You must always respond with a story. You will adjust the length of the 
story (short, medium, long) as requested by the user.
"""

model = genai.GenerativeModel(
    model_name='gemini-pro-latest',
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

    st.radio(
        "Choose a story length:", 
        ["Short", "Medium", "Long"], 
        index=1,
        horizontal=True,
        key="selected_length" 
    )
    
    genres = ["(No Genre)", "Fantasy", "Sci-Fi", "Mystery", "Horror", "Adventure", "Romance", "Comedy"]
    st.selectbox(
        "Choose a genre (optional):", 
        genres,
        key="selected_genre" 
    )

    st.text_area(
        "Your Story Prompt:", 
        height=150, 
        key="prompt_text" 
    )

    button_clicked = st.button(
        "Tell Me a Story",
        on_click=run_story_generation 
    )

    if button_clicked and not st.session_state.prompt_text:
        st.warning("Please enter a prompt for your story.")

    st.divider() 
    
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

    st.divider() 
    
    if st.button("Clear Story History"):
        st.session_state.history = [] 
        st.session_state.prompt_text = "" 
        st.rerun() 

    st.info(" You can change the app's theme (light/dark) in the ☰ menu at the top-right!")


# --- Main Page (History) ---
st.title("Your StorySaga History")

if st.session_state.loading:
    with st.spinner("Thinking of a story for you..."):
        time.sleep(0.1) 

# --- Display the History ---
if not st.session_state.history:
    st.write("Your stories will appear here once you enter a prompt and click the button in the sidebar.")
else:
    for i, entry in enumerate(st.session_state.history):
        story_number = len(st.session_state.history) - i
        st.subheader(f"Story #{story_number}  (Genre: {entry['genre']}, Length: {entry['length']})")
        
        with st.expander(f"**Prompt:** {entry['prompt'][:60]}..."):
            st.markdown(entry["story"])
            
            # --- NEW: Download Button ---
            # This is the only new code block
            st.download_button(
                label="Download this Story",
                data=entry["story"],
                file_name=f"storysaga_story_{story_number}.txt",
                mime="text/plain",
                key=f"download_btn_{i}" # Add a unique key for each button
            )
