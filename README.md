# storySaga-bot
📚 StorySaga-bot
An interactive web app built with Streamlit that uses the Google Gemini API to generate creative stories based on your prompts, genre, and length preferences.

✨ Features
AI-Powered Story Generation: Leverages the gemini-pro-latest model to write unique stories on demand.

Custom Story Controls: Fine-tune your story with:

Genre Selection (Fantasy, Sci-Fi, Mystery, etc.)

Length Selector (Short, Medium, or Long)

Persistent Story History: All your generated stories are saved in an expanding list, so you never lose a great idea.

Download Your Stories: Easily save any story as a .txt file with a single click.

Prompt Suggestions: Get started quickly with one-click example prompts.

Clean Interface: All controls are neatly organized in a sidebar, leaving the main page for your story collection.

Secure: Uses Streamlit's built-in secrets management to keep your API key safe.

🚀 How to Run This Project
You can run this app either by deploying it to Streamlit Community Cloud or by running it locally on your machine.

Option 1: Deploy to Streamlit Cloud (Recommended)
Fork this repository to your own GitHub account.

Go to Streamlit Community Cloud and sign up.

Click "New app" and select your forked repository.

In the app's Settings > Secrets tab, add your API key:

Ini, TOML

GEMINI_API_KEY = "your_actual_api_key_here"
Click "Deploy!"

Option 2: Run Locally
Clone the repository:

Bash

git clone https://github.com/your-username/storyteller-bot.git
cd storyteller-bot
Install the dependencies:

Bash

pip install -r requirements.txt
Create your local secrets file:

Create a folder named .streamlit in the project directory.

Inside that folder, create a file named secrets.toml.

Add your API key to that file:

Ini, TOML

GEMINI_API_KEY = "your_actual_api_key_here"
Run the app:

Bash

streamlit run app.py
🛠️ Technologies Used
Python

Streamlit - For the web app UI.

Google Gemini API (google-generativeai) - For the core AI story generation.
