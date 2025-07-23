from kiteconnect import KiteConnect
from src.utils.db_util import get_latest_access_token
import yaml

CONFIG_PATH = "config/config.yaml"


def read_config():
    with open(CONFIG_PATH, 'r') as file:
        return yaml.safe_load(file)


def get_authenticated_kite():
    config = read_config()
    access_token = get_latest_access_token(config['kite']['api_key'])
    if not access_token:
        raise Exception("No active login. Run login first.")
    kite = KiteConnect(api_key=config['kite']['api_key'])
    kite.set_access_token(access_token)
    return kite
