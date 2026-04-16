"""
Telegram Auto Report Engine
- Sends PreMarket Report
- Sends EOD Report
- Sends Top Setup Alerts
"""

import logging
from datetime import datetime

from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


class TelegramReportEngine:

    def __init__(self):

        self.poster = TelegramPoster()

    # -----------------------------
    # 🚀 PREMARKET REPORT
    # -----------------------------
    def send_premarket_report(self, global_data, top_setups):

        msg = f"""
🚀 *PREMARKET MARKET INTELLIGENCE REPORT*

📅 Date: {datetime.now().strftime('%Y-%m-%d')}

🌍 *GLOBAL BIAS:* {global_data.get('overall_bias')}

━━━━━━━━━━━━━━━━━━
🔥 TOP STOCK SETUPS
━━━━━━━━━━━━━━━━━━
"""

        for s in top_setups:
            msg += (
                f"\n📌 {s['symbol']}"
                f"\n💰 Price: {s['price']}"
                f"\n📊 Surge: {s['surge']}x"
                f"\n🎯 Score: {s['score']}"
                f"\n----------------------"
            )

        msg += "\n\n⚠️ This is system-generated analysis, not financial advice."

        self.poster.send_message("premium", msg)

        logger.info("✅ Premarket Telegram report sent")

    # -----------------------------
    # 📉 EOD REPORT
    # -----------------------------
    def send_eod_report(self, eod_data):

        msg = f"""
📉 *EOD MARKET SUMMARY*

📅 {datetime.now().strftime('%Y-%m-%d')}

📊 Top Gainers:
{', '.join(eod_data.get('top_gainers', []))}

📈 Volume Breakouts:
{', '.join(eod_data.get('volume_breakouts', []))}

🧠 Market Summary:
{eod_data.get('market_summary')}

⚠️ Auto-generated report.
"""

        self.poster.send_message("premium", msg)

        logger.info("✅ EOD Telegram report sent")

    # -----------------------------
    # 🔥 LIVE SIGNAL ALERT
    # -----------------------------
    def send_signal_alert(self, signal):

        msg = f"""
🔥 *NEW TRADE SETUP DETECTED*

📌 Symbol: {signal['symbol']}
💰 Price: {signal['price']}
📊 Surge: {signal['surge_ratio']}x
🎯 Strength: {signal['strength']}

📦 Support: {signal['support']}
🚀 Resistance: {signal['resistance']}

⚠️ System Generated Signal
"""

        self.poster.send_message("free", msg)

        logger.info(f"🔥 Signal alert sent: {signal['symbol']}")
