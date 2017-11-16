#!-*-coding: utf8-*-
'''
    Simple socket server using threads
'''
 
import socket
import sys
import select
import ConfigParser
import os

from wsgi.application import *

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
                ready, _, _ = select.select([conn], [], [], 2)
                if ready:
                    data += conn.recv(1024)
                else:
                    break
            print(data)
            data_list = data.split("\r\n")
            headers = {}
            headers["method"], headers["uri"], headers["version"] = data_list[0].split()
            msg_body = ""
            for header in data_list[1:]:
                if header != "":
                    if ": " in header:
                        header_name, header_value = header.split(": ")
                        headers[header_name] = header_value
                        if header_name == "Content-Type" and "boundary=" in header_value:
                            boundary = header_value.split("boundary=")[1]
                            boundary_data = data.split(boundary)[1:]
                            for body_data in boundary_data:
                                if "filename" in body_data:
                                    data_file = body_data.split("\r\n\r\n")[1]
                                    filename = "test.txt"
                                    with open(filename, "wb") as in_file:
                                        in_file.write(data_file)
                    else:
                        msg_body += header + "\r\n"
            if "Host" in headers.keys():
                status_code = 404
                message = "Not Found"
                answer_body = ""
                env = {"host": "localhost"}
                for ans in simplest_wsgi_app(env, start_response):
                    answer_body += ans
                answer_headers = "{version} {status_code} {message}\n{headers}\n\n".format(version=headers["version"], status_code=status_code, message=message, headers="")
                answer = answer_headers + answer_body
                conn.send(answer)
                conn.close()
            else:
                conn.close()
