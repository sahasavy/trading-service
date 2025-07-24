import itertools


def construct_strategy_param_grid(strategy_dict):
    """
    Yields all parameter combinations for a strategy dict where all hyperparameters are lists (ending with _list).
    Returns each as a dict: {'name': '...', param1: v1, param2: v2, ...}
    """
    hyperparam_key_list = [key for key in strategy_dict if key.endswith("_list")]
    hyperparam_values = [strategy_dict[key] for key in hyperparam_key_list]
    for hyperparam_combo in itertools.product(*hyperparam_values):
        params = dict(
            zip([hyperparam_key[:-5] for hyperparam_key in hyperparam_key_list], hyperparam_combo))  # remove _list
        strategy_param_grid = {"name": strategy_dict['name']}
        strategy_param_grid.update(params)
        yield strategy_param_grid
