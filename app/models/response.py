from pydantic import BaseModel
from typing import Union, Optional, List

from app.models.user import User


class ResponseModel(BaseModel):
    message: Optional[str] = None
    data: Optional[Union[list, dict, int, str]] = None


class ResponseAllUsers(ResponseModel):
    data: List[User]


class ResponseOneUser(ResponseModel):
    data: User


class TokenResponse(ResponseModel):
    access_token: str
    token_type: str = "Bearer"
