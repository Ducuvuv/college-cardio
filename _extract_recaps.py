# -*- coding: utf-8 -*-
"""Extract full 'Points' récapitulatif sections from Cours/*.md into recap.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURS = ROOT / "Cours"
OUT = Path(__file__).resolve().parent / "recap.json"

# Same item coverage as vignettes / cours.json
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
    r"\n## (?:Notions indispensables|Réflexes transversalité|Entraînement|Pour en savoir plus)\b",
    re.I,
)


def find_file(name: str) -> Path | None:
    for p in COURS.rglob(name):
        return p
    return None


def extract_points(text: str) -> str | None:
    m = re.search(r"^## Points(?:\s*\([^)]+\))?\s*\n", text, re.M)
    if m:
        start = m.end()
        rest = text[start:]
        stop = STOP.search(rest)
        block = rest[: stop.start()] if stop else rest
        return clean_block(block)

    # Fallback: bullets before Notions (224 HTA — header missing in source md)
    m2 = re.search(
        r"(?:^|\n)(• La PA de consultation est mesurée.*?)(?=\n---\s*\n## Notions|\n## Notions)",
        text,
        re.S,
    )
    if m2:
        return clean_block(m2.group(1))

    # Fallback: 233 IM — récap en fin de chapitre sans titre « Points »
    m3 = re.search(
        r"(\*\*Rang A\.\*\* L'IM est caractérisée.*?)(?=\n---\s*\n## Notions|\n## Notions)",
        text,
        re.S,
    )
    if m3:
        return clean_block(m3.group(1))

    return None


def _is_bullet(line: str) -> bool:
    s = line.lstrip()
    return s.startswith("- ") or s.startswith("• ")


def _bullet_body(line: str) -> str:
    return re.sub(r"^(\s*)[-•]\s*", r"\1", line).strip()


def merge_broken_lines(text: str) -> str:
    """Join PDF line-wrap artifacts (mid-sentence bullets on next line)."""
    compact: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("•"):
            line = re.sub(r"^(\s*)•\s*", r"\1- ", line)
        if _is_bullet(line) and compact:
            prev = compact[-1]
            body = _bullet_body(line)
            prev_stripped = prev.rstrip()
            if prev_stripped.endswith("-") or (
                _is_bullet(prev)
                and not prev_stripped.endswith((".", ";", ":", ")", "»", "…", "!", "?"))
                and body
                and (body[0].islower() or body.startswith("+") or body.startswith("("))
            ):
                if prev_stripped.endswith("-"):
                    compact[-1] = prev_stripped[:-1] + body
                else:
                    compact[-1] = prev_stripped + " " + body
                continue
        compact.append(line)

    # Paragraph break between top-level bullets (not nested with 2+ spaces)
    out: list[str] = []
    for line in compact:
        if out and _is_bullet(line) and not line.startswith("  ") and _is_bullet(out[-1]) and not out[-1].startswith("  "):
            out.append("")
        out.append(line)
    return "\n".join(out).strip()


def clean_block(block: str) -> str:
    lines: list[str] = []
    for raw in block.splitlines():
        line = raw.rstrip()
        if line.strip() == "---":
            continue
        if line.lstrip().startswith("•"):
            line = re.sub(r"^(\s*)•\s*", r"\1- ", line)
        lines.append(line)
    text = merge_broken_lines("\n".join(lines))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main() -> None:
    recaps: list[dict] = []
    missing: list[str] = []

    for fname, (item_id, label) in sorted(ITEM_MAP.items(), key=lambda x: x[1][0]):
        path = find_file(fname)
        if not path:
            missing.append(fname)
            continue
        text = path.read_text(encoding="utf-8")
        body = extract_points(text)
        if not body:
            missing.append(f"{fname} (no Points section)")
            continue
        recaps.append({"item": item_id, "label": label, "text": body})

    payload = {
        "note": "Récapitulatif « Points » en fin de chapitre collège — texte intégral extrait des Cours/*.md.",
        "recaps": recaps,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(recaps)} recaps to {OUT.name}")
    if missing:
        print("Missing:", ", ".join(missing))


if __name__ == "__main__":
    main()
