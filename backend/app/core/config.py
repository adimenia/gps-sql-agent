from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database settings
    postgres_host: str = "localhost"
    postgres_port: int = 5433  # Docker container port
    postgres_db: str = "sports_analytics"
    postgres_user: str = "postgres"
    postgres_password: str = "P@ssw0rd"  # Match actual Docker password
    
    # Catapult API settings
    catapult_api_url: str = "https://connect-eu.catapultsports.com/api/v6"
    catapult_api_token: str = ""
    
    # Application settings
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # ETL settings
    etl_schedule_hours: int = 6
    etl_batch_size: int = 100
    
    # LLM API settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_model: str = "gpt-4"  # Default model
    llm_max_tokens: int = 1000
    llm_temperature: float = 0.1
    
    @property
    def database_url(self) -> str:
        """Construct database URL from components."""
        if self.postgres_password:
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        else:
            return f"postgresql://{self.postgres_user}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def async_database_url(self) -> str:
        """Construct async database URL from components."""
        if self.postgres_password:
            return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        else:
            return f"postgresql+asyncpg://{self.postgres_user}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def catapult_headers(self) -> dict:
        """Construct headers for Catapult API."""
        return {
            "accept": "application/json",
            "authorization": f"Bearer {self.catapult_api_token}"
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()