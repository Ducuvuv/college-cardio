# -*- coding: utf-8 -*-
"""Generate item 235 markdown from extracted PDF text."""
import re
from pathlib import Path

SRC = Path(r"C:\Users\gestu\Documents\college cardio\_tmp_item235.txt")
OUT = Path(r"C:\Users\gestu\Documents\college cardio\Cours\VI_Divers\235_Pericardite_aigue.md")

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Médecine cardiovasculaire\s*$",
    r"^Divers\s*$",
    r"^20\s*$",
    r"^Item 235\s*$",
    r"^Péricardite aiguë\s*$",
    r"^Situations de départ\s*$",
    r"^Hiérarchisation des connai.*",
    r"^497\s*$",
    r"^498\s*$",
    r"^499\s*$",
    r"^500\s*$",
    r"^502\s*$",
    r"^504\s*$",
    r"^506\s*$",
    r"^508\s*$",
    r"^509\s*$",
    r"^510\s*$",
    r"^19\s*$",
    r"^► Entraînement.*",
    r"^Les corrigés sont.*",
    r"^Pour en savoir plus\s*$",
    r"^Entraînement\s*$",
    r"^► Compléments.*",
    r"^Des compléments numériques.*",
    r"^par des flashcodes.*",
    r"^consulte\.com.*",
    r"^clés\s*$",
    r"^nts\s*$",
    r"^\\ V\s*$",
    r"^______x-\*.*",
    r"^Rang Rubrique\s*$",
    r"^Intitulé\s*$",
    r"^Descriptif\s*$",
    r"^Rang\s*$",
    r"^Rubrique\s*$",
    r"^à l'entraînement de l'intelligence artificielle.*",
    r"^!St strictement interdite.*",
    r"^: sur https://t\.me/Faille_V2\s*$",
    r"^«\s*$",
    r"^f\s*$",
    r"^QQRM\s*\d+.*",
    r"^QRM\s*\d+.*",
    r"^QRU\s*\d+.*",
    r"^GQRM\d+.*",
    r"^O QRU.*",
    r"^O QRM.*",
]

SECTION_MAP = {
    "I. Diagnostic": "\n\n# I. Diagnostic\n\n**Rang A** · **Rang B**.",
    "II. Complications à court et long terme": "\n\n---\n\n# II. Complications à court et long terme\n\n**Rang A** · **Rang B**.",
    "III. Traitement": "\n\n---\n\n# III. Traitement\n\n**Rang A** · **Rang B**.",
}

FIG_MAP = {
    "Fig. 20.1": ("fig_20_1_ecg_pericardite.png", "Fig. 20.1 — ECG d'une péricardite aiguë"),
    "Fig. 20.4": ("fig_20_4_demarche_diagnostique.png", "Fig. 20.4 — Démarche diagnostique après évocation d'une péricardite"),
}

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")

FLOWCHART_GARBAGE = {
    "Bilan d'une douleur thoracique aiguë", "Précordialgie typique", "Autres symptômes fréquents :",
    "Biologie", "Échocardiographie", "> 2 critères parmi :", "i 1. Précordialgie typique",
    "i 2. Frottement péricardique", "I 3. Modifications ECG", "i 4. Epanchement péricardique",
    "i- ", "----- ___ -----1", "ECG", "1. Sus-ST concave vers le haut. T+",
    "2. Sous-décalage du segment PQ", "3. Tachycardie sinusale", "4. Microvoltage (si tamponade)",
    "1. Prolongée", "2. Majorée à l'inspiration ou décubitus", "3. Soulagée en l'anteflexion",
    "4. Frottement péricardique (rare)", "• Fébrcule", "• Contage infectieux",
    "• Dyspnce [douleur thoracique inspiratoire ?)", "1. Inflammation dont CRP", "2. Troponine",
    "3. Tonogramme sanguin", "4. Hémocultures si fièvre", "1. Épanchement péricardique ?",
    "2. Altération de la fonction contractile,", "FEVG",
}


def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    if line in FLOWCHART_GARBAGE:
        return None
    if re.match(r"^[A-E]$", line):
        return None
    line = line.replace("El ", "• ")
    line = line.replace("201 5", "2015")
    line = line.replace("1 5 jours", "15 jours")
    line = line.replace("1 €r", "1er")
    line = line.replace("1 000 mg", "1 000 mg")
    line = line.replace("cidosporine", "ciclosporine")
    line = line.replace("Usic", "USIC")
    line = line.replace("without Image", "sans image")
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


def extract_body():
    text = SRC.read_text(encoding="utf-8")
    pages = re.split(r"===== PDF PAGE \d+ =====", text)
    lines_out = []
    skip_until_vignette = True
    done = False
    in_body = False
    in_points = False
    skip_flowchart = False
    intro_done = False

    for chunk in pages:
        if done or not chunk.strip():
            continue
        for line in chunk.splitlines():
            cl = clean_line(line)
            if cl is None:
                continue
            cl = re.sub(r"^Item 235 - Péricardite aiguë\s*", "", cl)
            if skip_until_vignette:
                if cl.startswith("Vignette clinique") or cl.startswith("Vous accueillez au service"):
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
                "► Compléments",
                "O QRM 1",
                "QQRM 1",
            )):
                done = True
                break
            if not intro_done and cl.startswith("**Rang A.** Inflammation aiguë"):
                lines_out.append("## Introduction\n")
                lines_out.append(cl)
                intro_done = True
                continue
            if cl.startswith("Le tableau typique de péricardite"):
                lines_out.append("\n\n---\n\n## Points\n")
                in_points = True
                in_body = False
                lines_out.append("• " + cl)
                continue
            matched = False
            for sec, hdr in SECTION_MAP.items():
                if cl == sec or cl.startswith(sec + " "):
                    lines_out.append(hdr)
                    in_body = True
                    in_points = False
                    skip_flowchart = False
                    matched = True
                    rest = cl[len(sec):].strip()
                    if rest:
                        lines_out.append(rest)
                    break
            if matched:
                continue
            if cl.startswith("La démarche diagnostique après évocation"):
                skip_flowchart = True
                continue
            if skip_flowchart:
                if "Fig. 20.4" in cl:
                    skip_flowchart = False
                else:
                    continue
            m = SUBSECTION_RE.match(cl)
            if m and in_body and not in_points:
                lines_out.append(f"\n## {m.group(1)}\n")
                continue
            m2 = NUM_SUBSECTION_RE.match(cl)
            if m2 and in_body and not in_points and len(cl) < 100:
                lines_out.append(f"\n### {m2.group(1)}\n")
                continue
            fig_handled = False
            for fig_key, (fname, caption) in FIG_MAP.items():
                if fig_key.lower() in cl.lower() and cl.startswith("Fig."):
                    lines_out.append(f"\n![{caption}](./img/{fname})\n")
                    cap = re.sub(r"^Fig\. 20\.\d+\.?\s*[0-9ODElQ]?\s*", "", cl)
                    lines_out.append(f"\n**Fig. {fig_key.split()[-1]}.** {cap.lstrip('0123456789. ')}\n")
                    fig_handled = True
                    break
            if fig_handled:
                continue
            if cl == "•":
                continue
            if cl.startswith("- ") or cl.startswith("• ") or (in_body and not in_points and cl.endswith(";") and not cl.startswith("#")):
                if not cl.startswith("• ") and not cl.startswith("- "):
                    cl = "• " + cl
                lines_out.append(cl)
            elif cl.startswith("> "):
                lines_out.append(cl)
            elif in_points and not cl.startswith("•"):
                lines_out.append("• " + cl)
            else:
                lines_out.append(cl)
        if done:
            break
    return "\n".join(lines_out)


def postprocess(cleaned: str) -> str:
    cleaned = cleaned.replace("Item 235 - Péricardite aiguë ", "")
    cleaned = re.sub(r"\n•\n\n", "\n• ", cleaned)
    cleaned = re.sub(r"\n•\n", "\n• ", cleaned)
    cleaned = re.sub(r"(?<=\w)-\s+(?=[a-zàâ])", "", cleaned)
    cleaned = cleaned.replace("bio- logie", "biologie")
    cleaned = cleaned.replace("tho- racique", "thoracique")
    cleaned = cleaned.replace("péri- cardique", "péricardique")
    cleaned = cleaned.replace("péri- cardiques", "péricardiques")
    cleaned = cleaned.replace("cardiques parfois", "cardiques parfois")
    cleaned = cleaned.replace("péri- cardite", "péricardite")
    cleaned = cleaned.replace("sans Image en miroir", "sans image en miroir")
    cleaned = cleaned.replace("1€r jour", "1er jour")
    cleaned = re.sub(r"(?m)^• (.+)\n• ", r"• \1 ", cleaned)
    cleaned = re.sub(r"\n## Points\n\n(• .+\n)+", lambda m: "\n\n---\n\n## Points\n\n" + re.sub(r"\n• ", " ", m.group(0).split("## Points\n\n",1)[-1]).strip() + "\n", cleaned, count=1)
    cleaned = cleaned.replace("sympto- matique", "symptomatique")
    cleaned = cleaned.replace("anti- inflammatoire", "anti-inflammatoire")
    cleaned = cleaned.replace("transa- minases", "transaminases")
    cleaned = cleaned.replace("cardio- logue", "cardiologue")
    cleaned = cleaned.replace("écho- cardiographie", "échocardiographie")
    cleaned = cleaned.replace("cyto- mégalovirus", "cytomégalovirus")
    cleaned = cleaned.replace("péri- cardique", "péricardique")
    cleaned = cleaned.replace("tubages gastriques", "tubages gastriques")
    cleaned = cleaned.replace("péri- cardique", "péricardique")
    cleaned = re.sub(r"(vidéo 20\.1)\.\s+([A-G]\.)", r"\1.\n\n## \2", cleaned)
    cleaned = re.sub(r"\.\s+([A-G]\.\s[A-Z])", r".\n\n## \1", cleaned)
    cleaned = re.sub(r"\.\s+(\d+\.\s[A-Z])", r".\n\n### \1", cleaned)
    return cleaned


HEADER = '''# Item 235 — Péricardite aiguë

> **Collège CNEC / SFC** · 3e édition (2025) · p. 497–510 · R2C  
> Partie VI — Divers

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

43 Découverte d'une hypotension artérielle.  
161 Douleur thoracique.  
166 Tachycardie.  
178 Demande/prescription raisonnée et choix d'un examen diagnostique.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
203 Élévation de la protéine C-réactive (CRP).  
249 Prescrire des anti-inflammatoires non stéroïdiens (AINS).

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Définition d'une péricardite aiguë | |
| **A** | Diagnostic positif | Symptômes et signes cliniques | Enjeu diagnostique vs SCA |
| **A** | Identification de l'urgence | Signes de gravité, drainage | Insuffisance cardiaque droite, hypotension, pouls paradoxal |
| **A** | Examens complémentaires | ECG et bilan biologique initial | Signes ECG, marqueurs inflammation/nécrose |
| **A** | Examens complémentaires | Intérêt diagnostique de la ponction péricardique | Étiologie infectieuse, IC, tumorale |
| **B** | Examens complémentaires | Imagerie (radio, échocardiographie) | Silhouette cardiaque, épanchement, cinétique |
| **A** | Contenu multimédia | Exemple ECG péricardite aiguë | |
| **A** | Prise en charge | Évaluer les risques de complications | Fièvre, durée, épanchement, résistance AINS |
| **A** | Étiologies | Forme clinique usuelle | Péricardite aiguë virale |
| **B** | Étiologies | Péricardite au cours d'un IDM | Précoce, syndrome de Dressler |
| **B** | Étiologies | Formes cliniques moins fréquentes | Purulente, tuberculeuse, néoplasique, auto-immune, IRC, post-péricardiotomie |
| **A** | Prise en charge | Traitement péricardite aiguë bénigne | Repos, AINS, colchicine |
| **A** | Suivi et/ou pronostic | Complications | Épanchement, tamponnade, myocardite, récidive, constriction |
| **B** | Étiologies | Étiologies devant une tamponnade | Hémopéricarde, traumatique, néoplasique, virale, post-IDM, dissection |
| **A** | Identification de l'urgence | Diagnostic de tamponnade | Signes droits, choc obstructif |

---

## Parcours Rang A

- [I. Diagnostic](#i-diagnostic)
- [II. Complications (tamponnade)](#ii-complications-à-court-et-long-terme)
- [III. Traitement](#iii-traitement)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [Introduction](#introduction)
- [I. Diagnostic](#i-diagnostic)
- [II. Complications à court et long terme](#ii-complications-à-court-et-long-terme)
- [III. Traitement](#iii-traitement)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/235_Pericardite_aigue.md)

---

'''

FOOTER = '''
---

## Notions indispensables et inacceptables

### Notions indispensables

- Hospitalisation recommandée en cas de mauvaise tolérance clinique, fièvre > 38 °C, début subaigu, épanchement péricardique abondant ou résistance au traitement anti-inflammatoire au bout d'une semaine.
- Autres facteurs devant aussi faire discuter une hospitalisation : patient immunodéprimé, patient sous anticoagulant, suites d'un traumatisme thoracique, présence d'une myocardite associée (ou augmentation de la troponine).
- La tamponnade est une urgence médicochirurgicale qui nécessite une prise en charge en USIC et un drainage urgent (risque d'arrêt cardiocirculatoire).

### Notions inacceptables

- Ne pas identifier les situations d'urgence et planifier leur prise en charge (tamponnade).
- Recourir au traitement corticoïde en 1re intention.

---

## Réflexes transversalité

- Item 230 — Douleur thoracique aiguë.
- Item 231 — Électrocardiogramme : indications et interprétation.

---

## Entraînement

Questions isolées et corrigés : [Entrainement/QI/235_Pericardite_aigue.md](../../Entrainement/QI/235_Pericardite_aigue.md)
'''


def main():
    body = extract_body()
    cleaned = postprocess(body)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(HEADER + cleaned + FOOTER, encoding="utf-8")
    print(f"Written {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
