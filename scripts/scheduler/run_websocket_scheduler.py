from apscheduler.schedulers.blocking import BlockingScheduler
from src.market_data.websocket_ticks import start_websocket
from src.utils.time_util import get_current_ist_time
import yaml

CONFIG_PATH = "config/config.yaml"


def read_config():
    with open(CONFIG_PATH, 'r') as file:
        return yaml.safe_load(file)


def scheduled_websocket():
    config = read_config()
    symbols = config['websocket']['default_symbols']
    print(f"🚀 Scheduled websocket started at: {get_current_ist_time()}")
    start_websocket(symbols)


scheduler = BlockingScheduler(timezone='Asia/Kolkata')
scheduler.add_job(scheduled_websocket, 'cron', day_of_week='mon-fri', hour=9, minute=0)

if __name__ == "__main__":
    print("🕒 Starting websocket scheduler.")
    scheduled_websocket()       # initial run immediately
    # scheduler.start()           # We can uncomment it when we want to run a full-fledged scheduler
