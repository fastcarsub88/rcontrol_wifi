import cgi,json,threading
from time import sleep
from functions import *

def set_man(node):
    params = load_params()
    params['auto'][node] = 'false'
    save_params(params)
    status = json.loads(read_status())
    save_status(status.open_time,status.close_time,params['auto'])

def func_caller(post):
    if "method" not in post:
        return '{"response":"error","error":"no method"}'
    method = post.getvalue('method')
    try:
        if method == 'move_door':
            action = post.getvalue('action')
            relay = post.getvalue('relay')
            node = post.getvalue('node')
            nodes = load_params()['nodes']
            set_man(node)
            send_message('params_saved')
            if action == 'close':
                close_door(nodes,relay,node)
            else:
                open_door(nodes,relay,node)
        if method == 'get_params':
            return get_params()
        if method == 'put_params':
            save_params(post.getvalue('params'))
            send_message('params_saved')
        if method == 'get_status':
            return get_status()
        return '{"response":"ok"}'
    except Exception as e:
        return '{"response":"error","error":"Exception: '+repr(e)+'"}'


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
