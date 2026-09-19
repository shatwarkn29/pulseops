from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.website import WebsiteCreate , WebsiteUpdate, WebsiteResponse 
from app.schemas.health_check import HealthCheckResponse

from app.services import website_service , health_check_service


router = APIRouter(prefix="/websites",tags=["websites"],)

@router.post("/", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)

def create_website(website_data: WebsiteCreate , db:Session = Depends(get_db)):
    try:
        return website_service.create_website(db, website_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
@router.get("/",response_model = list[WebsiteResponse], status_code = status.HTTP_200_OK)
def get_websites(db:Session = Depends(get_db)) -> list[WebsiteResponse]:
    return website_service.get_websites(db)

@router.get("/{website_id}",response_model = WebsiteResponse , status_code = status.HTTP_200_OK)
def get_website(website_id:UUID , db:Session = Depends(get_db)):
    website = website_service.get_website(db, website_id)
    if website is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= "Website not found",)
    return website 

@router.put("/{website_id}",response_model = WebsiteResponse, status_code = status.HTTP_200_OK)
def update_website(website_id:UUID , website_data:WebsiteUpdate , db: Session = Depends(get_db)):
    website = website_service.get_website(db,website_id)
    if website is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= "Website not found",)
    return website_service.update_website(db,website,website_data)

@router.delete("/{website_id}",status_code=status.HTTP_200_OK,)
def delete_website(website_id:UUID , db:Session = Depends(get_db)):
    website = website_service.get_website(db,website_id)
    if website is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= "Website not found",)
    return website_service.delete_website(db,website)

@router.post("/{website_id}/health-check",response_model = HealthCheckResponse)
def trigger_manual_health_check(website_id:UUID , db:Session = Depends(get_db)):
    website = website_service.get_website(db,website_id)
    if website is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= "Website not found",)
    if website.deleted_at is not None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail= "Cannot perform health check on a deleted website",)
    health_check_result = health_check_service.perform_health_check(db, website)
    return health_check_result

@router.get("/{website_id}/health-checks",response_model=List[HealthCheckResponse])
def get_website_health_check_history(website_id:UUID , limit:int = 100 , db:Session = Depends(get_db)):
    website = website_service.get_website(db,website_id=website_id)
    if website is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= "Website not found",)
    health_checks = health_check_service.get_health_checks(db, website_id, limit)
    return health_checks

@router.get("/{website_id}/health-checks/latest",response_model=HealthCheckResponse)
def get_latest_health_check(website_id:UUID , db:Session = Depends(get_db)):
    website = website_service.get_website(db, website_id=website_id)
    if not website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    latest_health_check = health_check_service.get_latest_health_check(db, website_id)
    if not latest_health_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No health checks found for this website")
    return latest_health_check