"""
Configuration — loads settings from .env with validation and live reload support.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)


class Settings:
    """Application settings loaded from environment variables."""

    @property
    def NEO4J_URI(self) -> str:
        return os.getenv("NEO4J_URI", "bolt://localhost:7687")

    @property
    def NEO4J_USER(self) -> str:
        return os.getenv("NEO4J_USER", "neo4j")

    @property
    def NEO4J_PASSWORD(self) -> str:
        return os.getenv("NEO4J_PASSWORD", "lexgraph2024")

    @property
    def GEMINI_API_KEY(self) -> str:
        return os.getenv("GEMINI_API_KEY", "")

    @property
    def PORT(self) -> int:
        return int(os.getenv("PORT", "3000"))

    def reload(self):
        """Reload settings from .env file."""
        load_dotenv(dotenv_path=_env_path, override=True)

    def validate(self):
        """Print diagnostic info about the current configuration."""
        print("\n📋 Configuration:")
        print(f"   NEO4J_URI:      {self.NEO4J_URI}")
        print(f"   NEO4J_USER:     {self.NEO4J_USER}")
        print(f"   NEO4J_PASSWORD: {'*' * len(self.NEO4J_PASSWORD) if self.NEO4J_PASSWORD else '(not set)'}")

        api_key = self.GEMINI_API_KEY
        if not api_key or api_key == "your_gemini_api_key_here":
            print(f"   GEMINI_API_KEY: ⚠️  Not configured")
        else:
            print(f"   GEMINI_API_KEY: {api_key[:8]}...{api_key[-4:]}")

        print(f"   PORT:           {self.PORT}")
        print()


settings = Settings()
