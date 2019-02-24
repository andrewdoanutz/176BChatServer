import socket
import select
import sys
from Crypto.Cipher import AES

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 4:
    print ("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))


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

def encrypt_message(message):
	#modify to always work even with non-16 length stuff
	message = message + (16 - (len(message) % 16)) * chr(16 - len(message) % 16)
	encryptor = AES.new(key)
        print(len(message))
	text = encryptor.encrypt(message)
	return text

def decrypt_message(text):
	decryptor = AES.new(key)
	message = decryptor.decrypt(text)
	message = message[: (-1 * ord(message[len(message)-1]))]
	return message


def getFile(conn):

    filename=conn.read(1024)+'2'

    #filename="filelul.txt"
    with open(filename, 'wb') as f:
        while True:
            print('receiving data...')
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)


def sendFile(conn,filename):
    conn.send(encrypt_message(filename))
    f = open(filename,'rb')
    l = f.read(1024)
    while (l):
       conn.send(encrypt_message(l))
       print("Sent: %r" % repr(l))
       l = f.read(1024)
    f.close()





while True:

    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            # print(message)
            message = decrypt_message(message)
            print (message)
        else:
            message = sys.stdin.readline()
            if message[0:9]=='send file':
                message = encrypt_message(message)
                server.send(message)
                print("Enter filename")
                filename=sys.stdin.readline()
                filename=filename[:-1]
                sendFile(server,filename)
                server.send(encrypt_message("done sending"))
            else:
                sys.stdout.write("<You>")
                sys.stdout.write(message)
                message = encrypt_message(message)
                server.send(message)
                sys.stdout.flush()
server.close()
