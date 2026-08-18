# -*- coding: utf-8 -*-
"""Generate item 203 dyspnée aiguë et chronique markdown + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item203.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Cours" / "IV_IC" / "203_Dyspnee_aigue_chronique.md"
IMG_DIR = OUT.parent / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "203_Dyspnee.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"Pour avoir plus d’exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Insuffisance cardiaque\s*$",
    r"^CHAPITRE\s*$",
    r"^17\s*$",
    r"^18\s*$",
    r"^Item 203\s*$",
    r"^Item 203 -.*",
    r"^Dyspnée aiguë\s*$",
    r"^et chronique\s*$",
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
    r"^===== PDF PAGE \d+ =====$",
    r"^O QRM\s*\d+.*",
    r"^QQRU2.*",
    r"^QRU\s*\d+.*",
    r"^QRM\s*\d+.*",
    r"^Médecine cardiovasculaire\s*$",
    r"^CEMIR \(.*",
    r"^- réanimation\).*",
    r"^urgences et défaillances.*",
    r"^Paris ; Elsevier Masson.*",
    r"^CEP\. \(Collège.*",
    r"^pneumologie - Rangs.*",
    r"^S-Éditions; 2021\..*",
    r"^Item 234\s*$",
    r"^de l'adulte\s*$",
    r"^v Item 234.*",
    r"^CHAPITf\s*$",
    r"^\[ \s*$",
    r"^424 \|\s*$",
]

FLOW_GARBAGE = {
    "Syndrome pleural ?", "Non", "Oui", "Embolie pulmonaire", "Dyspnée isolée",
    "Sepsis sévère", "Psychogène", "Anémie", "Acidose", "Atteinte neuromusculaire",
    "BPCO", "OAP", "Asthme",
}

SECTION_MAP = {
    "I. Généralités": "\n\n# I. Généralités\n\n**Rang A.**",
    "II. Orientation diagnostique devant une dyspnée": (
        "\n\n---\n\n# II. Orientation diagnostique devant une dyspnée aiguë\n\n**Rang A.**"
    ),
    "II. Orientation diagnostique devant une dyspnée aiguë": (
        "\n\n---\n\n# II. Orientation diagnostique devant une dyspnée aiguë\n\n**Rang A.**"
    ),
    "III. Orientation diagnostique devant une dyspnée": (
        "\n\n---\n\n# III. Orientation diagnostique devant une dyspnée chronique\n\n**Rang A.**"
    ),
    "III. Orientation diagnostique devant une dyspnée chronique": (
        "\n\n---\n\n# III. Orientation diagnostique devant une dyspnée chronique\n\n**Rang A.**"
    ),
}

SUBSECTION_RE = re.compile(r"^([A-E]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")

ENCADRE_17_1 = """
**Encadré 17.1 — Étiologies principales des dyspnées aiguës et chroniques**

### Dyspnées aiguës

1. **Étiologies d'origine cardiaque** — OAP, pseudoasthme cardiaque, tamponnade, troubles du rythme mal tolérés, choc cardiogénique
2. **Embolie pulmonaire**
3. **Pulmonaires et pleurales** — crise d'asthme, exacerbation de BPCO, pneumopathie, SDRA, décompensation d'une IRC, atélectasie, pneumothorax, épanchement pleural, traumatisme thoracique
4. **Laryngotrachéales** — œdème de Quincke, corps étranger, épiglottite/laryngite (enfant), sténose tumorale, granulome post-intubation
5. **Autres** — choc, acidose métabolique, causes neurologiques (bulbares, polyradiculonévrite, myasthénie), anémie aiguë, hyperthermie, intoxication CO, hyperventilation psychogène

### Dyspnées chroniques

1. **Cardiaques** — insuffisance cardiaque, constriction péricardique
2. **Pulmonaires et pleurales** — BPCO, asthme à dyspnée continue, PID, pneumoconioses, séquelles pleurales, paralysie phrénique, cyphoscoliose
3. **HTAP** — idiopathique, familiale, connectivite (sclérodermie), shunt, VIH, toxique
4. **HTP post-embolique**
5. **Autres** — obstacles VAS, anémie, acidose, neuromusculaire, dyspnée psychogène, troubles du transport de l'O2, intoxication CO
"""

POINTS_BLOCK = """
• Devant une dyspnée aiguë, le bilan de 1re intention associe : clinique, radiographie du thorax, ECG, NFS, D-dimères, BNP (ou NT-proBNP), gazométrie.

• D'autres examens sont discutés selon l'orientation : EFR, échographie cardiaque, scintigraphie V/Q, angioscanner thoracique.

• Étiologies les plus fréquentes de dyspnée aiguë chez l'adulte : OAP, embolie pulmonaire, décompensation d'une pathologie respiratoire.

• Attention au diagnostic d'OAP souvent porté par excès chez les patients BPCO avec encombrement trachéobronchique.

• Tableaux trompeurs : pseudoasthme cardiaque (subœdème pulmonaire bronchospastique) ; EP sur terrain broncho-emphysémateux.

• Les causes extrathoraciques (acidose, anémie) entraînent davantage une polypnée qu'une dyspnée.

• Chez l'enfant : corps étranger, laryngite, épiglottite.

• Gravité souvent sous-estimée : causes laryngées (Quincke), neuromusculaires (polyradiculonévrites). Le SDRA est une urgence de réanimation.

• Dyspnées chroniques : nombreuses, le plus souvent cardiaques ou pulmonaires.
"""

HEADER = '''# Item 203 — Dyspnée aiguë et chronique

> **Collège CNEC / SFC** · 3e édition (2025) · p. 411–424 · R2C  
> Partie IV — Insuffisance cardiaque

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
20 Découverte d'anomalies à l'auscultation pulmonaire.  
145 Douleur pharyngée.  
149 Ingestion ou inhalation d'un corps étranger.  
160 Détresse respiratoire aiguë.  
162 Dyspnée.  
163 Expectoration.  
167 Toux.  
223 Interprétation de l'hémogramme.  
283 Consultation de suivi et éducation thérapeutique d'un patient asthmatique.  
285 Consultation de suivi et éducation thérapeutique d'un patient avec un antécédent cardiovasculaire.  
286 Consultation de suivi et éducation thérapeutique d'un patient BPCO.  
287 Consultation de suivi et éducation thérapeutique d'un patient insuffisant cardiaque.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Dyspnée, inspiratoire / expiratoire | |
| **A** | Diagnostic positif | Examen clinique d'un patient dyspnéique | |
| **A** | Étiologies | Principales étiologies d'une dyspnée aiguë | OAP, EP, asthme, BPCO, pneumopathie, PNO, SDRA, corps étranger, Quincke, anémie |
| **A** | Diagnostic positif | Signes de gravité d'une dyspnée aiguë | |
| **A** | Diagnostic positif | Orientation diagnostique d'une dyspnée chronique | |
| **A** | Étiologies | Signes d'orientation étiologique | |
| **A** | Examens complémentaires | Examens de 1re intention selon aigu/chronique | |
| **A** | Examens complémentaires | Examens de 2e intention | |
| **B** | Étiologies | Étiologies plus rares | |

---

## Parcours Rang A

- [I. Généralités](#i-généralités)
- [II. Orientation diagnostique devant une dyspnée aiguë](#ii-orientation-diagnostique-devant-une-dyspnée-aiguë)
- [III. Orientation diagnostique devant une dyspnée chronique](#iii-orientation-diagnostique-devant-une-dyspnée-chronique)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Généralités](#i-généralités)
- [II. Orientation diagnostique devant une dyspnée aiguë](#ii-orientation-diagnostique-devant-une-dyspnée-aiguë)
- [III. Orientation diagnostique devant une dyspnée chronique](#iii-orientation-diagnostique-devant-une-dyspnée-chronique)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/203_Dyspnee.md)

---

'''

QI_CONTENT = '''# Entraînement — Item 203 Dyspnée aiguë et chronique

> Collège CNEC 3e éd. · Chapitre 17 · corrigés p. 585  
> Cours : [203 Dyspnée](../../Cours/IV_IC/203_Dyspnee_aigue_chronique.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRM 1

Devant une dyspnée aiguë, quels sont les facteurs qui orientent vers une insuffisance cardiaque ?

- A. Antécédent d'infarctus du myocarde
- B. Fièvre
- C. Turgescence jugulaire
- D. Fibrillation atriale sur l'ECG
- E. Augmentation du BNP > 500 pg/mL

**Réponse : A, C, D, E**

Terrain ischémique (1re cause d'IC), turgescence jugulaire (IC droite), FA (facteur déclenchant et cause), BNP nettement élevé (**A**, **C**, **D**, **E**). La fièvre oriente plutôt vers une cause infectieuse (**B** faux).

---

## QRU 2

M. A., 72 ans, est hospitalisé pour une dyspnée aiguë. Quel élément permet d'éliminer une insuffisance cardiaque ?

- A. FEVG > 50 %
- B. BNP = 50 pg/mL
- C. Épanchement pleural
- D. D-dimères à 800 pg/L
- E. Troponine normale

**Réponse : B**

Un BNP < 100 pg/mL oriente vers un autre diagnostic (**B**). L'IC à FE préservée est fréquente : une FEVG normale n'élimine pas l'IC (**A** faux). Épanchement pleural possible dans l'IC. D-dimères peu spécifiques. Troponine normale n'exclut pas l'IC.

---

## QRM 3

Mme B, 75 ans, consulte car elle présente depuis plusieurs jours un essoufflement anormal à la montée de ses deux étages. Elle a comme seuls antécédents une HTA traitée par amlodipine et a été opérée il y a 2 mois d'une prothèse de genou. À l'examen, elle est eupnéique au repos, sa fréquence cardiaque est à 96/min, sans galop. Quels sont les arguments à retenir en faveur d'une EP ?

- A. L'âge
- B. Le sexe
- C. L'HTA
- D. L'antécédent de prothèse de genou
- E. Le score de Genève = 3

**Réponse : A, D, E**

Âge > 65 ans = critère de Genève (**A**). Prothèse de genou il y a 2 mois : hors score (chirurgie < 1 mois) mais facteur de risque temporaire si < 3 mois (**D**). Genève = 3 (âge + FC ≥ 95) (**E**). Sexe et HTA ne sont pas des arguments ici (**B**, **C** faux).

---

## QRM 4

M. C, 68 ans, diabétique de type 2, hypertendu et obèse, se présente aux urgences pour une détresse respiratoire aiguë qui a commencé dans la nuit. Quels sont les arguments pour un œdème aigu pulmonaire ?

- A. Crépitants dans les deux champs pulmonaires
- B. Opacités floconneuses bilatérales périhilaires sur la radiographie de thorax
- C. Hypoxémie à 60 mmHg
- D. NT-proBNP = 150 pg/mL
- E. Tachycardie

**Réponse : A, B**

Crépitants bilatéraux et œdème alvéolaire périhilaire orientent vers l'OAP (**A**, **B**). Une hypoxémie à 60 mmHg se voit dans d'autres détresses respiratoires (**C** faux). NT-proBNP < 300 pg/mL plaide plutôt contre l'IC (**D** faux). La tachycardie n'est pas spécifique (**E** faux).
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
    if re.match(r"^(411|412|413|414|415|416|417|418|419|420|421|422|423|424)$", line):
        return None
    if re.match(r"^[A-G]$", line) and len(line) == 1:
        return None
    line = line.replace("Mme, X 69", "Mme X, 69")
    line = re.sub(r"^• 0 ", "• **Rang A.** ", line)
    for prefix, repl in (("• O ", "• **Rang A.** "), ("• □ ", "• **Rang B.** ")):
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
    return line


def match_section(cl):
    if cl.startswith("aiguë (encadré") or cl.startswith("chronique (cf."):
        return None
    for sec, hdr in SECTION_MAP.items():
        if cl == sec or cl.startswith(sec):
            return hdr
    return None


def extract_footer(text):
    notions_ind, notions_inacc, reflexes = [], [], []
    mode = None
    for raw in text.splitlines():
        raw_s = raw.strip()
        if raw_s.startswith("► Entraînement") or raw_s.startswith("O QRM") or raw_s.startswith("Pour en savoir plus"):
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
        stop = text.find("===== PDF PAGE 455")
    chunk = text[:stop] if stop != -1 else text

    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False
    pending_bullet = None
    skip_encadre = False
    skip_flow = False
    encadre_done = False
    points_done = False

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
        if (cl.startswith("Devant une dyspnée aiguë, le bilan") or cl.startswith("• Devant une dyspnée")) and not points_done:
            lines_out.append("\n\n---\n\n## Points\n")
            lines_out.append(POINTS_BLOCK)
            points_done = True
            in_points = True
            continue
        if in_points:
            continue

        if skip_encadre:
            if cl.startswith("La dyspnée aiguë est un motif") or cl.startswith("A. Étiologies d'origine cardiaque"):
                skip_encadre = False
            else:
                continue
        if skip_flow:
            if cl.startswith("Fig. 17.1") or cl.startswith("III."):
                skip_flow = False
            else:
                continue

        hdr = match_section(cl)
        if hdr:
            lines_out.append(hdr)
            in_body = True
            if "aiguë" in hdr and not encadre_done:
                lines_out.append(ENCADRE_17_1)
                encadre_done = True
            continue

        if cl.startswith("Encadré 17.1"):
            if not encadre_done:
                lines_out.append(ENCADRE_17_1)
                encadre_done = True
            skip_encadre = True
            continue

        if cl.startswith("Fig. 17.1"):
            lines_out.append("\n![Fig. 17.1 — Arbre décisionnel en cas de dyspnée aiguë](./img/fig_17_1_arbre_dyspnee.png)\n")
            lines_out.append("\n**Fig. 17.1.** Arbre décisionnel en cas de dyspnée aiguë.\n")
            skip_flow = False
            continue

        if "La figure 17.1" in cl or "fig. 17.1" in cl.lower() and "Arbre" not in cl:
            skip_flow = True

        m = SUBSECTION_RE.match(cl)
        if m and in_body and len(cl) < 140:
            lines_out.append(f"\n## {m.group(1)}\n")
            continue
        m2 = NUM_SUBSECTION_RE.match(cl)
        if m2 and in_body and len(cl) < 120:
            lines_out.append(f"\n### {m2.group(1)}\n")
            continue

        if cl.startswith("> "):
            lines_out.append(cl)
        elif cl.startswith(">"):
            lines_out.append("> " + cl[1:].strip())
        elif cl.startswith("- ") or cl.startswith("• "):
            lines_out.append(cl)
        else:
            lines_out.append(cl)
    if not points_done:
        lines_out.append("\n\n---\n\n## Points\n")
        lines_out.append(POINTS_BLOCK)
    return "\n".join(lines_out)


def postprocess(text):
    text = re.sub(r">\s*\n+\s*", "> ", text)
    text = re.sub(r"(?<=\w)-\s+(?=[a-zàâéèêëîïôùûü])", "", text)
    text = re.sub(r"Pour avoir plus d['’]exclusivités.*?Faille_V2\s*", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(
        r"(> À l'interrogatoire, comment caractérisez-vous la dyspnée et comment évaluez-vous son importance)\n\n(et retentissement)",
        r"\1 \2",
        text,
    )
    text = re.sub(r"\n\naiguë \(encadré 17\.1\)\n\n", "\n\n", text)
    text = re.sub(r"\n\nchronique \(cf\. encadré 17\.1\)\n\n", "\n\n", text)
    if "fig_17_1_arbre_dyspnee.png" not in text:
        text = text.replace(
            "# III. Orientation diagnostique devant une dyspnée chronique",
            "![Fig. 17.1 — Arbre décisionnel en cas de dyspnée aiguë](./img/fig_17_1_arbre_dyspnee.png)\n\n**Fig. 17.1.** Arbre décisionnel en cas de dyspnée aiguë.\n\n# III. Orientation diagnostique devant une dyspnée chronique",
            1,
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
        "• Connaître la classification NYHA.\n"
        "• Connaître les signes de gravité devant une dyspnée aiguë.\n"
        "• Savoir la conduite à tenir devant une dyspnée aiguë.\n"
        "• Savoir aussi penser aux causes extracardiaques et extrapulmonaires de dyspnée (anémie, causes ORL, etc.)."
    )
    inacc = "\n".join(n if n.startswith("•") else "• " + n for n in notions_inacc) or (
        "• Oublier les examens à prescrire en 1re intention devant une dyspnée aiguë."
    )
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

Questions isolées et corrigés : [Entrainement/QI/203_Dyspnee.md](../../Entrainement/QI/203_Dyspnee.md)
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
        return
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF)
    page = doc[449]  # PDF page 450
    hits = page.search_for("Fig. 17.1")
    if hits:
        r = max(hits, key=lambda x: x.y0)
        y0 = max(0, r.y0 - 420)
        clip = fitz.Rect(18, y0, page.rect.width - 18, min(page.rect.height, r.y1 + 28))
    else:
        clip = fitz.Rect(18, 80, page.rect.width - 18, 720)
        print("WARN: Fig. 17.1 not found")
    pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
    out = IMG_DIR / "fig_17_1_arbre_dyspnee.png"
    pix.save(str(out))
    print(f"Figure 17.1 -> {out} ({out.stat().st_size} bytes)")
    doc.close()


def update_readme():
    text = README.read_text(encoding="utf-8")
    row = "| Fait | 203 Dyspnée aiguë et chronique | [IV_IC/203_Dyspnee_aigue_chronique.md](./IV_IC/203_Dyspnee_aigue_chronique.md) |\n"
    if "203 Dyspnée" not in text:
        text = text.replace("| À faire | … | lots suivants |", row + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 203")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    sections = re.findall(r"^# [IVX]+\.", content, re.M)
    print(f"Course size: {size} bytes, section headers: {len(sections)} ({sections})")
    if size < 15_000 or len(sections) < 3:
        print("WARN: verification thresholds not met")
    if "Item 234" in content.split("## Réflexes")[0]:
        print("WARN: Item 234 leak")


def main():
    build_course()
    build_qi()
    extract_figures()
    update_readme()
    verify()


if __name__ == "__main__":
    main()
