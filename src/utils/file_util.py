import os
import re

import pandas as pd
import yaml

HISTORICAL_DATA_DIR = "data/historical"
FEATURE_DATA_DIR = "data/feature"
BASE_DIR = "data/simulation_results"
TRADES_DIR = "trades"
FEATURES_DIR = "features"
PLOTS_DIR = "plots"


def read_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def get_next_simulation_dir():
    os.makedirs(BASE_DIR, exist_ok=True)
    sim_dirs = [d for d in os.listdir(BASE_DIR) if re.match(r'^sim_\d+$', d)]
    if sim_dirs:
        last_sim = max([int(re.search(r'\d+', d).group()) for d in sim_dirs])
        new_sim = last_sim + 1
    else:
        new_sim = 1
    sim_dir = os.path.join(BASE_DIR, f"sim_{new_sim}")
    os.makedirs(sim_dir, exist_ok=True)
    return sim_dir


def get_trades_dir(sim_dir):
    trades_dir = os.path.join(sim_dir, TRADES_DIR)
    os.makedirs(trades_dir, exist_ok=True)
    return trades_dir


def get_features_dir(sim_dir):
    features_dir = os.path.join(sim_dir, FEATURES_DIR)
    os.makedirs(features_dir, exist_ok=True)
    return features_dir


def get_plots_dir(sim_dir):
    plots_dir = os.path.join(sim_dir, PLOTS_DIR)
    os.makedirs(plots_dir, exist_ok=True)
    return plots_dir


def save_df_to_csv(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def read_df_from_csv(filename, parse_dates=None):
    return pd.read_csv(filename, parse_dates=parse_dates)
