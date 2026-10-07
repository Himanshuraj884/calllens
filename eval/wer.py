"""Word error rate (WER) for the STT accuracy KPI.

Usage:
  python eval/wer.py reference.txt hypothesis.txt            # one pair
  python eval/wer.py --dir eval/pairs                        # folder of x.ref.txt + x.hyp.txt pairs
Strip timestamps like [00:12] automatically. Hand-correct the reference transcripts yourself."""
import re, sys
from pathlib import Path

def normalize(text: str):
    text = re.sub(r"\[\d+:\d+\]", " ", text.lower())
    return re.sub(r"[^a-z0-9' ]+", " ", text).split()

def wer(ref: str, hyp: str) -> float:
    r, h = normalize(ref), normalize(hyp)
    if not r:
        raise ValueError("Reference transcript is empty.")
    prev = list(range(len(h) + 1))
    for i, rw in enumerate(r, 1):
        cur = [i]
        for j, hw in enumerate(h, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (rw != hw)))
        prev = cur
    return prev[-1] / len(r)

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] != "--dir":
        print(f"WER: {wer(Path(sys.argv[1]).read_text(), Path(sys.argv[2]).read_text()):.1%}")
    elif len(sys.argv) == 3:
        scores = []
        for ref in sorted(Path(sys.argv[2]).glob("*.ref.txt")):
            hyp = ref.with_name(ref.name.replace(".ref.", ".hyp."))
            s = wer(ref.read_text(), hyp.read_text()); scores.append(s)
            print(f"{ref.name.split('.')[0]}: {s:.1%}")
        if scores:
            print(f"Average WER over {len(scores)} calls: {sum(scores)/len(scores):.1%}")
    else:
        print(__doc__)
