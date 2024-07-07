import os
import json

from fastapi import Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth as firebase_auth
import pyrebase

# Initialize Firebase Admin SDK for Authentication
firebase_keyfile = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_FILE")
if not firebase_admin._apps:
    firebase_cred = firebase_admin.credentials.Certificate(firebase_keyfile)
    firebase_admin.initialize_app(firebase_cred)
firebase_config = json.load(open(os.getenv("FIREBASE_CONFIG_FILE"), "r"))
firebase = pyrebase.initialize_app(firebase_config)


async def authenticate_user_credentials(
    cred: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> str:
    """Takes HTTP Bearer Token and returns firebase_id of user if valid."""
    if not cred:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in for access. Requires HTTP Bearer Token.",
        )
    try:
        decoded_token = firebase_auth.verify_id_token(cred.credentials)
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired Token. Sign in again.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials. {e}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )

    return decoded_token["user_id"]


async def authenticate_token(token: str):
    try:
        decoded_token = firebase_auth.verify_id_token(token)
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired Token. Sign in again.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials. {e}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )

    return decoded_token["user_id"]
