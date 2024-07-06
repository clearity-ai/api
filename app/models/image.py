from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class ImageFormat(str, Enum):
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"


class ProgressImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    experiment_id: Optional[int] = Field(default=None, foreign_key="experiment.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    storage_bucket: str
    image_path: str
    segmask_path: Optional[str] = None
    image_format: ImageFormat
    image_size: int
    date_uploaded: date = datetime.today().strftime("%Y-%m-%d")
    deleted: bool = False
