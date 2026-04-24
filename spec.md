# klockslag.se — Projektspec

## Koncept
En webbapp som omvandlar klockslag till nördiga fakta. Klockan blir en siffra och siffran tolkas genom olika kategorier. 11:18 som årtal → Tempelriddarorden grundas. 11:18 som frekvens → 1118 Hz, nästan ett högt D. 11:18 som avstånd → 1118 km från Stockholm = Berlin.

Användaren väljer kategori, tolkar sitt klockslag eller får förslag, och kan kopiera en färdig möteskallelse.

## Målgrupp
Nördar som vill imponera på andra nördar. All UI-text och genererat innehåll på svenska.

## Kategorier

Varje kategori tolkar klockslaget (HH:MM → siffran HHMM) genom en egen lins. Alla fem är aktiva.

- **Årtal** (`historical`) – 1118 → historisk händelse
- **Frekvens/Toner** (`frequency`, Hz) – 1118 Hz → närmaste ton, vad som låter så
- **Avstånd** (`distance`, km) – 1118 km från Stockholm → vilken stad/plats
- **Temperatur** (`temperature`, °C) – 1118 °C → vad som smälter/kokar
- **Hastighet** (`speed`, km/h) – 1118 km/h → vad som rör sig så fort

Alla kategorier följer samma datamodell och UI-mönster, bara tolkningslagret skiljer sig.

## Funktioner

### 1. Kategorival
- Horisontell rad med kategori-chips överst
- Alla fem aktiva

### 2. Mötestid in, nördig tid ut
- Användaren skriver in en planerad mötestid (timme + minut)
- Default-värde vid sidladdning: aktuell tid
- Om aktuell tid ligger utanför 07:00–19:55 används 07:00 som default (meningen är att nästa arbetsdag planeras)
- Ingen lunch-default eller annan förinställd tidszon
- Ingen live-tickande klocka, värdet är statiskt tills användaren ändrar
- Resultatet är en enskild närmaste post i vald kategori:
  - Klockslag (från datan)
  - Tolkning av siffran (label)
  - Titel + beskrivning
  - Fun fact
  - Färdig inbjudningstext redo att kopiera
- Nearest-logik: linjär minsta absolutdifferens i minuter mot postens klockslag, ingen wrap över dygnsgränsen

## Datamodell

### Filstruktur
```
data/
├── categories.json
├── historical/events.json
├── frequency/events.json
├── distance/events.json
├── temperature/events.json
└── speed/events.json
```

### categories.json
Array med metadata per kategori: `id`, `name`, `unit`, `description`, `enabled`.

### events.json (per kategori)
Nyckel = "HH:MM". Sparse, bara kuraterade tider (idag 30–63 poster per kategori), inte alla 1440 minuter.

```json
{
  "11:18": {
    "label": "år 1118",
    "title": "Tempelriddarorden grundas",
    "description": "2-3 meningar...",
    "fun_fact": "Överraskande detalj...",
    "invite_text": "Möte 11:18? Samma år som..."
  }
}
```

Dataposter skrivs för hand som JSON, ingen generator.

## Frontend
- Standalone `index.html` med CSS + vanilla JS, ingen byggsteg
- Responsiv, funkar på mobil
- Design: mörk bakgrund (#1a1209), guld-accenter (#8b6914), parchment-kortkänsla
- Typsnitt: Cormorant Garamond (rubriker), EB Garamond (brödtext) via Google Fonts
- Analog klocka som SVG
- Data laddas via fetch mot `data/categories.json` och `data/{id}/events.json`

## Deploy
- Docker-container med nginx som serverar statiska filer, se `Dockerfile`
- Nginx reverse proxy framför på VPS
- Domän: klockslag.se
- Email: hej@klockslag.se
- HTTPS via Let's Encrypt/certbot

## Tech stack
- HTML + CSS + vanilla JS, inga frontend-dependencies
- nginx (via Docker) som statisk server
- Ingen backend, inga API-endpoints

## Filer i repo
```
klockslag.se/
├── index.html
├── og-image.png
├── Dockerfile
├── spec.md
├── spec-delta.md
└── data/
    ├── categories.json
    └── {historical,frequency,distance,temperature,speed}/events.json
```
