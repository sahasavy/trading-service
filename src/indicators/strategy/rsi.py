from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class RSI(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> RSI
    """

    def __init__(self):
        super().__init__(IndicatorName.RSI.name)

    def compute_signals(self, df, params):
        if 'period' not in params or 'overbought' not in params or 'oversold' not in params:
            raise ValueError(
                f"{self.name} params 'period' and 'overbought' and 'oversold' are required in backtest-config.yaml/indicator-config.yaml")

        period = params['period']
        overbought = params['overbought']
        oversold = params['oversold']

        delta = df['close'].diff()
        gain = delta.clip(lower=0).rolling(window=period).mean()
        loss = -delta.clip(upper=0).rolling(window=period).mean()
        rs = gain / loss

        df['RSI'] = 100 - (100 / (1 + rs))
        df['RSI_LONG_SIGNAL'] = ((df['RSI'] < oversold) & (df['RSI'].shift(1) >= oversold)
                                 ).shift(1, fill_value=False).astype(int)
        df['RSI_SHORT_SIGNAL'] = ((df['RSI'] > overbought) & (df['RSI'].shift(1) <= overbought)
                                  ).shift(1, fill_value=False).astype(int)
