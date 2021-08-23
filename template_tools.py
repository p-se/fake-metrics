from random import random
from typing import Dict, Callable, Any


metric_values: Dict[str, float] = {}

def chance(
    key: str,
    probability: float = 0.01,
    step_size: float = 1.0,
    start_value: float = 0.0,
):
    assert 0 < probability < 1  # chance needs to be between 0 and 1, but not 0 and 1.
    if not key in metric_values:
        metric_values[key] = start_value
    else:
        hit = random() < probability
        if hit:
            metric_values[key] += step_size

    return metric_values[key]

def increase(key: str, step_size: float = 1.0, start_value: float = 0.0):
    if not key in metric_values:
        metric_values[key] = start_value
    else:
        metric_values[key] += step_size

    return metric_values[key]

def reset(key: str):
    metric_values[key] = 0
    return metric_values[key]

def either(fn1: Callable[[], Any], fn2: Callable[[], Any], fn1_probability: float):
    assert 0 <= fn1_probability <= 1
    return fn1() if random() < 0.5 else fn2()

def increase_or_reset(
    key: str,
    step_size: float = 1.0,
    start_value: float = 0.0,
    reset_probability: float = 0.05
):
    if not key in metric_values:
        metric_values[key] = float(start_value)
        return metric_values[key]

    if random() < reset_probability:
        return reset(key)

    return increase(key, step_size=step_size)
