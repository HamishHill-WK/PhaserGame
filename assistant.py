from openai import OpenAI
import os
# import tiktoken

# Get the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Check if it exists
if not api_key:
    print("API key not found!")

client = OpenAI()

def get_response(user_message=""):
    code =  get_gamescript()
    
    response = client.responses.create(
        model="gpt-4.1-mini",
        input="Write a brief explanation of hello world in JavaScript. Include a simple code example.",
    )
    return response

def get_gamescript():
    try:
        with open("static/js/game.js", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "Error: game.js file not found"
    except Exception as e:
        return f"Error reading game.js: {e}"
    

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