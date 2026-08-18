# -*- coding: utf-8 -*-
"""Generate item 238 souffle cardiaque chez l'enfant markdown + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item238.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Cours" / "II_Valves" / "238_Souffle_cardiaque_enfant.md"
IMG_DIR = OUT.parent / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "238_Souffle_cardiaque_enfant.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Maladies des valves\s*$",
    r"^Item 238\s*$",
    r"^Item 238 - Souffle cardiaque.*",
    r"^Item 238 - Souffle cardiaque chez l'enfant\s*$",
    r"^Souffle cardiaque\s*$",
    r"^chez l'enfant\s*$",
    r"^Situations de départ\s*$",
    r"^Hiérarchisation des connaissances\s*$",
    r"^Rang Rubrique\s*$",
    r"^Intitulé\s*$",
    r"^Descriptif\s*$",
    r"^Rang\s*$",
    r"^Rubrique\s*$",
    r"^► Entraînement.*",
    r"^Les corrigés sont.*",
    r"^Pour en savoir plus\s*$",
    r"^Entraînement\s*$",
    r"^► Compléments.*",
    r"^Des compléments numériques.*",
    r"^clés\s*$",
    r"^clésl\s*$",
    r"^nts\s*$",
    r"^à l'entraînement de l'intelligence artificielle.*",
    r"^!St strictement interdite.*",
    r"^: sur https://t\.me/Faille_V2\s*$",
    r"^===== PDF PAGE \d+ =====$",
    r"^O QRM\s*\d+.*",
    r"^© QRM\s*\d+.*",
    r"^G QRM\s*\d+.*",
    r"^S QRM\s*\d+.*",
    r"^□ QRM\s*\d+.*",
    r"^QRM\s*\d+.*",
    r"^QRU\s*\d+.*",
    r"^Vidéo 11\.\d+.*",
    r"^11\s*$",
    r"^Médecine cardiovasculaire\s*$",
    r"^4H 11.*",
    r"^[\d\s\.ÏHWMflBï\.\\\/\*]+$",
    r"^Pédiatrique\s*$",
    r"^Cardiomé\s*$",
    r"^Coarctation\s*$",
    r"^aortique\s*$",
    r"^CIA\s*$",
    r"^► fi\s*$",
    r"^FOV.*",
    r"^TNW.*",
    r"^Coai\s*$",
    r"^aocti\s*$",
    r"^S8-3\s*$",
    r"^26Hz\s*$",
    r"^CIV\s*$",
    r"^VD\s*$",
    r"^VG\s*$",
    r"^Fin 0 0\s*$",
    r"^r\.A Mod\..*",
    r"^> 5/MP\s*$",
    r"^1 55:45 AM\s*$",
    r"^VCS\s*$",
]

FLOWCHART_GARBAGE = {
    "*61", "\\", "\\X", "-61 6", "cm/s", "////", "P Arrêt", "Gên", "ÇouJ",
    "bpm", "6600Hz", "F P 659Hz", "3 3MHz", "76%", "C 50", "8 1cm", "2Q",
    "4Ô%", "Mod.", "HE*", "mm", "sp", "Fin", "AM", "r.A", "MP", "v $0",
}

SECTION_MAP = {
    "I. Généralités sur les cardiopathies de l'enfant": (
        "\n\n# I. Généralités cardiopathies enfant\n\n**Rang A.**"
    ),
    "II. Particularités de l'auscultation de l'enfant": (
        "\n\n---\n\n# II. Particularités auscultation enfant\n\n**Rang A.**"
    ),
    "III. Circonstances de découverte": (
        "\n\n---\n\n# III. Circonstances de découverte\n\n**Rang A.**"
    ),
    "IV. Clinique et examens complémentaires": (
        "\n\n---\n\n# IV. Clinique et examens complémentaires\n\n**Rang A** · **Rang B**."
    ),
    "V. Principales cardiopathies rencontrées en fonction de l'âge": (
        "\n\n---\n\n# V. Principales cardiopathies par âge\n\n**Rang A** · **Rang B**."
    ),
    "V. Principales cardiopathies rencontrées en fonction": (
        "\n\n---\n\n# V. Principales cardiopathies par âge\n\n**Rang A** · **Rang B**."
    ),
    "VI. Les souffles anorganiques (ou fonctionnels ou « innocents »)": (
        "\n\n---\n\n# VI. Souffles anorganiques/innocents\n\n**Rang A.**"
    ),
    "VI. Les souffles anorganiques (ou fonctionnels": (
        "\n\n---\n\n# VI. Souffles anorganiques/innocents\n\n**Rang A.**"
    ),
}

FIG_MAP = {
    "Fig. 11.1": ("fig_11_1_coarctation_neonat.png", "Fig. 11.1 — Coarctation aortique du nouveau-né (ETT)"),
    "Fig. 11.2": ("fig_11_2_coarctation.png", "Fig. 11.2 — Coarctation aortique"),
    "Fig. 11.3": ("fig_11_3_ventricule_unique.png", "Fig. 11.3 — Ventricule unique (ETT)"),
    "Fig. 11.4": ("fig_11_4_civ_rx.png", "Fig. 11.4 — CIV large : radiographie thoracique"),
    "Fig. 11.5": ("fig_11_5_civ_echo.png", "Fig. 11.5 — Large CIV (ETT avec couleur)"),
    "Fig. 11.6": ("fig_11_6_cia_3d.png", "Fig. 11.6 — Large CIA (ETT 3D)"),
}

FIGURES = [
    ("11.1", "fig_11_1_coarctation_neonat.png", 298),
    ("11.2", "fig_11_2_coarctation.png", 298),
    ("11.3", "fig_11_3_ventricule_unique.png", 299),
    ("11.4", "fig_11_4_civ_rx.png", 299),
    ("11.5", "fig_11_5_civ_echo.png", 300),
    ("11.6", "fig_11_6_cia_3d.png", 301),
]

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")

POINTS_BLOCK = """
**Points clés**

• Les souffles découverts dans la 2e enfance correspondent le plus souvent à des souffles anorganiques (« innocents », « fonctionnels », « normaux »), apanage de l'enfant et de l'adolescent.

• Dans les pays occidentaux, les cardiopathies organiques de l'enfant sont pratiquement toujours liées à des malformations congénitales ; les valvulopathies rhumatismales ont disparu. Il existe également des cardiomyopathies et des myocardites.

• Les signes d'appel : cyanose ou défaillance cardiaque chez le nouveau-né (plus rarement chez le nourrisson), dyspnée, insuffisance cardiaque, difficultés de croissance ; souvent la découverte fortuite d'un souffle asymptomatique.

• Les syndromes polymalformatifs (caryotype normal ou anormal) s'accompagnent fréquemment de cardiopathies congénitales : échocardiographie systématique.

• Particularités de l'auscultation de l'enfant : tachycardie sinusale, arythmie sinusale respiratoire, dédoublement variable du B2, B3 fréquent et physiologique.

• Il n'y a pas toujours de parallélisme entre l'intensité d'un souffle et la gravité de la cardiopathie. Une cardiopathie grave peut ne pas s'accompagner de souffle ; une cardiopathie mineure (petite CIV) peut générer un souffle intense.

• **Rang B.** L'ECG et le cliché de thorax n'ont qu'une valeur d'orientation ; l'ECG doit toujours être interprété en fonction de l'âge.

• Dans l'immense majorité des cas, l'interrogatoire et l'examen physique (dont une bonne auscultation) permettent d'étiqueter l'origine du souffle et son caractère organique ou fonctionnel. L'échocardiographie est l'examen clé ; elle permet de limiter les indications du cathétérisme, surtout à visée interventionnelle.

• D'autres examens peuvent être indiqués : holter ECG, épreuve d'effort dans la 2e enfance, IRM ou scanner.

• Les communications interatriales sont les cardiopathies bénignes les plus répandues.

• Chez le nourrisson, les shunts gauche-droite sont les malformations les plus communes, surtout les CIV. La cardiopathie cyanogène la plus courante est la tétralogie de Fallot (souffle précoce, cyanose retardée).

• **Rang A.** Dans la 2e enfance, les souffles fonctionnels dominent : il faut en connaître les caractéristiques.

• En cas de souffle fonctionnel (le plus fréquent en 2e enfance), aucun suivi, aucune restriction d'activité ni examen complémentaire ne sont indiqués.
"""

HEADER = '''# Item 238 — Souffle cardiaque chez l'enfant

> **Collège CNEC / SFC** · 3e édition (2025) · p. 262–274 · R2C  
> Partie II — Maladies des valves

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
19 Découverte d'un souffle vasculaire.  
20 Découverte d'anomalies à l'auscultation pulmonaire.  
26 Anomalies de la croissance staturo-pondérale.  
39 Examen du nouveau-né à terme.  
42 Hypertension artérielle.  
43 Découverte d'une hypotension artérielle.  
46 Hypotonie/malaise du nourrisson.  
55 Pâleur de l'enfant.  
160 Détresse respiratoire aiguë.  
162 Dyspnée.  
165 Palpitations.  
166 Tachycardie.  
178 Demande/prescription raisonnée et choix d'un examen diagnostique.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
230 Rédaction de la demande d'un examen d'imagerie.  
231 Demande d'un examen d'imagerie.  
265 Consultation de suivi d'un nourrisson en bonne santé.  
296 Consultation de suivi pédiatrique.  
308 Dépistage néonatal systématique.  
335 Évaluation de l'aptitude au sport et rédaction d'un certificat de non-contre-indication.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Diagnostic positif | Sémiologie cardiovasculaire chez l'enfant | |
| **A** | Définition | Définition d'un souffle cardiaque organique et non organique | Fréquence en fonction de l'âge |
| **B** | Examens complémentaires | Apports des examens de 1re intention devant un souffle de l'enfant | Radiographie thoracique, ECG, échocardiographie |
| **B** | Étiologies | Orientation étiologique des souffles cardiaques | |

---

## Parcours Rang A

- [I. Généralités cardiopathies enfant](#i-généralités-cardiopathies-enfant)
- [II. Particularités auscultation enfant](#ii-particularités-auscultation-enfant)
- [III. Circonstances de découverte](#iii-circonstances-de-découverte)
- [VI. Souffles anorganiques/innocents](#vi-souffles-anorganiquesinnocents)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Généralités cardiopathies enfant](#i-généralités-cardiopathies-enfant)
- [II. Particularités auscultation enfant](#ii-particularités-auscultation-enfant)
- [III. Circonstances de découverte](#iii-circonstances-de-découverte)
- [IV. Clinique et examens complémentaires](#iv-clinique-et-examens-complémentaires)
- [V. Principales cardiopathies par âge](#v-principales-cardiopathies-par-âge)
- [VI. Souffles anorganiques/innocents](#vi-souffles-anorganiquesinnocents)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/238_Souffle_cardiaque_enfant.md)

---

'''

QI_CONTENT = '''# Entraînement — Item 238 Souffle cardiaque chez l'enfant

> Collège CNEC 3e éd. · Chapitre 11 · corrigés p. 612  
> Cours : [238 Souffle cardiaque enfant](../../Cours/II_Valves/238_Souffle_cardiaque_enfant.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRU 1

Parmi les propositions suivantes concernant les souffles cardiaques de l'enfant, laquelle est vraie ?

- A. Le souffle innocent est le plus fréquent des souffles cardiaques de l'enfant
- B. Le souffle innocent peut être systolique ou diastolique
- C. Le souffle innocent est souvent intense
- D. Le souffle innocent peut varier avec le temps et la position
- E. Le souffle innocent a souvent une irradiation dorsale

**Réponse : D**

Le souffle innocent varie avec le temps et la position (**D**). **A** faux : ce n'est pas le plus fréquent chez le nourrisson (90 % organiques). **B** faux : jamais diastolique. **C** faux : intensité < 3/6. **E** faux : pas d'irradiation dorsale.

---

## QRU 2

Un enfant de 1 mois vous est présenté pour défaut de croissance staturo-pondérale. Il prend ses biberons en plusieurs fois, semble s'essouffler. L'enfant est rose avec des saturations à 100 % au repos. L'auscultation révèle un souffle intense, 4/6, au 4e espace intercostal. Ce souffle irradie tout autour de ce foyer en rayon de roue. Le diagnostic le plus probable que vous suspectez est :

- A. Un canal artériel persistant
- B. Une communication interventriculaire
- C. Une sténose pulmonaire
- D. Une tétralogie de Fallot
- E. Un souffle innocent

**Réponse : B**

CIV large restrictive : souffle holosystolique intense (4/6), irradiation en rayon de roue au 4e EIC, signes d'IC du nourrisson (**B**). CAP = souffle continu (**A** faux). Fallot = cyanose tardive (**D** faux).

---

## QRM 3

Concernant la coarctation de l'aorte, indiquer les bonnes réponses :

- A. Elle est typiquement accompagnée d'un souffle diastolique irradiant dans le dos
- B. Elle est une cause d'hypertension artérielle systémique chez l'enfant
- C. Elle est associée à une diminution de la perception des pouls fémoraux
- D. Elle peut être associée à une hypertrophie ventriculaire gauche électrique
- E. Elle peut être associée à une bicuspidie aortique

**Réponse : B, C, D, E**

HTA, pouls fémoraux diminués, HVG à l'ECG, bicuspidie aortique associée fréquente (**B–E**). **A** faux : souffle **systolique** sous-claviculaire irradiant en interscapulaire, pas diastolique.

---

## QRM 4

Concernant l'auscultation précordiale de l'enfant :

- A. Le 2e bruit (B2) est presque toujours dédoublé de façon fixe
- B. Il n'y a généralement pas de corrélation entre l'intensité d'un souffle et la gravité de la cardiopathie sous-jacente
- C. Un rythme cardiaque variable doit faire évoquer une arythmie
- D. L'auscultation cardiaque est souvent parasitée par les bruits respiratoires chez le petit enfant
- E. La perception d'un 3e bruit (B3) est toujours pathologique

**Réponse : B, D**

Pas de corrélation intensité/gravité ; auscultation difficile chez le petit enfant (cris, agitation) (**B**, **D**). DB2 **variable** physiologique, fixe = anormal mais pas « presque toujours fixe » (**A** faux). Variabilité = arythmie sinusale respiratoire physiologique (**C** faux). B3 fréquent et physiologique à l'apex (**E** faux).
'''


def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    if line in FLOWCHART_GARBAGE:
        return None
    if re.match(r"^(262|263|264|265|266|267|268|269|270|271|272|273|274)$", line):
        return None
    if re.match(r"^[A-G]$", line) and len(line) == 1:
        return None
    if line.startswith("El "):
        line = "• " + line[3:]
    line = line.replace("011 ", "• ")
    line = line.replace("1 52", "152")
    line = line.replace("1 53", "153")
    line = line.replace("2 38", "238")
    line = line.replace("2 1", "21")
    line = line.replace("1 1 .", "11.")
    line = line.replace("1 1.", "11.")
    line = line.replace("fig. 1 1", "fig. 11")
    line = line.replace("Fig. 1 1", "Fig. 11")
    line = line.replace("1 re", "1re")
    line = line.replace("1 €r", "1re")
    line = line.replace("Ve intention", "1re intention")
    line = line.replace("Item 2 38", "Item 238")
    line = line.replace("Fallût", "Fallot")
    line = line.replace("slnusale", "sinusale")
    line = line.replace("l!insuffisance", "L'insuffisance")
    line = line.replace("type die n'", "type clic n'")
    line = line.replace("trisomique 2 1", "trisomique 21")
    line = line.replace("22q1 1", "22q11")
    line = line.replace("264 j", "")
    line = line.replace("268 j", "")
    line = line.replace("270 j", "")
    line = line.replace("272", "272")
    line = line.replace("I 160", "160")
    line = line.replace("I 308", "308")
    line = line.replace("HTAP)", "HTAP)")
    line = re.sub(r"^C Symptômes", "C. Symptômes", line)
    line = re.sub(r"^• 0 ", "• **Rang A.** ", line)
    for prefix, repl in (("• O ", "• **Rang A.** "), ("• □ ", "• **Rang B.** "), ("• Q ", "• **Rang A.** ")):
        if line.startswith(prefix):
            line = repl + line[len(prefix):]
            break
    for prefix, repl in (
        ("□ ", "**Rang B.** "),
        ("O ", "**Rang A.** "),
        ("Q ", "**Rang A.** "),
    ):
        if line.startswith(prefix):
            rest = line[len(prefix):]
            if rest and rest[0].islower():
                break
            line = repl + rest
            break
    # Fix figure captions OCR (keep figure number)
    line = re.sub(r"^(Fig\. 11\.\d+)\. El ", r"\1. ", line)
    line = re.sub(r"^(Fig\. 11\.\d+)\. G ", r"\1. ", line)
    line = re.sub(r"^(Fig\. 11\.\d+)\. S ", r"\1. ", line)
    return line


def match_section(cl):
    if cl.startswith("de l'âge"):
        return None
    for sec, hdr in SECTION_MAP.items():
        if cl == sec or cl.startswith(sec):
            return hdr
    return None


def extract_footer(text):
    notions_ind, notions_inacc, reflexes = [], [], []
    mode = None
    for raw in text.splitlines():
        cl = clean_line(raw)
        if cl is None:
            continue
        if cl.startswith("Notions indispensables") and "inacceptables" not in cl.lower():
            mode = "ind"
            continue
        if cl.startswith("Notions inacceptables") or cl.startswith("Notions Inacceptables"):
            mode = "inacc"
            continue
        if cl.startswith("Réflexes transversalité"):
            mode = "reflex"
            continue
        if cl.startswith("► Entraînement"):
            break
        if mode == "ind":
            notions_ind.append(cl if cl.startswith("•") else "• " + cl)
        elif mode == "inacc":
            notions_inacc.append(cl if cl.startswith("•") else "• " + cl)
        elif mode == "reflex":
            txt = cl.replace("Item 2 38", "Item 238").replace("Item 1 52", "Item 152")
            txt = txt.replace("Item 1 53", "Item 153").replace("Item 53", "Item 53")
            reflexes.append(txt if txt.startswith("•") else "• " + txt)
    return notions_ind, notions_inacc, reflexes


def extract_body():
    text = SRC.read_text(encoding="utf-8")
    stop_idx = text.find("===== PDF PAGE 306 =====")
    if stop_idx == -1:
        stop_idx = text.find("Item 342")
    chunk = text[:stop_idx] if stop_idx != -1 else text

    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False
    points_manual_done = False
    in_pourquoi = False
    fig_caption_lines = 0

    for line in chunk.splitlines():
        cl = clean_line(line)
        if cl is None:
            continue
        if skip_until_vignette:
            if cl.startswith("Vignette clinique") or cl.startswith("Vous êtes médecin"):
                skip_until_vignette = False
                lines_out.append("## Vignette clinique\n")
                if not cl.startswith("Vignette"):
                    lines_out.append(cl)
                continue
            continue
        if cl.startswith("Notions indispensables"):
            break
        if cl.startswith("Pourquoi entend-on un souffle fonctionnel"):
            lines_out.append("\n\n### Pourquoi entend-on un souffle fonctionnel ?\n")
            in_pourquoi = True
            continue
        if in_pourquoi and cl.startswith("Points"):
            in_pourquoi = False
        elif in_pourquoi:
            lines_out.append(cl)
            continue
        if cl.startswith("Points") and not in_points:
            lines_out.append("\n\n---\n\n## Points\n")
            if not points_manual_done:
                lines_out.append(POINTS_BLOCK)
                points_manual_done = True
            in_points = True
            in_body = False
            continue
        if in_points:
            continue
        hdr = match_section(cl)
        if hdr:
            lines_out.append(hdr)
            in_body = True
            fig_caption_lines = 0
            continue
        if cl.startswith("de l'âge") and in_body:
            continue
        # Subsection letter without dot fix
        if re.match(r"^C\s+Symptômes", cl):
            lines_out.append("\n## C. Symptômes extracardiaques\n")
            continue
        if cl.startswith("Il n'y a généralement pas de corrélation"):
            lines_out.append(f"\n> {cl}\n")
            continue
        if fig_caption_lines > 0:
            if cl.startswith("Fig.") or cl.startswith("###") or cl.startswith("##"):
                fig_caption_lines = 0
            elif fig_caption_lines <= 2:
                lines_out.append(cl)
                fig_caption_lines += 1
                continue
            else:
                fig_caption_lines = 0
        m = SUBSECTION_RE.match(cl)
        if m and in_body and len(cl) < 120:
            lines_out.append(f"\n## {m.group(1)}\n")
            continue
        m2 = NUM_SUBSECTION_RE.match(cl)
        if m2 and in_body and len(cl) < 120:
            lines_out.append(f"\n### {m2.group(1)}\n")
            continue
        fig_handled = False
        fig_m = re.match(r"^Fig\.\s*(11\.\d+)", cl, re.I)
        if fig_m:
            fig_key = f"Fig. {fig_m.group(1)}"
            if fig_key in FIG_MAP:
                fname, caption = FIG_MAP[fig_key]
                lines_out.append(f"\n![{caption}](./img/{fname})\n")
                cap = re.sub(r"^Fig\.\s*11\.\d+\.\s*", "", cl)
                lines_out.append(f"\n**Fig. {fig_m.group(1)}.** {cap.strip()}\n")
                fig_caption_lines = 1
                fig_handled = True
        if fig_handled:
            continue
        if cl.startswith("> "):
            lines_out.append(cl)
        elif cl.startswith(">"):
            lines_out.append("> " + cl[1:].strip())
        elif cl.startswith("- ") or cl.startswith("• "):
            lines_out.append(cl)
        elif cl == "•":
            continue
        else:
            lines_out.append(cl)
    return "\n".join(lines_out)


def postprocess(text):
    text = re.sub(r">\s*\n+\s*", "> ", text)
    text = re.sub(r"\*\*Rang [AB]\.\*\*\s*\n+\*\*Rang [AB]\.\*\*", "**Rang A.**", text)
    fixes = [
        ("cardio- pathie", "cardiopathie"), ("auscul- tation", "auscultation"),
        ("sous- jacente", "sous-jacente"), ("valvulo- pathies", "valvulopathies"),
        ("anatomique sous- jacente", "anatomique sous-jacente"),
        ("staturopondéral", "staturopondéral"), ("broncho- pulmonaire", "bronchopulmonaire"),
        ("gastro- intestinale", "gastro-intestinale"), ("écho- cardiographie", "échocardiographie"),
        ("\'IRM", "l'IRM"),         ("Fallût", "Fallot"), ("l!insuffisance", "L'insuffisance"),
        ("malaclic", "maladie"), ("sousjacente", "sous-jacente"),
        ("anatomique sousjacente", "anatomique sous-jacente"),
        ("**Rang B.** II pratique", "**Rang B.** Il pratique"),
        ("heartdefect", "heart defect"), ("génital hypoplasia", "genital hypoplasia"),
        ("Item 2 38", "Item 238"), ("2 38", "238"), ("1 1.", "11."),
        ("ou « innocents »)\n\n•", "•"),
        ("cardiaque Il peut", "cardiaque\n\nIl peut"),
        ("malformatives Il s'agit", "malformatives\n\nIl s'agit"),
        ("('hypervascularisation", "(l'hypervascularisation"),
        ("(l'hypervascularisation pulmonaire. la persistance",
         "(l'hypervascularisation pulmonaire.\n\n• la persistance"),
        ("fig. 11.1 et 11.2", "fig. 11.1 et 11.2"),
        ("(fig. 11.3)", "(fig. 11.3)"),
        ("(fig. 11.5)", "(fig. 11.5)"),
        ("(fig. 11.6)", "(fig. 11.6)"),
        ("• Insuffisance", "L'insuffisance"),
        ("• l'insuffisance", "L'insuffisance"),
    ]
    for old, new in fixes:
        text = text.replace(old, new)
    text = re.sub(r"\s*===== PDF PAGE \d+ =====\s*", " ", text)
    text = re.sub(r"(?<=\w)-\s+(?=[a-zàâéèêëîïôùûü])", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"Ce livre a été acheté.*?https://t\.me/Faille_V2\s*", " ", text, flags=re.S)
    text = re.sub(r"> 5/MP.*?55:45 AM", "", text, flags=re.S)
    text = re.sub(r"\n\n•\n\n", "\n\n• ", text)
    text = re.sub(
        r"## C\. Dans la deuxième enfance \(de 2 à 16 ans\) : cardiopathies\n\n\n\nmalformatives",
        "## C. Dans la deuxième enfance (de 2 à 16 ans) : cardiopathies malformatives",
        text,
    )
    text = re.sub(r"\n\n-\n", "\n• ", text)
    text = re.sub(r"• \*\*Rang A\.\*\* \*\*Rang A\.\*\*", "• **Rang A.**", text)
    text = re.sub(r"• \*\*Rang A\.\*\* La découverte", "• La découverte", text)
    text = re.sub(r"\*\*Rang A\.\*\* Ils sont souvent", "**Rang A.** Ils sont souvent", text)
    # Vignette questions as blockquotes
    text = re.sub(
        r"(3 ans, qui vient pour un écoulement nasal fébrile\.[^\n]+)\n> Vous rassurez",
        r"\1\n\n> Vous rassurez",
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
        if line.strip() == "-":
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append("•")
            continue
        if line.startswith(("#", "##", "###", "**", "-", "•", ">", "!", "|", "---", "![", "**Tableau", "**Points")):
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append(line)
        else:
            buf.append(line.strip())
    if buf:
        paragraphs.append(" ".join(buf))
    return "\n\n".join(p for p in paragraphs if p is not None)


def make_footer(notions_ind, notions_inacc, reflexes):
    ind = "\n".join(n if n.startswith("•") else "• " + n for n in notions_ind) or "• (Voir cours.)"
    inacc = "\n".join(n if n.startswith("•") else "• " + n for n in notions_inacc) or "• (Voir cours.)"
    refl = "\n".join(r if r.startswith("•") else "• " + r for r in reflexes)
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

Questions isolées et corrigés : [Entrainement/QI/238_Souffle_cardiaque_enfant.md](../../Entrainement/QI/238_Souffle_cardiaque_enfant.md)
"""


def build_course():
    text = SRC.read_text(encoding="utf-8")
    body = extract_body()
    body = postprocess(body)
    body = merge_paragraphs(body)
    notions_ind, notions_inacc, reflexes = extract_footer(text)
    content = HEADER + body + make_footer(notions_ind, notions_inacc, reflexes)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(content, encoding="utf-8")
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
    extracted = set()
    for fig_num, fname, page_idx in FIGURES:
        if page_idx >= len(doc):
            print(f"Skip {fig_num}: page index {page_idx} out of range")
            continue
        page = doc[page_idx]
        label = f"Fig. {fig_num}"
        hits = page.search_for(label)
        if not hits:
            for alt in (f"Fig. {fig_num}.", f"fig. {fig_num}"):
                hits = page.search_for(alt)
                if hits:
                    break
        if not hits:
            print(f"WARN: {label} not found on page {page_idx + 1}")
            continue
        if fig_num == "11.2" and len(hits) > 1:
            idx = 1
        elif fig_num == "11.4" and len(hits) > 1:
            idx = 1
        else:
            idx = 0
        r = hits[idx]
        tall = {"11.1", "11.3", "11.5", "11.6"}
        height = 420 if fig_num in tall else 350
        y1 = min(page.rect.height, r.y1 + height)
        clip = fitz.Rect(25, max(0, r.y0 - 15), page.rect.width - 25, y1)
        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
        out = IMG_DIR / fname
        pix.save(str(out))
        extracted.add(fig_num)
        print(f"Figure {fig_num} -> {out} ({out.stat().st_size} bytes)")
    if "11.2" not in extracted and "11.1" in extracted:
        src = IMG_DIR / "fig_11_1_coarctation_neonat.png"
        dst = IMG_DIR / "fig_11_2_coarctation.png"
        if src.exists() and not dst.exists():
            dst.write_bytes(src.read_bytes())
            print(f"Figure 11.2 -> copied from 11.1 (no separate label in PDF)")
    doc.close()


def update_readme():
    text = README.read_text(encoding="utf-8")
    row = "| Fait | 238 Souffle cardiaque enfant | [II_Valves/238_Souffle_cardiaque_enfant.md](./II_Valves/238_Souffle_cardiaque_enfant.md) |\n"
    if "238 Souffle" not in text:
        text = text.replace("| À faire | … | lots suivants |", row + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 238")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    sections = re.findall(r"^# [IVX]+\.", content, re.M)
    fig_count = len(list(IMG_DIR.glob("fig_11_*.png")))
    ok = size > 20_000 and len(sections) >= 6 and fig_count >= 5
    print(f"Course size: {size} bytes, section headers: {len(sections)} ({sections})")
    print(f"Figures: {fig_count} PNGs")
    if not ok:
        print("WARN: verification thresholds not met")
    return ok


def main():
    build_course()
    build_qi()
    extract_figures()
    update_readme()
    verify()


if __name__ == "__main__":
    main()
