import requests
import os

# Your Azure OpenAI key and endpoint from the email
# Retrieve the API key and URL from environment variables
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
OPEN_AI_URL = os.getenv("OPEN_AI_URL")

def get_openai_response(message):
    headers = {
        "Content-Type": "application/json",
        "api-key": OPEN_AI_KEY  # Use `api-key` for Azure OpenAI instances
    }
    
    data = {
        "prompt": message,  
        "max_tokens": 50,  
        "temperature": 0.5,  
        "top_p": 0.9,  
        "frequency_penalty": 0.2,  
        "presence_penalty": 0.2  
    }
    
    try:
        response = requests.post(OPEN_AI_URL, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for non-200 responses
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['text'].strip()
        else:
            return "Sorry, I couldn't generate a response at the moment."
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "There was an error with the OpenAI API request."
