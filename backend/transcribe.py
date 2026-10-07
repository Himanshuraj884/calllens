import os
_model = None

def transcribe_audio(path: str) -> str:
    global _model
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise RuntimeError("faster-whisper is not installed. Run: pip install faster-whisper, "
                           "or upload a .txt transcript instead.") from e
    if _model is None:
        _model = WhisperModel(os.getenv("WHISPER_MODEL", "base"), compute_type="int8")
    segments, _ = _model.transcribe(path, vad_filter=True)
    lines = []
    for s in segments:
        m, sec = divmod(int(s.start), 60)
        lines.append(f"[{m:02d}:{sec:02d}] {s.text.strip()}")
    return "\n".join(lines)
