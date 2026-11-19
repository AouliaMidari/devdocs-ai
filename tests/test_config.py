"""Tests de la configuration centralisee (core/config.py).

Chaque test est isole : il ignore le vrai fichier .env du projet et les
variables DEVDOCS_ eventuellement definies sur la machine.
"""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.config import PROJECT_ROOT, Settings, get_settings


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    """Supprime les variables DEVDOCS_ de la machine et vide le cache."""
    for name in list(os.environ):
        if name.upper().startswith("DEVDOCS_"):
            monkeypatch.delenv(name)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def write_env_file(directory: Path, content: str) -> Path:
    """Cree un fichier .env temporaire et renvoie son chemin."""
    env_file = directory / ".env"
    env_file.write_text(content, encoding="utf-8")
    return env_file


def test_defaults_without_env_file():
    settings = Settings(_env_file=None)

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.retrieval_top_k == 5
    assert settings.llm_api_key is None


def test_environment_variable_overrides_default(monkeypatch):
    monkeypatch.setenv("DEVDOCS_RETRIEVAL_TOP_K", "8")

    settings = Settings(_env_file=None)

    assert settings.retrieval_top_k == 8  # le texte "8" est converti en entier 8


def test_env_file_is_read(tmp_path):
    env_file = write_env_file(tmp_path, "DEVDOCS_LOG_LEVEL=WARNING\n")

    settings = Settings(_env_file=env_file)

    assert settings.log_level == "WARNING"


def test_environment_variable_has_priority_over_env_file(tmp_path, monkeypatch):
    env_file = write_env_file(tmp_path, "DEVDOCS_LOG_LEVEL=WARNING\n")
    monkeypatch.setenv("DEVDOCS_LOG_LEVEL", "ERROR")

    settings = Settings(_env_file=env_file)

    assert settings.log_level == "ERROR"


def test_log_level_is_normalized(monkeypatch):
    monkeypatch.setenv("DEVDOCS_LOG_LEVEL", " debug ")

    settings = Settings(_env_file=None)

    assert settings.log_level == "DEBUG"


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("DEVDOCS_RETRIEVAL_TOP_K", "0"),
        ("DEVDOCS_RETRIEVAL_TOP_K", "51"),
        ("DEVDOCS_RETRIEVAL_TOP_K", "abc"),
        ("DEVDOCS_ENVIRONMENT", "staging"),
        ("DEVDOCS_LOG_LEVEL", "VERBOSE"),
    ],
)
def test_invalid_values_are_rejected(monkeypatch, variable, value):
    monkeypatch.setenv(variable, value)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_unknown_variable_in_env_file_is_rejected(tmp_path):
    # Faute de frappe volontaire : LOG_LEVL au lieu de LOG_LEVEL
    env_file = write_env_file(tmp_path, "DEVDOCS_LOG_LEVL=DEBUG\n")

    with pytest.raises(ValidationError):
        Settings(_env_file=env_file)


def test_empty_api_key_is_treated_as_missing(tmp_path):
    env_file = write_env_file(tmp_path, "DEVDOCS_LLM_API_KEY=\n")

    settings = Settings(_env_file=env_file)

    assert settings.llm_api_key is None


def test_api_key_is_hidden_when_printed(monkeypatch):
    monkeypatch.setenv("DEVDOCS_LLM_API_KEY", "cle-factice-123")

    settings = Settings(_env_file=None)

    assert "cle-factice-123" not in str(settings)
    assert "cle-factice-123" not in repr(settings)
    assert settings.llm_api_key is not None
    assert settings.llm_api_key.get_secret_value() == "cle-factice-123"


def test_settings_are_immutable():
    settings = Settings(_env_file=None)

    with pytest.raises(ValidationError):
        settings.retrieval_top_k = 10


def test_get_settings_returns_the_same_instance():
    assert get_settings() is get_settings()


def test_env_example_matches_settings():
    # .env.example doit toujours correspondre aux champs de Settings :
    # avec extra="forbid", ce test echoue si une variable est mal nommee.
    settings = Settings(_env_file=PROJECT_ROOT / ".env.example")

    assert settings.llm_api_key is None
