import pytest
from unittest.mock import AsyncMock, patch

from src.services.gemini_ai import gemini_service

@pytest.mark.asyncio
@patch('src.services.gemini_ai.genai.GenerativeModel.generate_content_async')
async def test_generate_summary_success(mock_generate_content):
    """Test successful summary generation."""
    # Arrange
    collection_data = {"name": "Test Collection", "stats": {"floor_price": 1.5}}
    mock_response_text = "This is a test summary."
    
    mock_gemini_response = AsyncMock()
    mock_gemini_response.text = mock_response_text
    mock_generate_content.return_value = mock_gemini_response

    # Act
    result = await gemini_service.generate_summary(collection_data)

    # Assert
    assert result == mock_response_text
    mock_generate_content.assert_called_once()

@pytest.mark.asyncio
@patch('src.services.gemini_ai.genai.GenerativeModel.generate_content_async')
async def test_generate_summary_failure(mock_generate_content):
    """Test handling of a failed summary generation."""
    # Arrange
    collection_data = {"name": "Test Collection"}
    mock_generate_content.side_effect = Exception("API Error")

    # Act
    result = await gemini_service.generate_summary(collection_data)

    # Assert
    assert "unable to generate a summary" in result
