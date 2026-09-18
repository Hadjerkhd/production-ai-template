# tests/regression/test_llm_service_random.py

import random
import pytest

from app.services.llm_service import LLMService


@pytest.mark.asyncio
async def test_llm_regression():

    service = LLMService()

    response = await service.generate_response(
        "Hello"
    )

    assert response is not None

    # Random failure to demonstrate CI/CD gate
    assert random.random() > 0.5, (
        "Intentional random regression failure"
    )