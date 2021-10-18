#!-*-coding: utf8-*-
'''
Простой веб-сервер с запуском php-кода
'''

import socket
import select
import configparser
import os
from pathlib import Path
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

        inputs = [sock]
        outputs = [sock]

        base_dir = Path(__file__).parent
        root_dir = base_dir.parent

        config = configparser.ConfigParser()
        config.read(
            root_dir.absolute() / Path('conf') / Path('localhost.conf')
        )

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
                version = headers['version']
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
                    host = headers["Host"]
                    directory = Path(config.get(
                        host, "Directory"
                    ))
                    status_code = 404
                    message = "Not Found"
                    answer_body = ""
                    if "?" in headers["uri"]:
                        uri_file, uri_params = headers["uri"].split("?")
                    else:
                        uri_file, uri_params = headers["uri"], msg_body
                    if uri_file in ["/", "/index", "/index.html"]:
                        path = Path('index.html')
                    else:
                        path = os.path.join(*uri_file.split("/")[1:])
                    file_path = base_dir / directory / path
                    if file_path.exists():
                        status_code = 200
                        message = "OK"
                        if not file_path.endswith(".php"):
                            answer_body = file_path.read_text().format(
                                data=uri_params.replace("&", "\n")
                            )
                        else:
                            answer_body = os.popen(f'php {file_path}').read()
                    answer_headers = (
                        f"{version} {status_code} {message}\n{headers}\n\n"
                    )
                    answer = answer_headers + answer_body
                    conn.send(answer)
                    conn.close()
                else:
                    conn.close()
