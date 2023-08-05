
# coding: utf-8

# In[1]:

import tornado.ioloop
has_ioloop = tornado.ioloop.IOLoop.initialized()
myport = 9500
server_list = {}
prefix_list = {}
proxy_private = 9011

def get_port():
    myport = 9500
    while True:
        if not myport in list(server_list.keys()):
            return myport
        myport = myport + 1

def register_port(prefix, port):
    import json
    import urllib.request
    data = {"target" : "http://localhost:%d" %  port }
    request = urllib.request.Request("http://localhost:%d/api/routes%s"
                                     % (proxy_private, prefix))
    request.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(request,
                                      json.dumps(data).encode('utf-8'))

def register_start_app(prefix, app_list):
    import tornado.web
    import tornado.httpserver
    
    if prefix in prefix_list:
        unregister(prefix_list[prefix])

    application = tornado.web.Application(app_list)
    http_server = tornado.httpserver.HTTPServer(application)
    port = get_port()
    http_server.listen(port)
    register_port(prefix, port)
    prefix_list[prefix] = port
    server_list[port] = http_server
    return port

def register_tornado_handler(prefix, handler):
    return register_start_app(prefix, [
        (r"^($|/.*$)", handler)
        ])

def register_wsgi(prefix, handler):
    import tornado.wsgi
    container = tornado.wsgi.WSGIContainer(handler)
    return register_start_app(prefix, [
        (r"^($|/.*$)",
         tornado.web.FallbackHandler, dict(fallback=container))
        ])

def unregister(port):
    server_list[port].stop()
    del server_list[port]

def unregister_all():
    for k, v in list(server_list.items()):
        v.stop()
        del server_list[k]

def start_loop():
    if not has_ioloop:
        tornado.ioloop.IOLoop.instance().start()
  


# In[ ]:



