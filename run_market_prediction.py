import os
import requests
from datetime import datetime

# =========================================
# ENV CONFIGURATION
# =========================================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FREE_CHANNEL = os.getenv("CHANNEL_FREE_MAIN")
PREMIUM_CHANNEL = os.getenv("CHANNEL_PREMIUM")
ELITE_CHANNEL = os.getenv("CHANNEL_PREMIUM_ELITE")

# =========================================
# NATIVE TELEGRAM DISPATCH
# =========================================
def send(msg, channel):
    if not channel:
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        response = requests.post(
            url,
            data={
                "chat_id": channel,
                "text": msg,
                "parse_mode": "Markdown"
            },
            timeout=20
        )
        if response.status_code == 200:
            print(f"✅ Sent to {channel}")
        else:
            print(f"❌ Telegram Error Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Telegram Exception: {e}")

# =========================================
# LIGHTWEIGHT NATIVE MACRO DATA FETCH
# =========================================
def fetch_data():
    """
    Fetches international indices and global assets using clean, native 
    HTTP structures, completely bypassing the need for yfinance.
    """
    try:
        print("🔄 Pulling Global Macro Trends via Direct Engine Data Core...")
        url = "https://query1.finance.yahoo.com/v7/finance/spark"
        params = {
            "symbols": "^DJI,^IXIC,^GSPC,^NSEI,CL=F,GC=F,SI=F,INR=X,DX-Y.NYB",
            "range": "2d",
            "interval": "1d"
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Macro Gateway Rejected: {response.status_code}")
            return {}

        raw_results = response.json().get("spark", {}).get("result", [])
        
        ticker_mapping = {
            "^DJI": "DOW", "^IXIC": "NASDAQ", "^GSPC": "SP500",
            "^NSEI": "GIFTNIFTY", "CL=F": "CRUDE", "GC=F": "GOLD",
            "SI=F": "SILVER", "INR=X": "USDINR", "DX-Y.NYB": "DXY"
        }
        
        processed_data = {}
        for item in raw_results:
            symbol = item.get("symbol")
            name = ticker_mapping.get(symbol)
            if not name:
                continue
                
            response_data = item.get("response", [{}])[0]
            indicators = response_data.get("indicators", {}).get("quote", [{}])[0]
            close_prices = indicators.get("close", [])
            
            close_prices = [c for c in close_prices if c is not None]
            if len(close_prices) < 2:
                continue
                
            prev_close = close_prices[-2]
            latest_close = close_prices[-1]
            pct_change = ((latest_close - prev_close) / prev_close) * 100
            
            processed_data[name] = {
                "price": round(latest_close, 2),
                "change": round(pct_change, 2)
            }
            
        return processed_data
    except Exception as e:
        print(f"❌ Macro Fetch Error: {e}")
        return {}

# =========================================
# MARKET ANALYSIS
# =========================================
def analyze_market(data):
    score = 0
    score += data.get("DOW", {}).get("change", 0)
    score += data.get("NASDAQ", {}).get("change", 0)
    score += data.get("SP500", {}).get("change", 0)
    score += data.get("GIFTNIFTY", {}).get("change", 0) * 2

    if score > 2:
        bias = "🟢 BULLISH"
    elif score < -2:
        bias = "🔴 BEARISH"
    else:
        bias = "🟡 SIDEWAYS"

    return bias, round(score, 2)

# =========================================
# ESTIMATE NIFTY RANGE
# =========================================
def estimate_range(score):
    nifty_base = 25000
    move = int(score * 120)
    open_price = nifty_base + move
    return open_price, (open_price - 180), (open_price + 180)

# =========================================
# BUILD TELEGRAM MESSAGE
# =========================================
def build_message(data, bias, score):
    open_p, support, resistance = estimate_range(score)
    
    msg = "📈 *AI PRE-MARKET INTELLIGENCE*\n\n"
    msg += f"🧠 Market Bias: {bias}\n"
    msg += f"⚡ Global Score: {score}\n\n"
    
    msg += "*🌍 GLOBAL MARKETS*\n"
    for key in ["DOW", "NASDAQ", "SP500"]:
        if key in data:
            msg += f"• {key}: {data[key]['change']}%\n"
            
    msg += "\n*🇮🇳 INDIA OUTLOOK*\n"
    if "GIFTNIFTY" in data:
        msg += f"• GIFT NIFTY: {data['GIFTNIFTY']['change']}%\n"
    msg += f"• Expected Open: {open_p}\n"
    msg += f"• Resistance: {resistance}\n"
    msg += f"• Support: {support}\n"
    
    msg += "\n*🛢 COMMODITIES*\n"
    for key in ["CRUDE", "GOLD", "SILVER"]:
        if key in data:
            msg += f"• {key}: {data[key]['change']}%\n"
            
    msg += "\n*💵 CURRENCY*\n"
    for key in ["USDINR", "DXY"]:
        if key in data:
            msg += f"• {key}: {data[key]['change']}%\n"
            
    msg += f"\n⚠️ Educational Purpose Only\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    return msg

# =========================================
# RUN TIME DISPATCH ENTRY
# =========================================
if __name__ == "__main__":
    print("=======================================")
    print("🚀 RUNNING AI PRE-MARKET ENGINE")
    print("=======================================")
    
    data = fetch_data()
    if not data:
        print("❌ CRITICAL: Market context map extraction failure.")
        send("⚠️ Pre-Market processing pipeline data unavailable.", FREE_CHANNEL)
        exit()

    bias, score = analyze_market(data)
    message = build_message(data, bias, score)
    
    send(message, FREE_CHANNEL)
    send(message, PREMIUM_CHANNEL)
    send(message, ELITE_CHANNEL)
    
    print("=======================================")
    print("✅ MARKET PREDICTION COMPLETED")
    print("=======================================")
