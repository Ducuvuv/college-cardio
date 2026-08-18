# -*- coding: utf-8 -*-
"""Generate item 233 valvulopathies markdown (RA, IM, IA) + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401 — legacy pymupdf alias

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item233.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT_DIR = ROOT / "Cours" / "II_Valves"
IMG_DIR = OUT_DIR / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "233_Valvulopathies.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Maladies des valves\s*$",
    r"^Item 233\s*$",
    r"^Item 233 - Valvulopathies\s*$",
    r"^Valvulopathies\s*$",
    r"^Situations de départ\s*$",
    r"^Hiérarchisation des connai.*",
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
    r"^nts\s*$",
    r"^Ce\s*$",
    r"^S\s*$",
    r"^ëf\s*$",
    r"^\*' ric,8m.*",
    r"^“ I” interdite.*",
    r"^à l'entraînement de l'intelligence artificielle.*",
    r"^!St strictement interdite.*",
    r"^: sur https://t\.me/Faille_V2\s*$",
    r"^[\d\s\.ÏHWMflBï\.]+$",
    r"^BH HW1.*",
    r"^BB B Bfl.*",
    r"^®\s+H il H.*",
    r"^VL\s*$",
    r"^il\.\s*$",
    r"^VIL\s*$",
    r"^VI\.\s*$",
    r"^V\.\s*$",
    r"^I\.\s*$",
    r"^II\.\s*$",
    r"^III\.\s*$",
    r"^IV\.\s*$",
    r"^VIII\.\s*$",
    r"^IX\.\s*$",
    r"^X\.\s*$",
    r"^O QRM\s*\d+.*",
    r"^© QRM\s*\d+.*",
    r"^G QRM\s*\d+.*",
    r"^QRM\s*\d+.*",
    r"^QRU\s*\d+.*",
    r"^Obadia JF.*",
    r"^Otto CM.*",
    r"^Vahanian A.*",
    r"^Cormier B.*",
    r"^Delgado V.*",
    r"^Lancellotti P.*",
    r"^Erwm JP.*",
    r"^Erwin JP.*",
    r"^ACCZ\s*$",
    r"^□\s*$",
    r"^S\s*$",
    r"^L\s*$",
    r"^A\s*$",
    r"^B\s*$",
    r"^C\s*$",
    r"^D\s*$",
    r"^E\s*$",
    r"^G\s*$",
    r"^O\s*$",
    r"^===== PDF PAGE \d+ =====$",
    r"^B1\s*$",
    r"^B2\s*$",
    r"^Losangique\s*$",
    r"^2 5MHz FPHaut Moy\s*$",
    r"^Attention\s*$",
    r"^& La quantification.*",
    r"^Pour avoir plus d.exclusivités.*",
]

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")
ENCADRE_RE = re.compile(r"^Encadré 8\.\d")

SHARED_SITUATIONS = """18 Découverte d'anomalies à l'auscultation cardiaque.
20 Découverte d'anomalies à l'auscultation pulmonaire.
21 Asthénie.
22 Diminution de la diurèse.
44 Hyperthermie/fièvre.
50 Malaise/perte de connaissance.
160 Détresse respiratoire aiguë.
161 Douleur thoracique.
162 Dyspnée.
165 Palpitations.
166 Tachycardie.
178 Demande/prescription raisonnée et choix d'un examen diagnostique.
185 Réalisation et interprétation d'un électrocardiogramme (ECG).
190 Hémoculture positive.
203 Élévation de la protéine C-réactive (CRP).
230 Rédaction de la demande d'un examen d'imagerie.
231 Demande d'un examen d'imagerie.
232 Demande d'explication d'un patient sur le déroulement, les risques et les bénéfices attendus d'un examen d'imagerie.
233 Identifier/reconnaître les différents examens d'imagerie (type/fenêtre/séquences/incidences/injection).
239 Explication préopératoire et recueil de consentement d'un geste invasif diagnostique ou thérapeutique.
247 Prescription d'une rééducation.
248 Prescription et suivi d'un traitement par anticoagulant et/ou antiagrégant.
253 Prescrire des diurétiques.
255 Prescrire un anti-infectieux.
258 Prévention de la douleur liée aux soins.
259 Évaluation et prise en charge de la douleur aiguë.
271 Prescription et surveillance d'une voie d'abord vasculaire.
279 Consultation de suivi d'une pathologie chronique.
285 Consultation de suivi éducation thérapeutique d'un patient avec antécédents cardiovasculaires.
300 Consultation pré-anesthésique.
311 Prévention des infections liées aux soins.
314 Prévention des risques liés au tabac.
320 Prévention des maladies cardiovasculaires.
324 Modification thérapeutique du mode de vie (sommeil, activité physique, alimentation, etc.).
328 Annonce d'une maladie chronique.
334 Demande de traitement et investigation inappropriés.
335 Évaluation de l'aptitude au sport et rédaction d'un certificat de non-contre-indication.
339 Prescrire un arrêt de travail.
342 Rédaction d'une ordonnance/d'un courrier médical.
352 Expliquer un traitement au patient (adulte/enfant/adolescent).
354 Évaluation de l'observance thérapeutique.
355 Organisation de la sortie d'hospitalisation."""

SHARED_HIERARCH = """| **A** | Définition | Définition IM, RA, IA, RM | |
| **A** | Étiologies | Principales étiologies des valvulopathies (IM, RA, IA, RM) | |
| **A** | Diagnostic positif | Signes fonctionnels et auscultation IM, RA, IA, RM | |
| **A** | Examens complémentaires | Valeur primordiale de l'échocardiographie (IM, IA, RA, RM) | Diagnostic positif, mécanisme, étiologie, sévérité |
| **A** | Physiopathologie | Mécanismes et conséquences IM, IA, RA, RM | |
| **B** | Examens complémentaires | Intérêt ECG, radiographie thoracique, épreuve d'effort | |
| **B** | Suivi et/ou pronostic | Évolutions et complications IM, RA, IA, RM | |
| **B** | Prise en charge | Principes du traitement chirurgical IM, RA, IA, RM | Plastie ou remplacement valvulaire |
| **B** | Prise en charge | Traitements percutanés IM, RA, RM | TAVI ; alternative percutanée IM (MitraClip®) |
| **A** | Prise en charge | Indications chirurgicales IM, RA, RM, IA | |
| **A** | Prise en charge | Indications percutanées RA et IM | |
| **A** | Prise en charge | Modalités du traitement médical de l'IA | Bêtabloquant dans le Marfan |"""

FIGURES = [
    ("8.1", "fig_8_1_gradient_pressions.png", 196),
    ("8.2", "fig_8_2_souffle_ra.png", 198),
    ("8.3", "fig_8_3_hvg_ecg.png", 199),
    ("8.4", "fig_8_4_echo_doppler_ra.png", 200),
    ("8.5", "fig_8_5_bicuspidie.png", 202),
    ("8.7", "fig_8_7_im_secondaire.png", 210),
    ("8.10", "fig_8_10_prolapsus.png", 216),
    ("8.11", "fig_8_11_jet_im.png", 216),
    ("8.12", "fig_8_12_endocardite_im.png", 217),
    ("8.13", "fig_8_13_racine_aorte.png", 225),
    ("8.14", "fig_8_14_anatomie_valve_aortique.png", 225),
    ("8.15", "fig_8_15_bicuspidie_ia.png", 225),
    ("8.16", "fig_8_16_mecanisme_ia.png", 228),
    ("8.17", "fig_8_17_ia_types_1_2.png", 229),
    ("8.18", "fig_8_18_endocardite_ia.png", 229),
    ("8.19", "fig_8_19_ia_type_3.png", 230),
    ("8.20", "fig_8_20_rx_ia.png", 233),
    ("8.22", "fig_8_22_eval_vg_ia.png", 235),
    ("8.23", "fig_8_23_irm_aorte.png", 236),
]

VALVE_CONFIGS = {
    "ra": {
        "title": "Rétrécissement aortique",
        "slug": "233_RA_Retrecissement_aortique",
        "pages": "164–178",
        "start": "Rétrécissement aortique",
        "stop": "Insuffisance mitrale",
        "parcours": """- [I. Définition](#i-définition)
- [III. Physiopathologie](#iii-physiopathologie-et-conséquences-hémodynamiques)
- [V. Aspects cliniques](#v-aspects-cliniques)
- [VI. Examens complémentaires](#vi-examens-complémentaires)
- [VIII. Traitement](#viii-traitement)""",
        "sommaire": """- [Vignette clinique](#vignette-clinique)
- [I. Définition](#i-définition)
- [II. Rappel anatomique](#ii-rappel-anatomique)
- [III. Physiopathologie](#iii-physiopathologie-et-conséquences-hémodynamiques)
- [IV. Étiologies](#iv-étiologies)
- [V. Aspects cliniques](#v-aspects-cliniques)
- [VI. Examens complémentaires](#vi-examens-complémentaires)
- [VII. Évolution et complications](#vii-évolution-et-complications)
- [VIII. Traitement](#viii-traitement)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/233_Valvulopathies.md)""",
        "section_map": {
            "I. Définition": "\n\n# I. Définition\n\n**Rang A.**",
            "II. Rappel anatomique": "\n\n---\n\n# II. Rappel anatomique\n\n**Rang A.**",
            "III. Physiopathologie et conséquences": "\n\n---\n\n# III. Physiopathologie et conséquences hémodynamiques\n\n**Rang A** · **Rang B**.",
            "IV. Étiologies": "\n\n---\n\n# IV. Étiologies\n\n**Rang A** · **Rang B**.",
            "V. Aspects cliniques": "\n\n---\n\n# V. Aspects cliniques\n\n**Rang A** · **Rang B**.",
            "VI. Examens complémentaires": "\n\n---\n\n# VI. Examens complémentaires\n\n**Rang A** · **Rang B**.",
            "VII. Évolution et complications": "\n\n---\n\n# VII. Évolution et complications\n\n**Rang A** · **Rang B**.",
            "VIII. Traitement": "\n\n---\n\n# VIII. Traitement\n\n**Rang A** · **Rang B**.",
        },
        "fig_map": {
            "Fig. 8.1": ("fig_8_1_gradient_pressions.png", "Fig. 8.1 — Enregistrement cathétérisme des pressions aorte/VG"),
            "Fig. 8.2": ("fig_8_2_souffle_ra.png", "Fig. 8.2 — Souffle losangique du rétrécissement aortique"),
            "Fig. 8.3": ("fig_8_3_hvg_ecg.png", "Fig. 8.3 — HVG avec surcharge systolique à l'ECG"),
            "Fig. 8.4": ("fig_8_4_echo_doppler_ra.png", "Fig. 8.4 — Échocardiographie doppler transthoracique du RA"),
            "Fig. 8.5": ("fig_8_5_bicuspidie.png", "Fig. 8.5 — Valve aortique bicuspide (ETO 2D/3D)"),
        },
        "default_reflexes": [
            "Item 152 — Endocardite infectieuse.",
            "Item 153 — Surveillance des porteurs de valves et prothèses vasculaires.",
            "Item 342 — Malaises, perte de connaissance, crise comitiale de l'adulte.",
        ],
    },
    "im": {
        "title": "Insuffisance mitrale",
        "slug": "233_IM_Insuffisance_mitrale",
        "pages": "178–194",
        "start": "Insuffisance mitrale",
        "stop": "Insuffisance aortique",
        "parcours": """- [I. Définition](#i-définition)
- [IV. Étiologies](#iv-étiologies)
- [VI. Clinique](#vi-clinique)
- [VII. Examens complémentaires](#vii-examens-complémentaires)
- [IX. Traitement](#ix-traitement)""",
        "sommaire": """- [Vignette clinique](#vignette-clinique)
- [I. Définition](#i-définition)
- [II. Rappel anatomique et mécanismes](#ii-rappel-anatomique-et-mécanismes-de-la-fuite)
- [III. Physiopathologie](#iii-physiopathologie)
- [IV. Étiologies](#iv-étiologies)
- [V. Causes des IM aiguës](#v-causes-des-insuffisances-mitrales-aiguës)
- [VI. Clinique](#vi-clinique)
- [VII. Examens complémentaires](#vii-examens-complémentaires)
- [VIII. Évolution et complications](#viii-évolution-naturelle-et-complications)
- [IX. Traitement](#ix-traitement)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/233_Valvulopathies.md)""",
        "section_map": {
            "I. Définition": "\n\n# I. Définition\n\n**Rang A.**",
            "II. Rappel anatomique et mécanismes": "\n\n---\n\n# II. Rappel anatomique et mécanismes de la fuite\n\n**Rang A** · **Rang B**.",
            "III. Physiopathologie": "\n\n---\n\n# III. Physiopathologie\n\n**Rang A** · **Rang B**.",
            "IV. Étiologies": "\n\n---\n\n# IV. Étiologies\n\n**Rang A** · **Rang B**.",
            "V. Causes des insuffisances mitrales aiguës": "\n\n---\n\n# V. Causes des insuffisances mitrales aiguës\n\n**Rang A** · **Rang B**.",
            "VI. Clinique": "\n\n---\n\n# VI. Clinique\n\n**Rang A** · **Rang B**.",
            "VII. Examens complémentaires": "\n\n---\n\n# VII. Examens complémentaires\n\n**Rang A** · **Rang B**.",
            "VIII. Évolution naturelle et complications": "\n\n---\n\n# VIII. Évolution naturelle et complications\n\n**Rang A** · **Rang B**.",
            "IX. Traitement": "\n\n---\n\n# IX. Traitement\n\n**Rang A** · **Rang B**.",
        },
        "fig_map": {
            "Fig. 8.7": ("fig_8_7_im_secondaire.png", "Fig. 8.7 — Mécanismes de la fuite mitrale secondaire ventriculaire"),
            "Fig. 8.10": ("fig_8_10_prolapsus.png", "Fig. 8.10 — Prolapsus du feuillet postérieur"),
            "Fig. 8.11": ("fig_8_11_jet_im.png", "Fig. 8.11 — Jet d'insuffisance mitrale (doppler couleur)"),
            "Fig. 8.12": ("fig_8_12_endocardite_im.png", "Fig. 8.12 — Endocardite mitrale avec végétation"),
        },
        "default_reflexes": [
            "Item 152 — Endocardite infectieuse.",
            "Item 153 — Surveillance des porteurs de valves et prothèses vasculaires.",
        ],
    },
    "ia": {
        "title": "Insuffisance aortique",
        "slug": "233_IA_Insuffisance_aortique",
        "pages": "194–216",
        "start": "Insuffisance aortique",
        "stop": "Entraînement",
        "parcours": """- [I. Définition](#i-définition)
- [III. Physiopathologie](#iii-physiopathologie)
- [V. Clinique](#v-clinique)
- [VI. Examens complémentaires](#vi-examens-complémentaires)
- [X. Traitement](#x-traitement)""",
        "sommaire": """- [Vignette clinique](#vignette-clinique)
- [I. Définition](#i-définition)
- [II. Rappel anatomique](#ii-rappel-anatomique)
- [III. Physiopathologie](#iii-physiopathologie)
- [IV. Étiologies](#iv-étiologies)
- [V. Clinique](#v-clinique)
- [VI. Examens complémentaires](#vi-examens-complémentaires)
- [VII. Diagnostic différentiel](#vii-diagnostic-différentiel)
- [VIII. Évolution et complications](#viii-évolution-et-complications)
- [IX. Surveillance](#ix-surveillance)
- [X. Traitement](#x-traitement)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/233_Valvulopathies.md)""",
        "section_map": {
            "I. Définition": "\n\n# I. Définition\n\n**Rang A.**",
            "II. Rappel anatomique": "\n\n---\n\n# II. Rappel anatomique\n\n**Rang A.**",
            "III. Physiopathologie": "\n\n---\n\n# III. Physiopathologie\n\n**Rang A** · **Rang B**.",
            "IV. Étiologies": "\n\n---\n\n# IV. Étiologies\n\n**Rang A** · **Rang B**.",
            "V. Clinique": "\n\n---\n\n# V. Clinique\n\n**Rang A** · **Rang B**.",
            "VI. Examens complémentaires": "\n\n---\n\n# VI. Examens complémentaires\n\n**Rang A** · **Rang B**.",
            "VII. Diagnostic différentiel": "\n\n---\n\n# VII. Diagnostic différentiel\n\n**Rang B**.",
            "VIL Diagnostic différentiel": "\n\n---\n\n# VII. Diagnostic différentiel\n\n**Rang B**.",
            "VIII. Évolution et complications": "\n\n---\n\n# VIII. Évolution et complications\n\n**Rang A** · **Rang B**.",
            "IX. Surveillance": "\n\n---\n\n# IX. Surveillance\n\n**Rang A** · **Rang B**.",
            "X. Traitement": "\n\n---\n\n# X. Traitement\n\n**Rang A** · **Rang B**.",
        },
        "fig_map": {
            "Fig. 8.13": ("fig_8_13_racine_aorte.png", "Fig. 8.13 — Racine de l'aorte en échocardiographie"),
            "Fig. 8.14": ("fig_8_14_anatomie_valve_aortique.png", "Fig. 8.14 — Anatomie normale de la valve aortique"),
            "Fig. 8.15": ("fig_8_15_bicuspidie_ia.png", "Fig. 8.15 — Bicuspidie aortique"),
            "Fig. 8.16": ("fig_8_16_mecanisme_ia.png", "Fig. 8.16 — Mécanisme de fuite selon mobilité des cusps"),
            "Fig. 8.17": ("fig_8_17_ia_types_1_2.png", "Fig. 8.17 — Mécanisme de fuite aortique types 1 et 2"),
            "Fig. 8.18": ("fig_8_18_endocardite_ia.png", "Fig. 8.18 — Endocardites infectieuses aortiques"),
            "Fig. 8.19": ("fig_8_19_ia_type_3.png", "Fig. 8.19 — Mécanisme de fuite aortique type 3"),
            "Fig. 8.20": ("fig_8_20_rx_ia.png", "Fig. 8.20 — Radiographie thoracique (HVG, débord aortique)"),
            "Fig. 8.22": ("fig_8_22_eval_vg_ia.png", "Fig. 8.22 — Évaluation ventriculaire gauche"),
            "Fig. 8.23": ("fig_8_23_irm_aorte.png", "Fig. 8.23 — IRM : aorte thoracique"),
        },
        "default_reflexes": [
            "Item 152 — Endocardite infectieuse.",
            "Item 153 — Surveillance des porteurs de valves et prothèses vasculaires.",
            "Item 230 — Douleur thoracique aiguë.",
        ],
    },
}


def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    if re.match(r"^\d{1,3}$", line):
        return None
    line = line.replace("El ", "• ")
    line = line.replace("011 ", "• ")
    line = line.replace("1 52", "152")
    line = line.replace("1 53", "153")
    line = line.replace("1 €r", "1er")
    line = line.replace("Ve intention", "1re intention")
    line = line.replace("MitraClip®", "MitraClip®")
    line = line.replace("Mitradip®", "MitraClip®")
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
    return line


def get_section_chunk(full_text, start_marker, stop_marker):
    start_idx = full_text.find(start_marker)
    if start_idx == -1:
        raise ValueError(f"Start marker not found: {start_marker}")
    stop_idx = full_text.find(stop_marker, start_idx + len(start_marker))
    if stop_idx == -1:
        raise ValueError(f"Stop marker not found: {stop_marker}")
    return full_text[start_idx:stop_idx]


def extract_footer(chunk, default_reflexes):
    notions_ind = []
    notions_inacc = []
    reflexes = []
    mode = None
    for raw in chunk.splitlines():
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
        if cl.startswith("Pour en savoir plus"):
            break
        if mode == "ind":
            if cl.startswith("•"):
                notions_ind.append(cl)
            elif not cl.startswith("Notions"):
                notions_ind.append("• " + cl)
        elif mode == "inacc":
            if cl.startswith("•"):
                notions_inacc.append(cl)
            else:
                notions_inacc.append("• " + cl)
        elif mode == "reflex":
            if cl.startswith("•"):
                reflexes.append(cl.replace("• Item ", "• Item ").replace("Item 1 52", "Item 152").replace("Item 1 53", "Item 153"))
    if not reflexes:
        reflexes = ["• " + r for r in default_reflexes]
    return notions_ind, notions_inacc, reflexes


def match_section(cl, section_map):
    for sec, hdr in section_map.items():
        if cl == sec or cl.startswith(sec):
            return hdr, sec
    cl_norm = re.sub(r"^VIL\b", "VII", cl)
    cl_norm = re.sub(r"^VL\b", "VI", cl_norm)
    for sec, hdr in section_map.items():
        if cl_norm == sec or cl_norm.startswith(sec):
            return hdr, sec
    return None, None


def extract_body(chunk, section_map, fig_map):
    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False

    for line in chunk.splitlines():
        cl = clean_line(line)
        if cl is None:
            continue
        if skip_until_vignette:
            if cl.startswith("Vignette clinique") or cl.startswith("Vous ") or cl.startswith("M. ") or cl.startswith("Un homme"):
                skip_until_vignette = False
                lines_out.append("## Vignette clinique\n")
                if not cl.startswith("Vignette"):
                    lines_out.append(cl)
                continue
            continue
        if cl.startswith("Notions indispensables"):
            break
        hdr, _ = match_section(cl, section_map)
        if hdr:
            lines_out.append(hdr)
            in_body = True
            in_points = False
            continue
        if cl.startswith("Points") and not in_points:
            lines_out.append("\n\n---\n\n## Points\n")
            in_points = True
            in_body = False
            continue
        if ENCADRE_RE.match(cl):
            lines_out.append(f"\n### {cl}\n")
            continue
        m = SUBSECTION_RE.match(cl)
        if m and in_body and not in_points and len(cl) < 80:
            lines_out.append(f"\n## {m.group(1)}\n")
            continue
        m2 = NUM_SUBSECTION_RE.match(cl)
        if m2 and in_body and len(cl) < 100:
            lines_out.append(f"\n### {m2.group(1)}\n")
            continue
        fig_handled = False
        for fig_key, (fname, caption) in fig_map.items():
            if fig_key.lower() in cl.lower() and cl.lower().startswith("fig."):
                lines_out.append(f"\n![{caption}](./img/{fname})\n")
                cap = re.sub(r"^Fig\. 8\.\d+\.?\s*[0-9ODElQ©©]?\s*", "", cl)
                lines_out.append(f"\n**Fig. {fig_key.split()[-1]}.** {cap.lstrip('0123456789. ')}\n")
                fig_handled = True
                break
        if fig_handled:
            continue
        if cl == "•":
            continue
        if cl.startswith("- ") or cl.startswith("• "):
            lines_out.append(cl)
        elif cl.startswith("> "):
            lines_out.append(cl)
        elif cl.startswith(">"):
            lines_out.append("> " + cl[1:].strip())
        elif in_points and not cl.startswith("#"):
            if not cl.startswith("•"):
                lines_out.append("• " + cl)
            else:
                lines_out.append(cl)
        else:
            lines_out.append(cl)
    return "\n".join(lines_out)


def postprocess(text):
    text = re.sub(r"\s*===== PDF PAGE \d+ =====\s*", " ", text)
    text = re.sub(r"\s*Pour avoir plus d'exclusivités rejoindre nous sur www\.amis-med\.com et sur https://t\.me/Faille_V2\s*", " ", text)
    text = re.sub(r"(?<=\w)-\s+(?=[a-zàâéèêëîïôùûü])", "", text)
    fixes = [
        ("bio- logie", "biologie"), ("tho- racique", "thoracique"), ("écho- cardiographie", "échocardiographie"),
        ("cardio- logue", "cardiologue"), ("sympto- matique", "symptomatique"), ("anti- inflammatoire", "anti-inflammatoire"),
        ("coro- scanner", "coroscanner"), ("trans- thoracique", "transthoracique"), ("trans- œsophagienne", "transœsophagienne"),
        (" pré- opératoire", " préopératoire"), ("bilan préopérafoi", "bilan préopératoire"), ("postprandialejustifie", "postprandiale justifie"),
        ("tri- cuspide", "tricuspide"), ("antéro- gauche", "antérogauche"), ("antéro- droit", "antérodroit"),
        ("sigmoï- des", "sigmoïdes"), ("endocar- dite", "endocardite"), ("hémody- namique", "hémodynamique"),
        ("£ 60", "≤ 60"), ("Z 40", "≥ 40"), ("2 50", "≥ 50"), ("DTS £", "DTS ≥"),
        ("Item 1 52", "Item 152"), ("Item 1 53", "Item 153"), ("1 000", "1 000"),
        ("cm 2", "cm²"), ("m 2", "m²"), ("mm 2", "mm²"), ("mL/m 2", "mL/m²"),
        ("hémodynamiques\n\n# IV", "hémodynamiques\n\n---\n\n# IV"),
    ]
    for old, new in fixes:
        text = text.replace(old, new)
    text = re.sub(r"\n+hémodynamiques\n+(?=# IV)", "", text)
    text = re.sub(r"(# III\. Physiopathologie et conséquences hémodynamiques\n\n\*\*Rang A\*\* · \*\*Rang B\*\*\.)\n\nhémodynamiques", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
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
        if line.startswith(("#", "##", "###", "**", "-", "•", ">", "!", "|", "---", "![")):
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append(line)
        else:
            buf.append(line.strip())
    if buf:
        paragraphs.append(" ".join(buf))
    return "\n\n".join(p for p in paragraphs if p is not None)


def make_header(cfg):
    situations = "\n".join(f"{s.split(' ', 1)[0]} {s.split(' ', 1)[1]}." if " " in s else s for s in SHARED_SITUATIONS.split("\n"))
    return f"""# Item 233 — {cfg['title']}

> **Collège CNEC / SFC** · 3e édition (2025) · p. {cfg['pages']} · R2C  
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

{situations}

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
{SHARED_HIERARCH}

---

## Parcours Rang A

{cfg['parcours']}

---

## Sommaire

{cfg['sommaire']}

---

"""


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

Questions isolées et corrigés : [Entrainement/QI/233_Valvulopathies.md](../../Entrainement/QI/233_Valvulopathies.md)
"""


def build_course_files(full_text):
    results = []
    for key, cfg in VALVE_CONFIGS.items():
        chunk = get_section_chunk(full_text, cfg["start"], cfg["stop"])
        body = extract_body(chunk, cfg["section_map"], cfg["fig_map"])
        body = postprocess(body)
        body = merge_paragraphs(body)
        notions_ind, notions_inacc, reflexes = extract_footer(chunk, cfg["default_reflexes"])
        out_path = OUT_DIR / f"{cfg['slug']}.md"
        content = make_header(cfg) + body + make_footer(notions_ind, notions_inacc, reflexes)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        results.append((out_path, out_path.stat().st_size))
        print(f"Written {out_path} ({out_path.stat().st_size} bytes)")
    return results


QI_CONTENT = '''# Entraînement — Item 233 Valvulopathies

> Collège CNEC 3e éd. · Chapitre 8 · corrigés p. 580–581  
> Cours : [233 RA](../../Cours/II_Valves/233_RA_Retrecissement_aortique.md) · [233 IM](../../Cours/II_Valves/233_IM_Insuffisance_mitrale.md) · [233 IA](../../Cours/II_Valves/233_IA_Insuffisance_aortique.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRM 1

Les sténoses valvulaires aortiques :

- A. Nécessitent un suivi uniquement s'il y a des symptômes
- B. Peuvent être traités médicalement
- C. Font partie du « groupe à haut risque » pour la prévention de l'endocardite
- D. Nécessitent une surveillance par échocardiographie transthoracique annuelle
- E. Nécessitent un suivi dentaire au moins annuel

**Réponse : D, E**

Suivi et éducation annuels (**A** : SCZ). Pas de traitement médical curatif : en cas de symptôme, il faut changer la valve (**B** faux). L'échocardiographie est l'examen clé de suivi (**D**). Prévention de l'endocardite : suivi dentaire (**E**). Le groupe à haut risque d'EI ne correspond pas spécifiquement au RA isolé (**C** faux).

---

## QRM 2

Quels sont, parmi les symptômes suivants, ceux qui peuvent être attribués au rétrécissement aortique ?

- A. La syncope d'effort
- B. L'hémolyse
- C. La dyspnée d'effort
- D. La douleur angineuse
- E. L'insuffisance cardiaque droite

**Réponse : A, C, D**

Triade classique du RA serré : dyspnée d'effort, angor d'effort, syncope d'effort. L'hémolyse n'est pas un symptôme typique du RA (**B** faux). L'IC droite isolée n'est pas le mode de révélation habituel (**E** faux).

---

## QRM 3

Concernant le rétrécissement aortique serré, quelles affirmations sont exactes ?

- A. La consultation cardiologique sans échocardiographie tous les 5 ans est suffisante
- B. L'échocardiographie est l'examen clé pour apprécier la sévérité de la sténose
- C. Un gradient moyen à 47 mmHg justifie à lui seul une chirurgie
- D. Un gradient moyen à 48 mmHg avec dyspnée d'effort justifie un bilan préopératoire
- E. Une surface valvulaire à 0,8 cm² avec syncope postprandiale justifie un bilan préopératoire

**Réponse : B, D, E**

Suivi clinique **et** échocardiographique (**A** : SCZ). L'échocardiographie quantifie la sévérité (**B**). Le gradient seul ne suffit pas sans symptôme (**C** : SCZ). Sténose serrée + symptôme (repas = effort, syncope = gravité) → bilan préopératoire (**D**, **E**).

---

## QRM 4

Les insuffisances mitrales :

- A. Sont toujours liées à une anomalie des feuillets valvulaires
- B. Peuvent être traitées médicalement quand elles sont primitives organiques
- C. Peuvent compliquer un infarctus du myocarde
- D. Nécessitent une surveillance par échocardiographie transthoracique
- E. Nécessitent un suivi dentaire au moins annuel

**Réponse : C, D, E**

Les cordages, l'anneau et les piliers participent à l'appareil mitral : la fuite secondaire peut être sévère sans feuillet pathologique (**A** : SCZ). Pas de traitement médical curatif des IM organiques sévères (**B** faux). IM secondaire post-IDM (**C**). Échographie clé de suivi (**D**). Suivi dentaire (**E**).

---

## QRM 5

Quels sont, parmi les symptômes suivants, ceux qui peuvent être attribués à une insuffisance mitrale ?

- A. Les palpitations
- B. L'hémolyse
- C. La dyspnée d'effort
- D. La douleur angineuse
- E. L'insuffisance cardiaque gauche

**Réponse : A, C, E**

Palpitations (FA, dilatation AG), dyspnée d'effort et IC gauche sont fréquentes. Hémolyse non typique (**B** faux). Angor possible mais moins caractéristique que dyspnée/IC (**D** faux).

---

## QRM 6

Quelles sont les affirmations exactes concernant l'insuffisance mitrale ?

- A. La consultation cardiologique sans échocardiographie tous les 5 ans est suffisante
- B. L'échocardiographie est l'examen clé pour apprécier la sévérité de la fuite
- C. La fuite peut être sévère et symptomatique sans que les feuillets soient pathologiques
- D. Le prolapsus mitral est caractéristique d'une fuite secondaire (fonctionnelle)
- E. La fuite mitrale s'accompagne d'une dilatation des cavités gauches quand elle est sévère

**Réponse : B, C, E**

Suivi clinique et échocardiographique (**A** : SCZ). Échographie = examen clé (**B**). Fuite secondaire sévère possible sans feuillet pathologique (**C**). Prolapsus = anomalie primitive, non fonctionnelle (**D** : SCZ). Dilatation VG et AG si sévère (**E**).

---

## QRM 7

Mme D, 77 ans, présente une dyspnée d'effort d'aggravation récente. Elle est porteuse d'une insuffisance mitrale dystrophique considérée comme modérée et qui fait l'objet d'une surveillance annuelle chez son cardiologue. L'auscultation retrouve un souffle systolique en jet de vapeur 3/6 à l'apex, qui vous semble beaucoup plus franc qu'antérieurement. Quelles sont les propositions exactes ?

- A. Le dosage du BNP doit être demandé en 1re intention
- B. Une radiographie de thorax est indispensable
- C. L'échocardiographie est à faire en 1re intention
- D. Il faut éliminer une endocardite
- E. L'aggravation est peut-être due à une rupture de cordage

**Réponse : C, D, E**

Le souffle aggravé oriente déjà vers le cœur ; BNP et radio ne sont pas décisifs en 1re intention (**A**, **B** faux). Échocardiographie en 1re intention pour réévaluer la fuite (**C**). Endocardite à évoquer devant aggravation brutale (**D**). Rupture de cordage = diagnostic le plus vraisemblable ici (**E**).

---

## QRM 8

Concernant la prise en charge de l'insuffisance mitrale par prolapsus, quelles sont les affirmations exactes ?

- A. Le remplacement valvulaire doit être préféré à la plastie mitrale
- B. La chirurgie est indiquée en cas d'insuffisance mitrale modérée et symptomatique
- C. La chirurgie est indiquée en cas d'insuffisance mitrale sévère asymptomatique avec hypertension pulmonaire
- D. La chirurgie est indiquée en cas d'insuffisance mitrale sévère asymptomatique et de fibrillation atriale
- E. Une prise en charge percutanée est possible pour les patients contre-indiqués à la chirurgie

**Réponse : C, D, E**

Plastie privilégiée au remplacement dans le prolapsus (**A** faux). Chirurgie pour IM **sévère** (grade III–IV) symptomatique, pas modérée seule (**B** faux). IM sévère asymptomatique + HTP ou FA → indication chirurgicale (**C**, **D**). Clip percutané si haut risque/inopérable (**E**).

---

## QRM 9

Concernant la physiopathologie de l'insuffisance aortique (IA) chronique, quelles sont les propositions exactes ?

- A. L'IA entraîne une surcharge volumétrique sans surcharge barométrique
- B. La baisse de la pression artérielle diastolique peut altérer la perfusion coronaire
- C. Le remodelage ventriculaire gauche secondaire à l'IA est de type hypertrophie concentrique
- D. La fraction d'éjection du ventricule gauche s'altère de façon précoce dans l'IA
- E. La pression de remplissage du ventricule gauche reste longtemps normale

**Réponse : B, E**

Surcharge volumétrique **et** barométrique (baisse PAD) (**A** faux). Baisse PAD → baisse perfusion coronarienne, vol coronarien (**B**). Remodelage excentrique (hypertrophie + dilatation), pas concentrique (**C** faux). FE conservée longtemps (**D** faux). Pression de remplissage normale au long cours (**E**).

---

## QRM 10

Concernant l'insuffisance aortique (IA) aiguë, quelles propositions sont exactes ?

- A. Elle est souvent responsable de symptômes importants
- B. Elle peut être secondaire à une endocardite infectieuse
- C. Elle peut être secondaire à une ischémie myocardique
- D. Une dissection aortique peut entraîner une IA aiguë
- E. Elle nécessite souvent une prise en charge chirurgicale précoce

**Réponse : A, B, D, E**

IA aiguë mal tolérée, souvent très symptomatique (**A**). ÉI fébrile (**B**). Pas de lien physiopathologique direct avec ischémie myocardique (**C** faux). Dissection aortique ± IA aiguë non fébrile (**D**). Chirurgie précoce fréquente (**E**).

---

## QRU 11

Concernant les étiologies de l'insuffisance aortique (IA), quelle proposition est exacte ?

- A. La maladie rhumatismale valvulaire est la principale étiologie dans les pays occidentaux
- B. Il n'y a pas d'étiologie génétique à l'IA
- C. La dilatation de l'aorte thoracique initiale entraîne une IA par prolapsus de cusp
- D. La bicuspidie est une anomalie exceptionnelle de la valve aortique
- E. Les dystrophies valvulaires aortiques et la dilatation de l'aorte sont les principales étiologies d'IA dans les pays occidentaux

**Réponse : E**

RAA très rare en Occident (**A** faux). Marfan = génétique (**B** faux). Dilatation annuloectasiante par restriction de mobilité des cusps, pas prolapsus (**C** faux). Bicuspidie = 1–2 % (**D** faux). Dystrophie valvulaire et dilatation aortique = étiologies dominantes (**E**).

---

## QRU 12

Concernant les symptômes de l'IA, quelle proposition est exacte ?

- A. La syncope est un symptôme fréquent d'IA
- B. L'IA chronique est souvent asymptomatique
- C. L'IA n'entraîne jamais d'angor
- D. La dyspnée de repos est un symptôme précoce de l'IA chronique
- E. Les palpitations sont un symptôme précoce de l'IA chronique

**Réponse : B**

Syncope = plutôt sténose aortique (**A** faux). IA chronique longtemps silencieuse (**B**). Angor possible (perfusion coronarienne, vol coronarien) (**C** faux). Dyspnée de repos et palpitations plutôt tardives (**D**, **E** faux).

---

## QRM 13

Concernant les examens complémentaires dans l'insuffisance aortique (IA) chronique, quelles propositions sont exactes ?

- A. L'ECG permet de faire le diagnostic d'IA
- B. La radiographie thoracique permet de faire le diagnostic d'une IA
- C. L'échocardiographie permet de faire le diagnostic d'une IA
- D. L'échocardiographie permet de quantifier une IA
- E. L'échocardiographie permet d'évaluer le retentissement cardiaque d'une IA

**Réponse : C, D, E**

Pas de signe ECG ou radiographique spécifique d'IA (**A**, **B** : SCZ). Échocardiographie = examen essentiel : diagnostic, quantification, retentissement VG (**C**, **D**, **E**).
'''


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
    for fig_num, fname, page_idx in FIGURES:
        if page_idx >= len(doc):
            print(f"Skip {fig_num}: page index {page_idx} out of range")
            continue
        page = doc[page_idx]
        label = f"Fig. {fig_num}"
        hits = page.search_for(label)
        if hits:
            r = hits[0]
            y1 = min(page.rect.height, r.y1 + (420 if fig_num in ("8.17", "8.18", "8.19") else 320))
            clip = fitz.Rect(25, max(0, r.y0 - 20), page.rect.width - 25, y1)
        else:
            clip = page.rect
        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
        out = IMG_DIR / fname
        pix.save(str(out))
        print(f"Figure {fig_num} -> {out} ({out.stat().st_size} bytes)")
    doc.close()


def update_readme():
    text = README.read_text(encoding="utf-8")
    rows = """| Fait | 233 RA Rétrécissement aortique | [II_Valves/233_RA_Retrecissement_aortique.md](./II_Valves/233_RA_Retrecissement_aortique.md) |
| Fait | 233 IM Insuffisance mitrale | [II_Valves/233_IM_Insuffisance_mitrale.md](./II_Valves/233_IM_Insuffisance_mitrale.md) |
| Fait | 233 IA Insuffisance aortique | [II_Valves/233_IA_Insuffisance_aortique.md](./II_Valves/233_IA_Insuffisance_aortique.md) |
"""
    if "233 RA Rétrécissement aortique" not in text:
        text = text.replace("| À faire | … | lots suivants |", rows + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 233 rows")


def verify_outputs(results):
    ok = True
    for path, size in results:
        content = path.read_text(encoding="utf-8")
        headers = len(re.findall(r"^#+ ", content, re.M))
        if size < 15_000:
            print(f"WARN: {path.name} only {size} bytes (< 15 KB)")
            ok = False
        if headers < 8:
            print(f"WARN: {path.name} only {headers} section headers")
            ok = False
    qi_size = QI_OUT.stat().st_size if QI_OUT.exists() else 0
    print(f"QI size: {qi_size} bytes, figures: {len(list(IMG_DIR.glob('*.png')))} PNGs")
    return ok


def main():
    full_text = SRC.read_text(encoding="utf-8")
    results = build_course_files(full_text)
    build_qi()
    extract_figures()
    update_readme()
    verify_outputs(results)


if __name__ == "__main__":
    main()
