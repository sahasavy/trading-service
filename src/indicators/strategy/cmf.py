from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class ChaikinMF(BaseIndicatorStrategy):
    """
    The Chaikin Money Flow (CMF) is a volume-weighted average of accumulation/distribution over a specified period.
    It measures the buying and selling pressure for an asset over that window.

    Hyperparameters:
        period: int
            The lookback window for summing Money Flow Volume and Volume (typical: 10–40).

    Signal Logic:
        - Long signal: CMF crosses above zero (buying pressure).
        - Short signal: CMF crosses below zero (selling pressure).
    """

    def __init__(self):
        super().__init__(IndicatorName.CHAIKIN_MF.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # Typical period for CMF is 10–40
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

        high = df['high']
        low = df['low']
        close = df['close']
        volume = df['volume']

        # Avoid division by zero
        denominator = (high - low).replace(0, 1e-9)
        mfv = ((2 * close - low - high) / denominator * volume).fillna(0)
        cmf = mfv.rolling(period, min_periods=period).sum() / volume.rolling(period, min_periods=period).sum()

        new_cols = {
            f'CMF{suffix}': cmf,
            f'CHAIKIN_MF_LONG_SIGNAL{suffix}': (cmf > 0).shift(1, fill_value=False).astype(int),
            f'CHAIKIN_MF_SHORT_SIGNAL{suffix}': (cmf < 0).shift(1, fill_value=False).astype(int)
        }
        return new_cols
