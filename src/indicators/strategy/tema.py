from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class TEMA(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> TEMA (Triple EMA)
    """

    def __init__(self):
        super().__init__(IndicatorName.TEMA.name)

    def compute_signals(self, df, params):
        period = params.get('period', 21)
        ema1 = df['close'].ewm(span=period, adjust=False).mean()
        ema2 = ema1.ewm(span=period, adjust=False).mean()
        ema3 = ema2.ewm(span=period, adjust=False).mean()
        tema = 3 * (ema1 - ema2) + ema3
        df['TEMA'] = tema
        cross_up = (df['close'] > tema) & (df['close'].shift(1) <= tema.shift(1))
        cross_down = (df['close'] < tema) & (df['close'].shift(1) >= tema.shift(1))
        df['TEMA_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['TEMA_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
