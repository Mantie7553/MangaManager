from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Series(Base):
    __tablename__ = "series"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    total_volumes = Column(Integer, nullable=True)
    is_favorite = Column(Boolean, default=False, nullable=False, server_default="0")
    volumes = relationship("Volume", back_populates="series")


class Volume(Base):
    __tablename__ = "volume"
    id = Column(Integer, primary_key=True)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False)
    volume_number = Column(Integer, nullable=False)
    cover_url = Column(String)
    is_favorite = Column(Boolean, default=False, nullable=False, server_default="0")
    series = relationship("Series", back_populates="volumes")
