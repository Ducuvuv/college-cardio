# -*- coding: utf-8 -*-
"""Build sigles.json from extracted college abbreviation pages."""
from __future__ import annotations

import json
import re
from pathlib import Path

RAW = Path(r"C:\Users\gestu\Documents\college cardio\_tmp_abbrev.txt")
OUT = Path(__file__).with_name("sigles.json")

SKIP = re.compile(
    r"^(Abréviations|Ce livre|Pour avoir|XXXX*|I XXV|XXII|F\s*$|XXX)$",
    re.I,
)


def clean_pages(text: str) -> list[list[str]]:
    pages, cur = [], []
    for line in text.splitlines():
        if line.startswith("===== PAGE"):
            if cur:
                pages.append(cur)
            cur = []
            continue
        t = line.strip()
        if not t or SKIP.match(t):
            continue
        if "amis-med" in t.lower() or "Faille" in t:
            continue
        cur.append(t)
    if cur:
        pages.append(cur)
    return pages


def is_abbrev(s: str) -> bool:
    compact = s.replace(" ", "")
    if len(compact) > 18:
        return False
    letters = re.sub(r"[^A-Za-z0-9+\-]", "", compact)
    if not letters:
        return False
    up = sum(1 for c in letters if c.isupper() or c.isdigit())
    return up / len(letters) >= 0.55 and len(letters) <= 16


FIX = {
    "El": "EI",
    "H BAG": "HBAG",
    "TlH": "TIH",
    "STEMl": "STEMI",
    "SpO 2": "SpO2",
    "vo 2": "VO2",
    "Cydo-oxygénase": "Cyclo-oxygénase",
    "Échographie transoesophagienne": "Échographie transœsophagienne",
    "Metabolic équivalant task": "Metabolic equivalent task",
    "Myocardial infraction with non-obstructive coronary arteries": "Myocardial infarction with non-obstructive coronary arteries",
    "Prostate spécifie antigen": "Prostate specific antigen",
    "mmse": "MMSE",
    "mini mental State examination": "Mini-Mental State Examination",
    "SCANST": "SCA NST",
    "ig": "Ig",
}


def norm(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return FIX.get(s, s)


def zip_defs_abbrs(defs: list[str], abbrs: list[str]) -> list[tuple[str, str]]:
    n = min(len(defs), len(abbrs))
    return list(zip(abbrs[:n], defs[:n]))


def main() -> None:
    pages = clean_pages(RAW.read_text(encoding="utf-8"))
    pairs: list[tuple[str, str]] = []

    # p25: defs then abbrevs; BASIC has a 2-line definition
    p = pages[0]
    idx = p.index("AAA")
    defs, abbrs = p[:idx], p[idx:]
    merged = []
    i = 0
    while i < len(defs):
        if defs[i].startswith("Bêtabloquant, antiagrégants") and i + 1 < len(defs):
            merged.append(defs[i] + " " + defs[i + 1])
            i += 2
        else:
            merged.append(defs[i])
            i += 1
    pairs.extend(zip_defs_abbrs(merged, abbrs))

    # p26 interleaved
    p = pages[1]
    i = 0
    while i < len(p):
        if is_abbrev(p[i]) and i + 1 < len(p) and not is_abbrev(p[i + 1]):
            d, j = p[i + 1], i + 2
            if p[i] == "CHARGE" and j < len(p) and not is_abbrev(p[j]):
                d = d + " " + p[j]
                j += 1
            pairs.append((p[i], d))
            i = j
        else:
            i += 1

    # p27 defs then abbrs; HACEK 2-line
    p = pages[2]
    idx = next(i for i, x in enumerate(p) if x.startswith("Fl"))
    defs, abbrs = p[:idx], [a for a in p[idx:] if a != "I XXV"]
    merged = []
    i = 0
    while i < len(defs):
        if defs[i].startswith("Haemophilus") and i + 1 < len(defs):
            merged.append(defs[i] + " " + defs[i + 1])
            i += 2
        else:
            merged.append(defs[i])
            i += 1
    pairs.extend(zip_defs_abbrs(merged, abbrs))

    # p28: first block abbrevs then defs (LSD..MINOCA), then remaining abbrevs then defs
    p = pages[3]
    cut = p.index("Lysergic acid diethylamide")
    abbrs1, rest = p[:cut], p[cut:]
    # first 10 abbrevs pair with first 10 defs, but MINOCA def is last of those
    # lines: 10 abbrevs, then 10 defs, then mmse..PNNS abbrevs mixed with leftover
    # From extract: abbrevs LSD-MINOCA (10), defs LSD-MINOCA (10), then mmse-PPSB abbrevs, then defs
    defs1 = rest[:10]
    pairs.extend(zip_defs_abbrs(defs1, abbrs1))
    rest = rest[10:]
    # rest starts with mmse (abbrev-like lower) then MRC... then defs mini mental...
    # Treat from mmse to PPSB as abbrevs (until a long lowercase def)
    abbrs2 = []
    i = 0
    while i < len(rest) and (is_abbrev(rest[i]) or rest[i] in {"mmse", "F"}):
        if rest[i] != "F":
            abbrs2.append(rest[i])
        i += 1
    defs2 = rest[i:]
    # PPSB has 2-line def
    merged = []
    j = 0
    while j < len(defs2):
        if defs2[j].startswith("Facteurs II") and j + 1 < len(defs2):
            merged.append(defs2[j] + " " + defs2[j + 1])
            j += 2
        else:
            merged.append(defs2[j])
            j += 1
    pairs.extend(zip_defs_abbrs(merged, abbrs2))

    # p29 defs then abbrs; some 2-line? SCA NST duplicated in extract
    p = pages[4]
    idx = p.index("QRM")
    defs, abbrs = p[:idx], [a for a in p[idx:] if a != "XXII"]
    pairs.extend(zip_defs_abbrs(defs, abbrs))

    # p30 interleaved
    p = pages[5]
    i = 0
    while i < len(p):
        if is_abbrev(p[i]) and i + 1 < len(p) and not is_abbrev(p[i + 1]):
            pairs.append((p[i], p[i + 1]))
            i += 2
        else:
            i += 1

    seen = set()
    items = []
    for abbr, defn in pairs:
        a, d = norm(abbr), norm(defn)
        if a in {"Fl, Fil, etc."}:
            a = "FI, FII, etc."
        key = (a, d)
        if key in seen or not a or not d:
            continue
        seen.add(key)
        items.append({"abbr": a, "def": d})

    # Sigles très utilisés dans les cours mais absents de la liste liminaire.
    extra = [
        ("ARNI", "Angiotensin receptor-neprilysin inhibitor (sacubitril/valsartan)"),
        ("CHA2DS2-VA", "Score embolique de la FA (CNEC 3e : sans point « sexe », 0–8). Ne s’applique pas si prothèse mécanique ou RM modéré–sévère"),
        ("CRT", "Cardiac resynchronization therapy (stimulateur biventriculaire)"),
        ("DAPT", "Dual antiplatelet therapy (double antiagrégation plaquettaire)"),
        ("DEA", "Défibrillateur externe automatisé"),
        ("HAS-BLED", "Score de risque hémorragique sous anticoagulant (FA)"),
        ("HFpEF", "Heart failure with preserved ejection fraction (IC à FEVG conservée, > 50 %)"),
        ("HFrEF", "Heart failure with reduced ejection fraction (IC à FEVG diminuée, < 40 %)"),
        ("WPW", "Syndrome de Wolff–Parkinson–White (voie accessoire)"),
    ]
    have_abbr = {x["abbr"].upper() for x in items}
    for a, d in extra:
        if a.upper() in have_abbr:
            continue
        items.append({"abbr": a, "def": d, "extra": True})
        have_abbr.add(a.upper())
    items.sort(key=lambda x: x["abbr"].upper())
    OUT.write_text(
        json.dumps(
            {
                "source": "Liste des abréviations du collège CNEC 3e éd. (pages liminaires).",
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"{len(items)} sigles -> {OUT}")


if __name__ == "__main__":
    main()
