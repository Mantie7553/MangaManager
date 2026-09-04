import os
import shutil
import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
import models

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _delete_cover_file(cover_url: str):
    """Delete a cover image from disk given its /uploads/<...> URL."""
    if not cover_url:
        return
    path = os.path.join(UPLOAD_DIR, cover_url.lstrip("/").removeprefix("uploads/"))
    if os.path.isfile(path):
        os.remove(path)


router = APIRouter(prefix="/volumes", tags=["volumes"])


@router.get("/")
def get_all_volumes(db: Session = Depends(get_db)):
    return db.query(models.Volume).all()


@router.get("/{series_id}")
def get_all_for_series(series_id: int, db: Session = Depends(get_db)):
    series = db.query(models.Series).filter(models.Series.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    return series.volumes


@router.post("/")
def create_volume(series_id: int, volume_number: int, cover_url: str = "", db: Session = Depends(get_db)):
    series = db.query(models.Series).filter(models.Series.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    volume = models.Volume(series_id=series_id, volume_number=volume_number, cover_url=cover_url)
    db.add(volume)
    db.commit()
    db.refresh(volume)
    return volume


@router.post("/{volume_id}/cover")
def upload_cover(volume_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    volume = db.query(models.Volume).filter(models.Volume.id == volume_id).first()
    if not volume:
        raise HTTPException(status_code=404, detail="Volume not found")

    _delete_cover_file(volume.cover_url)

    series_dir = os.path.join(UPLOAD_DIR, str(volume.series_id))
    os.makedirs(series_dir, exist_ok=True)

    ext = file.filename.split(".")[-1]
    filename = f"vol_{volume.volume_number}.{ext}"
    path = os.path.join(series_dir, filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    volume.cover_url = f"/uploads/{volume.series_id}/{filename}"
    db.commit()
    db.refresh(volume)
    return volume


@router.put("/{series_id}/{volume_id}")
def update_volume(series_id: int, volume_id: int, volume_number: int, cover_url: str = "", db: Session = Depends(get_db)):
    series = db.query(models.Series).filter(models.Series.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    volume = db.query(models.Volume).filter(models.Volume.id == volume_id).first()
    if not volume:
        raise HTTPException(status_code=404, detail="Volume not found")

    if volume.series_id != series_id:
        raise HTTPException(status_code=404, detail="Volume not found in this series")
    
    volume.volume_number = volume_number
    volume.cover_url = cover_url
    db.commit()
    db.refresh(volume)
    return volume


@router.delete("/{series_id}/{volume_id}")
def delete_volume(series_id: int, volume_id: int, db: Session = Depends(get_db)):
    series = db.query(models.Series).filter(models.Series.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    volume = db.query(models.Volume).filter(models.Volume.id == volume_id).first()
    if not volume:
        raise HTTPException(status_code=404, detail="Volume not found")

    if volume.series_id != series_id:
        raise HTTPException(status_code=404, detail="Volume not found in this series")
    
    _delete_cover_file(volume.cover_url)
    db.delete(volume)
    db.commit()
    return {"message": f"Deleted volume {volume.volume_number} from {series.name}"}


@router.patch("/{volume_id}/favorite")
def toggle_volume_favorite(volume_id: int, db: Session = Depends(get_db)):
    volume = db.query(models.Volume).filter(models.Volume.id == volume_id).first()
    if not volume:
        raise HTTPException(status_code=404, detail="Volume not found")
    volume.is_favorite = not volume.is_favorite
    db.commit()
    db.refresh(volume)
    return volume