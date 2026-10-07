# CallLens: Sales Call Intelligence Pilot

Upload a sales call (audio or transcript) and get a transcript, summary, action items, objections, and answers from a product playbook. Built as a product pilot: it logs usage and feedback so you can measure STT accuracy, latency, summary quality and adoption.

**Stack:** Python, FastAPI, Whisper (faster-whisper), scikit-learn retrieval, Anthropic API (optional), SQLite, plain HTML/JS.

## Run it
```bash
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # optional; without it a rule-based fallback runs
uvicorn app:app --reload
```
Open http://localhost:8000 and upload `samples/demo_call.txt` to try it without audio.
`mode` is shown on every result (`llm` or `rule-based`), so always report which one produced your numbers.

## Product documents
- [PRD](docs/PRD.md): problem, users, user stories, acceptance criteria, KPIs, scope
- [User research guide](docs/user-research-guide.md): interview scripts and synthesis
- [Pilot report template](docs/pilot-report-template.md): where the real results go

## Measuring the KPIs
| KPI | Where it comes from |
|-----|---------------------|
| STT word error rate | Hand-correct 5 transcripts, put them in `eval/pairs/` as `name.ref.txt` and `name.hyp.txt`, run `python eval/wer.py --dir eval/pairs` |
| Latency, repeat use, ratings, action item precision, Ask usage | `GET /api/metrics` |

## Project layout
```
backend/   FastAPI app, Whisper transcription, retrieval, LLM layer, metrics, SQLite
frontend/  Single-page UI
eval/      WER script
docs/      PRD, research guide, pilot report template
samples/   Demo transcript
tests/     Unit tests (pip install -r requirements-dev.txt; pytest tests)
```

## Notes
- Everyone must enter a name; metrics are per name.
- Set `CALLLENS_ADMIN_TOKEN` to require an `X-Admin-Token` header on `/api/metrics`. There is no other authentication, so do not expose this publicly.
- Rule-based mode is a rough fallback (keyword matching, customer lines only for objections). Use an API key for real pilot numbers.

## License
MIT

## Status
Pilot code is complete. Pilot results are **not** included: run the pilot with real participants, then fill in the report with your measured numbers.
