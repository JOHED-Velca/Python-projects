import hashlib
from typing import List


# Step 1: lightweight, deterministic mock embedding
# (swap with real model later)


def embed(text: str, dim: int = 128) -> List[float]:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    # repeat hash to fill dimension
    buf = (h * ((dim // len(h)) + 1))[:dim]
    return [b / 255.0 for b in buf]


def cosine(a: List[float], b: List[float]) -> float:
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return (dot / (na * nb)) if na and nb else 0.0