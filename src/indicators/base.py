class Indicator:
    def __init__(self, name):
        self.name = name

    def calculate(self, df, **params):
        raise NotImplementedError("Each indicator must implement its own calculate method.")
