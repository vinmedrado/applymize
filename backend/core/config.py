import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "Applymize")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://applymize:applymize@localhost:5432/applymize")
    test_database_url: str = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_applymize.db")

    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    refresh_secret_key: str = os.getenv("REFRESH_SECRET_KEY", "dev-refresh-secret-change-me")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "14"))

    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
    )
    cors_origin_regex: str | None = os.getenv("CORS_ORIGIN_REGEX") or None
    cors_allow_credentials: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    app_timezone: str = os.getenv("APP_TIMEZONE", os.getenv("TZ", "America/Sao_Paulo"))
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    password_min_length: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))

    frontend_base_url: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    password_reset_token_minutes: int = int(os.getenv("PASSWORD_RESET_TOKEN_MINUTES", "30"))
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    application_agent_daily_limit: int = int(os.getenv("APPLICATION_AGENT_DAILY_LIMIT", "10"))
    application_agent_min_profile_completeness: float = float(os.getenv("APPLICATION_AGENT_MIN_PROFILE_COMPLETENESS", "35"))

    strategy_weight_match: float = float(os.getenv("STRATEGY_WEIGHT_MATCH", "0.38"))
    strategy_weight_recency: float = float(os.getenv("STRATEGY_WEIGHT_RECENCY", "0.16"))
    strategy_weight_competition: float = float(os.getenv("STRATEGY_WEIGHT_COMPETITION", "0.14"))
    strategy_weight_location: float = float(os.getenv("STRATEGY_WEIGHT_LOCATION", "0.10"))
    strategy_weight_remote: float = float(os.getenv("STRATEGY_WEIGHT_REMOTE", "0.10"))
    strategy_weight_seniority: float = float(os.getenv("STRATEGY_WEIGHT_SENIORITY", "0.12"))

    notifications_enabled: bool = os.getenv("NOTIFICATIONS_ENABLED", "false").lower() == "true"
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    evolution_api_url: str = os.getenv("EVOLUTION_API_URL", "")
    evolution_api_key: str = os.getenv("EVOLUTION_API_KEY", "")
    evolution_instance_id: str = os.getenv("EVOLUTION_INSTANCE_ID", "")
    evolution_instance_prefix: str = os.getenv("EVOLUTION_INSTANCE_PREFIX", "applymize")
    evolution_default_country_code: str = os.getenv("EVOLUTION_DEFAULT_COUNTRY_CODE", "55")
    evolution_target_number: str = os.getenv("EVOLUTION_TARGET_NUMBER", "")
    whatsapp_enabled: bool = os.getenv("WHATSAPP_ENABLED", "true").lower() == "true"
    whatsapp_connected_cache_seconds: int = int(os.getenv("WHATSAPP_CONNECTED_CACHE_SECONDS", "600"))
    whatsapp_status_force_refresh_seconds: int = int(os.getenv("WHATSAPP_STATUS_FORCE_REFRESH_SECONDS", "1800"))
    automation_scheduler_enabled: bool = os.getenv("AUTOMATION_SCHEDULER_ENABLED", "false").lower() == "true"
    automation_scheduler_loop_seconds: int = int(os.getenv("AUTOMATION_SCHEDULER_LOOP_SECONDS", "300"))
    automation_default_ingest_limit: int = int(os.getenv("AUTOMATION_DEFAULT_INGEST_LIMIT", "20"))
    automation_default_provider: str = os.getenv("AUTOMATION_DEFAULT_PROVIDER", "all")
    automation_default_term: str = os.getenv("AUTOMATION_DEFAULT_TERM", "Analista de Dados")
    automation_default_city: str = os.getenv("AUTOMATION_DEFAULT_CITY", "São Paulo")
    automation_default_state: str = os.getenv("AUTOMATION_DEFAULT_STATE", "SP")
    automation_default_country: str = os.getenv("AUTOMATION_DEFAULT_COUNTRY", "Brazil")
    automation_default_infojobs_city_code: str = os.getenv("AUTOMATION_DEFAULT_INFOJOBS_CITY_CODE", "5211323")
    automation_whatsapp_delay_seconds: float = float(os.getenv("AUTOMATION_WHATSAPP_DELAY_SECONDS", "2"))
    automation_max_notifications_per_run: int = int(os.getenv("AUTOMATION_MAX_NOTIFICATIONS_PER_RUN", "5"))
    notification_max_per_run: int = int(os.getenv("NOTIFICATION_MAX_PER_RUN", "5"))
    notification_min_priority: str = os.getenv("NOTIFICATION_MIN_PRIORITY", "HIGH")
    job_radar_enabled: bool = os.getenv("JOB_RADAR_ENABLED", "false").lower() == "true"
    job_radar_interval: str = os.getenv("JOB_RADAR_INTERVAL", "24h")

    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    ollama_enabled: bool = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    career_ai_timeout_seconds: float = float(os.getenv("CAREER_AI_TIMEOUT_SECONDS", "25"))
    career_ai_max_message_chars: int = int(os.getenv("CAREER_AI_MAX_MESSAGE_CHARS", "3000"))
    linkedin_analyzer_daily_limit: int = int(os.getenv("LINKEDIN_ANALYZER_DAILY_LIMIT", "3"))
    career_ai_daily_limit: int = int(os.getenv("CAREER_AI_DAILY_LIMIT", "20"))
    public_ai_demo_enabled: bool = os.getenv("PUBLIC_AI_DEMO_ENABLED", "false").lower() == "true"
    applymize_fit_daily_limit: int = int(os.getenv("APPLYMIZE_FIT_DAILY_LIMIT", "8"))
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_price_pro_monthly: str = os.getenv("STRIPE_PRICE_PRO_MONTHLY", "")
    stripe_price_recruiter_monthly: str = os.getenv("STRIPE_PRICE_RECRUITER_MONTHLY", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

    def cors_origin_list(self) -> list[str]:
        raw = [x.strip() for x in self.cors_origins.split(",") if x.strip()]
        if self.environment.lower() in {"production", "prod"}:
            return [x for x in raw if x != "*"]
        return raw or ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
