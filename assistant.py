import time
from pydantic import BaseModel

from openai import AsyncOpenAI
from openai.types.completion_usage import CompletionUsage
from db import FaqCollection
from config import OPENAI_API_KEY, OPENAI_MODEL
from prompt import INSTRUCTION_PROMPT, RAG_PROMPT_TEMPLATE, OutputStructure, REQUERY_PROMPT, REQUERY_USER_PROMPT_TEMPLATE, RequeryResponse

    
def to_message(role: str, content: str, name: str = None) -> dict:
    message = {
        "role": role,
        "content": content  
    }
    if name is not None:
        message["name"] = name
    return message

def to_developer_message(text: str, name: str = None) -> dict:
    return to_message("system", text, name)

def to_user_message(text: str, name: str = None) -> dict: 
    return to_message("user", text, name)

def to_assistant_message(text: str, name: str = None) -> dict:
    return to_message("assistant", text, name)

def to_faq_message(faq_data: list[dict]) -> dict:
    if faq_data:
        str_faq_data = str(faq_data)
    else:
        str_faq_data = "No relevant FAQ found."

    text = RAG_PROMPT_TEMPLATE.format(faq_data=str_faq_data)
    return to_assistant_message(text, name="faq_data")


class AssistantReport(BaseModel):
    model: str
    completion_tokens: int = 0
    prompt_tokens: int = 0
    cache_hit_tokens: int = 0

    def update_from_usage(self, usage: CompletionUsage):
        self.completion_tokens += usage.completion_tokens
        self.prompt_tokens += usage.prompt_tokens
        self.cache_hit_tokens += usage.prompt_tokens_details.cached_tokens


class Assistant:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.faq_collection = FaqCollection()
        self.model = OPENAI_MODEL

        self.report = AssistantReport(model=self.model)
    
    async def search_faq(self, query: str):
        search_results = await self.faq_collection.vector_search(query)
        search_entities = [result['entity'] for result in search_results]
        return search_entities

    async def make_requery(self, conversation_history: list[dict], user_query: str):
        developer_message = to_developer_message(REQUERY_PROMPT)
        user_query_message = to_user_message(REQUERY_USER_PROMPT_TEMPLATE.format(conversation_history=conversation_history, user_question=user_query))

        messages = [developer_message, user_query_message]

        response = await self.client.beta.chat.completions.parse(
            model=self.model, 
            messages=messages,
            response_format=RequeryResponse,
            seed=42,
        )

        self.report.update_from_usage(response.usage)
        return response.choices[0].message.parsed.new_query

    async def stream(self, conversation_history: list[dict], user_query: str):
        developer_message = to_developer_message(INSTRUCTION_PROMPT)
        user_query_message = to_user_message(user_query)

        requery = await self.make_requery(conversation_history, user_query)
        searched_faq = await self.search_faq(requery)
        faq_message = to_faq_message(searched_faq)

        messages = [developer_message] + conversation_history + [user_query_message] + [faq_message]
        async with self.client.beta.chat.completions.stream(
            model=self.model,
            messages=messages,
            response_format=OutputStructure,
            stream_options={
                "include_usage": True
            },
            seed=42,
        ) as stream:
            async for chunk in stream:
                if chunk.type == "content.delta":
                    yield chunk.delta
                
                elif chunk.type == "chunk" and chunk.chunk.usage is not None:
                    usage = chunk.chunk.usage
                    self.report.update_from_usage(usage)
