import requests,json
from datetime import datetime

class Environ:
    def __init__(self):
        self.nodes = ''
        self.location = ''
        self.error = ''
        self.params = ''

    def load_params(self):
        with open('params.json') as f:
            params = f.read()
        self.params = json.loads(params)
        self.nodes = self.params['nodes']
        self.location = self.params['location']
        return params

    def save_params(self):
        if len(self.params) == 11:
            with open('params.json','w') as f:
                f.write(json.dumps(self.params))

def get_relay(ip):
    relay_state = []
    try:
        js = requests.get('http://'+ip+'/rpc/Shelly.GetStatus',timeout=5).json()
    except Exception:
        return "Error"
    relay_state.append('on' if js['switch:0']['output'] == True else 'off')
    relay_state.append('on' if js['switch:1']['output'] == True else 'off')
    return relay_state

def get_relay_state(node='all'):
    relay_state = {}
    if node == 'all':
        for index,value in enumerate(init.nodes):
            relay_state[value] = get_relay(init.nodes[value])
    else:
        relay_state[value] = get_relay(init.nodes[value])
    return json.dumps(relay_state)

def open_door(relay,node):
    try:
        js = requests.get('http://'+init.nodes[node]+'/rpc/Switch.Set?id='+str(relay)+'&on=true')
    except Exception:
        return

def close_door(relay,node):
    try:
        js = requests.get('http://'+init.nodes[node]+'/rpc/Switch.Set?id='+str(relay)+'&on=false')
    except Exception:
        return

def close_all_doors():
    for index,value in enumerate(init.nodes):
        close_door(0,value)
        close_door(1,value)

def set_man(node):
    init.load_params()
    init.params['auto'][node] = 'false'
    init.save_params()

def get_params():
    return init.load_params()

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
    n_prms = jsn if type(jsn) is dict else json.loads(jsn)
    for value in n_prms:
        init.params[value] = n_prms[value]
    init.save_params()

init = Environ()
init.load_params()
