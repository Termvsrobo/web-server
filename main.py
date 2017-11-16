#!-*-coding: utf8-*-
'''
    Simple socket server using threads
'''
 
import socket
import sys
import select
 
HOST = ''   # Symbolic name, meaning all available interfaces
PORT = 80 # Arbitrary non-privileged port

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'Socket created'

    #Bind socket to local host and port
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    print 'Socket bind complete'

    #Start listening on socket
    s.listen(10)
    print 'Socket now listening'
    num = 0
    #now keep talking with the client
    while 1:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        conn.setblocking(0)
        ready, _, _ = select.select([conn], [], [], 1)
        if ready:
            data = conn.recv(1024)
            print(data)
            while True:
                ready, _, _ = select.select([conn], [], [], 15)
                if ready:
                    data = conn.recv(1024)
                    print(data)
                else:
                    break
        answermsg = """HTTP/1.1 200 OK\n\n<html><head><title>Test done!!!</title></head><body><b><i>ok {num}</i></b></body></html>""".format(num=num)
        conn.send(answermsg)
        conn.close()
        num += 1
