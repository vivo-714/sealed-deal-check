"""Recompute market trends for Rip or Skip.

Reads history.json  {"series": {product_id: [["YYYY-MM-DD", price], ...]}}
Writes a "trend" object onto each product in prices.json:
  {"c30": fraction or null, "c90": fraction or null, "spark": [13 weekly medians, null for gaps], "n": points used}

Usage: python3 tools/trends.py [YYYY-MM-DD]   (defaults to prices.json "asOf")
"""
import json, sys, statistics
from datetime import date, timedelta

def clean(points):
    """Drop one-off outliers: points more than 25% away from the median of their 7 neighbours."""
    out = []
    for i, (d, p) in enumerate(points):
        window = [q for _, q in points[max(0, i - 3): i + 4]]
        m = statistics.median(window)
        if m and abs(p - m) / m <= 0.25:
            out.append((d, p))
    return out

def window_median(points, today, start_days, end_days, min_n=2):
    lo, hi = today - timedelta(days=start_days), today - timedelta(days=end_days)
    vals = [p for d, p in points if lo <= d <= hi]
    return statistics.median(vals) if len(vals) >= min_n else None

def trend(series, today):
    pts = sorted((date.fromisoformat(d), float(p)) for d, p in series)
    pts = [x for x in pts if today - timedelta(days=100) <= x[0] <= today]
    pts = clean(pts)
    now = window_median(pts, today, 10, 0)
    if now is None:
        now = window_median(pts, today, 17, 0, 1)
    def change(back):
        then = window_median(pts, today, back + 6, back - 6)
        if then is None:
            then = window_median(pts, today, back + 10, back - 10)
        return round(now / then - 1, 4) if now and then else None
    spark = []
    for w in range(12, -1, -1):
        hi = today - timedelta(days=7 * w)
        vals = [p for d, p in pts if hi - timedelta(days=6) <= d <= hi]
        spark.append(round(statistics.median(vals), 2) if vals else None)
    return {"c30": change(30), "c90": change(90), "spark": spark, "n": len(pts)}

def main():
    prices = json.load(open("prices.json"))
    hist = json.load(open("history.json"))["series"]
    today = date.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else prices["asOf"])
    for p in prices["products"]:
        s = hist.get(p["id"])
        p["trend"] = trend(s, today) if s else {"c30": None, "c90": None, "spark": [None] * 13, "n": 0}
    json.dump(prices, open("prices.json", "w"), indent=1, ensure_ascii=False)
    moved = sorted((p for p in prices["products"] if p["trend"]["c30"] is not None), key=lambda p: p["trend"]["c30"])
    print("products with 30d trend:", len(moved), "of", len(prices["products"]))
    for p in moved[:3] + moved[-3:]:
        print(f'  {p["set"]} {p["type"]}: 30d {p["trend"]["c30"]:+.1%}  90d {p["trend"]["c90"] if p["trend"]["c90"] is None else format(p["trend"]["c90"], "+.1%")}')

if __name__ == "__main__":
    main()
