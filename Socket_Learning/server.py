import socket
import threading



HEADER = 64 # header size # how many bytes we are going to send
PORT = 5050 # choosing our port to use # must be opening port
SERVER = socket.gethostbyname(socket.gethostname()) # Gives u the local ip Address for ur computer
ADDR = (SERVER, PORT) # tuple of server and port
FORMAT = 'utf-8' # encoding format (string format)
DISCONNECT_MESSAGE = "!DISCONNECT" # message to disconnect the client

# creating a socket object 
# socket.AF_INET - address family => IPv4 meaning that we are using the protocol IPv4 over this connection
# socket.SOCK_STREAM - meaning that we are using TCP protocol 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
 # binding the server to the address meaning that anything that comes to this address will
 # be handled by this server
server.bind(ADDR)


def handle_client(conn, addr):
    #can u display the name of the device that is connected
    print(f"[NEW CONNECTION] {addr} connected.") # printing the address of the client
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT) # receiving the message from the client
        if msg_length: # if the message is empty
            msg_length = int(msg_length) # make it an integer
            msg = conn.recv(msg_length).decode(FORMAT) # receiving the message from the client with the length of msg_length
            print(f"[{addr}] {msg}") # printing the message from the client
            if msg == DISCONNECT_MESSAGE: # if the message is the disconnect message
                connected = False # disconnect the client
                print(f"[{addr}] disconnected.")
                #update the Active connections
                conn.close() # close the connection

def start():
    server.listen() # server is listening for connections
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT}")
    while True:
        conn, addr = server.accept() # accepting a connection #addr is the port of the client
        thread = threading.Thread(target=handle_client, args=(conn, addr)) # creating a thread to handle the client
        thread.start() # starting the thread
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}") # printing the number of active connections

print("[STARTING] server is starting...")
start() # starting the server