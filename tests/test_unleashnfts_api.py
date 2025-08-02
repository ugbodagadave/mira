import pytest
import respx
from httpx import Response

from src.services.unleashnfts_api import unleash_nfts_service, BASE_URL

@pytest.mark.asyncio
@respx.mock
async def test_get_collection_metrics_success():
    """Test successful retrieval of collection metrics."""
    # Arrange
    blockchain = "ethereum"
    address = "0xbd49448e92423253930b3310a5563539a68e643e"
    mock_response = {"floor_price": 1.23}
    
    respx.get(f"{BASE_URL}/collection/{blockchain}/{address}/metrics", params={"metrics": "volume"}).mock(
        return_value=Response(200, json=mock_response)
    )

    # Act
    result = await unleash_nfts_service.get_collection_metrics(blockchain, address)

    # Assert
    assert result == mock_response

@pytest.mark.asyncio
@respx.mock
async def test_get_collection_metrics_failure():
    """Test handling of a failed API request."""
    # Arrange
    blockchain = "ethereum"
    address = "0xbd49448e92423253930b3310a5563539a68e643e"
    
    respx.get(f"{BASE_URL}/collection/{blockchain}/{address}/metrics", params={"metrics": "volume"}).mock(
        return_value=Response(404)
    )

    # Act
    result = await unleash_nfts_service.get_collection_metrics(blockchain, address)

    # Assert
    assert result is None
