import requests,setup,json
from datetime import datetime

def get_relay(value):
    relay_state = []
    try:
        js = requests.get('http://'+value+'/rpc/Shelly.GetStatus').json()
    except Exception:
        return
    relay_state.append('on' if js['switch:0']['output'] == True else 'off')
    relay_state.append('on' if js['switch:1']['output'] == True else 'off')
    return relay_state

def get_relay_state(node='all'):
    relay_state = {}
    if node == 'all':
        for index,value in enumerate(setup.nodes):
            relay_state['node'+str(index)] = get_relay(value)
    else:
        relay_state['node'+node] = get_relay(setup.nodes[int(node)])
    return json.dumps(relay_state)

def open_door(relay,node):
    try:
        js = requests.get('http://'+setup.nodes[int(node)]+'/rpc/Switch.Set?id='+str(relay)+'&on=true')
    except Exception:
        return

def close_door(relay,node):
    try:
        js = requests.get('http://'+setup.nodes[int(node)]+'/rpc/Switch.Set?id='+str(relay)+'&on=false')
    except Exception:
        return

def close_all_doors():
    for index,value in enumerate(setup.nodes):
        close_door(0,index)
        close_door(1,index)

def set_man(node):
    params = get_params()
    auto = params['auto']
    if node == len(setup.nodes):
        params['auto'] = auto[:node]+'0'
    elif node == 0:
        params['auto'] = '0'+auto[1:]
    else:
        params['auto'] = auto[:node]+'0'+auto[node+1:]
    return params['auto']
    with open('params.json','w') as f:
        f.write(json.dumps(params))

def get_params():
    with open('params.json') as f:
        return f.read()

def get_weather():
    with open('weather.json') as f:
        return f.read()

def get_errors():
    with open('errors') as f:
        return f.read()

def get_status():
    res = {}
    res['d_stat'] = get_relay_state()
    res['params'] = get_params()
    res['weather'] = get_weather()
    res['errors'] = get_errors()
    res['time'] = datetime.now().strftime('%H:%M')
    return json.dumps(res)

def put_params(jsn):
    o_prms = json.loads(get_params())
    n_prms = jsn if type(jsn) is dict else json.loads(jsn)
    for value in n_prms:
        o_prms[value] = n_prms[value]
    if len(o_prms) == 8:
        with open('params.json','w') as f:
            f.write(json.dumps(o_prms))
