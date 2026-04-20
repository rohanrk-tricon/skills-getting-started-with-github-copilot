"""
Pytest configuration and fixtures for FastAPI tests
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from src.app import app


@pytest.fixture
def async_client():
    """
    Fixture that provides an AsyncClient for making asynchronous HTTP requests to the FastAPI app.
    
    Yields:
        AsyncClient: An async HTTP client connected to the test app
    """
    async def get_client():
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    return get_client()


@pytest.fixture
async def client():
    """
    Fixture that provides an AsyncClient for making HTTP requests to the FastAPI app.
    
    This fixture is async-aware and works with pytest-asyncio.
    
    Yields:
        AsyncClient: An async HTTP client connected to the test app
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
