from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class PSAR(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Parabolic SAR (PSAR)
    """

    def __init__(self):
        super().__init__(IndicatorName.PSAR.name)

    def compute_signals(self, df, params):
        # TODO - Implemented as trend direction change (use third party lib for more accurate!)
        af = 0.02
        max_af = 0.2
        uptrend = True
        psar = [df['low'].iloc[0]]
        for i in range(1, len(df)):
            prev_psar = psar[-1]
            if uptrend:
                psar.append(prev_psar + af * (df['high'].iloc[i - 1] - prev_psar))
                if df['low'].iloc[i] < psar[-1]:
                    uptrend = False
                    psar[-1] = df['high'].iloc[i - 1]
            else:
                psar.append(prev_psar + af * (df['low'].iloc[i - 1] - prev_psar))
                if df['high'].iloc[i] > psar[-1]:
                    uptrend = True
                    psar[-1] = df['low'].iloc[i - 1]
        df['PSAR'] = psar
        # Signal: trend change
        cross_up = (df['close'] > df['PSAR']) & (df['close'].shift(1) <= pd.Series(psar).shift(1))
        cross_down = (df['close'] < df['PSAR']) & (df['close'].shift(1) >= pd.Series(psar).shift(1))
        df['PSAR_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['PSAR_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
