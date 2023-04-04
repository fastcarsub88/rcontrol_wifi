import requests
import setup

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

def open_all_doors(relay):
    for index,value in enumerate(setup.nodes):
        open_door(relay,index)
