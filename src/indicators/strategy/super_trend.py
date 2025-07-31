import pandas as pd
from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class SuperTrend(BaseIndicatorStrategy):
    """
    The SuperTrend indicator is a trend-following overlay that uses ATR (Average True Range)
    to determine the direction of the trend and possible reversals. It plots a line above or
    below price, switching sides when price closes across the band.

    Hyperparameters:
        period: int
            The lookback period for ATR calculation (typical: 5–20).
        multiplier: float
            The ATR multiplier to widen or narrow the bands (typical: 1.0–5.0).

    Signal Logic:
        - Long signal: Price crosses above the SuperTrend band (trend reversal up).
        - Short signal: Price crosses below the SuperTrend band (trend reversal down).
    """

    def __init__(self):
        super().__init__(IndicatorName.SUPER_TREND.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 5–20, multiplier: 1.0–5.0 in 0.5 steps
        period_range = list(range(5, 21))  # 5, 6, ..., 20
        multiplier_range = [round(x, 2) for x in [1.0 + 0.5 * i for i in range(9)]]  # 1.0, 1.5, ..., 5.0
        return {
            "period": period_range,
            "multiplier": multiplier_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period > 1, multiplier > 0
        return [
            combo for combo in combos
            if combo['period'] > 1 and combo['multiplier'] > 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params or 'multiplier' not in params:
            raise ValueError(
                f"{self.name} params 'period' and 'multiplier' are required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        multiplier = params['multiplier']
        suffix = df_col_suffix or ""

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

        cross_up = (close > super_trend) & (close.shift(1) <= super_trend.shift(1))
        cross_down = (close < super_trend) & (close.shift(1) >= super_trend.shift(1))

        new_cols = {
            f'SUPERTREND{suffix}': super_trend,
            f'SUPER_TREND_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'SUPER_TREND_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int),
        }
        return new_cols
