import os
import re
import yaml


def read_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def get_next_simulation_dir(base_dir="data/simulation_results"):
    os.makedirs(base_dir, exist_ok=True)
    sim_dirs = [d for d in os.listdir(base_dir) if re.match(r'^sim_\d+$', d)]
    if sim_dirs:
        last_sim = max([int(re.search(r'\d+', d).group()) for d in sim_dirs])
        new_sim = last_sim + 1
    else:
        new_sim = 1
    sim_dir = os.path.join(base_dir, f"sim_{new_sim}")
    os.makedirs(sim_dir, exist_ok=True)
    return sim_dir


def get_trade_dir(sim_dir):
    trade_dir = os.path.join(sim_dir, "trade")
    os.makedirs(trade_dir, exist_ok=True)
    return trade_dir


def save_df_to_csv(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
