from asyncio.log import logger
import logging
import httpx 
from typing import List
from uuid import UUID
from sqlalchemy import desc , func, case
from typing import Optional 
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.models.website import Website
from app.models.health_check import HealthCheck

# Initialize the logger
logger = logging.getLogger(__name__)

def perform_health_check(db: Session, website: Website) -> HealthCheck:
    previous_health_check = db.query(HealthCheck).filter(HealthCheck.website_id == website.id).order_by(desc(HealthCheck.requested_at)).first()

    status_code = None
    response_time = None
    success = False
    error_message = None 

    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(website.url)
            response_time = response.elapsed.total_seconds()*1000.0
            status_code = response.status_code 

            if response.status_code < 400:
                success = True
            else:
                success = False 
                error_message = f"HTTP error : {response.status_code}  {response.reason_phrase}"
    except httpx.TimeoutException:
        success = False
        error_message = "Request timed out"
    except httpx.RequestError as e:
        success = False
        error_message = f"Request error : {str(e)}"
    except Exception as e:
        success = False
        error_message = f"Unexpected error : {str(e)}"

    db_health_check = HealthCheck(
        website_id = website.id,
        status_code = status_code,
        response_time = response_time,
        success = success,
        error_message = error_message
    )

    db.add(db_health_check)
    db.commit()
    db.refresh(db_health_check)

    if previous_health_check is not None:
        if previous_health_check.success and not db_health_check.success:
            logger.error(f"Website {website.url} is down. Previous health check was successful, but the current one failed.")
        elif not previous_health_check.success and db_health_check.success:
            logger.info(f"Website {website.url} is back up. Previous health check failed, but the current one was successful.")

    return db_health_check

def get_health_checks(db:Session , website_id: UUID , limit:int = 100) ->List[HealthCheck]:
    return db.query(HealthCheck).filter(HealthCheck.website_id == website_id).order_by(desc(HealthCheck.requested_at)).limit(limit).all()

def get_latest_health_check(db:Session , website_id:  UUID) -> Optional[HealthCheck]:
    return db.query(HealthCheck).filter(HealthCheck.website_id == website_id).order_by(desc(HealthCheck.requested_at)).first()

def get_website_metrics(db:Session , website_id:UUID , hours:int = 24) -> Optional[dict]:
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    metrics = (
        db.query(
            func.count(HealthCheck.id).label("total_checks"),
            func.sum(case((HealthCheck.success == True, 1), else_=0)).label("successful_checks"),
            func.avg(
                case(
                    (HealthCheck.success == True, HealthCheck.response_time),
                    else_=None
                )
            ).label("avg_response_time")
        ).filter(
            HealthCheck.website_id == website_id,
            HealthCheck.requested_at >= cutoff_time
        )
        .first()
    )

    total_checks = metrics.total_checks or 0
    successful_checks = metrics.successful_checks or 0
    failed_checks = total_checks - successful_checks

    uptime_percentage = round((successful_checks / total_checks * 100),2) if total_checks > 0 else 0.0
    average_response_time = metrics.avg_response_time if metrics.avg_response_time is not None else None

    return {
        "website_id": website_id,
        "time_window_hours": hours,
        "total_checks": total_checks,
        "successful_checks": successful_checks,
        "failed_checks": failed_checks,
        "uptime_percentage": uptime_percentage,
        "average_response_time_ms": average_response_time
    }
