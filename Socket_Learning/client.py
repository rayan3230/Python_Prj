import socket


HEADER = 64 
PORT = 5050 
SERVER = '192.168.100.250'
ADDR = (SERVER, PORT) 
FORMAT = 'utf-8' 
DISCONNECT_MESSAGE = "!DISCONNECT" 

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT) 
    msg_length = len(message) # get length of the message
    send_length = str(msg_length).encode(FORMAT) #encode the length of the message to send it 
    send_length += b' ' * (HEADER - len(send_length)) # adding padding to the length of the message to make it equal to HEADER size
    client.send(send_length) 
    client.send(message)

#make it interactive
while True:
    msg = input("Enter message to send to server (or type '!DISCONNECT' to quit): ")
    send(msg)
    if msg == DISCONNECT_MESSAGE:
        break
send(DISCONNECT_MESSAGE)