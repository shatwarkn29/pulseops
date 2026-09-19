import httpx 
from typing import List
from uuid import UUID
from sqlalchemy import desc
from typing import Optional 

from sqlalchemy.orm import Session

from app.models.website import Website
from app.models.health_check import HealthCheck

def perform_health_check(db: Session, website: Website) -> HealthCheck:
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

    return db_health_check

def get_health_checks(db:Session , website_id: UUID , limit:int = 100) ->List[HealthCheck]:
    return db.query(HealthCheck).filter(HealthCheck.website_id == website_id).order_by(desc(HealthCheck.requested_at)).limit(limit).all()

def get_latest_health_check(db:Session , website_id:  UUID) -> Optional[HealthCheck]:
    return db.query(HealthCheck).filter(HealthCheck.website_id == website_id).order_by(desc(HealthCheck.requested_at)).first()

