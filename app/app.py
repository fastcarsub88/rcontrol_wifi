import cgi,json,threading
from time import sleep
from functions import *

def func_caller(post):
    if "method" not in post:
        return '{"response":"error","error":"no method"}'
    method = post.getvalue('method')
    try:
        if method == 'move_door':
            action = post.getvalue('action')
            relay = post.getvalue('relay')
            node = post.getvalue('node')
            set_man(node)
            if action == 'close':
                close_door(relay,node)
            else:
                open_door(relay,node)
        if method == 'set_auto':
            auto = post.getvalue('auto')
            bool =  1 if auto == 'true' else 0
            set_auto_man(bool)
        if method == 'get_params':
            return get_params()
        if method == 'put_params':
            put_params(post.getvalue('params'))
        if method == 'get_status':
            return get_status()
        return '{"response":"ok"}'
    except Exception:
        return '{"response":"error","error":"Exception"}'


def application(env, start_response):
    if env['REQUEST_METHOD'] == 'POST':
        post_env = env.copy()
        post_env['QUERY_STRING'] = ''
        post = cgi.FieldStorage(
            fp=env['wsgi.input'],
            environ=post_env,
            keep_blank_values=True
        )
        response = func_caller(post)
    else:
        response = '{"error":"not allowed"}'
    start_response('200',[('Content-Type','text/html'),('Access-Control-Allow-Origin','*')])
    return[response.encode('utf_8')]
