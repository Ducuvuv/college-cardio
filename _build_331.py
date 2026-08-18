# -*- coding: utf-8 -*-
"""Generate item 331 markdown from extracted PDF text."""
import re
from pathlib import Path

SRC = Path(r"C:\Users\gestu\Documents\college cardio\_tmp_item331.txt")
OUT = Path(r"C:\Users\gestu\Documents\college cardio\Cours\VI_Divers\331_Arret_cardiocirculatoire.md")

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Médecine cardiovasculaire\s*$",
    r"^Divers\s*$",
    r"^CHAPITRE\s*$",
    r"^21\s*$",
    r"^w Item 331\s*$",
    r"^Arrêt cardiocirculatoire\s*$",
    r"^\d{3}\s*$",
    r"^Item 331.*$",
    r"^► Entraînement.*",
    r"^Les corrigés sont.*",
    r"^Pour en savoir plus\s*$",
    r"^Bornstein K.*",
    r"^Monsieurs KG.*",
    r"^PerkinsGD.*",
    r"^Soar J.*",
    r"^Trulhar A.*",
    r"^Source : Reynolds.*",
    r"^resuscitation\. Circulation.*",
    r"^2SN$",
    r"^Uhflflfl.*",
    r"^10:24:43.*",
    r"^W:22:23.*",
]

SECTION_MAP = {
    "I. Définitions": "\n\n# I. Définitions\n\n**Rang A.**",
    "II. Notions de chaîne de survie": "\n\n---\n\n# II. Notions de chaîne de survie, défibrillation\n\n**Rang A** · **Rang B**.",
    "III. Étiologies": "\n\n---\n\n# III. Étiologies\n\n**Rang A** · **Rang B**.",
    "IV. Diagnostic": "\n\n---\n\n# IV. Diagnostic\n\n**Rang A.**",
    "V. Conduite à tenir en pratique": "\n\n---\n\n# V. Conduite à tenir en pratique\n\n**Rang A** · **Rang B**.",
    "VI. Pronostic et survie à la phase préhospitalière": "\n\n---\n\n# VI. Pronostic et survie à la phase préhospitalière\n\n**Rang A** · **Rang B**.",
    "VII. Conditionnement hospitalier": "\n\n---\n\n# VII. Conditionnement hospitalier et pronostic à la phase hospitalière\n\n**Rang A** · **Rang B**.",
}

FIG_MAP = {
    "Fig. 21.1": ("fig_21_1_survie_rcp.png", "Fig. 21.1 — Probabilité de survie en fonction de la durée de la RCP"),
    "Fig. 21.2": ("fig_21_2_pronostic_chocable.png", "Fig. 21.2 — Amélioration du pronostic (rythme chocable, témoin)"),
    "Fig. 21.5": ("fig_21_5_asystolie.png", "Fig. 21.5 — Exemple d'ECG d'asystolie"),
    "Fig. 21.7": ("fig_21_7_ecg_fv.png", "Fig. 21.7 — ECG (FV)"),
}

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")
ENCADRE_RE = re.compile(r"^Encadré 21\.\d")

def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    if re.match(r"^[0-9%\.]+$", line):
        return None
    if re.match(r"^(Probaility|CPR Duration|Bystander|Witnessed|Non-shockable|Unwitnessed|W<tnes|Ufwtnesied|Probaility|Proballlty|Ql\(n\)|Q2\(n\)|Q3\(n\)|Q4\(n\)|Shockable|CPR Duration)", line):
        return None
    line = line.replace("El ", "• ")
    line = line.replace("1 0 ", "10 ")
    line = line.replace("1 5", "15")
    line = line.replace("1 50 ", "150 ")
    line = line.replace("1 00/", "100/")
    line = line.replace("rw-flow", "no-flow")
    line = line.replace("Jow-flow", "low-flow")
    line = line.replace("dAC", "d'AC")
    line = line.replace("AC R", "ACR")
    line = line.replace("RC P", "RCP")
    line = line.replace("MCE", "MCE")
    line = line.replace("CEE", "CEE")
    line = line.replace("DSA", "DSA")
    line = line.replace("Smur", "SMUR")
    line = line.replace("fig. 21 .", "fig. 21.")
    for prefix, repl in (("• O ", "• **Rang A.** "), ("• □ ", "• **Rang B.** ")):
        if line.startswith(prefix):
            line = repl + line[len(prefix):]
            break
    rank_prefix = {
        "□ ": "**Rang B.** ",
        "O ": "**Rang A.** ",
    }
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
    skip_until_vignette = True
    done = False
    in_body = False
    in_encadre = False

    for chunk in pages:
        if done or not chunk.strip():
            continue
        for line in chunk.splitlines():
            cl = clean_line(line)
            if cl is None:
                continue
            if skip_until_vignette:
                if cl.startswith("Vignette clinique") or cl.startswith("Vous êtes de garde"):
                    skip_until_vignette = False
                    lines_out.append("## Vignette clinique\n")
                    if cl.startswith("Vous"):
                        lines_out.append(cl)
                    continue
                continue
            if any(cl.startswith(s) for s in (
                "Notions indispensables",
                "Réflexes transversalité",
                "► Entraînement",
                "Pour en savoir plus",
                "O QRM 1",
                "M. X,",
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
            if cl.startswith("Points"):
                lines_out.append("\n\n---\n\n## Points\n")
                continue
            if cl == "pas synonyme de survie.":
                lines_out.append("• La récupération d'une activité circulatoire efficace n'est pas synonyme de survie.")
                continue
            if ENCADRE_RE.match(cl):
                lines_out.append(f"\n### {cl}\n")
                in_encadre = True
                continue
            m = SUBSECTION_RE.match(cl)
            if m and in_body and not in_encadre:
                lines_out.append(f"\n## {m.group(1)}\n")
                continue
            m2 = NUM_SUBSECTION_RE.match(cl)
            if m2 and in_body and len(cl) < 90:
                lines_out.append(f"\n### {m2.group(1)}\n")
                continue
            fig_handled = False
            for fig_key, (fname, caption) in FIG_MAP.items():
                if fig_key.lower() in cl.lower() and ("fig" in cl.lower() or "probabilité" in cl.lower() or "amélioration" in cl.lower() or "asystolie" in cl.lower() or "ECG" in cl):
                    if cl.startswith("Fig."):
                        lines_out.append(f"\n![{caption}](./img/{fname})\n")
                        cap = re.sub(r"^Fig\. 21\.\d+\.?\s*[0-9ODEl]?\s*", "Fig. ", cl)
                        lines_out.append(f"\n**{cap}**\n")
                        fig_handled = True
                        break
                    if f"(fig. {fig_key.split()[-1].lower()}" in cl.lower() or f"fig. {fig_key.split()[-1].lower()}" in cl.lower():
                        lines_out.append(f"\n![{caption}](./img/{fname})\n")
                        fig_handled = True
                        break
            if fig_handled:
                continue
            if cl.startswith("Les arrêts cardiaques") or cl.startswith("L'arrêt cardiaque"):
                if not any("Les arrêts" in x or "L'arrêt cardiaque" in x for x in lines_out[-3:]):
                    lines_out.append(cl)
                continue
            if cl.startswith("- ") or cl.startswith("• "):
                lines_out.append(cl)
            elif cl.startswith("> "):
                lines_out.append(cl)
            elif cl.startswith(">") and not cl.startswith("> "):
                lines_out.append("> " + cl[1:].strip())
            elif len(cl) < 80 and cl.endswith(":") and in_body:
                lines_out.append(f"\n**{cl}**\n")
            else:
                lines_out.append(cl)
        if done:
            break
    return "\n".join(lines_out)

HEADER = '''# Item 331 — Arrêt cardiocirculatoire

> **Collège CNEC / SFC** · 3e édition (2025) · p. 511–528 · R2C  
> Partie VI — Divers

---

## Trois repères à ne pas confondre

| Badge | Signification (R2C) |
|---|---|
| **Rang A** | Connaissances fondamentales de fin de 2e cycle |
| **Rang B** | Connaissances essentielles, plus spécialisées |
| **Rang C** | Connaissances de 3e cycle (DES) |

Les pastilles du livre (● = A, ■ = B) sont reprises inline. Objectifs grisés (*) non traités dans le corps.

---

## Situations de départ

28 Coma et troubles de conscience (diagnostic différentiel).  
38 État de mort apparente.  
50 Malaise/perte de connaissance.  
159 Bradycardie.  
160 Détresse respiratoire aiguë.  
161 Douleur thoracique.  
165 Palpitations.  
166 Tachycardie.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Définir un arrêt cardiocirculatoire | Définition OMS ; diagnostic positif = absence de réponse + ventilation inefficace |
| **A** | Définition | Définir la chaîne de survie | Maillons de la chaîne de survie |
| **B** | Prévalence, épidémiologie | Incidence et pronostic de l'AC chez l'adulte et l'enfant | *Enfant non traité* |
| **A** | Étiologies | Principales étiologies d'AC | Prééminence de l'origine coronarienne |
| **A** | Définition | No-flow et low-flow | |
| **A** | Prise en charge | Ventilation de base | Canule de Guedel ; ventilation adulte vs enfant |
| **A** | Prise en charge | Algorithme universel de RCP de l'adulte | |
| **B** | Prise en charge | Scope/défibrillateur manuel ou semi-automatique | Rythmes chocables, DEM, asystolies |
| **B** | Prise en charge | Voies d'abord vasculaires d'urgence | Veineuse périphérique, intra-artérielle |
| **B** | Prise en charge | Adrénaline (rythme chocable) | Indications, posologie, séquence ; amiodarone |
| **B** | Prise en charge | Traitements médicamenteux de la RCP | |
| **B** | Prise en charge | Diagnostic et traitement étiologique | Causes réversibles ; coronarographie |
| **A** | Prise en charge | Critères d'arrêt de la réanimation | |
| **A*** | Prise en charge | Algorithme RCP de l'enfant | *Non traité* |
| **A*** | Identifier une urgence | ACR chez l'enfant : épidémiologie et mécanisme | *Non traité* |
| **A*** | Prise en charge | Principes ACR de l'enfant (premières minutes) | *Non traité* |

---

## Parcours Rang A

- [I. Définitions (no-flow, low-flow)](#i-définitions)
- [IV. Diagnostic](#iv-diagnostic)
- [V. Conduite à tenir (ACD, RCP)](#v-conduite-à-tenir-en-pratique)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Définitions](#i-définitions)
- [II. Chaîne de survie, défibrillation](#ii-notions-de-chaîne-de-survie-défibrillation)
- [III. Étiologies](#iii-étiologies)
- [IV. Diagnostic](#iv-diagnostic)
- [V. Conduite à tenir](#v-conduite-à-tenir-en-pratique)
- [VI. Pronostic préhospitalier](#vi-pronostic-et-survie-à-la-phase-préhospitalière)
- [VII. Pronostic hospitalier](#vii-conditionnement-hospitalier-et-pronostic-à-la-phase-hospitalière)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/331_Arret_cardiocirculatoire.md)

---

'''

FOOTER = '''
---

## Notions indispensables et inacceptables

### Notions indispensables

- La cause la plus fréquente des AC est la FV survenant au cours des cardiopathies ischémiques (SCA récent ou séquelles d'infarctus).
- Pronostic et chances de survie sans séquelle faibles au-delà de 5 minutes de no-flow.
- Les DSA permettent de délivrer un CEE en cas d'AC « chocable » (TV ou FV).

### Notions inacceptables

- Ne pas connaître les mesures de survie ACD (libération des voies aériennes, massage cardiaque, défibrillation).

---

## Réflexes transversalité

- Item 14 — La mort.
- Item 201 — Transplantation d'organes ; prélèvements d'organes et législation.
- Item 230 — Douleur thoracique aiguë.
- Item 231 — Électrocardiogramme : indications et interprétations.
- Item 236 — Troubles de la conduction intracardiaque.
- Item 237 — Palpitations.
- Item 332 — État de choc.
- Item 339 — Syndromes coronariens aigus.

---

## Entraînement

Questions isolées et corrigés : [Entrainement/QI/331_Arret_cardiocirculatoire.md](../../Entrainement/QI/331_Arret_cardiocirculatoire.md)
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
    cleaned = cleaned.replace("puis et procéder", "puis procéder")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(HEADER + cleaned + FOOTER, encoding="utf-8")
    print(f"Written {OUT} ({OUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
