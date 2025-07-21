from apscheduler.schedulers.blocking import BlockingScheduler
from src.utils.instruments import fetch_and_cache_instruments

scheduler = BlockingScheduler()

# Configurable cron-like syntax (below runs every Sunday at 09:00 IST)
scheduler.add_job(fetch_and_cache_instruments, 'cron', day_of_week='sun', hour=9, minute=0)

if __name__ == "__main__":
    print("🚀 Starting instruments cache scheduler.")
    fetch_and_cache_instruments()  # initial run immediately
    # scheduler.start()               # We can uncomment it when we want to run a full-fledged scheduler
