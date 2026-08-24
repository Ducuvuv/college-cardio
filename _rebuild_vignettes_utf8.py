# -*- coding: utf-8 -*-
"""Rebuild vignettes.json with clean UTF-8 stems/questions from Cours + answers from existing file."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURS = ROOT / "Cours"
OUT = Path(__file__).resolve().parent / "vignettes.json"

ITEM_MAP = {
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
    "232_Fibrillation_atriale.md": ("232", "232 FA"),
    "236_Troubles_conduction.md": ("236", "236 Conduction"),
    "237_Palpitations.md": ("237", "237 Palpitations"),
    "342_Malaises_PDCB.md": ("342", "342 Malaises / syncope"),
    "203_Dyspnee_aigue_chronique.md": ("203", "203 Dyspnée"),
    "234_Insuffisance_cardiaque.md": ("234", "234 Insuffisance cardiaque"),
    "226_TVP_embolie_pulmonaire.md": ("226", "226 TVP / EP"),
    "235_Pericardite_aigue.md": ("235", "235 Péricardite"),
    "331_Arret_cardiocirculatoire.md": ("331", "331 Arrêt cardiaque"),
}

SPECIAL_235 = {
    "stem": (
        "Vous accueillez au service des urgences un homme de 26 ans, sportif, qui présente une douleur "
        "thoracique intense (EVA 8/10), rétrosternale, fluctuante car majorée par les inspirations et la "
        "position en décubitus. La douleur a débuté la veille au soir. Contexte de virose ORL récente. "
        "Fébricule 38 °C, frottement systolodiastolique. ECG initial normal puis sus-décalage ST diffus "
        "n'englobant pas l'onde T. Aspirine 1 g soulage. CRP 15 mg/L, troponine normale, ETT : "
        "épanchement péricardique minime."
    ),
    "questions": [
        "Quels critères permettent de retenir le diagnostic de péricardite aiguë chez ce patient ?",
        "Quels éléments ECG différencient une péricardite d'un SCA ST+ ?",
        "Quel est le rôle de la troponine et de l'échocardiographie ?",
        "Quel traitement proposez-vous en première intention ?",
        "Quelles consignes donnez-vous concernant le sport ?",
        "Le traitement ambulatoire est-il possible ? Quelles précautions ?",
    ],
}

SPECIAL_339 = {
    "stem": (
        "Vous êtes de garde au service d'accueil des urgences. Vous prenez en charge un patient "
        "ayant une douleur thoracique aiguë depuis environ 2 heures."
    ),
    "questions": [
        "Que recherchez-vous en priorité ?",
        "Quel(s) examen(s) complémentaire(s) réalisez-vous en premier lieu ?",
        "En cas de SCA ST+, attitude thérapeutique aux urgences ?",
        "En cas de souffle systolique, hypothèses ?",
        "Prescriptions à la sortie si évolution favorable ?",
        "Objectifs thérapeutiques ?",
    ],
}


def extract_block(text: str) -> str:
    m = re.search(
        r"## Vignette clinique\s*(.*?)(?=\n# |\n## Introduction|\n---\s*\n# |\Z)",
        text,
        re.S,
    )
    return m.group(1) if m else ""


def parse_qs(block: str) -> tuple[str, list[str]]:
    block = re.sub(r"\*\(Le collège[^*]*\*\)", "", block)
    lines = block.splitlines()
    qs: list[str] = []
    stem_parts: list[str] = []
    buf = ""
    hit_q = False
    for line in lines:
        if line.startswith(">"):
            hit_q = True
            part = line.lstrip("> ").strip()
            if not part:
                continue
            buf = f"{buf} {part}".strip() if buf else part
        else:
            if buf:
                qs.append(re.sub(r"\s+", " ", buf).strip())
                buf = ""
            if not hit_q and line.strip() and not line.strip().startswith("##"):
                stem_parts.append(line.strip())
    if buf:
        qs.append(re.sub(r"\s+", " ", buf).strip())
    stem = re.sub(r"\s+", " ", " ".join(stem_parts)).strip().rstrip("> ").strip()
    qs = [q for q in qs if q and not q.startswith("I J")]
    return stem, qs


def clean_ans(s: str) -> str:
    return (
        s.replace("Arrét", "Arrêt")
        .replace("spécialise", "spécialisé")
        .replace("Pericardite", "Péricardite")
        .replace("sous-decalage", "sous-décalage")
        .replace("Caracteriser", "Caractériser")
    )


def main() -> None:
    old = json.loads(OUT.read_text(encoding="utf-8"))
    old_by = {v["item"]: v for v in old["vignettes"]}
    out = []
    missing = []
    for p in sorted(COURS.rglob("*.md")):
        if p.name not in ITEM_MAP:
            continue
        item, label = ITEM_MAP[p.name]
        oldqs = old_by.get(item, {}).get("questions", [])
        if item == "235":
            stem, qs = SPECIAL_235["stem"], SPECIAL_235["questions"]
        elif item == "339":
            stem, qs = SPECIAL_339["stem"], SPECIAL_339["questions"]
        else:
            stem, qs = parse_qs(extract_block(p.read_text(encoding="utf-8")))
        questions = []
        for i, q in enumerate(qs):
            ans = clean_ans(oldqs[i]["answer"]) if i < len(oldqs) else ""
            if not ans:
                missing.append((item, i, q[:70]))
            questions.append({"q": q, "answer": ans})
        out.append({"item": item, "label": label, "stem": stem, "questions": questions})

    data = {
        "note": (
            "Réponses pédagogiques alignées sur le cours CNEC 3e éd. "
            "(les vignettes du collège n'ont pas de corrigé officiel dans le livre)."
        ),
        "vignettes": out,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    nq = sum(len(v["questions"]) for v in out)
    print(f"vignettes={len(out)} questions={nq} missing={len(missing)}")
    for m in missing:
        print("MISSING", m)


if __name__ == "__main__":
    main()
