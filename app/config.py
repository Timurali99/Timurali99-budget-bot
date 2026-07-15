from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    db_path: str = "./data/bot.db"
    base_currency: str = "RUB"
    rate_cache_ttl_seconds: int = 90

    # AI-ассистент (OpenAI-совместимый OpenRouter). Ключ бесплатный: openrouter.ai/keys
    openrouter_api_key: str = ""
    ai_model: str = "meta-llama/llama-3.3-70b-instruct:free"

    # Новости: RSS проверенного источника (по умолчанию RBC). Меняется без деплоя.
    news_rss_url: str = "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"
    news_source_name: str = "РБК"


settings = Settings()
