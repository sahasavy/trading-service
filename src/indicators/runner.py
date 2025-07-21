import yaml
from src.indicators.registry import get_indicator

CONFIG_PATH = "config/config.yaml"
INDICATOR_CONFIG_PATH = "config/indicator-config.yaml"


def read_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def apply_indicators(df):
    config = read_config(CONFIG_PATH)
    indicator_config = read_config(INDICATOR_CONFIG_PATH)

    active = config["indicators"]  # Picks up active indicators from this config
    all_params = indicator_config["indicators"]  # Picks up default indicator config values from here

    for indicator_name in active:
        indicator_class = get_indicator(indicator_name)
        params = all_params.get(indicator_name, {})
        df = indicator_class().calculate(df, **params)
    return df
