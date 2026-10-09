from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import ChatVertexAI

from app.config import settings


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
            )
            self._chain = self.prompt | llm | StrOutputParser()
        return self._chain

    async def generate_response(self, query: str) -> str:
        result = await self._get_chain().ainvoke({"question": query})
        return result


# Singleton instance usually suffices for simple services,
# or use dependency injection if needed.
llm_service = LLMService()
