import os
import requests
from datetime import datetime, timedelta
import pandas as pd
import pytz
from kiteconnect import KiteConnect

# =========================================
# ENV VARIABLES
# =========================================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

FREE_CHANNELS = [
    os.getenv("CHANNEL_FREE_MAIN"),
    os.getenv("CHANNEL_FREE_SIGNALS"),
]

PREMIUM_CHANNELS = [
    os.getenv("CHANNEL_PREMIUM"),
    os.getenv("CHANNEL_PREMIUM_ELITE"),
]

# =========================================
# ZERODHA CONNECTION
# =========================================
kite = None
try:
    kite = KiteConnect(api_key=KITE_API_KEY)
    kite.set_access_token(KITE_ACCESS_TOKEN)
    profile = kite.profile()
    print(f"✅ Zerodha Connected Successfully: {profile['user_name']}")
except Exception as e:
    print("❌ Zerodha Connection Failed Hard:", e)
    exit()

# =========================================
# LOAD INSTRUMENT MAP (Master NSE Token Registry)
# =========================================
instrument_map = {}
try:
    instruments = kite.instruments("NSE")
    for item in instruments:
        instrument_map[item["tradingsymbol"]] = item["instrument_token"]
    print(f"✅ Loaded {len(instrument_map)} Active NSE Instruments Into Memory")
except Exception as e:
    print("❌ Instrument Load Error:", e)
    exit()

# =========================================
# LOAD AND CLEAN FNO STOCKS CSV
# =========================================
WATCHLIST = []
try:
    df = pd.read_csv("fno_stocks.csv")
    raw_symbols = df.iloc[:, 0].dropna().tolist()
    
    for stock in raw_symbols:
        # Clean string formats and strip out any .NS or .BSE Yahoo suffixes
        clean_stock = str(stock).strip().upper().split('.')[0]
        
        if clean_stock and clean_stock != "NAN" and clean_stock != "TRADINGSYMBOL":
            if clean_stock in instrument_map:
                if clean_stock not in WATCHLIST:
                    WATCHLIST.append(clean_stock)
            else:
                print(f"⚠️ Stock {clean_stock} from CSV not found in NSE Live Registry")
                
    print(f"🎯 Final Validated Watchlist Count: {len(WATCHLIST)} F&O Symbols matched with Zerodha")
except Exception as e:
    print("❌ Critical CSV Load Error:", e)
    exit()

# =========================================
# TELEGRAM DISPATCHER
# =========================================
def send_message(channels, text):
    for ch in channels:
        if not ch:
            continue
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": ch,
                "text": text,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, data=payload, timeout=20)
            print(f"✅ Telegram Sent -> {ch} | Response Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Telegram Delivery Failure to {ch}:", e)

# =========================================
# FETCH VALID DATA FROM ZERODHA
# =========================================
def fetch_stock(symbol):
    try:
        token = instrument_map[symbol]
        
        # Expand historical window back by 5 days to safely catch past structural candles
        end_date = datetime.now(pytz.timezone('Asia/Kolkata'))
        start_date = end_date - timedelta(days=5)

        data = kite.historical_data(
            instrument_token=token,
            from_date=start_date.strftime("%Y-%m-%d %H:%M:%S"),
            to_date=end_date.strftime("%Y-%m-%d %H:%M:%S"),
            interval="day"
        )

        if not data or len(data) < 2:
            print(f"⚠️ Insufficient Candle Depth for {symbol}")
            return None

        # Extract last two settled historical entries safely
        latest = data[-1]
        prev = data[-2]

        close = float(latest["close"])
        prev_close = float(prev["close"])
        volume = int(latest["volume"])

        change = ((close - prev_close) / prev_close) * 100

        return {
            "symbol": symbol,
            "close": round(close, 2),
            "change": round(change, 2),
            "volume": volume
        }

    except Exception as e:
        print(f"❌ Structural Processing Error on Ticker {symbol}: {e}")
        return None

# =========================================
# INSTITUTIONAL SCANNING ENGINE
# =========================================
def generate_signals():
    signals = []

    for symbol in WATCHLIST:
        data = fetch_stock(symbol)
        if not data:
            continue

        probability = 50

        # High-Status Momentum Adjustments
        if data["change"] > 2:
            probability += 20
        if data["change"] > 4:
            probability += 20
        if data["volume"] > 1000000:
            probability += 15
        if data["change"] > 6:
            probability += 10

        probability = min(probability, 95)

        print(f"🔍 Evaluated: {data['symbol']} | Price: ₹{data['close']} | Move: {data['change']}% | Match Strength: {probability}%")

        # Keep tracks that pass the institutional gatekeeper criteria
        if probability >= 70:
            signals.append({
                "symbol": data["symbol"],
                "change": data["change"],
                "close": data["close"],
                "volume": data["volume"],
                "probability": probability
            })

    # Sort descending by breakout probability strength and slice top 5 setups
    return sorted(signals, key=lambda x: x["probability"], reverse=True)[:5]

# =========================================
# FORMAT MESSAGES
# =========================================
def free_message(signals):
    msg = "📊 *END OF DAY MARKET REPORT*\n\n"
    if not signals:
        msg += "⚠️ No high probability structural setups identified today.\n"
    else:
        msg += "🔥 *Strong Institutional Closing Breakouts:*\n\n"
        for s in signals:
            msg += f"• *{s['symbol']}* Structure Shift ({s['change']}%)\n"
    msg += "\n🔐 *Premium gives exact algorithmic entry points, stop-losses, and core targets.*"
    msg += f"\n\n⏰ Execution Clock: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')} IST"
    return msg

def premium_message(signals):
    msg = "🏦 *MULTIBAGGER ALGORITHMIC REPORT*\n\n"
    if not signals:
        msg += "⚠️ No institutional setups detected passing standard baseline parameters.\n"
    else:
        for s in signals:
            msg += (
                f"🔥 *Sectors Momentum: {s['symbol']}*\n"
                f"📈 Day Move: {s['change']}%\n"
                f"🎯 Match Strength: {s['probability']}%\n"
                f"💰 Smart Closing Price: ₹{s['close']}\n"
                f"📊 Institutional Volume: {s['volume']:,}\n\n"
            )
    msg += "📌 *Trading Strategy:* Focus strictly on institutional momentum continuation structures tomorrow morning.\n"
    msg += "\n⚠️ _Educational analysis framework only._"
    msg += f"\n⏰ Execution Clock: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')} IST"
    return msg

# =========================================
# MAIN EXECUTION CORE
# =========================================
if __name__ == "__main__":
    try:
        print("====================================")
        print("🚀 RUNNING MULTIBAGGER SCANNER ENGINE")
        print("====================================")

        signals = generate_signals()
        print(f"📊 Filtering Done. High-Status Setups Retained: {len(signals)}")

        send_message(FREE_CHANNELS, free_message(signals))
        send_message(PREMIUM_CHANNELS, premium_message(signals))

        print("====================================")
        print("✅ ALGORITHMIC SCANNER COMPLETE")
        print("====================================")
    except Exception as e:
        print("❌ Critical Breakdown in Main Engine Layer:", e)
