from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class VolumeSpike(BaseIndicatorStrategy):
    """
    The Volume Spike indicator identifies periods where trading volume is significantly
    higher than normal. This can signal breakouts, news events, or high activity.

    Hyperparameters:
        period: int
            Lookback window for the moving average of volume (typical: 10–40).
        spike_mult: float
            Multiplier over the average volume to define a "spike" (typical: 1.5–3.0).

    Signal Logic:
        - Long/Short signal: Volume exceeds spike_mult × average volume over the period.
    """

    def __init__(self):
        super().__init__(IndicatorName.VOLUME_SPIKE.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 10–40 (inclusive), spike_mult: 1.5, 2.0, 2.5, 3.0
        period_range = list(range(10, 41))
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

        vol_ma = df['volume'].rolling(period, min_periods=period).mean()
        spike = df['volume'] > (vol_ma * spike_mult)

        new_cols = {
            f'VOLUME_SPIKE{suffix}': spike.astype(int),
            f'VOLUME_SPIKE_LONG_SIGNAL{suffix}': spike.shift(1, fill_value=False).astype(int),
            f'VOLUME_SPIKE_SHORT_SIGNAL{suffix}': spike.shift(1, fill_value=False).astype(int)
        }
        return new_cols
