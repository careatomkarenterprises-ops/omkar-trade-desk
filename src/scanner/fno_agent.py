import pandas as pd
from src.scanner.volume_analyzer import VolumeSetupAnalyzer
from src.scanner.data_fetcher import fetch_historical_data
from src.telegram.poster import send_alert

def scan_fno_stocks(fno_list, interval="3minute"):
    """Scan F&O stocks using volume setup on 3-min chart (all segments)"""
    analyzer = VolumeSetupAnalyzer()
    signals = []

    for symbol in fno_list:
        try:
            # Fetch 3-min data for current, next, far futures
            df = fetch_historical_data(symbol, interval=interval, days=5)
            if df is None or df.empty:
                continue

            setups = analyzer.detect_setups(df)
            if not setups:
                continue

            latest_setup = setups[-1]
            current_price = df['close'].iloc[-1]
            sma_cross = analyzer.check_sma_crossover(df)

            # Signal condition: breakout above top + SMA crossover
            if current_price > latest_setup['top'] and sma_cross:
                signals.append({
                    'symbol': symbol,
                    'type': 'LONG',
                    'entry': current_price,
                    'target': latest_setup['fab_50'],
                    'stop': latest_setup['stop_loss_long'],
                    'setup': latest_setup,
                    'timeframe': interval
                })
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

    return signals

def run_fno_scanner():
    """Main entry point called by GitHub Actions"""
    fno_list = pd.read_csv("fno_stocks.csv")['symbol'].tolist()
    signals = scan_fno_stocks(fno_list)

    for sig in signals:
        msg = (f"🔔 *F&O ALERT* - {sig['symbol']}\n"
               f"📊 Timeframe: 3-min\n"
               f"📈 Signal: {sig['type']}\n"
               f"💰 Entry: ₹{sig['entry']}\n"
               f"🎯 Target (50% FAB): ₹{sig['target']}\n"
               f"🛑 Stop: ₹{sig['stop']}\n"
               f"📐 Setup range: ₹{sig['setup']['range']}\n"
               f"🚀 Extensions: 1.272 | 1.618 | 2.0")
        send_alert(msg, channel="@OmkarPro")  # Premium channel

    return len(signals)
