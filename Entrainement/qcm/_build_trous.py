# -*- coding: utf-8 -*-
"""Détecte les points de cours peu couverts par la banque QCM et génère des QRU ciblés."""
from __future__ import annotations

import json
import re
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COURS = ROOT / "cours.json"
BANK = ROOT / "bank.json"
OUT_META = ROOT / "trous.json"
OUT_LOT = ROOT / "nouveau" / "lot_trous.json"

STOP = {
    "de", "la", "le", "les", "du", "des", "un", "une", "et", "ou", "en", "par", "sur",
    "dans", "est", "sont", "peut", "doit", "chez", "avec", "sans", "pour", "que", "qui",
    "ne", "pas", "plus", "moins", "si", "au", "aux", "the", "une", "cela", "cette", "ces",
    "son", "sa", "ses", "leur", "leurs", "être", "avoir", "comme", "entre", "après", "avant",
    "notamment", "également", "aussi", "tout", "tous", "toute", "toutes", "très", "souvent",
}

NUM_RE = re.compile(r"\d+(?:[,\.]\d+)?(?:\s*(?:%|mmhg|g/l|mg|min|h|j|ms|bpm|pg/ml|mm|cm))?", re.I)


def tokens(text: str) -> list[str]:
    t = text.lower().replace("’", "'")
    words = re.findall(r"[\w'≤≥<>%/\-]+", t)
    out = []
    for w in words:
        w = w.strip("'")
        if len(w) < 3 or w in STOP:
            continue
        out.append(w)
    for m in NUM_RE.finditer(text):
        out.append(m.group(0).lower().replace(" ", ""))
    return list(dict.fromkeys(out))


def q_blob(q: dict) -> str:
    parts = [q.get("prompt", "")]
    for o in q.get("options") or []:
        parts.append(o.get("text", ""))
    parts.append(q.get("explanation", ""))
    return " ".join(parts).lower()


def coverage(bullet: str, questions: list[dict]) -> float:
    bt = tokens(bullet)
    if not bt:
        return 1.0
    best = 0.0
    for q in questions:
        blob = q_blob(q)
        hit = sum(1 for t in bt if t in blob)
        score = hit / len(bt)
        # bonus if key numbers appear
        nums = [m.group(0).lower().replace(" ", "") for m in NUM_RE.finditer(bullet)]
        if nums and any(n in blob for n in nums):
            score = max(score, 0.55)
        best = max(best, score)
    return best


def shorten(s: str, n: int = 180) -> str:
    s = re.sub(r"\s+", " ", s.strip())
    if len(s) <= n:
        return s
    cut = s[: n - 1].rsplit(" ", 1)[0]
    return cut + "…"


def make_distractors(bullet: str, pool: list[str], n: int = 4) -> list[str]:
    cands = [shorten(x, 160) for x in pool if x.strip() != bullet.strip()]
    random.shuffle(cands)
    out = []
    for c in cands:
        if c == shorten(bullet, 160):
            continue
        if c not in out:
            out.append(c)
        if len(out) >= n:
            break
    while len(out) < n:
        out.append(f"Affirmation inexacte ou hors collège ({len(out) + 1}).")
    return out[:n]


def make_qru(item: str, label: str, bullet: str, rang: str, pool: list[str], idx: int) -> dict:
    correct = shorten(bullet, 200)
    wrongs = make_distractors(bullet, pool, 4)
    opts = [{"letter": "A", "text": correct, "why": "Point essentiel du cours CNEC."}]
    letters = ["B", "C", "D", "E"]
    for L, w in zip(letters, wrongs):
        opts.append({"letter": L, "text": w, "why": "Autre point du cours ou distracteur."})
    snippet = shorten(bullet, 95)
    return {
        "item": item,
        "kind": "QRU",
        "rang": rang,
        "theme": "trou",
        "format": "standard",
        "prompt": f"[Trou collège · {label}] Quelle proposition est exacte ? « {snippet} »",
        "options": opts,
        "correct": ["A"],
        "pcz": [],
        "scz": [],
        "explanation": bullet.strip(),
        "gapIndex": idx,
        "gapText": bullet.strip(),
    }


def main() -> None:
    random.seed(42)
    cours = json.loads(COURS.read_text(encoding="utf-8"))
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    by_item: dict[str, list[dict]] = {}
    for q in bank.get("questions") or []:
        by_item.setdefault(q["item"], []).append(q)

    gaps: list[dict] = []
    generated: list[dict] = []
    COVER_A = 0.38
    COVER_B = 0.32

    for entry in cours:
        item = entry["item"]
        label = entry.get("label") or item
        qs = by_item.get(item, [])
        pool = (entry.get("rangA") or []) + (entry.get("rangB") or [])

        for rang, arr in (("A", entry.get("rangA") or []), ("B", entry.get("rangB") or [])):
            thresh = COVER_A if rang == "A" else COVER_B
            for i, bullet in enumerate(arr):
                if len(bullet.strip()) < 25:
                    continue
                cov = coverage(bullet, qs)
                if cov >= thresh:
                    continue
                gap = {
                    "item": item,
                    "label": label,
                    "rang": rang,
                    "index": i,
                    "coverage": round(cov, 2),
                    "text": bullet.strip(),
                }
                gaps.append(gap)
                generated.append(make_qru(item, label, bullet, rang, pool, i))

    gaps.sort(key=lambda g: (g["coverage"], g["item"]))
    by_item_gaps: dict[str, list] = {}
    for g in gaps:
        by_item_gaps.setdefault(g["item"], []).append(g)

    meta = {
        "source": "cours.json vs bank.json",
        "thresholdA": COVER_A,
        "thresholdB": COVER_B,
        "totalGaps": len(gaps),
        "totalQuestions": len(generated),
        "byItem": {
            item: {
                "label": next((c["label"] for c in cours if c["item"] == item), item),
                "n": len(arr),
                "gaps": arr[:20],
            }
            for item, arr in sorted(by_item_gaps.items())
        },
    }

    OUT_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_LOT.write_text(
        json.dumps({"questions": generated}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Gaps: {len(gaps)} · QRU générés: {len(generated)}")
    print(f"-> {OUT_META.name} + {OUT_LOT.name}")
    print("Relance _build_bank.py pour fusionner dans bank.json")


if __name__ == "__main__":
    main()
