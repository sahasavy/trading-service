from src.market_data.websocket_ticks import start_websocket
import yaml

CONFIG_PATH = "config/config.yaml"

def read_config():
    with open(CONFIG_PATH, 'r') as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    config = read_config()
    user_input = input("Enter symbols (comma-separated, press enter for default list from Config): ").strip()

    if user_input:
        symbols = [sym.strip().upper() for sym in user_input.split(',')]
    else:
        symbols = config['websocket']['default_symbols']

    start_websocket(symbols)
