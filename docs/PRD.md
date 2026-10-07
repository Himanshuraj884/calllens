# PRD: CallLens (Sales Call Intelligence Pilot)

**Author:** Himanshu Raj | **Status:** Pilot | **Version:** 1.0

## 1. Problem
Sales reps spend time after every call writing notes, finding follow-ups and checking what to say about pricing, competitors and security. Notes are inconsistent, and action items get lost.
*Validate with interviews (see user-research-guide.md) and replace this paragraph with what you actually heard.*

## 2. Users
- **Primary:** Sales rep who runs 3 to 10 calls a week and writes follow-ups afterwards.
- **Secondary:** Sales manager who wants consistent call records.

## 3. Goals and non-goals
**Goals:** Cut post-call admin; surface action items and objections; answer playbook questions with sources.
**Non-goals (v1):** Live (real-time) transcription, CRM sync, speaker diarization, multi-language support, authentication.

## 4. User stories and acceptance criteria
| ID | Story | Acceptance criteria |
|----|-------|---------------------|
| US1 | As a rep, I upload a call recording so I get a transcript. | Accepts .wav/.mp3/.m4a up to 50 MB; transcript has timestamps; clear error for bad files. |
| US2 | As a rep, I see a summary of the call so I can recall it quickly. | Summary is at most 4 sentences and uses only facts from the transcript. |
| US3 | As a rep, I see action items so I do not miss follow-ups. | Items listed as separate lines; I can mark each correct or incorrect. |
| US4 | As a rep, I see objections raised so I can prepare my reply. | Objections listed with the customer's own wording. |
| US5 | As a rep, I ask a question and get an answer from the playbook. | Answer comes from retrieved playbook text; says so when nothing relevant exists. |
| US6 | As the PM, I can see pilot KPIs. | /api/metrics returns the KPIs in section 5. |

## 5. Success metrics (KPIs)
| KPI | How measured | Pilot target (set before the pilot, adjust after) |
|-----|--------------|--------|
| STT accuracy | Word error rate on 5 hand-corrected calls (eval/wer.py) | 15% or lower |
| Latency | Median upload-to-summary time (/api/metrics) | Under 60 s for a 5-minute call |
| Summary quality | Average user rating, 1 to 5 | 4.0 or higher |
| Action item precision | Share of action items users tick as correct | 80% or higher |
| Adoption | Pilot users who upload a second call (repeat use rate) | 50% or higher |
| Feature use | Share of calls where Ask was used | 30% or higher |

## 6. Scope and phasing
- **v1 (this pilot):** Upload, transcribe (Whisper), analyse, playbook Q&A, feedback, metrics.
- **v2 candidates (decide from pilot data):** Real-time transcription, CRM export, speaker labels, Hindi/English mixed calls.

## 7. Risks and open questions
- Whisper accuracy drops with noise, accents and code-mixed speech.
- LLM summaries can invent details. Mitigation: grounded prompt and user confirmation of action items.
- Call recordings are sensitive. Pilot uses role-played calls only, with consent.
- Open question: is the summary or the Q&A the feature users value more?

## 8. Pilot plan
See pilot-report-template.md. 8 to 10 participants, 5 to 10 role-played calls, 5 interviews, 2 weeks.
