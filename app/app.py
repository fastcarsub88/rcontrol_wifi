import cgi,json,threading
from time import sleep
from datetime import datetime
from functions import *

def set_auto_man(bool):
    with open('params.json') as f:
        params = json.load(f)
    if params['auto'] != bool:
        params['auto'] = bool
        with open('params.json','w') as f:
             f.write(json.dumps(params))

def get_params():
    with open('params.json') as f:
        return f.read()

def get_weather():
    with open('weather.json') as f:
        return f.read()

def get_status():
    res = {}
    res['d_stat'] = get_relay_state()
    res['params'] = get_params()
    res['weather'] = get_weather()
    res['time'] = datetime.now().strftime('%H:%M')
    return json.dumps(res)

def put_params(jsn):
    o_prms = json.loads(get_params())
    n_prms = json.loads(jsn)
    for value in n_prms:
        n_val = n_prms[value]
        if value == "max_pres" or value == 'min_pres' or value == 'rain_pres':
            f_val = float(n_prms[value])
            if f_val > 100 or f_val < 0:
                raise Exception
            n_val = f_val/10
        o_prms[value] = n_val
    with open('params.json','w') as f:
         f.write(json.dumps(o_prms))

def func_caller(post):
    if "method" not in post:
        return '{"response":"error","error":"no method"}'
    method = post.getvalue('method')
    try:
        if method == 'move_door':
            op_cl = post.getvalue('dfunc')
            relay = post.getvalue('dnum')
            node = post.getvalue('node')
            set_auto_man(0)
            if op_cl == 'close':
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
