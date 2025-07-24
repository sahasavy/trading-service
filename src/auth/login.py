from kiteconnect import KiteConnect

from src.utils.db_util import save_access_token
from src.utils.file_util import read_config

CONFIG_PATH = "config/config.yaml"


def authenticate_interactively():
    config = read_config(CONFIG_PATH)
    kite = KiteConnect(api_key=config['kite']['api_key'])

    login_url = kite.login_url()
    print(f"\n👉 Login URL:\n{login_url}\n")

    request_token = input("✅ Enter your request token: ").strip()
    session_data = kite.generate_session(request_token, api_secret=config['kite']['api_secret'])
    access_token = session_data["access_token"]
    save_access_token(config['kite']['api_key'], access_token)
    print("🎉 Login successful, access token saved!")
