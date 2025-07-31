class BaseIndicatorStrategy:
    def __init__(self, name):
        self.name = name

    @classmethod
    def grid_ranges(cls, default_params):
        """
        Returns a dict: param name -> list of values.
        By default, uses the default value (no grid search).
        """
        return {k: [v] for k, v in default_params.items()}

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        """
        Receives a list of dicts, each dict a param combo.
        Return a filtered list with only valid combos.
        """
        return combos

    def compute_signals(self, df, params, df_col_suffix=None):
        raise NotImplementedError("Each indicator must implement its own compute_signals method.")
