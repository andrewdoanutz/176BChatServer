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
    with open('received_file', 'wb') as f:
        print ('file opened')
        while True:
            print('receiving data...')
            data = conn.recv(1024)
            print('data=%s', (data))
            if not data:
                break
            # write data to a file
            f.write(data)

    f.close()
    print('Successfully get the file')


def sendFile(conn,filename):
   
    f = open(filename,'rb')
    l = f.read(1024)
    while (l):
       conn.send(l)
       print('Sent ',repr(l))
       l = f.read(1024)
    f.close()

    print('Type done sending to finish sending')




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
            else:
                server.send(message) 
                sys.stdout.write("<You>") 
                sys.stdout.write(message) 
                sys.stdout.flush() 
server.close() 