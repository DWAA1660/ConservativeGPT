from flask import Flask, request, jsonify, render_template
import requests
import json
import argparse

from llama_cpp import Llama

import websockets
from characters import *
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)
ws_url = "https://discord.com/api/webhooks/1162120808412479639/WQYw_dqR7wC8sLcPPPR-EPQO_9rU7WHQifbqOikW24jhizbxPYyY8hbQbNddSb4_eiM7"# obv not active 
nodes = [
	{"url": "http://node5.lunes.host:5000/v1/chat/completions", "queue": 0}
]

def get_least_busy_node():
	# Sort the nodes based on their "queue" values in ascending order
	sorted_nodes = sorted(nodes, key=lambda node: node["queue"])
	# The least busy node will be the first element in the sorted list
	return sorted_nodes[0]

def visitor(item, path):
    print(f"{item} at path {path}")
    

def get_response(prompt: str, character: str, ws):

	parser = argparse.ArgumentParser()
	parser.add_argument("-m", "--model", type=str, default="Wizard-Vicuna30B-UncensoredQ4ks.gguf")
	args = parser.parse_args()

	llm = Llama(model_path=args.model, n_threads=48)

	stream = llm(
		f"{to_fine_tune[character]} Question: {prompt} Answer: ",
		max_tokens=4800,
		stop=[],
		stream=True,
	)

	for output in stream:
		text = json.dumps(output)
		print(text, type(text))
		text_json = json.loads(text)
		print(text_json, type(text_json))
		content = text_json['choices'][0]['text']
		ws.send(content)

	# ws.send("COMPLETE")
	# node['queue'] -= 1
	# requests.post(ws_url, json={"username": "Prompts", "content": f"`{prompt}`: {character}"})
	# requests.post(ws_url, json={"username": "Result", "content": f"`{returned}`"})
	# return returned

@app.route("/", methods=["GET"])
def index():
	return render_template("index.html")

@sock.route('/ai-chat')
def echo(ws):
    while True:
        
        data = ws.receive()
        real_data = json.loads(data)
        get_response(real_data['message'], real_data['character'], ws)

if __name__ == '__main__':

	app.run(host="0.0.0.0", port=5001, debug=True)

