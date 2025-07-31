import pandas as pd

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class SuperTrend(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> SUPER TREND
    """

    def __init__(self):
        super().__init__(IndicatorName.SUPER_TREND.name)

    def compute_signals(self, df, params):
        if 'period' not in params or 'multiplier' not in params:
            raise ValueError(
                f"{self.name} params 'period' and 'multiplier' are required in backtest-config.yaml/indicator-config.yaml")

        period = params.get('period', 10)
        multiplier = params.get('multiplier', 3.0)
        high = df['high']
        low = df['low']
        close = df['close']
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period, min_periods=period).mean()
        hl2 = (high + low) / 2
        basic_ub = hl2 + (multiplier * atr)
        basic_lb = hl2 - (multiplier * atr)
        final_ub = basic_ub.copy()
        final_lb = basic_lb.copy()

        for i in range(1, len(df)):
            if close.iloc[i - 1] > final_ub.iloc[i - 1]:
                final_ub.iloc[i] = basic_ub.iloc[i]
            else:
                final_ub.iloc[i] = min(basic_ub.iloc[i], final_ub.iloc[i - 1])
            if close.iloc[i - 1] < final_lb.iloc[i - 1]:
                final_lb.iloc[i] = basic_lb.iloc[i]
            else:
                final_lb.iloc[i] = max(basic_lb.iloc[i], final_lb.iloc[i - 1])

        super_trend = pd.Series(index=df.index, dtype="float64")
        in_uptrend = True
        for i in range(period, len(df)):
            if in_uptrend:
                if close.iloc[i] < final_ub.iloc[i]:
                    in_uptrend = False
            else:
                if close.iloc[i] > final_lb.iloc[i]:
                    in_uptrend = True
            super_trend.iloc[i] = final_lb.iloc[i] if in_uptrend else final_ub.iloc[i]

        df['SUPERTREND'] = super_trend

        cross_up = (close > super_trend) & (close.shift(1) <= super_trend.shift(1))
        cross_down = (close < super_trend) & (close.shift(1) >= super_trend.shift(1))

        df['SUPER_TREND_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['SUPER_TREND_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
