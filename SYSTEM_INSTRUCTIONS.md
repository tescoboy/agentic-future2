# System Instructions – Always Evaluate Before Making Changes

## 1. Data Integrity
- Do not fabricate data, IDs, platforms, fields, or endpoints.
- Use only real sources: adapters, database.py, sample_data.json.
- In demo mode or without credentials, use only seeded/sample data.
- On failure or unexpected shapes, return explicit errors — never silent fallbacks.

## 2. API Contracts & Logic
- Preserve AI ranking/scoring exactly; no changes unless instructed.
- Leave scores blank if not computable; never synthesize.
- Add UI pass-through fields without altering backend order.
- Provide thin REST shims wrapping A2A logic:
  - POST /discovery
  - GET /activation/options
  - POST /activation
  - GET /status
  - GET /health
- Do not delete/break A2A or MCP routes. No duplication of business logic.

## 3. Architecture & Code Quality
- Single backend codebase; no duplicate dirs/files.
- Layering: API → Services → Repos → Adapters → Core → Models.
- Keep files small/focused; add docstrings.
- Centralise config; validate env on startup.
- Enforce Python venv and Node v20.19.4 (.nvmrc).
- CORS in dev: allow 127.0.0.1:5173 and localhost:5173.
- Frontend VITE_API_BASE must include scheme; block if missing.

## 4. UX & Frontend Behaviour
- Discover tab: show Matches & Proposals with all fields; badge Actual vs Proposed.
- Inline activate per segment; only show allowed platforms.
- Status tab fetches by activation ID.
- Health banner visible; errors via Bootstrap alerts.
- Always show fallback indicators, method (AI vs fallback), and meaning.
- Prominent styling for fallback states.

## 5. Pitfalls to Avoid
- No hardcoded platform lists.
- Respect max_results throughout.
- No invented status flows — use real or 501.
- Avoid directory confusion; provide start/stop/status scripts.

## 6. Observability & Errors
- Structured logs per request: request_id, route, duration_ms, outcome.
- Errors return JSON { detail: "..." }.
- Frontend logs timings in dev; shows safe errors.
- Log all fallback activations with context.

## 7. AI Integration & Fallbacks
- Implement robust, tested fallbacks for AI failures.
- Handle markdown-formatted JSON.
- Validate AI responses before use; use simple prompts.
- Gracefully degrade; never crash.
- Prominently alert UI on fallback; log activations with context.

## 8. Development Workflow
- Test imports/syntax before running.
- Keep functions small, modular, single-purpose.
- Test DB queries with realistic volumes.
- Sync types between FE/BE.
- Use proper loading states, error boundaries, and realistic test data.

## 9. Frontend Implementation Rules
- Bootstrap only for styling; no inline CSS.
- Custom styles in custom-bootstrap.css only.
- Use Bootstrap grid/utilities, not manual positioning.
- Separate concerns: fetching ≠ rendering; separate handlers.
- File structure: /components, /services, /utils, /styles.
- Use addEventListener() for events.
- Log API calls/errors to console.
- Support portrait mode on mobile.
- Lazy-load images, debounce heavy calls, no duplicate code.

## 10. Final Assistant Behaviour
- Enforce all above rules in generated code.
- Auto-correct violations before output.
- Include console logging for debugging.
- Keep HTML clean/semantic; JS modular/reusable.
- Test imports, syntax, and error handling before final output.
