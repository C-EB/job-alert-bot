# job_alert_bot/scheduler.py

import logging
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import scraper
import database as db
from config import SCHEDULED_JOB_TIME

logger = logging.getLogger(__name__)

async def job_processor(bot: Bot):
    """
    The main job function that scrapes, processes, and sends alerts.
    
    Args:
        bot (Bot): The aiogram Bot instance to send messages with.
    """
    logger.info("Daily scraping job started...")
    
    # 1. Scrape all jobs from all websites
    all_jobs = await scraper.scrape_all_sites()
    if not all_jobs:
        logger.info("No new jobs found. Job run finished.")
        return
        
    # 2. Get all user subscriptions from the database
    subscriptions = await db.get_all_subscriptions()
    if not subscriptions:
        logger.info("No user subscriptions found. Job run finished.")
        return
        
    # 3. Process and send alerts
    notifications_sent = 0
    for job in all_jobs:
        # Avoid sending duplicate jobs
        if await db.is_job_posted(job['id']):
            continue

        job_title_lower = job['title'].lower()
        
        # Check for matching keywords
        for keyword, user_ids in subscriptions.items():
            if keyword.lower() in job_title_lower:
                message = (
                    f"📢 **New Job Alert: {keyword}**\n\n"
                    f"**Title:** {job['title']}\n"
                    f"**Company:** {job['company']}\n"
                    f"**Source:** {job['source']}\n\n"
                    f"[View Job]({job['link']})"
                )
                
                # Send the alert to all users subscribed to this keyword
                for user_id in user_ids:
                    try:
                        await bot.send_message(user_id, message, parse_mode="Markdown", disable_web_page_preview=True)
                        notifications_sent += 1
                    except Exception as e:
                        logger.error(f"Failed to send message to user {user_id}: {e}")

        # Add the job to the database to mark it as sent
        await db.add_posted_job(job['id'], job['title'], job['company'], job['link'], job['source'])

    logger.info(f"Daily scraping job finished. Sent {notifications_sent} notifications.")


def setup_scheduler(bot: Bot):
    """Initializes and starts the APScheduler."""
    scheduler = AsyncIOScheduler()
    
    # Schedule job_processor to run daily at the time specified in config
    time = SCHEDULED_JOB_TIME.split(':')
    hour, minute = int(time[0]), int(time[1])
    
    scheduler.add_job(
        job_processor,
        trigger=CronTrigger(hour=hour, minute=minute, timezone="UTC"),
        args=[bot]
    )
    
    scheduler.start()
    logger.info(f"Scheduler started. Job will run daily at {SCHEDULED_JOB_TIME} UTC.")