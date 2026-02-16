from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BERTOPIC_MODEL_PATH: str = "../models/fishing_survey_bertopic"
    DATABASE_PATH: str = "./data/app.db"
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"  # "openai" or "local"
    LOCAL_LLM_MODEL: str = "flan-t5"
    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
