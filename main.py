from flask import Flask, request, jsonify, render_template
import requests

import json
import websockets
from characters import *
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)
ws_url = "https://discord.com/api/webhooks/1162120808412479639/WQYw_dqR7wC8sLcPPPR-EPQO_9rU7WHQifbqOikW24jhizbxPYyY8hbQbNddSb4_eiM7"# obv not active 
nodes = [
	{"url": "http://node2.lunes.host:6969/v1/chat/completions", "queue": 0},
	{"url": "http://212.193.3.237:6969/v1/chat/completions", "queue": 0}
]

def get_least_busy_node():
	# Sort the nodes based on their "queue" values in ascending order
	sorted_nodes = sorted(nodes, key=lambda node: node["queue"])
	# The least busy node will be the first element in the sorted list
	return sorted_nodes[0]

def visitor(item, path):
    print(f"{item} at path {path}")
    

def get_response(prompt: str, character: str, ws):
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
		"max_tokens": 2000,
		"stream": True
	}
	data['messages'][1]['content'] = prompt
	data['messages'][0]['content'] = to_fine_tune[character]
	node_to_use = get_least_busy_node()
	for node in nodes:
		if node == node_to_use:
			node['queue'] += 1
			break
	print(node_to_use, nodes)
	response = requests.post(node_to_use['url'], json=data, stream=True)
	returned = ""
	data = ""
	i = 0
	for thing in response:
		decoded_line = thing.decode('utf-8')
		var = decoded_line.replace("data: ", "")
		if ": ping -" not in var and "{'role': 'assistant" not in var and "[DONE]" not in var:
			json_var = json.dumps(var)
			uwu = json.loads(json_var)
			print(uwu, 6)
			data += uwu
			i +=1
			if i >=2:
				try:
					print(data, 7)
					almost_last = json.loads(data)['choices'][0]['delta']
				except json.decoder.JSONDecodeError as e:
					print(3, e, data)
				try:
					print(almost_last,8)
					try:
						content = almost_last['content']
					except KeyError as e:
						content = ""
				except json.decoder.JSONDecodeError as e:
					print(4, e, almost_last)			
				ws.send(content)
				print(10000)
				returned += content
				i = 0
				data = ""
	ws.send("COMPLETE")
	node['queue'] -= 1
	requests.post(ws_url, json={"username": "Prompts", "content": f"`{prompt}`: {character}"})
	requests.post(ws_url, json={"username": "Result", "content": f"`{returned}`"})
	return returned

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

	app.run(host="0.0.0.0", debug=True)
