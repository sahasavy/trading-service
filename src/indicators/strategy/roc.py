from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class ROC(BaseIndicatorStrategy):
    """
    The Rate of Change (ROC) is a momentum oscillator measuring the percent change in price over a specified period.
    It helps identify the speed and direction of price movements and is useful for spotting turning points.

    Hyperparameters:
        period: int
            The lookback window for the calculation (typical: 5–30).
        threshold: float
            The percent change threshold for generating signals (e.g., 0.5–2.0).

    Signal Logic:
        - Long signal: ROC rises above +threshold.
        - Short signal: ROC falls below –threshold.
    """

    def __init__(self):
        super().__init__(IndicatorName.ROC.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 5–30 (inclusive), threshold: 0.5–2.0 in 0.5 steps
        period_range = list(range(5, 31))  # 5, 6, ..., 30
        threshold_range = [round(x, 2) for x in [0.5 * i for i in range(1, 5)]]  # 0.5, 1.0, 1.5, 2.0
        return {
            "period": period_range,
            "threshold": threshold_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period > 0, threshold >= 0
        return [
            combo for combo in combos
            if combo['period'] > 0 and combo['threshold'] >= 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params or 'threshold' not in params:
            raise ValueError(
                f"{self.name} params 'period' and 'threshold' are required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        threshold = params['threshold']
        suffix = df_col_suffix or ""

        roc = df['close'].pct_change(periods=period) * 100

        new_cols = {
            f'ROC{suffix}': roc,
            f'ROC_LONG_SIGNAL{suffix}': (roc > threshold).shift(1, fill_value=False).astype(int),
            f'ROC_SHORT_SIGNAL{suffix}': (roc < -threshold).shift(1, fill_value=False).astype(int)
        }
        return new_cols
