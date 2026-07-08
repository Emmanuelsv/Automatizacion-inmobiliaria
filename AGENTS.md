# Jhaen Inmobiliarios — AGENTS.md

## Stack

- **Python 3.12** FastAPI (port **5000**, not 8000) — no AI, pure regex (`re`)
- **Docker Compose** — 3 services: `jhaen-parser` (FastAPI), `n8n`, Evolution API
- **External API**: Wasi (`https://api.wasi.co/v1`) — credentials in `.env`
- **Backend**: SQLite for dedup (7-day TTL), httpx async for Wasi calls

## Quick Start

```bash
cp .env.example .env   # then fill credentials
docker compose up -d --build
```

## Key Commands

| Action | Command |
|--------|---------|
| Run tests | `python3 -m pytest tests/ -v` |
| Single test file | `python3 -m pytest tests/test_parser.py -v` |
| Run dev server | `uvicorn app.main:app --reload` (or `python app/main.py`) |
| Start stack | `docker compose up -d --build` |

Test fixtures in `tests/fixtures/sample_messages.py` — parametrized via `pytest.mark.parametrize`.

## Architecture

```
WhatsApp → Evolution API → n8n → FastAPI (/process) → Wasi API
                                        ↓
                               app/parser.py (parse_message)
                               app/wasi_client.py (search_all_locations)
                               app/matcher.py (match_properties)
                               app/message_builder.py (build_response_message)
```

## Domain Rules (hard-earned, do not break)

- **City is a HARD filter** — `matcher.py:219` `continue` with no exceptions. Properties from other municipalities are dropped entirely.
- **Authorized Wasi sellers** hardcoded in `main.py:177` — user IDs `{219100, 219281}`. All other sellers are filtered out.
- **Price margin** configurable via `.env`: `PRICE_MARGIN_BELOW=100000000`, `PRICE_MARGIN_ABOVE=30000000`. For budgets > 1B, margin becomes 7% proportional.
- **Colombian price formats**: dots (`700.000.000`), apostrophes (`850'000.000`), "millones/800M/no sea mas 650", bare numbers (3-6 digits assumed millions). See `app/price_parser.py`.
- **Location matching** spans two files: `app/locations.py` (BARRIOS dictionary + POIs) and `app/matcher.py` (ZONE_ALIASES for zone expansion). Adding a barrio may require changes in both + `wasi_client.py` (ZONE_ID_MAP).
- **Scoring (current code)**: 6 layers (price 0-30, location 0-30, type 0-20, rooms 0-20, area 0-15, admin 0-10) + features 5pts each + base 5. The `wasi-domain` skill describes a **strict boolean filtering** paradigm that may not match the current code — verify the actual implementation, not the skill.
- **Duplicate detection**: SQLite at `/data/dedup.db`, keyed by `sha256(sender||normalized_text)`, 7-day TTL.

## Code Conventions

- Always use `_get_number(prop, [...keys])` for numeric Wasi fields — never `prop["key"]` directly.
- Always use `_word_match(pattern, text)` for keyword detection — ensures whole-word match, not substring.
- Use `normalize_text()` for comparison — removes diacritics, preserves `ñ`, strips emojis.
- N8n webhook URL inside Docker: `http://mye-parser:5000` (service name, not localhost).
- Docker container names: `jhaen_parser`, `jhaen_n8n`.

## Skills (loaded via OpenCode)

- `wasi-domain` — business rules, scoring, location logic. Load when editing matcher/wasi_client/locations.
- `data-patterns` — Colombian price formats, location aliases, WhatsApp message parsing patterns.

### Skill locations

| Skill | Path |
|-------|------|
| `wasi-domain` | `.claude/skills/wasi-domain/wasi-domain-SKILL.md` |
| `data-patterns` | `.claude/skills/wasi-domain/data-patterns/SKILL.md` |
| Wasi fields reference | `.claude/skills/wasi-domain/references/wasi-fields.md` |
