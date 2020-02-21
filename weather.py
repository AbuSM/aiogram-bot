import requests


class Weather:
    api_key = '40d73754f89f470fec630d7034ebecf2'
    api_address = 'http://api.openweathermap.org/data/2.5/weather'

    @staticmethod
    def get_weather_by_city(city):
        response = requests.get(Weather.api_address, params={'q': city, 'APPID': Weather.api_key, 'units': 'metric'})
        json_resp = response.json()
        if 'main' in json_resp:
            main = json_resp['main']
            temp = main.get('temp', '-'),
            temp_min = main.get('temp_min', '-'),
            temp_max = str(main.get('temp_max', '-')),
            pressure = str(main.get('pressure', '-')) + 'hPa',
            humidity = str(main.get('humidity', '-')) + '%',
            feels_like = str(main.get('feels_like', '-'))
            text = \
                "Temperature: {0}" \
                "Minimum temp: {1}" \
                "Maximum temp: {2}" \
                "Feels like: {3}" \
                "Pressure: {4}" \
                "Humidity: {5}".format(temp, temp_min, temp_max, feels_like, pressure, humidity)
            return text

        else:
            return 'Nothing found(('

