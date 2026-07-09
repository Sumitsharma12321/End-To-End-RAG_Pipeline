import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..","backend")))

from unittest.mock import patch, MagicMock
from app.services.llm_service import generate_answer


# ===================================================
# SECTION 1 — Prompt building tests (no API call)
# ===================================================

class TestPromptBuilding:
    """LLM ko bhejne se pehle prompt sahi bana ya nahi"""

    def test_answer_is_string(self):
        # Mock Groq API call — real API call nahi hoga
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "This is a test answer."
            mock_client.chat.completions.create.return_value = mock_response

            result = generate_answer(
                question="What is AI?",
                context_chunks=["AI is artificial intelligence."]
            )
            assert isinstance(result, str)

    def test_answer_is_not_empty(self):
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "AI stands for Artificial Intelligence."
            mock_client.chat.completions.create.return_value = mock_response

            result = generate_answer(
                question="What is AI?",
                context_chunks=["AI is artificial intelligence."]
            )
            assert len(result.strip()) > 0

    def test_llm_called_once(self):
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "Test answer."
            mock_client.chat.completions.create.return_value = mock_response

            generate_answer("Test?", ["Context here."])

            # Sirf ek baar call hona chahiye
            mock_client.chat.completions.create.assert_called_once()

    def test_question_in_prompt(self):
        """Question prompt mein jaana chahiye"""
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "Answer."
            mock_client.chat.completions.create.return_value = mock_response

            generate_answer("What is RAG?", ["RAG is retrieval augmented generation."])

            call_args = mock_client.chat.completions.create.call_args
            # messages argument nikalo
            messages = call_args[1].get("messages") or call_args[0][0] if call_args[0] else None
            if messages:
                prompt_text = str(messages)
                assert "What is RAG?" in prompt_text

    def test_context_in_prompt(self):
        """Context chunks prompt mein jaane chahiye"""
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "Answer."
            mock_client.chat.completions.create.return_value = mock_response

            context = ["This is very specific context about neural networks."]
            generate_answer("Question?", context)

            call_args = mock_client.chat.completions.create.call_args
            messages = call_args[1].get("messages") or []
            prompt_text = str(messages)
            assert "neural networks" in prompt_text

    def test_multiple_chunks_combined(self):
        """Multiple chunks ek saath prompt mein aane chahiye"""
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "Combined answer."
            mock_client.chat.completions.create.return_value = mock_response

            chunks = [
                "First chunk about Python.",
                "Second chunk about FastAPI.",
                "Third chunk about databases."
            ]
            result = generate_answer("Tell me everything.", chunks)
            assert isinstance(result, str)

            # Verify API was called
            mock_client.chat.completions.create.assert_called_once()

    def test_empty_chunks_handled(self):
        """Empty chunk list pe crash nahi hona chahiye"""
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "I don't know based on the document."
            mock_client.chat.completions.create.return_value = mock_response

            result = generate_answer("Any question?", [])
            assert isinstance(result, str)


# ===================================================
# SECTION 2 — Response handling tests
# ===================================================

class TestResponseHandling:
    """LLM ka response sahi se handle ho raha hai"""

    def test_returns_model_response_text(self):
        expected = "Machine learning is a subset of AI that learns from data."
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = expected
            mock_client.chat.completions.create.return_value = mock_response

            result = generate_answer("What is ML?", ["ML context here."])
            assert result == expected

    def test_strips_whitespace_from_response(self):
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "  Answer with spaces.  "
            mock_client.chat.completions.create.return_value = mock_response

            result = generate_answer("Question?", ["Context."])
            # strip hona chahiye
            assert result == result.strip()

    def test_long_answer_returned_fully(self):
        long_answer = "This is a very detailed answer. " * 50
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = long_answer.strip()
            mock_client.chat.completions.create.return_value = mock_response

            result = generate_answer("Explain everything.", ["Context."])
            assert len(result) > 100

    def test_answer_with_special_characters(self):
        special = "AI uses math like: y = mx + b. Cost = Σ(error²). Rate: 0.001%"
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = special
            mock_client.chat.completions.create.return_value = mock_response

            result = generate_answer("Math question?", ["Math context."])
            assert isinstance(result, str)
            assert len(result) > 0


# ===================================================
# SECTION 3 — Error handling tests
# ===================================================

class TestErrorHandling:
    """Errors gracefully handle ho rahe hain"""

    def test_api_timeout_raises_exception(self):
        """API timeout pe proper exception aana chahiye"""
        with patch("app.services.llm_service.client") as mock_client:
            import groq
            mock_client.chat.completions.create.side_effect = Exception("Connection timeout")

            with pytest.raises(Exception):
                generate_answer("Question?", ["Context."])

    def test_api_error_raises_exception(self):
        """API error pe exception propagate hona chahiye"""
        with patch("app.services.llm_service.client") as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")

            with pytest.raises(Exception) as exc_info:
                generate_answer("Question?", ["Context."])

            assert "Rate limit" in str(exc_info.value)

    def test_none_response_handled(self):
        """None response pe crash nahi hona chahiye"""
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = None
            mock_client.chat.completions.create.return_value = mock_response

            # Ya toh handle kare ya exception raise kare — crash nahi hona chahiye
            try:
                result = generate_answer("Question?", ["Context."])
                # Agar handle kiya toh string hona chahiye
                assert result is None or isinstance(result, str)
            except (TypeError, AttributeError):
                pass  # Exception raise karna bhi acceptable hai


# ===================================================
# SECTION 4 — Real API test (optional — .env key chahiye)
# ===================================================

class TestRealGroqAPI:
    """
    Ye tests real Groq API call karte hain.
    Run karo sirf tab jab internet ho aur GROQ_API_KEY .env mein ho.
    Command: pytest tests/test_llm.py::TestRealGroqAPI -v
    """

    @pytest.mark.skip(reason="Real API call — run manually")
    def test_real_groq_call_returns_answer(self):
        """Real Groq API se actual answer aata hai"""
        result = generate_answer(
            question="What is Python?",
            context_chunks=[
                "Python is a high level programming language.",
                "Python was created by Guido van Rossum in 1991.",
                "Python is widely used for data science and web development."
            ]
        )
        assert isinstance(result, str)
        assert len(result) > 20
        assert "python" in result.lower()
        print(f"\nReal API answer: {result[:200]}")

    @pytest.mark.skip(reason="Real API call — run manually")
    def test_real_groq_response_time(self):
        """Response time 30 seconds se kam hona chahiye"""
        import time
        start = time.time()
        result = generate_answer(
            question="What is machine learning?",
            context_chunks=["Machine learning is a type of AI that learns from data."]
        )
        elapsed = time.time() - start
        print(f"\nResponse time: {elapsed:.2f}s")
        assert elapsed < 30
        assert len(result) > 0

    @pytest.mark.skip(reason="Real API call — run manually")
    def test_real_groq_hindi_question(self):
        """Hindi question pe bhi answer aata hai"""
        result = generate_answer(
            question="Machine learning kya hota hai?",
            context_chunks=["Machine learning is a subset of AI that learns patterns from data."]
        )
        assert isinstance(result, str)
        assert len(result) > 10
        print(f"\nHindi query answer: {result[:200]}")