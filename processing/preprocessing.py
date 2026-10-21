def add_warm_clothes_flag(weather: dict) -> dict:
    return {**weather, "warm_clothes": weather["temp_c"] < 0}


def add_expensive_flag(rate_to_rub: float) -> dict:
    return {"rate_to_rub": rate_to_rub, "expensive": rate_to_rub > 100}