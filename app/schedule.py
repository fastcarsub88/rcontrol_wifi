import requests,threading,json,requests,time
from datetime import datetime
from functions import *

last_weather_check = 0
weather = get_conditions();

def get_conditions():
    try:
        w_data = requests.get("https://api.openweathermap.org/data/2.5/weather?zip=65078,us&appid=914fd2c984f8077049df587218d8579d&units=imperial")
    except requests.exceptions.RequestException as e:
        with open('errors','a') as f:
            f.write(e.message+"\n")
        return False
    if w_data.status_code == 200:
        w_data_check = w_data.text
        w_dict = json.loads(w_data_check)
        if w_dict['main']['feels_like']:
            weather['feels_like'] = w_dict['main']['feels_like']
            weather['wind_speed'] = w_dict['wind']['speed']
            weather['sunrise'] = time.strftime("%H:%M",time.localtime(w_dict['sys']['sunrise']))
            weather['sunset'] = time.strftime("%H:%M",time.localtime(w_dict['sys']['sunset']))
            weather['rain'] = ('false' if w_dict['weather'][0]['id'] > 781 else 'true')
            c_wind_dir = (w_dict['wind']['deg'] if 'deg' in w_dict['wind'] else '0')
            for value in wind_dir_dict:
                if value < c_wind_dir:
                    continue
                if (value - c_wind_dir) < 23:
                    wind_dir_str = wind_dir_dict[value]
                else:
                    wind_dir_str = wind_dir_dict[(value-45)]
            weather['wind_dir'] = wind_dir_str
            with open('weather.json','w') as f:
                 f.write(json.dumps(weather))
            return weather

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

def set_doors(state):
    # state == none,reset,main,small
    if state == 'reset' or state == 'none':
        close_all_doors()
        return
    if state == "main":
        open_all_doors(0)
    if state == 'small':
        open_all_doors(1)

while True:
    time.sleep(5)
    current_time = int(datetime.now().strftime('%H:%M').replace(":",''))
    with open('params.json') as f:
        try:
            params = json.load(f)
        except Exception as e:
            params['error'] = 'true'
            f.write(params)
            continue

    if (current_time - last_weather_check) > 10 or last_weather_check > current_time:
        last_weather_check = current_time
        weather_check = get_conditions()
        if weather_check:
            weather = weather_check

    if params['open_method'] == 'time':
        open_time = int(params['open'].replace(':',''))
    else:
        open_time = cnt_time(weather['sunrise'],params['open'])

    if params['close_method'] == 'time':
        close_time = int(params['close'].replace(':',''))
    else:
        close_time = cnt_time(weather['sunset'],params['close'])


    if params['auto'] == 0:
        continue
    if params['open_state'] == 'reset':
        if current_time > open_time:
            params['open_state'] = 'main'
            if feels_like < params['sm_door_temp']:
                params['open_state'] = 'small'
            if feels_like < params['min_temp']:
                params['open_state'] = 'none'

    if params['open_state'] == 'main' or params['open_state'] == 'small' or param['open_state'] == 'none':
        if current_time > close_time:
            params['open_state'] = 'reset'

    set_doors(params['open_state'])
