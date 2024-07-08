import os
from datetime import datetime

from fastapi import APIRouter, Depends, status, HTTPException, Response
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import torch

from app.ai.load_model import load_model
from app.ai.skin_segmentation_nn import SkinSegmentationNN
import app.ai.utils as utils
from app.auth.authenticate import authenticate_user_credentials
from app.database.connection import get_session
from app.database.querying import get_record, update_record, get_records_by_field
from app.database.storing import download_progress_image, upload_segmentation_mask
from app.models.image import ProgressImage
from app.models.response import ResponseModel
from app.models.user import User

import pdb

ai_router = APIRouter(tags=["AI"])

segmentation_model = load_model(SkinSegmentationNN, "app/ai/models/model")
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
segmentation_model.to(device)

storage_bucket = os.getenv("STORAGE_BUCKET_ROUTINE_SELFIES")


@ai_router.post(
    "/ai/segment/",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def segment_image(
    image_id: int,
    user_firebase_id: str = Depends(authenticate_user_credentials),
    session=Depends(get_session),
):
    user = await get_records_by_field(user_firebase_id, "id", User, session)
    user = user[0]

    image_record = await get_record(image_id, ProgressImage, session)
    if image_record.user_id != user.id:
        raise HTTPException(
            status_code=400, detail="Cannot segment image of another user"
        )

    image = await download_progress_image(image_record, storage_bucket)

    try:
        image = Image.open(BytesIO(image))
    except UnidentifiedImageError:
        raise HTTPException(status_code=500, detail="Stored image corrupted.")

    image = utils.transform_image(image)
    image = image.to(device)

    segmask = utils.segment_image(image, segmentation_model)
    segmask_path = (
        f"{image_record.image_path.split('_')[0]}"
        "_mask_"
        f"{datetime.today().strftime('%Y-%m-%d')}"
        ".csv"  # Or whatever format is appropriate
    )

    # TODO: upload segmentation mask to object storage
    # await upload_segmentation_mask(segmask, segmask_path, storage_bucket)

    # image_record.segmask_path = segmask_path
    # await update_record(image_id, ProgressImage, image_record, session)

    # return {
    #     "message": f"Image segmented successfully and segmentation mask stored at {segmask_path} ."
    # }

    return {
        "message": "Image segmented successfully but mask storage not implemented yet."
    }
