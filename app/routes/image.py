import os
from datetime import datetime

from fastapi import APIRouter, Depends, status, UploadFile, Path, HTTPException

from app.auth.authenticate import authenticate_user_credentials
from app.database.connection import get_session
from app.database.querying import (
    insert_record,
    get_record,
    get_records_by_field,
    update_record,
)
from app.database.storing import upload_file_to_object_storage
from app.models.image import ProgressImage
from app.models.experiment import Experiment
from app.models.response import ResponseModel
from app.models.user import User


image_router = APIRouter(tags=["Images"])

storage_bucket = os.getenv("STORAGE_BUCKET")


@image_router.post(
    "/image/create",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    image: UploadFile,
    experiment_id: int,
    user_firebase_id: str = Depends(authenticate_user_credentials),
    session=Depends(get_session),
):

    user = await get_records_by_field(user_firebase_id, "id", User, session)
    user = user[0]

    experiment_record = await get_record(experiment_id, Experiment, session)
    if experiment_record.user_id != user.id:
        return {
            "message": "User attempting to upload image to an experiment belonging to another user."
        }

    image_path = (
        f"{user.id}/{experiment_id}/{'.'.join(image.filename.split('.')[:-1])}_"
        f"{datetime.today().strftime('%Y-%m-%d')}.{image.filename.split('.')[-1]}"
    )

    await upload_file_to_object_storage(
        image, image_path, storage_bucket=storage_bucket
    )

    image_record = ProgressImage(
        experiment_id=experiment_id,
        user_id=user.id,
        storage_bucket=storage_bucket,
        image_path=image_path,
        image_format=image.content_type.split("/")[1],
        image_size=image.size,
    )

    await insert_record(image_record, session)

    return {
        "message": f"Image successfully uploaded to {experiment_record.name} experiment!"
    }


@image_router.get(
    "/image/retrieve", response_model=ResponseModel, status_code=status.HTTP_201_CREATED
)
async def retrieve_experiment_images(
    experiment_id: int,
    user_firebase_id: str = Depends(authenticate_user_credentials),
    session=Depends(get_session),
):
    """Function which only returns the image paths and storage buckets."""

    image_records = await get_records_by_field(
        experiment_id, "experiment_id", ProgressImage, session
    )

    data = [
        (
            image_record.storage_bucket,
            image_record.image_path,
            f"image/{image_record.image_format}",
            image_record.segmask_path,
        )
        for image_record in image_records
        if not image_record.deleted
    ]

    return {"message": "Experiment image paths successfully retrieved!", "data": data}


@image_router.put("/image/delete/{image_id}")
async def delete_image(
    image_id: int = Path(..., title="ID of image to delete."),
    user_id=Depends(authenticate_user_credentials),
    session=Depends(get_session),
):
    image_record = await get_record(image_id, ProgressImage, session)
    if image_record.image_path.split("/")[0] != user_id:
        raise HTTPException(
            status_code=400,
            detail="User is attempting to delete image not belonging to them.",
        )

    image_record.deleted = True
    await update_record(image_id, ProgressImage, image_record, session)

    return {"message": "Image successfuly deleted!"}
