from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class VolumeSpike(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Volume Spike
    """

    def __init__(self):
        super().__init__(IndicatorName.VOLUME_SPIKE.name)

    def calculate(self, df, **params):
        if 'period' not in params or 'spike_mult' not in params:
            raise ValueError("VOLUME_SPIKE params 'period' and 'spike_mult' are required in indicator-config.yaml")
        period = params['period']
        spike_mult = params['spike_mult']
        df = df.copy()
        df['VOL_MA'] = df['volume'].rolling(window=period).mean()
        df['VOLUME_SPIKE'] = (df['volume'] > df['VOL_MA'] * spike_mult).astype(int)
        return df

    @staticmethod
    def compute_signals(df, params):
        period = params.get('period', 20)
        spike_mult = params.get('spike_mult', 2.0)
        vol_ma = df['volume'].rolling(period).mean()
        spike = df['volume'] > (vol_ma * spike_mult)
        df['VOLUME_SPIKE_LONG_SIGNAL'] = spike.shift(1, fill_value=False).astype(int)
        df['VOLUME_SPIKE_SHORT_SIGNAL'] = spike.shift(1, fill_value=False).astype(int)
