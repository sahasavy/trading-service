from src.indicators.registry import add_signals
from src.utils.file_util import read_config

INDICATOR_CONFIG_PATH = "config/indicator-config.yaml"


def apply_indicators(df):
    indicator_config = read_config(INDICATOR_CONFIG_PATH)

    grid_search_enabled = indicator_config["grid_search_enabled"]
    active = indicator_config["active_indicators"]  # Picks up active indicators
    base_strategy_configs = indicator_config["default_hyperparam_values"]  # Picks up default hyperparam values

    if grid_search_enabled:
        # TODO - Implement new logic here
        pass
    else:
        for indicator_name in active:
            params = base_strategy_configs.get(indicator_name, {})
            add_signals(df, indicator_name, params)
