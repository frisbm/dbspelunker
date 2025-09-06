from pydantic_ai import Agent

from dbspelunker.genai import GeminiModel


class DBSpelunker:
    def __init__(self, gemini_model: GeminiModel, db_connection_str: str):
        self.gemini_model = gemini_model
        self.db_connection_str = db_connection_str

    def initiator_agent(self) -> Agent:
        return Agent(
            model=self.gemini_model.get_model(temperature=0.8),
        )
