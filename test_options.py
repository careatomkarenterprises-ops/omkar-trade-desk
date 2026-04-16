from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
import pandas as pd

engine = OptionsIntelligenceEngine()

dummy = pd.DataFrame({
    "close": [22000, 22100, 22250, 22300],
    "volume": [100, 120, 130, 150]
})

result = engine.generate_options_signal(dummy, dummy)

print(result)
