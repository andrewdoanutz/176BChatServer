import socket
import select
import sys
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


def getFile(conn, filename):
    #filename="filelul.txt"
    conn.send(encrypt_message("get file"))
    new_port = int(decrypt_message(conn.recv(1040)))
    fileserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fileserver.connect((IP_address, new_port))
    fileserver.send(encrypt_message(filename))

    filename = '(recv)' + filename
    with open(filename, 'wb') as f:
        data = fileserver.recv(1040)
        while data:
            print('receiving data...')
            data = decrypt_message(data)
            if (data == "file DNE"):
                f.close()
                print("file DNE")
                return
            f.write(data)
            data = fileserver.recv(1040)
    fileserver.close()


def sendFile(conn,filename):
    try:
        f = open(filename,'rb')
    except:
        print("file does not exist")
        return
    conn.send(encrypt_message("send file"))
    conn.send(encrypt_message(filename))
    new_port = int(decrypt_message(conn.recv(1040)))
    fileserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fileserver.connect((IP_address, new_port))
    fileserver.send(encrypt_message(filename))
    l = f.read(1024)
    print("herre")
    while (l):
        print("heere")
        fileserver.send(encrypt_message(l))
        print("Sent: %r" % repr(l))
        l = f.read(1024)
    f.close()
    # fileserver.shutdown(socket.SHUT_RDWR)
    fileserver.close()


print("Enter a username:\n")
username= sys.stdin.readline()
username=username[:-1]
print("stored "+username+" as username")

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

server.send(encrypt_message(username))

while True:

    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2080)
            message = decrypt_message(message)
            print (message)
        else:
            message = sys.stdin.readline()
            if message[0:9]=='send file':
                # message = encrypt_message(message)
                # server.send(message)
                print("Enter filename")
                filename=sys.stdin.readline()
                filename=filename[:-1]
                sendFile(server,filename)
            elif message[0:8] == 'get file':
                print("Enter filename")
                filename = sys.stdin.readline()
                filename = filename[:-1]
                getFile(server, filename)
                # server.send(encrypt_message("done sending"))
                # print("File Sent")
            elif message[0:13]=="make chatroom" or message[0:13]=="join chatroom":
                message = encrypt_message(message)
                server.send(message)

            else:
                sys.stdout.write("<" + username + "> ")
                sys.stdout.write(message)
                message = encrypt_message(message)
                server.send(message)
                sys.stdout.flush()
server.close()
