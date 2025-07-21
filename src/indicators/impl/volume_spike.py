from src.indicators.base import Indicator


class VolumeSpike(Indicator):
    def __init__(self):
        super().__init__("VOLUME_SPIKE")

    def calculate(self, df, **params):
        if 'period' not in params or 'spike_mult' not in params:
            raise ValueError("VOLUME_SPIKE params 'period' and 'spike_mult' are required in indicator-config.yaml")
        period = params['period']
        spike_mult = params['spike_mult']
        df = df.copy()
        df['VOL_MA'] = df['volume'].rolling(window=period).mean()
        df['VOLUME_SPIKE'] = (df['volume'] > df['VOL_MA'] * spike_mult).astype(int)
        return df
