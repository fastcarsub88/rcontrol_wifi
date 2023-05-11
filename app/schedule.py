import requests,json,time
from datetime import datetime
from ipcqueue import posixmq
from functions import *

queue = posixmq.Queue('/rcontrol')

last_weather_check = 0
weather = {}
params = load_params()

feels_like = 50.00
open_time = 1000
close_time = 1700

def update_conditions(location):
    wind_dir_dict = {
    0  : "N",
    45 : "NE",
    90 : "E",
    135: "SE",
    180: "S",
    225: "SW",
    270: "W",
    315: "NW",
    360: "N"
    }
    weather_string = 'lat='+location['lat']+"&lon="+location['lon']+"&appid=914fd2c984f8077049df587218d8579d&units=imperial"
    try:
        w_data = requests.get("https://api.openweathermap.org/data/2.5/weather?"+weather_string)
    except Exception as e:
        with open('errors','a') as f:
            f.write(repr(e)+"\n")
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

while True:
    time.sleep(5)
    current_time = int(datetime.now().strftime('%H:%M').replace(":",''))
    new_params = check_new_params():
    if new_params:
        params = new_params
        open_time,close_time = update_open_close_times(weather,params)
        save_params(new_params)
        save_status(open_time,close_time,params['auto'])

    if (current_time - last_weather_check) > 10 or last_weather_check > current_time:
        last_weather_check = current_time
        params = load_params()
        weather_check = update_conditions(params['location'])
        if weather_check:
            weather = weather_check
            open_time,close_time = update_open_close_times(weather,params)
            feels_like = weather['feels_like']
            save_status(open_time,close_time,params['auto'])

    if params['open_state'] == 'reset':
        if current_time >= open_time:
            params['open_state'] = 'main'
            if feels_like < params['sm_door_temp']:
                params['open_state'] = 'small'
            if feels_like < params['min_temp']:
                params['open_state'] = 'none'
            save_params(params)

    if params['open_state'] == 'main' or params['open_state'] == 'small' or params['open_state'] == 'none':
        if current_time >= close_time:
            params['open_state'] = 'reset'
            save_params(params)

    for index,value in enumerate(params['nodes']):
        if params['auto'][value] == 'true':
            if params['open_state'] == 'reset' or params['open_state'] == 'none':
                close_door(params['nodes'],0,value)
                close_door(params['nodes'],1,value)
            if params['open_state'] == "main":
                if params['door_config'] == 'all_same':
                    open_door(params['nodes'],0,value)
                    open_door(params['nodes'],1,value)
                if params['door_config'] == 'big_small':
                    open_door(params['nodes'],0,value)
                    close_door(params['nodes'],1,value)
            if params['open_state'] == 'small':
                open_door(params['nodes'],1,value)
                close_door(params['nodes'],0,value)
