import pandas as pd
from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class ATR(BaseIndicatorStrategy):
    """
    The Average True Range (ATR) measures market volatility by decomposing the entire
    range of an asset price for a given period. ATR is widely used in stop-loss placement,
    position sizing, and as a filter for volatility regimes.

    Hyperparameters:
        period: int
            Lookback window for ATR calculation (typical: 7–30).
        spike_mult: float (optional)
            Optional: Spike threshold multiplier (e.g., 1.5–3.0) to generate volatility spike signals.

    Signal Logic:
        - ATR is used directly as a volatility measure.
        - Optionally, signal a "volatility spike" if the current ATR is greater than spike_mult × median ATR.
    """

    def __init__(self):
        super().__init__(IndicatorName.ATR.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 7–30, spike_mult: 1.5, 2.0, 2.5, 3.0 (as steps)
        period_range = list(range(7, 31))  # 7, ..., 30
        spike_mult_range = [round(1.5 + 0.5 * i, 2) for i in range(4)]  # 1.5, 2.0, 2.5, 3.0
        return {
            "period": period_range,
            "spike_mult": spike_mult_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period > 1, spike_mult > 1.0
        return [
            combo for combo in combos
            if combo['period'] > 1 and combo['spike_mult'] > 1.0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params or 'spike_mult' not in params:
            raise ValueError(
                f"{self.name} params 'period' and 'spike_mult' are required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        spike_mult = params['spike_mult']
        suffix = df_col_suffix or ""

        tr1 = df['high'] - df['low']
        tr2 = (df['high'] - df['close'].shift()).abs()
        tr3 = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = tr.rolling(window=period, min_periods=period).mean()

        # Optional: Volatility spike signal
        median_atr = atr.rolling(window=period, min_periods=period).median()
        spike = atr > (median_atr * spike_mult)

        new_cols = {
            f'ATR{suffix}': atr,
            f'ATR_SPIKE_SIGNAL{suffix}': spike.shift(1, fill_value=False).astype(int)
        }
        return new_cols
