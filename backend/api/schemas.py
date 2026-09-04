from pydantic import BaseModel

class VolumeSchema(BaseModel):
    id: int
    volume_number: int
    cover_url: str | None
    is_favorite: bool = False

    model_config = {"from_attributes": True}


class SeriesSchema(BaseModel):
    id: int
    name: str
    total_volumes: int | None = None
    is_favorite: bool = False
    volumes: list[VolumeSchema] = []

    model_config = {"from_attributes": True}