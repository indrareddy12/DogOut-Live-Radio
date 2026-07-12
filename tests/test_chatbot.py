import pytest
from unittest.mock import patch
from app.services.chatbot import ChatbotService

def test_chatbot_fallback_translation():
    service = ChatbotService()
    
    raw_event = "14.3: Shaheen Afridi to Virat Kohli, OUT! Clean bowled!"
    persona = "Ravi Shastri"
    
    with patch("app.services.chatbot.api_key", None):
        translation = service.translate_to_persona(persona, raw_event, "Wicket (Bowled)")
    
    assert translation is not None
    assert len(translation) > 0
    # The offline fallback includes the raw event details up to the comma
    assert "14.3: Shaheen Afridi to Virat Kohli!" in translation or "14.3: Shaheen Afridi to Virat Kohli" in translation

def test_chatbot_personas():
    service = ChatbotService()
    raw_event = "15.1: Jasprit Bumrah to Babar Azam, Dot Ball"
    
    with patch("app.services.chatbot.api_key", None):
        shastri = service.translate_to_persona("Ravi Shastri", raw_event, "Dot Ball")
        sehwag = service.translate_to_persona("Virender Sehwag", raw_event, "Dot Ball")
        harbhajan = service.translate_to_persona("Harbhajan Singh", raw_event, "Dot Ball")
    
    assert shastri is not None
    assert sehwag is not None
    assert harbhajan is not None
    
    # Verify different personas output different texts
    assert shastri != sehwag
    assert sehwag != harbhajan
