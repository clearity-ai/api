import os
import numpy as np
from io import BytesIO
from google.cloud import storage
from fastapi import UploadFile

from app.models.image import ProgressImage

import pdb

storage_client = storage.Client()


async def upload_file_to_object_storage(
    file: UploadFile, file_path: str, storage_bucket: str
):

    bucket = storage_client.bucket(storage_bucket)
    blob = bucket.blob(file_path)
    blob.upload_from_file(file_obj=file.file, content_type=file.content_type)


async def download_file_from_object_storage(file_path: str, storage_bucket: str):
    bucket = storage_client.bucket(storage_bucket)
    blob = bucket.blob(file_path)
    return blob.download_as_bytes()


async def download_progress_image(
    image_record: ProgressImage,
    storage_bucket: str,
):
    return await download_file_from_object_storage(
        image_record.image_path, storage_bucket
    )


async def upload_segmentation_mask(
    segmask: np.array,
    mask_path: str,
    storage_bucket: str,
):
    in_memory_file = BytesIO()
    np.save(in_memory_file, segmask)
    in_memory_file.seek(0)

    pdb.set_trace()
    # TODO: Fix this shit
