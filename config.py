from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8',
                                      extra='ignore')

    ELEVENLABS_API_KEY: str
    DEBUG: False
    GEMINI_API_KEY: str


config = Settings()