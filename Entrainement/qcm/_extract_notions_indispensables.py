# -*- coding: utf-8 -*-
"""Extract 'Notions indispensables et inacceptables' from Cours/*.md."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURS = ROOT / "Cours"
OUT = Path(__file__).resolve().parent / "notions_indispensables.json"

ITEM_MAP: dict[str, tuple[str, str]] = {
    "221_Atherome.md": ("221", "221 Athérome"),
    "222_Facteurs_risque_et_prevention.md": ("222", "222 FDR / prévention"),
    "223_Dyslipidemies.md": ("223", "223 Dyslipidémies"),
    "224_Hypertension_arterielle.md": ("224", "224 HTA"),
    "225_Arteriopathie_AOMI_anevrismes.md": ("225", "225 AOMI / anévrismes"),
    "230_Douleur_thoracique_aigue.md": ("230", "230 Douleur thoracique"),
    "339_SCA_angor_stable.md": ("339", "339 SCA / angor"),
    "152_Endocardite_infectieuse.md": ("152", "152 Endocardite"),
    "153_Surveillance_porteurs_valves_protheses.md": ("153", "153 Prothèses"),
    "233_IA_Insuffisance_aortique.md": ("233IA", "233 IA"),
    "233_IM_Insuffisance_mitrale.md": ("233IM", "233 IM"),
    "233_RA_Retrecissement_aortique.md": ("233RA", "233 RA"),
    "238_Souffle_cardiaque_enfant.md": ("238", "238 Souffle enfant"),
    "231_ECG.md": ("231", "231 ECG"),
    "232_Fibrillation_atriale.md": ("232", "232 FA"),
    "236_Troubles_conduction.md": ("236", "236 Conduction"),
    "237_Palpitations.md": ("237", "237 Palpitations"),
    "342_Malaises_PDCB.md": ("342", "342 Malaises / syncope"),
    "203_Dyspnee_aigue_chronique.md": ("203", "203 Dyspnée"),
    "234_Insuffisance_cardiaque.md": ("234", "234 Insuffisance cardiaque"),
    "226_TVP_embolie_pulmonaire.md": ("226", "226 TVP / EP"),
    "235_Pericardite_aigue.md": ("235", "235 Péricardite"),
    "331_Arret_cardiocirculatoire.md": ("331", "331 Arrêt cardiaque"),
    "330_Antithrombotiques_accidents_anticoagulants.md": ("330", "330 Antithrombotiques"),
}

STOP = re.compile(
    r"\n## (?:Réflexes transversalité|Entraînement|Pour en savoir plus)\b",
    re.I,
)


def find_file(name: str) -> Path | None:
    for p in COURS.rglob(name):
        return p
    return None


def _is_bullet(line: str) -> bool:
    s = line.lstrip()
    return s.startswith("- ") or s.startswith("• ")


def _bullet_body(line: str) -> str:
    return re.sub(r"^(\s*)[-•]\s*", "", line).strip()


def merge_broken_bullets(lines: list[str]) -> list[str]:
    return parse_bullets("\n".join(lines))


def parse_bullets(block: str) -> list[str]:
    if not block:
        return []
    items: list[str] = []
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if not _is_bullet(line):
            if items:
                items[-1] = items[-1] + " " + line
            continue
        body = _bullet_body(line)
        is_sub = body.startswith("- ")
        if is_sub:
            body = body[2:].strip()
        if is_sub and items:
            items[-1] = items[-1] + "\n  • " + body
            continue
        if items and (
            body.startswith("+")
            or body.startswith("(")
            or items[-1].endswith("-")
            or (body and body[0].islower() and not body.startswith("item "))
        ):
            if items[-1].endswith("-"):
                items[-1] = items[-1][:-1] + body
            elif body.startswith("+"):
                items[-1] = items[-1] + " + " + body.lstrip("+").strip()
            else:
                items[-1] = items[-1] + " " + body
            continue
        items.append(body)
    return [x.strip() for x in items if x.strip()]


def extract_notion_sections(text: str) -> tuple[list[str], list[str]] | None:
    m = re.search(
        r"^## Notions indispensables et inacceptables\s*\n(.*?)(?="
        r"\n---\s*\n## |\n## (?:Réflexes|Entraînement|Pour en savoir plus)\b|\Z)",
        text,
        re.S | re.M | re.I,
    )
    if not m:
        return None
    body = m.group(1)
    ind_m = re.search(
        r"### Notions indispensables\s*\n(.*?)(?=\n### Notions inacceptables|\Z)",
        body,
        re.S | re.I,
    )
    inacc_m = re.search(
        r"### Notions inacceptables\s*\n(.*)",
        body,
        re.S | re.I,
    )
    indispensables = parse_bullets(ind_m.group(1)) if ind_m else []
    inacceptables = parse_bullets(inacc_m.group(1)) if inacc_m else []
    if not indispensables and not inacceptables:
        return None
    return indispensables, inacceptables


def main() -> None:
    items: list[dict] = []
    missing: list[str] = []

    for fname, (item_id, label) in sorted(ITEM_MAP.items(), key=lambda x: x[1][0]):
        path = find_file(fname)
        if not path:
            missing.append(fname)
            continue
        parsed = extract_notion_sections(path.read_text(encoding="utf-8"))
        if not parsed:
            missing.append(f"{fname} (no section)")
            continue
        ind, inacc = parsed
        items.append({
            "item": item_id,
            "label": label,
            "indispensables": ind,
            "inacceptables": inacc,
        })

    payload = {
        "note": "Notions indispensables et inacceptables — fin de chapitre collège (après « Points »).",
        "items": items,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(items)} items to {OUT.name}")
    if missing:
        print("Missing:", ", ".join(missing))


if __name__ == "__main__":
    main()
