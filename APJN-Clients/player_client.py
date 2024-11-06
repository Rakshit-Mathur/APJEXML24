import json
import socketio
import requests
import time
import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

# URL and Token
link = "http://127.0.0.1:5000"
token = input('Enter your token: ')
name = input('Enter your name: ')

# Initialize socket connection
sio = socketio.Client()
connected = False

# Connect to server
@sio.event
def connect():
    global connected
    connected = True
    print("Connected to server")
    sio.emit('request')

@sio.event
def disconnect():
    global connected
    connected = False
    print("Disconnected from server")
    os._exit(0)

@sio.on('reset')
def reset():
    print("Resetting")
    os._exit(0)

@sio.on('board')
def handle_server_message(data):
    if not connected:
        print("Not connected yet, ignoring message")
        return
    board, points = data
    process(board, points)

# Neural Network Model
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 512)
        self.fc2 = nn.Linear(512, 512)
        self.fc3 = nn.Linear(512, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Model Variables
input_dim = 498  
output_dim = 4 
dqn_model = DQN(input_dim, output_dim)
dqn_model.load_state_dict(torch.load('dqn_model.pth'))


def process(board, points):
    state = prepare_state(board, points)

    state_tensor = torch.FloatTensor(state).unsqueeze(0)  # Shape (1, input_dim)
    with torch.no_grad():
        action_values = dqn_model(state_tensor)
    action = torch.argmax(action_values).item()

    #Actions Array
    move = [0] * 4
    move[action] = 1

    # Log data and send move
    log_data(board, points, move)
    send_move(move)

def prepare_state(board, points):
    # Flatten or encode the board as needed, include points, etc.
    # Customize this function according to how your model expects the state
    state = np.array(board).flatten().tolist() + [points]
    return state

# Logging function
def log_data(board, points, move):
    data = {
        'board': board,
        'points': points,
        'move': move
    }
    with open('data.json', 'a') as f:
        f.write(json.dumps(data) + '\n')

# Send move to server
def send_move(move):
    url = f"{link}/move/player"
    headers = {'content-type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.post(url, json=move, headers=headers)
    print(response.text)

# Connect and wait for events
sio.connect(link, headers={'Authorization': f'Bearer {token}', 'Name': name})
sio.wait()
