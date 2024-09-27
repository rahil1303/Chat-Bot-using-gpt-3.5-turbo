from flask import session, jsonify

# Simulated shoe inventory with 4 shoes and their sizes, availability, and store locations
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

# Simulated payment data with 4 receipts for testing
payments = {
    "receipt001": {"confirmed": True, "amount": 130},
    "receipt002": {"confirmed": True, "amount": 110},
    "receipt003": {"confirmed": True, "amount": 140},
    "receipt004": {"confirmed": True, "amount": 90}
}

def reset_state():
    session['step'] = 'init'
    session['shoe_model'] = ''
    session['size'] = ''
    session['price'] = 0
    session['store'] = ''
    session['address'] = ''
    session['total_cost'] = 0

# Function to handle shoe sales conversation
def handle_sales(message):
    if session.get('step') == 'init':
        reset_state()
        session['step'] = 'ask_model_or_color'
        return jsonify({"response": "Do you have a specific model in mind or colour?"})

    elif session.get('step') == 'ask_model_or_color':
        matching_models = [model for model in inventory.keys() if model in message]
        if matching_models:
            session['shoe_model'] = matching_models[0]
            session['step'] = 'ask_size'
            return jsonify({"response": "What would be your size?"})
        else:
            return jsonify({"response": "I'm sorry, we don't have that model. Please choose from Neon Air Jordans or Classic Adidas."})

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
            return jsonify({"response": "Sorry, we don't have that size in stock. Please let me know if you'd like to try a different size or model."})

    elif session.get('step') == 'confirm_purchase':
        if "yes" in message:
            session['step'] = 'ask_address'
            return jsonify({"response": "Can you give me your address where the order is supposed to be shipped?"})
        else:
            reset_state()
            return jsonify({"response": "Sorry to see you leave. Let me know if there's anything else I can help with."})

    elif session.get('step') == 'ask_address':
        session['address'] = message
        session['step'] = 'ask_billing'
        return jsonify({"response": f"The total cost including shipping is {session['total_cost']} Euros. Would you like to proceed to billing?"})

    elif session.get('step') == 'ask_billing':
        if any(word in message for word in ["yes", "sure", "absolutely", "great"]):
            session['step'] = 'payment'
            return jsonify({"response": "Please follow the link to complete your purchase: link1.com. Once you've completed the payment, provide the receipt number."})
        else:
            reset_state()
            return jsonify({"response": "Thank you for visiting! Let me know if you need help with anything else."})

    elif session.get('step') == 'payment':
        receipt = message
        if receipt in payments and payments[receipt]['confirmed']:
            reset_state()
            return jsonify({"response": "Payment confirmed! Your order has been placed successfully. Thank you for shopping with us!"})
        else:
            return jsonify({"response": "Sorry, the receipt number you provided is invalid. Please try again."})
