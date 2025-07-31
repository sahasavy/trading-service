from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class WilliamsR(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Williams %R
    """

    def __init__(self):
        super().__init__(IndicatorName.WILLIAMS_R.name)

    def compute_signals(self, df, params):
        period = params.get('period', 14)
        overbought = params.get('overbought', -20)
        oversold = params.get('oversold', -80)

        high_roll = df['high'].rolling(window=period).max()
        low_roll = df['low'].rolling(window=period).min()
        wr = -100 * ((high_roll - df['close']) / (high_roll - low_roll))

        df['WILLIAMSR'] = wr
        df['WILLIAMS_R_LONG_SIGNAL'] = (wr < oversold).shift(1, fill_value=False).astype(int)
        df['WILLIAMS_R_SHORT_SIGNAL'] = (wr > overbought).shift(1, fill_value=False).astype(int)
