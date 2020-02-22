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
            return main

        else:
            return None
