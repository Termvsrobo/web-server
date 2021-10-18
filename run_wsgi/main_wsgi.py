#!-*-coding: utf8-*-
'''
Простой веб-сервер с wsgi
'''

import socket
import select

from wsgi.application import simplest_wsgi_app, start_response

HOST = ''  # Символическое имя. По умолчанию localhost
PORT = 8080  # Указываем непривилированный порт

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print('Socket created')

        # Связываем сокет с локальным хостом и портом
        sock.bind((HOST, PORT))

        print('Привязка сокета')

        # Слушаем сокет
        sock.listen(10)
        print('Слушаем сокет')
        # Теперь можем общаться с клиентами
        while True:
            # Ждем подключения клиентов
            conn, addr = sock.accept()
            print('Подключение с ' + addr[0] + ':' + str(addr[1]))
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
                headers["method"], headers["uri"], headers["version"] = (
                    data_list[0].split()
                )
                version = headers["version"]
                msg_body = ""
                for header in data_list[1:]:
                    if header != "":
                        if ": " in header:
                            header_name, header_value = header.split(": ")
                            headers[header_name] = header_value
                            if (
                                header_name == "Content-Type"
                                and "boundary=" in header_value
                            ):
                                boundary = header_value.split("boundary=")[1]
                                boundary_data = data.split(boundary)[1:]
                                for body_data in boundary_data:
                                    if "filename" in body_data:
                                        data_file = (
                                            body_data.split("\r\n\r\n")[1]
                                        )
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
                    answer_headers = (
                        f"{version} {status_code} {message}\n{headers}\n\n"
                    )
                    answer = answer_headers + answer_body
                    conn.send(answer)
                    conn.close()
                else:
                    conn.close()
