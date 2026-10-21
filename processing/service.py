from clients.rates import get_rate
from clients.weather import get_weather
from processing.preprocessing import add_expensive_flag, add_warm_clothes_flag


def build_city_summary(city: str, currency: str = "USD") -> dict:
    weather = get_weather(city)
    rate = get_rate(currency)

    return {
        "city": weather["city"],
        "weather": add_warm_clothes_flag(weather),
        "rates": {
            "currency": currency,
            **add_expensive_flag(rate),
        },
    }
    