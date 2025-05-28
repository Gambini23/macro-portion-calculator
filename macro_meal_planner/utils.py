def round_5g(val: float) -> int:
    return int(5 * round(val / 5))

def egg_portion(grams: float) -> str:
    if grams <= 70:
        return "1 uovo"
    elif grams <= 130:
        return "2 uova"
    else:
        return f"{round_5g(grams)}g Uova"