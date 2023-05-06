import openai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from ln import add_invoice, lookup_invoice
from util import price

# Load env vars
load_dotenv()
# Set up the OpenAI API credentials
openai.api_key = os.getenv('OPENAI_API_KEY')

# Set up the Flask app
app = Flask(__name__)

invoice_query = {
    "query": "What is the meaning of life?",
    "invoice": "lnbc..."
}

def generate_invoice(query):
    amount = price(query)
    result = add_invoice(amount, f"Query: {query}")
    # result contains the payment request and the r_hash
    return result

def check_payment(r_hash):
    # Call the OpenAI API to generate a response
    invoice = lookup_invoice(r_hash)
    # Extract the response text from the API response
    paid = invoice['settled']
    return paid

# standard chatgpt query
@app.route('/query', methods=['POST'])
def query_chatbot():
    # Parse the request data
    data = request.get_json()
    query = data['query']

    # check if we're in the middle of a payment 
    if 'r_hash' in data:
        r_hash = data['r_hash']
        paid = check_payment(r_hash)
        if paid:
            # Call the OpenAI API to generate a response
            summary = openai.Completion.create(
                # davinci is the standard gpt3 model
                model="davinci",
                prompt=query,
                max_tokens=len(query),
                n=1,
                stop=None,
                temperature=0.7,
            )

            # Extract the response text from the API response
            message = summary.choices[0].text.strip()

            # Return the response to the client
            response = jsonify({'message': message})
            response.status_code = 200
            return response
        else:
            # Return the response to the client
            invoice = generate_invoice(query)
            response = jsonify({'message': 'Payment Required', 'invoice': invoice})
            response.status_code = 402
            return response


# TODO: send file data in request 
# translate audio files (TODO: list which audio types are supported)
# @app.route('/audio', methods=['GET'])
# def summarize_audio():
#     # Parse the request data
#     data = request.get_json()
#     query = data['query']

#     # Call the OpenAI API to generate a response
#     f = open("testfile.mp3", "rb")
#     transcript = openai.Audio.transcribe("whisper-1", f)
#     prompt = f"Summarize the following text: {transcript}"
#     summary = openai.Completion.create(
#         engine="text-davinci-002",
#         prompt=prompt,
#         max_tokens=60,
#         n=1,
#         stop=None,
#         temperature=0.7,
#     )


#     # Extract the response text from the API response
#     message = summary.choices[0].text.strip()

#     # Return the response to the client
#     return jsonify({'message': message})



# Start the Flask app on localhost:5000
if __name__ == '__main__':
    app.run(debug=True)