from langchain_core.prompts import PromptTemplate
from langchain_community.llms import FakeListLLM
from langchain_core.output_parsers import StrOutputParser

class LLMService:
    def __init__(self):
        # Initialize a Fake LLM for demonstration purposes.
        # In a real app, you would use OpenAI, Anthropic, etc.
        # e.g., from langchain_openai import OpenAI
        # self.llm = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.llm = FakeListLLM(responses=["I am a trivial AI response.", "Here is another fake response."])
        
        self.prompt = PromptTemplate(
            input_variables=["question"],
            template="You are a helpful assistant. Question: {question} Answer:",
        )
        
        # improved LCEL chain
        self.chain = self.prompt | self.llm | StrOutputParser()

    async def generate_response(self, query: str) -> str:
        result = await self.chain.ainvoke({"question": query})
        return result

# Singleton instance usually suffices for simple services, 
# or use dependency injection if needed.
llm_service = LLMService()
