from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class VWAP(BaseIndicatorStrategy):
    """
    VWAP is the average price weighted by volume. It is widely used for trade benchmarking,
    and as an intraday indicator for mean reversion and institutional trading.

    Hyperparameters:
        period: int (optional)
            If set, use rolling window VWAP for signals (typical: 10–100). Default: full cumulative VWAP.

    Signal Logic:
        - Long signal: Price crosses above VWAP (buy/mean reversion).
        - Short signal: Price crosses below VWAP (sell/mean reversion).
    """

    def __init__(self):
        super().__init__(IndicatorName.VWAP.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 0 = full cumulative; or typical rolling windows 10–100
        period_range = [0] + list(range(10, 101, 10))  # 0 means full cumulative
        return {
            "period": period_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period >= 0 (0 means no rolling)
        return [
            combo for combo in combos
            if combo['period'] >= 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params:
            raise ValueError(
                f"{self.name} param 'period' is required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        suffix = df_col_suffix or ""

        if period == 0:
            cum_vol = df['volume'].cumsum()
            cum_vp = (df['close'] * df['volume']).cumsum()
            vwap = cum_vp / cum_vol
        else:
            # Rolling VWAP: industry practice for intraday slices
            rolling_vp = (df['close'] * df['volume']).rolling(window=period, min_periods=period).sum()
            rolling_vol = df['volume'].rolling(window=period, min_periods=period).sum()
            vwap = rolling_vp / rolling_vol

        cross_up = (df['close'] > vwap)
        cross_down = (df['close'] < vwap)
        new_cols = {
            f'VWAP{suffix}': vwap,
            f'VWAP_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'VWAP_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int),
        }
        return new_cols
