# -*- coding: utf-8 -*-
"""Generate item 237 palpitations markdown + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item237.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Cours" / "III_Rythmologie" / "237_Palpitations.md"
IMG_DIR = OUT.parent / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "237_Palpitations.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"Pour avoir plus d’exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Rythmologie\s*$",
    r"^CHAPITRE\s*$",
    r"^16\s*$",
    r"^17\s*$",
    r"^Item 237\s*$",
    r"^Item 237 -.*",
    r"^Palpitations\s*$",
    r"^Situations de départ\s*$",
    r"^Hiérarchisation.*",
    r"^Rang Rubrique\s*$",
    r"^Intitulé\s*$",
    r"^Descriptif\s*$",
    r"^Rang\s*$",
    r"^Rubrique\s*$",
    r"^► Entraînement.*",
    r"^Les corrigés sont.*",
    r"^Pour en savoir plus\s*$",
    r"^Entraînement\s*$",
    r"^clés\s*$",
    r"^clésl\s*$",
    r"^===== PDF PAGE \d+ =====$",
    r"^O QRU\s*\d+.*",
    r"^G QRU\s*\d+.*",
    r"^B QRU\s*\d+.*",
    r"^QRU\s*\d+.*",
    r"^QRM\s*\d+.*",
    r"^Médecine cardiovasculaire\s*$",
    r"^Bordachar P,.*",
    r"^de la conduction.*",
    r"^pathologique - ECG.*",
    r"^des cardiomyopathies.*",
    r"^Stimuprat\..*",
    r"^Item 203\s*$",
    r"^Dyspnée aiguë\s*$",
    r"^et chronique\s*$",
    r"^Figure 16\.6A.*",
    r"^F 407\s*$",
    r"^G®.*",
    r"^_{5,}.*",
    r"^«\s*$",
]

FLOW_GARBAGE = {
    "Tachycardie", "ORS larges", "Supraventriculaire", "avec anomalie",
    "de conduction", "Fibrillation", "atriale", "Irrégulière", "TV",
    "4)U", "MM", "N", "F",
}

SECTION_MAP = {
    "I. Définition et diagnostic": "\n\n# I. Définition et diagnostic\n\n**Rang A.**",
    "II. Diagnostic de gravité": "\n\n---\n\n# II. Diagnostic de gravité\n\n**Rang A.**",
    "III. Diagnostic étiologique": "\n\n---\n\n# III. Diagnostic étiologique\n\n**Rang A** · **Rang B**.",
    "IV. Étiologies les plus fréquentes": "\n\n---\n\n# IV. Étiologies les plus fréquentes\n\n**Rang A.**",
}

SUBSECTION_RE = re.compile(r"^([A-E]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")

POINTS_BLOCK = """
• Les palpitations sont une perception anormale des battements cardiaques.

• Il s'agit d'un symptôme banal qui s'efface derrière un éventuel symptôme plus grave de type syncope, douleur thoracique ou dyspnée.

• Il faut savoir écarter des signes de gravité liés au terrain, à une mauvaise tolérance hémodynamique ou à l'enregistrement immédiat d'une tachycardie ventriculaire.

• Il faut savoir rechercher une cardiopathie ou une maladie extracardiaque.

• L'enregistrement de l'ECG au moment exact des palpitations est la notion de corrélation électroclinique.

• La corrélation électroclinique peut requérir dans l'ordre : ECG standard, holter de 24–96 heures, monitorage ambulatoire de 21 jours, moniteur ECG implantable, étude électrophysiologique endocavitaire, mais aussi montres connectées, smartphones.

• Le diagnostic final peut être une tachycardie sinusale ou des extrasystoles dont il faut connaître les causes extracardiaques. Parmi les causes de tachycardie sinusale : grossesse, hyperthyroïdie, SAOS, alcoolisme.

• En diagnostic d'élimination, des causes psychologiques sont parfois involontairement entretenues par les professionnels de santé.
"""

HEADER = '''# Item 237 — Palpitations

> **Collège CNEC / SFC** · 3e édition (2025) · p. 388–410 · R2C  
> Partie III — Rythmologie

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

18 Découverte d'anomalies à l'auscultation cardiaque.  
44 Hyperthermie, fièvre.  
49 Ivresse aiguë.  
161 Douleur thoracique.  
162 Dyspnée.  
165 Palpitations.  
166 Tachycardie.  
178 Demande/prescription raisonnée et choix d'un examen diagnostique.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
194 Analyse du bilan thyroïdien.  
248 Prescription et suivi d'un traitement par anticoagulant et/ou antiagrégant.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Définition des palpitations | Description et champ syndromique |
| **A** | Identifier une urgence | Signes de gravité et diagnostics ECG urgents | Symptômes alarmants ; SCA et TV |
| **A** | Diagnostic positif | Parallélisme électroclinique | Corrélation ECG–clinique |
| **B** | Examens complémentaires | Bilan initial | Biologie et examens de 1re intention |
| **A** | Étiologies | Extrasystoles | Diagnostic ECG, contextes à risque |
| **A** | Étiologies | Tachycardie sinusale | Contextes adaptatifs |
| **A** | Étiologies | Tachycardies jonctionnelles | Clinique, ECG |
| **A** | Étiologies | Wolff-Parkinson-White | Diagnostic ECG |
| **A** | Étiologies | Névrose cardiaque | Causes psychiatriques, attaques de panique |

---

## Parcours Rang A

- [I. Définition et diagnostic](#i-définition-et-diagnostic)
- [II. Diagnostic de gravité](#ii-diagnostic-de-gravité)
- [III. Diagnostic étiologique](#iii-diagnostic-étiologique)
- [IV. Étiologies les plus fréquentes](#iv-étiologies-les-plus-fréquentes)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Définition et diagnostic](#i-définition-et-diagnostic)
- [II. Diagnostic de gravité](#ii-diagnostic-de-gravité)
- [III. Diagnostic étiologique](#iii-diagnostic-étiologique)
- [IV. Étiologies les plus fréquentes](#iv-étiologies-les-plus-fréquentes)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/237_Palpitations.md)

---

'''

QI_CONTENT = '''# Entraînement — Item 237 Palpitations

> Collège CNEC 3e éd. · Chapitre 16 · corrigés p. 585  
> Cours : [237 Palpitations](../../Cours/III_Rythmologie/237_Palpitations.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRU 1

Concernant les palpitations, indiquer la bonne réponse :

- A. Elles constituent des symptômes très spécifiques
- B. Elles sont rares
- C. Elles sont similaires d'une personne à l'autre
- D. L'interrogatoire constitue un temps primordial
- E. L'ECG n'a aucun intérêt

**Réponse : D**

L'interrogatoire est le premier temps, indispensable, de l'examen clinique (**D**). Les palpitations sont un symptôme **peu spécifique**, fréquent, variable d'une personne à l'autre. L'ECG (corrélation électroclinique) est central.

---

## QRU 2

Concernant la corrélation électroclinique, indiquer la bonne réponse :

- A. Elle permet de faire le lien entre les symptômes cliniques et l'enregistrement du rythme cardiaque
- B. Elle est toujours réalisée sur un ECG 12 dérivations
- C. Elle est facile à obtenir
- D. Elle peut être réalisée en prenant le pouls du patient
- E. Elle n'apporte rien

**Réponse : A**

C'est le lien symptômes ↔ tracé (ECG, holter, montre connectée) (**A**). Pas toujours un 12 dérivations ; souvent difficile à obtenir si crises rares ; le pouls ne documente pas le rythme.

---

## QRU 3

Concernant la tachycardie sinusale, indiquer la bonne réponse :

- A. Elle est exclusivement adaptative
- B. Elle est exclusivement de causes cardiaques
- C. Elle est physiologique
- D. Elle est rare
- E. Elle est habituellement bruyante

**Réponse : C**

La tachycardie sinusale est le plus souvent **physiologique** / adaptative (fièvre, effort, anxiété, grossesse, etc.), fréquente, souvent peu bruyante. Elle n'est ni exclusivement adaptative (il existe des formes inappropriées) ni exclusivement cardiaque.

---

## QRU 4

Concernant la tachycardie jonctionnelle par réentrée intranodale, indiquer la bonne réponse :

- A. Elle est habituellement sur cœur sain
- B. Elle est due à la présence d'une seule voie de conduction nodale
- C. Elle ne donne jamais de syncope
- D. Elle est rarement ressentie
- E. Elle est à haut risque de mort subite

**Réponse : A**

TJ par réentrée intranodale : typiquement **cœur sain**, deux voies nodales, souvent très symptomatique (Bouveret), syncopes possibles, pas de risque de mort subite.

---

## QRU 5

Concernant la tachycardie jonctionnelle sur voie accessoire, indiquer la bonne réponse :

- A. Elle est présente uniquement chez des patients porteurs de cardiopathie
- B. Le pronostic vital peut être engagé en cas de faisceau accessoire avec période réfractaire courte
- C. La fibrillation atriale n'a pas d'impact sur le pronostic lorsqu'elle est associée
- D. Elle se traduit par un allongement de l'intervalle PR
- E. Une tachycardie antidromique est à QRS fins

**Réponse : B**

Voie accessoire à période réfractaire courte : FA pouvant conduire très vite aux ventricules → risque de **FV** (**B**). PR **court**, pas allongé. Antidromique = QRS **larges**. Souvent cœur sain.
'''


def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    if line in FLOW_GARBAGE:
        return None
    if re.match(r"^(388|389|390|391|392|393|394|395|396|397|398|399|400|401|402|403|404|405|406|407|408|409|410)$", line):
        return None
    if re.match(r"^[A-G]$", line) and len(line) == 1:
        return None
    line = line.replace("< 1 50", "< 150")
    line = line.replace("> 1 50", "> 150")
    line = line.replace("fig. 1 6", "fig. 16")
    line = line.replace("Fig. 1 6", "Fig. 16")
    line = line.replace("El Les", "Les")
    line = re.sub(r"^• 0 ", "• **Rang A.** ", line)
    for prefix, repl in (("• O ", "• **Rang A.** "), ("• □ ", "• **Rang B.** "), ("• Q ", "• **Rang A.** ")):
        if line.startswith(prefix):
            line = repl + line[len(prefix):]
            break
    for prefix, repl in (("□ ", "**Rang B.** "), ("O ", "**Rang A.** "), ("Q ", "**Rang A.** ")):
        if line.startswith(prefix):
            rest = line[len(prefix):]
            if rest and rest[0].islower():
                break
            line = repl + rest
            break
    line = re.sub(r"^(Fig\. 16\.\d+)\.0 ", r"\1. ", line)
    line = re.sub(r"^(Fig\. 16\.\d+)\. 0 ", r"\1. ", line)
    return line


def match_section(cl):
    for sec, hdr in SECTION_MAP.items():
        if cl == sec or cl.startswith(sec):
            return hdr
    return None


def extract_footer(text):
    notions_ind, notions_inacc, reflexes = [], [], []
    mode = None
    for raw in text.splitlines():
        raw_s = raw.strip()
        if raw_s.startswith("► Entraînement") or raw_s.startswith("O QRU") or raw_s.startswith("Pour en savoir plus"):
            break
        cl = clean_line(raw)
        if cl is None:
            continue
        if cl.startswith("Notions indispensables") and "inacceptables" not in cl.lower():
            mode = "ind"
            continue
        if cl.startswith("Notions inacceptables"):
            mode = "inacc"
            continue
        if cl.startswith("Réflexes transversalité"):
            mode = "reflex"
            continue
        if mode == "ind":
            notions_ind.append(cl if cl.startswith("•") else "• " + cl)
        elif mode == "inacc":
            notions_inacc.append(cl if cl.startswith("•") else "• " + cl)
        elif mode == "reflex":
            reflexes.append(cl if cl.startswith("•") else "• " + cl)
    return notions_ind, notions_inacc, reflexes


def extract_body():
    text = SRC.read_text(encoding="utf-8")
    stop = text.find("► Entraînement")
    if stop == -1:
        stop = text.find("===== PDF PAGE 438")
    chunk = text[:stop] if stop != -1 else text

    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False
    pending_bullet = None
    seen_figs = set()
    skip_flow = False

    for line in chunk.splitlines():
        stripped = line.strip()
        if stripped in ("•", "-", "–"):
            pending_bullet = "• " if stripped == "•" else "- "
            continue
        cl = clean_line(line)
        if cl is None:
            continue
        if pending_bullet and not cl.startswith(("• ", "- ", "#", "**Rang")):
            cl = pending_bullet + cl
            pending_bullet = None
        else:
            pending_bullet = None

        if skip_until_vignette:
            if cl.startswith("Vignette clinique"):
                skip_until_vignette = False
                lines_out.append("## Vignette clinique\n")
            continue
        if cl.startswith("Notions indispensables"):
            break
        if cl.startswith("Points") and not in_points:
            lines_out.append("\n\n---\n\n## Points\n")
            lines_out.append(POINTS_BLOCK)
            in_points = True
            continue
        if in_points:
            continue

        if skip_flow:
            if cl.startswith("Fig. 16.") or cl.startswith("2. Holter") or cl.startswith("### "):
                skip_flow = False
            else:
                continue

        hdr = match_section(cl)
        if hdr:
            lines_out.append(hdr)
            in_body = True
            continue

        fig_m = re.match(r"^Fig\.\s*16\.(\d+)", cl)
        if fig_m:
            n = fig_m.group(1)
            fname = f"fig_16_{n}.png"
            cap = re.sub(r"^Fig\.\s*16\.\d+\.?\s*[0O©ElQG]?\s*", "", cl).strip()
            if not cap:
                cap = f"Fig. 16.{n}"
            lines_out.append(f"\n![Fig. 16.{n} — {cap}](./img/{fname})\n")
            lines_out.append(f"\n**Fig. 16.{n}.** {cap}\n")
            seen_figs.add(n)
            if n == "1":
                skip_flow = True
            continue

        m = SUBSECTION_RE.match(cl)
        if m and in_body and len(cl) < 160:
            lines_out.append(f"\n## {m.group(1)}\n")
            continue
        m2 = NUM_SUBSECTION_RE.match(cl)
        if m2 and in_body and len(cl) < 140:
            lines_out.append(f"\n### {m2.group(1)}\n")
            continue
        if cl.startswith("2. Tachycardies jonctionnelles sur voie") or cl.startswith("de Wolff-Parkinson-White"):
            if cl.startswith("2."):
                lines_out.append(f"\n### {cl} de Wolff-Parkinson-White\n")
            continue

        if cl.startswith("> "):
            lines_out.append(cl)
        elif cl.startswith(">"):
            lines_out.append("> " + cl[1:].strip())
        elif cl.startswith("- ") or cl.startswith("• "):
            lines_out.append(cl)
        else:
            lines_out.append(cl)
    return "\n".join(lines_out)


def postprocess(text):
    text = re.sub(r">\s*\n+\s*", "> ", text)
    text = re.sub(r"(?<=\w)-\s+(?=[a-zàâéèêëîïôùûü])", "", text)
    text = re.sub(r"Pour avoir plus d['’]exclusivités.*?Faille_V2\s*", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.replace("Devant toutes palpitations", "Devant toute palpitation")
    text = re.sub(
        r"(> Vous paraît-il important de documenter une éventuelle récidive et, si oui, comment envisagez-vous)\n\n(de le faire)",
        r"\1 \2",
        text,
    )
    text = re.sub(
        r"(### 2\. Tachycardies jonctionnelles sur voie accessoire : syndrome)\n\n(de Wolff-Parkinson-White)",
        r"\1 de Wolff-Parkinson-White",
        text,
    )
    return text


def merge_paragraphs(body):
    paragraphs = []
    buf = []
    for line in body.splitlines():
        if not line.strip():
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append("")
            continue
        if line.startswith(("#", "##", "###", "**", "- ", "• ", ">", "!", "|", "---")) or re.match(r"^\s+- ", line):
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append(line)
        else:
            if not buf and paragraphs and paragraphs[-1].startswith(("• ", "- ")):
                paragraphs[-1] = paragraphs[-1] + " " + line.strip()
            else:
                buf.append(line.strip())
    if buf:
        paragraphs.append(" ".join(buf))
    return "\n\n".join(p for p in paragraphs if p is not None)


def make_footer(notions_ind, notions_inacc, reflexes):
    ind = "\n".join(n if n.startswith("•") else "• " + n for n in notions_ind) or (
        "• Notion électroclinique : documentation du tracé ECG au moment des symptômes.\n"
        "• Existence ou non d'une cardiopathie sous-jacente.\n"
        "• Signes de gravité."
    )
    inacc = "\n".join(n if n.startswith("•") else "• " + n for n in notions_inacc) or (
        "• S'orienter d'emblée vers des causes psychogènes sans avoir fait un bilan minimal."
    )
    # join split reflex lines
    refl_lines = []
    buf = ""
    for r in reflexes:
        txt = r.lstrip("• ").strip()
        if buf and not txt.startswith("Item"):
            buf += " " + txt
        else:
            if buf:
                refl_lines.append("• " + buf)
            buf = txt
    if buf:
        refl_lines.append("• " + buf)
    refl = "\n".join(refl_lines)
    return f"""
---

## Notions indispensables et inacceptables

### Notions indispensables

{ind}

### Notions inacceptables

{inacc}

---

## Réflexes transversalité

{refl}

---

## Entraînement

Questions isolées et corrigés : [Entrainement/QI/237_Palpitations.md](../../Entrainement/QI/237_Palpitations.md)
"""


def build_course():
    text = SRC.read_text(encoding="utf-8")
    body = merge_paragraphs(postprocess(extract_body()))
    notions_ind, notions_inacc, reflexes = extract_footer(text)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(HEADER + body + make_footer(notions_ind, notions_inacc, reflexes), encoding="utf-8")
    print(f"Written {OUT} ({OUT.stat().st_size} bytes)")


def build_qi():
    QI_OUT.parent.mkdir(parents=True, exist_ok=True)
    QI_OUT.write_text(QI_CONTENT, encoding="utf-8")
    print(f"Written {QI_OUT} ({QI_OUT.stat().st_size} bytes)")


def extract_figures():
    if not PDF.exists():
        print(f"PDF not found: {PDF}")
        return
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF)
    found = 0
    saved = set()
    for i in range(421, 435):
        if i >= len(doc):
            break
        page = doc[i]
        hits_by_n = {}
        for n in range(24, 0, -1):
            if n in saved:
                continue
            raw_hits = page.search_for(f"Fig. 16.{n}")
            valid = []
            for h in raw_hits:
                probe = fitz.Rect(h.x0, h.y0, min(page.rect.width, h.x1 + 30), h.y1)
                t = page.get_text("text", clip=probe)
                if re.search(rf"Fig\.\s*16\.{n}(?!\d)", t):
                    valid.append(h)
            if valid:
                hits_by_n[n] = max(valid, key=lambda x: x.y0)
        for n, r in hits_by_n.items():
            if n in saved:
                continue
            saved.add(n)
            y0 = max(0, r.y0 - 300)
            y1 = min(page.rect.height, r.y1 + 36)
            clip = fitz.Rect(18, y0, page.rect.width - 18, y1)
            pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
            out = IMG_DIR / f"fig_16_{n}.png"
            pix.save(str(out))
            found += 1
            print(f"Figure 16.{n} p.{i+1} -> {out.name} ({out.stat().st_size} bytes)")
    doc.close()
    print(f"Extracted {found} figures")


def update_readme():
    text = README.read_text(encoding="utf-8")
    row = "| Fait | 237 Palpitations | [III_Rythmologie/237_Palpitations.md](./III_Rythmologie/237_Palpitations.md) |\n"
    if "237 Palpitations" not in text:
        text = text.replace("| À faire | … | lots suivants |", row + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 237")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    sections = re.findall(r"^# [IVX]+\.", content, re.M)
    fig_count = len(list(IMG_DIR.glob("fig_16_*.png")))
    print(f"Course size: {size} bytes, section headers: {len(sections)} ({sections})")
    print(f"Figures: {fig_count} PNGs")
    if size < 20_000 or len(sections) < 4:
        print("WARN: verification thresholds not met")
    if "Item 203" in content.split("## Réflexes")[0]:
        print("WARN: Item 203 leak")


def main():
    build_course()
    build_qi()
    extract_figures()
    update_readme()
    verify()


if __name__ == "__main__":
    main()
