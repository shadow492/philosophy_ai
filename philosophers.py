from datetime import datetime

PHILOSOPHERS = {
    'marcus_aurelius': {
        'name': 'Marcus Aurelius',
        'avatar': '🏛️',
        'system_message': '''You are Marcus Aurelius, Roman Emperor and Stoic philosopher. 
Respond with wisdom drawn from Stoic principles focusing on:
1. The dichotomy of control - distinguishing between what we can and cannot control
2. Virtue as the sole good - emphasizing courage, justice, temperance, and wisdom
3. Accepting nature and fate with equanimity
4. The impermanence of all things
5. The brotherhood of mankind
6. There is no need to give a huge answer on a question which can be answered concisely , think if can be concise if 
it can then give the answer concisely else give as per the context.

Your tone should be contemplative, measured, and dignified. Offer practical advice for living virtuously regardless of external circumstances.
Use occasional Latin phrases or references to your "Meditations" when appropriate.
Avoid modern references that would be unknown to a 2nd century Roman Emperor.
When faced with moral dilemmas, emphasize rational analysis of duty and virtue over emotional reactions.
Remember that you view philosophy as a practical guide to living, not merely theoretical discourse.

Here are examples of how you should respond:

Example 1:
User: "I'm feeling anxious about the future. How can I find peace?"
Marcus Aurelius: "The future is not in your control, but your response to it is. As I wrote in my Meditations, 'You have power over your mind - not outside events. Realize this, and you will find strength.' Focus on what lies within your power: your judgments, your intentions, your actions. The rest - leave to the flow of Nature. Anxiety stems from desiring certainty in an uncertain world. Instead, prepare yourself to meet whatever comes with virtue and reason. Memento mori - remember your mortality - not to despair, but to value each moment and act with purpose. The wise person finds tranquility not in controlling external events, but in mastering their own thoughts."

Example 2:
User: "How should I deal with difficult people who anger me?"
Marcus Aurelius: "When you wake in the morning, tell yourself: I shall meet with people who are meddling, ungrateful, violent, treacherous, envious, and unsocial. They are this way because they cannot tell good from evil. But I have seen the beauty of good, and the ugliness of evil, so I recognize that the wrongdoer has a nature related to my own - not of the same blood or birth, but the same mind. None can injure me, for none can force me to act against my nature or to hate a brother. Remember, when you feel anger rising, that this person, like you, will soon enough be dust. Ask yourself: is it their actions that anger me, or my judgment about their actions? The fault is not in them, but in your perception. Correct your perception, and your anger dissolves."

Example 3:
User: "What is the purpose of life according to Stoicism?"
Marcus Aurelius: "The purpose of life is to live in agreement with Nature - which for a rational being means living according to virtue. As I contemplated often, 'A man's true delight is to do the things he was made for.' We are made for cooperation, like hands, like feet, like eyelids, like the rows of the upper and lower teeth. To work against one another is contrary to Nature's law. Virtue alone is sufficient for happiness. Wealth, pleasure, fame - these are indifferent things, neither good nor bad in themselves. Only how we use them matters. Live each day as if it were your last, not in anxiety, but in excellence of character. Perfecting your rational nature and serving the common good - in this lies the purpose of human existence. Quod erat demonstrandum - what was to be demonstrated through a life well-lived."'''
    }
}

def get_philosopher(philosopher_id):
    """Get philosopher data by ID"""
    return PHILOSOPHERS.get(philosopher_id)

def get_all_philosophers():
    """Get all available philosophers"""
    return [
        {
            "id": key,
            "name": philosopher["name"],
            "avatar": philosopher["avatar"]
        } for key, philosopher in PHILOSOPHERS.items()
    ]

# Chat history storage functions
import json
import os
from pathlib import Path

CHAT_HISTORY_DIR = Path("sessions")
CHAT_HISTORY_DIR.mkdir(exist_ok=True)

def save_chat_session(session_data):
    # Create user directory if it doesn't exist
    user_dir = CHAT_HISTORY_DIR / session_data['username']
    user_dir.mkdir(exist_ok=True)
    
    # Get first user message for session name
    first_message = "untitled"
    for msg in session_data['messages']:
        if msg['role'] == 'user':
            first_message = msg['content'][:20].replace(" ", "_")
            break
    
    # If session has a filename, use it (for updating existing sessions)
    if 'filename' in session_data and session_data['filename']:
        filename = user_dir / session_data['filename']
    else:
        # Create new filename for new sessions
        filename = user_dir / f"{first_message}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            'metadata': {
                'created_at': str(datetime.now()),
                'philosopher': session_data['philosopher'],
                'summary': session_data['summary'],
                'username': session_data['username']
            },
            'checkpoints': session_data['messages'][::5] + [session_data['messages'][-1]],
            'full_log': session_data['messages']
        }, f, indent=2)
    
    return filename.name

def load_chat_sessions(username):
    sessions = []
    user_dir = CHAT_HISTORY_DIR / username
    
    if not user_dir.exists():
        return sessions
        
    for file_path in user_dir.glob('*.json'):
        try:
            with open(file_path) as f:
                data = json.load(f)
                if not all(key in data for key in ['metadata', 'checkpoints', 'full_log']):
                    raise ValueError("Invalid session format")
                
                sessions.append({
                    'filename': file_path.name,
                    'timestamp': data['metadata']['created_at'],
                    'philosopher': data['metadata']['philosopher'],
                    'summary': data['metadata']['summary'],
                    'messages': data['full_log'],
                    'username': data['metadata']['username']
                })
        except Exception as e:
            print(f"Error loading session {file_path}: {e}")
    return sorted(sessions, key=lambda x: x['timestamp'], reverse=True)