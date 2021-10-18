#!-*-coding: utf8-*-
'''
Конфигурируемый веб-сервер с параметрами
'''

import socket
import select
import configparser
from pathlib import Path
HOST = ''  # Символическое имя. По умолчанию localhost
PORT = 8080  # Указываем непривилированный порт

if __name__ == '__main__':
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
            reads, writes, excepts = select.select(inputs, outputs, inputs)
            for conn in reads:
                _conn, client_addr = conn.accept()
                with _conn as client_conn:
                    ip_addr, client_port = client_addr
                    print(f'Подключение с {ip_addr}:{client_port}')
                    data = client_conn.recv(1024)
                    data = data.decode('utf-8')
                    print(data)
                    answer = ''
                    data_list = data.split('\r\n')
                    header_line, *other_lines = data_list
                    headers = {}
                    headers['method'], headers['uri'], headers['version'] = (
                        header_line.split()
                    )
                    version = headers['version']
                    for header in other_lines:
                        if header and ':' in header:
                            header_name, header_value = map(
                                lambda x: x.strip(),
                                header.split(':', maxsplit=1)
                            )
                            headers[header_name] = header_value
                    if 'Host' in headers.keys():
                        host = headers['Host']
                        directory = Path(config.get(
                            host.split(':')[0], 'Directory'
                        ))
                        status_code = 404
                        message = 'Not Found'
                        answer_body = ''
                        if '?' in headers['uri']:
                            uri_file, uri_params = headers['uri'].split('?')
                        else:
                            uri_file, uri_params = headers['uri'], ''
                        if uri_file in ['/', '/index', '/index.html']:
                            path = Path('index.html')
                        else:
                            path = Path().joinpath(*uri_file.split('/')[1:])
                        file_path = base_dir / directory / path
                        if file_path.exists():
                            status_code = 200
                            message = 'OK'
                            answer_body = file_path.read_text().format(
                                data=uri_params.replace('&', '\n')
                            )
                        answer_headers = (
                            f'{version} {status_code} {message}\n{headers}\n\n'
                        )
                        answer = answer_headers + answer_body
                    client_conn.send(bytes(answer, 'utf-8'))
