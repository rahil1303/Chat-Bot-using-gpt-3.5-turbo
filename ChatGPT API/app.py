import os
import pickle
import pandas as pd
import re
import tiktoken  # OpenAI's tokenizer for token counting
from flask import Flask, request, jsonify
from flask_cors import CORS
from news import get_news
from wikipedia import get_wikipedia_summary
from openai_fallback import get_openai_response
from rohit_facts import get_rohit_fact, get_random_fact

# Load MS Dhoni trained model
with open('ms_dhoni_model.pkl', 'rb') as model_file:
    ms_dhoni_model = pickle.load(model_file)

# Load MS Dhoni facts dataset
dhoni_facts_df = pd.read_excel('MS_Dhoni_Facts.xlsx')

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.secret_key = 'supersecretkey'

# History file path
history_file = 'conversation_history.txt'

# Pricing details for Azure OpenAI (Modify as per your actual pricing)
PRICE_PER_1000_TOKENS = 0.02  # Example cost for GPT-3.5-turbo in Azure OpenAI

def preprocess_query(query):
    # Preprocess query by lowercasing and removing special characters
    query = query.lower()
    query = re.sub(r'[^\w\s]', '', query)  # Remove punctuation
    return query

# Function to log the conversation in a text file, including tokens and cost
def log_conversation(user_message, bot_response, tokens_used=None, cost=None):
    with open(history_file, 'a') as file:
        file.write(f"User: {user_message}\n")
        file.write(f"Bot: {bot_response}\n")
        if tokens_used is not None and cost is not None:
            file.write(f"Tokens used: {tokens_used}\n")
            file.write(f"Estimated cost: ${cost:.6f}\n")
        file.write("-" * 50 + "\n")

# Function to calculate tokens and cost
def calculate_tokens_and_cost(message, response):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    # Calculate tokens for the user's message and the bot's response
    tokens_used = len(encoding.encode(message)) + len(encoding.encode(response))
    
    # Calculate cost (assuming price is per 1000 tokens)
    cost = (tokens_used / 1000) * PRICE_PER_1000_TOKENS
    
    return tokens_used, cost

# Route to handle chatbot API requests
@app.route("/api", methods=["POST"])
def api():
    try:
        message = request.json.get("message").lower().strip()
        print(f"Received message: {message}")
        
        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Check for simple greetings
        if message in ["hi", "hello", "hey", "what's up", "how are you"]:
            response = "Hey there! How can I help you today?"
            tokens_used, cost = calculate_tokens_and_cost(message, response)
            log_conversation(message, response, tokens_used, cost)
            return jsonify({"response": response, "tokens_used": tokens_used, "estimated_cost": cost})

        # Check for Rohit Sharma fact requests
        if "rohit sharma" in message and "fact" in message:
            fact_response = get_random_fact() if "random" in message else get_rohit_fact(1)
            tokens_used, cost = calculate_tokens_and_cost(message, fact_response)
            log_conversation(message, fact_response, tokens_used, cost)
            return jsonify({"response": fact_response, "tokens_used": tokens_used, "estimated_cost": cost})

        # Check for MS Dhoni-related questions
        if "dhoni" in message:
            processed_query = preprocess_query(message)
            predicted_fact_index = ms_dhoni_model.predict([processed_query])[0]
            predicted_fact_text = dhoni_facts_df.loc[dhoni_facts_df['Fact Number'] == predicted_fact_index, 'Fact'].values[0]
            tokens_used, cost = calculate_tokens_and_cost(message, predicted_fact_text)
            log_conversation(message, predicted_fact_text, tokens_used, cost)
            return jsonify({"response": predicted_fact_text, "tokens_used": tokens_used, "estimated_cost": cost})

        # Check for news requests
        if "news" in message or "latest" in message:
            topic = message.replace("news", "").strip()
            news_response = get_news(topic)
            if news_response:
                tokens_used, cost = calculate_tokens_and_cost(message, news_response)
                log_conversation(message, news_response, tokens_used, cost)
                return jsonify({"response": news_response, "tokens_used": tokens_used, "estimated_cost": cost})
            else:
                response = f"Sorry, no news found on {topic}."
                tokens_used, cost = calculate_tokens_and_cost(message, response)
                log_conversation(message, response, tokens_used, cost)
                return jsonify({"response": response, "tokens_used": tokens_used, "estimated_cost": cost})

        # Check for Wikipedia summary requests
        if "what is" in message or "who is" in message or "tell me about" in message:
            query = message.replace("what is", "").replace("who is", "").replace("tell me about", "").strip()
            wiki_response = get_wikipedia_summary(query)
            if wiki_response:
                tokens_used, cost = calculate_tokens_and_cost(message, wiki_response)
                log_conversation(message, wiki_response, tokens_used, cost)
                return jsonify({"response": wiki_response, "tokens_used": tokens_used, "estimated_cost": cost})
            else:
                response = f"Sorry, I couldn't find information about {query}."
                tokens_used, cost = calculate_tokens_and_cost(message, response)
                log_conversation(message, response, tokens_used, cost)
                return jsonify({"response": response, "tokens_used": tokens_used, "estimated_cost": cost})

        # Fallback to OpenAI for all other queries
        openai_response = get_openai_response(message)
        tokens_used, cost = calculate_tokens_and_cost(message, openai_response)
        log_conversation(message, openai_response, tokens_used, cost)
        return jsonify({"response": openai_response, "tokens_used": tokens_used, "estimated_cost": cost})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": f"Internal Server Error: {e}"}), 500

# Endpoint to retrieve the conversation history from the text file
@app.route("/history", methods=["GET"])
def get_history():
    try:
        with open(history_file, 'r') as file:
            history_content = file.read()
        return jsonify({"history": history_content})
    except FileNotFoundError:
        return jsonify({"history": "No history available yet."})

if __name__ == '__main__':
    app.run(debug=True)
