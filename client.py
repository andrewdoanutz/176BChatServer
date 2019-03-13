import socket
import select
import sys
import os
from Crypto.Cipher import AES
import Tkinter
import thread

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

def sendMessage(username,server,message,msg_list):
    msg_list.insert(Tkinter.END,"<"+username+"> "+message)
    message = encrypt_message(message)
    server.send(message)


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

#GUI methods
def sendFileFunc(message):
    sendFile(server,message)

def getFileFunc(message):
    getFile(server, message)

def roomFunc(roomNum):
    message = encrypt_message(roomNum)
    server.send(message)

def on_closing(top,event=None):
    """This function is to be called when the window is closed."""
    top.quit()

def messageProcessing(message,f,msg_list):
    print("here")
    if f=='send file':
        msg_list.insert(Tkinter.END,"Sending file "+message)
        sendFileFunc(message)
    elif f == 'get file':
        msg_list.insert(Tkinter.END,"Getting file "+message)
        getFileFunc(message)
    elif f=="make chatroom" or f=="join chatroom":
        if(f=="make chatroom"):
            text="Making chatroom"
            sendText = encrypt_message(f)
            server.send(sendText)
        else:
            text="Joining chatroom "+message
            message = encrypt_message(f+" "+message)
            server.send(message)
        msg_list.insert(Tkinter.END,text)
        
    else:
        sendMessage(username,server,message,msg_list)




def recieve():
    print("start receive")
    while True:
        message = server.recv(2080)
        message = decrypt_message(message)
        msg_list.insert(Tkinter.END, message)

#main script

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 5:
    print ("Correct usage: script, username, IP address, port number, keyfile")
    exit()
IP_address = str(sys.argv[2])
Port = int(sys.argv[3])
server.connect((IP_address, Port))
username=str(sys.argv[1])
keyfile = str(sys.argv[4])
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

print("starting gui")
top = Tkinter.Tk()
top.title("Chatter")
messages_frame = Tkinter.Frame(top)
my_msg = Tkinter.StringVar()  # For the messages to be sent.
scrollbar = Tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = Tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
msg_list.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH)
msg_list.pack()
messages_frame.pack()
entry_field = Tkinter.Entry(top, textvariable=my_msg)
entry_field.pack()
send_button = Tkinter.Button(top, text="Send Message", command=lambda:messageProcessing(my_msg.get(),"send",msg_list))
send_button.pack()
sendFileBut=Tkinter.Button(top, text="Send File", command=lambda:messageProcessing(my_msg.get(),"send file",msg_list))
sendFileBut.pack()
getFileBut=Tkinter.Button(top, text="Get File", command=lambda:messageProcessing(my_msg.get(),"get file",msg_list))
getFileBut.pack()
makeRoomBut=Tkinter.Button(top, text="Make Chatroom", command=lambda:messageProcessing(my_msg.get(),"make chatroom",msg_list))
makeRoomBut.pack()
joinRoomBut=Tkinter.Button(top, text="Join Chatroom", command=lambda:messageProcessing(my_msg.get(),"join chatroom",msg_list))
joinRoomBut.pack()
top.protocol("WM_DELETE_WINDOW", on_closing(top))
thread.start_new_thread(recieve,())
Tkinter.mainloop()




server.close()
