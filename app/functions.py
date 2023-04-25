import requests,json
from datetime import datetime

def load_params():
    with open('params.json') as f:
        return json.loads(f.read())

def get_params():
    with open('params.json') as f:
        return f.read()

def save_params(params):
    if type(params) == str:
        params = json.loads(params)
    if len(params) == 11:
        with open('params.json','w') as f:
            f.write(json.dumps(params))

def save_status(open_time,close_time,auto_stat):
    with open('status.json','w') as f:
        f.write(json.dumps({
          'open_time':open_time,
          'close_time': close_time,
          'auto': auto_stat,
          }))

def update_open_close_times(weather,params):
    if params['open_method'] == 'time':
        open_time = int(params['open'].replace(':',''))
    else:
        open_time = cnt_time(weather['sunrise'],params['open'])

    if params['close_method'] == 'time':
        close_time = int(params['close'].replace(':',''))
    else:
        close_time = cnt_time(weather['sunset'],params['close'])
    return open_time,close_time

def cnt_time(time,num):
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

def send_message(mess):
    with open('messages','w') as f:
        f.write(mess)

def read_message():
    with open('messages') as f:
        return f.read()

def clear_message():
    with open('messages','w') as f:
        f.write('')

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
