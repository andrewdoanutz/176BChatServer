import socket
import select
import sys
import thread
import os
from Crypto.Cipher import AES

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

filerecvserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
filerecvserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

filesendserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
filesendserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

if len(sys.argv) != 6:
    print ("Correct usage: script, IP address, port number, filesendport, filerecvport, keyfile")
    exit()

IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
Port2 = int(sys.argv[3])
Port3 = int(sys.argv[4])
keyfile = str(sys.argv[5])
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

filerecvserver.bind((IP_address, Port2))
filerecvserver.listen(100)

filesendserver.bind((IP_address, Port3))
filesendserver.listen(100)

list_of_clients = []

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

def getFile(conn, addr):
    filename = ""
    filename = str(decrypt_message(conn.recv(16)))
    # conn.send(encrypt_message(str(Port2)))
    # newconn, newaddr = fileserver.()

    print("receiving " + filename)
    filename='(copy)'+filename
    print("receiving " + filename)
    with open(filename, 'wb') as f:
        data = conn.recv(1040)
        while data:
            data = decrypt_message(data)
            print('receiving data...')
            # data = decrypt_message(conn.recv(1040))
            # if data[-12:]=="done sending":
                # break
            f.write(data)
            data = conn.recv(1040)
    conn.close()
    sys.exit()

def sendFile(conn, addr):
    # conn.send(filename)
    filename = decrypt_message(conn.recv(1040))
    try:
        f = open(filename,'rb')
    except:
        conn.send(encrypt_message("file DNE"))
        conn.close()
        sys.exit()

    l = f.read(1024)
    while (l):
       conn.send(encrypt_message(l))
       print("Sent %r",repr(l))
       l = f.read(1024)
    f.close()
    print("done sending")
    conn.close()
    # conn.send("done sending")




def clientthread(conn, addr):
    encrypted_intro = encrypt_message(intromessage)
    conn.send(encrypted_intro)

    while True:
            try:
                message = conn.recv(2080)
                message = decrypt_message(message)
                if message[0:9] == "send file":
                    filename=decrypt_message(conn.recv(1040))
                    conn.send(encrypt_message(str(Port2)))
                    # print("here")
                    # getFile(conn,filename)
                    # print("got file")
                    broadcast(encrypt_message("file " + filename + " sent"), conn)
                    #broadcastFile("received_file",conn)
                elif message[0:8] == "get file":
                    conn.send(encrypt_message(str(Port3)))
                    # print("here1")
                    # print(message)
                    # filename = decrypt_message(conn.recv(1024))
                    # print("here2")

                elif message:
                    print ("<" + addr[0] + "> " + message)
                    message_to_send = "<" + addr[0] + "> " + message
                    message_to_send = encrypt_message(message_to_send)
                    broadcast(message_to_send, conn)
                else:
                    remove(conn)

            except:
                continue

def filerecv():
    while True:
        fileconn, fileaddr = filerecvserver.accept()
        thread.start_new_thread(getFile, (fileconn, fileaddr))

def filesend():
    while True:
        fileconn, fileaddr = filesendserver.accept()
        thread.start_new_thread(sendFile, (fileconn, fileaddr))

def broadcast(message, connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:
                clients.send(message)
            except:
                clients.close()
                remove(clients)

def broadcastFile(filename,conn):
    for clients in list_of_clients:
        if clients!=conn:
            try:
                sendFile(filename,clients)
            except:
                clients.close()
                remove(clients)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)



thread.start_new_thread(filerecv, ())
thread.start_new_thread(filesend, ())

while True:
    #chat
    conn, addr = server.accept()
    list_of_clients.append(conn)
    print (addr[0] + " connected")
    thread.start_new_thread(clientthread,(conn,addr))
    #file transfer



conn.close()
server.close()
