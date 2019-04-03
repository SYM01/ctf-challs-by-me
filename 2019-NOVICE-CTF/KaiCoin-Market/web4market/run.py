# coding: utf-8

from gevent.wsgi import WSGIServer
from application import app

print('Starting server ...')
http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()