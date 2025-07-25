from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class ChaikinMF(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Chaikin Money Flow (CMF)
    """

    def __init__(self):
        super().__init__(IndicatorName.CHAIKIN_MF.name)

    def calculate(self, df, **params):
        # TODO - Add logic
        pass

    @staticmethod
    def compute_signals(df, params):
        period = params.get('period', 20)
        mfv = ((2 * df['close'] - df['low'] - df['high']) / (df['high'] - df['low']) * df['volume']).fillna(0)
        cmf = mfv.rolling(period).sum() / df['volume'].rolling(period).sum()
        df['CMF'] = cmf
        df['CHAIKIN_MF_LONG_SIGNAL'] = (cmf > 0).shift(1, fill_value=False).astype(int)
        df['CHAIKIN_MF_SHORT_SIGNAL'] = (cmf < 0).shift(1, fill_value=False).astype(int)
