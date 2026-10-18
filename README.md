# AI PR Review Agent

Multi-agent PR review: 4 LangGraph agents (security, quality, tests, docs) + RAG over the repo
and a knowledge base, FastAPI backend, Postgres+pgvector, React dashboard (later).

## Quick start
```bash
cp .env.example .env
docker compose up --build
curl localhost:8000/health        # {"status":"ok"}
curl localhost:8000/health/db     # {"pgvector":true,"missing_tables":[],"ok":true}
```
Run tests without Docker: `cd backend && pip install -r requirements.txt && pytest`

If you change `db/init.sql`: `docker compose down -v && docker compose up --build`

## Phase 1: try it
```bash
# Upgrading from Phase 0 without wiping data:
docker compose exec -T db psql -U prreview -d prreview < db/migrations/001_phase1.sql
# (or wipe and recreate: docker compose down -v && docker compose up --build)

curl -X POST localhost:8000/reviews -H "Content-Type: application/json" \
     -d '{"pr_url":"https://github.com/<owner>/<repo>/pull/<n>"}'      # -> {"id": "...", "status": "queued"}
curl localhost:8000/reviews/<id>          # status queued -> running -> ingested (or failed + error), file summary
curl localhost:8000/reviews/<id>/files    # hunks with line numbers + enclosing functions (with source)
```
Or use the interactive docs at http://localhost:8000/docs. Public PRs work without a token, but GitHub
allows only 60 unauthenticated requests/hour, so set `GITHUB_TOKEN` in `.env` (a fine-grained token with
read access to Contents and Pull requests; needed for private repos). Restart after editing `.env`.

### Webhook (optional)
1. Generate a secret: `python -c "import secrets;print(secrets.token_hex(32))"` and put it in `.env` as `GITHUB_WEBHOOK_SECRET`.
2. Expose localhost, e.g. `npx smee-client --url https://smee.io/<your-channel> --target http://localhost:8000/webhook/github`
   (or ngrok).
3. In the GitHub repo: Settings > Webhooks > Add: payload URL = your smee/ngrok URL (smee forwards to `/webhook/github`),
   content type `application/json`, the same secret, event = "Pull requests".
Signatures are verified (HMAC-SHA256), and repeated deliveries of the same `X-GitHub-Delivery` id are dropped.

## Tests
`docker compose exec backend pytest` (21 tests; the API tests use a fake GitHub and need the db container).

## Layout
- `backend/app/integrations/github_client.py` - PR URL parsing, diff and file fetch, readable errors
- `backend/app/diff/parser.py` - unified diff -> per-file hunks with exact line numbers
- `backend/app/diff/functions.py` - changed lines -> enclosing Python function (ast)
- `backend/app/services/ingest.py` - the background ingestion pipeline
- `backend/app/api/reviews.py`, `webhook.py` - REST endpoints
- `backend/app/schemas/finding.py` - the Finding contract every agent returns
- `backend/app/graph/state.py` - LangGraph state (graph built in Phase 5)
- `db/init.sql`, `db/migrations/` - schema
- `frontend/` (Phase 7), `eval/` (Phase 9)
