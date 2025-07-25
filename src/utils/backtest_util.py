import itertools

from src.commons.constants.constants import IndicatorName


# def construct_strategy_param_grid(strategy_dict):
#     """
#     Yields all parameter combinations for a strategy dict where all hyperparameters are lists (ending with _list).
#     Returns each as a dict: {'name': '...', param1: v1, param2: v2, ...}
#     """
#     hyperparam_key_list = [key for key in strategy_dict if key.endswith("_list")]
#     hyperparam_values = [strategy_dict[key] for key in hyperparam_key_list]
#     for hyperparam_combo in itertools.product(*hyperparam_values):
#         params = dict(
#             zip([hyperparam_key[:-5] for hyperparam_key in hyperparam_key_list], hyperparam_combo))  # remove _list
#         strategy_param_grid = {"name": strategy_dict['name']}
#         strategy_param_grid.update(params)
#         yield strategy_param_grid


def construct_strategy_param_grid(strategy):
    """
    Returns a list of dicts, each dict being a full hyperparameter set for a strategy.
    Rules:
    1. For EMA_CROSS and SMA_CROSS (fast < slow, fast != slow).
    2. For other strategies, generates all combinations.
    """
    name = strategy['name'].upper()

    if name in (IndicatorName.EMA_CROSS.name, IndicatorName.SMA_CROSS.name):
        # Keys might be: fast_list, slow_list
        fast_list = strategy.get('fast_list', [])
        slow_list = strategy.get('slow_list', [])
        # Only combinations where fast < slow and fast != slow
        strategy_param_grid = []
        for fast in fast_list:
            for slow in slow_list:
                if fast < slow:
                    strategy_param_grid.append({
                        'name': name,
                        'fast': fast,
                        'slow': slow
                    })
        return strategy_param_grid
    else:
        # General grid: get all lists, remove 'name'
        param_keys = [key for key in strategy.keys() if key != 'name']
        param_lists = [strategy[key] for key in param_keys]
        hyperparam_combo = list(itertools.product(*param_lists))
        strategy_param_grid = [
            dict({'name': name}, **{key.replace('_list', ''): v for key, v in zip(param_keys, values)})
            for values in hyperparam_combo
        ]
        return strategy_param_grid


def construct_strategy_hyperparam_str(strategy_params):
    """Create a string like 8-21, 14-70-30, etc. from params dict, excluding 'name'."""
    return "-".join(str(strategy_params[k]) for k in sorted(strategy_params) if k != "name")
