# -*- coding: utf-8 -*-
"""Parse Entrainement/QI/*.md → bank.json for the QCM trainer."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QI_DIR = ROOT / "Entrainement" / "QI"
OUT = Path(__file__).resolve().parent / "bank.json"

GROUPS = [
    ("I — Athérome", ["221", "222", "223", "224", "225", "339", "230"]),
    ("II — Valves", ["233RA", "233IM", "233IA", "152", "153", "238"]),
    ("III — Rythme", ["342", "231", "232", "236", "237"]),
    ("IV — IC", ["203", "234"]),
    ("V — MTEV", ["226"]),
    ("VI — Divers", ["235", "331", "330"]),
]

LABELS = {
    "221": "221 Athérome",
    "222": "222 FDR / prévention",
    "223": "223 Dyslipidémies",
    "224": "224 HTA",
    "225": "225 AOMI / anévrismes",
    "339": "339 SCA / angor",
    "230": "230 Douleur thoracique",
    "233RA": "233 RA",
    "233IM": "233 IM",
    "233IA": "233 IA",
    "152": "152 Endocardite",
    "153": "153 Prothèses",
    "238": "238 Souffle enfant",
    "342": "342 Malaises / syncope",
    "231": "231 ECG",
    "232": "232 FA",
    "236": "236 Conduction",
    "237": "237 Palpitations",
    "203": "203 Dyspnée",
    "234": "234 Insuffisance cardiaque",
    "226": "226 TVP / EP",
    "235": "235 Péricardite",
    "331": "331 Arrêt cardiaque",
    "330": "330 Antithrombotiques",
}

FILE_ITEM = {
    "221_Atherome.md": "221",
    "222_Facteurs_risque_et_prevention.md": "222",
    "223_Dyslipidemies.md": "223",
    "224_Hypertension_arterielle.md": "224",
    "225_Arteriopathie_AOMI_anevrismes.md": "225",
    "339_SCA_angor_stable.md": "339",
    "230_Douleur_thoracique_aigue.md": "230",
    "233_Valvulopathies.md": "233",
    "152_Endocardite_infectieuse.md": "152",
    "153_Surveillance_porteurs_valves_protheses.md": "153",
    "238_Souffle_cardiaque_enfant.md": "238",
    "342_Malaises_PDCB.md": "342",
    "231_ECG.md": "231",
    "232_Fibrillation_atriale.md": "232",
    "236_Troubles_conduction.md": "236",
    "237_Palpitations.md": "237",
    "203_Dyspnee.md": "203",
    "234_Insuffisance_cardiaque.md": "234",
    "226_TVP_embolie_pulmonaire.md": "226",
    "235_Pericardite_aigue.md": "235",
    "331_Arret_cardiocirculatoire.md": "331",
    "330_Antithrombotiques_accidents_anticoagulants.md": "330",
}

Q_SPLIT = re.compile(r"^## (QRM|QRU)\s+(\d+)\s*$", re.M)
OPT_RE = re.compile(r"^- ([A-E])\.\s+(.*)$", re.M)
ANS_RE = re.compile(r"^\*\*Réponse\s*:\s*(.+?)\*\*\s*$", re.M)
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LETTER_RE = re.compile(r"\b([A-E])\b(?:\s*\((PCZ)\))?", re.I)


def item_for_233(n: int) -> str:
    if n <= 3:
        return "233RA"
    if n <= 8:
        return "233IM"
    return "233IA"


def parse_answers(raw: str) -> tuple[list[str], list[str]]:
    correct: list[str] = []
    pcz: list[str] = []
    for m in LETTER_RE.finditer(raw):
        letter = m.group(1).upper()
        if letter not in correct:
            correct.append(letter)
        if m.group(2):
            pcz.append(letter)
    return correct, pcz


def parse_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    base = FILE_ITEM[path.name]
    matches = list(Q_SPLIT.finditer(text))
    out: list[dict] = []
    for i, m in enumerate(matches):
        kind = m.group(1)
        num = int(m.group(2))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        am = ANS_RE.search(body)
        if not am:
            raise SystemExit(f"No answer in {path.name} {kind} {num}")
        stem = body[: am.start()].strip()
        explanation = body[am.end() :].strip()
        explanation = re.sub(r"^---+\s*", "", explanation).strip()
        explanation = re.sub(r"\n---+\s*$", "", explanation).strip()
        options = [{"letter": om.group(1), "text": om.group(2).strip()} for om in OPT_RE.finditer(stem)]
        # stem = everything before first option
        first_opt = OPT_RE.search(stem)
        if not first_opt:
            raise SystemExit(f"No options in {path.name} {kind} {num}")
        prompt = stem[: first_opt.start()].strip()
        images = []
        for im in IMG_RE.finditer(prompt):
            src = im.group(2)
            # QI files use ../../Cours/... ; qcm/ is also two levels under root
            images.append({"alt": im.group(1), "src": src})
        prompt = IMG_RE.sub("", prompt).strip()
        correct, pcz = parse_answers(am.group(1))
        scz = sorted({m.upper() for m in re.findall(r"\b([A-E])\s*=\s*SCZ", explanation, flags=re.I)})
        item = item_for_233(num) if base == "233" else base
        out.append(
            {
                "id": f"{item}-{kind}{num}",
                "item": item,
                "kind": kind,
                "n": num,
                "prompt": prompt,
                "options": options,
                "correct": correct,
                "pcz": pcz,
                "scz": scz,
                "explanation": explanation,
                "images": images,
                "origin": "college",
                "rang": "A",
                "theme": "",
            }
        )
    return out


NOUVEAU_DIR = Path(__file__).resolve().parent / "nouveau"


def load_nouveau() -> list[dict]:
    allowed = set(LABELS)
    letters = set("ABCDE")
    out: list[dict] = []
    errors: list[str] = []
    for path in sorted(NOUVEAU_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for i, q in enumerate(data.get("questions") or [], 1):
            item = q.get("item")
            opts = q.get("options") or []
            correct = [c.upper() for c in (q.get("correct") or [])]
            kind = q.get("kind") or "QRM"
            opt_letters = [o.get("letter", "").upper() for o in opts]
            if item not in allowed:
                errors.append(f"{path.name}#{i}: item inconnu {item}")
            if opt_letters != ["A", "B", "C", "D", "E"]:
                errors.append(f"{path.name}#{i}: options A-E requises ({opt_letters})")
            if not correct or any(c not in letters for c in correct):
                errors.append(f"{path.name}#{i}: correct invalide {correct}")
            if kind == "QRU" and len(correct) != 1:
                errors.append(f"{path.name}#{i}: QRU doit avoir 1 réponse")
            if not (q.get("prompt") or "").strip() or not (q.get("explanation") or "").strip():
                errors.append(f"{path.name}#{i}: prompt/explanation vide")
            if set(correct) == letters:
                errors.append(f"{path.name}#{i}: les 5 propositions sont vraies (inutile)")
            options = []
            for o in opts:
                row = {"letter": o["letter"].upper(), "text": o["text"].strip()}
                why = (o.get("why") or "").strip()
                if why:
                    row["why"] = why
                options.append(row)
            out.append(
                {
                    "id": f"{item}-N-{path.stem}-{i:03d}",
                    "item": item,
                    "kind": kind,
                    "n": i,
                    "prompt": q["prompt"].strip(),
                    "options": options,
                    "correct": correct,
                    "pcz": [x.upper() for x in (q.get("pcz") or [])],
                    "scz": [x.upper() for x in (q.get("scz") or [])],
                    "explanation": q["explanation"].strip(),
                    "images": q.get("images") or [],
                    "format": q.get("format") or "standard",
                    "theme": q.get("theme") or "",
                    "origin": "nouveau",
                    "rang": q.get("rang") or "A",
                }
            )
    seen = {}
    for q in out:
        key = re.sub(r"\s+", " ", q["prompt"].lower())
        if key in seen:
            errors.append(f"doublon prompt: {q['id']} / {seen[key]}")
        else:
            seen[key] = q["id"]
    if errors:
        raise SystemExit("Banque neuve invalide:\n" + "\n".join(errors[:40]))
    return out


TREAT_RE = re.compile(
    r"(?i)\b("
    r"traitement|m[ée]dicament|statine|IEC|ARA2|b[êe]ta-?bloquant|"
    r"aspirine|clopidogrel|prasugrel|ticagr[ée]lor|anticoag|antiagr[ée]g|"
    r"AOD|AVK|h[ée]parine|HBPM|furos[ée]mide|gliflozine|amiodarone|"
    r"fl[ée]ca[iï]nide|TAVI|fibrinol|INR|CHA2DS2|nitr[ée]s|dobutamine|"
    r"fondaparinux|apixaban|rivaroxaban|dabigatran|[ée]noxaparine|"
    r"spironolactone|sacubitril|[ée]z[ée]timibe|PCSK9|colchicine|"
    r"bith[ée]rapie|DAPT|idarucizumab|protamine|warfarine"
    r")\b"
)


def tag_treatment(q: dict) -> None:
    if q.get("theme") == "traitement":
        return
    blob = q.get("prompt", "") + " " + " ".join(o.get("text", "") for o in q.get("options") or [])
    if TREAT_RE.search(blob):
        q["theme"] = "traitement"


def main() -> None:
    college = []
    for name, _item in FILE_ITEM.items():
        path = QI_DIR / name
        if not path.exists():
            raise SystemExit(f"Missing {path}")
        college.extend(parse_file(path))
    nouveau = load_nouveau()
    questions = nouveau + college
    for q in questions:
        tag_treatment(q)
    n_new: dict[str, int] = {}
    n_col: dict[str, int] = {}
    formats: dict[str, int] = {}
    rangs: dict[str, int] = {}
    themes: dict[str, int] = {}
    for q in nouveau:
        n_new[q["item"]] = n_new.get(q["item"], 0) + 1
        fmt = q.get("format") or "standard"
        formats[fmt] = formats.get(fmt, 0) + 1
        rang = (q.get("rang") or "A").upper()
        if rang not in ("A", "B", "C"):
            rang = "A"
        rangs[rang] = rangs.get(rang, 0) + 1
        th = q.get("theme") or "autre"
        themes[th] = themes.get(th, 0) + 1
    for q in college:
        n_col[q["item"]] = n_col.get(q["item"], 0) + 1
        fmt = q.get("format") or "standard"
        formats[fmt] = formats.get(fmt, 0) + 1
        rang = (q.get("rang") or "A").upper()
        if rang not in ("A", "B", "C"):
            rang = "A"
        rangs[rang] = rangs.get(rang, 0) + 1
        th = q.get("theme") or "autre"
        themes[th] = themes.get(th, 0) + 1
    items = []
    for gid, ids in GROUPS:
        for iid in ids:
            items.append(
                {
                    "id": iid,
                    "label": LABELS[iid],
                    "group": gid,
                    "nNouveau": n_new.get(iid, 0),
                    "nCollege": n_col.get(iid, 0),
                    "n": n_new.get(iid, 0),
                    "highYield": iid in {
                        "234", "233RA", "233IM", "232", "339", "231", "152", "342", "226", "230",
                    },
                }
            )
    bank = {
        "source": "Questions neuves d'après les cours MD du dépôt + QI collège (pas d'annales UNESS)",
        "groups": [{"id": g, "items": ids} for g, ids in GROUPS],
        "items": items,
        "origins": {"nouveau": len(nouveau), "college": len(college)},
        "formats": formats,
        "rangs": rangs,
        "themes": themes,
        "cible": {
            "seenHigh": 12,
            "pctHigh": 80,
            "seenOther": 8,
            "pctOther": 70,
            "sessionSize": 20,
        },
        "questions": questions,
    }
    OUT.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"nouveau={len(nouveau)} college={len(college)} total={len(questions)} treat={themes.get('traitement', 0)} -> {OUT}")
    for it in items:
        print(f"  {it['id']:7} N={it['nNouveau']:2} C={it['nCollege']:2}  {it['label']}")


if __name__ == "__main__":
    main()
