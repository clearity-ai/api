import asyncio
import httpx
import pytest

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# API #
@pytest.fixture(scope="session")
async def default_client():
    async with httpx.AsyncClient(app=app, base_url="http://app") as client:
        yield client


# Test User #
@pytest.fixture()
def testuser_dict():
    return {
        "email": "testuser@mail.com",
        "password": "testpassword",
        "username": "test-user",
        "sex": "female",
        "birthdate": "2000-01-07",
    }


@pytest.fixture()
def testuser_form():
    return {
        "username": "testuser@mail.com",
        "password": "testpassword",
    }
