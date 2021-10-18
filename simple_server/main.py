#!-*-coding: utf8-*-
'''
Простой веб-сервер
'''

import socket
import select

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
        num = 0
        # Теперь можем общаться с клиентами
        while True:
            # Ждем подключения клиентов
            reads, writes, excepts = select.select(inputs, outputs, inputs)
            for conn in reads:
                _conn, client_addr = conn.accept()
                with _conn as client_conn:
                    ip_addr, client_port = client_addr
                    print(f'Подключение с {ip_addr}:{client_port}')
                    data = client_conn.recv(1024)
                    print(data)
                    answermsg = (
                        'HTTP/1.1 200 OK\n\n'
                        '<html>'
                        '    <head>'
                        '        <title>Test done!!!</title>'
                        '    </head>'
                        '    <body>'
                        '        <b>'
                        f'            <i>ok {num}</i>'
                        '        </b>'
                        '    </body>'
                        '</html>'
                    )
                    client_conn.send(bytes(answermsg, 'utf-8'))
                    num += 1
