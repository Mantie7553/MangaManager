from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from schemas import SeriesSchema
import models

router = APIRouter(prefix="/series", tags=["series"])

@router.get("/", response_model=list[SeriesSchema])
def get_all_series(db: Session = Depends(get_db)):
    return db.query(models.Series).all()


@router.post("/")
def create_series(name: str, total_volumes: int | None = None, db: Session = Depends(get_db)):
    existing = db.query(models.Series).filter(
        func.lower(models.Series.name) == name.lower()
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Series already exists")

    series = models.Series(name=name, total_volumes=total_volumes)
    db.add(series)
    db.commit()
    db.refresh(series)
    return series


@router.put("/{series_id}")
def update_series(series_id: int, name: str, total_volumes: int | None = None, db: Session = Depends(get_db)):
    series = db.query(models.Series).filter(models.Series.id == series_id).first()
    series.name = name
    series.total_volumes = total_volumes
    db.commit()
    db.refresh(series)
    return series


@router.delete("/{series_id}")
def delete_series(series_id: int, db: Session = Depends(get_db)):
    series = db.query(models.Series).filter(models.Series.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    db.query(models.Volume).filter(models.Volume.series_id == series_id).delete()
    db.delete(series)
    db.commit()
    return {"message": f"Deleted series {series_id}"}


@router.patch("/{series_id}/favorite")
def toggle_series_favorite(series_id: int, db: Session = Depends(get_db)):
    series = db.query(models.Series).filter(models.Series.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    series.is_favorite = not series.is_favorite
    db.commit()
    db.refresh(series)
    return series