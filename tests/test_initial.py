import pytest

from src.preprocessing import clean_text
from src.text_classification import classify_text
from src.prediction import get_final_prediction

def test_clean_text():
    """Test that the clean_text function works as expected."""
    # Currently just tests that strip works
    assert clean_text("  hello  ") == "hello"

def test_classify_text_stub():
    """Test the stub text classification function."""
    result = classify_text("Some text")
    assert "prediction" in result
    assert result["prediction"] == "unknown"

def test_get_final_prediction_stub():
    """Test the stub final prediction function."""
    text_res = {"prediction": "unknown", "confidence": 0.0}
    final_res = get_final_prediction(text_res)
    assert "final_prediction" in final_res
    assert final_res["final_prediction"] == "unknown"
