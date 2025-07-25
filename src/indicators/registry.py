from src.commons.constants.constants import IndicatorName
from src.indicators.strategy.adx import ADX
from src.indicators.strategy.aroon import Aroon
from src.indicators.strategy.atr import ATR
from src.indicators.strategy.bollinger import Bollinger
from src.indicators.strategy.cci import CCI
from src.indicators.strategy.cmf import ChaikinMF
from src.indicators.strategy.dema import DEMA
from src.indicators.strategy.donchian_channel import Donchian
from src.indicators.strategy.ema_cross import EMACross
from src.indicators.strategy.envelope import Envelope
from src.indicators.strategy.hull_ma import HullMA
from src.indicators.strategy.keltner_channel import Keltner
from src.indicators.strategy.macd import MACD
from src.indicators.strategy.mfi import MFI
from src.indicators.strategy.momentum import Momentum
from src.indicators.strategy.obv import OBV
from src.indicators.strategy.pivot_points import Pivot
from src.indicators.strategy.psar import PSAR
from src.indicators.strategy.roc import ROC
from src.indicators.strategy.rsi import RSI
from src.indicators.strategy.sma_cross import SMACross
from src.indicators.strategy.stochastic_oscillator import Stochastic
from src.indicators.strategy.stochastic_rsi import StochRSI
from src.indicators.strategy.super_trend import SuperTrend
from src.indicators.strategy.tema import TEMA
from src.indicators.strategy.trix import TRIX
from src.indicators.strategy.ultimate_oscillator import UltimateOsc
from src.indicators.strategy.volume_spike import VolumeSpike
from src.indicators.strategy.vwap import VWAP
from src.indicators.strategy.williams_r import WilliamsR

INDICATOR_STRATEGY_REGISTRY = {
    IndicatorName.EMA_CROSS.value: EMACross,
    IndicatorName.SMA_CROSS.value: SMACross,
    IndicatorName.RSI.value: RSI,
    IndicatorName.MACD.value: MACD,
    IndicatorName.SUPER_TREND.value: SuperTrend,
    IndicatorName.ADX.value: ADX,
    IndicatorName.BOLLINGER.value: Bollinger,
    IndicatorName.CCI.value: CCI,
    IndicatorName.DONCHIAN.value: Donchian,
    IndicatorName.VOLUME_SPIKE.value: VolumeSpike,
    IndicatorName.WILLIAMS_R.value: WilliamsR,
    IndicatorName.STOCHASTIC.value: Stochastic,
    IndicatorName.ATR.value: ATR,
    IndicatorName.KELTNER.value: Keltner,
    IndicatorName.ROC.value: ROC,
    IndicatorName.OBV.value: OBV,
    IndicatorName.ULTIMATE_OSC.value: UltimateOsc,
    IndicatorName.MOMENTUM.value: Momentum,
    IndicatorName.PSAR.value: PSAR,
    IndicatorName.ENVELOPE.value: Envelope,
    IndicatorName.PIVOT.value: Pivot,
    IndicatorName.VWAP.value: VWAP,
    IndicatorName.MFI.value: MFI,
    IndicatorName.CHAIKIN_MF.value: ChaikinMF,
    IndicatorName.AROON.value: Aroon,
    IndicatorName.TEMA.value: TEMA,
    IndicatorName.DEMA.value: DEMA,
    IndicatorName.HULL_MA.value: HullMA,
    IndicatorName.STOCH_RSI.value: StochRSI,
    IndicatorName.TRIX.value: TRIX,
}


def get_indicator(name):
    indicator = INDICATOR_STRATEGY_REGISTRY.get(name)
    if not indicator:
        raise ValueError(f"Indicator {name} not found in registry.")
    return indicator


def add_signals(df, strategy_name, strategy_params):
    strat_enum = IndicatorName(strategy_name) if not isinstance(strategy_name, IndicatorName) else strategy_name
    strat_cls = INDICATOR_STRATEGY_REGISTRY.get(strat_enum.value)
    if not strat_cls:
        raise ValueError(f"Unsupported strategy: {strategy_name}")
    strat_cls.compute_signals(df, strategy_params)
