# tests/regression/test_llm_service_random.py

import pytest

from app.services.llm_service import LLMService


@pytest.mark.asyncio
async def test_llm_regression():
    service = LLMService()

    class FakeChain:
        async def ainvoke(self, _inputs):
            return "test response"

    service._chain = FakeChain()

    response = await service.generate_response("Hello")

    assert response is not None

    assert isinstance(response, str)
