"""Monatlicher Gartenbericht per E-Mail.

Liest die Pflanzendaten aus der Datenbank, erstellt mit einem LLM
einen schön formulierten deutschen Gartenbrief für den aktuellen Monat und
verschickt ihn per Gmail SMTP.

Unterstützte LLM-Provider (über LLM_PROVIDER):
    claude   — Anthropic Claude (Standard)
    mistral  — Mistral AI

Benötigte Umgebungsvariablen:
    DB_PATH            — Pfad zur SQLite-Datenbank (Standard: /data/plants.db)
    LLM_PROVIDER       — LLM-Provider: "claude" oder "mistral" (Standard: claude)
    LLM_MODEL          — Modellname (optional, Provider-spezifischer Default)
    ANTHROPIC_API_KEY  — API-Key für Claude (wenn LLM_PROVIDER=claude)
    MISTRAL_API_KEY    — API-Key für Mistral (wenn LLM_PROVIDER=mistral)
    MAIL_FROM          — Absender-Adresse (z.B. dein.garten@gmail.com)
    MAIL_TO            — Empfänger-Adresse(n), kommasepariert
    MAIL_PASSWORD      — Gmail App-Passwort (nicht das normale Gmail-Passwort!)
    MAIL_SMTP_HOST     — SMTP-Server (Standard: smtp.gmail.com)
    MAIL_SMTP_PORT     — SMTP-Port (Standard: 587)

Ausführen:
    docker exec garden-tracker python monthly_report.py

Oder lokal:
    DB_PATH=plants.db ANTHROPIC_API_KEY=... MAIL_FROM=... MAIL_TO=... MAIL_PASSWORD=... python monthly_report.py
"""

from __future__ import annotations

import os
import smtplib
import sqlite3
import sys
from abc import ABC, abstractmethod
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ---------------------------------------------------------------------------
# Konfiguration aus Umgebungsvariablen
# ---------------------------------------------------------------------------

DB_PATH = os.environ.get("DB_PATH", "/data/plants.db")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "claude").lower()
LLM_MODEL = os.environ.get("LLM_MODEL", "")
MAIL_FROM = os.environ.get("MAIL_FROM", "")
MAIL_TO = os.environ.get("MAIL_TO", "")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
MAIL_SMTP_HOST = os.environ.get("MAIL_SMTP_HOST", "smtp.gmail.com")
MAIL_SMTP_PORT = int(os.environ.get("MAIL_SMTP_PORT", "587"))

GERMAN_MONTHS = {
    1: "Januar", 2: "Februar", 3: "März", 4: "April",
    5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
    9: "September", 10: "Oktober", 11: "November", 12: "Dezember",
}

# Reihenfolge der Ereignistypen im Bericht
EREIGNIS_REIHENFOLGE = [
    "Vorkultur",
    "Direktsaat",
    "Auspflanzen",
    "Blüte",
    "Ernte",
    "Rückschnitt",
    "Düngen",
    "Pflege",
]


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
        self.model = LLM_MODEL or "claude-haiku-4-5"

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


# ---------------------------------------------------------------------------
# Datenbankabfrage
# ---------------------------------------------------------------------------

def get_ereignisse_fuer_monat(monat: int) -> dict[str, list[dict]]:
    """Alle aktiven Pflanzen mit Ereignissen im angegebenen Monat, gruppiert nach Ereignistyp."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    rows = conn.execute(
        """
        SELECT
            p.name,
            p.kategorie,
            p.beschreibung,
            e.ereignistyp,
            e.startmonat,
            e.endmonat,
            e.start_detail,
            e.end_detail
        FROM ereignisse e
        JOIN plants p ON e.plant_id = p.id
        WHERE p.aktiv = 1
          AND e.startmonat <= ?
          AND e.endmonat >= ?
        ORDER BY e.ereignistyp, p.name COLLATE NOCASE
        """,
        (monat, monat),
    ).fetchall()

    conn.close()

    # Gruppieren nach Ereignistyp
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        etyp = row["ereignistyp"]
        if etyp not in grouped:
            grouped[etyp] = []
        grouped[etyp].append({
            "name": row["name"],
            "kategorie": row["kategorie"],
            "beschreibung": row["beschreibung"] or "",
            "startmonat": row["startmonat"],
            "endmonat": row["endmonat"],
            "start_detail": row["start_detail"],
            "end_detail": row["end_detail"],
        })

    return grouped


# ---------------------------------------------------------------------------
# Prompt-Aufbau
# ---------------------------------------------------------------------------

def _zeitraum_text(eintrag: dict, monat: int) -> str:
    """Beschreibt den Zeitraum eines Ereignisses relativ zum aktuellen Monat."""
    start = eintrag["startmonat"]
    end = eintrag["endmonat"]
    if start == end:
        return ""
    if start == monat:
        return " (beginnt diesen Monat)"
    if end == monat:
        return " (letzter Monat)"
    return f" (läuft noch bis {GERMAN_MONTHS[end]})"


def baue_prompt(monat: int, grouped: dict[str, list[dict]]) -> str:
    """Erstellt den Prompt aus den Datenbankdaten."""
    monatsname = GERMAN_MONTHS[monat]

    abschnitte = []
    for etyp in EREIGNIS_REIHENFOLGE:
        if etyp not in grouped:
            continue
        eintraege = grouped[etyp]
        zeilen = []
        for e in eintraege:
            zeitraum = _zeitraum_text(e, monat)
            zeile = f"- {e['name']} ({e['kategorie']}){zeitraum}"
            # Kurze Beschreibung anhängen, wenn vorhanden (erste 200 Zeichen)
            if e["beschreibung"]:
                kurztext = e["beschreibung"].strip().split("\n")[0][:200]
                zeile += f"\n  Info: {kurztext}"
            zeilen.append(zeile)
        abschnitte.append(f"### {etyp}\n" + "\n".join(zeilen))

    if not abschnitte:
        pflanzenliste = "Keine Einträge für diesen Monat."
    else:
        pflanzenliste = "\n\n".join(abschnitte)

    prompt = f"""Du bist ein freundlicher Gartenassistent. Schreibe einen persönlichen, 
warmherzigen monatlichen Gartenbrief auf Deutsch für den Monat {monatsname}.

Der Brief soll folgende Teile enthalten:

**Teil 1: Einleitung**
Einen kurzen einleitenden Satz über den Monat im Garten.

**Teil 2: Aufgaben und Ereignisse aus dem Garten**
Die Aufgaben und Ereignisse nach Themen gegliedert beschreiben (nutze die vorgegebene Struktur).
Praktische Hinweise aus den Pflanzenbeschreibungen einarbeiten, wo sinnvoll.

**Teil 3: Pflanz-Tipps für den Monat**
Am Ende zwei zusätzliche kurze Abschnitte mit allgemeinem Gartenwissen (nicht aus der Datenbank):
- Eine Überschrift "🥕 Gemüse & Obst zum Pflanzen im {monatsname}" mit einem kurzen Absatz, 
  welches Gemüse und Obst man in diesem Monat aussäen, vorziehen oder pflanzen kann.
- Eine Überschrift "🌸 Blumen & Stauden im {monatsname}" mit einem kurzen Absatz,
  welche Blumen und Stauden man jetzt pflanzen, teilen oder pflegen kann.

**Teil 4: Abschluss**
Einen motivierenden Abschlusssatz.

Formatierung:
- Nicht zu lang sein (ca. 400–600 Wörter)
- Direkt angesprochen (Du-Form)
- Als HTML formatiert (mit <h2>, <h3>, <ul>, <li>, <p> Tags)

Hier sind die Daten aus der Gartendatenbank für {monatsname}:

{pflanzenliste}

Schreibe jetzt den Gartenbrief als HTML. Beginne direkt mit dem HTML-Inhalt, ohne Präambel.
"""
    return prompt


# ---------------------------------------------------------------------------
# E-Mail-Versand
# ---------------------------------------------------------------------------

def baue_html_mail(monat: int, brief_html: str) -> str:
    """Bettet den generierten Brief in ein vollständiges HTML-Dokument ein."""
    monatsname = GERMAN_MONTHS[monat]
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{
    font-family: Georgia, 'Times New Roman', serif;
    max-width: 680px;
    margin: 0 auto;
    padding: 24px;
    color: #2d2d2d;
    background: #fafaf8;
    line-height: 1.7;
  }}
  h1 {{
    color: #4a7c59;
    border-bottom: 2px solid #c8e6c9;
    padding-bottom: 8px;
    font-size: 1.5em;
  }}
  h2 {{ color: #4a7c59; font-size: 1.2em; margin-top: 1.5em; }}
  h3 {{
    color: #6a9e7a;
    font-size: 1em;
    margin-top: 1.2em;
    margin-bottom: 0.3em;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  ul {{ padding-left: 1.4em; }}
  li {{ margin-bottom: 0.4em; }}
  p {{ margin: 0.8em 0; }}
  .footer {{
    margin-top: 2em;
    padding-top: 1em;
    border-top: 1px solid #ddd;
    font-size: 0.85em;
    color: #888;
  }}
</style>
</head>
<body>
<h1>🌿 Gartenbrief {monatsname}</h1>
{brief_html}
<div class="footer">
  Dieser Brief wurde automatisch von deinem Garten-Tracker erstellt.
</div>
</body>
</html>"""


def sende_mail(monat: int, html_inhalt: str) -> None:
    """Verschickt die HTML-Mail per Gmail SMTP.

    MAIL_TO kann kommasepariert mehrere Empfänger enthalten,
    z.B. "achim@example.com,kiki@example.com"
    """
    monatsname = GERMAN_MONTHS[monat]
    jahr = date.today().year

    empfaenger = [addr.strip() for addr in MAIL_TO.split(",") if addr.strip()]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🌿 Gartenbrief {monatsname} {jahr}"
    msg["From"] = MAIL_FROM
    msg["To"] = ", ".join(empfaenger)

    msg.attach(MIMEText(html_inhalt, "html", "utf-8"))

    with smtplib.SMTP(MAIL_SMTP_HOST, MAIL_SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(MAIL_FROM, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM, empfaenger, msg.as_string())


# ---------------------------------------------------------------------------
# Hauptprogramm
# ---------------------------------------------------------------------------

def main() -> None:
    # Provider erstellen und konfigurieren
    provider = get_provider()

    # Konfiguration prüfen
    fehlend = provider.validate_config()
    if not MAIL_FROM:
        fehlend.append("MAIL_FROM")
    if not MAIL_TO:
        fehlend.append("MAIL_TO")
    if not MAIL_PASSWORD:
        fehlend.append("MAIL_PASSWORD")
    if fehlend:
        print(f"Fehler: Folgende Umgebungsvariablen fehlen: {', '.join(fehlend)}")
        sys.exit(1)

    heute = date.today()
    monat = heute.month
    monatsname = GERMAN_MONTHS[monat]

    print(f"Erstelle Gartenbrief für {monatsname} {heute.year}...")
    print(f"  → LLM-Provider: {provider.name}")

    # 1. Daten aus DB holen
    print("  → Lese Pflanzendaten aus Datenbank...")
    grouped = get_ereignisse_fuer_monat(monat)
    gesamt = sum(len(v) for v in grouped.values())
    print(f"  → {gesamt} Ereignisse in {len(grouped)} Kategorien gefunden.")

    if not grouped:
        print("  → Keine Ereignisse für diesen Monat. Mail wird trotzdem verschickt.")

    # 2. Prompt bauen und LLM befragen
    print(f"  → Generiere Text mit {provider.name}...")
    prompt = baue_prompt(monat, grouped)
    brief_html = provider.generate(prompt)
    print("  → Text generiert.")

    # 3. HTML-Mail zusammenbauen
    html_mail = baue_html_mail(monat, brief_html)

    # 4. Mail verschicken
    print(f"  → Sende Mail an {MAIL_TO}...")
    sende_mail(monat, html_mail)
    print(f"  ✓ Gartenbrief für {monatsname} erfolgreich verschickt.")


if __name__ == "__main__":
    main()
