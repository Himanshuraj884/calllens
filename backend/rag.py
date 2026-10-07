import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Playbook:
    def __init__(self, path: Path):
        text = Path(path).read_text(encoding="utf-8")
        self.chunks = [c.strip() for c in re.split(r"\n(?=## )", text) if c.strip().startswith("##")]
        self.vec = TfidfVectorizer(stop_words="english")
        self.matrix = self.vec.fit_transform(self.chunks)

    def search(self, query: str, k: int = 2):
        sims = cosine_similarity(self.vec.transform([query]), self.matrix)[0]
        top = sims.argsort()[::-1][:k]
        return [{"text": self.chunks[i], "score": round(float(sims[i]), 3)} for i in top if sims[i] > 0]
