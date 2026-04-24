#!/usr/bin/env python3
"""
Generate klockslag.se data via LLM.

Examples:
    python generate.py --category historical --only themes
    python generate.py --category historical --only events --resume
    python generate.py --category historical --llm-provider anthropic --llm-model claude-sonnet-4-6
    python generate.py --category historical --llm-url http://localhost:11434/v1 --llm-model llama3.1
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

DATA_DIR = Path("data")


def make_client(provider: str, base_url: str, api_key: str | None):
    if provider == "anthropic":
        import anthropic
        return anthropic.Anthropic(api_key=api_key)
    else:
        from openai import OpenAI
        return OpenAI(base_url=base_url, api_key=api_key or "local")


def call_llm(client, provider: str, model: str, prompt: str, max_tokens: int = 500) -> str:
    if provider == "anthropic":
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    else:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content


def extract_json(text: str):
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        return json.loads(m.group(1).strip())
    raise ValueError(f"Could not parse JSON from: {text[:300]}")


def generate_event(client, provider: str, model: str, value: str) -> dict:
    prompt = f"""Generera fakta om år {value} på svenska.
Returnera ett JSON-objekt med exakt dessa fält:
- "value": "{value}"
- "label": "år {value}"
- "title": kort titel på händelsen (max 8 ord)
- "description": 2-3 meningar om händelsen
- "fun_fact": en överraskande detalj om händelsen eller epoken

Välj den mest intressanta händelsen globalt från år {value}.
Returnera BARA JSON, ingen markdown, inga förklaringar."""
    text = call_llm(client, provider, model, prompt, max_tokens=400)
    return extract_json(text)


def generate_events(client, provider: str, model: str, out: Path, resume: bool):
    existing: dict = {}
    if resume and out.exists():
        existing = json.loads(out.read_text(encoding="utf-8"))

    results = dict(existing)
    new_count = 0

    for h in range(24):
        for m in range(60):
            time_str = f"{h:02d}:{m:02d}"
            value = f"{h:02d}{m:02d}"
            if time_str in results:
                continue

            try:
                entry = generate_event(client, provider, model, value)
                results[time_str] = entry
                new_count += 1
                print(f"  {time_str}: {entry.get('title', '?')}")
            except Exception as e:
                print(f"  {time_str}: ERROR — {e}", file=sys.stderr)

            if new_count % 10 == 0 and new_count > 0:
                out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  [saved {new_count} new]")

            time.sleep(0.1)

    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Events done. {len(results)} total ({new_count} new).")


def generate_theme(client, provider: str, model: str, theme: str) -> list:
    prompt = f"""Generera 4 förslag på mötestider för temat "{theme}" på svenska.
Varje förslag ska ha en tid mellan 11:00 och 13:30 som är historiskt intressant.
Returnera ett JSON-array med 4 objekt, varje objekt har:
- "time": "HH:MM" (tid mellan 11:00 och 13:30)
- "value": "HHMM"
- "label": "år HHMM" (t.ex. "år 1118")
- "title": titel på historisk händelse (max 8 ord)
- "description": 2-3 meningar om händelsen
- "invite_text": färdig möteskallelse på vardaglig svenska (1-2 meningar, t.ex. "Lunch 11:18? Samma år som...")

Temat "{theme}" ska speglas i valet av historiska händelser.
Returnera BARA JSON-array, ingen markdown."""
    text = call_llm(client, provider, model, prompt, max_tokens=800)
    return extract_json(text)


def generate_themes(client, provider: str, model: str, theme_list: list, out: Path, resume: bool):
    existing: dict = {}
    if resume and out.exists():
        existing = json.loads(out.read_text(encoding="utf-8"))

    results = dict(existing)

    for theme in theme_list:
        if theme in results:
            print(f"  {theme}: skip")
            continue
        try:
            entries = generate_theme(client, provider, model, theme)
            results[theme] = entries
            print(f"  {theme}: {len(entries)} entries")
        except Exception as e:
            print(f"  {theme}: ERROR — {e}", file=sys.stderr)

        out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(0.2)

    print(f"Themes done. {len(results)} themes.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--category", required=True)
    p.add_argument("--only", choices=["events", "themes"])
    p.add_argument("--resume", action="store_true")
    p.add_argument("--llm-provider", default="openai", choices=["openai", "anthropic"])
    p.add_argument("--llm-url", default="http://localhost:11434/v1")
    p.add_argument("--llm-model", default="llama3.1")
    p.add_argument("--api-key", default=None)
    args = p.parse_args()

    cats_file = DATA_DIR / "categories.json"
    if not cats_file.exists():
        print("ERROR: data/categories.json not found.", file=sys.stderr)
        sys.exit(1)

    cats = json.loads(cats_file.read_text(encoding="utf-8"))
    cat = next((c for c in cats if c["id"] == args.category), None)
    if cat is None:
        print(f"ERROR: Category '{args.category}' not in categories.json", file=sys.stderr)
        sys.exit(1)

    cat_dir = DATA_DIR / args.category
    cat_dir.mkdir(parents=True, exist_ok=True)

    client = make_client(args.llm_provider, args.llm_url, args.api_key)

    if args.only != "themes":
        print(f"Generating events for '{args.category}'...")
        generate_events(client, args.llm_provider, args.llm_model,
                        cat_dir / "events.json", args.resume)

    if args.only != "events":
        print(f"Generating themes for '{args.category}'...")
        generate_themes(client, args.llm_provider, args.llm_model,
                        cat["themes"], cat_dir / "themes.json", args.resume)


if __name__ == "__main__":
    main()
