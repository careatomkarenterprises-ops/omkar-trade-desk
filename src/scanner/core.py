import datetime
import random


def fetch_market_data():
    """
    Dummy market data generator (replace with real API later)
    """
    stocks = [
        {"symbol": "RELIANCE", "price": random.uniform(2400, 2600)},
        {"symbol": "TCS", "price": random.uniform(3200, 3500)},
        {"symbol": "HDFCBANK", "price": random.uniform(1400, 1600)},
        {"symbol": "INFY", "price": random.uniform(1300, 1500)},
        {"symbol": "ICICIBANK", "price": random.uniform(900, 1100)},
    ]
    return stocks


def calculate_score(stock):
    """
    Simple scoring logic (you can upgrade this later)
    """
    price = stock.get("price", 0)

    # Example logic
    score = 0

    if price > 2000:
        score += 2
    if price % 2 == 0:
        score += 1

    return score


def scan_market():
    """
    Main scanner logic
    """
    data = fetch_market_data()
    patterns = []

    for stock in data:
        score = calculate_score(stock)

        patterns.append({
            "symbol": stock.get("symbol"),
            "price": stock.get("price"),
            "score": score
        })

    # ✅ SAFE SORTING (NO ERROR)
    if patterns:
        patterns_sorted = sorted(
            patterns,
            key=lambda x: x.get("score", 0),
            reverse=True
        )
    else:
        patterns_sorted = []

    return patterns_sorted


def print_results(results):
    """
    Print scanner results
    """
    print("\n🔍 Omkar Market Scanner Results")
    print(f"⏰ Time: {datetime.datetime.now()}")
    print("-" * 40)

    if not results:
        print("No data found")
        return

    for item in results:
        print(
            f"{item.get('symbol')} | "
            f"Price: {round(item.get('price', 0), 2)} | "
            f"Score: {item.get('score')}"
        )


def main():
    """
    Entry point
    """
    try:
        results = scan_market()
        print_results(results)

    except Exception as e:
        print("❌ Error in scanner:", str(e))


# ✅ IMPORTANT (THIS MAKES IT RUN)
if __name__ == "__main__":
    main()
