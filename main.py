import argparse
import json
import logging
import sys
import uuid

from clients.http import ExternalServiceError
from clients.rates import CurrencyNotFoundError
from clients.weather import CityNotFoundError
from processing.service import build_city_summary


def setup_logging(run_id: str) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s [%(levelname)s] run_id={run_id} %(name)s: %(message)s",
    )


def main() -> int:
    run_id = str(uuid.uuid4())[:8]
    setup_logging(run_id)
    logger = logging.getLogger("main")

    parser = argparse.ArgumentParser(description="Сводка по городу")
    parser.add_argument("--city", required=True, help="Название города")
    parser.add_argument("--currency", default="USD", help="ISO-код валюты (по умолчанию USD)")
    parser.add_argument("--json", action="store_true", help="Вывод в формате JSON")
    args = parser.parse_args()

    currency = args.currency.upper()
    logger.info("Starting summary for city=%s currency=%s", args.city, currency)

    try:
        summary = build_city_summary(args.city, currency)
    except (CityNotFoundError, CurrencyNotFoundError) as exc:
        logger.error("Not found: %s", exc)
        print(f"Не найдено: {exc}", file=sys.stderr)
        return 3
    except ExternalServiceError as exc:
        logger.error("External service error: %s", exc)
        print(f"Внешний сервис недоступен: {exc}", file=sys.stderr)
        return 4

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        weather = summary["weather"]
        rates = summary["rates"]
        print(f"Город: {summary['city']}")
        print(f"Погода: {weather['temp_c']:.1f}°C, {weather['description']}")
        print(f"Тёплая одежда: {'да' if weather['warm_clothes'] else 'нет'}")
        print(f"{rates['currency']}→RUB: {rates['rate_to_rub']:.2f}")
        print(f"Дорогой курс: {'да' if rates['expensive'] else 'нет'}")

    logger.info("Summary successfully built")
    return 0


if __name__ == "__main__":
    sys.exit(main())