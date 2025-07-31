from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class RSI(BaseIndicatorStrategy):
    """
    The Relative Strength Index (RSI) is a momentum oscillator that measures the speed
    and change of price movements. It ranges from 0 to 100 and is typically used to
    identify overbought and oversold conditions.

    Hyperparameters:
        period: int
            Lookback window for RSI calculation (typical: 7–30).
        overbought: int
            The RSI value above which the asset is considered overbought (e.g., 70–90).
        oversold: int
            The RSI value below which the asset is considered oversold (e.g., 10–40).
        mode: str
            Calculation mode for gains/losses: "simple" (rolling mean) or "exponential" (EMA).

    Signal Logic:
        - Long signal: RSI crosses below oversold threshold.
        - Short signal: RSI crosses above overbought threshold.
    """

    def __init__(self):
        super().__init__(IndicatorName.RSI.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 7–30, overbought: 70–90 (step 5), oversold: 10–40 (step 5), mode: categorical
        period_range = list(range(7, 31))  # 7, 8, ..., 30
        overbought_range = list(range(70, 91, 5))  # 70, 75, ..., 90
        oversold_range = list(range(10, 41, 5))  # 10, 15, ..., 40
        mode_range = ['simple', 'exponential']
        return {
            "period": period_range,
            "overbought": overbought_range,
            "oversold": oversold_range,
            "mode": mode_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period > 1, overbought > oversold, all within 0–100, valid mode
        return [
            combo for combo in combos
            if combo['period'] > 1
               and combo['overbought'] > combo['oversold']
               and 0 <= combo['oversold'] <= 100
               and 0 <= combo['overbought'] <= 100
               and combo['mode'] in ['simple', 'exponential']
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params or 'overbought' not in params or 'oversold' not in params:
            raise ValueError(
                f"{self.name} params 'period' and 'overbought' and 'oversold' are required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        overbought = params['overbought']
        oversold = params['oversold']
        mode = params.get('mode', 'simple')
        suffix = df_col_suffix or ""

        delta = df['close'].diff()
        if mode == 'simple':
            gain = delta.clip(lower=0).rolling(window=period, min_periods=period).mean()
            loss = -delta.clip(upper=0).rolling(window=period, min_periods=period).mean()
        elif mode == 'exponential':
            gain = delta.clip(lower=0).ewm(span=period, adjust=False, min_periods=period).mean()
            loss = -delta.clip(upper=0).ewm(span=period, adjust=False, min_periods=period).mean()
        else:
            raise ValueError(f"Unknown mode '{mode}' for RSI")

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        new_cols = {
            f'RSI{suffix}': rsi,
            f'RSI_LONG_SIGNAL{suffix}': ((rsi < oversold) & (rsi.shift(1) >= oversold)
                                         ).shift(1, fill_value=False).astype(int),
            f'RSI_SHORT_SIGNAL{suffix}': ((rsi > overbought) & (rsi.shift(1) <= overbought)
                                          ).shift(1, fill_value=False).astype(int)
        }
        return new_cols
