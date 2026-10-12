import asyncio
import logging
import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import ChatVertexAI

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self._chain = None
        self.prompt = PromptTemplate(
            input_variables=["question"],
            template="You are a helpful assistant. Question: {question} Answer:",
        )

    def _get_chain(self):
        if self._chain is None:
            llm = ChatVertexAI(
                model=settings.VERTEX_AI_MODEL,
                project=settings.GCP_PROJECT_ID,
                location=settings.VERTEX_AI_LOCATION,
                temperature=0.2,
                max_tokens=settings.MAX_OUTPUT_TOKENS,
                timeout=settings.VERTEX_AI_TIMEOUT_SECONDS,
                max_retries=1,
            )
            self._chain = self.prompt | llm | StrOutputParser()
        return self._chain

    async def generate_response(self, query: str) -> str:
        started_at = time.perf_counter()
        try:
            result = await asyncio.wait_for(
                self._get_chain().ainvoke({"question": query}),
                timeout=settings.VERTEX_AI_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "Vertex AI request timed out",
                extra={
                    "model": settings.VERTEX_AI_MODEL,
                    "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
                },
            )
            raise
        except Exception as error:
            logger.error(
                "Vertex AI request failed",
                extra={
                    "model": settings.VERTEX_AI_MODEL,
                    "error_type": type(error).__name__,
                    "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
                },
            )
            raise

        logger.info(
            "Vertex AI request completed",
            extra={
                "model": settings.VERTEX_AI_MODEL,
                "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
            },
        )
        return result


# Singleton instance usually suffices for simple services,
# or use dependency injection if needed.
llm_service = LLMService()
