import asyncio
import random
from dataclasses import dataclass, field
from typing import (
    Awaitable,
    Callable,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    cast,
)

from google import genai
from google.genai import types
from google.genai.types import ToolListUnion
from pydantic import BaseModel

from config import Config

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")


# ---- A callable protocol for the *bound* generate_content method ----
class GenerateContentFn(Protocol):
    def __call__(
        self,
        *,
        model: str,
        contents: Union[types.ContentListUnion, types.ContentListUnionDict],
        config: Optional[types.GenerateContentConfigOrDict] = None,
    ) -> Awaitable[types.GenerateContentResponse]: ...


# ------------------------------- Agent -------------------------------
@dataclass
class Agent[T: BaseModel]:
    gemini_model: "GeminiModel"
    system_instruction: str
    temperature: float
    response_schema: Type[T]
    tools: Optional[ToolListUnion]
    generate_content_func: GenerateContentFn
    __conversation_history: List[str] = field(default_factory=list)
    max_retries: int = 3

    async def _retry_invoke[R](
        self, invoke_func: Callable[[], Awaitable[R]], max_retries: int = 3
    ) -> R:
        """Retry wrapper for GenAI invoke calls with exponential backoff."""

        last_exception: Optional[BaseException] = None
        for attempt in range(max_retries):
            try:
                return await invoke_func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    delay = (2**attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)
                continue

        # If all retries failed, raise the last exception
        raise Exception("All retries failed") from last_exception

    def _clean_response_text(self, text: str) -> str:
        clean_text = text.strip()
        clean_text = clean_text.strip("\n\r\t ")
        # Remove starting markdown
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        # Remove ending markdown
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        # Strip any remaining leading/trailing whitespace and newlines
        clean_text = clean_text.strip("\n\r\t ")

        return clean_text

    def _parse_response(self, resp: types.GenerateContentResponse) -> T:
        if (
            hasattr(resp, "parsed")
            and resp.parsed is not None
            and isinstance(resp.parsed, self.response_schema)
        ):
            return resp.parsed
        if hasattr(resp, "text") and resp.text is not None:
            clean_text = self._clean_response_text(resp.text)
            raise ValueError(
                f"Failed to parse response text into schema {self.response_schema}: {clean_text}"
            )
        raise ValueError(
            "No valid response received from model, cannot find parsed or text in response"
        )

    async def run(self, prompt: str) -> T:
        self.__conversation_history.append(prompt)

        async def _make_request() -> T:
            contents = "\n".join(self.__conversation_history)
            resp = await self.generate_content_func(
                model=self.gemini_model.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_mime_type="application/json",
                    response_schema=self.response_schema,
                    tools=self.tools,
                    max_output_tokens=self.gemini_model.max_output_tokens,
                    temperature=self.temperature,
                    top_p=self.gemini_model.top_p,
                    top_k=self.gemini_model.top_k,
                    seed=self.gemini_model.seed,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        maximum_remote_calls=self.gemini_model.maximum_remote_calls
                    ),
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=self.gemini_model.thinking_budget
                    ),
                ),
            )
            try:
                parsed_resp = self._parse_response(resp)
                return parsed_resp
            except Exception as e:
                self.__conversation_history.append(
                    f"Error parsing response: {str(e)}. Full response: {resp.model_dump_json(indent=2)}"
                )
                raise e

        resp = await self._retry_invoke(_make_request, max_retries=self.max_retries)
        return resp


class GeminiModel:
    def __init__(self, config: Config):
        self.model = config.model
        self.vertex = genai.Client(
            vertexai=True,
            project=config.project_id,
            location=config.location,
        )

        self.__token_limit = config.token_limit
        self.top_p = config.top_p
        self.top_k = config.top_k
        self.max_output_tokens = config.max_output_tokens
        self.thinking_budget = config.thinking_budget
        self.maximum_remote_calls = config.maximum_remote_calls
        self.seed: Optional[int] = None

    @property
    def token_limit(self) -> int:
        return self.__token_limit

    async def count_tokens(self, contents: str) -> int:
        resp = await self.vertex.aio.models.count_tokens(
            model=self.model, contents=contents
        )
        return resp.total_tokens or 0

    async def tokenize(self, contents: str) -> List[bytes]:
        resp = await self.vertex.aio.models.compute_tokens(
            model=self.model, contents=contents
        )
        if not resp.tokens_info:
            return []
        return resp.tokens_info[0].tokens or []

    def generate_content(self) -> GenerateContentFn:
        return cast(GenerateContentFn, self.vertex.aio.models.generate_content)

    def new_agent(
        self,
        system_instruction: str,
        response_schema: Type[T],
        temperature: float = 1.0,
        tools: Optional[ToolListUnion] = None,
    ) -> Agent[T]:
        return Agent[T](
            gemini_model=self,
            system_instruction=system_instruction,
            response_schema=response_schema,
            temperature=temperature,
            tools=tools,
            generate_content_func=self.generate_content(),
        )
