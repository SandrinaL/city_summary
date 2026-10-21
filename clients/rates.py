from clients.http import ExternalServiceError, get_json
import time
_cache = {}


class CurrencyNotFoundError(Exception):
    pass


RATE_URL = "https://api.frankfurter.dev/v2/rate/{currency}/RUB"


def get_rate(currency: str) -> float:
    # Кэш на 5 минут (300 секунд)
    if currency in _cache:
        rate, timestamp = _cache[currency]
        if time.time() - timestamp < 300:
            return rate

    try:
        data = get_json(RATE_URL.format(currency=currency))
    except Exception as exc:
        if "404" in str(exc):
            raise CurrencyNotFoundError(currency) from exc
        raise

    rate = data.get("rate")
    if rate is None and "rates" in data:
        rate = data["rates"].get("RUB")
        
    if rate is None:
        raise CurrencyNotFoundError(currency)
    
    rate = float(rate)
    _cache[currency] = (rate, time.time())  # сохраняем в кэш
    return rate
