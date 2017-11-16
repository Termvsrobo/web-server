def start_response(status_message, list_of_headers):
    print(status_message)
    print(list_of_headers)

def simplest_wsgi_app(environ, start_response):
     start_response('200 OK', [('Content-Type', 'text/plain')])
     yield 'Hello, world!'
