from flask import Flask, request, jsonify, render_template
import requests
from characters import *
app = Flask(__name__)

def get_response(prompt: str, character: str):
    data = {
  "messages": [
    {
      "content": "Placeholder1",
      "role": "system"
    },
    {
      "content": "placeholder",
      "role": "user"
    }
  ],
    "max_tokens": 800,
    "stop": ["<<SYS>>"]
    }
    data['messages'][1]['content'] = prompt
    data['messages'][0]['content'] = to_fine_tune[character]
    resp = requests.post("http://node2.lunes.host:6969/v1/chat/completions", json=data)
    return str(resp.json()['choices'][0]['message']['content']).replace(f"{character}:", "").replace("<<HUMAN>>", "Interviewer:").replace("<<SYS>>", f"{character}:")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    try:
        # Get the JSON data from the request body
        data = request.get_json()
        print(data)
        # Check if the 'message' key exists in the JSON data
        if 'message' in data:
            user_message = data['message']
            # Process the user_message with your AI model here

            # For demonstration purposes, let's echo the message back
            ai_response = get_response(user_message, data['character'])

            # Return the AI response as JSON
            return jsonify({"response": ai_response})

        else:
            return jsonify({"error": "Invalid request format"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
