from src.market_data.websocket_ticks import start_websocket

from src.utils.file_util import read_config

CONFIG_PATH = "config/config.yaml"

if __name__ == "__main__":
    config = read_config(CONFIG_PATH)
    user_input = input("Enter symbols (comma-separated, press enter for default list from Config): ").strip()

    if user_input:
        symbols = [symbol.strip().upper() for symbol in user_input.split(',')]
    else:
        symbols = config['websocket']['default_symbols']

    start_websocket(symbols)
