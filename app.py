import google.generativeai as genai
import streamlit as st
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Historical Dialogue Simulator",
    page_icon="🏛️",
    layout="wide"
)

# --- The Streamlit User Interface ---
st.title("Historical Dialogue Simulator")
st.subheader("Speak with the greatest minds in history.")

# --- The Grand Foyer Welcome Text ---
st.markdown("""
Welcome to the Historical Dialogue Simulator, a library of living minds.

Here, through the magic of modern AI, you can engage in conversation with recreations of some of history's most influential figures. Each personality is crafted from their known writings, philosophies, and vocal styles.

**To begin:**
1.  Choose a figure from the pantheon in the sidebar.
2.  Ask your question.
3.  Await their answer.

The conversation has begun.
""")
st.markdown("---") # Visual separator

# --- API Key Configuration ---
try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        st.error("GEMINI_API_KEY environment variable not set! Please set it before running the app.")
    else:
        genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Error configuring the API key: {e}")

# --- Function to load profile from file ---
def load_profile(character_name):
    filename = f"profiles/{character_name.lower().replace(' ', '_')}.txt"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Profile file not found for '{character_name}'. Looking for: {filename}")
        return None

# --- Simple list of characters ---
PANTHEON_NAMES = [
    "Bruce Lee",
    "Joe Rogan",
    "Muhammad Ali",
    "Carl Sagan",
    "Albert Einstein",
    "John Lennon",
    "Winston Churchill",
    "Doc Holliday",
    "Frida Kahlo",
    "John F. Kennedy",
    "Boudica" # <-- Boudica is now in the list
]

# --- The Core Engine Function ---
def get_gemini_response(character_profile, user_prompt, chat_history):
  model = genai.GenerativeModel('models/gemini-pro-latest')
  
  # --- NEW: Enhanced Prompt with Formatting Instruction ---
  # We also pass the chat history for context.
  full_prompt = (
      f"{character_profile}\n\n"
      f"IMPORTANT INSTRUCTION: Structure your response using Markdown. "
      f"Use bolding for emphasis, italics for thoughts or quoted text, and bullet points for lists where appropriate.\n\n"
      f"--- CONVERSATION HISTORY ---\n{chat_history}\n\n"
      f"--- CURRENT QUESTION ---\nUser asks: {user_prompt}"
  )
  
  response = model.generate_content(full_prompt)
  return response.text

# --- Sidebar Controls ---
st.sidebar.title("Control Panel")
character_choice = st.sidebar.selectbox(
    "Choose a historical figure:",
    PANTHEON_NAMES
)
user_question = st.sidebar.text_input(f"Ask your question to {character_choice}:")

# --- NEW: Session State Initialization for Conversation History ---
# This creates a 'memory' for our app
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = {}

if 'current_character' not in st.session_state:
    st.session_state['current_character'] = character_choice

# --- NEW: Reset history if character changes ---
if st.session_state['current_character'] != character_choice:
    st.session_state['chat_history'][st.session_state['current_character']] = [] # Save old history
    st.session_state['current_character'] = character_choice
    st.experimental_rerun() # Rerun to reflect the change

# Get the history for the currently selected character
current_history_list = st.session_state.chat_history.get(character_choice, [])

# --- Main Interaction Logic ---
if st.sidebar.button("Generate Response"):
    if user_question:
        profile_to_use = load_profile(character_choice)
        if profile_to_use:
            # Create a string version of the history for the prompt
            history_for_prompt = "\n".join([f"User: {entry['user']}\n{character_choice}: {entry['model']}" for entry in current_history_list])
            
            # Get the new response
            response = get_gemini_response(profile_to_use, user_question, history_for_prompt)
            
            # Add the new exchange to the history
            current_history_list.append({"user": user_question, "model": response})
            st.session_state.chat_history[character_choice] = current_history_list
    else:
        st.sidebar.warning("Please ask a question first.")

# --- NEW: Display the Conversation History ---
st.subheader(f"Conversation with {character_choice}")
if not current_history_list:
    st.info("Your conversation will appear here.")
else:
    for entry in current_history_list:
        with st.chat_message("user"):
            st.markdown(entry['user'])
        with st.chat_message("assistant"):
            st.markdown(entry['model'])
