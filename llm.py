"""Gemeinsames LLM-Provider-Modul.

Stellt die LLM-Provider-Abstraktion bereit, die sowohl vom monatlichen
Gartenbericht (monthly_report.py) als auch von der KI-Autofill-Funktion
(app.py) genutzt wird.

Unterstützte LLM-Provider (über LLM_PROVIDER):
    claude   — Anthropic Claude (Standard)
    mistral  — Mistral AI

Benötigte Umgebungsvariablen:
    LLM_PROVIDER       — LLM-Provider: "claude" oder "mistral" (Standard: claude)
    LLM_MODEL          — Modellname (optional, Provider-spezifischer Default)
    ANTHROPIC_API_KEY  — API-Key für Claude (wenn LLM_PROVIDER=claude)
    MISTRAL_API_KEY    — API-Key für Mistral (wenn LLM_PROVIDER=mistral)
"""

from __future__ import annotations

import os
import sys
from abc import ABC, abstractmethod

# ---------------------------------------------------------------------------
# Konfiguration aus Umgebungsvariablen
# ---------------------------------------------------------------------------

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "claude").lower()
LLM_MODEL = os.environ.get("LLM_MODEL", "")


# ---------------------------------------------------------------------------
# LLM-Provider-Abstraktion
# ---------------------------------------------------------------------------

class LLMProvider(ABC):
    """Abstrakte Basisklasse für LLM-Provider."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Sendet den Prompt an das LLM und gibt den generierten Text zurück."""

    @abstractmethod
    def validate_config(self) -> list[str]:
        """Prüft ob alle nötigen Umgebungsvariablen gesetzt sind.
        Gibt eine Liste fehlender Variablen zurück (leer = alles ok)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Anzeigename des Providers."""


class ClaudeProvider(LLMProvider):
    """Anthropic Claude API."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = LLM_MODEL or "claude-sonnet-4-latest"

    @property
    def name(self) -> str:
        return f"Claude ({self.model})"

    def validate_config(self) -> list[str]:
        return ["ANTHROPIC_API_KEY"] if not self.api_key else []

    def generate(self, prompt: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


class MistralProvider(LLMProvider):
    """Mistral AI API."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("MISTRAL_API_KEY", "")
        self.model = LLM_MODEL or "mistral-small-latest"

    @property
    def name(self) -> str:
        return f"Mistral ({self.model})"

    def validate_config(self) -> list[str]:
        return ["MISTRAL_API_KEY"] if not self.api_key else []

    def generate(self, prompt: str) -> str:
        from mistralai import Mistral
        client = Mistral(api_key=self.api_key)
        response = client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
        )
        return response.choices[0].message.content


PROVIDERS: dict[str, type[LLMProvider]] = {
    "claude": ClaudeProvider,
    "mistral": MistralProvider,
}


def get_provider() -> LLMProvider:
    """Erstellt den konfigurierten LLM-Provider."""
    if LLM_PROVIDER not in PROVIDERS:
        print(f"Fehler: Unbekannter LLM_PROVIDER '{LLM_PROVIDER}'. "
              f"Verfügbar: {', '.join(PROVIDERS.keys())}")
        sys.exit(1)
    return PROVIDERS[LLM_PROVIDER]()


def is_llm_configured() -> bool:
    """Prüft ob ein LLM-Provider mit gültigem API-Key konfiguriert ist.

    Gibt True zurück, wenn:
    - LLM_PROVIDER ein bekannter Provider ist UND
    - der zugehörige API-Key gesetzt ist
    """
    if LLM_PROVIDER not in PROVIDERS:
        return False
    provider = PROVIDERS[LLM_PROVIDER]()
    return len(provider.validate_config()) == 0
