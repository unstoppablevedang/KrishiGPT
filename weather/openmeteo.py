import requests
GEOCODING_URL='https://geocoding-api.open-meteo.com/v1/search'; FORECAST_URL='https://api.open-meteo.com/v1/forecast'
def geocode_city(city):
 r=requests.get(GEOCODING_URL,params={'name':city,'count':1,'language':'en','format':'json'},timeout=10); r.raise_for_status(); a=r.json().get('results') or []
 if not a:return None
 x=a[0]; return {'name':x.get('name'),'country':x.get('country'),'latitude':x['latitude'],'longitude':x['longitude'],'timezone':x.get('timezone')}
def get_weather(city):
 loc=geocode_city(city)
 if not loc:return None
 r=requests.get(FORECAST_URL,params={'latitude':loc['latitude'],'longitude':loc['longitude'],'current':'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m','hourly':'temperature_2m,precipitation_probability,precipitation,relative_humidity_2m','forecast_days':2,'timezone':'auto'},timeout=12); r.raise_for_status()
 return {'location':loc,'forecast':r.json()}
