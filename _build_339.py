# -*- coding: utf-8 -*-
"""Generate item 339 markdown from extracted PDF text."""
import re
from pathlib import Path

SRC = Path(r"C:\Users\gestu\Documents\college cardio\_tmp_item339.txt")
OUT = Path(r"C:\Users\gestu\Documents\college cardio\Cours\I_Atherome\339_SCA_angor_stable.md")

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^\d{1,3}\s*$",
    r"^Athérome, facteurs de risque.*$",
    r"^Item 339.*$",
    r"^5\s*$",
    r"^► Entraînement.*",
    r"^► Compléments.*",
    r"^Les corrigés sont.*",
    r"^Vidéo 5\..*",
    r"^Des compléments numériques.*",
    r"^par des flashcodes.*",
    r"^consulte\.com.*",
    r"^jî 'n.*",
    r"^iPaiîfe.*",
    r"^H Hffl.*",
    r"^à l'entraînement.*",
    r"^\*\"$",
    r"^PS '.*",
]

SECTION_MAP = {
    "I. Définitions": "# I. Définitions\n\n**Rang A.**",
    "II. Épidémiologie": "\n\n---\n\n# II. Épidémiologie\n\n**Rang A.**",
    "III. Physiopathologie": "\n\n---\n\n# III. Physiopathologie\n\n**Rang A** · **Rang B**.",
    "IV. Diagnostic": "\n\n---\n\n# IV. Diagnostic\n\n**Rang A** · **Rang B**.",
    "V. Traitement": "\n\n---\n\n# V. Traitement\n\n**Rang A** · **Rang B**.",
    "VI. Évolution et complications": "\n\n---\n\n# VI. Évolution et complications\n\n**Rang A** · **Rang B**.",
    "VII. Prise en charge au long cours": "\n\n---\n\n# VII. Prise en charge au long cours après hospitalisation pour un SCA\n\n**Rang A** · **Rang B**.",
    "VIII. Angor stable": "\n\n---\n\n# VIII. Angor stable\n\n**Rang A** · **Rang B**.",
}

FIG_MAP = {
    "Fig. 5.2": ("fig_5_2_idm_inferieur.png", "Fig. 5.2 — Tracés IDM ST+ inférieur"),
    "Fig. 5.3": ("fig_5_3_ondes_t.png", "Fig. 5.3 — Ondes T négatives antéro-septo-apicales"),
    "Fig. 5.5": ("fig_5_5_reperfusion.png", "Fig. 5.5 — Stratégie de reperfusion SCA ST+"),
    "Fig. 5.6": ("fig_5_6_ecg_effort.png", "Fig. 5.6 — ECG d'effort"),
    "Fig. 5.7": ("fig_5_7_scintigraphie.png", "Fig. 5.7 — Scintigraphie myocardique au thallium"),
    "Fig. 5.8": ("fig_5_8_coronarographie.png", "Fig. 5.8 — Coronarographie"),
    "Fig. 5.9": ("fig_5_9_coroscanner.png", "Fig. 5.9 — Scanner coronarien 3D"),
}

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")
TABLE_RE = re.compile(r"^Tableau 5\.\d")

def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    if line.startswith("G ") and len(line) > 2 and line[2].isupper():
        line = "**Rang A.** " + line[2:]
    line = line.replace("SCAST+", "SCA ST+")
    line = line.replace("SCANST", "SCA NST")
    line = line.replace("IDMNST", "IDMNST")
    line = line.replace("STEMI", "STEMI")
    line = line.replace("El ", "• ")
    line = line.replace("& ", "**Rang A.** ")
    for prefix, repl in (("• O ", "• **Rang A.** "), ("• □ ", "• **Rang B.** "), ("• Q ", "• **Rang A.** ")):
        if line.startswith(prefix):
            line = repl + line[len(prefix):]
            break
    rank_prefix = {
        "□ ": "**Rang B.** ",
        "O ": "**Rang A.** ",
        "Q ": "**Rang A.** ",
    }
    for prefix, repl in rank_prefix.items():
        if line.startswith(prefix):
            rest = line[len(prefix):]
            if rest and rest[0].islower():
                break
            line = repl + rest
            break
    return line

def fix_broken_abbreviations(text):
    fixes = [
        (r"EC\*\*Rang A\.\*\*", "ECG"),
        (r"ID\*\*Rang A\.\*\*", "IDM"),
        (r"SC\*\*Rang A\.\*\*", "SCA"),
        (r"T\*\*Rang A\.\*\*", "TNT"),
    ]
    for pat, repl in fixes:
        text = re.sub(pat, repl, text)
    return text

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
                "► Compléments",
                "O QRM 1",
                "Item 230",
            )):
                done = True
                break
            matched_sec = False
            for sec, hdr in SECTION_MAP.items():
                if cl.startswith(sec):
                    lines_out.append(hdr)
                    in_body = True
                    matched_sec = True
                    break
            if matched_sec:
                continue
            if cl.startswith("Points") and "clés" not in cl.lower():
                lines_out.append("\n\n---\n\n## Points\n")
                continue
            m = SUBSECTION_RE.match(cl)
            if m and in_body:
                lines_out.append(f"\n## {m.group(1)}\n")
                continue
            m2 = NUM_SUBSECTION_RE.match(cl)
            if m2 and in_body and len(cl) < 90:
                lines_out.append(f"\n### {m2.group(1)}\n")
                continue
            if TABLE_RE.match(cl):
                lines_out.append(f"\n**{cl.rstrip('.')}**\n")
                continue
            fig_handled = False
            for fig_key, (fname, caption) in FIG_MAP.items():
                if cl.startswith(fig_key):
                    lines_out.append(f"\n![{caption}](./img/{fname})\n")
                    cap = re.sub(r"^Fig\. 5\.\d+\.?\s*[0-9OD]?\s*", "Fig. ", cl)
                    lines_out.append(f"\n**{cap}**\n")
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

HEADER = '''# Item 339 — Syndromes coronariens aigus et angor stable

> **Collège CNEC / SFC** · 3e édition (2025) · p. 82–120 · R2C  
> Partie I — Athérome, facteurs de risque cardiovasculaire, maladie coronarienne, artériopathie

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

4 Douleur abdominale.  
42 Hypertension artérielle.  
50 Malaise/perte de connaissance.  
159 Bradycardie.  
161 Douleur thoracique.  
162 Dyspnée.  
165 Palpitations.  
166 Tachycardie.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
204 Élévation des enzymes cardiaques.  
208 Hyperglycémie.  
231 Demande d'un examen d'imagerie.  
239 Explication préopératoire et recueil de consentement d'un geste invasif diagnostique ou thérapeutique.  
247 Prescription d'une rééducation.  
248 Prescription et suivi d'un traitement anticoagulant et/ou antiagrégant.  
252 Prescription d'un hypolipémiant.  
259 Évaluation et prise en charge de la douleur aiguë.  
285 Consultation de suivi et éducation thérapeutique d'un patient avec un antécédent cardiovasculaire.  
314 Prévention des risques liés au tabac.  
316 Identifier les conséquences d'une pathologie/situation sur le maintien d'un emploi.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Connaître la définition de l'infarctus du myocarde | |
| **A** | Définition | Connaître la définition d'un syndrome coronarien aigu (SCA) non ST+ et ST+ | |
| **A** | Épidémiologie | Connaître la prévalence du SCA et sa mortalité | |
| **B** | Physiopathologie | Connaître la physiopathologie des SCA (NST et ST+) et de l'angor stable | |
| **A** | Diagnostic positif | Connaître les éléments de l'interrogatoire et de l'examen clinique d'une douleur angineuse et ses présentations atypiques, du SCA et de ses complications | |
| **A** | Diagnostic positif | Connaître les signes électrocardiographiques d'un SCA ST+ et confirmer sa localisation ; connaître les signes électrocardiographiques d'un SCA NST | |
| **A** | Examens complémentaires | Connaître les indications de l'ECG devant toute douleur thoracique ou suspicion de SCA ; connaître les indications et interpréter le dosage de la troponine | |
| **B** | Examens complémentaires | Connaître l'apport de la coronarographie et du coroscanner | |
| **A** | Identifier une urgence | Reconnaître l'urgence et savoir appeler (SAMU-Centre 15 en extrahospitalier) en cas de douleur thoracique | |
| **A** | Prise en charge | Connaître les modalités de revascularisation coronarienne | |
| **A** | Prise en charge | Connaître les principes et stratégie thérapeutiques depuis la prise en charge par le SAMU du SCA ST+, du SCA NST, de l'angor stable | |
| **B** | Prise en charge | Connaître les principes de la stratégie thérapeutique au long cours devant un angor stable | |

*Note du livre : l'angor stable est traité à part en fin de chapitre (section VIII).*

---

## Parcours Rang A

- [I. Définitions](#i-définitions)
- [II. Épidémiologie](#ii-épidémiologie)
- [III. Physiopathologie](#iii-physiopathologie)
- [IV. Diagnostic](#iv-diagnostic)
- [V. Traitement](#v-traitement)
- [VI. Évolution et complications](#vi-évolution-et-complications)
- [VII. Prise en charge au long cours](#vii-prise-en-charge-au-long-cours-après-hospitalisation-pour-un-sca)
- [VIII. Angor stable](#viii-angor-stable)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Définitions](#i-définitions)
- [II. Épidémiologie](#ii-épidémiologie)
- [III. Physiopathologie](#iii-physiopathologie)
- [IV. Diagnostic](#iv-diagnostic)
- [V. Traitement](#v-traitement)
- [VI. Évolution et complications](#vi-évolution-et-complications)
- [VII. Prise en charge au long cours](#vii-prise-en-charge-au-long-cours-après-hospitalisation-pour-un-sca)
- [VIII. Angor stable](#viii-angor-stable)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/339_SCA_angor_stable.md)

---

'''

FOOTER = '''
---

## Notions indispensables et inacceptables

### Notions indispensables

- Devant toute douleur thoracique aiguë, un ECG doit être réalisé en urgence (dans les 10 minutes).
- Le diagnostic d'IDM repose sur une élévation de la troponine au-dessus du 99e percentile avec au moins un critère associé (symptômes, ECG, imagerie ou thrombus en coronarographie).
- Le SCA ST+ impose une reperfusion coronarienne urgente (angioplastie primaire ou fibrinolyse).
- Le SCA NST avec troponine élevée relève d'une stratégie de revascularisation selon le risque (immédiat, précoce ou différé).

### Notions inacceptables

- Retarder l'ECG ou la prise en charge d'un SCA ST+.
- Ne pas interpréter le dosage de troponine dans son contexte clinique et temporel (courbe, heure de début des symptômes).
- Omettre la double antiagrégation plaquettaire et l'anticoagulation dans le SCA.

---

## Réflexes transversalité

- Item 221 — Athérome : épidémiologie et physiopathologie. Le malade polyathéromateux.
- Item 222 — Facteurs de risque cardiovasculaire et prévention.
- Item 223 — Dyslipidémies.
- Item 230 — Douleur thoracique aiguë.

---

## Entraînement

Questions isolées et corrigés : [Entrainement/QI/339_SCA_angor_stable.md](../../Entrainement/QI/339_SCA_angor_stable.md)
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
    cleaned_body = "\n\n".join(p for p in paragraphs if p is not None)
    cleaned_body = re.sub(r"\n{3,}", "\n\n", cleaned_body)
    cleaned_body = re.sub(r"(?m)^•\s*\n\n", "• ", cleaned_body)
    cleaned_body = fix_broken_abbreviations(cleaned_body)

    OUT.write_text(HEADER + cleaned_body + FOOTER, encoding="utf-8")
    print(f"Written {OUT} ({OUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
