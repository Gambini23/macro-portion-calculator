from typing import Dict
from food_data import KCAL_PER_GRAM

def compute_macros(kcal: float, split: Dict[str, float]) -> Dict[str, float]:
    return {
        macro: round((kcal * perc) / KCAL_PER_GRAM[macro], 1) if macro != "fat" else round(((kcal * perc) / KCAL_PER_GRAM[macro]) * 0.5, 1)
        for macro, perc in split.items()
    }