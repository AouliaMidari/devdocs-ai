"""Configuration centralisee de DevDocs AI.

Les reglages sont lus dans cet ordre de priorite (la premiere valeur trouvee gagne) :
1. les variables d'environnement du systeme (ex. : $env:DEVDOCS_LOG_LEVEL) ;
2. le fichier .env a la racine du projet (jamais versionne) ;
3. les valeurs par defaut definies dans la classe Settings.

Toutes les variables commencent par le prefixe DEVDOCS_ pour eviter les
collisions avec les variables d'autres outils installes sur la machine.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# core/config.py -> core/ -> racine du projet (independant du dossier courant)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Reglages de l'application, valides par Pydantic au demarrage."""

    model_config = SettingsConfigDict(
        env_prefix="DEVDOCS_",
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,  # DEVDOCS_X= (valeur vide) -> valeur par defaut
        extra="forbid",  # une variable inconnue dans .env (faute de frappe) -> erreur
        frozen=True,  # les reglages ne changent pas pendant l'execution
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    retrieval_top_k: int = Field(default=5, ge=1, le=50)

    # Cle API du LLM (etape 11). SecretStr masque la valeur dans print() et les logs.
    llm_api_key: SecretStr | None = None

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: Any) -> Any:
        """Accepte 'debug' ou ' Debug ' et les convertit en 'DEBUG'."""
        if isinstance(value, str):
            return value.strip().upper()
        return value


@lru_cache
def get_settings() -> Settings:
    """Retourne une instance unique des reglages (lue une seule fois)."""
    return Settings()
