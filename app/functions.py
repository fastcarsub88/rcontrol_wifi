import requests,json
from datetime import datetime

class Environ:
    def __init__(self):
        self.nodes = ''
        self.location = ''
        self.params = ''
        self.open_time = ''
        self.close_time = ''

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

    def update(self,weather):
        if self.params['open_method'] == 'time':
            self.open_time = int(selfparams['open'].replace(':',''))
        else:
            self.open_time = self.cnt_time(weather['sunrise'],self.params['open'])

        if self.params['close_method'] == 'time':
            self.close_time = int(self.params['close'].replace(':',''))
        else:
            self.close_time = self.cnt_time(weather['sunset'],self.params['close'])
        with open('status.json','w') as f:
            f.write(json.dumps({
              'open_time':init.open_time,
              'close_time':init.close_time,
              'auto':init.params['auto'],
              }))

    def cnt_time(self,time,num):
        t = int(time.replace(':',''))
        num = int(num)
        dir = float(num)
        if dir >= 0:
            for i in range(num):
                if int(str(t)[-2:]) == 60:
                    t += 41
                else:
                    t += 1
        else:
            num = -num
            for i in range(num):
                if int(str(t)[-2:]) == 00:
                    t -= 41
                else:
                    t -= 1
        return t

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

def send_message(mess):
    with open('messages','w') as f:
        f.write(mess)

def read_message():
    with open('messages','a+') as f:
        f.seek(0)
        mess = f.read()
        f.seek(0)
        r.write('')
    return mess

def put_params(params):
    send_message('params_saved')
    init.params = json.loads(params)
    init.save_params()

def get_weather():
    with open('weather.json') as f:
        return f.read()

def read_status():
    with open('status.json') as f:
        return f.read()

def get_errors():
    with open('errors') as f:
        return f.read()

def get_status():
    res = {}
    res['d_stat'] = get_relay_state()
    res['params'] = read_status()
    res['errors'] = get_errors()
    res['weather'] = get_weather()
    res['time'] = datetime.now().strftime('%H:%M')
    return json.dumps(res)

init = Environ()
init.load_params()
