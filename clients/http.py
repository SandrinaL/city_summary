import logging
import random
import time

import requests

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
TIMEOUT = (3, 7)
RETRY_STATUSES = {500, 502, 503, 504}


class ExternalServiceError(Exception):
    """Внешний сервис недоступен после retry."""


def get_json(url: str, params: dict | None = None) -> dict:
    last_exc: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT)
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as exc:
            last_exc = exc
            logger.warning("network error attempt=%s url=%s err=%s", attempt, url, exc)
        else:
            if response.status_code in RETRY_STATUSES:
                last_exc = ExternalServiceError(f"status={response.status_code}")
                logger.warning("5xx attempt=%s url=%s status=%s", attempt, url, response.status_code)
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "1")
                try:
                    delay = float(retry_after)
                except ValueError:
                    delay = 1.0
                last_exc = ExternalServiceError("429 rate limit")
                logger.warning("429 attempt=%s url=%s retry_after=%s", attempt, url, delay)
                if attempt < MAX_ATTEMPTS:
                    time.sleep(delay)
                    continue
            else:
                response.raise_for_status()
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError as exc:
                    raise ExternalServiceError(f"non-JSON response from {url}") from exc

        if attempt < MAX_ATTEMPTS:
            delay = 2 ** (attempt - 1) + random.uniform(0, 0.5)
            time.sleep(delay)

    raise ExternalServiceError(f"{url} failed after {MAX_ATTEMPTS} attempts") from last_exc
