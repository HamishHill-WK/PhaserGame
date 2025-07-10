from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os
import boto3
import tiktoken
import requests

print("Loading OpenAI API key from AWS Secrets Manager...")

def get_secret(secret_name, region_name="eu-west-2"):
    print(f"Fetching secret: {secret_name} from AWS Secrets Manager in region {region_name}")
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
    
    print(f"Loaded secret: {secret_name} from AWS Secrets Manager"
          f" in region {region_name}"
          f" at {datetime.now().isoformat()}")

    return get_secret_value_response['SecretString']

MAX_TOKENS = 1014808

# --- Fetch and set the OpenAI API key from AWS Secrets Manager ---
try:
    openai_api_key = get_secret("openai_api_key1").split(':')[1].replace('\"', '').replace('}', '')  
    os.environ["OPENAI_API_KEY"] = openai_api_key
except Exception as e:
    print("Could not load OpenAI API key from AWS Secrets Manager:", e)

load_dotenv()
client = OpenAI(api_key=openai_api_key)

# Dictionary to store conversations by session_id
conversations = {}

def get_response(prompt="", content="", model="gpt-4.1-mini"):
    # Initialize conversation for new sessions
    response = client.responses.create(
        model=model,
        instructions=prompt,
        input=content
    )
    
    headers = getattr(response, 'headers', {})
    requests_left = headers.get('x-ratelimit-remaining-requests', 'Unknown')
    tokens_left = headers.get('x-ratelimit-remaining-tokens', 'Unknown')    
    
    print(f"💬 Response: {response}")
    # WARN IF LOW
    if requests_left != 'Unknown' and int(requests_left) < 10:
        print("⚠️ WARNING: Less than 10 requests remaining!")
    
    if tokens_left != 'Unknown' and int(tokens_left) < 1000:
        print("⚠️ WARNING: Less than 1000 tokens remaining!")

    return response.output_text

def get_conversation(session_id):
    """Get conversation history for a specific session"""
    return conversations.get(session_id, [])

def clear_conversation(session_id):
    if session_id in conversations:
        del conversations[session_id]

def get_gamescript(session_id="default"):
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

def get_llm_response(context="", user_message="", session_id="default", user_id=None):
    # Initialize conversation for new sessions
    if session_id not in conversations:
        conversations[session_id] = []
    
    print(f"Assistant.py: {user_id}, {session_id}, {user_message}")

    # Append user message (no timestamp for OpenAI input)
    conversations[session_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Prepare content for OpenAI (strip timestamps)
    content = [
        {"role": m["role"], "content": m["content"]}
        for m in conversations[session_id] if "role" in m and "content" in m
    ]
    
    
    
    
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="You are a JavaScript and Phaser.js coding assistant. You are helping a game developer implement mechanics. Provide clear, working code solutions and explanations.",
        input=content
    )
    
    # Store conversation in session-specific list (with timestamp for local tracking)
    conversations[session_id].append({
        "role": "assistant",
        "response": response.output_text,
        "timestamp": datetime.now().isoformat()
    })
    
# CHECK RATE LIMITS FROM RESPONSE
    headers = getattr(response, 'headers', {})
    requests_left = headers.get('x-ratelimit-remaining-requests', 'Unknown')
    tokens_left = headers.get('x-ratelimit-remaining-tokens', 'Unknown')    
    
    print(f"💬 Response: {response}")
    # WARN IF LOW
    if requests_left != 'Unknown' and int(requests_left) < 10:
        print("⚠️ WARNING: Less than 10 requests remaining!")
    
    if tokens_left != 'Unknown' and int(tokens_left) < 1000:
        print("⚠️ WARNING: Less than 1000 tokens remaining!")
        
    return response.output_text

def get_react_response(context="", user_message="", session_id="default", user_id=None):
    # Initialize conversation for new sessions
    if session_id not in conversations:
        conversations[session_id] = []
    
    print(f"Assistant.py: {user_id}, {session_id}, {user_message}")

    # Append user message
    conversations[session_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Calculate total length of all conversation content for this user/session
    total_token_length = sum(
        count_tokens(content=msg.get("content", "")) for msg in conversations[session_id] if "content" in msg
    )
    print(f"Total token length for session {session_id}: {total_token_length}")
    
    total_token_length = total_token_length + count_tokens(user_message)
    
    if total_token_length > MAX_TOKENS:
        return {"error": "Your conversation is too long for the AI to process. Please start a new chat using the clear chat button. This will reset the conversation and allow you to continue. If you have any important information, please copy it before clearing the chat."}
    
    # Initialize conversation context for this ReAct session
    react_context = [user_message]
    final_response = None
    accumulated_data = {
        "session_id": session_id,
        "user_message": user_message,
        "code": None,
        "analysis": None,
        "search_results": None
    }
    
    # ReAct loop
    for step in range(3):
        print(f"ReAct Step {step + 1}")
        
        # Get reasoning with accumulated context
        reasoning_response = reasoning_step(react_context)
        reasoning_text = reasoning_response.output_text
                
        # Parse tools needed
        try:
            tools_section = reasoning_text.split("Tools_needed:")[1].strip()
            tools_requested = [tool.strip() for tool in tools_section.split(',')]
        except IndexError:
            print("No tools section found in reasoning")
            tools_requested = []
        
        # Execute tools if any
        if tools_requested and tools_requested[0]:
            tool_results = call_tools(tools_requested, accumulated_data)
            tool_summary = "\n".join([f"Tool: {tool} -> {result[:100]}..." 
                                    for tool, result in zip(tools_requested, tool_results)])
                        
            # Add to context for next iteration
            react_context.append(f"Reasoning: {reasoning_text}")
            react_context.append(f"Tool Results: {tool_summary}")
        else:
            # No more tools needed, break early
            print("✅ No tools requested, proceeding to final answer")
            break
    
        # Generate final response with all context
        final_response = generate_final_response(
            user_message, 
            react_context, 
            accumulated_data
        )
        
        final_response, final_response_confidence = final_response.output_text.split("Confidence:")
        final_response_confidence = float(final_response_confidence) if final_response_confidence.replace('.', '', 1).isdigit() else 0.0
        if final_response_confidence < 0.5:
            print("⚠️ Low confidence in final response, continuing ReAct loop")
            print(f"Confidence score: {final_response_confidence}")
            print(f"Final response: {final_response}")
            continue
        elif final_response_confidence >= 0.5:
            print("✅ High confidence in final response, breaking ReAct loop")
            break
        
    # Store conversation
    conversations[session_id].append({
        "role": "assistant",
        "response": final_response,
        "timestamp": datetime.now().isoformat()
    })
    
    # Check rate limits
    headers = getattr(final_response, 'headers', {})
    requests_left = headers.get('x-ratelimit-remaining-requests', 'Unknown')
    tokens_left = headers.get('x-ratelimit-remaining-tokens', 'Unknown')    
    
    print(f"💬 Response: {final_response}")
    if requests_left != 'Unknown' and int(requests_left) < 10:
        print("⚠️ WARNING: Less than 10 requests remaining!")
    
    if tokens_left != 'Unknown' and int(tokens_left) < 1000:
        print("⚠️ WARNING: Less than 1000 tokens remaining!")

    return final_response

def call_tools(tools, accumulated_data):
    """Call the specified tools with the given input data."""
    results = []
    
    for tool in tools:
        tool = tool.strip()
        print(f"🔧 Executing tool: {tool}")
        
        try:
            if tool == "get_current_code":
                result = get_gamescript(accumulated_data.get("session_id", "default"))
                accumulated_data["code"] = result
                results.append(f"Retrieved game code ({len(result)} characters)")
                
            elif tool == "analyze_code":
                code = accumulated_data.get("code")
                if not code:
                    code = get_gamescript(accumulated_data.get("session_id", "default"))
                    accumulated_data["code"] = code
                
                result = analyze_code(code)
                accumulated_data["analysis"] = result
                results.append(result)
                
            elif tool.startswith("search_phaser_docs"):
                # Parse query from tool string
                if "query:" in tool:
                    query = tool.split("query:")[1].rstrip(")]").strip()
                else:
                    query = "general phaser documentation"
                
                result = search_phaser_docs(query)
                accumulated_data["search_results"] = result
                results.append(result)
                
            elif tool == "generate_code_example":
                result = generate_code_example(accumulated_data)
                results.append(result)
                
            else:
                result = f"Unknown tool: {tool}"
                results.append(result)
                
        except Exception as e:
            error_msg = f"Error executing {tool}: {str(e)}"
            print(f"❌ {error_msg}")
            results.append(error_msg)
    
    return results

def analyze_code(code):
    """Analyze the provided code using AI for comprehensive insights."""
    
    if not code or code.startswith("Error:"):
        return "No valid code to analyze"
    
    # Prepare the analysis prompt
    prompt = f"""You are a Phaser.js expert analyzing game code. Provide a comprehensive analysis of the following JavaScript/Phaser.js code.

Code to analyze:
```javascript
{code}
```

Provide analysis in the following format:

STRUCTURE:
- Comment on the overall code structure and organization
- Identify classes, methods, and their purposes

PHASER.JS IMPLEMENTATION:
- Evaluate proper use of Phaser.js patterns and best practices
- Check for correct Scene lifecycle methods (preload, create, update)
- Assess physics, sprites, and game object usage

GAME MECHANICS:
- Identify implemented game features (scoring, lives, collision, etc.)
- Evaluate game logic and mechanics implementation

POTENTIAL ISSUES:
- Point out any bugs, syntax errors, or logic problems
- Identify performance concerns or anti-patterns

SUGGESTIONS:
- Recommend specific improvements
- Suggest missing features or enhancements
- Provide actionable next steps

Keep the analysis concise but thorough. Focus on practical feedback."""

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=prompt,
        input=code
    )
    
    return f"AI Code Analysis:\n\n{response.output_text}"



def search_phaser_docs(query: str) -> str:
    """Search Phaser.js documentation using web search."""
    
    search_url = "https://api.duckduckgo.com/"
    params = {
        'q': f'"{query}" site:phaser.io OR site:photonstorm.github.io/phaser3-docs',
        'format': 'json'
    }
    
    response = requests.get(search_url, params=params, timeout=10)
    data = response.json()
    
    results = []
    
    # Get abstract/summary
    if data.get('Abstract'):
        results.append(data['Abstract'])
    
    # Get related topics
    for topic in data.get('RelatedTopics', [])[:3]:
        if isinstance(topic, dict) and 'Text' in topic:
            results.append(topic['Text'])
    
    if results:
        return f"Phaser.js Documentation for '{query}':\n\n" + "\n\n".join(results)
    else:
        return f"No documentation found for '{query}'. Visit https://phaser.io/docs for complete documentation."

def generate_code_example(data):
    """Generate a code example using AI based on accumulated data and user request."""
    
    user_message = data.get("user_message", "")
    current_code = data.get("code", "")
    analysis = data.get("analysis", "")
    search_results = data.get("search_results", "")
    
    # Build context for AI
    context_parts = []
    
    if current_code and not current_code.startswith("Error:"):
        context_parts.append(f"Current game code:\n```javascript\n{current_code}\n```")
    
    if analysis:
        context_parts.append(f"Code analysis results:\n{analysis}")
    
    if search_results:
        context_parts.append(f"Documentation findings:\n{search_results}")
    
    context_str = "\n\n".join(context_parts) if context_parts else "No current code context available."
    
    prompt = f"""You are a Phaser.js expert. Generate a specific, working code example for the user's request.

User Request: {user_message}

Context:
{context_str}

Requirements:
1. Provide ONLY working JavaScript/Phaser.js code
2. Include clear comments explaining each part
3. Make the code integrate well with existing code structure
4. Use Phaser.js best practices
5. Make it copy-paste ready
6. If modifying existing code, show the specific changes needed

Generate a practical code example that directly addresses the user's request:"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=prompt,
        input=user_message
    )

    return f"AI-generated code example:\n\n{response.output_text}"

def reasoning_step(context_list):
    """Perform reasoning step with accumulated context."""
    
    # Join context into a single string
    context_str = "\n\n".join(context_list)
    
    prompt = f"""You are the reasoning step of a Reasoning and Action agent. Your job is to analyze the user's request and determine the best course of action. You will not execute any actions, but will provide a clear reasoning for the next step.

Available tools:
- get_current_code: Get user's current game code
- analyze_code: Analyze code for issues and structure
- search_phaser_docs(query:[search term]): Find Phaser.js documentation 
- generate_code_example: Create code examples for features

Context from previous steps:
{context_str}

Format your response as follows:
Reasoning: [Use this section as a scratchpad for your reasoning]
Identify: [Try to identify the user's intent max 1 sentence] 
Tools_needed: [List the tools you need to use in order, separated by commas. If no more tools needed, write "none"]"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=prompt,
        input=context_str
    )
    
    return response


def generate_final_response(user_message, context_list, accumulated_data):
    """Generate the final response based on accumulated context and user message."""
    
    # Join context into a single string
    context_str = "\n\n".join(context_list)
    
    prompt = f"""You are the final response generator of a Reasoning and Action agent. Your job is to provide a clear, concise answer to the user's request based on the accumulated context.
Context from previous steps:
{context_str}
User Request: {user_message}

Generate a final response that summarizes the reasoning and provides a clear answer to the user's request. If code was generated, include it in the response.

Format your response as follows:
Final Response: [Your final answer here]
Confidence: [Your confidence in the answer from 0 to 1.0, where 1 is very confident]"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=prompt,
        input=context_str
    )
    
    
    return response

def count_tokens(content=""):
    encoding = tiktoken.get_encoding("o200k_base")
    tokens = encoding.encode(content)
    return len(tokens)