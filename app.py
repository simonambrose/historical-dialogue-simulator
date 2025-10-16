import google.generativeai as genai
import streamlit as st
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Historical Dialogue Simulator",
    page_icon="🏛️",
    layout="wide"
)

# --- The Grand Foyer Welcome Text ---
st.title("Historical Dialogue Simulator")
st.subheader("Speak with the greatest minds in history.")
st.markdown("""
Welcome to the Library of Minds.

Here, through the magic of modern AI, you can engage in conversation with recreations of some of history's most influential figures. Each personality is crafted from their known writings, philosophies, and vocal styles.

**To begin:**
1.  Explore the categories in the Library Wing in the sidebar.
2.  Select a figure to speak with.
3.  Ask your question.

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

# --- NEW: Categorized Pantheon ---
PANTHEON_CATEGORIZED = {
    "Leaders & Statesmen": [
        "Winston Churchill",
        "John F. Kennedy",
        "Boudica"
    ],
    "Scientists & Thinkers": [
        "Carl Sagan",
        "Albert Einstein"
    ],
    "Artists & Rebels": [
        "John Lennon",
        "Frida Kahlo",
        "Bruce Lee"
    ],
    "Warriors & Strategists": [
        "Muhammad Ali",
        "Doc Holliday"
    ],
    "Modern Minds": [
        "Joe Rogan"
    ]
}

# --- The Core Engine Function ---
def get_gemini_response(character_profile, user_prompt, chat_history):
  model = genai.GenerativeModel('models/gemini-pro-latest')
  
  full_prompt = (
      f"{character_profile}\n\n"
      f"IMPORTANT INSTRUCTION: Structure your response using Markdown. "
      f"Use bolding for emphasis, italics for thoughts or quoted text, and bullet points for lists where appropriate.\n\n"
      f"--- CONVERSATION HISTORY ---\n{chat_history}\n\n"
      f"--- CURRENT QUESTION ---\nUser asks: {user_prompt}"
  )
  
  response = model.generate_content(full_prompt)
  return response.text

# --- Session State Initialization ---
if 'character_choice' not in st.session_state:
    st.session_state['character_choice'] = "Winston Churchill" # Default character
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = {}

# --- Sidebar Controls ---
st.sidebar.title("The Library Wing")

# --- NEW: Categorized Sidebar Layout ---
for category, members in PANTHEON_CATEGORIZED.items():
    with st.sidebar.expander(category):
        for member in members:
            if st.button(member, key=member, use_container_width=True):
                # When a character button is clicked, update the session state
                if st.session_state['character_choice'] != member:
                    st.session_state['character_choice'] = member
                    # No need to rerun here, Streamlit's button logic handles it

character_choice = st.session_state['character_choice']

st.sidebar.markdown("---")
user_question = st.sidebar.text_input(f"Ask your question to {character_choice}:")

# Get the history for the currently selected character
current_history_list = st.session_state.chat_history.get(character_choice, [])

# --- Main Interaction Logic ---
if st.sidebar.button("Generate Response"):
    if user_question:
        profile_to_use = load_profile(character_choice)
        if profile_to_use:
            history_for_prompt = "\n".join([f"User: {entry['user']}\n{character_choice}: {entry['model']}" for entry in current_history_list])
            response = get_gemini_response(profile_to_use, user_question, history_for_prompt)
            current_history_list.append({"user": user_question, "model": response})
            st.session_state.chat_history[character_choice] = current_history_list
    else:
        st.sidebar.warning("Please ask a question first.")

# --- Display the Conversation History ---
st.subheader(f"Conversation with {character_choice}")
if not current_history_list:
    st.info("Your conversation will appear here.")
else:
    # We use a little trick to make sure the chat rerenders when a new response is added
    chat_container = st.container()
    with chat_container:
        for entry in current_history_list:
            with st.chat_message("user"):
                st.markdown(entry['user'])
            with st.chat_message("assistant"):
                st.markdown(entry['model'])
