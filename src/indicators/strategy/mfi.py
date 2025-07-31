import numpy as np
import pandas as pd
from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class MFI(BaseIndicatorStrategy):
    """
    The Money Flow Index (MFI) is a momentum oscillator that uses price and volume
    to measure buying and selling pressure. It is similar to RSI but incorporates volume.

    Hyperparameters:
        period: int
            The lookback window for MFI calculation (typical: 7–30).

    Signal Logic:
        - Long signal: MFI falls below 20 (oversold).
        - Short signal: MFI rises above 80 (overbought).
    """

    def __init__(self):
        super().__init__(IndicatorName.MFI.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 7–30 (inclusive)
        period_range = list(range(7, 31))  # 7, 8, ..., 30
        return {
            "period": period_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # Only allow period > 1
        return [
            combo for combo in combos
            if combo['period'] > 1
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params:
            raise ValueError(
                f"{self.name} param 'period' is required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        suffix = df_col_suffix or ""

        tp = (df['high'] + df['low'] + df['close']) / 3
        mf = tp * df['volume']
        pos_mf = np.where(tp > tp.shift(1), mf, 0)
        neg_mf = np.where(tp < tp.shift(1), mf, 0)
        pos_mf = pd.Series(pos_mf, index=df.index)
        neg_mf = pd.Series(neg_mf, index=df.index)

        # Avoid division by zero in Money Flow Ratio
        mfr_denominator = neg_mf.rolling(period, min_periods=period).sum().replace(0, np.nan)
        mfr = pos_mf.rolling(period, min_periods=period).sum() / mfr_denominator
        mfi = 100 - 100 / (1 + mfr)

        new_cols = {
            f'MFI{suffix}': mfi,
            f'MFI_LONG_SIGNAL{suffix}': (mfi < 20).shift(1, fill_value=False).astype(int),
            f'MFI_SHORT_SIGNAL{suffix}': (mfi > 80).shift(1, fill_value=False).astype(int)
        }
        return new_cols
