import pandas as pd
from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class OBV(BaseIndicatorStrategy):
    """
    OBV is a momentum indicator that relates volume flow to price change.
    It adds volume on up days and subtracts volume on down days, building a cumulative total.
    A moving average of OBV is often used to generate trading signals.

    Hyperparameters:
        ma_period: int
            The period for the OBV signal moving average (typical: 10–40).

    Signal Logic:
        - Long signal: OBV crosses above its MA (bullish volume confirmation).
        - Short signal: OBV crosses below its MA (bearish volume confirmation).
    """

    def __init__(self):
        super().__init__(IndicatorName.OBV.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # ma_period: 10–40 (inclusive)
        ma_period_range = list(range(10, 41))  # 10, 11, ..., 40
        return {
            "ma_period": ma_period_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # Only allow ma_period > 1
        return [
            combo for combo in combos
            if combo['ma_period'] > 1
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'ma_period' not in params:
            raise ValueError(
                f"{self.name} param 'ma_period' is required in backtest-config.yaml/indicator-config.yaml"
            )

        ma_period = params['ma_period']
        suffix = df_col_suffix or ""

        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i - 1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i - 1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])

        obv_series = pd.Series(obv, index=df.index)
        obv_ma = obv_series.rolling(window=ma_period, min_periods=ma_period).mean()

        new_cols = {
            f'OBV{suffix}': obv_series,
            f'OBV_SIGNAL_MA{suffix}': obv_ma,
            f'OBV_LONG_SIGNAL{suffix}': (obv_series > obv_ma).shift(1, fill_value=False).astype(int),
            f'OBV_SHORT_SIGNAL{suffix}': (obv_series < obv_ma).shift(1, fill_value=False).astype(int)
        }
        return new_cols
