import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent.parent / "eval"))
from wer import wer
import llm
from rag import Playbook

def test_wer_identical_is_zero():
    assert wer("hello world", "Hello, world!") == 0

def test_wer_one_substitution():
    assert abs(wer("a b c d", "a b x d") - 0.25) < 1e-9

def test_wer_ignores_timestamps():
    assert wer("[00:01] hi there", "hi there") == 0

def test_fallback_extracts_items():
    text = Path(__file__).parent.parent.joinpath("samples/demo_call.txt").read_text()
    result, mode = llm.analyze(text)
    assert mode in {"rule-based", "llm"}
    assert result["action_items"] and result["objections"]

def test_playbook_retrieval():
    pb = Playbook(Path(__file__).parent.parent / "backend" / "playbook.md")
    hits = pb.search("is it SOC 2 certified and secure")
    assert hits and "SOC 2" in hits[0]["text"]

def test_objections_are_customer_only():
    text = Path(__file__).parent.parent.joinpath("samples/demo_call.txt").read_text()
    result, _ = llm._fallback(text)
    assert result["objections"]
    assert not any(o.startswith("Rep:") or "SOC 2 Type II certified" in o for o in result["objections"])
    assert not any(o.startswith("Priya:") for o in result["objections"])

def test_normalise_bad_shapes():
    assert llm._normalise({"summary": 5, "action_items": "x"}) == {"summary": "5", "action_items": [], "objections": []}

def test_metrics_ignore_unreviewed(tmp_path):
    import store, metrics
    store.DB_PATH = tmp_path / "t.db"; store.init()
    store.save_call({"id": "a", "user_id": "u", "filename": "f", "transcript": "t", "result": {}, "mode": "m", "stt_seconds": 0, "total_seconds": 1})
    store.save_feedback("a", 4, [True, None, False, None], "")
    assert metrics.compute()["action_item_precision"] == 0.5
