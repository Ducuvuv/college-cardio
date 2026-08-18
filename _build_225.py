# -*- coding: utf-8 -*-
"""Generate item 225 markdown from extracted PDF text."""
import re
from pathlib import Path

SRC = Path(r"C:\Users\gestu\Documents\college cardio\_tmp_item225.txt")
OUT = Path(r"C:\Users\gestu\Documents\college cardio\Cours\I_Atherome\225_Arteriopathie_AOMI_anevrismes.md")

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^\d{1,3}\s*$",
    r"^Athérome, facteurs de risque.*$",
    r"^Item 225.*$",
    r"^Médecine cardiovasculaire\s*$",
    r"^► Entraînement.*",
    r"^Les corrigés sont.*",
    r"^a\s*$",
    # "clés" = début section Points (page 187)
    r"^Les corrigés sont.*",
    r"^Aman».*",
]

SECTION_MAP = {
    "I. Artériopathie de l'aorte et des artères viscérales": "# I. Artériopathie de l'aorte et des artères viscérales\n\n**Rang A** · **Rang B**.",
    "II. Artériopathie oblitérante des membres inférieurs": "\n\n---\n\n# II. Artériopathie oblitérante des membres inférieurs (AOMI)\n\n**Rang A** · **Rang B**.",
    "III. Ischémie aiguë des membres inférieurs": "\n\n---\n\n# III. Ischémie aiguë des membres inférieurs\n\n**Rang A** · **Rang B**.",
    "IV. Anévrismes": "\n\n---\n\n# IV. Anévrismes\n\n**Rang A** · **Rang B**.",
}

FIG_MAP = {
    "Fig. 7.2": ("fig_7_2_echodoppler.png", "Fig. 7.2 — Échodoppler"),
    "Fig. 7.3": ("fig_7_3_angioscanner.png", "Fig. 7.3 — Angioscanner"),
    "Fig. 7.4": ("fig_7_4_angio_irm.png", "Fig. 7.4 — Angio-IRM"),
    "Fig. 7.5": ("fig_7_5_arteriographie.png", "Fig. 7.5 — Artériographie numérisée"),
    "Fig. 7.6": ("fig_7_6_claudication.png", "Fig. 7.6 — Prise en charge de la claudication intermittente"),
    "Fig. 7.7": ("fig_7_7_ischemie_aigue.png", "Fig. 7.7 — Prise en charge de l'ischémie aiguë"),
    "Fig. 7.9": ("fig_7_9_aaa_scanner.png", "Fig. 7.9 — Angioscanner aortique abdominal"),
}

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")
TABLE_RE = re.compile(r"^Tableau 7\.\d")

def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    line = line.replace("1'1PS", "IPS")
    line = line.replace("l'1PS", "IPS")
    line = line.replace("1' IPS", "IPS")
    line = line.replace(" de 1'1PS", " de l'IPS")
    line = line.replace(" mesures de 1'1PS", " mesures de l'IPS")
    line = line.replace("Unfibrate", "Un fibrate")
    line = line.replace("2-5 %o", "2-5 ‰")
    line = line.replace("Énolisme", "Énolisme")  # keep
    line = line.replace("0 Les AP", "**Rang A.** Les AP")
    line = line.replace("El ", "• ")
    line = line.replace("& ", "**Rang A.** ")
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
            if rest and rest[0].islower():
                break
            line = repl + rest
            break
    return line

def fix_broken_abbreviations(text):
    fixes = [
        (r"IP\*\*Rang B\.\*\*", "IPP"),
        (r"ATC\*\*Rang B\.\*\*", "ATC"),
        (r"AAA\*\*Rang B\.\*\*", "AAA"),
        (r"AOMI\*\*Rang B\.\*\*", "AOMI"),
        (r"EC\*\*Rang B\.\*\*", "ECG"),
        (r"DF\*\*Rang B\.\*\*", "DFG"),
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
    in_points = False

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
                "O QRU 1",
                "O QRM 2",
                "Item 226",
                "Maladies des valves",
            )):
                done = True
                break
            for sec, hdr in SECTION_MAP.items():
                if cl.startswith(sec):
                    lines_out.append(hdr)
                    in_body = True
                    in_points = False
                    continue
            if cl == "clés" or cl.startswith("Points clés"):
                lines_out.append("\n\n---\n\n## Points\n")
                in_points = True
                continue
            if in_points and cl in (
                "Artériopathie de l'aorte et des artères viscérales",
                "Artériopathie oblitérante des membres inférieurs (AOMI)",
                "Ischémie aiguë des membres inférieurs",
                "Anévrisme de l'aorte abdominale (AAA)",
            ):
                lines_out.append(f"\n### {cl}\n")
                continue
            m = SUBSECTION_RE.match(cl)
            if m and in_body and not in_points:
                lines_out.append(f"\n## {m.group(1)}\n")
                continue
            m2 = NUM_SUBSECTION_RE.match(cl)
            if m2 and in_body and not in_points and len(cl) < 80:
                lines_out.append(f"\n### {m2.group(1)}\n")
                continue
            if TABLE_RE.match(cl):
                lines_out.append(f"\n**{cl.rstrip('.')}**\n")
                continue
            for fig_key, (fname, caption) in FIG_MAP.items():
                if cl.startswith(fig_key):
                    lines_out.append(f"\n![{caption}](./img/{fname})\n")
                    cap = re.sub(r"^Fig\. 7\.\d+\.?\s*0?\s*", "Fig. ", cl)
                    lines_out.append(f"\n**{cap}**\n")
                    break
            else:
                if cl.startswith("- ") or cl.startswith("• "):
                    lines_out.append(cl)
                elif cl.startswith("> "):
                    lines_out.append(cl)
                elif len(cl) < 80 and cl.endswith(":") and not in_points:
                    lines_out.append(f"\n**{cl}**\n")
                else:
                    lines_out.append(cl)
        if done:
            break
    return "\n".join(lines_out)

HEADER = '''# Item 225 — Artériopathie de l'aorte, des artères viscérales et des membres inférieurs ; anévrismes

> **Collège CNEC / SFC** · 3e édition (2025) · p. 134–162 · R2C  
> Partie I — Athérome, facteurs de risque cardiovasculaire, maladie coronarienne, artériopathie

---

## Trois repères à ne pas confondre

| Badge | Signification (R2C) |
|---|---|
| **Rang A** | Connaissances fondamentales de fin de 2e cycle |
| **Rang B** | Connaissances essentielles, plus spécialisées |
| **Rang C** | Connaissances de 3e cycle (DES) |

Les pastilles du livre (● = A, ■ = B) sont reprises inline. Un objectif sans pastille = **Rang C**.

---

## Situations de départ

3 Distension abdominale.  
4 Douleur abdominale.  
15 Anomalies de couleur des extrémités.  
19 Découverte d'un souffle vasculaire.  
30 Dénutrition/malnutrition.  
42 Hypertension artérielle.  
63 Troubles sexuels et troubles de l'érection.  
66 Apparition d'une difficulté à la marche.  
68 Boiterie.  
69 Claudication intermittente d'un membre.  
71 Douleur d'un membre (supérieur ou inférieur).  
92 Ulcère cutané.  
195 Analyse du bilan lipidique.  
231 Demande d'un examen d'imagerie.  
232 Demande d'explication d'un patient sur le déroulement, les risques et les bénéfices attendus d'un examen d'imagerie.  
248 Prescription et suivi d'un traitement par anticoagulant et/ou antiagrégant.  
252 Prescription d'un hypolipémiant.  
259 Évaluation et prise en charge de la douleur aiguë.  
260 Évaluation et prise en charge de la douleur chronique.  
271 Prescription et surveillance d'une voie d'abord vasculaire.  
281 Prescription médicamenteuse, consultation de suivi et éducation d'un patient diabétique de type 2 ou ayant un diabète secondaire.  
282 Prescription médicamenteuse, consultation de suivi et éducation d'un patient hypertendu.  
300 Consultation pré-anesthésique.  
314 Prévention des risques liés au tabac.  
328 Annonce d'une maladie chronique.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Connaître la définition et la fréquence de l'AOMI | |
| **B** | Physiopathologie | Connaître l'étiologie et les facteurs de risque de l'AOMI | |
| **A** | Diagnostic positif | Connaître les manifestations cliniques et la classification de l'AOMI et savoir évoquer les diagnostics différentiels | |
| **A** | Examens complémentaires | Savoir prescrire les examens complémentaires de 1re intention | |
| **A** | Prise en charge | Connaître le traitement médical : traitement médicamenteux et principes du traitement chirurgical | |
| **A** | Suivi et/ou pronostic | Connaître les complications et le pronostic : ischémie aiguë des membres inférieurs, morbimortalité cardiovasculaire | |
| **A** | Diagnostic positif | Savoir définir et identifier les manifestations cliniques d'ischémie aiguë complète ou incomplète | |
| **B** | Étiologies | Connaître les autres causes de l'ischémie aiguë | |
| **A** | Identifier une urgence | Connaître les principes d'un traitement en urgence | |
| **A** | Définition | Connaître la définition et l'histoire naturelle d'un anévrisme de l'aorte abdominale et savoir rechercher d'autres localisations anévrismales | |
| **B** | Étiologies | Connaître les principales étiologies des anévrismes de l'aorte abdominale et les principes du dépistage | |
| **A** | Diagnostic positif | Connaître les signes cliniques des anévrismes de l'aorte | |
| **A** | Examens complémentaires | Savoir comment faire le diagnostic des anévrismes de l'aorte abdominale | |
| **C** | Prise en charge | Connaître les principes thérapeutiques d'un anévrisme de l'aorte abdominale | |
| **A** | Identifier une urgence | Savoir reconnaître et prendre en charge une situation d'urgence chez les patients porteurs d'un anévrisme de l'aorte abdominale | |
| **A** | Définition | Connaître la définition de l'ischémie intestinale aiguë et chronique | |
| **A** | Diagnostic positif | Connaître la sémiologie de l'ischémie intestinale aiguë et chronique : signes fonctionnels et signes physiques | |

---

## Parcours Rang A

- [I. Artériopathie de l'aorte et des artères viscérales](#i-artériopathie-de-laorte-et-des-artères-viscérales)
- [II. AOMI](#ii-artériopathie-oblitérante-des-membres-inférieurs-aomi)
- [III. Ischémie aiguë des membres inférieurs](#iii-ischémie-aiguë-des-membres-inférieurs)
- [IV. Anévrismes](#iv-anévrismes)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Artériopathie de l'aorte et des artères viscérales](#i-artériopathie-de-laorte-et-des-artères-viscérales)
- [II. Artériopathie oblitérante des membres inférieurs (AOMI)](#ii-artériopathie-oblitérante-des-membres-inférieurs-aomi)
- [III. Ischémie aiguë des membres inférieurs](#iii-ischémie-aiguë-des-membres-inférieurs)
- [IV. Anévrismes](#iv-anévrismes)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/225_Arteriopathie_AOMI_anevrismes.md)

---

'''

FOOTER = '''
---

## Notions indispensables et inacceptables

### Notions indispensables

- Chez un patient porteur d'un AOMI ou d'un anévrisme de l'aorte abdominale, penser à rechercher une maladie coronarienne sous-jacente ou une sténose carotidienne.
- L'ischémie aiguë des membres inférieurs est une urgence, aucun examen ne doit faire retarder la prise en charge.
- La rupture d'AAA est aussi une urgence absolue dont le diagnostic doit être confirmé par un scanner avant la prise en charge thérapeutique.

### Notions inacceptables

- Réaliser des examens d'imagerie inutiles retardant la prise en charge en cas d'ischémie aiguë de membre.

---

## Réflexes transversalité

- Item 221 — Athérome : épidémiologie et physiopathologie. Le malade polyathéromateux.
- Item 222 — Facteurs de risque cardiovasculaire et prévention.

---

## Entraînement

Questions isolées et corrigés : [Entrainement/QI/225_Arteriopathie_AOMI_anevrismes.md](../../Entrainement/QI/225_Arteriopathie_AOMI_anevrismes.md)
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
    cleaned_body = re.sub(r"est sévère lorsque IPS est > 0,7", "est sévère lorsque l'IPS est < 0,7", cleaned_body)
    cleaned_body = re.sub(r"est sévère lorsque IPS est", "est sévère lorsque l'IPS est", cleaned_body)
    # Points : uniquement après fin section IV (marqueur fin poplitée)
    cleaned_body = re.sub(
        r"thrombose veineuse compressive\)\.\s+Artériopathie de l'aorte et des artères viscérales",
        "thrombose veineuse compressive).\n\n---\n\n## Points\n\n### Artériopathie de l'aorte et des artères viscérales",
        cleaned_body,
    )
    cleaned_body = re.sub(
        r"endovasculaire\.\s+Artériopathie oblitérante des membres inférieurs \(AOMI\)",
        "endovasculaire.\n\n### Artériopathie oblitérante des membres inférieurs (AOMI)",
        cleaned_body,
    )
    cleaned_body = re.sub(
        r"endovasculaire\.\s+Ischémie aiguë des membres inférieurs",
        "endovasculaire.\n\n### Ischémie aiguë des membres inférieurs",
        cleaned_body,
    )
    cleaned_body = re.sub(
        r"charge\.\s+Anévrisme de l'aorte abdominale \(AAA\)",
        "charge.\n\n### Anévrisme de l'aorte abdominale (AAA)",
        cleaned_body,
    )

    OUT.write_text(HEADER + cleaned_body + FOOTER, encoding="utf-8")
    print(f"Written {OUT} ({OUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
