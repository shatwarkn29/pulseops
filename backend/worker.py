import sys
import pika 
import json
import logging 
from sqlalchemy.orm import Session 

from app.db.session import SessionLocal
from app.models.website import Website
from app.services import health_check_service

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def process_health_check(ch, method, properties, body):
    website_id = json.loads(body).get("website_id")
    logger.info(f"Worker picked up job for website_id: {website_id}")

    db: Session = SessionLocal()
    try: 
        website = db.query(Website).filter(Website.id == website_id).first()
        if website and website.is_active and website.deleted_at is None:
            logger.info("Performing Health Check for website %s", website.url)
            health_check_service.perform_health_check(db, website)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Finished job for website_id:{website_id}")
    except Exception as e:
        logger.error(f"Error occurred while processing health check for website_id: {website_id}", exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    finally:
        db.close()

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # FIX 2: Change to 'health_checks' to match your producer
    channel.queue_declare(queue='health_check', durable=True)

    channel.basic_qos(prefetch_count=1)
    # FIX 2: Change to 'health_checks' here as well
    channel.basic_consume(queue='health_check', on_message_callback=process_health_check)

    logger.info("Worker started. Waiting for messages.")
    channel.start_consuming()

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        print("Worker stopped by user.")
        sys.exit(0)