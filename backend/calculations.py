import math
from statistics import mean


def average_glucose(values):
    clean = [v for v in values if v is not None]
    return mean(clean) if clean else None


def time_in_range(values, lo=70, hi=180):
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    in_range = sum(1 for v in clean if lo <= v <= hi)
    return in_range / len(clean) * 100


def gmi(mean_glucose_mgdl):
    if mean_glucose_mgdl is None:
        return None
    return 3.31 + 0.02392 * mean_glucose_mgdl


def percent_delta(current, prior):
    if current is None or prior in (None, 0):
        return None
    return (current - prior) / prior * 100


def composite_score(pcts):
    clean = [p for p in pcts if p is not None]
    if not clean:
        return None
    return round(mean(clean))


def pearson_r(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 2:
        return None

    x_mean = mean(x for x, _ in pairs)
    y_mean = mean(y for _, y in pairs)
    x_dev = [x - x_mean for x, _ in pairs]
    y_dev = [y - y_mean for _, y in pairs]
    denominator = math.sqrt(sum(x * x for x in x_dev) * sum(y * y for y in y_dev))
    if denominator == 0:
        return None
    return sum(x * y for x, y in zip(x_dev, y_dev)) / denominator
