# -*- coding: utf-8 -*-
"""Generate item 234 insuffisance cardiaque de l'adulte markdown + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item234.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Cours" / "IV_IC" / "234_Insuffisance_cardiaque.md"
IMG_DIR = OUT.parent / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "234_Insuffisance_cardiaque.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"Pour avoir plus d’exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^CHAPITRE\s*$",
    r"^CHAPITf\s*$",
    r"^18\s*$",
    r"^19\s*$",
    r"^v Item 234\s*$",
    r"^Item 234\s*$",
    r"^Item 234 -.*",
    r"^Insuffisance cardiaque de l'adulte\s*$",
    r"^Insuffisance cardiaque de l'adu11e\s*$",
    r"^de l'adulte\s*$",
    r"^Insuffisance cardiaque\s*$",
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
    r"^par des flashcodes.*",
    r"^consulte\.com.*",
    r"^clés\s*$",
    r"^clésl\s*$",
    r"^===== PDF PAGE \d+ =====$",
    r"^O QRM\s*\d+.*",
    r"^0 QRM\s*\d+.*",
    r"^GQRM.*",
    r"^QRM\s*\d+.*",
    r"^QRU\s*\d+.*",
    r"^Médecine cardiovasculaire\s*$",
    r"^Adapté de American Heart Association.*",
    r"^Item 1 7\..*",
    r"^Item\. 18 Santé.*",
    r"^Vidéo 18\.\d+.*",
    r"^USIC\s+\d+\s*$",
    r"^aVL\s*$",
    r"^aVF\s*$",
    r"^C6\s*$",
    r"^\[ \s*$",
    r"^f \d+\s*$",
    r"^f\s*$",
    r"^J il H H.*",
    r"^srtifiriaiici.*",
    r"^- «r -u.*",
    r"^à l'entraînement de l'intelligence artificielle.*",
    r"^!St strictement interdite.*",
    r"^: sur https://t\.me/Faille_V2\s*$",
    r"^Faille_V2\s*$",
    r"^Source : Glikson.*",
    r"^Item 226\s*$",
    r"^Thrombose veineuse\s*$",
    r"^profonde et embolie\s*$",
    r"^pulmonaire\s*$",
    r"^Maladie\s*$",
    r"^thromboembolique\s*$",
    r"^veineuse\s*$",
    r"^\(Oy\s*$",
    r"^v\s*$",
    r"^V\s*$",
    r"^B\s*$",
    r"^A\s*$",
]

PAGE_NUM_RE = re.compile(
    r"^(425|426|427|428|429|430|431|432|433|434|435|436|437|438|439|440|"
    r"441|442|443|444|445|446|447|448|449|450|451|452|453|454|455|456|"
    r"457|458|459|460|461|462)\s*[j|]?\s*$"
)

FLOW_GARBAGE = {
    "Suspicion d'IC (terrain, symptômes ou signes)",
    "Suspicion d’IC (terrain, symptômes ou signes)",
    "BNP >35 pg/mL ou NT-proBNP >125 pg/mL",
    "Oui",
    "Non",
    "Échocardiographie",
    "IC peu probable",
    "Confirme ou infirme IC",
    "Prise en charge des patients avec IC à FEVG diminuée",
    "lEC/inhibiteur des récepteurs de la néprilysine et de",
    "l’angiotensine 2'",
    "Bêtabloquants",
    "Antialdostérones",
    "Dapagliflozine/empagliflozine",
    "Diurétiques de l’anse pour rétention hydrosodée",
    "(Classe /)",
    "FEVG >35%",
    "ou traitement électrique",
    "contre-indiqué ou inapproprié",
    "Rythme sinusal",
    "et FEVG <35 %",
    "et QRS >130 ms",
    "FEVG <35%",
    "et QRS <130 ms",
    "et si approprié",
    "DAI",
    "Non ischémique",
    "(Classe lia)",
    "CRT-D2/CRT-P",
    "QRS 130-149 ms",
    "QRS £150 ms",
    "(Classe I)",
    "Ischémique",
    "Si les symptômes persistent, considérer les",
    "traitements recommandés de classe II",
    "Classe NYHA 1",
    "Adaptation/désadaptation cardiaque",
    "Désadaptation périphérique",
    "Poussée d’insuffisance cardiaque aiguë",
}

ECHO_OCR_RE = re.compile(
    r"^(5\.0|2c-S|3V2C|lh148|IM40|loOmm|Larsiologs|taraiolcgc|General|"
    r"7Û3B|70dB|Tl/|11/|Gan=|FC=|SUf|Surf VG|Major Axis|Volume Smpson|"
    r"EE3T-|ld>|1<£|A=2|'60mm)",
    re.I,
)

SECTION_MAP = {
    "I. Généralités": "\n\n# I. Généralités\n\n**Rang A.**",
    "II. Diagnostic": "\n\n---\n\n# II. Diagnostic\n\n**Rang A** · **Rang B**.",
    "III. Diagnostic étiologique": (
        "\n\n---\n\n# III. Diagnostic étiologique\n\n**Rang A.**"
    ),
    "IV. Formes cliniques": "\n\n---\n\n# IV. Formes cliniques\n\n**Rang A** · **Rang B**.",
    "V. Évolution, complications, pronostic": (
        "\n\n---\n\n# V. Évolution, complications, pronostic\n\n**Rang A** · **Rang B**."
    ),
    "VI. Traitement de l'insuffisance cardiaque chronique": (
        "\n\n---\n\n# VI. Traitement de l'insuffisance cardiaque chronique\n\n**Rang A** · **Rang B**."
    ),
    "VII. Traitement de l'insuffisance cardiaque aiguë": (
        "\n\n---\n\n# VII. Traitement de l'insuffisance cardiaque aiguë\n\n**Rang A.**"
    ),
}

FIG_MAP = {
    "Fig. 18.1": (
        "fig_18_1_ondes_q.png",
        "Fig. 18.1 — Ondes Q en antéroseptal évoquant une séquelle d'infarctus du myocarde",
    ),
    "Fig. 18.2": (
        "fig_18_2_cardiomegalie.png",
        "Fig. 18.2 — Cardiomégalie et redistribution vasculaire vers les sommets",
    ),
    "Fig. 18.3": (
        "fig_18_3_oap_rx.png",
        "Fig. 18.3 — Œdème pulmonaire radiologique",
    ),
    "Fig. 18.4": (
        "fig_18_4_echo_volumes.png",
        "Fig. 18.4 — Mesure échocardiographique des volumes télédiastolique (A) et télésystolique (B)",
    ),
    "Fig. 18.5": (
        "fig_18_5_algo_diagnostic.png",
        "Fig. 18.5 — Algorithme pour le diagnostic d'insuffisance cardiaque hors urgence",
    ),
    "Fig. 18.6": (
        "fig_18_6_evolution.png",
        "Fig. 18.6 — Évolution de l'insuffisance cardiaque",
    ),
    "Fig. 18.7": (
        "fig_18_7_algo_traitement_hfref.png",
        "Fig. 18.7 — Algorithme du traitement de l'IC à FEVG diminuée (ESC 2021, classe I)",
    ),
}

FIGURES = [
    ("18.1", "fig_18_1_ondes_q.png", 463, 250),
    ("18.2", "fig_18_2_cardiomegalie.png", 463, 210),
    ("18.3", "fig_18_3_oap_rx.png", 464, 205),
    ("18.4", "fig_18_4_echo_volumes.png", 465, 340),
    ("18.5", "fig_18_5_algo_diagnostic.png", 466, 310),
    ("18.6", "fig_18_6_evolution.png", 473, 280),
    ("18.7", "fig_18_7_algo_traitement_hfref.png", 481, 390),
]

SUBSECTION_RE = re.compile(r"^([A-H]\.\s+[A-ZÉÈÀÔÎÂÙÛÇŒ«].+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s+[A-ZÉÈÀÔÎÂÙÛÇŒ«].+)$")
MNEMONIC_RE = re.compile(r"^([A-G]\.\s+[a-zéèà].+)$")

ENCADRE_18_1 = """
**Encadré 18.1 — Définition de l'insuffisance cardiaque (ESC 2021)**

L'insuffisance cardiaque est un **syndrome clinique** constitué de symptômes cardinaux (dyspnée, œdème des chevilles, fatigue) qui peuvent être accompagnés de signes (turgescence jugulaire, crépitants pulmonaires, œdèmes périphériques). Il est dû à une **anomalie de structure et/ou de fonction du cœur**, entraînant une élévation des pressions intracardiaques et/ou un débit cardiaque inadapté au repos et/ou à l'effort.

Source : McDonagh TA et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. *Eur Heart J* 2021 ; 42 : 3599–726.
"""

ENCADRE_18_2 = """
**Encadré 18.2 — Principaux facteurs déclenchants d'insuffisance cardiaque**

- **Rang A.** Rupture ou observance imparfaite au traitement
- Écarts de régime (sel)
- Surinfection bronchique
- Troubles du rythme (fibrillation atriale)
- Anémie
- Embolie pulmonaire
- Dysthyroïdie (amiodarone)
- Causes iatrogènes : antiarythmique déprimant la fonction cardiaque, bêtabloquants, AINS, inhibiteurs calciques (diltiazem, vérapamil), diminution trop importante de la précharge (diurétiques, vasodilatateurs)
- Poussée hypertensive
- Syndrome coronarien aigu, ischémie myocardique
"""

ENCADRE_18_3 = """
**Encadré 18.3 — Procédures d'introduction et de surveillance d'un traitement par IEC**

- **Rang A.** Commencer à **faibles doses**.
- Surveiller la **pression artérielle**, la **créatininémie** et la **kaliémie** une semaine après l'introduction et après chaque augmentation de doses ; diminuer la posologie ou arrêter en cas d'hypotension artérielle symptomatique ou d'augmentation de la créatinine > 20–30 %.
- Être particulièrement vigilant en cas d'introduction chez un patient âgé, déshydraté ou ayant reçu de fortes doses de diurétiques, diabétique, insuffisant rénal ou ayant déjà une hypotension artérielle (PAS < 100 mmHg).
- Éviter d'introduire simultanément IEC et antialdostérones ; les AINS sont à proscrire.
- Respecter les contre-indications : sténose bilatérale des artères rénales, antécédent d'angio-œdème, grossesse, hyperkaliémie.
"""

ENCADRE_18_4 = """
**Encadré 18.4 — Procédures d'introduction et de surveillance d'un traitement bêtabloquant**

- **Rang A.** Introduire le traitement chez un patient **stabilisé** sans signe de décompensation (instauration possible au décours d'une poussée d'IC avant la sortie).
- Commencer par de **très faibles doses** (en règle : 1/8e de la dose maximale, exemple : 3,125 mg de carvédilol 2 fois/j ou 1,25 mg/j de bisoprolol).
- Augmenter les doses par **paliers hebdomadaires** jusqu'à un maximum de 25 mg 2 fois/j de carvédilol ou de 10 mg/j de bisoprolol, en fonction de la tolérance.
- Surveiller la fréquence cardiaque et la pression artérielle.
- Respecter les contre-indications : asthme ou BPCO sévère, bradycardie ou hypotension symptomatique, BAV 2 ou 3.
"""

TABLE_18_1 = """
**Tableau 18.1.** Classification NYHA (New York Heart Association).

| Stade | Définition |
|---|---|
| **I** | Absence de dyspnée, palpitations ou fatigue pour les efforts habituels : aucune gêne n'est ressentie dans la vie courante |
| **II** | Dyspnée, palpitations ou fatigue pour des efforts importants habituels (marche rapide ou en côte, montée des escaliers > 2 étages) |
| **III** | Dyspnée, palpitations ou fatigue pour des efforts peu intenses de la vie courante (marche en terrain plat, montée des escaliers < 2 étages) |
| **IV** | Dyspnée, palpitations ou fatigue permanente de repos ou pour des efforts minimes (s'habiller, se laver) |

Adapté de l'American Heart Association.
"""

PHYSIO_OAP_BLOCK = """
**Rang A.** Lorsque la pression capillaire pulmonaire s'élève au-delà d'environ **25 mmHg**, un passage de liquide (transsudat) des capillaires vers les alvéoles pulmonaires peut survenir : c'est l'**œdème aigu pulmonaire cardiogénique** (hydrostatique).

**Rang A.** Par opposition, l'**œdème pulmonaire lésionnel** non cardiogénique est dû à des lésions de la membrane alvéolocapillaire (origines nombreuses), avec accumulation intra-alvéolaire. La distinction a une implication immédiate thérapeutique.

### 2. En cas de dysfonction cardiaque

L'organisme réagit en mettant en jeu des mécanismes compensateurs destinés à maintenir le débit cardiaque et les pressions de perfusion des différents organes ; ces mécanismes aboutissent à augmenter le travail et la consommation d'oxygène du cœur et à favoriser les processus d'hypertrophie et de fibrose.
"""

POINTS_BLOCK = """
• L'insuffisance cardiaque est définie par l'association de symptômes (dyspnée) et de signes cliniques à un dysfonctionnement de la pompe cardiaque ; c'est une affection fréquente (1 à 2 % de la population), en particulier chez le sujet âgé (âge moyen du diagnostic : 78 ans). Le pronostic est sévère : environ 50 % de mortalité 5 ans après le diagnostic. La mortalité est le plus souvent due à une mort subite par troubles du rythme ou à une insuffisance cardiaque réfractaire.

• Le signe fonctionnel le plus fréquent est la dyspnée d'effort, quantifiée par la classification de NYHA, mais non spécifique.

• Outre l'ECG et la radiographie de thorax, les examens complémentaires pour confirmer le diagnostic sont le dosage du BNP ou du NT-proBNP et l'échocardiographie.

• Les principales étiologies sont les cardiopathies ischémiques, l'HTA, les maladies du muscle cardiaque (cardiomyopathies). Néanmoins, toutes les affections cardiovasculaires peuvent aboutir à l'insuffisance cardiaque (pathologie valvulaire, troubles du rythme, maladie du péricarde, etc.).

• Lors du bilan, il est important d'éliminer une cardiopathie ischémique si elle n'est pas connue (coroscanner ou coronarographie).

• L'insuffisance cardiaque aiguë caractérise un patient ayant des signes de congestion (hypervolémie, pressions de remplissage élevées) et/ou un bas débit cardiaque. Il faut rechercher des facteurs déclenchants.

• Le patient doit en général être hospitalisé pour recevoir des traitements intraveineux (diurétique, dérivés nitrés, voire inotropes en cas de choc cardiogénique). Le tableau le plus caractéristique est l'OAP, une des grandes urgences cardiovasculaires.

• L'insuffisance cardiaque droite est le plus souvent secondaire à une pathologie du cœur gauche, mais il existe des étiologies d'insuffisance cardiaque droite isolée.

• On oppose les IC à fraction d'éjection abaissée aux IC à fraction d'éjection préservée, forme prédominante chez le sujet âgé.

• Le traitement repose toujours sur la correction d'une cause curable éventuelle (revascularisation coronaire si possible, correction d'une anomalie valvulaire).

• Le traitement symptomatique repose d'abord sur l'éducation du patient et les mesures hygiénodiététiques (régime pauvre en sel, maintien d'une activité physique, vaccination, etc.).

• Le traitement médicamenteux est bien codifié dans l'IC à FE basse (diurétiques, IEC, bêtabloquants, antialdostérone, gliflozines).

• Le traitement « électrique » peut faire appel au DAI pour diminuer le risque de mort subite par FV et/ou au pacemaker biventriculaire en cas de désynchronisation (BBG large).

• En cas de résistance au traitement médical : greffe cardiaque ou pompe d'assistance ventriculaire (attente de greffe ou définitive).

• Le traitement de l'IC à FE préservée est moins codifié mais repose sur la prévention de la FA, des poussées hypertensives et de la surcharge volumique, le traitement de l'ischémie myocardique, et la prescription de gliflozine.
"""

HEADER = '''# Item 234 — Insuffisance cardiaque de l'adulte

> **Collège CNEC / SFC** · 3e édition (2025) · p. 425–462 · R2C  
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
21 Asthénie.  
42 Hypertension artérielle.  
50 Malaise/perte de connaissance.  
54 Œdème localisé ou diffus.  
159 Bradycardie.  
160 Détresse respiratoire aiguë.  
161 Douleur thoracique.  
162 Dyspnée.  
165 Palpitations.  
166 Tachycardie.  
178 Demande/prescription raisonnée et choix d'un examen diagnostique.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
201 Dyskaliémie.  
204 Élévation des enzymes cardiaques.  
232 Demande d'explication d'un patient sur le déroulement, les risques et les bénéfices attendus d'un examen d'imagerie.  
239 Explication préopératoire et recueil de consentement d'un geste invasif diagnostique ou thérapeutique.  
248 Prescription et suivi d'un traitement par anticoagulant et/ou antiagrégant.  
253 Prescrire des diurétiques.  
271 Prescription et surveillance d'une voie d'abord vasculaire.  
285 Consultation de suivi et éducation thérapeutique d'un patient avec un antécédent cardiovasculaire.  
287 Consultation de suivi et éducation thérapeutique d'un patient insuffisant cardiaque.  
320 Prévention des maladies cardiovasculaires.  
328 Annonce d'une maladie chronique.  
352 Expliquer un traitement au patient (adulte/enfant/adolescent).  
354 Évaluation de l'observance thérapeutique.  
355 Organisation de la sortie d'hospitalisation.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Épidémiologie | Épidémiologie de l'IC | Vieillissement, amélioration du traitement des pathologies CV |
| **A** | Définition | IC à FE diminuée ou conservée | Définir HFrEF / HFpEF |
| **A** | Définition | OAP cardiogénique | IC gauche → œdème pulmonaire transsudatif |
| **A** | Définition | Choc cardiogénique | Défaillance aiguë sévère, hypoperfusion, anoxie tissulaire |
| **A** | Physiopathologie | IC gauche et droite | Débit, FE, remodelage, désynchronisation, arythmies ; ICD souvent secondaire à ICG |
| **A** | Physiopathologie | OAP cardiogénique vs lésionnel | Œdème hydrostatique vs lésion de membrane alvéolocapillaire |
| **A** | Diagnostic positif | Diagnostics différentiels de l'OAP | Pneumonie, exacerbation de BPCO, asthme |
| **A** | Diagnostic positif | IC à FE diminuée ou conservée | Valeurs seuils de FEVG |
| **A** | Diagnostic positif | Diagnostic d'une IC | Signes fonctionnels, NYHA, signes physiques, tableaux cliniques |
| **B** | Examens complémentaires | Bilan d'une IC | ECG, biologie, indications coronarographie / coroscanner |
| **A** | Examens complémentaires | Examens en urgence dans l'OAP | ECG, GDS, radio thorax, biologie, BNP/NT-proBNP, troponine, ETT |
| **A** | Examens complémentaires | BNP / NT-proBNP | Intérêt et limites pour diagnostic et suivi |
| **A** | Examens complémentaires | ETT | Diagnostic positif et étiologique |
| **A** | Examens complémentaires | Sémiologie radiographique de l'OAP | Syndrome alvéolo-interstitiel gravitodépendant, Kerley, redistribution, épanchements |
| **A** | Étiologies | Principales étiologies | Ischémique, HTA, valvulopathies, cardiomyopathies, rythmiques |
| **A** | Identifier une urgence | Diagnostic d'un OAP | Détresse respiratoire, orthopnée, crépitants, tachycardie, galop, signes de gravité |
| **A** | Prise en charge | Traitement d'urgence de l'OAP | Diurétiques de l'anse, dérivés nitrés, oxygénothérapie |
| **A** | Prise en charge | Mesures hygiénodiététiques, ETP, réadaptation | Régime pauvre en sel, observance, signes d'alerte |
| **A** | Prise en charge | Classes médicamenteuses HFrEF | Cardioprotecteurs, diurétiques, réadaptation |
| **A** | Suivi / pronostic | Complications de l'IC | Décès, décompensations, rythme, embolie, hypotension, IR |
| **A** | Identifier une urgence | Diagnostiquer un choc cardiogénique | PA, perfusion périphérique, oligurie, conscience |
| **A** | Prise en charge | Traitement du choc cardiogénique | Inotropes, diurétiques |

---

## Parcours Rang A

- [I. Généralités](#i-généralités)
- [II. Diagnostic](#ii-diagnostic)
- [III. Diagnostic étiologique](#iii-diagnostic-étiologique)
- [IV. Formes cliniques](#iv-formes-cliniques)
- [V. Évolution, complications, pronostic](#v-évolution-complications-pronostic)
- [VI. Traitement de l'insuffisance cardiaque chronique](#vi-traitement-de-linsuffisance-cardiaque-chronique)
- [VII. Traitement de l'insuffisance cardiaque aiguë](#vii-traitement-de-linsuffisance-cardiaque-aiguë)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Généralités](#i-généralités)
- [II. Diagnostic](#ii-diagnostic)
- [III. Diagnostic étiologique](#iii-diagnostic-étiologique)
- [IV. Formes cliniques](#iv-formes-cliniques)
- [V. Évolution, complications, pronostic](#v-évolution-complications-pronostic)
- [VI. Traitement de l'insuffisance cardiaque chronique](#vi-traitement-de-linsuffisance-cardiaque-chronique)
- [VII. Traitement de l'insuffisance cardiaque aiguë](#vii-traitement-de-linsuffisance-cardiaque-aiguë)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/234_Insuffisance_cardiaque.md)

---

'''

QI_CONTENT = '''# Entraînement — Item 234 Insuffisance cardiaque de l'adulte

> Collège CNEC 3e éd. · Chapitre 18 · corrigés p. 585  
> Cours : [234 Insuffisance cardiaque](../../Cours/IV_IC/234_Insuffisance_cardiaque.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRM 1

Indiquer les causes d'insuffisance ventriculaire gauche :

- A. Insuffisance mitrale
- B. Rétrécissement mitral
- C. Myocardite
- D. Constriction péricardique
- E. Hypertension artérielle

**Réponse : A, C, E**

Causes d'IVG : IM, myocardite, HTA (**A**, **C**, **E**). Le RM et la constriction péricardique peuvent donner une IC gauche/droite **sans** insuffisance ventriculaire gauche (**B**, **D** faux).

---

## QRM 2

Concernant les peptides natriurétiques (BNP ou NT-proBNP), indiquer les réponses vraies :

- A. Ils sont sécrétés chez l'adulte en réponse à l'étirement des cardiomyocytes
- B. Leur élimination est peu influencée par la fonction rénale
- C. Le NT-proBNP est biologiquement plus actif que le BNP
- D. Ils ont des actions vasodilatatrices
- E. Les taux sont augmentés chez le patient obèse

**Réponse : A, D**

BNP sécrété par étirement des cardiomyocytes ; actions vasodilatatrices (et diurétiques) (**A**, **D**). L'élimination est influencée par le rein (**B** faux). C'est le **BNP** (pas le NT-proBNP) qui est biologiquement actif (**C** faux). Les taux sont **diminués** en cas d'obésité (**E** faux).

---

## QRM 3

M. F, 68 ans, 170 cm, 68 kg, a été hospitalisé pour un infarctus du myocarde. À sa sortie, la FEVG est à 37 % et le bilan biologique retrouve : créatininémie 125 µmol/L, DFG (CKD-EPI) 49 mL/min/1,73 m², kaliémie 4,8 mEq/L, NT-proBNP 3 517 pg/mL. Parmi les propositions suivantes, lesquelles sont vraies ?

- A. Il manque le dosage de la troponine ultrasensible pour le suivi ultérieur
- B. La valeur du NT-proBNP n'est pas interprétable
- C. La valeur du NT-proBNP préjuge d'un pronostic péjoratif
- D. La fonction rénale chez ce patient contre-indique la prescription d'un antagoniste des récepteurs aux minéralocorticoïdes
- E. La kaliémie ne contre-indique pas la prescription conjointe d'un inhibiteur de l'enzyme de conversion et d'un antagoniste des récepteurs aux minéralocorticoïdes

**Réponse : C, E**

NT-proBNP élevé = pronostic péjoratif ; K 4,8 n'interdit pas IEC + ARM (**C**, **E**). La troponine ne fait pas partie du suivi ambulatoire post-IDM (**A** faux). Le NT-proBNP reste interprétable en IR modérée (**B** faux). Créat 125 µmol/L / DFG 49 n'interdit pas un ARM (seuil ≈ 220 µmol/L) (**D** faux).

---

## QRM 4

M. Z, 62 ans, est suivi pour une insuffisance cardiaque gauche post-infarctus, en classe III de la NYHA. Il a été réhospitalisé il y a 6 mois pour une décompensation cardiaque gauche. Son traitement médicamenteux est considéré comme optimisé. La FEVG est mesurée à 32 %, il est en rythme sinusal, il existe un bloc de branche gauche complet avec une largeur de QRS à 150 ms. Quelles mesures thérapeutiques peuvent lui être proposées dans ce contexte ?

- A. Réadaptation cardiaque
- B. Implantation d'un défibrillateur cardiaque automatique
- C. Implantation d'un resynchronisateur cardiaque
- D. Transplantation cardiaque
- E. Prise en charge multidisciplinaire

**Réponse : A, B, C, E**

Réadaptation, DAI (FEVG 32 % NYHA III), CRT (BBG 150 ms), prise en charge multidisciplinaire (**A**, **B**, **C**, **E**). La transplantation n'est pas indiquée en 1re ligne ici : pas d'IC réfractaire NYHA IV (**D** faux).

---

## QRM 5

Un homme de 55 ans est hospitalisé aux urgences en raison d'une orthopnée. L'examen retrouve une polypnée, un galop, des râles crépitants pulmonaires bilatéraux à mi-champs, sa pression artérielle est mesurée à 169/98 mmHg et ses extrémités sont chaudes. L'échocardiographie retrouve un ventricule gauche dilaté et une FEVG à 35 %. Quelles sont les démarches les plus appropriées pour la prise en charge initiale du patient ?

- A. Furosémide per os
- B. Furosémide IV
- C. Bêtabloquant per os
- D. Dérivés nitrés IV
- E. Dobutamine IV

**Réponse : B, D**

OAP congestif « chaud » hypertendu → furosémide **IV** + nitrés IV (**B**, **D**). Pas de furosémide per os, pas de bêtabloquant à la phase aiguë, pas de dobutamine (extrémités chaudes, pas de choc) (**A**, **C**, **E** faux).
'''

DRUG_HEADERS = {
    "Ivabradine",
    "Digoxine",
    "Dérivés nitrés",
    "Amiodarone",
    "Antiagrégants plaquettaires et anticoagulants",
}

SIDE_HEADERS = {
    "Prise en charge des comorbidités",
    "Télésurveillance de l'insuffisance cardiaque",
    "Mécanismes cardiaques",
    "Mécanismes extracardiaques",
}


def clean_line(line):
    line = line.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    if PAGE_NUM_RE.match(line):
        return None
    if line in FLOW_GARBAGE:
        return None
    if ECHO_OCR_RE.match(line):
        return None
    if re.match(r"^[A-G]$", line) and len(line) == 1:
        return None
    if re.match(r"^[\d\.]{1,6}$", line):
        return None
    line = line.replace("adu11e", "adulte")
    line = line.replace("• 0 ", "• **Rang A.** ")
    line = line.replace("• El ", "• **Rang A.** ")
    for prefix, repl in (
        ("• O ", "• **Rang A.** "),
        ("• □ ", "• **Rang B.** "),
        ("• Q ", "• **Rang A.** "),
        ("• D ", "• **Rang B.** "),
        ("• El ", "• **Rang A.** "),
    ):
        if line.startswith(prefix):
            line = repl + line[len(prefix):]
            break
    for prefix, repl in (
        ("El ", "**Rang A.** "),
        ("□ ", "**Rang B.** "),
        ("O ", "**Rang A.** "),
        ("Q ", "**Rang A.** "),
        ("0 ", "**Rang A.** "),
        ("©", "**Rang A.** "),
    ):
        if line.startswith(prefix):
            rest = line[len(prefix):]
            if rest and rest[0].islower() and prefix not in ("El ", "□ ", "O ", "Q ", "0 ", "©"):
                break
            if prefix == "0 " and rest and rest[0].isdigit():
                break
            line = repl + rest
            break
    if line.startswith("D ") and not line.startswith("D. ") and line[2:3].isupper():
        line = "**Rang B.** " + line[2:]
    if line.startswith("| ") or line == "|":
        rest = line[1:].strip()
        if rest.lower().startswith("l'effet délétère") or rest.lower().startswith("les effets délétères"):
            line = "> " + rest
        elif not rest:
            return None
    return line


def match_section(cl):
    for sec, hdr in sorted(SECTION_MAP.items(), key=lambda x: -len(x[0])):
        if cl == sec or cl.startswith(sec + " ") or cl.startswith(sec + "\n"):
            return hdr
        if cl == sec:
            return hdr
    return None


def insert_fig(lines_out, key):
    fname, caption = FIG_MAP[key]
    lines_out.append(f"\n![{caption}](./img/{fname})\n")
    extra = caption.split("—", 1)[-1].strip()
    lines_out.append(f"\n**{key}.** {extra}\n")


def _append_footer(bucket, cl):
    item = cl if cl.startswith("•") else "• " + cl
    if bucket and not cl.startswith("•") and not cl.startswith("**"):
        bucket[-1] = bucket[-1] + " " + cl
    else:
        bucket.append(item)


def extract_footer(text):
    notions_ind, notions_inacc, reflexes = [], [], []
    mode = None
    stop_markers = ("► Entraînement", "GQRM", "O QRM", "===== PDF PAGE 489", "Item 226")
    for raw in text.splitlines():
        raw_s = raw.strip()
        if any(raw_s.startswith(s) for s in stop_markers):
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
            _append_footer(notions_ind, cl)
        elif mode == "inacc":
            _append_footer(notions_inacc, cl)
        elif mode == "reflex":
            _append_footer(reflexes, cl)
    return notions_ind, notions_inacc, reflexes


def extract_body():
    text = SRC.read_text(encoding="utf-8")
    stop = text.find("► Entraînement")
    if stop == -1:
        stop = text.find("===== PDF PAGE 489")
    if stop == -1:
        stop = text.find("Item 226")
    chunk = text[:stop] if stop != -1 else text

    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False
    pending_bullet = None
    pending_header = None
    skip_mode = None
    enc1 = enc2 = enc3 = enc4 = tab1 = False
    physio_done = False
    fig4_skip = False

    def flush_header():
        nonlocal pending_header
        if pending_header:
            lines_out.append(f"\n{pending_header}\n")
            pending_header = None

    def start_header(level, title):
        nonlocal pending_header
        flush_header()
        pending_header = f"{'#' * level} {title}"

    for line in chunk.splitlines():
        stripped = line.strip()
        if stripped == "•":
            pending_bullet = "• "
            continue
        if stripped in ("-", "–"):
            pending_bullet = " - "
            continue
        cl = clean_line(line)
        if cl is None:
            continue
        if pending_bullet:
            if pending_bullet == " - ":
                cl = (" - " if not cl.startswith("-") else " ") + cl
                if lines_out and not cl.startswith(("#", "!", "|")):
                    lines_out[-1] = lines_out[-1].rstrip() + cl
                    pending_bullet = None
                    continue
            elif not cl.startswith(("• ", "- ", "#", "**Rang")):
                cl = pending_bullet + cl
            pending_bullet = None

        if pending_header:
            if (cl[0].islower() or cl.startswith("(") or cl.startswith("ou ")
                    or cl.startswith("avec ") or cl.startswith("cardiaque à")):
                pending_header += " " + cl
                continue
            flush_header()

        if skip_until_vignette:
            if cl.startswith("Vignette clinique"):
                skip_until_vignette = False
                lines_out.append("## Vignette clinique\n")
            continue
        if cl.startswith("Notions indispensables"):
            break
        if cl.startswith("Points") and not in_points:
            flush_header()
            lines_out.append("\n\n---\n\n## Points\n")
            lines_out.append(POINTS_BLOCK)
            in_points = True
            continue
        if in_points:
            continue

        if skip_mode == "enc1":
            if cl.startswith("Le diagnostic peut être difficile"):
                skip_mode = None
            else:
                continue
        if skip_mode == "enc2":
            if cl.startswith("3. Choc") or cl.startswith("### 3"):
                skip_mode = None
            else:
                continue
        if skip_mode == "enc3":
            if cl.startswith("Les IEC diminuent"):
                skip_mode = None
            else:
                continue
        if skip_mode == "enc4":
            if cl.startswith("5. Antialdostérones") or cl.startswith("### 5"):
                skip_mode = None
            else:
                continue
        if skip_mode == "tab1":
            if cl.startswith("L'orthopnée") or cl.startswith("• L'orthopnée"):
                skip_mode = None
            else:
                continue
        if skip_mode == "fig5":
            if cl.startswith("G. Examens") or cl.startswith("BNP :"):
                if cl.startswith("BNP :"):
                    continue
                skip_mode = None
            else:
                continue
        if skip_mode == "fig6":
            if cl.startswith("B. Principales") or cl.startswith("FEVG :"):
                if cl.startswith("FEVG :"):
                    continue
                skip_mode = None
            else:
                continue
        if skip_mode == "fig7":
            if cl.startswith("E. Traitement percutané") or cl.startswith("CRT-D"):
                if cl.startswith("CRT-D") or cl.startswith("Source : McDonagh"):
                    continue
                skip_mode = None
            else:
                continue
        if skip_mode == "physio":
            if cl.startswith("Mécanismes cardiaques") or cl.startswith("Le remodelag") or "dilatation ventriculaire" in cl.lower():
                skip_mode = None
            else:
                continue
        if skip_mode == "echo":
            if cl.startswith("Fig. 18.4"):
                skip_mode = None
            else:
                continue

        if fig4_skip:
            if cl.startswith("Elle peut en plus orienter") or cl.startswith("Fig. 18.4"):
                fig4_skip = False
            elif cl.startswith("Fig. 18.4"):
                fig4_skip = False
            else:
                if not cl.startswith("Fig. 18.4"):
                    if "ventricule gauche chez un patient" in cl or "tion d'éjection" in cl:
                        continue

        garbled_physio = (
            cl.startswith("ral >")
            or cl.startswith("2. En cas de dysfoncti")
            or cl.startswith("alvéoles pulmonaires à l'origine")
            or "c rdiogéniq" in cl
            or cl.startswith("L'organisme réagit en mettant")
        )
        if garbled_physio and not physio_done:
            flush_header()
            lines_out.append(PHYSIO_OAP_BLOCK)
            physio_done = True
            skip_mode = "physio"
            continue

        hdr = match_section(cl)
        if hdr:
            flush_header()
            lines_out.append(hdr)
            in_body = True
            continue

        if cl.startswith("Encadré 18.1"):
            if not enc1:
                lines_out.append(ENCADRE_18_1)
                enc1 = True
            skip_mode = "enc1"
            continue
        if cl.startswith("Encadré 18.2"):
            if not enc2:
                lines_out.append(ENCADRE_18_2)
                enc2 = True
            skip_mode = "enc2"
            continue
        if cl.startswith("Encadré 18.3"):
            if not enc3:
                lines_out.append(ENCADRE_18_3)
                enc3 = True
            skip_mode = "enc3"
            continue
        if cl.startswith("Encadré 18.4"):
            if not enc4:
                lines_out.append(ENCADRE_18_4)
                enc4 = True
            skip_mode = "enc4"
            continue
        if cl.startswith("Tableau 18.1"):
            if not tab1:
                lines_out.append(TABLE_18_1)
                tab1 = True
            skip_mode = "tab1"
            continue

        if cl.startswith("Fig. 18.1"):
            insert_fig(lines_out, "Fig. 18.1")
            continue
        if cl.startswith("Fig. 18.2"):
            insert_fig(lines_out, "Fig. 18.2")
            continue
        if cl.startswith("Fig. 18.3"):
            insert_fig(lines_out, "Fig. 18.3")
            continue
        if cl.startswith("Fig. 18.4"):
            insert_fig(lines_out, "Fig. 18.4")
            fig4_skip = True
            continue
        if cl.startswith("Fig. 18.5"):
            insert_fig(lines_out, "Fig. 18.5")
            skip_mode = "fig5"
            continue
        if cl.startswith("Fig. 18.6"):
            insert_fig(lines_out, "Fig. 18.6")
            skip_mode = "fig6"
            continue
        if cl.startswith("Fig. 18.7"):
            insert_fig(lines_out, "Fig. 18.7")
            skip_mode = "fig7"
            continue

        if cl.startswith("Suspicion d") or cl.startswith("Prise en charge des patients avec IC"):
            continue
        if cl.startswith("Classe NYHA") or cl.startswith("Adaptation/désadaptation"):
            skip_mode = "fig6"
            continue

        if cl in DRUG_HEADERS:
            start_header(4, cl)
            continue
        if cl in SIDE_HEADERS:
            start_header(3, cl)
            continue

        mnem = MNEMONIC_RE.match(cl)
        if mnem and in_body:
            letter = mnem.group(1)[0]
            rest = mnem.group(1)[3:]
            lines_out.append(f"• **{letter}.** {rest}")
            continue

        m = SUBSECTION_RE.match(cl)
        if m and in_body and len(cl) < 160:
            start_header(2, m.group(1))
            continue
        m2 = NUM_SUBSECTION_RE.match(cl)
        if m2 and in_body and len(cl) < 140:
            start_header(3, m2.group(1))
            continue

        if cl.startswith("> "):
            lines_out.append(cl)
        elif cl.startswith(">"):
            lines_out.append("> " + cl[1:].strip())
        elif cl.startswith("- ") or cl.startswith("• "):
            lines_out.append(cl)
        else:
            lines_out.append(cl)

    flush_header()
    if not in_points:
        lines_out.append("\n\n---\n\n## Points\n")
        lines_out.append(POINTS_BLOCK)
    return "\n".join(lines_out)


def postprocess(text):
    text = re.sub(r">\s*\n+\s*", "> ", text)
    text = re.sub(r"(?<=\w)-\s+(?=[a-zàâéèêëîïôùûüçœ])", "", text)
    fixes = [
        ("**Rang A.** Toutes les pathologies", "**Rang A.** Toutes les pathologies"),
        ("l 'incapacité", "l'incapacité"),
        ("des-pressions diastoliqyS5e transme'", "des pressions diastoliques se transmet"),
        ("une gênent retour veineux", "une gêne au retour veineux"),
        ("gênent retour", "gêne au retour"),
        ("Le remodelag£<«$3faque es| cféflbi comme", "Le remodelage cardiaque est défini comme"),
        ("Le remodelage cardiaque es| cféflbi comme", "Le remodelage cardiaque est défini comme"),
        ("5 Umin", "5 L/min"),
        ("captopril 1 50 mg", "captopril 150 mg"),
        ("QRS > 1 20 ms", "QRS > 120 ms"),
        ("O II doit", "**Rang A.** Il doit"),
        ("**Rang A.** II doit", "**Rang A.** Il doit"),
        ("O II ", "Il "),
        ("llb, C", "IIb, C"),
        ("llb, B", "IIb, B"),
        ("recommandation llb", "recommandation IIb"),
        ("(Classe lia)", "(Classe IIa)"),
        ("AA2", "ARA2"),
        ("J'IC", "l'IC"),
        ("de J'IC", "de l'IC"),
        ("unjraitement", "un traitement"),
        ("ransthyrétine", "transthyrétine"),
        ("tafami- dis", "tafamidis"),
        ("cardiologue eVfé médecin", "cardiologue et le médecin"),
        ("insuffisance cardi que de réhospitalisations est important",
         "insuffisance cardiaque, le risque de réhospitalisations est important"),
        ("Après une première hospitalisation pour insuffisance cardiaque que de réhospitalisations est important",
         "Après une première hospitalisation pour insuffisance cardiaque, le risque de réhospitalisations est important"),
        ("avec cardiologue et le médecin généraliste", "avec le cardiologue et le médecin généraliste"),
        ("classes ll-lll", "classes II-III"),
        ("l'insuffisance cardiaque et fortement", "l'insuffisance cardiaque est fortement"),
        ("c'està-dire", "c'est-à-dire"),
        ("postgreffe", "post-greffe"),
        ("IMC 32 kg/m 2", "IMC 32 kg/m²"),
        ("de 1'1M", "de l'IM"),
        ("TSHus;", "TSHus ;"),
        ("NT pro-BNP", "NT-proBNP"),
        ("V0 2", "VO2"),
        ("préservée) et se rencontre", "préservée et se rencontre"),
        ("d'un fait de l'augmentation", "du fait de l'augmentation"),
        ("lors des épisodes l'alitement", "lors des épisodes d'alitement"),
        ("celle des IEC", "celles des IEC"),
        ("et de la pression artérielle", "et la pression artérielle"),
        ("On parle de désynchronisation quand", "On parle de désynchronisation quand"),
        ("Stade I\n", ""),
    ]
    for old, new in fixes:
        text = text.replace(old, new)
    text = re.sub(r"Pour avoir plus d['’]exclusivités.*?Faille_V2\s*", " ", text)
    text = re.sub(r"Ce livre a été acheté.*?Faille_V2\s*", " ", text, flags=re.S)
    text = re.sub(r"Faille_V2", " ", text)
    text = re.sub(
        r"(> Une fois l['’]épisode aigu contrôlé, quelle prise en charge thérapeutique envisagez-vous pour le)\n\n(moyen et le long terme \?)",
        r"\1 \2",
        text,
    )
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
        if (line.startswith(("#", "##", "###", "####", "**", "- ", "• ", ">", "!", "|", "---"))
                or re.match(r"^\s+- ", line)):
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append(line)
        else:
            if not buf and paragraphs:
                prev = paragraphs[-1]
                if prev.startswith(("• ", "- ", "> ", "**Rang")):
                    paragraphs[-1] = prev + " " + line.strip()
                    continue
            buf.append(line.strip())
    if buf:
        paragraphs.append(" ".join(buf))
    return "\n\n".join(p for p in paragraphs if p is not None)


def make_footer(notions_ind, notions_inacc, reflexes):
    ind = "\n".join(n if n.startswith("•") else "• " + n for n in notions_ind) or (
        "• Devant une IC à FEVG abaissée, il faut toujours penser à éliminer une origine ischémique (coronarographie ou coroscanner chez le sujet jeune).\n"
        "• Le traitement médical de l'IC à FEVG abaissée repose sur 5 classes : diurétiques de l'anse, bloqueurs du SRAA (IEC ou sacubitril/valsartan ou ARA2), bêtabloquants, antialdostérones, gliflozines.\n"
        "• Les gliflozines sont hautement recommandées pour l'IC à FEVG conservée.\n"
        "• L'OAP est une urgence cardiovasculaire dont la prise en charge doit être parfaitement connue.\n"
        "• Connaître les facteurs favorisant une poussée d'IC aiguë.\n"
        "• Prendre en compte et traiter les comorbidités."
    )
    inacc = "\n".join(n if n.startswith("•") else "• " + n for n in notions_inacc) or (
        "• Méconnaître les médicaments contre-indiqués dans l'IC à FE altérée (vérapamil ou diltiazem, antiarythmiques de classe I comme la flécaïne), et ne pas savoir que les AINS doivent être évités.\n"
        "• Oublier les conseils de régime pauvre en sel."
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

Questions isolées et corrigés : [Entrainement/QI/234_Insuffisance_cardiaque.md](../../Entrainement/QI/234_Insuffisance_cardiaque.md)
"""


def build_course():
    text = SRC.read_text(encoding="utf-8")
    body = postprocess(merge_paragraphs(extract_body()))
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
    for fig_num, fname, page_idx, height in FIGURES:
        page = doc[page_idx]
        label = f"Fig. {fig_num}"
        hits = page.search_for(label)
        if not hits:
            for alt in (f"Fig. {fig_num}.", f"fig. {fig_num}", f"Fig. {fig_num}."):
                hits = page.search_for(alt)
                if hits:
                    break
        if hits:
            r = max(hits, key=lambda x: x.y0)
            y1 = min(page.rect.height, r.y1 + 10)
            y0 = max(0, r.y0 - height)
            others = []
            for other_num, _, other_idx, _ in FIGURES:
                if other_idx != page_idx or other_num == fig_num:
                    continue
                oh = page.search_for(f"Fig. {other_num}")
                if oh:
                    others.append(max(oh, key=lambda x: x.y0))
            for oc in others:
                if oc.y0 < r.y0 and (r.y0 - oc.y1) < height:
                    y0 = max(y0, oc.y1 + 4)
            clip = fitz.Rect(22, y0, page.rect.width - 22, y1)
        else:
            clip = fitz.Rect(20, 50, page.rect.width - 20, 420)
            print(f"WARN: {label} not found on page {page_idx + 1}")
        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
        out = IMG_DIR / fname
        pix.save(str(out))
        print(f"Figure {fig_num} -> {out.name} ({out.stat().st_size} bytes)")
    doc.close()


def update_readme():
    text = README.read_text(encoding="utf-8")
    row = "| Fait | 234 Insuffisance cardiaque | [IV_IC/234_Insuffisance_cardiaque.md](./IV_IC/234_Insuffisance_cardiaque.md) |\n"
    if "234 Insuffisance cardiaque" not in text:
        text = text.replace("| À faire | … | lots suivants |", row + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 234")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    sections = re.findall(r"^# [IVX]+\.", content, re.M)
    fig_count = len(list(IMG_DIR.glob("fig_18_*.png")))
    print(f"Course size: {size} bytes, section headers: {len(sections)} ({sections})")
    print(f"Figures: {fig_count} PNGs")
    if size < 40_000:
        print("WARN: course < 40 KB")
    if len(sections) < 7:
        print("WARN: missing section headers")
    if fig_count < 6:
        print("WARN: fewer than 6 figures")
    head = content.split("## Réflexes")[0] if "## Réflexes" in content else content
    if "Item 226" in head or "Thrombose veineuse profonde" in content:
        print("WARN: Item 226 leak")
    else:
        print("No Item 226 leak")
    qi = QI_OUT.read_text(encoding="utf-8")
    print(f"QI size: {len(qi.encode('utf-8'))} bytes")


def main():
    build_course()
    build_qi()
    extract_figures()
    update_readme()
    verify()


if __name__ == "__main__":
    main()
