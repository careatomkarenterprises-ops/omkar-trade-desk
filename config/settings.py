# Telegram channels – consolidated to 4
TELEGRAM_CHANNELS = {
    "free_main": "@OmkarFree",
    "free_signals": "@OmkarFreeSignals",
    "premium": "@OmkarPro",
    "premium_elite": "@OmkarProElite"
}

# Remove all old channel references (Nifty50, BankNifty, Swing, Intraday, FNO, Commodity, Currency, Education, TradeDesk, TradeDeskPro)
# Keep only these 4.

# Other settings (keep your existing API keys, etc.)
import os
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RAZORPAY_LINK = os.getenv("RAZORPAY_LINK", "")
