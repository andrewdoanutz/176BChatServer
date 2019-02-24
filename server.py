import socket
import select
import sys
import thread
import os
from Crypto.Cipher import AES


def encrypt_message(message):
	#modify to always work even with non-16 length stuff
	message = message + (16 - (len(message) % 16)) * chr(16 - len(message) % 16)
	encryptor = AES.new(key)
	text = encryptor.encrypt(message)
	return text

def decrypt_message(text):
	decryptor = AES.new(key)
	message = decryptor.decrypt(text)
	message = message[: (-1 * ord(message[len(message)-1]))]
	return message

def getFile(conn,filename):
    filename='(copy)'+filename
    with open(filename, 'wb') as f:
        while True:
            print('receiving data...')
            data = decrypt_message(conn.recv(1040))
            if data[-12:]=="done sending":
                break
            f.write(data)
    f.close()


def sendFile(conn,filename):
    conn.send(filename)

    f = open(filename,'rb')
    l = f.read(1024)
    while (l):
       conn.send(l)
       print("Sent %r",repr(l))
       l = f.read(1024)
    f.close()

    conn.send("done sending")



def clientthread(conn, addr):
    username = conn.recv(2048)
    username=decrypt_message(username)
    chatrooms[0].append((conn,username))
    currentRoom=0
    conn.send(encrypt_message("Welcome to this chatroom!\n"+"Current chatroom: "+str(currentRoom)+"\n"+"Range of chatrooms: 0-"+str((len(chatrooms)-1))))
    while True:
            try:
                message = conn.recv(2048)
                message = decrypt_message(message)
                
                if message[0:9] == "send file":
                    filename=decrypt_message(conn.recv(1024))
                    print("here")
                    getFile(conn,filename)
                    print("got file")
                    broadcast(encrypt_message("file " + filename + " sent by "+addr[0]), conn,currentRoom)
                    #broadcastFile("received_file",conn)
                elif message[0:8] == "get file":
                    filename = decrypt_message(conn.recv(1024))
                    print("here2")
                elif message[0:13]=="make chatroom":
                    chatrooms[currentRoom].remove((conn,username))
                    chatrooms.append([(conn,username)])
                    currentRoom=len(chatrooms)-1
                    conn.send(encrypt_message("Current chatroom: "+str(currentRoom)+"\n"+"Range of chatrooms: 0-"+str((len(chatrooms)-1))))
                    broadcastAll(encrypt_message("New chatroom "+str(len(chatrooms)-1)+" created"),conn)
                elif message[0:13]=="join chatroom":
                    roomnum=int(message[13:])
            
                    #try:
                    chatrooms[currentRoom].remove((conn,username))
                    chatrooms[roomnum].append((conn,username))
                    currentRoom=roomnum
                    conn.send(encrypt_message("Current chatroom: "+str(currentRoom)+"\n"+"Range of chatrooms: 0-"+str((len(chatrooms)-1))))
                    #except:
                        #conn.send(encrypt_message("Chatroom does not exist"))
                elif message:
                    print ("<" + username + "> " + message)
                    message_to_send = "<" + username + "> " + message
                    message_to_send = encrypt_message(message_to_send)
                    broadcast(message_to_send, conn,currentRoom)
                else:
                    remove(conn,chatrooms[currentRoom])
                    remove(conn,list_of_clients)

            except:
                continue

def broadcast(message, connection,roomNum):
    for clients,username in chatrooms[roomNum]:
        if clients!=connection:
            try:
                clients.send(message)
            except:
                clients.close()
                remove(clients,chatrooms[roomNum])
                remove(clients,list_of_clients)

def broadcastAll(message,connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:
                clients.send(message)
            except:
                clients.close()
                remove(clients,list_of_clients)

def remove(connection,curList):
    if connection in curList:
        curList.remove(connection)

# sometext = "hello, I'm a fnonucasfdasfdasd"
# interim = encrypt_message(sometext)
# testtext = decrypt_message(interim)
# print(testtext)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

if len(sys.argv) != 4:
    print ("Correct usage: script, IP address, port number, keyfile")
    exit()

IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
keyfile = str(sys.argv[3])
key = ""
try:
	file = open(keyfile, "r")
	key = file.readline()
	file.close()
except:
	print("keyfile generated")
	key = os.urandom(16)
	file = open(keyfile, "w")
	file.write(key)
	file.close()


intromessage = "Welcome to this chatroom!"


server.bind((IP_address, Port))
server.listen(100)

list_of_clients = []
chatrooms=[[]]

while True:
    conn, addr = server.accept()
    list_of_clients.append(conn)
    print (addr[0] + " connected")
    thread.start_new_thread(clientthread,(conn,addr))

conn.close()
server.close()
