# -*- coding: utf-8 -*-
"""Generate item 330 markdown from extracted PDF text."""
import re
from pathlib import Path

SRC = Path(r"C:\Users\gestu\Documents\college cardio\_tmp_item330.txt")
OUT = Path(r"C:\Users\gestu\Documents\college cardio\Cours\VI_Divers\330_Antithrombotiques_accidents_anticoagulants.md")

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Médecine cardiovasculaire\s*$",
    r"^Divers\s*$",
    r"^F\s*$",
    r"^22\s*$",
    r"^Item 330.*$",
    r"^Prescription et surveillance\s*$",
    r"^des classes de médicaments\s*$",
    r"^les plus courantes\s*$",
    r"^chez l'adulte\s*$",
    r"^et chez l'enfant.*$",
    r"^Connaître les grands\s*$",
    r"^principes thérapeutiques.*$",
    r"^► Entraînement.*",
    r"^Les corrigés sont.*",
    r"^Pour en savoir plus\s*$",
    r"^Valgimigli M.*",
    r"^Source : Lo GK.*",
    r"^1\s*$",
    r"^\d{3}\s*$",
    r"^https://academic.*",
    r"^eurheartj/artide.*",
    r"^Ticlopidine : Ticlid.*",
    r"^Clopidogrel : Plavix.*",
    r"^Prasugrel ; Efient.*",
    r"^Ticagrélor : Brilique.*",
    r"^Dipyramidole:$",
    r"^Persantine.*",
    r"^Anti-GPHb.*",
    r"^Tirofiban.*",
    r"^Eptifibatide.*",
    r"^Récepteur fibrinogène$",
    r"^Récepteur$",
    r"^aspirine \(inhibiteur.*",
    r"^ADP : inhibiteur.*",
    r"^dipyramidole$",
    r"^llb/llla$",
]

SECTION_MAP = {
    "I. Antiagrégants plaquettaires": "\n\n# I. Antiagrégants plaquettaires — AAP\n\n**Rang A** · **Rang B**.",
    "II. Héparines et héparinoïdes": "\n\n---\n\n# II. Héparines et héparinoïdes\n\n**Rang A** · **Rang B**.",
    "III. Antivitamines K": "\n\n---\n\n# III. Antivitamines K\n\n**Rang A** · **Rang B**.",
    "IV. Anticoagulants oraux directs": "\n\n---\n\n# IV. Anticoagulants oraux directs\n\n**Rang A** · **Rang B**.",
    "V. Thrombolytiques": "\n\n---\n\n# V. Thrombolytiques\n\n**Rang A** · **Rang B**.",
    "VI. Accidents des anticoagulants": "\n\n---\n\n# VI. Accidents des anticoagulants\n\n**Rang A** · **Rang B**.",
}

FIG_MAP = {
    "Fig. 22.1": ("fig_22_1_aap_sites.png", "Fig. 22.1 — Sites d'action des antiagrégants plaquettaires"),
    "Fig. 22.2": ("fig_22_2_ep_anticoagulant.png", "Fig. 22.2 — Bonne conduite du traitement anticoagulant dans l'EP"),
    "Fig. 22.3": ("fig_22_3_surveillance_inr.png", "Fig. 22.3 — Fréquence de surveillance des INR"),
}

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")
TABLE_RE = re.compile(r"^Tableau 22\.\d+")
ENCADRE_RE = re.compile(r"^Encadré 22\.\d")

def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    line = line.replace("El ", "• ")
    line = line.replace("1 53", "153")
    line = line.replace("1 00", "100")
    line = line.replace("1 5", "15")
    line = line.replace("1 2", "12")
    line = line.replace("1 0 ", "10 ")
    line = line.replace("1 3", "13")
    line = line.replace("1 8", "18")
    line = line.replace("1 77", "177")
    line = line.replace("1 75", "175")
    line = line.replace("1 58", "158")
    line = line.replace("1 26", "126")
    line = line.replace("1 00/", "100/")
    line = line.replace("1 3/4095043", "13/4095043")
    line = line.replace("artide", "article")
    line = line.replace("justifié", "justifié")  # fix aspirinejustifié
    line = line.replace("aspirinejustifié", "aspirine justifié")
    line = line.replace("relais héparine -AVK", "relais héparine-AVK")
    line = line.replace("relais héparine - AVK", "relais héparine-AVK")
    for prefix, repl in (("• O ", "• **Rang A.** "), ("• □ ", "• **Rang B.** "), ("D ", "• ")):
        if line.startswith(prefix) and prefix != "D ":
            line = repl + line[len(prefix):]
            break
    rank_prefix = {"□ ": "**Rang B.** ", "O ": "**Rang A.** ", "Q ": "**Rang B.** "}
    for prefix, repl in rank_prefix.items():
        if line.startswith(prefix):
            rest = line[len(prefix):]
            if rest and rest[0].islower():
                break
            line = repl + rest
            break
    return line

def extract_body():
    text = SRC.read_text(encoding="utf-8")
    pages = re.split(r"===== PDF PAGE \d+ =====", text)
    lines_out = []
    skip_until_body = True
    done = False
    in_body = False
    in_encadre_points = False

    for chunk in pages:
        if done or not chunk.strip():
            continue
        for line in chunk.splitlines():
            cl = clean_line(line)
            if cl is None:
                continue
            if skip_until_body:
                if "Le traitement antithrombotique" in cl:
                    skip_until_body = False
                    lines_out.append("## Introduction\n")
                    intro = cl.split("Le traitement antithrombotique", 1)[-1]
                    lines_out.append("**Rang A.** Le traitement antithrombotique" + intro)
                    continue
                continue
            if any(cl.startswith(s) for s in (
                "Notions indispensables",
                "Réflexes transversalité",
                "► Entraînement",
                "Pour en savoir plus",
                "O QRM 1",
                "Vous recevez un patient de 77 ans",
            )):
                done = True
                break
            matched = False
            for sec, hdr in SECTION_MAP.items():
                if cl.startswith(sec):
                    lines_out.append(hdr)
                    in_body = True
                    matched = True
                    break
            if matched:
                continue
            if ENCADRE_RE.match(cl):
                if "22.1" in cl:
                    lines_out.append("\n\n---\n\n## Points (encadré 22.1)\n")
                    in_encadre_points = True
                else:
                    lines_out.append(f"\n### {cl}\n")
                continue
            if cl in ("Antiagrégants", "Héparines", "Antivitamines K", "AOD", "Fibrinolytiques", "Accidents des anticoagulants") and in_encadre_points:
                lines_out.append(f"\n**{cl}**\n")
                continue
            if cl.startswith("Grandes règles"):
                lines_out.append(f"\n**{cl}**\n")
                continue
            m = SUBSECTION_RE.match(cl)
            if m and in_body and not in_encadre_points:
                lines_out.append(f"\n## {m.group(1)}\n")
                continue
            m2 = NUM_SUBSECTION_RE.match(cl)
            if m2 and in_body and len(cl) < 90:
                lines_out.append(f"\n### {m2.group(1)}\n")
                continue
            if TABLE_RE.match(cl):
                lines_out.append(f"\n**{cl.strip()}**\n")
                continue
            fig_handled = False
            for fig_key, (fname, caption) in FIG_MAP.items():
                if fig_key in cl and ("Fig." in cl or "fig." in cl):
                    if cl.startswith("Fig."):
                        lines_out.append(f"\n![{caption}](./img/{fname})\n")
                        cap = re.sub(r"^Fig\. 22\.\d+\.?\s*[0-9OEl]?\s*", "Fig. ", cl)
                        lines_out.append(f"\n**{cap}**\n")
                    elif f"fig. {fig_key.split()[-1]}" in cl.lower():
                        lines_out.append(f"\n![{caption}](./img/{fname})\n")
                    fig_handled = True
                    break
            if fig_handled:
                continue
            if cl.startswith("- ") or cl.startswith("• "):
                lines_out.append(cl)
            elif cl.startswith("> "):
                lines_out.append(cl)
            elif len(cl) < 80 and cl.endswith(":") and in_body:
                lines_out.append(f"\n**{cl}**\n")
            else:
                lines_out.append(cl)
        if done:
            break
    return "\n".join(lines_out)

HEADER = '''# Item 330 — Prescription et surveillance des antithrombotiques. Accidents des anticoagulants

> **Collège CNEC / SFC** · 3e édition (2025) · p. 529–554 · R2C  
> Partie VI — Divers  
> *Dans cet ouvrage : antithrombotiques et accidents des anticoagulants.*

---

## Trois repères à ne pas confondre

| Badge | Signification (R2C) |
|---|---|
| **Rang A** | Connaissances fondamentales de fin de 2e cycle |
| **Rang B** | Connaissances essentielles, plus spécialisées |
| **Rang C** | Connaissances de 3e cycle (DES) |

Les pastilles du livre (● = A, ■ = B) sont reprises inline.

---

## Situations de départ

10 Méléna/rectorragies.  
59 Tendance aux saignements.  
60 Hémorragie aiguë.  
89 Purpura/ecchymose/hématome.  
102 Hématurie.  
147 Épistaxis.  
213 Allongement du TCA.  
215 Anomalies des plaquettes.  
217 Baisse de l'hémoglobine.  
218 Diminution du TP.  
248 Prescription et suivi anticoagulant/antiagrégant.  
264 Adaptation sur terrain particulier.  
272 Transfusion sanguine.  
285 Suivi et éducation thérapeutique.  
331 Aléa thérapeutique ou erreur médicale.  
352 Expliquer un traitement au patient.  
354 Évaluation de l'observance.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé |
|---|---|---|
| **A** | Prise en charge | Antiagrégants plaquettaires : mécanismes, indications, effets secondaires, interactions, surveillance, échec |
| **A** | Prise en charge | Héparines : idem |
| **A** | Prise en charge | Anticoagulants oraux (AVK et AOD) : idem |

---

## Parcours Rang A

- [I. Antiagrégants plaquettaires](#i-antiagrégants-plaquettaires--aap)
- [II. Héparines](#ii-héparines-et-héparinoïdes)
- [III. Antivitamines K](#iii-antivitamines-k)
- [IV. AOD](#iv-anticoagulants-oraux-directs)

---

## Sommaire

- [Introduction](#introduction)
- [I. Antiagrégants plaquettaires](#i-antiagrégants-plaquettaires--aap)
- [II. Héparines](#ii-héparines-et-héparinoïdes)
- [III. Antivitamines K](#iii-antivitamines-k)
- [IV. Anticoagulants oraux directs](#iv-anticoagulants-oraux-directs)
- [V. Thrombolytiques](#v-thrombolytiques)
- [VI. Accidents des anticoagulants](#vi-accidents-des-anticoagulants)
- [Points](#points-encadré-221)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/330_Antithrombotiques_accidents_anticoagulants.md)

---

'''

FOOTER = '''
---

## Notions indispensables et inacceptables

### Notions indispensables

- Ne pas oublier l'éducation du patient sous AVK et sous AOD.
- Pas d'AOD dans les prothèses valvulaires mécaniques ou dans le RM.
- Savoir faire un relais héparine-AVK.

### Notions inacceptables

- Prescrire une HBPM ou un AOD en cas d'insuffisance rénale sévère.
- Prescrire un AOD dans les prothèses valvulaires mécaniques ou dans le rétrécissement mitral.

---

## Réflexes transversalité

- Item 153 — Surveillance des porteurs de valve et prothèses vasculaires.
- Item 226 — Thrombose veineuse profonde et embolie pulmonaire.
- Item 232 — Fibrillation atriale.
- Item 339 — Syndromes coronariens aigus.

---

## Entraînement

Questions isolées et corrigés : [Entrainement/QI/330_Antithrombotiques_accidents_anticoagulants.md](../../Entrainement/QI/330_Antithrombotiques_accidents_anticoagulants.md)
'''

def main():
    body = extract_body()
    paragraphs = []
    buf = []
    for line in body.splitlines():
        if not line.strip():
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append("")
            continue
        if line.startswith(("#", "##", "###", "**", "-", "•", ">", "!", "|", "---", "![")):
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append(line)
        else:
            buf.append(line.strip())
    if buf:
        paragraphs.append(" ".join(buf))
    cleaned = "\n\n".join(p for p in paragraphs if p is not None)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(HEADER + cleaned + FOOTER, encoding="utf-8")
    print(f"Written {OUT} ({OUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
