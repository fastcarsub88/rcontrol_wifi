import requests,threading,json,requests,time
from datetime import datetime
from functions import *

last_weather_check = 0

def get_conditions(data_file):
    try:
        w_data = requests.get("https://api.openweathermap.org/data/2.5/weather?zip=65078,us&appid=914fd2c984f8077049df587218d8579d&units=imperial")
        data_file['weather_error'] = 'false'
    except requests.exceptions.RequestException as e:
        data_file['weather_error'] = e.message
        f.write(json.dumps(data_file))
        return
    if w_data.status_code == 200:
        w_data_check = w_data.text
        w_dict = json.loads(w_data_check)
        if w_dict['main']['feels_like']:
            data_file['feels_like'] = w_dict['main']['feels_like']
            data_file['wind_speed'] = w_dict['wind']['speed']
            data_file['sunrise'] = time.strftime("%H:%M",time.localtime(w_dict['sys']['sunrise']))
            data_file['sunset'] = time.strftime("%H:%M",time.localtime(w_dict['sys']['sunset']))
            data_file['rain'] = ('false' if w_dict['weather'][0]['id'] > 781 else 'true')
            c_wind_dir = (w_dict['wind']['deg'] if 'deg' in w_dict['wind'] else '0')
            for value in wind_dir_dict:
                if value < c_wind_dir:
                    continue
                if (value - c_wind_dir) < 23:
                    wind_dir_str = wind_dir_dict[value]
                else:
                    wind_dir_str = wind_dir_dict[(value-45)]
            data_file['wind_dir'] = wind_dir_str
            with open('data_file.json','w') as f:
                 f.write(json.dumps(data_file))

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

def set_door_press(data,tm):
    cr_tm = str(tm)
    cr_tm = (cr_tm[0:2]+":"+cr_tm[2:4])
    if (cnt_time(cr_tm, fst_close_tm) > cl_tm):
        set_press(data['min_pres'])
    elif (data['rain'] == 'true'):
        set_press(data['rain_pres'])
    else:
        set_press(data['max_pres'])

def set_doors(state):
    # state == none,reset,main,small
    if is_tunnel():
        set_door_relays(calc_tun_doors())
        return
    if state == 'reset' or state == 'none':
        set_door_relays(0)
        return
    set_door_relays(calc_doors(state))

while True:
    time.sleep(5)
    cr_tm = int(datetime.now().strftime('%H:%M').replace(":",''))
    with open('data_file.json') as f:
        try:
            data_file = json.load(f)
        except Exception as e:
            requests.post('https://api.telegram.org/bot987030942:AAG49kJiZGQBAOFBgS_SOM9-RWGIT5On_ws/sendMessage?chat_id=-1001154782385&text='+name+' has an error')
    if (cr_tm - last_weather_check) > 10 or last_weather_check > cr_tm:
        last_weather_check = cr_tm
        get_conditions(data_file)
    if data_file['auto'] == 0:
        set_press(data['rain_pres'])
        continue
    feels_like = data_file['feels_like']
    if data_file['open_method'] == 'time':
        op_tm = int(data_file['open'].replace(':',''))
    else:
        op_tm = cnt_time(data_file['sunrise'],data_file['open'])
    if data_file['close_method'] == 'time':
        cl_tm = int(data_file['close'].replace(':',''))
    else:
        cl_tm = cnt_time(data_file['sunset'],data_file['close'])
    min_temp = data_file['min_temp']
    sm_door_temp = data_file['sm_door_temp']
    fst_close_tm = data_file['fst_close_tm']
    if cr_tm > op_tm and cr_tm < cl_tm:
        if data_file['open_state'] == 'reset':
            data_file['open_state'] = 'main'
            if feels_like < sm_door_temp:
                data_file['open_state'] = 'small'
            if feels_like < min_temp:
                date_file['open_state'] = 'none'
            with open('data_file.json','w') as f:
                f.write(json.dumps(data_file))
        if data_file['state'] == 'close':
            data_file['state'] = 'open'
            with open('data_file.json','w') as f:
                f.write(json.dumps(data_file))
        set_door_press(data_file,cr_tm)
    else:
        if data_file['state'] == 'open':
            data_file['state'] = 'close'
            data_file['open_state'] = 'reset'
            with open('data_file.json','w') as f:
                f.write(json.dumps(data_file))
        set_press(7)
    set_doors(data_file['open_state'])
