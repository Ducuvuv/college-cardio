# -*- coding: utf-8 -*-
"""Generate item 230 markdown from extracted PDF text."""
import re
from pathlib import Path

SRC = Path(r"C:\Users\gestu\Documents\college cardio\_tmp_item230.txt")
OUT = Path(r"C:\Users\gestu\Documents\college cardio\Cours\I_Atherome\230_Douleur_thoracique_aigue.md")

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"Connaissances\s*$",
    r"^\d{1,3}\s*$",
    r"^Athérome, facteurs de risque.*$",
    r"^Item 230.*$",
    r"^► Entraînement.*",
    r"^Les corrigés sont.*",
    r"^Détresse vitale\?$",
    r"^Réanimation, Usic$",
    r"^S/ oui$",
    r"^Via Samu$",
    r"^dés\s*$",
]

SECTION_MAP = {
    "I. Conduite à tenir en présence d'un patient": "# I. Conduite à tenir en présence d'un patient qui consulte pour douleur thoracique\n\n**Rang A.**",
    "II. Orientation diagnostique : identifier les urgences": "\n\n---\n\n# II. Orientation diagnostique : identifier les urgences cardiaques\n\n**Rang A** · **Rang B**.",
    "III. Orientation diagnostique : douleurs chroniques": "\n\n---\n\n# III. Orientation diagnostique : douleurs chroniques de cause cardiaque\n\n**Rang A** · **Rang B**.",
    "IV. Orientation diagnostique : principales causes": "\n\n---\n\n# IV. Orientation diagnostique : principales causes extracardiaques d'une douleur thoracique\n\n**Rang A** · **Rang B**.",
}

FIG_MAP = {
    "Fig. 6.1": ("fig_6_1_conduite_douleur.png", "Fig. 6.1 — Conduite à tenir devant une douleur thoracique"),
}

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")

def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    line = line.replace("El ", "• ")
    line = line.replace("1 2 dérivations", "12 dérivations")
    line = line.replace("1 5", "15")
    line = line.replace("ECC ", "ECG ")
    line = line.replace("Usic", "USIC")
    line = line.replace("EVA", "EVA")
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

    for chunk in pages:
        if done or not chunk.strip():
            continue
        for line in chunk.splitlines():
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
                "O QRM 1",
                "O QRU 2",
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
            if cl.startswith("Points") or cl == "motif très fréquent":
                lines_out.append("\n\n---\n\n## Points\n")
                if cl.startswith("Points"):
                    continue
            if cl.startswith("La douleur thoracique est un"):
                lines_out.append("• La douleur thoracique est un motif très fréquent de recours aux soins soit aux urgences, soit en consultation.")
                continue
            m = SUBSECTION_RE.match(cl)
            if m and in_body:
                lines_out.append(f"\n## {m.group(1)}\n")
                continue
            m2 = NUM_SUBSECTION_RE.match(cl)
            if m2 and in_body and len(cl) < 90:
                lines_out.append(f"\n### {m2.group(1)}\n")
                continue
            fig_handled = False
            for fig_key, (fname, caption) in FIG_MAP.items():
                if fig_key.lower() in cl.lower() or cl.startswith("Fig. 6"):
                    if "synthétisée" in cl or cl.startswith("Fig. 6"):
                        lines_out.append(f"\n![{caption}](./img/{fname})\n")
                        if cl.startswith("Fig."):
                            lines_out.append(f"\n**{cl}**\n")
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

HEADER = '''# Item 230 — Douleur thoracique aiguë

> **Collège CNEC / SFC** · 3e édition (2025) · p. 121–133 · R2C  
> Partie I — Athérome, facteurs de risque cardiovasculaire, maladie coronarienne, artériopathie

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

161 Douleur thoracique.  
162 Dyspnée.  
178 Demande/prescription raisonnée et choix d'un examen diagnostique.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
203 Élévation de la protéine C-réactive (CRP).  
204 Élévation des enzymes cardiaques.  
259 Évaluation et prise en charge de la douleur aiguë.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Savoir définir une douleur thoracique aiguë | |
| **A** | Identifier une urgence | Savoir rechercher une détresse vitale devant une douleur thoracique | Détresse respiratoire ou hémodynamique, troubles de la conscience |
| **A** | Identifier une urgence | Identifier les signes de gravité imposant des décisions thérapeutiques immédiates | |
| **A** | Diagnostic positif | Savoir évoquer les 4 urgences cardiovasculaires devant une douleur thoracique | Dissection aortique, SCA, péricardite avec tamponnade, embolie pulmonaire |
| **A** | Diagnostic positif | Connaître la sémiologie clinique fonctionnelle et physique de la dissection aortique | |
| **A** | Diagnostic positif | Connaître la démarche diagnostique des 4 urgences cardiovasculaires | Terrain, caractéristiques de la douleur, examen clinique |
| **A** | Examens complémentaires | Anomalies ECG des 4 urgences cardiovasculaires | |
| **A** | Examens complémentaires | Place et anomalies de la radiographie thoracique | |
| **A** | Examens complémentaires | Examens biologiques et interprétation | |
| **B** | Examens complémentaires | Place de la coronarographie et principes de prise en charge du SCA | |
| **B** | Examens complémentaires | Place de l'échocardiographie, ETO et scanner thoracique dans la dissection aortique | |
| **C*** | Étiologies | Devant un angor d'effort, principales causes d'angor fonctionnel | *Non traité* |
| **C*** | Étiologies | Principales causes thoraciques de douleur aiguë hors 4 urgences CV | *Non traité* |
| **C*** | Étiologies | Principales causes extrathoraciques | *Non traité* |

---

## Parcours Rang A

- [I. Conduite à tenir](#i-conduite-à-tenir-en-présence-dun-patient-qui-consulte-pour-douleur-thoracique)
- [II. Urgences cardiaques (PIED)](#ii-orientation-diagnostique--identifier-les-urgences-cardiaques)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Conduite à tenir](#i-conduite-à-tenir-en-présence-dun-patient-qui-consulte-pour-douleur-thoracique)
- [II. Urgences cardiaques](#ii-orientation-diagnostique--identifier-les-urgences-cardiaques)
- [III. Douleurs chroniques cardiaques](#iii-orientation-diagnostique--douleurs-chroniques-de-cause-cardiaque)
- [IV. Causes extracardiaques](#iv-orientation-diagnostique--principales-causes-extracardiaques-dune-douleur-thoracique)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/230_Douleur_thoracique_aigue.md)

---

'''

FOOTER = '''
---

## Notions indispensables et inacceptables

### Notions indispensables

- Devant une douleur thoracique aiguë, toujours éliminer en premier une détresse vitale.
- Puis éliminer les urgences cardiaques (PIED : péricardite, infarctus, embolie pulmonaire, dissection aortique).

### Notions inacceptables

- Faire un dosage de la troponine avant de réaliser un ECG.

---

## Réflexes transversalité

- Item 226 — Thrombose veineuse profonde et embolie pulmonaire.
- Item 235 — Péricardite aiguë.
- Item 339 — Syndromes coronariens aigus.

---

## Entraînement

Questions isolées et corrigés : [Entrainement/QI/230_Douleur_thoracique_aigue.md](../../Entrainement/QI/230_Douleur_thoracique_aigue.md)
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
        if line.startswith(("#", "##", "###", "**", "-", "•", ">", "!", "|", "---")):
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
    # Insert figure after mention of figure 6.1
    if "figure 6.1" in cleaned and "fig_6_1" not in cleaned:
        cleaned = cleaned.replace(
            "figure 6.1 .",
            "figure 6.1.\n\n![Fig. 6.1 — Conduite à tenir devant une douleur thoracique](./img/fig_6_1_conduite_douleur.png)",
        )
    OUT.write_text(HEADER + cleaned + FOOTER, encoding="utf-8")
    print(f"Written {OUT} ({OUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
