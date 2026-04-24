# klockslag.se — Projektspec

## Koncept
En webbapp som omvandlar klockslag till nördiga fakta. Klockan blir en siffra — och siffran tolkas genom olika kategorier. 11:18 som årtal → Tempelriddarorden grundas. 11:18 som frekvens → 1118 Hz, nästan ett högt D. 11:18 som avstånd → 1118 km från Stockholm = Berlin.

Initialt lanseras med **Årtal** som enda aktiv kategori. Övriga kategorier syns i UI:t men är utgråade med "Kommer snart".

Användaren väljer kategori, väljer tema, får nördiga klockslag med kontext, och kan kopiera en färdig möteskallelse.

## Målgrupp
Nördar som vill imponera på andra nördar. All UI-text och genererat innehåll på svenska.

## Kategorier

Varje kategori tolkar klockslaget (HH:MM → siffran HHMM) genom en egen lins.

### Aktiv vid lansering
- **Årtal** — 1118 → historisk händelse

### Utgråade (planerade, ej implementerade)
- **Frekvens (Hz)** — 1118 Hz → närmaste ton, vad som låter så
- **Avstånd (km)** — 1118 km från Stockholm → vilken stad/plats
- **Temperatur (°C)** — 1118°C → vad som smälter/kokar vid den temperaturen
- **Hastighet (km/h)** — 1118 km/h → vad som rör sig så fort
- **Kalorier (kcal)** — 1118 kcal → vilken måltid/aktivitet det motsvarar
- **Matematik** — 1118 → primtalsfaktorisering, närmaste primtal, specialegenskaper
- **Grundämnen** — mapping via atomnummer/atomvikt/andra kemiska konstanter

Alla kategorier följer samma datamodell och UI-mönster — bara tolkningslagret skiljer sig.

## Funktioner

### 1. Kategorival
- Horisontell rad med kategori-chips överst
- "Årtal" aktiv, övriga utgråade med lås-ikon eller "Snart"-badge
- Klick på utgråad → kort tooltip/toast: "Kommer snart!"

### 2. Tickande klocka ("Just nu")
- Analog klocka med sekundvisare som tickar i realtid
- Digital tid bredvid/under
- Visar tolkning i aktiv kategori: "≈ År 1118" (eller framtida: "≈ 1118 Hz")
- Fakta hämtas från pre-genererad JSON
- Uppdateras automatiskt varje minut

### 3. Möteskallelse
- Användaren väljer tema inom aktiv kategori
- Fördefinierade teman som chips (teman varierar per kategori)
- Fritextfält för egna teman
- Får 3-4 förslag med:
  - Klockslag (valfritt spann, default 11:00–13:30 för lunch)
  - Tolkning av siffran i vald kategori
  - Kort beskrivning / fun fact
  - Färdig inbjudningstext redo att kopiera
- Varje förslag har en liten analog klocka
- Klicka → expandera → kopiera-knapp

## Datamodell

### Generell struktur per kategori

Varje kategori har en `events.json` och en `themes.json`:

```
data/
├── historical/          # Kategori: Årtal
│   ├── events.json
│   └── themes.json
├── frequency/           # Kategori: Frekvens (framtida)
│   ├── events.json
│   └── themes.json
└── ...
```

### events.json (per kategori)
Nyckel = "HH:MM", 1440 poster.
```json
{
  "11:18": {
    "value": "1118",
    "label": "år 1118",
    "title": "Tempelriddarorden grundas",
    "description": "2-3 meningar...",
    "fun_fact": "Överraskande detalj..."
  }
}
```

### themes.json (per kategori)
Nyckel = temanamn.
```json
{
  "Lingvistik": [
    {
      "time": "11:14",
      "value": "1114",
      "label": "år 1114",
      "title": "Gerard av Cremona föds",
      "description": "2-3 meningar...",
      "invite_text": "Lunch 11:14? Samma år som medeltidens störste översättare föddes."
    }
  ]
}
```

### categories.json (metadata)
```json
[
  {
    "id": "historical",
    "name": "Årtal",
    "unit": "",
    "description": "Klockslaget som historiskt årtal",
    "enabled": true,
    "themes": ["Vetenskap", "Lingvistik", "Matematik", "Krig & Politik", "Musik", "Konst", "Filosofi", "Teknik", "Sverige", "Sjöfart", "Astronomi", "Medicin", "Litteratur", "Arkitektur"]
  },
  {
    "id": "frequency",
    "name": "Frekvens",
    "unit": "Hz",
    "description": "Klockslaget som ljudfrekvens",
    "enabled": false,
    "themes": []
  }
]
```

## Datagenerering
- `generate.py` genererar all data via LLM
- Flagga `--category historical` för att generera specifik kategori
- Stödjer OpenAI-kompatibla endpoints (Ollama, llama.cpp, vLLM) och Anthropic API
- `--resume` för att fortsätta om det avbryts
- `--only events` / `--only themes` för att generera separat
- Sparar inkrementellt var 10:e post

## Server
- Python/FastAPI
- API-endpoints:
  - `GET /api/categories` — lista alla kategorier med enabled-status
  - `GET /api/{category}/event/{HH:MM}` — enskild händelse
  - `GET /api/{category}/events` — alla händelser i en kategori
  - `GET /api/{category}/themes` — alla teman i en kategori
  - `GET /api/{category}/theme/{namn}` — specifikt tema
  - `GET /api/status` — hälsokontroll
- Valfritt: `--llm-url` / `--llm-model` för live-generering av egna teman
- SPA-fallback: alla icke-API-routes → index.html

## Frontend
- Standalone HTML + CSS + vanilla JS (ingen byggsteg)
- Responsiv — funkar på mobil
- Design: mörk bakgrund (#1a1209), guld-accenter (#8b6914), parchment-kortkänsla
- Typsnitt: Cormorant Garamond (rubriker), EB Garamond (brödtext) via Google Fonts
- Analog klocka som SVG
- Tre lager: Kategorival → Flik (Just nu / Möteskallelse) → Innehåll

## Deploy
- VPS med nginx som reverse proxy
- Domän: klockslag.se
- Email: hej@klockslag.se
- HTTPS via Let's Encrypt/certbot

## Tech stack
- Python 3.10+
- FastAPI + uvicorn
- openai (Python-paket, för datagenerering)
- Inga frontend-dependencies (vanilla JS)

## Filstruktur
```
klockslag/
├── generate.py
├── server.py
├── requirements.txt
├── README.md
├── data/
│   ├── categories.json
│   └── historical/
│       ├── events.json
│       └── themes.json
└── static/
    └── index.html
```

## Prioritet för demo (idag)
1. Servern + frontend med kategoriväljare (bara Årtal aktiv)
2. `generate.py --only themes --category historical` (snabbt, ~1 min)
3. Tickande klocka + lunchkallelse med kopiera-funktion
4. De 1440 minuterna genereras i bakgrunden efteråt
