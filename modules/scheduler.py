import schedule
import time

def job():
    print("Scheduled task is running...")

def start_scheduled_tasks():
    schedule.every(10).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
