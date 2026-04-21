from src.scanner.master_scanner import MasterScanner

if __name__ == "__main__":
    scanner = MasterScanner()
    scanner.scan_intraday_fno()
    scanner.scan_commodity()
    scanner.post_delayed_patterns()
