import pytest
import json
from unittest.mock import AsyncMock, patch

from src.nlu.processor import classify_intent_and_extract_entities

@pytest.mark.asyncio
@patch('src.nlu.processor.model.generate_content_async')
async def test_classify_summary_intent(mock_generate_content):
    """Test classifying a 'get_project_summary' intent."""
    # Arrange
    user_input = "Tell me about the Bored Ape Yacht Club collection"
    mock_response_text = json.dumps({
        "intent": "get_project_summary",
        "entities": {
            "collection_name": "Bored Ape Yacht Club"
        },
        "confidence": 0.95,
        "reasoning": "The user is asking for information about a specific NFT collection."
    })
    
    mock_gemini_response = AsyncMock()
    mock_gemini_response.text = f"```json\n{mock_response_text}\n```"
    mock_generate_content.return_value = mock_gemini_response

    # Act
    result = await classify_intent_and_extract_entities(user_input)

    # Assert
    assert result['intent'] == 'get_project_summary'
    assert result['entities']['collection_name'] == 'Bored Ape Yacht Club'
    assert result['confidence'] == 0.95
    mock_generate_content.assert_called_once()

@pytest.mark.asyncio
@patch('src.nlu.processor.model.generate_content_async')
async def test_classify_price_alert_intent(mock_generate_content):
    """Test classifying a 'set_price_alert' intent with entities."""
    # Arrange
    user_input = "alert me if doodles drops below 10 eth"
    mock_response_text = json.dumps({
        "intent": "set_price_alert",
        "entities": {
            "collection_name": "doodles",
            "threshold_price": 10,
            "direction": "below"
        },
        "confidence": 0.98,
        "reasoning": "The user wants a notification based on a price threshold for an NFT collection."
    })

    mock_gemini_response = AsyncMock()
    mock_gemini_response.text = mock_response_text
    mock_generate_content.return_value = mock_gemini_response

    # Act
    result = await classify_intent_and_extract_entities(user_input)

    # Assert
    assert result['intent'] == 'set_price_alert'
    assert result['entities']['collection_name'] == 'doodles'
    assert result['entities']['threshold_price'] == 10
    assert result['entities']['direction'] == 'below'
    assert result['confidence'] == 0.98
