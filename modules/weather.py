import config
import requests

class WeatherModule:
    def __init__(self):
        self.CITY = config.CITY
        self.weather_api_url = "https://api.open-meteo.com/v1/forecast"

    def getWeather(self):
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={self.CITY}&count=1"
            response = requests.get(url)
            responseData = response.json()
            if "results" not in responseData or len(responseData["results"]) == 0:
                return f"Error: Location '{self.CITY}' not found."
            
            first_result = responseData["results"][0]
            lat = first_result["latitude"]
            lon = first_result["longitude"]

            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True
            }

            weather_res = requests.get(self.weather_api_url, params=weather_params)
            weather_data = weather_res.json()
            current = weather_data.get("current_weather", {})
            temp = current.get("temperature")
            wind = current.get("windspeed")

            return f"It is currently {temp} degrees in {self.CITY} with a windspeed of {wind} kilometer per hour"
        except:
            return "Sorry, I couldn't fetch the weather right now"
    
if __name__ == "__main__":
    w = WeatherModule()
    print(w.getWeather())