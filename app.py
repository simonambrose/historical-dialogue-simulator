import google.generativeai as genai
import streamlit as st
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Historical Dialogue Simulator", 
    page_icon="🏛️",
    layout="wide" # Use a wider layout for more space
)

# --- The Streamlit User Interface ---
st.title("Historical Dialogue Simulator")
st.subheader("Speak with the greatest minds in history.")

# --- NEW: The Grand Foyer Welcome Text ---
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
    """
    Loads a character's profile text from a file in the 'profiles' folder.
    """
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
    "Friedrich Nietzsche", 
    "Boudicca"
]

# --- The Core Engine Function ---
def get_gemini_response(character_profile, user_prompt):
  """
  Generates a response from Gemini.
  """
  model = genai.GenerativeModel('models/gemini-pro-latest')
  full_prompt = f"{character_profile}\n\n---\n\nUser asks: {user_prompt}"
  response = model.generate_content(full_prompt)
  return response.text

# --- MOVED TO SIDEBAR: Character Selection and Interaction ---
st.sidebar.title("Control Panel")

character_choice = st.sidebar.selectbox(
    "Choose a historical figure:",
    PANTHEON_NAMES
)

user_question = st.sidebar.text_input(f"Ask your question to {character_choice}:")

if st.sidebar.button("Generate Response"):
    if user_question:
        profile_to_use = load_profile(character_choice)
        
        if profile_to_use:
            st.write(f"--- {character_choice}'s Answer ---")
            response = get_gemini_response(profile_to_use, user_question)
            st.write(response)
    else:
        st.sidebar.write("Please ask a question first.")


