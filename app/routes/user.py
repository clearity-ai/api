import os
from typing import Optional, Annotated

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    status,
    HTTPException,
    Form,
    File,
)
from fastapi.responses import Response
from firebase_admin import auth as firebase_auth

from app.auth.authenticate import firebase, authenticate_user_credentials
from app.database.connection import get_session
from app.database.querying import (
    insert_record,
    get_record,
    get_records_by_field,
    update_record,
    delete_record,
)
from app.database.storing import (
    upload_file_to_object_storage,
    download_file_from_object_storage,
)
from app.models.user import UserSignup, UserSignin, User, UserUpdate
from app.models.response import (
    ResponseModel,
    ResponseOneUser,
    TokenResponse,
)


user_router = APIRouter(tags=["Users"])

storage_bucket = os.getenv("STORAGE_BUCKET_USER_ACCOUNT_IMAGES")


@user_router.post(
    "/user/signup/",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def signup_user(
    email: str = Form(...),
    password: str = Form(...),
    username: str = Form(...),
    sex: str = Form(...),
    birthdate: str = Form(...),
    profile_picture: Annotated[UploadFile, File(description="Some description")] = None,
    session=Depends(get_session),
) -> dict:

    user_data = UserSignup(
        email=email, password=password, username=username, sex=sex, birthdate=birthdate
    )

    try:
        firebase_user = firebase_auth.create_user(
            email=user_data.email, password=user_data.password
        )
    except firebase_auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400, detail="User with this email already exists."
        )

    profile_picture_path = (
        f"{firebase_user.uid}/profile_picture/{profile_picture.filename}"
    )
    await upload_file_to_object_storage(
        profile_picture, profile_picture_path, storage_bucket=storage_bucket
    )

    user = User(
        id=firebase_user.uid,
        email=user_data.email,
        username=user_data.username,
        sex=user_data.sex,
        birthdate=user_data.birthdate,
        profile_picture=profile_picture_path,
    )
    await insert_record(user, session)

    return {"message": "User successfully registered!"}


@user_router.post("/user/signin/", response_model=TokenResponse)
async def singin_user(user_data: UserSignin, session=Depends(get_session)) -> dict:

    # authenticate user with password via firebase
    try:
        firebase_user = firebase.auth().sign_in_with_email_and_password(
            user_data.email, user_data.password
        )  # Caution: Not the same datatype as in signup function
        firebase_token = firebase_user["idToken"]

        user = await get_records_by_field(firebase_user["localId"], "id", User, session)

        user = user[0]
        assert user.email == user_data.email, "Major error in user authentication."

        return {"access_token": firebase_token, "data": {"user_id": user.id}}

    except firebase_auth.EmailNotFoundError:
        raise HTTPException(status_code=400, detail="Invalid email.")
    except ValueError:  # TODO: Check if this occurs in other cases
        raise HTTPException(status_code=400, detail="Invalid password.")


@user_router.get("/user/get/", response_model=ResponseOneUser)
async def retrieve_user(
    user_firebase_id: str = Depends(authenticate_user_credentials),
    session=Depends(get_session),
) -> dict:
    user = await get_records_by_field(user_firebase_id, "id", User, session)
    user = user[0]

    return {"message": "User successfully retrieved!", "data": user}


@user_router.get("/user/get-profile-picture/")
async def retrieve_profile_picture(
    user_firebase_id: str = Depends(authenticate_user_credentials),
    session=Depends(get_session),
) -> Response:
    user = await get_records_by_field(user_firebase_id, "id", User, session)
    user = user[0]
    if user.profile_picture:
        profile_picture = await download_file_from_object_storage(
            user.profile_picture, storage_bucket
        )
        return Response(content=profile_picture, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="Profile picture not found.")


@user_router.put("/user/", response_model=ResponseOneUser)
async def update_user(
    updated_user: UserUpdate,
    user_firebase_id: str = Depends(authenticate_user_credentials),
    session=Depends(get_session),
) -> dict:

    user = await get_records_by_field(user_firebase_id, "id", User, session)
    user = user[0]

    record = await update_record(user.id, User, updated_user, session)
    return {"message": "User sucessfully updated!", "data": record}


@user_router.delete("/user/", response_model=ResponseModel)
async def delete_user(
    user_firebase_id: str = Depends(authenticate_user_credentials),
    session=Depends(get_session),
) -> dict:
    user = await get_records_by_field(user_firebase_id, "id", User, session)
    user = user[0]
    await delete_record(user.id, User, session)
    return {"message": "User successfully deleted!"}
