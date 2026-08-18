# -*- coding: utf-8 -*-
"""Generate item 224 markdown from extracted PDF text."""
import re
from pathlib import Path

SRC = Path(r"C:\Users\gestu\Documents\college cardio\_tmp_item224.txt")
OUT = Path(r"C:\Users\gestu\Documents\college cardio\Cours\I_Atherome\224_Hypertension_arterielle.md")

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^\d{1,2}\s*$",
    r"^Athérome, facteurs de risque.*$",
    r"^Item 224.*$",
    r"^4\s*$",
    r"^► Entraînement.*",
    r"^Les corrigés sont.*",
    r"^clés\s*$",
]

SECTION_MAP = {
    "I. Définition et confirmation diagnostique": "# I. Définition et confirmation diagnostique\n\n**Rang A.**",
    "II. Épidémiologie, physiopathologie et conséquences": "\n\n---\n\n# II. Épidémiologie, physiopathologie et conséquences\n\n**Rang A** · **Rang B**.",
    "III. Prise en charge initiale d'un patient hypertendu": "\n\n---\n\n# III. Prise en charge initiale d'un patient hypertendu\n\n**Rang A.**",
    "IV. Traitement": "\n\n---\n\n# IV. Traitement\n\n**Rang A.**",
    "V. Suivi du patient hypertendu après la prise": "\n\n---\n\n# V. Suivi du patient hypertendu après la prise en charge initiale\n\n**Rang A** · **Rang B**.",
    "VI. HTA secondaire": "\n\n---\n\n# VI. HTA secondaire\n\n**Rang A** · **Rang B**.",
    "VII. Urgences hypertensives et HTA maligne": "\n\n---\n\n# VII. Urgences hypertensives et HTA maligne\n\n**Rang A**.",
}

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
TABLE_RE = re.compile(r"^Tableau 4\.\d")

def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    # OCR fixes
    line = line.replace("cidosporine", "ciclosporine")
    line = line.replace("0-hCG", "β-hCG")
    line = line.replace("p-bloquants", "β-bloquants")
    line = line.replace("p-bloquants", "β-bloquants")
    line = line.replace("SC0RE", "SCORE")
    line = line.replace("s 1 10", "≥ 110")
    line = line.replace("à 110", "≥ 110")
    line = line.replace("> 180/1 10", "> 180/110")
    line = line.replace("180/1 10", "180/110")
    line = line.replace("195/1 10", "195/110")
    line = line.replace("220/1 20", "220/120")
    line = line.replace("160/1 10", "160/110")
    line = line.replace("1 20-139", "120-139")
    line = line.replace("1 35", "135")
    line = line.replace("1 10-1 19", "110-119")
    line = line.replace("1 5-20", "15-20")
    line = line.replace("1 5 %", "15 %")
    line = line.replace("1 0 %", "10 %")
    line = line.replace("1 00 mmol", "100 mmol")
    line = line.replace("1 5 minutes", "15 minutes")
    line = line.replace("1 00 mg/m", "100 mg/m")
    line = line.replace("1 '", "1.")
    line = line.replace("El ", "• ")
    # Pastilles inline dans les listes à puces
    for prefix, repl in (("• O ", "• **Rang A.** "), ("• □ ", "• **Rang B.** ")):
        if line.startswith(prefix):
            line = repl + line[len(prefix):]
            break
    rank_prefix = {
        "□ ": "**Rang B.** ",
        "O ": "**Rang A.** ",
        "Q ": "**Rang A.** ",
        "D ": "**Rang B.** ",
        "S ": "**Rang B.** ",
    }
    for prefix, repl in rank_prefix.items():
        if line.startswith(prefix):
            rest = line[len(prefix):]
            # Ignore hyphenation continuations (e.g. "HV" + "G et" from HVG)
            if rest and rest[0].islower():
                break
            line = repl + rest
            break
    return line

def fix_broken_abbreviations(text):
    """Repair abbreviations corrupted by rank-marker logic or OCR line breaks."""
    fixes = [
        (r"PA\*\*Rang B\.\*\*", "PAD"),
        (r"HV\*\*Rang B\.\*\*", "HVG"),
        (r"EC\*\*Rang B\.\*\*", "ECG"),
        (r"ATC\*\*Rang B\.\*\*", "ATC"),
        (r"DF\*\*Rang B\.\*\*", "DFG"),
        (r"IP\*\*Rang B\.\*\*", "IPP"),
        (r"SAO\*\*Rang B\.\*\*", "SAOS"),
        (r"AIN\*\*Rang B\.\*\*", "AINS"),
        (r"HA\*\*Rang B\.\*\*", "HAS"),
        (r"β-hC\*\*Rang B\.\*\*", "β-hCG"),
        (r"V\*\*Rang B\.\*\*", "VG"),
        (r"B\*\*Rang B\.\*\*", "BB"),
        (r"\*\*Rang B\.\*\* et", "G et"),  # residual HVG fragments
    ]
    for pat, repl in fixes:
        text = re.sub(pat, repl, text)
    return text

def extract_body():
    text = SRC.read_text(encoding="utf-8")
    pages = re.split(r"===== PDF PAGE \d+ =====", text)
    lines_out = []
    in_body = False
    skip_until_vignette = True
    done = False

    for chunk in pages:
        if done or not chunk.strip():
            continue
        raw_lines = chunk.splitlines()
        for line in raw_lines:
            cl = clean_line(line)
            if cl is None:
                continue
            if skip_until_vignette:
                if cl.startswith("Vignette clinique"):
                    skip_until_vignette = False
                    lines_out.append("## Vignette clinique\n")
                    continue
                continue
            if any(cl.startswith(s) for s in (
                "Notions indispensables",
                "Réflexes transversalité",
                "► Entraînement",
                "Parmi les mesures hygiénodiététiques",
                "Item 339",
            )):
                done = True
                break
            for sec, hdr in SECTION_MAP.items():
                if cl.startswith(sec):
                    lines_out.append(hdr)
                    in_body = True
                    continue
            if cl.startswith("Points") and "clés" not in cl.lower():
                lines_out.append("\n\n---\n\n## Points\n")
                continue
            m = SUBSECTION_RE.match(cl)
            if m and in_body:
                lines_out.append(f"\n## {m.group(1)}\n")
                continue
            if TABLE_RE.match(cl):
                lines_out.append(f"\n**{cl.rstrip('.')}**\n")
                continue
            if cl.startswith("Fig. 4.1"):
                lines_out.append("\n![Fig. 4.1 — Associations bithérapie initiale](./img/fig_4_1_bitherapie.png)\n")
                lines_out.append(f"\n**{cl}**\n")
                continue
            if cl.startswith("- ") or cl.startswith("• "):
                lines_out.append(cl)
            elif cl.startswith("> "):
                lines_out.append(cl)
            elif len(cl) < 80 and cl.endswith(":"):
                lines_out.append(f"\n**{cl}**\n")
            else:
                lines_out.append(cl)

    return "\n".join(lines_out)

HEADER = '''# Item 224 — Hypertension artérielle de l'adulte et de l'enfant

> **Collège CNEC / SFC** · 3e édition (2025) · p. 51–81 · R2C  
> Partie I — Athérome, facteurs de risque cardiovasculaire, maladie coronarienne, artériopathie

---

## Trois repères à ne pas confondre

| Badge | Signification (R2C) |
|---|---|
| **Rang A** | Connaissances fondamentales de fin de 2e cycle |
| **Rang B** | Connaissances essentielles, plus spécialisées |
| **Rang C** | Connaissances de 3e cycle (DES) |

Les pastilles du livre (● = A, ■ = B) sont reprises inline. Un objectif sans pastille = **Rang C**. Les objectifs grisés (*) ne sont pas traités dans le corps du chapitre.

---

## Situations de départ

42 Hypertension artérielle.  
53 Hypertension durant la grossesse.  
178 Demande/prescription raisonnée et choix d'un examen diagnostique.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
201 Dyskaliémie.  
253 Prescrire des diurétiques.  
282 Prescription médicamenteuse, consultation de suivi et éducation d'un patient hypertendu.  
320 Prévention des maladies cardiovasculaires.  
328 Annonce d'une maladie chronique.  
354 Évaluation de l'observance thérapeutique.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Définition de l'HTA | |
| **B** | Prévalence, épidémiologie | Épidémiologie de l'HTA, HTA facteur de risque cardiovasculaire majeur | Prévalence, liens (âge, obésité, diabète, etc.), complications cardiovasculaires, répartition HTA essentielle et secondaire |
| **B** | Physiopathologie | Physiopathologie de l'HTA | Principaux mécanismes (rénine ou volodépendants), facteurs environnementaux |
| **A** | Diagnostic positif | Mesure de la pression artérielle | Connaître les méthodes de mesure de la PA (consultation, automesure, MAPA) et interpréter |
| **A** | Diagnostic positif | Évaluation initiale d'un patient hypertendu | Circonstances de découverte, interrogatoire, risque cardiovasculaire, examen clinique |
| **A** | Examens complémentaires | Examens complémentaires de 1re intention | Bilan biologique minimal, ECG |
| **A** | Suivi et/ou pronostic | Complications de l'HTA, retentissement sur les organes cibles | Neurosensorielles, cardiovasculaires, rénales |
| **A** | Diagnostic positif | Connaître les signes d'orientation en faveur d'une HTA secondaire | Savoir mener l'examen clinique et prescrire les examens complémentaires permettant d'évoquer une HTA secondaire |
| **A** | Étiologies | Connaître les principales causes d'HTA secondaire | Néphropathies parenchymateuses, HTA rénovasculaire, causes endocriniennes, coarctation de l'aorte, etc. |
| **B** | Diagnostic positif | Connaître la démarche diagnostique en cas de suspicion d'HTA secondaire | Clinique, biologie, imagerie |
| **A** | Identifier une urgence | Reconnaître une urgence hypertensive et une HTA maligne | Définition d'une crise hypertensive et d'une urgence hypertensive |
| **B** | Définition | Définition d'une HTA résistante | Connaître les facteurs de résistance (non-observance, sel, syndrome d'apnées du sommeil, médicaments ou substances hypertensives, etc.) |
| **A** | Prise en charge | Connaître les objectifs de la consultation d'annonce | Intérêts et objectifs de la prise en charge, modification du style de vie, prise en charge des autres facteurs de risque |
| **A** | Prise en charge | Connaître la stratégie du traitement médicamenteux de l'HTA | Traitement initial, classes thérapeutiques, adaptation, surveillance, chiffres cibles de PA |
| **A** | Prise en charge | Connaître les principaux effets indésirables et contre-indications des traitements antihypertenseurs | |
| **B** | Prise en charge | Connaître les situations cliniques particulières pouvant orienter le choix du traitement antihypertenseur | |
| **A** | Prise en charge | Connaître les particularités du traitement antihypertenseur du sujet âgé de plus de 80 ans | |
| **B** | Prise en charge | Prise en charge d'une urgence hypertensive | |
| **B** | Suivi et/ou pronostic | Plan de soins à long terme et modalités de suivi d'un patient hypertendu | Savoir évaluer l'efficacité du traitement, la tolérance au traitement et l'observance du patient |
| **A** | Prise en charge | Principes de prise en charge d'une HTA secondaire | HTA rénovasculaire et endocrinienne |
| **C*** | Définition | Connaître la définition de l'HTA chez l'enfant et l'existence de normes pédiatriques | *Non traité* |
| **C*** | Diagnostic positif | Mesure de la pression artérielle chez l'enfant | Connaître les indications de mesure de la PA chez l'enfant (examen systématique annuel après 3 ans, en cas de FDR) et en connaître les modalités (brassards adaptés, abaques pour l'âge et le sexe) · *Non traité* |
| **C*** | Étiologies | Connaître les principales causes d'HTA chez l'enfant | *Non traité* |

---

## Parcours Rang A

- [I. Définition et confirmation diagnostique](#i-définition-et-confirmation-diagnostique)
- [III. Prise en charge initiale](#iii-prise-en-charge-initiale-dun-patient-hypertendu)
- [IV. Traitement](#iv-traitement)
- [VI. HTA secondaire](#vi-hta-secondaire)
- [VII. Urgences hypertensives](#vii-urgences-hypertensives-et-hta-maligne)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Définition et confirmation diagnostique](#i-définition-et-confirmation-diagnostique)
- [II. Épidémiologie, physiopathologie et conséquences](#ii-épidémiologie-physiopathologie-et-conséquences)
- [III. Prise en charge initiale d'un patient hypertendu](#iii-prise-en-charge-initiale-dun-patient-hypertendu)
- [IV. Traitement](#iv-traitement)
- [V. Suivi du patient hypertendu](#v-suivi-du-patient-hypertendu-après-la-prise-en-charge-initiale)
- [VI. HTA secondaire](#vi-hta-secondaire)
- [VII. Urgences hypertensives et HTA maligne](#vii-urgences-hypertensives-et-hta-maligne)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/224_Hypertension_arterielle.md)

---

'''

FOOTER = '''
---

## Notions indispensables et inacceptables

### Notions indispensables

- Avant de débuter un traitement antihypertenseur, il est indispensable de confirmer le diagnostic d'HTA en dehors du cabinet médical par AMT (de préférence) ou MAPA.
- La stratégie thérapeutique dépend du niveau de PA, du niveau de risque cardiovasculaire et d'une éventuelle atteinte des organes cibles du patient.
- Le bilan minimal comprend natrémie, kaliémie, créatininémie avec estimation de la filtration glomérulaire, glycémie à jeun, exploration d'une anomalie lipidique, ECG, recherche de protéinurie sur échantillon urinaire.
- L'urgence hypertensive est une HTA sévère (grade 3) associée à une atteinte aiguë d'un organe cible.
- L'HTA maligne associe une HTA élevée et un œdème papillaire (fond d'œil stade 4) et éventuellement d'autres atteintes d'organe (insuffisance cardiaque, rénale, trouble neurologique).

### Notions inacceptables

- Ne pas mettre en place les bonnes conditions de mesures de la pression artérielle (AMT, MAPA).
- Ne pas rechercher d'éléments orientant vers une cause secondaire ou de facteurs aggravants lors de la prise en charge initiale : souffle vasculaire abdominal, triade céphalées — palpitations — sueurs, causes toxiques (réglisse ou médicaments), contraception orale, consommation d'alcool, crampes fréquentes, hypokaliémie, syndrome d'apnées du sommeil, etc.
- Ne pas atteindre les objectifs tensionnels recommandés en adaptant le traitement (bi, puis trithérapie et titration).

---

## Réflexes transversalité

- Item 222 — Facteurs de risque cardiovasculaire et prévention.
- Item 234 — Insuffisance cardiaque de l'adulte.
- Item 263 — Néphropathie vasculaire.
- Item 264 — Insuffisance rénale chronique chez l'adulte et l'enfant.
- Item 340 — Accidents vasculaires cérébraux.

---

## Entraînement

Questions isolées et corrigés : [Entrainement/QI/224_Hypertension_arterielle.md](../../Entrainement/QI/224_Hypertension_arterielle.md)
'''

def main():
    body = extract_body()
    # post-process: merge broken paragraphs (lines not starting with special chars)
    paragraphs = []
    buf = []
    for line in body.splitlines():
        if not line.strip():
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append("")
            continue
        if line.startswith(("#", "##", "**", "-", "•", ">", "!", "|", "---")):
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append(line)
        else:
            buf.append(line.strip())
    if buf:
        paragraphs.append(" ".join(buf))
    # collapse excessive blank lines
    cleaned_body = "\n\n".join(p for p in paragraphs if p is not None)
    cleaned_body = re.sub(r"\n{3,}", "\n\n", cleaned_body)
    cleaned_body = re.sub(r"(?m)^•\s*\n\n", "• ", cleaned_body)
    cleaned_body = fix_broken_abbreviations(cleaned_body)

    OUT.write_text(HEADER + cleaned_body + FOOTER, encoding="utf-8")
    print(f"Written {OUT} ({OUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
