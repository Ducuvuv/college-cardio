# -*- coding: utf-8 -*-
"""Generate item 342 malaises/PDCB markdown + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item342.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Cours" / "III_Rythmologie" / "342_Malaises_PDCB.md"
IMG_DIR = OUT.parent / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "342_Malaises_PDCB.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Rythmologie\s*$",
    r"^CHAPITRE\s*$",
    r"^12\s*$",
    r"^Item 342\s*$",
    r"^Item 342 - Malaises.*",
    r"^Malaises, perte\s*$",
    r"^de connaissance, crise\s*$",
    r"^comitiale chez l'adulte\s*$",
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
    r"^Médecine cardiovasculaire\s*$",
    r"^wtiVHWWHîi.*",
    r"^[\d\s\.ÏHWMflBï\.\\\/\*]+$",
    r"^Item 17\..*",
    r"^Item 18\..*",
    r"^Attention\s*$",
    r"^Encadré 12\.\d+\s*$",
    r"^Test d'inclinaison\s*$",
    r"^Étude électrophysiologique endocavitaire \(EEP\)\s*$",
]

FLOWCHART_GARBAGE = {
    "« Malaise »", "Autre cadre nosologique", "Autres cadres nosologiques",
    "Perte de connaissance brève (PDCB) ?", "Oui", "Non", "Non*", "PDCB",
    "Traumatisme crânien initial ?", "Douleur thoracique ?", "» Oui",
    "PDCB non traumatique, non ischémique", "Épilepsie", "PDCB psychogène",
    "Arguments pour syncope ?", "Interrogatoire, examen clinique, ECG", "Syncope",
    "- Obstacle mécanique", "- Cause rythmique", "- Hypotension orthostatique",
    "- Syncope réflexe", "Cause évidente ?", "Recherche de cardiopathie sous-jacente",
    "Syncope grave possible,", "discuter :", "- défibrillateur d'emblée",
    "- étude électrophysiologique", "- moniteur ECG implantable",
    "Tous examens normaux ?", "Probable syncope réflexe,",
    "- test d'inclinaison", "- moniteur ECG implantable",
    "AIT : accident ischémique transitoire ; AVC : accident vasculaire cérébral ; "
    "ECG : électrocardiogramme ; PDCB : perte de connaissance brève.",
    "A", "B", "C", "D", "E", "F",
}

SECTION_MAP = {
    "I. Définitions et sémantique, notion de perte": (
        "\n\n# I. Définitions et sémantique, notion de PDCB\n\n**Rang A.**"
    ),
    "I. Définitions et sémantique, notion de perte de connaissance brève": (
        "\n\n# I. Définitions et sémantique, notion de PDCB\n\n**Rang A.**"
    ),
    "II. Physiopathologie des PDCB": (
        "\n\n---\n\n# II. Physiopathologie des PDCB\n\n**Rang B.**"
    ),
    "III. Étiologies et classification des syncopes": (
        "\n\n---\n\n# III. Étiologies et classification des syncopes\n\n**Rang A.**"
    ),
    "IV. Diagnostic différentiel des syncopes": (
        "\n\n---\n\n# IV. Diagnostic différentiel des syncopes\n\n**Rang A.**"
    ),
    "V. Prise en charge clinique et paraclinique": (
        "\n\n---\n\n# V. Prise en charge clinique et paraclinique\n\n**Rang A** · **Rang B**."
    ),
    "VI. Critères de gravité": (
        "\n\n---\n\n# VI. Critères de gravité\n\n**Rang A.**"
    ),
    "VII. Formes cliniques typiques": (
        "\n\n---\n\n# VII. Formes cliniques typiques\n\n**Rang A** · **Rang B**."
    ),
    "VIL Formes cliniques typiques": (
        "\n\n---\n\n# VII. Formes cliniques typiques\n\n**Rang A** · **Rang B**."
    ),
}

FIG_MAP = {
    "Fig. 12.1": (
        "fig_12_1_arbre_decisionnel.png",
        "Fig. 12.1 — Arbre décisionnel en cas de « malaise »",
    ),
}

FIGURES = [
    ("12.1", "fig_12_1_arbre_decisionnel.png", 316),
]

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")

TABLE_12_1 = """
**Tableau 12.1.** Diagnostic différentiel entre syncope et crise comitiale : arguments cliniques.

| | Syncope | Épilepsie |
|---|---|---|
| **Facteur déclenchant** | Très fréquent : verticalisation (hypotension orthostatique), effort, etc. | Rare : stimulation lumineuse intermittente, privation de sommeil, alcool |
| **Prodromes** | Sensation cotonneuse, tête vide, nausées, vomissements, sensation de froid, sueurs ; palpitations (arythmies) | Aura : déjà-vu, étrangeté, sensation épigastrique, hallucinations visuelles, olfactives, auditives |
| **Mouvements anormaux** | Myoclonies inconstantes, peu abondantes (< 10), tardives après la PDCB, asymétriques et asynchrones | Mouvements tonicocloniques nombreux (> 20), synchrones, symétriques ou hémicorps, débutant avec la PDCB, automatismes prolongés de mâchonnement |
| **Morsure de langue** | Bout de la langue | Bord latéral de la langue |
| **Tégument** | Normal ou pâle | Cyanosé |
| **Récupération de la conscience** | En 10 à 30 secondes | En plusieurs minutes |
| **État confusionnel** | Très bref (< 10 secondes), puis vigilance normale | Amnésie de fixation pendant plusieurs minutes |
| **Douleurs musculaires** | Absentes | Fréquentes |

La perte des urines ainsi que la fatigue avec envie de dormir après la PDCB ne sont pas dans ce tableau car considérés désormais comme peu discriminants. PDCB : perte de connaissance brève.
"""

ENCADRE_12_1 = """
**Encadré 12.1 — Étude électrophysiologique endocavitaire (EEP)**

- **Rang A.** Examen réalisé avec asepsie après recueil du consentement.
- Dans une salle de cathétérisme, par voie veineuse fémorale.
- Sous anesthésie locale et sédation légère.
- Montée de deux ou trois sondes pour recueil de l'activité électrique du faisceau de His et mesure de l'intervalle HV (conduction infrahissienne).
- Stimulation atriale à fréquence croissante pour évaluer les capacités de la conduction atrioventriculaire.
- Stimulation ventriculaire programmée pour tentative de déclenchement de TV.
- Tests pharmacologiques éventuels.
- Surveillance du point de ponction, mobilisation du patient 4 heures plus tard.

> **Attention.** Les TV sont la première cause de mort subite des patients cardiaques et la syncope peut en être l'élément annonciateur. La sanction thérapeutique en cas de déclenchement de TV est la pose d'un défibrillateur automatique intracorporel.
"""

POINTS_BLOCK = """
• L'interrogatoire, l'examen clinique et l'ECG résolvent plus de 50 % des cas de syncope et de lipothymie.

• Les prises en charge des syncopes et des lipothymies sont superposables.

• L'âge est un bon élément d'orientation mais trompeur pour affirmer qu'une syncope est nécessairement vasovagale chez un jeune et ne peut pas l'être chez un sujet âgé.

• Les PDCB regroupent syncopes, crises comitiales et PDCB psychogènes.

• L'interrogatoire retrouve les éléments pour une crise comitiale et permet de changer de champ diagnostique vers l'épilepsie : aura, survenue pendant le sommeil, durée longue de la perte de connaissance, mouvements tonicocloniques prolongés ou automatismes, morsure du bord de langue, cyanose du visage, confusion prolongée, céphalées, douleurs musculaires et somnolence après la crise.

• Les syncopes sont classées en :
  - obstacle mécanique : prépondérance du rétrécissement aortique et de l'embolie pulmonaire, des cardiomyopathies obstructives, des tamponnades et des thromboses de valve mécanique, etc. ;
  - causes rythmiques : tachycardies ventriculaires, bradycardies par bloc atrioventriculaire ou dysfonction sinusale, torsades de pointes, etc. ;
  - hypotension artérielle orthostatique souvent iatrogène, souvent du sujet âgé, parfois avec dysautonomie ;
  - syncopes réflexes : vasovagales ou situationnelles, syndrome du sinus carotidien.

• Il faut rechercher une hypotension artérielle orthostatique, par 5 à 10 minutes de repos puis mesure de la pression artérielle à 1, 2 et 3 minutes d'orthostatisme ; la positivité correspond à une chute > 20 mmHg de la PAS ou > 10 mmHg de la PAD, ou à une PAS < 90 mmHg.

• L'objectif principal est de déterminer la présence ou non d'une cardiopathie sous-jacente et, dans l'affirmative, de connaître le risque de mort subite (par trouble du rythme ventriculaire) qui peut amener rapidement à proposer un défibrillateur implantable.

• Les principales anomalies ECG permettant d'expliquer immédiatement la cause électrique d'une syncope sont les suivantes :
  - tachycardie ventriculaire ;
  - bradycardie sinusale < 40 bpm ;
  - pauses > 3 secondes ;
  - BAV complet ou du 2e degré de type Mobitz 2 ;
  - bloc de branche alternant ;
  - tachycardie supraventriculaire rapide (> 150 bpm).

• Les examens complémentaires sont ainsi hiérarchisés : holter et échocardiographie avant l'EEP notamment, MEI en cas d'EEP négative. Il faut différencier la recherche d'une cardiopathie sous-jacente et l'élucidation du mécanisme de la syncope.

• Attention au diagnostic de syncope vasovagale chez un cardiaque, ce diagnostic reste possible mais en diagnostic d'élimination après une prise en charge complète et réalisation des examens spécialisés (EEP et MEI principalement).
"""

ENCADRE_12_2 = """
**Encadré 12.2 — Test d'inclinaison**

- **Rang A.** Examen réalisé dans un environnement calme, patient à jeun.
- Surveillance continue de la pression artérielle et de l'ECG.
- Période de décubitus initial d'au moins 5 minutes.
- Patient incliné sur table basculante, angle de 60 à 70° tête en haut.
- Période d'inclinaison entre 20 et 45 minutes au plus.
- Sensibilisation par l'isoprénaline ou la trinitrine sublinguale.
- Résultat positif en cas de survenue d'une syncope vasovagale associant hypotension et/ou bradycardie.
"""

HEADER = '''# Item 342 — Malaises, perte de connaissance, crise comitiale chez l'adulte

> **Collège CNEC / SFC** · 3e édition (2025) · p. 279–296 · R2C  
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

50 Malaise/perte de connaissance.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Malaise, syncope, lipothymie, prodromes, crise d'épilepsie, état de mal épileptique | |
| **B** | Physiopathologie | Mécanisme principal d'un malaise | Hypoperfusion cérébrale ou dysfonctionnement de l'activité cérébrale |
| **A** | Diagnostic positif | Interrogatoire et examen clinique | Diagnostic rétrospectif de crise généralisée ; interrogatoire de l'entourage |
| **A** | Diagnostic positif | Éléments du diagnostic des syncopes et lipothymies | Circonstances déclenchantes, caractéristiques cliniques |
| **A** | Diagnostic positif | Hypotension orthostatique, hypoglycémie | |
| **A** | Diagnostic positif | Événement épileptique et non épileptique (pseudo-crise) | |
| **A** | Étiologies | Causes cardiovasculaires et non cardiovasculaires des syncopes/lipothymies | Réflexe, par hypotension, cardiaque |
| **A** | Étiologies | Causes neurologiques des malaises, crises épileptiques | Hypoglycémie, toxiques, méningite, arrêt de traitement, lésion intracérébrale focale* |
| **A** | Étiologies | Causes non cardiaques et non neurologiques | Malaise somatomorphe, attaque de panique |
| **A** | Identifier une urgence | Gravité des malaises et surveillance | |
| **A** | Examens complémentaires | Indications et anomalies décisives de l'ECG | Anomalies ECG ayant valeur diagnostique immédiate |
| **A** | Examens complémentaires | Indications d'un EEG* | En cas de malaise ou PDCB présumés d'origine épileptique |
| **B** | Examens complémentaires | Examens de 2e intention | MEI, test d'inclinaison, EEP endocavitaire |
| **A** | Identifier une urgence | Éléments justifiant avis cardiologique, neurologique ou réanimatoire | |
| **A** | Prise en charge | Gestes d'urgence devant crise convulsive généralisée* | |
| **A** | Prise en charge | Traitement symptomatique d'un malaise | |
| **A** | Prise en charge | Suivi syncope/lipothymie de cause rythmique | Prévention du risque de mort subite |
| **B** | Prise en charge | Suivi syncope/lipothymie réflexe | Bénignité, éducation du patient |
| **A** | Prise en charge | Suivi hypotension artérielle orthostatique | Sécurité des médicaments, sujet âgé |
| **A** | Prise en charge | Prescription d'un traitement anticonvulsivant | Benzodiazépines de courte durée d'action* |
| **A** | Prise en charge | Principes de la prise en charge de la crise comitiale | Traitements de longue durée d'action* |

---

## Parcours Rang A

- [I. Définitions et sémantique, notion de PDCB](#i-définitions-et-sémantique-notion-de-pdcb)
- [III. Étiologies et classification des syncopes](#iii-étiologies-et-classification-des-syncopes)
- [IV. Diagnostic différentiel des syncopes](#iv-diagnostic-différentiel-des-syncopes)
- [V. Prise en charge clinique et paraclinique](#v-prise-en-charge-clinique-et-paraclinique)
- [VI. Critères de gravité](#vi-critères-de-gravité)
- [VII. Formes cliniques typiques](#vii-formes-cliniques-typiques)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Définitions et sémantique, notion de PDCB](#i-définitions-et-sémantique-notion-de-pdcb)
- [II. Physiopathologie des PDCB](#ii-physiopathologie-des-pdcb)
- [III. Étiologies et classification des syncopes](#iii-étiologies-et-classification-des-syncopes)
- [IV. Diagnostic différentiel des syncopes](#iv-diagnostic-différentiel-des-syncopes)
- [V. Prise en charge clinique et paraclinique](#v-prise-en-charge-clinique-et-paraclinique)
- [VI. Critères de gravité](#vi-critères-de-gravité)
- [VII. Formes cliniques typiques](#vii-formes-cliniques-typiques)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/342_Malaises_PDCB.md)

---

'''

QI_CONTENT = '''# Entraînement — Item 342 Malaises, perte de connaissance, crise comitiale

> Collège CNEC 3e éd. · Chapitre 12 · corrigés p. 582  
> Cours : [342 Malaises PDCB](../../Cours/III_Rythmologie/342_Malaises_PDCB.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRU 1

L'absence de prodrome au cours d'une perte de connaissance brève :

- A. Est nécessaire pour le diagnostic de syncope
- B. Évoque une cause neurologique à la perte de connaissance brève
- C. Évoque une syncope réflexe
- D. Évoque une syncope par hypotension orthostatique
- E. Évoque une cause cardiaque

**Réponse : E**

L'absence de prodrome (syncope à l'emporte-pièce) évoque une cause **cardiaque**, souvent rythmique (**E**). Ce n'est pas nécessaire au diagnostic de syncope (**A** faux). Les syncopes réflexes, vasovagales et orthostatiques s'accompagnent le plus souvent de prodromes (**C**, **D** faux). L'épilepsie peut aussi avoir une aura mais l'absence de prodrome oriente surtout vers le cardiaque, pas le neurologique (**B** faux).

---

## QRM 2

L'exploration électrophysiologique au cours du bilan d'une syncope :

- A. Est indiquée en 1re intention
- B. A une sensibilité élevée pour le diagnostic de syncope cardiaque
- C. Peut conduire à l'implantation d'un stimulateur cardiaque si un trouble conductif sévère est mis en évidence
- D. Est indiquée en cas de syncope sans prodrome avec un bloc de branche droit et un hémibloc antérieur gauche à l'ECG
- E. Peut être suivie par l'implantation d'un Holter sous-cutané si l'EEP est normale mais la probabilité clinique de syncope cardiaque élevée

**Réponse : C, D, E**

L'EEP n'est pas de 1re intention si l'interrogatoire, l'examen et l'ECG orientent vers une syncope réflexe ou orthostatique (**A** faux). Sa valeur prédictive négative est faible (**B** faux). En cas de trouble conductif intermédiaire (BBD + hémibloc antérieur gauche), l'EEP peut documenter un bloc infrahissien et conduire au pacemaker (**C**, **D**). Si l'EEP est normale mais la probabilité clinique reste élevée, le MEI (Holter sous-cutané) peut rattraper les faux négatifs (**E**).

---

## QRM 3

L'implantation d'un Holter sous-cutané au cours du bilan d'une syncope :

- A. Peut être indiquée sans nécessairement réaliser d'exploration électrophysiologique au préalable si la probabilité clinique de syncope cardiaque est élevée et s'il n'y a pas de troubles conductifs évidents à l'ECG
- B. Permet de faire le diagnostic d'une future récidive de syncope cardiaque par trouble conductif paroxystique ou arythmie ventriculaire
- C. Permet d'enregistrer le rythme cardiaque en permanence sur une durée qui peut excéder plusieurs années
- D. Est indiquée pour exclure une syncope cardiaque quand plusieurs éléments de l'anamnèse évoquent une syncope par hypotension orthostatique
- E. Est indiquée pour préciser le type de syncope réflexe lorsqu'une syncope réflexe est très probable

**Réponse : A, B, C**

Le MEI est réservé aux patients à probabilité clinique élevée de syncope cardiaque, notamment sans trouble conductif évident à l'ECG (**A**). Il enregistre le rythme sur plusieurs années et peut documenter une récidive (**B**, **C**). Il n'est pas indiqué pour exclure une syncope cardiaque si l'anamnèse évoque une hypotension orthostatique (**D** faux) ni pour typer une syncope réflexe probable (**E** faux).

---

## QRM 4

À propos des syncopes par hypotension orthostatique :

- A. C'est la cause la plus fréquente de syncopes
- B. Elles ne s'accompagnent habituellement pas de prodromes
- C. Certains médicaments (antihypertenseurs, diurétiques, vasodilatateurs) peuvent jouer un rôle favorisant
- D. L'hypotension orthostatique se recherche en mesurant la pression artérielle et le pouls, d'abord allongé et au repos depuis plus de 5 minutes, puis lorsque la personne se met debout, puis à 1, 2, et 3 minutes
- E. L'adaptation des traitements est parfois suffisante pour prévenir les récidives

**Réponse : A, C, D, E**

L'hypotension orthostatique est la **première cause** de syncope (**A**). Les prodromes sont **souvent présents** (cotonneuse, faiblesse) — **B** est faux. Médicaments hypotenseurs, mesure PA orthostatisme (5 min repos puis 1–3 min debout) et adaptation thérapeutique font partie de la prise en charge (**C**, **D**, **E**).

---

## QRM 5

À propos de l'anamnèse d'une perte de connaissance brève :

- A. Une syncope peut être accompagnée de convulsions
- B. Une perte d'urines et des mouvements anormaux nocturnes peuvent être en rapport avec une arythmie cardiaque grave
- C. Une perte d'urine oriente fortement vers une crise d'épilepsie généralisée
- D. L'absence de prodrome (syncope à l'emporte-pièce) oriente vers une cause cardiaque
- E. La présence d'un souffle systolique au foyer aortique doit faire rechercher une sténose valvulaire aortique

**Réponse : A, B, D, E**

Les syncopes convulsives (myoclonies tardives) existent (**A**). Une crise nocturne avec mouvements anormaux peut révéler une arythmie grave (**B**, rang C). La perte d'urine n'oriente **pas fortement** vers l'épilepsie (**C** faux). Syncope à l'emporte-pièce → cardiaque (**D**). Souffle systolique aortique → rechercher un rétrécissement aortique cause de syncope (**E**).
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
    if re.match(r"^(279|280|281|282|283|284|285|286|287|288|289|290|291|292|293|294|295|296)$", line):
        return None
    if re.match(r"^[A-G]$", line) and len(line) == 1:
        return None
    if line.startswith("El "):
        line = "• " + line[3:]
    line = line.replace("011 ", "• ")
    line = line.replace("3 42", "342")
    line = line.replace("1 2.", "12.")
    line = line.replace("1 2 .", "12.")
    line = line.replace("fig. 1 2", "fig. 12")
    line = line.replace("Fig. 1 2", "Fig. 12")
    line = line.replace("tableau 1 2", "tableau 12")
    line = line.replace("Tableau 1 2", "Tableau 12")
    line = line.replace("encadré 1 2", "encadré 12")
    line = line.replace("Encadré 1 2", "Encadré 12")
    line = line.replace("1 re", "1re")
    line = line.replace("1 €r", "1re")
    line = line.replace("Ve intention", "1re intention")
    line = line.replace("Item 3 42", "Item 342")
    line = line.replace("VIL ", "VII. ")
    line = line.replace("> 1 5", "> 15")
    line = line.replace("> 1 50", "> 150")
    line = line.replace("J 289", "")
    line = line.replace("13\nPrise", "• **Rang A.** Prise")
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
    line = re.sub(r"^(Fig\. 12\.\d+)\. 0 ", r"\1. ", line)
    line = re.sub(r"^(Tableau 12\.\d+)\. 0 ", r"\1. ", line)
    return line


def match_section(cl):
    if cl.startswith("de connaissance brève") and not cl.startswith("I."):
        return None
    for sec, hdr in SECTION_MAP.items():
        if cl == sec or cl.startswith(sec):
            return hdr
    if cl.startswith("I. Définitions"):
        return SECTION_MAP["I. Définitions et sémantique, notion de perte de connaissance brève"]
    if cl.startswith("VII.") or cl.startswith("VIL "):
        return SECTION_MAP["VII. Formes cliniques typiques"]
    return None


def extract_footer(text):
    notions_ind, notions_inacc, reflexes = [], [], []
    mode = None
    for raw in text.splitlines():
        if "► Entraînement" in raw or raw.strip().startswith("O QRU"):
            break
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
        if mode == "ind":
            notions_ind.append(cl if cl.startswith("•") else "• " + cl)
        elif mode == "inacc":
            notions_inacc.append(cl if cl.startswith("•") else "• " + cl)
        elif mode == "reflex":
            txt = cl.replace("Item 3 42", "Item 342")
            reflexes.append(txt if txt.startswith("•") else "• " + txt)
    return notions_ind, notions_inacc, reflexes


def extract_body():
    text = SRC.read_text(encoding="utf-8")
    stop_idx = text.find("===== PDF PAGE 325 =====")
    chunk = text[:stop_idx] if stop_idx != -1 else text

    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False
    skip_flowchart = False
    table_mode = None
    table_12_1_done = False
    encadre_mode = None
    encadre_12_1_done = False
    encadre_12_2_done = False
    fig_caption_lines = 0
    points_manual_done = False

    for line in chunk.splitlines():
        cl = clean_line(line)
        if cl is None:
            continue
        if skip_until_vignette:
            if cl.startswith("Vignette clinique") or cl.startswith("Une femme de 88 ans"):
                skip_until_vignette = False
                lines_out.append("## Vignette clinique\n")
                if not cl.startswith("Vignette"):
                    lines_out.append(cl)
                continue
            continue
        if cl.startswith("Notions indispensables"):
            break
        if cl.startswith("Points") and not in_points:
            lines_out.append("\n\n---\n\n## Points\n")
            if not points_manual_done:
                lines_out.append(POINTS_BLOCK)
                points_manual_done = True
            in_points = True
            in_body = False
            skip_flowchart = False
            table_mode = None
            encadre_mode = None
            continue
        if in_points:
            continue
        if cl == "de connaissance brève" or cl.startswith("de connaissance brève"):
            continue
        hdr = match_section(cl)
        if hdr:
            lines_out.append(hdr)
            in_body = True
            skip_flowchart = False
            table_mode = None
            encadre_mode = None
            fig_caption_lines = 0
            continue
        if cl.startswith("Tableau 12.1"):
            if not table_12_1_done:
                lines_out.append(TABLE_12_1)
                table_12_1_done = True
            table_mode = "skip12.1"
            continue
        if table_mode == "skip12.1":
            if cl.startswith("V. Prise en charge") or cl.startswith("La perte des urines"):
                table_mode = None
                if cl.startswith("V."):
                    lines_out.append(match_section(cl))
                else:
                    pass
            continue
        if cl.startswith("Encadré 12.1"):
            if not encadre_12_1_done:
                lines_out.append(ENCADRE_12_1)
                encadre_12_1_done = True
            encadre_mode = "skip12.1"
            continue
        if cl.startswith("Encadré 12.2"):
            if not encadre_12_2_done:
                lines_out.append(ENCADRE_12_2)
                encadre_12_2_done = True
            encadre_mode = "skip12.2"
            continue
        if encadre_mode == "skip12.1":
            if cl.startswith("• **Rang A.** Le monitoring") or cl.startswith("Attention") or cl.startswith("Encadré 12.2"):
                encadre_mode = None
                if cl.startswith("Encadré 12.2"):
                    if not encadre_12_2_done:
                        lines_out.append(ENCADRE_12_2)
                        encadre_12_2_done = True
                    encadre_mode = "skip12.2"
            continue
        if encadre_mode == "skip12.2":
            if cl.startswith("Item 17.") or cl.startswith("VI. Critères"):
                encadre_mode = None
                if cl.startswith("VI."):
                    lines_out.append(match_section(cl))
                continue
            continue
        if skip_flowchart:
            if cl.startswith("Fig. 12.1") or cl.startswith("A. Interrogatoire") or cl.startswith("288"):
                skip_flowchart = False
                if cl.startswith("A."):
                    lines_out.append(f"\n## {cl}\n")
                    continue
            else:
                continue
        if "La figure 12.1 résume" in cl or "fig. 12.1" in cl.lower() and "Arbre" not in cl:
            if "La figure 12.1" in cl:
                lines_out.append(cl)
                skip_flowchart = True
                continue
        if cl.startswith("Fig. 12.1") and "Arbre" in cl:
            skip_flowchart = False
        m = SUBSECTION_RE.match(cl)
        if m and in_body and len(cl) < 120:
            lines_out.append(f"\n## {m.group(1)}\n")
            continue
        m2 = NUM_SUBSECTION_RE.match(cl)
        if m2 and in_body and len(cl) < 120:
            lines_out.append(f"\n### {m2.group(1)}\n")
            continue
        fig_handled = False
        fig_m = re.match(r"^Fig\.\s*(12\.\d+)", cl, re.I)
        if fig_m:
            fig_key = f"Fig. {fig_m.group(1)}"
            if fig_key in FIG_MAP:
                fname, caption = FIG_MAP[fig_key]
                lines_out.append(f"\n![{caption}](./img/{fname})\n")
                cap = re.sub(r"^Fig\.\s*12\.\d+\.?\s*[0ODElQ©G]?\s*", "", cl)
                lines_out.append(f"\n**Fig. {fig_m.group(1)}.** {cap.lstrip('0123456789. ')}\n")
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
        ("amné- sie", "amnésie"), ("notam- ment", "notamment"), ("systé- matique", "systématique"),
        ("corona- rienne", "coronarienne"), ("dysautonomie", "dysautonomie"),
        ("cardio- vasculaire", "cardiovasculaire"), ("électro- cardiogramme", "électrocardiogramme"),
        ("écho- cardiographie", "échocardiographie"), ("endocavitaire", "endocavitaire"),
        ("Item 3 42", "Item 342"), ("3 42", "342"), ("1 2.", "12."),
        ("O II s'agit", "**Rang A.** Il s'agit"), ("**Rang A.** II s'agit", "**Rang A.** Il s'agit"),
        ("etç.).EIIe", "etc.). Elle"), ("montreHjne", "montrer une"), ("cardiomyopathîmcjîl tée", "cardiomyopathie dilatée"),
        ("duvejïtricule", "du ventricule"), ("cardiopathie ischémique) avec", "cardiopathie ischémique) avec"),
        ("identifyies situatiops-Mtèque", "identifier les situations à risque vital"),
        ("subite sans autre examen supplémentaire)", "subite sans autre examen supplémentaire"),
        ("d'effortsuggère", "d'effort suggère"), ("parnexemple", "par exemple"),
        ("bioraard Ètirs", "biomarqueurs"), ("utifes", "utiles"),
        ("durées4fex9", "durées de 24"), ("tes< cgpés", "ces syncopes"),
        ("sensible pourJâ\\dysfonction", "sensible pour la dysfonction"),
        ("atriovemTrculaire", "atrioventriculaire"), ("qg èxamen", "un examen"),
        ("mas- sàge", "massage"), ("manoeuvre", "manœuvre"),
        ("Il ne s'agit pas du nœud sinusal mais du sinus (glomus) de l'artère carotide.",
         "> **Attention.** Il ne s'agit pas du nœud sinusal mais du sinus (glomus) de l'artère carotide."),
        ("L'insuffisance cardiaque sévère de stade IV",
         "> **Attention.** L'insuffisance cardiaque sévère de stade IV"),
        ("Il faut éviter le terme de « syncope convulsivante ».",
         "> **Attention.** Il faut éviter le terme de « syncope convulsivante »."),
    ]
    for old, new in fixes:
        text = text.replace(old, new)
    text = re.sub(r"\s*===== PDF PAGE \d+ =====\s*", " ", text)
    text = re.sub(r"(?<=\w)-\s+(?=[a-zàâéèêëîïôùûü])", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"Ce livre a été acheté.*?https://t\.me/Faille_V2\s*", " ", text, flags=re.S)
    if "fig_12_1_arbre_decisionnel.png" not in text and "La figure 12.1" in text:
        fig_block = (
            "\n\n![Fig. 12.1 — Arbre décisionnel en cas de « malaise »]"
            "(./img/fig_12_1_arbre_decisionnel.png)\n\n"
            "**Fig. 12.1.** Arbre décisionnel en cas de « malaise ».\n"
        )
        text = text.replace("La figure 12.1 résume la conduite à tenir en cas de « malaise ».",
                            "La figure 12.1 résume la conduite à tenir en cas de « malaise »." + fig_block)
    if TABLE_12_1.strip() not in text and "tableau 12.1" in text.lower():
        text = text.replace(
            "(tableau 12.1).",
            "(tableau 12.1)." + TABLE_12_1,
            1,
        )
    text = re.sub(
        r"(> À l'issue de ces premières étapes[^\n]+pensez-vous)\n\nqu'il soit",
        r"\1 qu'il soit",
        text,
    )
    text = re.sub(r"\n\nde connaissance brève\n\n", "\n\n", text)
    text = re.sub(
        r"(diagnostic différen-\n• tiel)",
        "diagnostic différentiel",
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
        if line.startswith(("#", "##", "###", "**", "-", "•", ">", "!", "|", "---", "![", "**Tableau", "**Encadré", "**Points")) or re.match(r"^\s+- ", line):
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
    if notions_ind:
        ind_lines = []
        buf = ""
        for n in notions_ind:
            txt = n.lstrip("• ").strip()
            if txt.startswith("tiel ") and buf.endswith("différen-"):
                buf = buf[:-8] + "différentiel " + txt[5:]
            elif txt.startswith("un bilan") and "surveillance et" in buf:
                buf += " " + txt
            elif txt.startswith("avant de porter") and "s'impose" in buf:
                buf += " " + txt
            elif buf:
                ind_lines.append("• " + buf)
                buf = txt
            else:
                buf = txt
        if buf:
            ind_lines.append("• " + buf)
        ind = "\n".join(ind_lines)
    else:
        ind = "• Connaître les principaux éléments permettant de faire le diagnostic différentiel des PDCB.\n• Savoir conduire un interrogatoire pour recueillir les éléments permettant d'orienter le diagnostic différentiel et également les étiologies des syncopes.\n• Bien connaître les critères cliniques et paracliniques qui, devant une syncope, imposent une surveillance et un bilan en hospitalisation.\n• Une syncope n'est jamais banale chez un patient porteur d'une cardiopathie : un bilan complet s'impose avant de porter un diagnostic de syncope vasovagale, qui doit être un diagnostic d'élimination."
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

Questions isolées et corrigés : [Entrainement/QI/342_Malaises_PDCB.md](../../Entrainement/QI/342_Malaises_PDCB.md)
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
        if hits:
            r = hits[0]
            y0 = max(0, r.y0 - 420)
            y1 = min(page.rect.height, r.y1 + 40)
            clip = fitz.Rect(25, y0, page.rect.width - 25, y1)
        else:
            clip = fitz.Rect(25, 80, page.rect.width - 25, page.rect.height - 80)
            print(f"WARN: {label} not found on page {page_idx + 1}, using full clip")
        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
        out = IMG_DIR / fname
        pix.save(str(out))
        print(f"Figure {fig_num} -> {out} ({out.stat().st_size} bytes)")
    doc.close()


def update_readme():
    text = README.read_text(encoding="utf-8")
    row = "| Fait | 342 Malaises PDCB | [III_Rythmologie/342_Malaises_PDCB.md](./III_Rythmologie/342_Malaises_PDCB.md) |\n"
    if "342 Malaises" not in text:
        text = text.replace("| À faire | … | lots suivants |", row + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 342")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    sections = re.findall(r"^# [IVX]+\.", content, re.M)
    fig_count = len(list(IMG_DIR.glob("fig_12_*.png")))
    ok = size > 25_000 and len(sections) >= 7 and fig_count >= 1
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
