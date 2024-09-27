from flask import Flask, render_template, request, jsonify, session
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.secret_key = 'supersecretkey'  # Needed for session management

# Azure OpenAI key and URL setup (You can replace this with OpenAI's official API if needed)
OPEN_AI_KEY = "1a59b268be394006a33883dd2f7219a3"  # Azure OpenAI API key
OPEN_AI_URL = "https://dev-open-ai-sherpa.openai.azure.com/openai/deployments/gpt-3/completions?api-version=2022-12-01"

# Set NewsAPI URL and Key
NEWS_API_KEY = "6f61c4536a214fc287ca31f6125b65b2"
NEWS_API_URL = "https://newsapi.org/v2/everything"

# Wikipedia summary URL
WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{query}"

# Inventory and payments data
inventory = {
    "neon air jordans": {
        "10": {"store": "Utrecht", "price": 120, "availability": True},
        "9": {"store": "Rotterdam", "price": 110, "availability": True},
    },
    "classic adidas": {
        "11": {"store": "Amsterdam", "price": 100, "availability": True},
        "8": {"store": "Hague", "price": 90, "availability": True},
    }
}
payments = {
    "receipt001": {"confirmed": True, "amount": 130},
    "receipt002": {"confirmed": True, "amount": 110},
    "receipt003": {"confirmed": True, "amount": 140},
    "receipt004": {"confirmed": True, "amount": 90}
}

# Helper function to reset conversation state
def reset_state():
    session['step'] = 'init'
    session['shoe_model'] = ''
    session['size'] = ''
    session['price'] = 0
    session['store'] = ''
    session['address'] = ''
    session['total_cost'] = 0

# Function to get news from NewsAPI
def get_news(query):
    try:
        params = {'q': query, 'apiKey': NEWS_API_KEY, 'sortBy': 'relevancy', 'language': 'en'}
        response = requests.get(NEWS_API_URL, params=params)
        if response.status_code == 200:
            news_data = response.json()
            if news_data['totalResults'] > 0:
                top_article = news_data['articles'][0]
                return f"Latest news on {query}: {top_article['title']}. Read more: {top_article['url']}"
            else:
                return f"Sorry, no news found about {query}."
        else:
            return "Error retrieving news. Please try again later."
    except Exception as e:
        return f"Error occurred while fetching news: {str(e)}"

# Function to get Wikipedia summary
def get_wikipedia_summary(query):
    try:
        summary_url = WIKI_SUMMARY_URL.format(query=query.replace(' ', '_'))
        response = requests.get(summary_url)
        data = response.json()

        if "extract" in data:
            return data['extract']
        else:
            return None  # Return None so it can fall back to OpenAI
    except Exception as e:
        return f"Error occurred while fetching Wikipedia info: {str(e)}"

# Function to call Azure OpenAI API for fallback
def get_openai_response(message, context=''):
    headers = {
        "Content-Type": "application/json",
        "api-key": OPEN_AI_KEY
    }
    prompt = f"You are an intelligent assistant helping with {context}. Answer the following query: {message}"
    data = {
        "prompt": prompt,
        "max_tokens": 150,
        "n": 1,
        "stop": None,
        "temperature": 0.5  # Lowered temperature for more factual responses
    }
    response = requests.post(OPEN_AI_URL, headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['choices'][0]['text'].strip()
    else:
        return "Sorry, I couldn't generate a response at the moment."

# Reset state when starting the app
@app.route("/")
def index():
    reset_state()  # Always reset conversation state when accessing index
    return render_template("index.html")

# Simulated shoe purchase use case
@app.route("/api", methods=["POST"])
def api():
    try:
        message = request.json.get("message").lower()
        print(f"Received message: {message}")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Simple greetings
        if message in ["hi", "hello", "hey", "what's up", "how are you"]:
            return jsonify({"response": "Hey there! How can I help you today?"})

        # Check for news-related queries
        elif "news" in message:
            query = message.split("about")[-1].strip()
            news_response = get_news(query)
            return jsonify({"response": news_response})

        # Wikipedia queries
        elif "tell me about" in message or "what is" in message:
            query = message.split("about")[-1].strip() if "about" in message else message.split("is")[-1].strip()
            wiki_summary = get_wikipedia_summary(query)
            if wiki_summary:
                return jsonify({"response": wiki_summary})
            else:
                openai_response = get_openai_response(query, "general knowledge")
                return jsonify({"response": openai_response})

        # Sales process: Step 1 - Starting the conversation
        if session.get('step') == 'init':
            reset_state()
            session['step'] = 'ask_model_or_color'
            return jsonify({"response": "Do you have a specific model in mind or a preferred color?"})

        # Step 2: User provides model or color
        elif session.get('step') == 'ask_model_or_color':
            matching_models = [model for model in inventory.keys() if model in message]
            if matching_models:
                session['shoe_model'] = matching_models[0]  # Get the first matching model
                session['step'] = 'ask_size'
                return jsonify({"response": "What size would you like?"})
            else:
                return jsonify({"response": "Sorry, we don't have that model. You can choose between Neon Air Jordans or Classic Adidas."})

        # Step 3: User provides shoe size
        elif session.get('step') == 'ask_size':
            if session['shoe_model'] in inventory and message in inventory[session['shoe_model']]:
                shoe_data = inventory[session['shoe_model']][message]
                session['size'] = message
                session['price'] = shoe_data['price']
                session['store'] = shoe_data['store']
                session['total_cost'] = session['price'] + 10  # Adding shipping fee of 10 Euros
                session['step'] = 'confirm_purchase'
                return jsonify({"response": f"This model and size is available at the {session['store']} store and costs {session['price']} Euros. Would you like to go ahead with the purchase?"})
            else:
                return jsonify({"response": "Sorry, we don't have that size in stock."})

        # Step 4: Confirm purchase
        elif session.get('step') == 'confirm_purchase':
            if "yes" in message:
                session['step'] = 'ask_address'
                return jsonify({"response": "Please provide your shipping address."})
            else:
                reset_state()
                return jsonify({"response": "Thank you for shopping with us!"})

        # Step 5: User provides address
        elif session.get('step') == 'ask_address':
            session['address'] = message
            session['step'] = 'ask_billing'
            return jsonify({"response": f"The total cost including shipping is {session['total_cost']} Euros. Would you like to proceed to payment?"})

        # Step 6: Confirm billing
        elif session.get('step') == 'ask_billing':
            if any(word in message for word in ["yes", "sure", "absolutely", "great"]):
                session['step'] = 'payment'
                return jsonify({"response": "Please follow the link to complete your purchase: link1.com. Once completed, provide the receipt number."})
            else:
                reset_state()
                return jsonify({"response": "Thank you for shopping with us!"})

        # Step 7: Validate receipt and confirm order
        elif session.get('step') == 'payment':
            receipt = message
            if receipt in payments and payments[receipt]['confirmed']:
                reset_state()
                return jsonify({"response": "Payment confirmed! Your order has been placed successfully. Thank you for shopping with us!"})
            else:
                return jsonify({"response": "Invalid receipt number. Please try again."})

        # Fallback to OpenAI for general queries
        else:
            openai_response = get_openai_response(message, "general assistant")
            return jsonify({"response": openai_response})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": f"Internal Server Error: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
