from fastapi import status
import httpx
import pytest

from app.tests.fixtures import *


@pytest.mark.asyncio
async def test_signup(testuser_dict, mocker, default_client: httpx.AsyncClient):
    mocker.patch("routes.user.insert_record", return_value=None)
    expected_response = {"data": None, "message": "User successfully registered!"}

    headers = {"accept": "application/json", "Content-Type": "application/json"}
    response = await default_client.post(
        "/user/signup", json=testuser_dict, headers=headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_user_signin(testuser_form, mocker, default_client: httpx.AsyncClient):
    response = await default_client.post("user/signin", data=testuser_form)

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("access_token", None) is not None


@pytest.mark.asyncio
async def test_retrieve_user(testuser_form, default_client: httpx.AsyncClient):
    signin_response = await default_client.post("user/signin", data=testuser_form)
    token = signin_response.json().get("access_token")

    headers = {"content-type": "application/json", "Authorization": f"Bearer {token}"}
    response = await default_client.get("user/get", headers=headers)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_user(testuser_form, default_client: httpx.AsyncClient):
    signin_response = await default_client.post("user/signin", data=testuser_form)
    token = signin_response.json().get("access_token")
    payload = {"username": "testuser"}

    headers = {"content-type": "application/json", "Authorization": f"Bearer {token}"}
    response = await default_client.put("user/", json=payload, headers=headers)

    assert response.status_code == status.HTTP_200_OK
