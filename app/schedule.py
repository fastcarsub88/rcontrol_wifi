import requests,json,time
from datetime import datetime
from functions import *

last_weather_check = 0
weather = {}
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

def get_conditions():
    weather_string = 'lat='+init.location['lat']+"&lon="+init.location['lon']+"&appid=914fd2c984f8077049df587218d8579d&units=imperial"
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
    init.load_params()
    params = init.params

    if (current_time - last_weather_check) > 10 or last_weather_check > current_time:
        last_weather_check = current_time
        weather_check = get_conditions()
        if weather_check:
            weather = weather_check
            init.update(weather)

    if read_message() == 'params_saved':
        init.update(weather)
        clear_message()

    feels_like = weather['feels_like']
    if params['open_state'] == 'reset':
        if current_time >= init.open_time:
            params['open_state'] = 'main'
            if feels_like < params['sm_door_temp']:
                params['open_state'] = 'small'
            if feels_like < params['min_temp']:
                params['open_state'] = 'none'
            init.params = params
            init.save_params()

    if params['open_state'] == 'main' or params['open_state'] == 'small' or params['open_state'] == 'none':
        if current_time >= init.close_time:
            params['open_state'] = 'reset'
            init.params = params
            init.save_params()

    for index,value in enumerate(init.nodes):
        if params['auto'][value] == 'true':
            if params['open_state'] == 'reset' or params['open_state'] == 'none':
                close_door(0,value)
                close_door(1,value)
            if params['open_state'] == "main":
                if params['door_config'] == 'all_same':
                    open_door(0,value)
                    open_door(1,value)
                if params['door_config'] == 'big_small':
                    open_door(0,value)
                    close_door(1,value)
            if params['open_state'] == 'small':
                open_door(1,value)
                close_door(0,value)
