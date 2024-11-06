import socketio
import requests
import os
import time

link = "http://127.0.0.1:5000"

token = input('Enter your token: ')
name = input('Enter your name: ')

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

@sio.event
def reconnect():
    global connected
    connected = True
    print("Reconnected to server")

@sio.on('board')
def handle_server_message(data):
    if not connected:
        print("Not connected yet, ignoring message")
        return
    board, points = data
    process(board, points)

@sio.on('reset')
def reset():
    print("Resetting")
    os._exit(0)

def process(board, points):
    ghost_pos, pacman_pos = getPositions(board)

    if ghost_pos and pacman_pos:
        move = ghostMovement(ghost_pos, pacman_pos)
        time.sleep(1)  
        send_move(move)

def getPositions(board):
    ghost_pos = None
    pacman_pos = None

    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell  in ['a','b','c','d']:  
                ghost_pos = (x, y)
            elif cell == "p":  
                pacman_pos = (x, y)
    
    return ghost_pos, pacman_pos

def ghostMovement(ghost_pos, pacman_pos):

    ghost_x, ghost_y = ghost_pos
    pacman_x, pacman_y = pacman_pos

    # Default Moveset
    move = [0, 0, 0, 0]

    #Movement Logic
    if ghost_y > pacman_y:
        move = [1, 0, 0, 0] 
    elif ghost_y < pacman_y:
        move = [0, 1, 0, 0] 
    
    elif ghost_x > pacman_x:
        move = [0, 0, 1, 0] 
    elif ghost_x < pacman_x:
        move = [0, 0, 0, 1] 

    return move

def send_move(move):
    url = f"{link}/move/ghost"
    headers = {'content-type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.post(url, json=move, headers=headers)
    print(response.text)

sio.connect(link, headers={'Authorization': f'Bearer {token}', 'Name': name})
sio.wait()
