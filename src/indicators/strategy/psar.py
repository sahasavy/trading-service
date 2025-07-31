import pandas as pd
from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class PSAR(BaseIndicatorStrategy):
    """
    The Parabolic SAR (Stop and Reverse) is a trend-following indicator that helps determine trend direction and potential reversal points.
    PSAR plots dots above or below price, switching sides when trend reverses. Parameters control sensitivity.

    Hyperparameters:
        af: float
            Initial acceleration factor (step size for SAR, typical: 0.01–0.05).
        max_af: float
            Maximum acceleration factor (limits sensitivity, typical: 0.1–0.5).

    Signal Logic:
        - Long signal: Price crosses above PSAR (bullish trend start).
        - Short signal: Price crosses below PSAR (bearish trend start).
    """

    def __init__(self):
        super().__init__(IndicatorName.PSAR.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # af: 0.01–0.05 by 0.01, max_af: 0.1–0.5 by 0.1
        af_range = [round(x, 2) for x in [0.01 + 0.01 * i for i in range(5)]]  # 0.01–0.05
        max_af_range = [round(x, 2) for x in [0.1 + 0.1 * i for i in range(5)]]  # 0.1–0.5
        return {
            "af": af_range,
            "max_af": max_af_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # af > 0, max_af >= af
        return [
            combo for combo in combos
            if 0 < combo['af'] <= combo['max_af']
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'af' not in params or 'max_af' not in params:
            raise ValueError(
                f"{self.name} params 'af' and 'max_af' are required in backtest-config.yaml/indicator-config.yaml"
            )

        af = params['af']
        max_af = params['max_af']
        suffix = df_col_suffix or ""

        high = df['high'].values
        low = df['low'].values
        close = df['close'].values

        psar = [low[0]]
        uptrend = True
        ep = high[0]
        curr_af = af

        for i in range(1, len(df)):
            prev_psar = psar[-1]

            if uptrend:
                psar_i = prev_psar + curr_af * (ep - prev_psar)
                # Check for reversal
                if low[i] < psar_i:
                    uptrend = False
                    psar_i = ep
                    ep = low[i]
                    curr_af = af
                else:
                    if high[i] > ep:
                        ep = high[i]
                        curr_af = min(curr_af + af, max_af)
            else:
                psar_i = prev_psar + curr_af * (ep - prev_psar)
                if high[i] > psar_i:
                    uptrend = True
                    psar_i = ep
                    ep = high[i]
                    curr_af = af
                else:
                    if low[i] < ep:
                        ep = low[i]
                        curr_af = min(curr_af + af, max_af)
            psar.append(psar_i)

        psar_series = pd.Series(psar, index=df.index)
        cross_up = (df['close'] > psar_series) & (df['close'].shift(1) <= psar_series.shift(1))
        cross_down = (df['close'] < psar_series) & (df['close'].shift(1) >= psar_series.shift(1))

        new_cols = {
            f'PSAR{suffix}': psar_series,
            f'PSAR_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'PSAR_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int)
        }
        return new_cols
