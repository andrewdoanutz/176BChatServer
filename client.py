import socket 
import select 
import sys 
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
if len(sys.argv) != 3: 
    print ("Correct usage: script, IP address, port number")
    exit() 
IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server.connect((IP_address, Port)) 
  


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
    conn.send(filename)
    f = open(filename,'rb')
    l = f.read(1024)
    while (l):
       conn.send(l)
       print("Sent: %r" % repr(l))
       l = f.read(1024)
    f.close()
    
    



while True: 

    sockets_list = [sys.stdin, server] 
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 
    
    for socks in read_sockets: 
        if socks == server: 
            message = socks.recv(2048)
            print (message)
        else: 
            message = sys.stdin.readline() 
            if message[0:9]=='send file':
                server.send(message)
                print("Enter filename")
                filename=sys.stdin.readline()
                filename=filename[:-1]
                sendFile(server,filename)
                server.send("done sending")
            else:
                server.send(message) 
                sys.stdout.write("<You>") 
                sys.stdout.write(message) 
                sys.stdout.flush() 
server.close() 