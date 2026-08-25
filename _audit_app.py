# -*- coding: utf-8 -*-
"""Audit rapide de l'app QCM — JSON, couverture items, QCM, assets."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"

EXPECTED_ITEMS = {
    "221", "222", "223", "224", "225", "230", "339",
    "152", "153", "233RA", "233IM", "233IA", "238",
    "231", "232", "236", "237", "342",
    "203", "234", "226", "235", "331", "330",
}

JSON_FILES = [
    "bank.json", "cours.json", "fiches.json", "notions.json", "sigles.json",
    "traitements.json", "arbres.json", "trous.json", "ecos.json", "ecg_rappels.json",
    "mnemos.json", "vignettes.json", "flashcards_lot1.json", "recap.json",
    "notions_indispensables.json",
]


def load_json(name: str):
    p = ROOT / name
    if not p.exists():
        return None, f"MISSING FILE: {name}"
    try:
        return json.loads(p.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as e:
        return None, f"INVALID JSON {name}: {e}"


def audit_fetch_refs() -> list[str]:
    issues = []
    if not INDEX.exists():
        return ["index.html missing"]
    html = INDEX.read_text(encoding="utf-8")
    refs = set(re.findall(r'fetch\("([^"]+\.json)"\)', html))
    for ref in sorted(refs):
        if not (ROOT / ref).exists():
            issues.append(f"index.html fetch missing file: {ref}")
    return issues


def audit_bank(bank: dict) -> list[str]:
    issues = []
    prompts: dict[str, list[str]] = {}
    ids: set[str] = set()
    for q in bank.get("questions", []):
        qid = q.get("id", "")
        if qid in ids:
            issues.append(f"Duplicate QCM id: {qid}")
        ids.add(qid)
        prompt = (q.get("prompt") or "").strip()
        if prompt in prompts:
            issues.append(f"Duplicate prompt ({qid} ~ {prompts[prompt][0]}): {prompt[:80]}…")
        else:
            prompts[prompt] = [qid]
        ans = q.get("correct") or q.get("answer") or q.get("answers")
        if not ans:
            issues.append(f"No answer: {qid}")
        choices = q.get("options") or q.get("choices") or []
        if len(choices) < 2:
            issues.append(f"<2 choices: {qid}")
        if q.get("image"):
            img = q["image"]
            if not (ROOT / img).exists() and not (ROOT / "images" / Path(img).name).exists():
                # try relative to qcm folder
                candidates = list(ROOT.glob(f"**/{Path(img).name}"))
                if not candidates:
                    issues.append(f"Missing image {img} for {qid}")
    items = {it["id"] for it in bank.get("items", [])}
    missing = EXPECTED_ITEMS - items
    if missing:
        issues.append(f"Bank missing items: {sorted(missing)}")
    return issues


def audit_cours(cours: list) -> list[str]:
    issues = []
    items = {c["item"] for c in cours}
    missing = EXPECTED_ITEMS - items
    extra = items - EXPECTED_ITEMS
    if missing:
        issues.append(f"cours.json missing items: {sorted(missing)}")
    if extra:
        issues.append(f"cours.json extra items: {sorted(extra)}")
    for c in cours:
        if not c.get("rangA"):
            issues.append(f"cours {c['item']}: empty rangA")
    return issues


def audit_recap(recap: dict) -> list[str]:
    issues = []
    items = {r["item"] for r in recap.get("recaps", [])}
    missing = EXPECTED_ITEMS - items
    if missing:
        issues.append(f"recap.json missing items: {sorted(missing)}")
    empty = [r["item"] for r in recap.get("recaps", []) if not (r.get("text") or "").strip()]
    if empty:
        issues.append(f"recap.json empty text: {empty}")
    return issues


def audit_indisp(data: dict) -> list[str]:
    issues = []
    items = {r["item"] for r in data.get("items", [])}
    # 231 has no section in collège
    expected = EXPECTED_ITEMS - {"231"}
    missing = expected - items
    if missing:
        issues.append(f"notions_indispensables.json missing: {sorted(missing)}")
    for r in data.get("items", []):
        if not r.get("indispensables") and not r.get("inacceptables"):
            issues.append(f"notions_indispensables empty: {r['item']}")
    return issues


def audit_vignettes(vig: dict) -> list[str]:
    issues = []
    for v in vig.get("vignettes", []):
        qs = v.get("questions") or []
        for i, qa in enumerate(qs):
            if not (qa.get("answer") or "").strip():
                issues.append(f"vignette {v['item']} Q{i+1}: no answer")
    return issues


def audit_ecg_svg(bank: dict) -> list[str]:
    issues = []
    for q in bank.get("questions", []):
        img = q.get("image") or ""
        if "ecg" in img.lower() or img.endswith(".svg"):
            p = ROOT / img if not img.startswith("http") else None
            if p and not p.exists():
                alt = list(ROOT.glob(f"**/{Path(img).name}"))
                if not alt:
                    issues.append(f"ECG/svg missing: {img} ({q.get('id')})")
    return issues


def main() -> int:
    all_issues: list[str] = []
    all_issues.extend(audit_fetch_refs())

    data: dict = {}
    for name in JSON_FILES:
        obj, err = load_json(name)
        if err:
            all_issues.append(err)
        else:
            data[name] = obj

    if "bank.json" in data:
        all_issues.extend(audit_bank(data["bank.json"]))
        all_issues.extend(audit_ecg_svg(data["bank.json"]))
    if "cours.json" in data:
        all_issues.extend(audit_cours(data["cours.json"]))
    if "recap.json" in data:
        all_issues.extend(audit_recap(data["recap.json"]))
    if "notions_indispensables.json" in data:
        all_issues.extend(audit_indisp(data["notions_indispensables.json"]))
    if "vignettes.json" in data:
        all_issues.extend(audit_vignettes(data["vignettes.json"]))

    # Rebuild bank check
    import subprocess
    r = subprocess.run(
        [sys.executable, str(ROOT / "_build_bank.py")],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    if r.returncode != 0:
        all_issues.append(f"_build_bank.py failed: {r.stderr or r.stdout}")

    if all_issues:
        print(f"=== {len(all_issues)} issue(s) ===")
        for i, x in enumerate(all_issues, 1):
            print(f"{i}. {x}")
        return 1
    print("OK — no issues found")
    print(f"  JSON files: {len(JSON_FILES)}")
    if "bank.json" in data:
        print(f"  QCMs: {len(data['bank.json'].get('questions', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
