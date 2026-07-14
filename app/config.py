from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    db_path: str = "./data/bot.db"
    base_currency: str = "RUB"
    rate_cache_ttl_seconds: int = 90


settings = Settings()
