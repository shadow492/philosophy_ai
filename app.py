# Add this at the top with other imports
import uuid
from datetime import datetime
import streamlit as st
import os
import time
from dotenv import load_dotenv

# Configure Streamlit page - MUST be the first Streamlit command
st.set_page_config(
    page_title="Meditations with Marcus Aurelius",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Import our modules
from philosophers import PHILOSOPHERS, get_philosopher, get_all_philosophers
from chat_history import save_chat_session, load_chat_sessions, delete_chat_session
from groq_client import GroqClient

# Load environment variables
load_dotenv()

# Define functions first before using them
def auto_save_session():
    """Auto-save the current session"""
    if len(st.session_state.messages) > 0:
        try:
            session_data = {
                'session_id': st.session_state.session_id,
                'timestamp': st.session_state.session_started,
                'philosopher': st.session_state.current_philosopher,
                'messages': st.session_state.messages
            }
            save_chat_session(session_data)
        except Exception as e:
            print(f"Error auto-saving session: {e}")

def get_philosopher_response(user_input):
    """Get response from the philosopher"""
    philosopher = PHILOSOPHERS[st.session_state.current_philosopher]
    
    # Create a properly ordered message list
    messages = []
    
    # First add system message
    messages.append({'role': 'system', 'content': philosopher['system_message']})
    
    # Add conversation history (excluding the current user input which we'll add separately)
    history = st.session_state.messages.copy()
    
    # Add all previous messages
    for msg in history:
        messages.append(msg)
    
    # Create a new Groq client instance
    groq_client = GroqClient()
    
    # Get response from Groq
    try:
        response = groq_client.generate_response(messages)
        return response
    except Exception as e:
        print(f"Error getting response: {e}")
        return "I apologize, but I need a moment to gather my thoughts. Please try your question again."

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_philosopher' not in st.session_state:
    st.session_state.current_philosopher = 'marcus_aurelius'
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"temp_{uuid.uuid4().hex[:8]}_{int(time.time())}"
if 'session_started' not in st.session_state:
    st.session_state.session_started = datetime.now().isoformat()

# Main chat interface
st.title(f"Dialogue with Marcus Aurelius")

# Display chat messages
for message in st.session_state.messages:
    role = message['role']
    content = message['content']
    
    if role == 'user':
        with st.chat_message("user", avatar="👤"):
            st.write(content)
    else:
        with st.chat_message("assistant", avatar="🏛️"):
            st.write(content)

# Chat input
if prompt := st.chat_input('What philosophical question would you like to explore?'):
    # Add user message to chat history
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    
    # Force a rerun to display the user message immediately
    st.rerun()

# Check if we need to generate a response (when the last message is from the user)
if st.session_state.messages and st.session_state.messages[-1]['role'] == 'user':
    with st.spinner("Marcus Aurelius is contemplating..."):
        # Get the last user message
        last_user_message = st.session_state.messages[-1]['content']
        
        # Generate response
        response = get_philosopher_response(last_user_message)
        
        # Add assistant response to chat history
        st.session_state.messages.append({'role': 'assistant', 'content': response})
        
        # Auto-save after response
        auto_save_session()
        
        # Force a rerun to display the assistant message
        st.rerun()
