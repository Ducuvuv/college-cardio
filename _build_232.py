# -*- coding: utf-8 -*-
"""Generate item 232 fibrillation atriale markdown + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item232.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Cours" / "III_Rythmologie" / "232_Fibrillation_atriale.md"
IMG_DIR = OUT.parent / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "232_Fibrillation_atriale.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Rythmologie\s*$",
    r"^CHAPITRE\s*$",
    r"^13\s*$",
    r"^14\s*$",
    r"^Item 232\s*$",
    r"^Item 232 - Fibrillation.*",
    r"^Fibrillation atriale\s*$",
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
    r"^clés\?\s*$",
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
    r"^mm™.*",
    r"^f 309\s*$",
    r"^[\d\s\.ÏHWMflBï\.\\\/\*]+$",
    r"^::\s*$",
    r"^F:\s*$",
    r"^Si\s*$",
    r"^■B\s*$",
    r"^\*\s*$",
    r"^ü\s*$",
    r"^hi:\s*$",
    r"^'L\s*$",
    r"^Saoudi N,.*",
    r"^Klug D,.*",
    r"^tachycardie atriale,.*",
    r"^maladies vasculaires\..*",
    r"^auriculaire\. In :.*",
    r"^française de cardiologie\..*",
    r"^Médical ; 2005\..*",
    r"^Item 236\s*$",
    r"^Troubles de la conduction\s*$",
    r"^intracardiaque\s*$",
    r"^■w Item 236.*",
]

ECG_GARBAGE = {
    "::", "II", "F:", "Si", "J", "■B", "*", "I", "1", "ü", "■",
    "hi:", "H", "n", "'L", "F",
}

SECTION_MAP = {
    "I. Définition": (
        "\n\n# I. Définition\n\n**Rang A.**"
    ),
    "II. Épidémiologie": (
        "\n\n---\n\n# II. Épidémiologie\n\n**Rang B.**"
    ),
    "III. Physiopathologie et mécanismes": (
        "\n\n---\n\n# III. Physiopathologie et mécanismes\n\n**Rang A.**"
    ),
    "IV. Classification et terminologie": (
        "\n\n---\n\n# IV. Classification et terminologie\n\n**Rang B.**"
    ),
    "V. Diagnostic": (
        "\n\n---\n\n# V. Diagnostic\n\n**Rang A** · **Rang B**."
    ),
    "VI. Évaluation et prévention du risque": (
        "\n\n---\n\n# VI. Évaluation et prévention du risque thromboembolique\n\n**Rang A** · **Rang B**."
    ),
    "VI. Évaluation et prévention du risque thromboembolique": (
        "\n\n---\n\n# VI. Évaluation et prévention du risque thromboembolique\n\n**Rang A** · **Rang B**."
    ),
    "VII. Traitement": (
        "\n\n---\n\n# VII. Traitement\n\n**Rang A** · **Rang B**."
    ),
    "VIII. Différents tableaux cliniques": (
        "\n\n---\n\n# VIII. Différents tableaux cliniques\n\n**Rang B.**"
    ),
    "IX. Dépistage": (
        "\n\n---\n\n# IX. Dépistage\n\n**Rang A.**"
    ),
}

FIG_MAP = {
    "Fig. 13.1": (
        "fig_13_1_fa_petites_mailles.png",
        "Fig. 13.1 — Fibrillation atriale à petites mailles",
    ),
    "Fig. 13.2": (
        "fig_13_2_fa_grosses_mailles.png",
        "Fig. 13.2 — Fibrillation atriale à grosses mailles",
    ),
}

FIGURES = [
    ("13.1", "fig_13_1_fa_petites_mailles.png", 330),
    ("13.2", "fig_13_2_fa_grosses_mailles.png", 331),
]

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")

TABLE_13_1 = """
**Tableau 13.1.** Indications de traitement au long cours selon l'estimation du risque thromboembolique.

| CHA2DS2-VA | FA et prothèse(s) mécanique(s) / RM modéré à sévère | Amylose cardiaque, cardiomyopathie hypertrophique |
|---|---|---|
| **0** : pas d'antithrombotique | AVK | AOD (ou AVK) |
| **≥ 1** : AOD (ou AVK) | AVK | AOD (ou AVK) |

AOD : anticoagulants oraux directs ; AVK : antivitamines K ; RM : rétrécissement mitral.

> Les AOD sont à favoriser par rapport aux AVK (hors prothèse mécanique / RM). Score = 1 : anticoagulants conseillés, discussion bénéfice/risque au cas par cas. Score > 1 : indication indiscutable.
"""

TABLE_13_2 = """
**Tableau 13.2.** Prise en charge selon le type de fibrillation atriale (FA) d'après la classification P-P-P-P.

| Objectif | Premier épisode | FA paroxystique | FA persistante | FA permanente |
|---|---|---|---|---|
| **Anticoagulation** | Initialement, puis selon évolution et terrain | Selon terrain | Avant et après cardioversion, puis selon terrain | Selon terrain |
| **Cardioversion** | Selon évolution | Selon évolution | Oui, si pas de régularisation spontanée | Non, par définition |
| **Contrôle de la fréquence** | Initialement, puis selon évolution | Oui, le plus souvent | En attendant la cardioversion | Oui, le plus souvent |
| **Contrôle du rythme** | Non, le plus souvent | Oui, le plus souvent | Oui, après cardioversion | Non, par définition |
"""

POINTS_BLOCK = """
• Les deux risques principaux liés à la FA sont l'insuffisance cardiaque (rapidité et irrégularité de la cadence ventriculaire) et le risque thromboembolique artériel systémique par formation d'un caillot atrial gauche qui migre dans la grande circulation (et non pas dans la petite circulation).

• Les symptômes, parfois absents, regroupent palpitations, dyspnée ou d'emblée une complication de type infarctus cérébral ou OAP, rarement syncope par pause de régularisation.

• L'ECG montre des QRS rapides (largeur des QRS le plus souvent < 120 ms) et irréguliers, une activité atriale anarchique avec trémulations ou en larges mailles irrégulières (attention aux confusions avec les flutters pour les formes à grandes mailles).

• Les formes cliniques principales sont : la FA souvent paroxystique du sujet d'âge mûr sans cardiopathie sous-jacente ni comorbidité ; la FA compliquée d'un OAP ou d'une insuffisance cardiaque préexistante sur cardiopathie sévère ; la FA révélée par un accident vasculaire cérébral souvent chez la femme âgée hypertendue ; l'association FA et dysfonction sinusale surtout chez le sujet âgé (syndrome bradycardie-tachycardie ou maladie de l'oreillette).

• Les étiologies principales sont :
  - l'HTA +++, les valvulopathies (mitrales davantage qu'aortiques), les SCA et séquelles d'infarctus, tous les types de cardiomyopathie, les péricardites, l'hyperthyroïdie, les cardiopathies congénitales ;
  - les pneumopathies aiguës ou chroniques, l'apnée du sommeil (souvent sous-estimée), l'embolie pulmonaire ;
  - l'hypokaliémie, l'alcoolisme, une réaction vagale, la fièvre ;
  - par élimination : les formes idiopathiques.

• L'enquête étiologique nécessite la réalisation systématique d'une radiographie de thorax, d'une échocardiographie et d'un dosage de TSHus.

• La classification P-P-P-P distingue les quatre formes suivantes :
  - paroxystique : retour spontané ou par cardioversion en rythme sinusal < 7 jours ;
  - persistante : retour spontané ou cardioversion (médicament ou choc électrique) > 7 jours ;
  - permanente : échec de cardioversion ou cardioversion non tentée ;
  - premier épisode : FA non encore classable.

• Le risque thromboembolique est très élevé sur valvulopathie rhumatismale (RM) ou prothèse valvulaire ; très faible en cas de FA sans cardiopathie ni comorbidité ; variable selon le terrain (âge, HTA, diabète, cardiopathie sous-jacente, antécédents emboliques).

• Ce risque, évalué grâce au score CHA2DS2-VA (non applicable en cas de FA avec prothèse valvulaire mécanique et/ou RM modéré à sévère), conditionne la prescription ou non d'anticoagulants oraux au long cours. Dans la FA avec prothèse valvulaire mécanique et/ou RM modéré à sévère, seules les AVK sont recommandées en chronique. Dans les autres situations, il faut privilégier les anticoagulants oraux directs.

• La FA persistante est réduite après 3 à 4 semaines d'anticoagulation efficace (ou à défaut après échographie transœsophagienne pour éliminer un caillot intra-atrial). On utilise le choc électrique externe sous anesthésie générale et/ou les antiarythmiques. Puis l'anticoagulation est poursuivie encore au moins 4 semaines, la prolongation ultérieure étant guidée par le score CHA2DS2-VA. C'est la stratégie dite de contrôle de rythme. Auparavant, on ralentit la cadence ventriculaire par un bradycardisant.

• Pour la FA permanente, on ralentit la cadence ventriculaire par des bradycardisants si nécessaire (bêtabloquants et/ou digitaliques ou vérapamil ou diltiazem). C'est la stratégie dite de contrôle de fréquence qui vise une valeur < 110 bpm à la marche normale pendant 5 minutes, contrôlée par holter. Chez l'insuffisant cardiaque, les inhibiteurs calciques bradycardisants (vérapamil et diltiazem) sont interdits.

• Pour la FA paroxystique, on peut opter pour l'une ou l'autre stratégie ou les deux. Souvent, association d'un antiarythmique et d'un bradycardisant de type bêtabloquant. Chez l'insuffisant cardiaque et le patient coronarien, seule l'amiodarone est autorisée comme antiarythmique.

• En cas de premier épisode, on utilise les AOD en attente de réduction spontanée (HBPM non approuvées). Si besoin, cardioversion planifiée. Habituellement, les antiarythmiques ne sont pas poursuivis après réduction d'un premier épisode.

• En cas de prescription d'AVK, l'INR cible est 2,5 (2 à 3) sauf valve mécanique mitrale (cible plus élevée). L'éducation du patient est primordiale. L'INR est mesuré au minimum 1 fois/mois une fois l'équilibre atteint.
"""

HEADER = '''# Item 232 — Fibrillation atriale

> **Collège CNEC / SFC** · 3e édition (2025) · p. 297–311 · R2C  
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

21 Asthénie.  
24 Bouffées de chaleur.  
27 Chute de la personne âgée.  
50 Malaise/perte de connaissance.  
54 Œdème localisé ou diffus.  
161 Douleur thoracique.  
162 Dyspnée.  
165 Palpitations.  
166 Tachycardie.  
178 Demande/prescription raisonnée et choix d'un examen diagnostique.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
201 Dyskaliémie.  
230 Rédaction de la demande d'un examen d'imagerie.  
231 Demande d'un examen d'imagerie.  
248 Prescription et suivi d'un traitement par anticoagulant et/ou antiagrégant.  
264 Adaptation des traitements sur un terrain particulier (insuffisant rénal, insuffisant hépatique, grossesse, personne âgée, etc.).  
319 Prévention du surpoids et de l'obésité.  
320 Prévention des maladies cardiovasculaires.  
335 Évaluation de l'aptitude au sport et rédaction d'un certificat de non-contre-indication.  
342 Rédaction d'une ordonnance/d'un courrier médical.  
348 Suspicion d'un effet indésirable des médicaments ou d'un soin.  
352 Expliquer un traitement au patient (adulte/enfant/adolescent).  
354 Évaluation de l'observance thérapeutique.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Définition de la fibrillation atriale (FA) | |
| **A** | Physiopathologie | Physiopathologie de la FA | Mécanismes et évolution |
| **B** | Épidémiologie | Épidémiologie de la FA | Prévalence, lien avec HTA et insuffisance cardiaque |
| **A** | Diagnostic positif | Symptômes usuels | |
| **A** | Diagnostic positif | Identifier la FA sur l'électrocardiogramme | |
| **B** | Diagnostic positif | Présentation clinique | Classification en « P » |
| **B** | Étiologies | Formes cliniques usuelles | FA sur cœur normal, FA de l'insuffisance cardiaque, FA et AVC |
| **B** | Étiologies | Formes cliniques non usuelles | FA valvulaire, maladie de l'oreillette |
| **A** | Étiologies | Comorbidités de la FA | HTA, SAOS, éthylisme, obésité |
| **A** | Étiologies | Facteurs déclenchants | FA de cause aiguë |
| **A** | Examens complémentaires | Bilan de 1re intention | ECG, échocardiographie, examens biologiques |
| **A** | Identifier une urgence | Risque thromboembolique et hémorragique | Scores adaptés |
| **A** | Prise en charge | Correction des facteurs de risque | Prise en charge des comorbidités |
| **B** | Prise en charge | Principes de prise en charge de la FA | Contrôle de la fréquence, contrôle du rythme, anticoagulants |
| **B** | Identifier une urgence | Mauvaise tolérance | Indications de cardioversion |

---

## Parcours Rang A

- [I. Définition](#i-définition)
- [III. Physiopathologie et mécanismes](#iii-physiopathologie-et-mécanismes)
- [V. Diagnostic](#v-diagnostic)
- [VI. Évaluation et prévention du risque thromboembolique](#vi-évaluation-et-prévention-du-risque-thromboembolique)
- [VII. Traitement](#vii-traitement)
- [IX. Dépistage](#ix-dépistage)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Définition](#i-définition)
- [II. Épidémiologie](#ii-épidémiologie)
- [III. Physiopathologie et mécanismes](#iii-physiopathologie-et-mécanismes)
- [IV. Classification et terminologie](#iv-classification-et-terminologie)
- [V. Diagnostic](#v-diagnostic)
- [VI. Évaluation et prévention du risque thromboembolique](#vi-évaluation-et-prévention-du-risque-thromboembolique)
- [VII. Traitement](#vii-traitement)
- [VIII. Différents tableaux cliniques](#viii-différents-tableaux-cliniques)
- [IX. Dépistage](#ix-dépistage)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/232_Fibrillation_atriale.md)

---

'''

QI_CONTENT = '''# Entraînement — Item 232 Fibrillation atriale

> Collège CNEC 3e éd. · Chapitre 13 · corrigés p. 583  
> Cours : [232 Fibrillation atriale](../../Cours/III_Rythmologie/232_Fibrillation_atriale.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRM 1

Parmi les examens complémentaires suivants, quels sont ceux que vous prescrivez dans le bilan initial d'un premier passage en fibrillation atriale ?

- A. Une numération formule sanguine
- B. Un dosage de troponine
- C. Une kaliémie
- D. Un dosage de TSHus
- E. Une échocardiographie

**Réponse : A, C, D, E**

Bilan de 1re intention : NFS, ionogramme (kaliémie), TSHus, échocardiographie (**A**, **C**, **D**, **E**). La troponine n'est pas systématique (**B** faux).

---

## QRM 2

Parmi les propositions suivantes, quelles sont celles qui correspondent à une complication classique de la fibrillation atriale ?

- A. Accident vasculaire cérébral hémorragique
- B. Insuffisance cardiaque
- C. Embolie pulmonaire
- D. Cardiomyopathie rythmique
- E. Ischémie aiguë d'un membre

**Réponse : B, D, E**

L'AVC/AIT **ischémique** (embolie à partir de l'auricule gauche) est une complication classique, pas l'AVC hémorragique (**A** faux). Pas de lien direct FA–embolie pulmonaire (**C** faux). Insuffisance cardiaque, cardiomyopathie rythmique (FA rapide) et ischémie aiguë de membre (thromboembolie systémique) sont classiques (**B**, **D**, **E**).

---

## QRM 3

Parmi les propositions suivantes, quelles sont les propositions exactes concernant l'aspect ECG de la fibrillation atriale ?

- A. Les ondes P sont remplacées par une trémulation de la ligne de base
- B. Les QRS sont habituellement larges (> 120 ms)
- C. Les QRS peuvent être réguliers en présence d'un bloc atrioventriculaire complet
- D. L'irrégularité des QRS est la principale caractéristique ECG de la fibrillation atriale
- E. En fibrillation atriale, on ne peut pas interpréter la repolarisation ventriculaire

**Réponse : A, C, D**

Ondes P absentes, trémulations de la ligne de base, QRS irréguliers (**A**, **D**). QRS le plus souvent **fins**, parfois élargis si bloc de branche préexistant ou fréquence-dépendant (**B** faux). QRS réguliers possibles en BAV complet concomitant (**C**). La repolarisation reste interprétable (**E** faux).

---

## QRM 4

Vous avez décidé de faire une cardioversion chez un patient présentant une fibrillation atriale depuis plus de 48 heures. Parmi les propositions suivantes, quelles sont celles qui sont exactes ?

- A. Réaliser la cardioversion après 3 semaines d'anticoagulation efficace
- B. Réaliser la cardioversion dès que l'anticoagulation est efficace
- C. Réaliser la cardioversion après avoir éliminé la présence d'un thrombus endocavitaire par échocardiographie transœsophagienne chez un patient anticoagulé efficacement
- D. La cardioversion peut se faire par choc électrique externe ou par injection IV de médicament antiarythmique
- E. Un traitement anticoagulant efficace d'au moins 4 semaines est nécessaire dans tous les cas après la cardioversion

**Réponse : A, C, D, E**

Anticoagulation ≥ 3 semaines **ou** ETO sans thrombus avant cardioversion si FA > 48 h (**A**, **C**). Pas dès que l'anticoagulation est « efficace » (**B** faux). CEE ou antiarythmique IV (**D**). Poursuite de l'anticoagulation ≥ 4 semaines après (troubles de contraction atriale persistants) (**E**).

---

## QRM 5

Parmi les propositions suivantes, quelles sont celles qui composent le score CHA2DS2-VA ?

- A. L'âge
- B. Le sexe féminin
- C. Le diabète
- D. Une coronaropathie
- E. Le type de fibrillation atriale

**Réponse : A, C, D**

Âge (1 point 65–74 ans, 2 points ≥ 75 ans), diabète (1 point), atteinte vasculaire dont coronaropathie (1 point) (**A**, **C**, **D**). Le sexe féminin n'est plus dans le CHA2DS2-VA (**B** faux). Le type de FA (paroxystique, persistante, etc.) n'entre pas dans le score (**E** faux).
'''


def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    if line in ECG_GARBAGE:
        return None
    if re.match(r"^(297|298|299|300|301|302|303|304|305|306|307|308|309|310|311)$", line):
        return None
    if re.match(r"^[A-G]$", line) and len(line) == 1:
        return None
    if line.startswith("El "):
        line = "• " + line[3:]
    line = line.replace("011 ", "• ")
    line = line.replace("2 32", "232")
    line = line.replace("1 3.", "13.")
    line = line.replace("fig. 1 3", "fig. 13")
    line = line.replace("Fig. 1 3", "Fig. 13")
    line = line.replace("tableau 1 3", "tableau 13")
    line = line.replace("Tableau 1 3", "Tableau 13")
    line = line.replace("1 re", "1re")
    line = line.replace("1 €r", "1re")
    line = line.replace("Ve intention", "1re intention")
    line = line.replace("Item 2 32", "Item 232")
    line = line.replace("VIL ", "VII. ")
    line = line.replace("VL ", "VI. ")
    line = line.replace("dassable", "classable")
    line = line.replace("CHA 2DS2-VA", "CHA2DS2-VA")
    line = line.replace("CHA 2DS2", "CHA2DS2")
    line = line.replace("< 1 10", "< 110")
    line = line.replace("< 1 30", "< 130")
    line = line.replace("2 e intention", "2e intention")
    line = line.replace("tableau 14.1", "tableau 13.1")
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
    line = re.sub(r"^(Fig\. 13\.\d+)\.0 ", r"\1. ", line)
    line = re.sub(r"^(Fig\. 13\.\d+)\. 0 ", r"\1. ", line)
    line = re.sub(r"^(Tableau 13\.\d+)\.0 ", r"\1. ", line)
    line = re.sub(r"^(Tableau 13\.\d+)\. 0 ", r"\1. ", line)
    line = re.sub(r"^(Tableau 13\.\d+)\. D ", r"\1. ", line)
    return line


def match_section(cl):
    if cl == "thromboembolique":
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
        if raw_s.startswith("► Entraînement") or raw_s.startswith("Pour en savoir plus") or raw_s.startswith("===== PDF PAGE 341"):
            break
        if raw_s.startswith("O QRM") or raw_s.startswith("QRM ") or raw_s.startswith("Item 236"):
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
            reflexes.append(cl if cl.startswith("•") else "• " + cl)
    return notions_ind, notions_inacc, reflexes


def extract_body():
    text = SRC.read_text(encoding="utf-8")
    stop_idx = text.find("===== PDF PAGE 342 =====")
    if stop_idx == -1:
        stop_idx = text.find("Item 236")
    chunk = text[:stop_idx] if stop_idx != -1 else text

    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False
    points_manual_done = False
    skip_table = None
    skip_ecg = False
    fig13_2_inserted = False
    table_13_1_done = False
    table_13_2_done = False
    pending_bullet = None

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
            if not points_manual_done:
                lines_out.append(POINTS_BLOCK)
                points_manual_done = True
            in_points = True
            in_body = False
            continue
        if in_points:
            continue
        if skip_table == "13.1":
            if cl.startswith("C. Fermeture") or cl.startswith("VII."):
                skip_table = None
            else:
                continue
        if skip_table == "13.2":
            if cl.startswith("•") or cl.startswith("Les indications") or cl.startswith("D. Éducation") or cl.startswith("VIII."):
                skip_table = None
            else:
                continue
        if skip_ecg:
            if cl.startswith("E. Autres") or cl.startswith("Fig. 13.1") or cl.startswith("Fig. 13.2"):
                skip_ecg = False
            else:
                continue
        hdr = match_section(cl)
        if hdr:
            lines_out.append(hdr)
            in_body = True
            continue
        if cl == "thromboembolique":
            continue
        if cl.startswith("Tableau 13.1"):
            if not table_13_1_done:
                lines_out.append(TABLE_13_1)
                table_13_1_done = True
            skip_table = "13.1"
            continue
        if cl.startswith("Tableau 13.2"):
            if not table_13_2_done:
                lines_out.append(TABLE_13_2)
                table_13_2_done = True
            skip_table = "13.2"
            continue
        if cl.startswith("Fig. 13.1"):
            fname, caption = FIG_MAP["Fig. 13.1"]
            lines_out.append(f"\n![{caption}](./img/{fname})\n")
            lines_out.append("\n**Fig. 13.1.** Fibrillation atriale à petites mailles.\n")
            if not fig13_2_inserted:
                fname2, caption2 = FIG_MAP["Fig. 13.2"]
                lines_out.append(f"\n![{caption2}](./img/{fname2})\n")
                lines_out.append("\n**Fig. 13.2.** Fibrillation atriale à grosses mailles (à ne pas confondre avec le flutter atrial).\n")
                fig13_2_inserted = True
            skip_ecg = True
            continue
        if cl.startswith("Fig. 13.2"):
            continue
        if "fig. 13.2" in cl.lower() and not fig13_2_inserted:
            lines_out.append(cl)
            continue
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
        elif cl == "•":
            continue
        else:
            lines_out.append(cl)
    return "\n".join(lines_out)


def postprocess(text):
    text = re.sub(r">\s*\n+\s*", "> ", text)
    text = re.sub(r"\*\*Rang [AB]\.\*\*\s*\n+\*\*Rang [AB]\.\*\*", "**Rang A.**", text)
    fixes = [
        ("élec- trique", "électrique"),
        ("atrioven- triculaire", "atrioventriculaire"),
        ("cardio- version", "cardioversion"),
        ("écho- cardiographie", "échocardiographie"),
        ("antiaryth- miques", "antiarythmiques"),
        ("thromboembo- lique", "thromboembolique"),
        ("anticoagu- lation", "anticoagulation"),
        ("**Rang A.** II doit", "**Rang A.** Il doit"),
        ("**Rang B.** II s'agit", "**Rang B.** Il s'agit"),
        ("O II doit", "**Rang A.** Il doit"),
        ("□ II s'agit", "**Rang B.** Il s'agit"),
        ("O Lors d'une", "**Rang A.** Lors d'une"),
        ("• Q La prévention", "• **Rang A.** La prévention"),
        ("mettre en place d'un programme", "mettre en place un programme"),
        ("coronaire saines", "coronaires saines"),
        ("Il s’agit", "Il s'agit"),
        ("dont l'insuffisance cardiaque à cause", "sont l'insuffisance cardiaque à cause"),
        ("ou d'une dyspnée d'effort inhabituelle depuis 48 heures.",
         "ou d'une dyspnée d'effort inhabituelle depuis 48 heures."),
    ]
    for old, new in fixes:
        text = text.replace(old, new)
    text = re.sub(r"\s*===== PDF PAGE \d+ =====\s*", " ", text)
    text = re.sub(r"(?<=\w)-\s+(?=[a-zàâéèêëîïôùûü])", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"Ce livre a été acheté.*?https://t\.me/Faille_V2\s*", " ", text, flags=re.S)
    text = re.sub(
        r"(C\. FA valvulaire post-rhumatismale \(RM post-rhumatismal)\n\n(ou prothèse mécanique\))",
        r"\1 \2",
        text,
    )
    text = re.sub(
        r"(> Vous revoyez le patient 48 heures plus tard car il garde des symptômes\. Quelle est votre prise en)\n\n(charge)",
        r"\1 \2",
        text,
    )
    text = re.sub(
        r"(## E\. Autres examens complémentaires \(cf\. aussi infra 3\. Bilan)\n\n(étiologique\))",
        r"\1 \2",
        text,
    )
    if TABLE_13_1.strip() not in text and "tableau 13.1" in text.lower():
        text = text.replace("(tableau 13.1) :", "(tableau 13.1) :" + TABLE_13_1, 1)
    if TABLE_13_2.strip() not in text and "tableau 13.2" in text.lower():
        text = text.replace("(tableau 13.2)", "(tableau 13.2)" + TABLE_13_2, 1)
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
    if notions_ind:
        ind_lines = []
        buf = ""
        for n in notions_ind:
            txt = n.lstrip("• ").strip()
            if txt.startswith("sévère") and buf.endswith("modéré à"):
                buf += " " + txt
            elif txt.startswith("obligatoire") and "cardioversion" in buf:
                buf += " " + txt
            elif txt.startswith("hémorragique") and "risque" in buf:
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
        ind = (
            "• Ne pas oublier l'ECG.\n"
            "• Penser aux maladies valvulaires dans l'enquête étiologique.\n"
            "• Évaluation du risque thromboembolique primordiale.\n"
            "• Ne pas utiliser le score CHA2DS2-VA en cas de FA avec prothèse valvulaire mécanique ou RM modéré à sévère en raison d'un risque d'emblée maximal, ou avant cardioversion en raison d'une anticoagulation obligatoire dans ce contexte.\n"
            "• Toujours peser le rapport bénéfice/risque de l'anticoagulation chronique et donc évaluer le risque hémorragique.\n"
            "• Ne pas confondre contrôle de fréquence et contrôle du rythme."
        )
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

Questions isolées et corrigés : [Entrainement/QI/232_Fibrillation_atriale.md](../../Entrainement/QI/232_Fibrillation_atriale.md)
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
            r = max(hits, key=lambda x: x.y0)
            y0 = max(0, r.y0 - 250)
            y1 = min(page.rect.height, r.y1 + 24)
            clip = fitz.Rect(20, y0, page.rect.width - 20, y1)
        else:
            # Fig. 13.2 unlabeled: ECG at top of page 332
            clip = fitz.Rect(20, 40, page.rect.width - 20, 420)
            print(f"WARN: {label} not found on page {page_idx + 1}, using top-of-page clip")
        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
        out = IMG_DIR / fname
        pix.save(str(out))
        print(f"Figure {fig_num} -> {out} ({out.stat().st_size} bytes)")
    doc.close()


def update_readme():
    text = README.read_text(encoding="utf-8")
    row = "| Fait | 232 Fibrillation atriale | [III_Rythmologie/232_Fibrillation_atriale.md](./III_Rythmologie/232_Fibrillation_atriale.md) |\n"
    if "232 Fibrillation" not in text:
        text = text.replace("| À faire | … | lots suivants |", row + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 232")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    sections = re.findall(r"^# [IVX]+\.", content, re.M)
    fig_count = len(list(IMG_DIR.glob("fig_13_*.png")))
    ok = size > 25_000 and len(sections) >= 9 and fig_count >= 1
    print(f"Course size: {size} bytes, section headers: {len(sections)} ({sections})")
    print(f"Figures: {fig_count} PNGs")
    if "Entraînement" in content.split("## Entraînement")[0][-200:] if "## Entraînement" in content else False:
        pass
    if "QRM 1" in content.split("# I.")[0] if "# I." in content else False:
        print("WARN: QI leaked into course header")
        ok = False
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
