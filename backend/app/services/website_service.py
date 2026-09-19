from datetime import datetime, timezone
from typing import Optional , List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.website import Website
from app.schemas.website import WebsiteCreate, WebsiteUpdate   
from app.services.scheduler_service import add_website_job , update_website_job , remove_website_job

def create_website(db: Session, website_data: WebsiteCreate) -> Website:

    url = str(website_data.url)

    # Check if an active website with this URL already exists
    existing_website = (
        db.query(Website)
        .filter(
            Website.url == url,
            Website.deleted_at.is_(None),
        )
        .first()
    )

    if existing_website:
        raise ValueError(
            f"Website with URL '{website_data.url}' already exists."
        )

    # Check if a soft-deleted website with this URL exists
    deleted_website = (
        db.query(Website)
        .filter(
            Website.url == url,
            Website.deleted_at.is_not(None),
        )
        .first()
    )

    # Restore the existing website
    if deleted_website:
        deleted_website.name = website_data.name
        deleted_website.monitoring_interval = website_data.monitoring_interval
        deleted_website.deleted_at = None
        deleted_website.is_active = True

        db.commit()
        db.refresh(deleted_website)
        add_website_job(deleted_website)
        return deleted_website

    # Create a completely new website
    db_website = Website(
        name=website_data.name,
        url=url,
        monitoring_interval=website_data.monitoring_interval,
    )

    db.add(db_website)

    try:
        db.commit()
        db.refresh(db_website)
        add_website_job(db_website)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(
            f"Website with URL '{website_data.url}' already exists."
        ) from e

    return db_website

def get_website(db:Session , website_id:UUID) -> Optional[Website]:
    return db.query(Website).filter(Website.id == website_id,Website.deleted_at.is_(None)).first()

def get_websites(db:Session) -> List[Website]:
    return db.query(Website).filter(Website.deleted_at.is_(None)).all()

def update_website(db:Session , website:Website , website_data: WebsiteUpdate) ->Website:
    update_data = website_data.model_dump(exclude_unset=True)
    for field , value in update_data.items():
        if field =="url":
            value=str(value)
        setattr(website,field,value)
    db.commit()
    db.refresh(website)
    update_website_job(website)
    return website

def delete_website(db:Session, website: Website) -> Website:
    website.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(website)
    remove_website_job(str(website.id))
    return website 
