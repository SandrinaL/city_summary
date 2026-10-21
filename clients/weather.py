from clients.http import ExternalServiceError, get_json


class CityNotFoundError(Exception):
    pass


GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_DESCRIPTIONS = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "depositing rime fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow",
    80: "rain showers", 95: "thunderstorm",
}


def get_weather(city: str) -> dict:
    geo = get_json(GEO_URL, params={"name": city, "count": 1, "language": "en", "format": "json"})
    results = geo.get("results") or []
    if not results:
        raise CityNotFoundError(city)

    lat = results[0]["latitude"]
    lon = results[0]["longitude"]
    name = results[0].get("name", city)

    forecast = get_json(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code",
            "timezone": "auto",
        },
    )

    current = forecast.get("current") or {}
    if "temperature_2m" not in current:
        raise ExternalServiceError("no temperature in forecast response")

    code = int(current.get("weather_code", -1))
    return {
        "city": name,
        "temp_c": float(current["temperature_2m"]),
        "description": WEATHER_DESCRIPTIONS.get(code, "unknown"),
    }
    