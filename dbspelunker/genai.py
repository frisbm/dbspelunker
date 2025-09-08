from typing import Optional

from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider

from config import Config


class GeminiModel:
    def __init__(self, config: Config):
        self.model = config.model

        self.provider = GoogleProvider(
            project=config.project_id,
            location=config.location,
        )
        self.__token_limit = config.token_limit
        self.top_p = config.top_p
        self.max_output_tokens = config.max_output_tokens
        self.thinking_budget = config.thinking_budget
        self.maximum_remote_calls = config.maximum_remote_calls
        self.seed: Optional[int] = None

    def get_model(self, temperature: float = 1.0) -> GoogleModel:
        settings = GoogleModelSettings(
            temperature=temperature,
            max_tokens=self.max_output_tokens,
            top_p=self.top_p,
            google_thinking_config={
                "thinking_budget": self.thinking_budget,
            },
        )
        model = GoogleModel(self.model, provider=self.provider, settings=settings)
        return model

    @property
    def token_limit(self) -> int:
        return self.__token_limit
