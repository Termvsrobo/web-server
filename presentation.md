﻿---
marp: true
theme: gaia
author: Tatarnikov Vladimir
---

# Предисловие
---
Когда-то давно, читая вопросы ребят, работающих с Django пришел к мысли о том, что большинство вопросов вызваны непониманием механизма общения браузера и сервера. Поэтому я решил написать статью, в которой попытаюсь пролить свет и объяснить как все происходит. В данной статье будет частично рассмотрен протокол http.

---
# Простой сервер
---
Для того, чтобы понять как все происходит, я создам свой собственный веб-сервер, на котором и буду объяснять процесс общения.

Создаем сервер:

---

```python
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

```
---
Как вы видите, я использую модуль [socket](https://docs.python.org/3/library/socket.html). Поэтому настоятельно рекомендую вам ознакомиться с этим модулем, так как здесь я буду объяснять лишь используемые мною свойства и методы модуля. В коде мы указываем, что сервер будет работать на localhost и 8080м порте (веб). Теперь, если мы запустим наш сервер и в браузере введем адрес localhost, то в консоли (или командной строке в Windows) увидим запрос, посланный браузером серверу. [Здесь](https://ru.wikipedia.org/wiki/Список_заголовков_HTTP#.D0.9E.D1.81.D0.BD.D0.BE.D0.B2.D0.BD.D1.8B.D0.B5_.D0.B7.D0.B0.D0.B3.D0.BE.D0.BB.D0.BE.D0.B2.D0.BA.D0.B8) вы можете прочитать про заголовки запроса и ответа в  http . Я в данной статье буду использовать лишь некоторые заголовки. А [здесь](https://ru.wikipedia.org/wiki/Список_MIME-типов) список Content-Type/MIME type.

Запускаем наш скрипт (сервер)

---

После запуска скрипта в консоли увидим сообщения о том, что сервер запустился.

Теперь осталось открывать браузер и перейти на localhost. Как только мы напечатаем в адресной строке и нажмем "Ввод", то браузер инициализирует соединение и передаст некоторую информацию. Что это за информация мы увидим чуть позже. В консоль мы выведем всю информацию, которую передаст нам браузер.

---

Теперь давайте разберемся, что же это за информация и как ее обрабатывать. В консоли мы видим, что к серверу подключились с ip-адреса 127.0.0.1:39494. А вот ниже уже идут строки данных, полученные от браузера. Разбираемся что это за информация. Согласно спецификации  http , первой строкой в запросе идет так называемая стартовая строка и формат ее такой:

```
Метод URI HTTP/Версия
```
---
где:
* Метод — тип запроса, одно слово заглавными буквами. Список методов для версии 1.1 представлен в спецификации.
* [URI](https://ru.wikipedia.org/wiki/URI) определяет путь к запрашиваемому документу.
* Версия — пара разделённых точкой цифр. Например: 1.0.

Все 3 параметра разделены между собой одним пробелом.

---
Далее идет блок заголовков. **Спецификация  http  регламентирует обязательно одну пустую строку после всех заголовков и перед началом тела самого сообщения.**

Все заголовки разделяются на четыре основных группы:

1. [General Headers](https://ru.wikipedia.org/wiki/Список_заголовков_HTTP#.D0.9E.D1.81.D0.BD.D0.BE.D0.B2.D0.BD.D1.8B.D0.B5_.D0.B7.D0.B0.D0.B3.D0.BE.D0.BB.D0.BE.D0.B2.D0.BA.D0.B8) ("Основные заголовки") — могут включаться в любое сообщение клиента и сервера
1. [Request Headers](https://ru.wikipedia.org/wiki/Список_заголовков_HTTP#.D0.97.D0.B0.D0.B3.D0.BE.D0.BB.D0.BE.D0.B2.D0.BA.D0.B8_.D0.B7.D0.B0.D0.BF.D1.80.D0.BE.D1.81.D0.B0) ("Заголовки запроса") — используются только в запросах клиента;
1. [Response Headers](https://ru.wikipedia.org/wiki/Список_заголовков_HTTP#.D0.97.D0.B0.D0.B3.D0.BE.D0.BB.D0.BE.D0.B2.D0.BA.D0.B8_.D0.BE.D1.82.D0.B2.D0.B5.D1.82.D0.B0) ("Заголовки ответа") — только для ответов от сервера;
1. [Entity Headers](https://ru.wikipedia.org/wiki/Список_заголовков_HTTP#.D0.97.D0.B0.D0.B3.D0.BE.D0.BB.D0.BE.D0.B2.D0.BA.D0.B8_.D1.81.D1.83.D1.89.D0.BD.D0.BE.D1.81.D1.82.D0.B8) ("Заголовки сущности") — сопровождают каждую сущность сообщения.

---
В стартовой строке мы видим, что браузер сообщает о методе GET (имена всех методов пишутся ПРОПИСНЫМИ БУКВАМИ). Обратился браузер к ресурсу по адресу / и версия  HTTP = 1.1. Далее смотрим на общие заголовки. Название заголовка и его значение разделены символами ": ". Первым заголовком идет Host. Так как мы обращались к localhost, то здесь мы и видим наш адрес. Если когда-то ранее браузер уже обращался к ресурсу localhost (возможно запускали тестовый веб-сервер, на котором разрабатывали сайт) и сервер передал браузеру куки, то браузер передаст серверу уже имеющиеся куки, что мы и видим на скрине выше по наличию заголовка Cookie. Благодаря этому имеют место быть атаки на куки у пользователей. Так как в запросе мы больше ничего не передаем, то тело запроса осталось пустым. Чуть позже я покажу что будет, если передать нашему серверу файл или какие-то другие данные из формы в html странице.

---
После того, как сервер получил и обработал запрос от браузера, сервер должен отправить браузеру ответ. Ответ так же начинается со стартовой строки.

Стартовая строка ответа сервера имеет следующий формат:

```
HTTP/Версия КодСостояния Пояснение
```

---
где:

* Версия — пара разделённых точкой цифр, как в запросе;
* Код состояния (англ. Status Code) — три цифры. По коду состояния определяется дальнейшее содержимое сообщения и поведение клиента;
* Пояснение (англ. Reason Phrase) — текстовое короткое пояснение к коду ответа для пользователя. Никак не влияет на сообщение и является необязательным.

---
Я воспользуюсь [таким](http://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html) соглашением. Например, стартовая строка ответа сервера на предыдущий запрос может выглядеть так:

```
HTTP/1.0 200 OK
```

После стартовой строки должны идти заголовки ответа. Но сейчас никаких заголовков я передавать не буду. Я лишь ограничусь только стартовой строкой, в которой указываю версию, код ответа (200) и пояснение (ОК). После этого я делаю одну пустую строку (она обязательна), иначе не будет работать. Ну а дальше уже я передаю простенькую html страницу (переменная answermsg). Если сделали все правильно, то вы увидите в браузере слово ok, выделенное жирным шрифтом и курсивом.

---
Но сейчас сервер получился не очень гибким. А точнее даже вообще не гибким. Если я захочу изменить страницу, то мне придется лезть в код и менять его. Поэтому сейчас я переделаю свой сервер так, чтобы я мог использовать конфигурационные файлы, в которых смогу указать пути, указать файлы и, может быть, что-нибудь еще.

---
# Конфигурируемый сервер

---
Сейчас я покажу простой пример того, как можно сделать наш сервер конфигурируемым. Для этого я воспользуюсь модулем configparser. Для этого я создам простенький файл конфигурации:

Файл конфигаруции: conf/localhost.conf

```ini
[localhost]
Directory: ./sites
```

Первой строкой здесь будет являться хост, запрос для которого мы должны обработать. А во второй строке я указываю директорию, в которой лежит файл index.html.

---
Теперь код сервера выглядит так:

```python
'''
Конфигурируемый веб-сервер
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
                        if headers['uri'] in ['/', '/index', '/index.html']:
                            path = Path('index.html')
                        else:
                            path = Path().joinpath(
                                *headers['uri'].split('/')[1:]
                            )

                        file_path = base_dir / directory / path
                        if file_path.exists():
                            status_code = 200
                            message = 'OK'
                            answer_body = file_path.read_text()

                        answer_headers = (
                            f'{version} {status_code} {message}\n\n\n'
                        )
                        answer = answer_headers + answer_body
                    client_conn.send(bytes(answer, 'utf-8'))

```

---
Здесь я на всякий случай проверяю наличие заголовка Host в запросе. Если такой есть, то читаю к какому хосту направлен запрос. Далее я смотрю по какому uri идет обращение. Если uri обращен к главной странице сайта, то как правило uri будет равен "/", либо будет содержать ключевое слово /index[.html|.php]. Если обращение идет к главной странице сайта, то стоит проверить существование файла index[.html|.php] в корневой директории сайта. Если такой сайт есть, тогда надо отдать страницу. Если обращение идет к какой-то конкретной странице, тогда, если файл страницы существует, отдаем эту страницу. Если файлов страниц не существует, мы должны выдать ошибку с кодом 404 и пояснением "Not Found". Такой статус у меня сделан по-умолчанию.

---
В папку sites я положил два файла:

```
index.html
test
```

Теперь, если запустить сервер и сделать запрос к `localhost`, то увидим в браузере страницу с содержанием из файла index.html.

Если сделать запрос к `localhost/test`, то увидим страницу с содержанием из файла test.

---
# Передача файлов и параметров

---
Теперь у нас есть сервер, который мы можем конфигурировать. В примере выше я не стал рассматривать вариант с несколькими конфигурационными файлами, как это сделано, например, в Apache2. Но здесь не сложно изменить код. Такой сервер уже можно назвать рабочим, но данный сервер пока еще не умеет работать с переданными в запросе параметрами.

---
Чтобы добавить параметры к GET запросу, нужно в конце URL-адреса поставить знак "?" и после него начинать задавать их по следующему правилу:

```
имя_параметра1=значение_параметра1&имя_параметра2=значение_параметра2&...
```

Разделителем между параметрами служит знак "&".

Если запустим текущий вариант сервера и обратиться по адресу `localhost/test?te=15`, то получим ошибку 404, так как файла с названием "test?te=15" не существует. Необходимо отделить название файла и параметры.

---
> Я мог бы указать в коде и другой код ответа, но я придерживаюсь соглашения, чтобы любой браузер правильно понимал ответ.

> **Пара слов о шаблоне для кода 404.** Как видно из примера, шаблон страницы ответа тоже нужно создавать.

---
Теперь у меня получился вот такой код:

```python
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

```

---
В папке sites у меня лежит файл test, в который я вставил вот такой код:

```html
<html>
    <head>
        <meta charset="utf-8">
        <title>Тестовая страница</title>
    </head>
    <body>
        {data}
    </body>
</html>
```

Поэтому в коде сервера я указал `answer_body.format(data=uri_params.replace("&", "\n"))`.

---
Таким образом я лишь просто вывожу переданные параметры.

Теперь, если запустить сервер и обратиться по адресу `localhost/test` с передачей различных параметров в запросе, эти параметры с их значениями будут выведены на странице в браузере.

---
Теперь осталось разобраться с тем, как происходит передача параметров в POST-запросе. Для этого в sites/index.html я создам форму, которая будет передавать POST-запрос к странице /test:

```html
<html>
<head>
    <meta charset="utf8">
    <title>New page</title>
</head>
<body>
    <b>
        <i>Это новая страница сайта</i>
    </b>
    <p>Заполните форму ниже</p>
    <form method="post" action="test">
        <input name="fullname">
        <input name="email" type="email">
        <button type="submit">Отправить</button>
    </form>
</body>
</html>
```
---
И вот здесь-то после нажатия на кнопку "Отправить" сервер у меня завершил процесс с ошибкой. Как оказалось, все дело в том, что параметры POST запроса передаются не в стартовой строке запроса, как в GET, а в теле сообщения запроса. Поэтому нужно переписать код так, чтобы обрабатывать текст сообщений запроса:

```python
#!-*-coding: utf8-*-
'''
Конфигурируемый веб-сервер с сохранением файлов
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
                    msg_body = ''
                    for header in other_lines:
                        if header:
                            if ':' in header:
                                header_name, header_value = map(
                                    lambda x: x.strip(),
                                    header.split(':', maxsplit=1)
                                )
                                headers[header_name] = header_value
                                if (
                                    header_name == 'Content-Type'
                                    and 'boundary=' in header_value
                                ):
                                    boundary = (
                                        header_value.split('boundary=')[1]
                                    )
                                    boundary_data = data.split(boundary)[1:]
                                    for body_data in boundary_data:
                                        if 'filename' in body_data:
                                            data_file = (
                                                body_data.split('\r\n\r\n')[1]
                                            )
                                            filename = Path('test.txt')
                                            data_file_path = (
                                                base_dir / Path('upload') /
                                                filename
                                            )
                                            data_file_path.parent.mkdir(
                                                parents=True, exist_ok=True
                                            )
                                            data_file_path.write_bytes(
                                                data_file
                                            )
                            else:
                                msg_body += header + '\r\n'
                    if 'Host' in headers.keys():
                        host = headers['Host']
                        directory = Path(config.get(host, 'Directory'))
                        status_code = 404
                        message = 'Not Found'
                        answer_body = ''
                        if '?' in headers['uri']:
                            uri_file, uri_params = headers['uri'].split('?')
                        else:
                            uri_file, uri_params = headers['uri'], msg_body
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

```

---
Обратите внимание, что названия передаваемых параметров есть ни что иное, как значение атрибута name тега **\<input\>**. Если не указать значение атрибута name, то в запрос данное поле не будет передано. Поэтому считайте, что этот атрибут обязательный, хотя на самом деле в html атрибуты не являются обязательными.

---
Теперь все в порядке. Процесс не завершается с ошибкой после нажатия на кнопку "Отправить" на клиенте. Вместо этого браузер переходит на страницу test и показывает параметры, которые мы передали в запросе POST.

Но теперь я хочу передать на сервер файл. Первое, что приходит на ум — это использовать поле типа file в форме:

```html
<html>
<head>
    <meta charset="utf8">
    <title>New page</title>
</head>
<body>
    <b>
        <i>Это новая страница сайта</i>
    </b>
    <p>Заполните форму ниже</p>
    <form method="post" action="test">
        <input name="fullname">
        <input name="email" type="email">
        <input name="myfile" type="file">
        <button type="submit">Отправить</button>
    </form>
</body>
</html>
```
---
Теперь на странице test мы увидим название файла. НО… Это ведь не сам файл, а лишь его наименование. Как сделать так, чтобы передать содержимое указанного файла??? Ответ на этот вопрос [здесь](http://htmlbook.ru/samhtml5/formy/zagruzka-failov). Перепишем код страницы:

```html
<html>
<head>
    <meta charset="utf8">
    <title>New page</title>
</head>
<body>
    <b>
        <i>Это новая страница сайта</i>
    </b>
    <p>Заполните форму ниже</p>
    <form method="post" action="test" enctype="multipart/form-data">
        <input name="fullname">
        <input name="email" type="email">
        <input name="myfile" type="file">
        <button type="submit">Отправить</button>
    </form>
</body>
</html>
```
---
Теперь вроде все в порядке. Но после запуска первое с чем я сталкиваюсь — это с размером передаваемого файла. В коде циклически читается 1024 байт, но файл, который я передаю, занимает порядка 10 кБ. В коде не происходит склейки новой порции данных со старыми при чтении данных. Исправляю:

```python
#!-*-coding: utf8-*-
'''
Конфигурируемый веб-сервер с post-запросом
'''

import socket
import select
import configparser
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
                    data_list = data.split("\r\n")
                    header_line, *other_lines = data_list
                    headers = {}
                    headers["method"], headers["uri"], headers["version"] = (
                        header_line.split()
                    )
                    version = headers['version']
                    msg_body = ""
                    for header in other_lines:
                        if header:
                            if ":" in header:
                                header_name, header_value = map(
                                    lambda x: x.strip(),
                                    header.split(':', maxsplit=1)
                                )
                                headers[header_name] = header_value
                            else:
                                msg_body += header + "\r\n"
                    if "Host" in headers.keys():
                        host = headers["Host"]
                        directory = Path(config.get(host, "Directory"))
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
                            path = Path().joinpath(*uri_file.split("/")[1:])
                        file_path = base_dir / directory / path
                        if file_path.exists():
                            status_code = 200
                            message = "OK"
                            answer_body = file_path.read_text().format(
                                data=uri_params.replace('&', '\n')
                            )
                        answer_headers = (
                            f"{version} {status_code} {message}\n{headers}\n\n"
                        )
                        answer = answer_headers + answer_body
                    client_conn.send(bytes(answer, 'utf-8'))

```
---
Теперь можно увидеть, что после добавления атрибута enctype="multipart/form-data" содержимое запроса изменилось и можно увидеть передаваемые байты файла с его названием.

---
Теперь в заголовке Content-Type помимо типа еще есть параметр boundary, который переводится как "граница". Эта граница между параметрами в теле сообщений. С помощью значения этого параметра я буду разделять передаваемые параметры и их значения. Я не стал усложнять код, поэтому у меня получился вот такой результат:

```python
#!-*-coding: utf8-*-
'''
Конфигурируемый веб-сервер с post-запросом
'''

import socket
import select
import configparser
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
                    data_list = data.split("\r\n")
                    header_line, *other_lines = data_list
                    headers = {}
                    headers["method"], headers["uri"], headers["version"] = (
                        header_line.split()
                    )
                    version = headers['version']
                    msg_body = ""
                    for header in other_lines:
                        if header:
                            if ":" in header:
                                header_name, header_value = map(
                                    lambda x: x.strip(),
                                    header.split(':', maxsplit=1)
                                )
                                headers[header_name] = header_value
                            else:
                                msg_body += header + "\r\n"
                    if "Host" in headers.keys():
                        host = headers["Host"]
                        directory = Path(config.get(host, "Directory"))
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
                            path = Path().joinpath(*uri_file.split("/")[1:])
                        file_path = base_dir / directory / path
                        if file_path.exists():
                            status_code = 200
                            message = "OK"
                            answer_body = file_path.read_text().format(
                                data=uri_params.replace('&', '\n')
                            )
                        answer_headers = (
                            f"{version} {status_code} {message}\n{headers}\n\n"
                        )
                        answer = answer_headers + answer_body
                    client_conn.send(bytes(answer, 'utf-8'))

```
---
После запуска сервера и передачи текстового файла в папке со скриптом сервера у меня появился файл test.txt с содержимым передаваемого файла. Думаю теперь многим станет ясно, что очень важно правильно прочитать и обработать входящие данные от браузера.

Я не буду здесь рассматривать способ скачивания файлов с сервера и его методы докачки. Об этом можно прочитать [тут](https://ru.wikipedia.org/wiki/HTTP#Докачка_и_фрагментарное_скачивание).

---
# WSGI

---
Но сервер еще до сих пор не является гибким и если нужно что-то добавить на сайт, то скорее всего придется переделывать код самого сервера. Чтобы избежать этого существует стандарт WSGI.

[WSGI](https://ru.wikipedia.org/wiki/WSGI) — стандарт обмена данными между веб-сервером (backend) и веб-приложением (frontend). Под это определение попадают многие вещи, тот же самый CGI. Так что поясню.

* Во-первых, WSGI — Python-специфичный стандарт, его описывают [PEP 333](https://www.python.org/dev/peps/pep-0333/) и [PEP 3333](https://www.python.org/dev/peps/pep-3333/).
* Во-вторых, он уже принят (статус Final).

---
По стандарту, WSGI-приложение должно удовлетворять следующим требованиям:

* должно быть вызываемым (callable) объектом (обычно это функция или метод)
* принимать два параметра:
    * словарь переменных окружения (environ)[[2](https://ru.wikipedia.org/wiki/WSGI#cite_note-2)]
    * обработчик запроса (start_response)[[3](https://ru.wikipedia.org/wiki/WSGI#cite_note-3)]
* вызывать обработчик запроса с кодом  HTTP-ответа  и  HTTP-заголовками
* возвращать итерируемый объект с телом ответа

---
Значит сейчас я создам простенькое приложение, которое будет удовлетворять всем выше изложенным требованиям. У меня оно выглядит так:

```python
def start_response(status_message, list_of_headers):
    print(status_message)
    print(list_of_headers)


def simplest_wsgi_app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    yield 'Hello, world!'

```

---
В данном случае я создал функцию-приложение с названием simplest_wsgi_app и обработчик запроса start_response. Как видно из кода я ничего не обрабатываю в обработчике запроса, так как это лишь тестовый пример, чтобы показать как работает WSGI. Теперь это приложение нужно импортировать в сервер и при запросе от клиента выполнить данное приложение.

У меня получился вот такой код сервера с WSGI:

```python
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

```
---
Я вызываю созданное приложение и полученное значение сохраняю в тело ответа сервера. Полученный ответ ниже отдается браузеру.

---
# Заставляем Python выполнить код на PHP

---
А для тех, кто все же хочет на своем сервере запускать скрипты php отвечу, что да, такое возможно. Решение взято [отсюда](https://stackoverflow.com/questions/89228/how-to-call-an-external-command).

У меня получился вот такой код:

```python
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

```
---
Если сейчас обратиться по адресу `localhost/test.php`, то будет выполнен скрипт test.php. У меня test.php выведет информацию о php:

```php
<?php
    phpinfo();
?>
```
---

# Спасибо за внимание!!!

---

[Ссылка на проект](https://github.com/Termvsrobo/web-server)