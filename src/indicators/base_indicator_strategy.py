class BaseIndicatorStrategy:
    def __init__(self, name):
        self.name = name

    def compute_signals(self, df, params):
        raise NotImplementedError("Each indicator must implement its own compute_signals method.")
