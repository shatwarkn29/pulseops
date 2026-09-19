import logging 
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, get_db
from app.models.website import Website
from app.services import health_check_service

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def scheduled_health_check_job(website_id: str):
    db: Session = SessionLocal()
    try:
        website = db.query(Website).filter(Website.id == website_id).first()
        if website and website.is_active and website.deleted_at is None:
            logger.info("Performing scheduler health check for website: %s",website.url)
            health_check_service.perform_health_check(db, website)
    except Exception as e:
        logger.error("Error during scheduled health check for website_id %s: %s", website_id, str(e))
    finally:
        db.close()

def start_scheduler():
    db: Session = SessionLocal()
    try:
        websites = db.query(Website).filter(Website.is_active == True, Website.deleted_at.is_(None)).all()
        for website in websites:
            scheduler.add_job(
                scheduled_health_check_job,
                'interval',
                seconds=website.monitoring_interval,
                args=[str(website.id)],
                id=str(website.id),
                replace_existing=True
            )
            logger.info("Scheduled health check for website: %s every %d seconds", website.url, website.monitoring_interval)
        scheduler.start()
        logger.info("PulseOps background scheduler started.")
    except Exception as e:
        logger.error("Error starting scheduler: %s", str(e))
    finally:
        db.close()

def stop_scheduler():
    """
    Called when FastAPI shuts down.
    """
    scheduler.shutdown()
    logger.info("PulseOps background scheduler stopped.")

def add_website_job(website: Website):
    if website.is_active and website.deleted_at is None:
        scheduler.add_job(
            scheduled_health_check_job,
            'interval',
            seconds=website.monitoring_interval,
            args=[str(website.id)],
            id=str(website.id),
            replace_existing=True
        )
        logger.info("Added scheduled health check for website: %s every %d seconds", website.url, website.monitoring_interval)

def remove_website_job(website_id:str):
    if scheduler.get_job(str(website_id)):
        scheduler.remove_job(str(website_id))
        logger.info("Removed scheduled health check for website_id: %s", website_id)

def update_website_job(website: Website):
    if website.is_active and website.deleted_at is None:
        add_website_job(website)
    else:
        remove_website_job(str(website.id))
