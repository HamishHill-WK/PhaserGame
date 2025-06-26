from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os
import shutil

load_dotenv()
client = OpenAI()

# Dictionary to store conversations by session_id
conversations = {}

def get_response(user_message="", session_id="default", user_id=None):
    # Initialize conversation for new sessions
    if session_id not in conversations:
        conversations[session_id] = []
    
    print(f"{user_id}, {session_id}, {user_message}")
    
    code = get_gamescript(session_id)
    
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f'{user_message} {code}'
    )
    
    # Store conversation in session-specific list
    conversations[session_id].append({
        "role": "user",
        "content": user_message,
        "response": response.output_text,
        "timestamp": datetime.now().isoformat()
    })
    
# CHECK RATE LIMITS FROM RESPONSE
    headers = getattr(response, 'headers', {})
    requests_left = headers.get('x-ratelimit-remaining-requests', 'Unknown')
    tokens_left = headers.get('x-ratelimit-remaining-tokens', 'Unknown')
    
    print(f"📊 Rate Limits - Requests left: {requests_left}, Tokens left: {tokens_left}")
    
    
    print(f"💬 Response: {response}")
    # WARN IF LOW
    if requests_left != 'Unknown' and int(requests_left) < 10:
        print("⚠️ WARNING: Less than 10 requests remaining!")
    
    if tokens_left != 'Unknown' and int(tokens_left) < 1000:
        print("⚠️ WARNING: Less than 1000 tokens remaining!")
        
        # Store co    
    # Save to database with user_id
    #save_conversation_to_db(session_id, user_id)
    
    return response

def get_conversation(session_id):
    """Get conversation history for a specific session"""
    return conversations.get(session_id, [])

def clear_conversation(session_id):
    """Clear conversation history for a specific session"""
    if session_id in conversations:
        del conversations[session_id]

def get_gamescript(session_id="default"):
    """Get user-specific game script"""
    try:
        # Each user gets their own game file
        user_game_file = f"static/js/users/game_{session_id}.js"
        
        # If user file doesn't exist, copy from template
        if not os.path.exists(user_game_file):
            import shutil
            os.makedirs("static/js/users", exist_ok=True)
            shutil.copy("static/js/game.js", user_game_file)
        
        with open(user_game_file, "r") as file:
            return file.read()
    except FileNotFoundError:
        return "Error: game.js template file not found"
    except Exception as e:
        return f"Error reading game file: {e}"
    

def save_conversation_to_db(session_id, user_id=None):
    """Save conversation to database with user tracking"""
    try:
        from data import ExperimentData, db
        import json
        
        if session_id in conversations and conversations[session_id]:
            # Find existing experiment data or create new
            experiment_data = ExperimentData.query.filter_by(
                session_id=session_id, 
                user_action="ai_conversation"
            ).first()
            
            if not experiment_data:
                experiment_data = ExperimentData(
                    session_id=session_id,
                    user_id=user_id,  # Link to anonymous user
                    user_action="ai_conversation",
                    timestamp=datetime.now(),
                    data=json.dumps({"conversation_started": True})
                )
                db.session.add(experiment_data)
            
            # Update conversation data and ensure user_id is set
            if user_id and not experiment_data.user_id:
                experiment_data.user_id = user_id
            
            experiment_data.conversation = json.dumps(conversations[session_id])
            experiment_data.timestamp = datetime.now()  # Update timestamp
            db.session.commit()
            
    except Exception as e:
        print(f"Error saving conversation to database: {e}")

# def count_tokens_in_file(encoding_name="o200k_base"):
#     """Count tokens in a file using OpenAI's tiktoken"""
    
#     # Get the encoding for the specific model
#     encoding = tiktoken.get_encoding(encoding_name)
    
#     content = get_gamescript()
#     print(f"Content length: {len(content)} characters")
#     print(content)
#     # Count tokens
#     tokens = encoding.encode(content)
#     return len(tokens)

# # Usage
# token_count = count_tokens_in_file()
# print(f"File contains {token_count} tokens")

#print(get_response().output_text)