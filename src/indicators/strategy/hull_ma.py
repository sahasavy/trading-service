import numpy as np
from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class HullMA(BaseIndicatorStrategy):
    """
    The Hull Moving Average (Hull MA) is a fast, smooth moving average designed to minimize lag.
    It combines weighted moving averages (WMAs) and a final smoothing over sqrt(period).

    Hyperparameters:
        period: int
            The base lookback period for the calculation (typical: 10–40).

    Signal Logic:
        - Long signal: Price crosses above the Hull MA.
        - Short signal: Price crosses below the Hull MA.
    """

    def __init__(self):
        super().__init__(IndicatorName.HULL_MA.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # Hull MA period: 10–40 (inclusive)
        period_range = list(range(10, 41))  # 10, 11, ..., 40
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

        # Use integer division for window sizes, avoid window=0
        half_period = max(1, period // 2)
        sqrt_period = max(1, int(np.sqrt(period)))

        wma_half = df['close'].rolling(window=half_period, min_periods=half_period).mean()
        wma_full = df['close'].rolling(window=period, min_periods=period).mean()

        hull = 2 * wma_half - wma_full
        hull_ma = hull.rolling(window=sqrt_period, min_periods=sqrt_period).mean()

        cross_up = (df['close'] > hull_ma) & (df['close'].shift(1) <= hull_ma.shift(1))
        cross_down = (df['close'] < hull_ma) & (df['close'].shift(1) >= hull_ma.shift(1))

        new_cols = {
            f'HULL_MA{suffix}': hull_ma,
            f'HULL_MA_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'HULL_MA_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int)
        }
        return new_cols
