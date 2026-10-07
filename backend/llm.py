"""Summaries, action items, objections and grounded Q&A.
Uses the Anthropic API when ANTHROPIC_API_KEY is set; otherwise a rule-based fallback so the
pilot can still run. The mode is returned with every result so you can report it honestly."""
import json, os, re

MODEL = os.getenv("CALLLENS_MODEL", "claude-sonnet-5-5")
SYSTEM = ("You analyse sales call transcripts. Reply with ONLY JSON: "
          '{"summary": str (max 4 sentences), "action_items": [str], "objections": [str]}. '
          "Use only facts present in the transcript. Do not invent items.")

def _client():
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
        return anthropic.Anthropic()
    except ImportError:
        return None

REP_LABELS = {"rep", "sales", "seller", "agent", "sdr", "ae", "host", "me"}
SPLIT = re.compile(r"(?<=[.!?])\s+")

def _tagged_sentences(text):
    out = []
    for line in text.splitlines():
        line = re.sub(r"^\s*\[\d+:\d+(?::\d+)?\]\s*", "", line).strip()
        if not line:
            continue
        m = re.match(r"^([A-Za-z][\w .'-]{0,30}):\s+(.*)$", line)
        speaker, body = (m.group(1).strip().lower(), m.group(2)) if m else ("", line)
        for sent in SPLIT.split(body):
            if len(sent.strip()) > 15:
                out.append((speaker, sent.strip()))
    return out

def _fallback(transcript):
    tagged = _tagged_sentences(transcript)
    sents = [t for _, t in tagged]
    act = [t for _, t in tagged if re.search(r"(will send|i'll send|follow up|schedule|next step|by (monday|tuesday|wednesday|thursday|friday)|share the|please share|send (me|over))", t, re.I)]
    has_labels = any(sp for sp, _ in tagged)
    customer = [t for sp, t in tagged if (sp and sp not in REP_LABELS) or not has_labels]
    obj = [t for t in customer if re.search(r"(expensive|price|pricing|budget|competitor|not sure|concern|too much|already use|too costly|worried)", t, re.I)]
    return {"summary": " ".join(sents[:3]), "action_items": act[:6], "objections": obj[:6]}, "rule-based"

def _normalise(data):
    if not isinstance(data, dict):
        raise ValueError("model did not return an object")
    def strs(v):
        return [str(x) for x in v] if isinstance(v, list) else []
    return {"summary": str(data.get("summary", "")),
            "action_items": strs(data.get("action_items")),
            "objections": strs(data.get("objections"))}

def analyze(transcript: str):
    client = _client()
    if not client:
        return _fallback(transcript)
    try:
        msg = client.messages.create(model=MODEL, max_tokens=1000, system=SYSTEM,
                                     messages=[{"role": "user", "content": transcript[:60000]}])
        raw = re.sub(r"^```(?:json)?|```$", "", msg.content[0].text.strip(), flags=re.M).strip()
        return _normalise(json.loads(raw)), "llm"
    except Exception:
        return _fallback(transcript)

def answer(question: str, transcript: str, passages: list):
    ctx = "\n\n".join(p["text"] for p in passages) or "(no playbook match)"
    client = _client()
    if not client:
        return {"answer": passages[0]["text"] if passages else "No relevant playbook entry found.",
                "sources": passages, "mode": "rule-based"}
    prompt = (f"Playbook:\n{ctx}\n\nCall transcript:\n{transcript[:40000]}\n\nQuestion: {question}\n"
              "Answer using only the playbook and transcript. If the answer is not there, say so.")
    try:
        msg = client.messages.create(model=MODEL, max_tokens=500,
                                     messages=[{"role": "user", "content": prompt}])
        return {"answer": msg.content[0].text.strip(), "sources": passages, "mode": "llm"}
    except Exception:
        return {"answer": "The model call failed. Showing the closest playbook entry instead.",
                "sources": passages, "mode": "rule-based"}
