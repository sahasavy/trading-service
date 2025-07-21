from src.indicators.impl.ema_cross import EMACross
from src.indicators.impl.sma_cross import SMACross
from src.indicators.impl.rsi import RSI
from src.indicators.impl.adx import ADX
from src.indicators.impl.bollinger import Bollinger
from src.indicators.impl.cci import CCI
from src.indicators.impl.donchian import Donchian
from src.indicators.impl.macd import MACD
from src.indicators.impl.super_trend import SuperTrend
from src.indicators.impl.volume_spike import VolumeSpike

INDICATOR_REGISTRY = {
    "EMA_CROSS": EMACross,
    "SMA_CROSS": SMACross,
    "RSI": RSI,
    "ADX": ADX,
    "BOLLINGER": Bollinger,
    "CCI": CCI,
    "DONCHIAN": Donchian,
    "MACD": MACD,
    "SUPER_TREND": SuperTrend,
    "VOLUME_SPIKE": VolumeSpike,
}


def get_indicator(name):
    ind = INDICATOR_REGISTRY.get(name)
    if not ind:
        raise ValueError(f"Indicator {name} not found in registry.")
    return ind
