import itertools

from src.indicators.registry import get_indicator, enrich_df
from src.utils.file_util import read_config

INDICATOR_CONFIG_PATH = "config/indicator-config.yaml"


def apply_indicators(df):
    indicator_config = read_config(INDICATOR_CONFIG_PATH)

    grid_search_enabled = indicator_config.get("grid_search_enabled", False)
    active = indicator_config["active_indicators"]  # Picks up active indicators
    base_strategy_configs = indicator_config["default_hyperparam_values"]  # Picks up default hyperparam values

    if grid_search_enabled:
        for indicator_name in active:
            indicator_class = get_indicator(indicator_name)
            default_params = base_strategy_configs.get(indicator_name, {})

            grid = indicator_class.grid_ranges(default_params)
            param_names = list(grid.keys())
            combos = [dict(zip(param_names, values)) for values in itertools.product(*[grid[k] for k in param_names])]

            valid_combos = indicator_class.filter_valid_grid_combos(combos)

            if not valid_combos:
                print(f"[{indicator_name}] ERROR: No valid grid combos after filtering! Skipping indicator.")
                continue
            print(f"[{indicator_name}] {len(valid_combos)} valid combos to process.")

            for combo in valid_combos:
                df_col_suffix = "_" + "_".join(f"{key}{value}" for key, value in combo.items())
                print(f"Enriching with params: {combo} -> suffix: {df_col_suffix}")
                df = enrich_df(df, indicator_name, combo, df_col_suffix)
    else:
        for indicator_name in active:
            params = base_strategy_configs.get(indicator_name, {})
            print(f"Enriching {indicator_name} with default params: {params}")
            df = enrich_df(df, indicator_name, params, None)

    # Defragment before cleanup and save!
    df = df.copy()
    return df
