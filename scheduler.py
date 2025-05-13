import schedule
import time
from threading import Thread
from database import get_subscribed_users
from app import get_news, send_email
 
def send_weekly_newsletter():
    api_key = "0a6927cd3408421aa01e13e3b6976cd7"
    users = get_subscribed_users()
    for user in users:
        email = user['email']
        categories = user['categories']
        if categories:
            articles = get_news(api_key, categories)
            if articles:
                send_email(email, articles, categories)
 
# Schedule the newsletter to be sent every Friday at 9 AM
schedule.every().tuesday.at("11:00").do(send_weekly_newsletter)
 
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
 
# Start the scheduler in a separate thread
scheduler_thread = Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
