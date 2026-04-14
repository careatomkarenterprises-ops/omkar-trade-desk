name: 🚀 Omkar Multi-Segment Scanner

on:
  schedule:
    - cron: '15 3 * * 1-5'  # 08:45 AM IST (Morning Setup)
    - cron: '*/15 4-10 * * 1-5' # Every 15 mins during market hours
  workflow_dispatch:

jobs:
  market_scanner:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Restore Token Cache
        uses: actions/cache@v4
        with:
          path: data/
          key: market-tokens-${{ github.run_id }}
          restore-keys: |
            market-tokens-

      - name: Install Dependencies
        run: pip install -r requirements.txt

      - name: Morning Setup (Only at 8:45 AM)
        if: github.event.schedule == '15 3 * * 1-5'
        run: python -m src.scanner.morning_setup
        env:
          KITE_API_KEY: ${{ secrets.KITE_API_KEY }}
          KITE_ACCESS_TOKEN: ${{ secrets.KITE_ACCESS_TOKEN }}

      - name: Run Scanners (Market Hours)
        if: github.event.schedule != '15 3 * * 1-5'
        run: |
          python -m src.scanner.fno_agent
          python -m src.scanner.swing_agent
          python -m src.scanner.currency_agent
        env:
          KITE_API_KEY: ${{ secrets.KITE_API_KEY }}
          KITE_ACCESS_TOKEN: ${{ secrets.KITE_ACCESS_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
