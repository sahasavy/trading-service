from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class StochRSI(BaseIndicatorStrategy):
    """
    Stochastic RSI is an oscillator that applies the Stochastic formula to RSI values
    rather than directly to price. It measures the level of RSI relative to its range
    over a set period.

    Hyperparameters:
        period: int
            The lookback period for both the RSI and the Stochastic calculation (typical: 7–30).

    Signal Logic:
        - Long signal: StochRSI < 0.2 (oversold).
        - Short signal: StochRSI > 0.8 (overbought).
    """

    def __init__(self):
        super().__init__(IndicatorName.STOCH_RSI.name)

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

        # Standard RSI calculation
        delta = df['close'].diff()
        gain = delta.clip(lower=0).rolling(window=period, min_periods=period).mean()
        loss = -delta.clip(upper=0).rolling(window=period, min_periods=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        min_rsi = rsi.rolling(window=period, min_periods=period).min()
        max_rsi = rsi.rolling(window=period, min_periods=period).max()
        denominator = (max_rsi - min_rsi).replace(0, 1e-9)  # avoid division by zero

        stoch_rsi = (rsi - min_rsi) / denominator

        new_cols = {
            f'STOCH_RSI{suffix}': stoch_rsi,
            f'STOCH_RSI_LONG_SIGNAL{suffix}': (stoch_rsi < 0.2).shift(1, fill_value=False).astype(int),
            f'STOCH_RSI_SHORT_SIGNAL{suffix}': (stoch_rsi > 0.8).shift(1, fill_value=False).astype(int)
        }
        return new_cols
