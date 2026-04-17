"""Daily budget cost guard."""
import time

from fastapi import HTTPException

from app.config import settings

_daily_cost: float = 0.0
_cost_reset_day: str = time.strftime("%Y-%m-%d")

# GPT-4o-mini pricing: $0.15/1M input tokens, $0.60/1M output tokens
_INPUT_COST_PER_TOKEN = 0.00015 / 1000
_OUTPUT_COST_PER_TOKEN = 0.0006 / 1000


def get_daily_cost() -> float:
    return _daily_cost


def check_and_record_cost(input_tokens: int, output_tokens: int) -> None:
    global _daily_cost, _cost_reset_day
    today = time.strftime("%Y-%m-%d")
    if today != _cost_reset_day:
        _daily_cost = 0.0
        _cost_reset_day = today
    if _daily_cost >= settings.daily_budget_usd:
        raise HTTPException(503, "Daily budget exhausted. Try tomorrow.")
    _daily_cost += input_tokens * _INPUT_COST_PER_TOKEN + output_tokens * _OUTPUT_COST_PER_TOKEN
