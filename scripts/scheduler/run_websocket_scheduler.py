from apscheduler.schedulers.blocking import BlockingScheduler

from src.market_data.websocket_ticks import start_websocket
from src.utils.file_util import read_config
from src.utils.time_util import get_current_ist_time

CONFIG_PATH = "config/config.yaml"


def scheduled_websocket():
    config = read_config(CONFIG_PATH)
    symbols = config['websocket']['default_symbols']
    print(f"🚀 Scheduled websocket started at: {get_current_ist_time()}")
    start_websocket(symbols)


scheduler = BlockingScheduler(timezone='Asia/Kolkata')
scheduler.add_job(scheduled_websocket, 'cron', day_of_week='mon-fri', hour=9, minute=0)

if __name__ == "__main__":
    print("🕒 Starting websocket scheduler.")
    scheduled_websocket()  # initial run immediately
    # scheduler.start()           # We can uncomment it when we want to run a full-fledged scheduler
