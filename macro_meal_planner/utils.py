def round_5g(val: float) -> int:
    return int(5 * round(val / 5))

def unit_portion(qty: float, unit_weight: float, food_name: str) -> str:
    unit_qty = qty / unit_weight
    rounded = round(unit_qty)
    if abs(unit_qty - rounded) <= 0.2:
        unit_qty = rounded
    return f"{int(unit_qty)} {food_name}" if unit_qty >= 1 else "Quantità insufficente utilizzare altri alimenti"
