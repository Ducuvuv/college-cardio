# -*- coding: utf-8 -*-
"""Generate item 153 surveillance porteurs valves/prothèses markdown + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item153.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Cours" / "II_Valves" / "153_Surveillance_porteurs_valves_protheses.md"
IMG_DIR = OUT.parent / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "153_Surveillance_porteurs_valves_protheses.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Maladies des valves\s*$",
    r"^Item 153\s*$",
    r"^Item 153 - Surveillance.*",
    r"^Item 1 53.*Surveillance.*",
    r"^Surveillance des porteurs\s*$",
    r"^de valve et prothèses\s*$",
    r"^vasculaires1?\s*$",
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
    r"^nts\s*$",
    r"^à l'entraînement de l'intelligence artificielle.*",
    r"^!St strictement interdite.*",
    r"^: sur https://t\.me/Faille_V2\s*$",
    r"^===== PDF PAGE \d+ =====$",
    r"^O QRM\s*\d+.*",
    r"^© QRM\s*\d+.*",
    r"^G QRM\s*\d+.*",
    r"^QRM\s*\d+.*",
    r"^QRU\s*\d+.*",
    r"^Vidéo 10\.\d+.*",
    r"^10\s*$",
    r"^11\s*$",
    r"^Médecine cardiovasculaire\s*$",
    r"^Figure [A-F] : ©.*",
    r"^© Zoghbi WA.*",
    r"^© Acknowledgement.*",
    r"^© Pericardial.*",
    r"^© Bernardi.*",
    r"^© Popma JJ.*",
    r"^©Transcatheter.*",
    r"^Source : (Vahanian|Rahimtoola|Fédération|Laboratoire).*",
    r"^endorsed by.*",
    r"^conjonction with.*",
    r"^conjunction with.*",
    r"^and Canadien Society.*",
    r"^and Canadian Society.*",
    r"^J Am Soc Echocardiogr.*",
    r"^Figure B : dessin.*",
    r"^A\. Prothèse à bille.*",
    r"^Shiley®\. C\. Prothèse.*",
    r"^[\d\s\.ÏHWMflBï\.]+$",
]

FLOWCHART_GARBAGE = {
    "Remplacement valvulaire", "Remplacement valvulaire aortique : âge > 60 ans",
    "Remplacement valvulaire aortique : âge < 60 ans", "Remplacement valvulaire mitral : âge > 65 ans",
    "Remplacement valvulaire mitral : âge < 65 ans", "Choix du patient", "Fibrillation atriale",
    "Autre risque cardioembolique", "Non", "Oui", "Espérance de vie très", "courte < 5 ans",
    "Risque hémorragique", "Élevé", "Très élevé", "Valve mécanique", "Bioprothèse",
    "Échocardiographie", "Biologie", "Surveillance clinique", "Cartes de suivi",
    "INR (AVK) selon", "le type de prothèse", "et la nécessité", "d'une AC",
    "À compléter selon", "les comorbidités", "et d'éventuelles", "complications",
    "Carte de porteur de prothèse", "Carnet de suivi de l'AC", "Carte d'antibioprophylaxie",
    "Symptômes", "Fièvre, foyers infectieux (dentaires ++)", "Examen clinique",
    "Suivi dentaire au moins biannuel", "Transthoracique pour", "le suivi conventionnel",
    "bidimensionnel et doppler", "(gradient, absence", "de régurgitation)",
    "Transoesophagienne", "seulement en cas", "de dysfonction", "Prothèse mécanique :",
    "bruits d'ouverture", "et fermeture claqués", "Prothèse biologique :",
    "bruits identiques", "à ceux des valves natives", "INTERVENTION VALVULAIRE",
    "Réalisée", "par voie chirurgicale par voie percutanée", "Date et lieu de réalisation :",
    "Nom du chirurgien:", "Aortique", "Mitrale", "Autres", "Mécanique", "Biologique",
    "TAVI", "Réparation", "Cty mitral", "Tncuspide", "Pulmonaire", "Modèie/ref.:",
    "MocWref.:", "Modèle ref :", "N° de série;", "Diamètre :", "Diamètre: __________________",
    "C'atguCM'l\\Kjn/(v", "Rtmnkn", "Si Srttnji", "A (je»", "FC 62", "Schizocyte",
    "A", "B", "C", "D", "E", "F", ".", "65", "/", "D", "æ»", "u", "i", "f", "»",
    "Remplacement valvulaire", "_________________", "_________ ___", "f________________________",
}

SECTION_MAP = {
    "I. Les différents types de prothèses valvulaires": "\n\n# I. Les différents types de prothèses valvulaires\n\n**Rang A.**",
    "II. Physiopathologie": "\n\n---\n\n# II. Physiopathologie\n\n**Rang A.**",
    "III. Complications des prothèses valvulaires": "\n\n---\n\n# III. Complications des prothèses valvulaires\n\n**Rang A.**",
    "III. Complications des valves cardiaques": "\n\n---\n\n# III. Complications des prothèses valvulaires\n\n**Rang A.**",
    "IV. Surveillance des porteurs de valve cardiaque": "\n\n---\n\n# IV. Surveillance des porteurs de valve cardiaque\n\n**Rang A.**",
}

FIG_MAP = {
    "Fig. 10.1": ("fig_10_1_protheses_mecaniques.png", "Fig. 10.1 — Prothèses mécaniques (Starr®, Björk-Shiley®, St-Jude®)"),
    "Fig. 10.2": ("fig_10_2_bioprotheses_chirurgicales.png", "Fig. 10.2 — Bioprothèses chirurgicales stentées (xénogreffes)"),
    "Fig. 10.3": ("fig_10_3_valves_humaines.png", "Fig. 10.3 — Valves humaines (homogreffes, Ross, Ozaki)"),
    "Fig. 10.4": ("fig_10_4_bioprotheses_stentless.png", "Fig. 10.4 — Bioprothèses stentless"),
    "Fig. 10.5": ("fig_10_5_tavi.png", "Fig. 10.5 — Endoprothèses aortiques percutanées (TAVI/TAVR)"),
    "Fig. 10.6": ("fig_10_6_algorithme_choix_prothese.png", "Fig. 10.6 — Algorithme décisionnel pour le choix d'une prothèse"),
    "Fig. 10.7": ("fig_10_7_thrombose_mecanique.png", "Fig. 10.7 — Thrombose obstructive de prothèse mécanique mitrale"),
    "Fig. 10.8": ("fig_10_8_thrombose_tavi.png", "Fig. 10.8 — Thrombose obstructive d'endoprothèse CoreValve®"),
    "Fig. 10.9": ("fig_10_9_endocardites_prothese.png", "Fig. 10.9 — Endocardites sur prothèses"),
    "Fig. 10.10": ("fig_10_10_degenerescence.png", "Fig. 10.10 — Dégénérescence structurelle calcifiée de bioprothèse aortique"),
    "Fig. 10.11": ("fig_10_11_desinsertion.png", "Fig. 10.11 — Désinsertion de bioprothèse mitrale et schizocyte"),
    "Fig. 10.12": ("fig_10_12_pannus.png", "Fig. 10.12 — Dysfonction sténosante par pannus"),
    "Fig. 10.13": ("fig_10_13_surveillance_long_cours.png", "Fig. 10.13 — Surveillance au long cours des porteurs de prothèse"),
    "Fig. 10.14": ("fig_10_14_carte_intervention.png", "Fig. 10.14 — Carte d'intervention valvulaire"),
    "Fig. 10.15": ("fig_10_15_coaguchek.png", "Fig. 10.15 — Système CoaguChek® INRange"),
}

FIGURES = [
    ("10.1", "fig_10_1_protheses_mecaniques.png", 270),
    ("10.2", "fig_10_2_bioprotheses_chirurgicales.png", 271),
    ("10.3", "fig_10_3_valves_humaines.png", 272),
    ("10.4", "fig_10_4_bioprotheses_stentless.png", 273),
    ("10.5", "fig_10_5_tavi.png", 274),
    ("10.6", "fig_10_6_algorithme_choix_prothese.png", 275),
    ("10.7", "fig_10_7_thrombose_mecanique.png", 277),
    ("10.8", "fig_10_8_thrombose_tavi.png", 278),
    ("10.9", "fig_10_9_endocardites_prothese.png", 279),
    ("10.10", "fig_10_10_degenerescence.png", 280),
    ("10.11", "fig_10_11_desinsertion.png", 282),
    ("10.12", "fig_10_12_pannus.png", 282),
    ("10.13", "fig_10_13_surveillance_long_cours.png", 284),
    ("10.14", "fig_10_14_carte_intervention.png", 284),
    ("10.15", "fig_10_15_coaguchek.png", 287),
]

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")

TABLE_10_1 = """
**Tableau 10.1.** Synthèse des caractéristiques des différents types de prothèses valvulaires.

| | Prothèse mécanique | Bioprothèse |
|---|---|---|
| **Indications** | Choix du patient ; absence de contre-indication aux AVK ; risque de dégénérescence précoce (hypoparathyroïdie, IRC) ; autres indications d'AVK (FA, MTE) ; patient jeune avec espérance de vie raisonnable : < 60 ans en position aortique, < 65 ans en position mitrale ; éducation thérapeutique possible ; souhait d'une intervention définitive (haut risque chirurgical si réintervention) | Choix du patient ; risque de complication (compliance) ou contre-indication aux AVK (risque hémorragique, comorbidités, conduites à risque) ; ATCD de thrombose de prothèse mécanique malgré INR efficace ; désir de grossesse ; faible risque de réintervention ; patient âgé ou espérance de vie inférieure à celle de la bioprothèse : ≥ 65 ans en position aortique, ≥ 70 ans en position mitrale |
| **Avantages** | Durée prolongée (> 15 ans en l'absence de complication) | Pas d'anticoagulation à vie |
| **Inconvénients / complications** | Anticoagulation à vie avec risque de thrombose (sous-dosage) ou de saignement (surdosage) ; endocardite infectieuse ; désinsertion, hémolyse ; bruits de valve perçus | Durée courte : 10–15 ans avec dégénérescence ; endocardite infectieuse ; désinsertion ; thrombose |
| **Suivi au long cours** | Anticoagulation à vie selon INR cible, éducation, auto-INR ; suivi cardiologique annuel ; prévention de l'endocardite infectieuse dont soins dentaires biannuels avec antibioprophylaxie ; port d'une carte | Anticoagulation/antiagrégants 3 mois postopératoires selon recommandations ; suivi cardiologique annuel ; prévention de l'endocardite infectieuse dont soins dentaires biannuels avec antibioprophylaxie ; port d'une carte |

ATCD : antécédent ; AVK : antivitamine K ; FA : fibrillation atriale ; INR : international normalized ratio ; IRC : insuffisance rénale chronique ; MTE : maladie thromboembolique.
"""

TABLE_10_2 = """
**Tableau 10.2.** INR cible pour les valves mécaniques.

| Risque thrombotique de la prothèse | Sans facteur de risque lié au patient | Avec facteur(s) de risque lié au patient |
|---|---|---|
| Faible | 2,5 | 3,0 |
| Moyen | 3,0 | 3,5 |
| Élevé | 3,5 | 4,0 |

Facteurs de risque liés au patient : remplacement valvulaire mitral ou tricuspide ; antécédent thromboembolique ; FA ; sténose mitrale quel que soit le degré ; FEVG < 35 %.

Prothèses à risque faible : Carbomedics, Medtronic Hall, ATS, Medtronic Open-Pivot, St Jude Medical, Sorin Bicarbon.

Prothèses à risque moyen : autres valves à double ailette avec données insuffisantes.

Prothèses à risque élevé : Lillehei-Kaster, Omniscience, Starr-Edwards (cage à bille), Björk-Shiley et autres prothèses à disque.

Source : Vahanian A, Beyersdorf F, Praz F, et al. 2021 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2022;43(7):561–632.
"""

TABLE_10_3 = """
**Tableau 10.3.** Anticoagulation pour les bioprothèses.

| Prothèse | Anticoagulation / AAP | AOD |
|---|---|---|
| Bioprothèse aortique | Aspirine ou AVK 3 mois puis rien | Autorisé > 3 mois si indication non valvulaire |
| Bioprothèse mitrale | AVK 3 mois puis rien | Toléré dès le postopératoire si FA ; autorisé > 3 mois si indication non valvulaire |
| Bioprothèse tricuspide, plastie mitrale | AVK 3 mois puis rien | Autorisé > 3 mois si indication non valvulaire |
| Endoprothèse aortique (TAVI) | Aspirine seule au long cours si rythme sinusal ; anticoagulation si FA | Autorisé si indication FA |

AAP : antiagrégant plaquettaire ; AOD : anticoagulant oral direct ; AVK : antivitamine K ; FA : fibrillation atriale ; TAVI : transcatheter aortic valve implantation.

Source : Vahanian A, Beyersdorf F, Praz F, et al. 2021 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2022;43(7):561–632.
"""

HEADER = '''# Item 153 — Surveillance des porteurs de valve et prothèses

> **Collège CNEC / SFC** · 3e édition (2025) · p. 238–260 · R2C  
> Partie II — Maladies des valves  
> **Note :** seule la partie concernant les **prothèses valvulaires** est traitée ici (pas les prothèses vasculaires).

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
22 Diminution de la diurèse.  
44 Hyperthermie/fièvre.  
50 Malaise/perte de connaissance.  
58 Splénomégalie.  
59 Tendance au saignement.  
60 Hémorragie aiguë.  
89 Purpura/ecchymose/hématome.  
102 Hématurie.  
121 Déficit neurologique sensitif et/ou moteur.  
147 Épistaxis.  
160 Détresse respiratoire aiguë.  
161 Douleur thoracique.  
162 Dyspnée.  
165 Palpitations.  
166 Tachycardie.  
178 Demande/prescription raisonnée et choix d'un examen diagnostique.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
190 Hémoculture positive.  
203 Élévation de la protéine C-réactive (CRP).  
217 Baisse de l'hémoglobine.  
248 Prescription et suivi d'un traitement par anticoagulant et/ou antiagrégant.  
255 Prescrire un anti-infectieux.  
285 Consultation de suivi et éducation thérapeutique d'un patient avec antécédent cardiovasculaire.  
352 Expliquer un traitement au patient (adulte/enfance/adolescent).  
354 Évaluation de l'observance thérapeutique.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Différents types de prothèses valvulaires | Prothèses mécaniques, bioprothèses chirurgicales et percutanées |
| **A** | Définition | Principales complications des prothèses valvulaires | Savoir les énumérer |
| **A** | Suivi et/ou pronostic | Modalités de surveillance des porteurs de prothèses valvulaires | |
| **A** | Identifier une urgence | Patient porteur de prothèse valvulaire à risque infectieux | Endocardite infectieuse, greffe |
| **A** | Suivi et/ou pronostic | Valeurs cibles d'INR selon prothèse et terrain | |
| **A** | Diagnostic positif | Diagnostic d'une désinsertion de prothèse valvulaire | Incluant l'hémolyse |

---

## Parcours Rang A

- [I. Les différents types de prothèses valvulaires](#i-les-différents-types-de-prothèses-valvulaires)
- [III. Complications des prothèses valvulaires](#iii-complications-des-prothèses-valvulaires)
- [IV. Surveillance des porteurs de valve cardiaque](#iv-surveillance-des-porteurs-de-valve-cardiaque)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Les différents types de prothèses valvulaires](#i-les-différents-types-de-prothèses-valvulaires)
- [II. Physiopathologie](#ii-physiopathologie)
- [III. Complications des prothèses valvulaires](#iii-complications-des-prothèses-valvulaires)
- [IV. Surveillance des porteurs de valve cardiaque](#iv-surveillance-des-porteurs-de-valve-cardiaque)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/153_Surveillance_porteurs_valves_protheses.md)

---

'''

QI_CONTENT = '''# Entraînement — Item 153 Surveillance des porteurs de valve et prothèses

> Collège CNEC 3e éd. · Chapitre 10 · corrigés p. 581  
> Cours : [153 Surveillance porteurs valves/prothèses](../../Cours/II_Valves/153_Surveillance_porteurs_valves_protheses.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRM 1

Concernant les prothèses valvulaires cardiaques, quelles sont les réponses exactes ?

- A. Elles nécessitent une anticoagulation efficace
- B. Elles sont une solution curative des valvulopathies
- C. Elles font partie du « groupe à haut risque » pour la prévention de l'endocardite
- D. Elles nécessitent une surveillance par échocardiographie transœsophagienne
- E. Elles nécessitent un suivi dentaire au moins annuel

**Réponse : B, C**

Seules les **prothèses mécaniques** nécessitent une anticoagulation efficace à vie ; pour les bioprothèses, l'anticoagulation n'est justifiée que les 3 premiers mois ou s'il existe une autre indication (FA) (**A** faux). Le remplacement valvulaire est curatif ; le suivi dentaire est **biannuel** avec antibioprophylaxie (**E** faux). L'ETO n'est pas systématique au suivi normal (**D** faux).

---

## QRM 2

Quelles sont les différentes complications communes des deux types de prothèses ?

- A. L'endocardite infectieuse
- B. L'hémolyse
- C. La désinsertion de prothèse
- D. La dégénérescence de prothèse
- E. La thrombose de prothèse

**Réponse : A, B, C, E**

EI, hémolyse, désinsertion et thrombose peuvent toucher les deux types. La **dégénérescence** concerne surtout les bioprothèses (**D** faux).

---

## QRM 3

Que comporte le suivi d'un patient porteur de prothèse valvulaire ?

- A. Consultation cardiologique à 3 mois avec ECG de repos
- B. Échocardiographie de référence à 6 mois postopératoires
- C. Traitement rapide de toute fièvre par antibiothérapie probabiliste
- D. Bilan d'hémolyse annuel
- E. Éducation thérapeutique

**Réponse : A, E**

Consultation cardiologique à 3 mois avec ECG ; échocardiographie de référence à **8–12 semaines** (2e–4e mois), pas à 6 mois (**B** faux). Pas d'antibiothérapie à l'aveugle : hémocultures d'abord (**C** faux). Bilan d'hémolyse annuel non recommandé (**D** faux). Éducation thérapeutique (EI, anticoagulation, carte de porteur) (**E**).

---

## QRM 4

Concernant l'anticoagulation et les prothèses, quelles sont les réponses exactes ?

- A. Les AVK ou les AOD peuvent être utilisés chez les sujets porteurs de prothèses valvulaires
- B. Le niveau d'anticoagulation efficace par AVK dépend du type de prothèse
- C. La surveillance de l'INR doit être hebdomadaire
- D. La surveillance de l'INR ne peut se faire qu'en laboratoire
- E. Les AOD peuvent être utilisés en cas de FA sur bioprothèse

**Réponse : B, E**

INR cible selon type de prothèse, position, FA, FEVG, etc. (**B**). AOD possibles si FA sur bioprothèse (**E**). AOD **contre-indiqués** sur prothèse mécanique (**A** faux). Surveillance INR mensuelle si stable ; automesure remboursée depuis 2017 (**C**, **D** faux).

---

## QRM 5

Quand suspecter une dysfonction de prothèse ?

- A. En cas d'apparition d'un souffle de régurgitation
- B. En cas de modification des signes fonctionnels à l'effort ou au repos
- C. En cas de modification de l'électrocardiogramme
- D. En cas de modification des paramètres échocardiographiques
- E. En cas d'AVC ischémique

**Réponse : A, B, D, E**

Souffle de régurgitation, signes fonctionnels, anomalies échographiques (gradient, fuite) et AVC ischémique (EI ou thrombose) orientent vers une dysfonction. L'ECG n'est **pas** un examen obligatoire de surveillance prothétique (**C** faux).

---

## QRM 6

Les prothèses valvulaires mécaniques :

- A. Peuvent être anticoagulées par les anticoagulants oraux directs
- B. Peuvent dégénérer
- C. Sont définitives (hors complication)
- D. Doivent faire prélever des hémocultures systématiques en cas de fièvre inexpliquée
- E. Doivent bénéficier d'une ETO en cas de suspicion de dysfonction ou de complication

**Réponse : C, D, E**

Prothèses mécaniques définitives, préférées chez le sujet jeune (**C**). AOD formellement contre-indiqués (**A** faux). Pas de dégénérescence tissulaire comme les bioprothèses (**B** faux). Fièvre inexpliquée → hémocultures systématiques avant antibiotiques (**D**). ETO si suspicion de dysfonction (**E**).
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
    if re.match(r"^(238|239|240|241|242|243|244|245|246|247|248|249|250|251|252|253|254|255|256|257|258|259|260)$", line):
        return None
    if re.match(r"^[A-G]$", line) and len(line) == 1:
        return None
    if line.startswith("El "):
        line = "• " + line[3:]
    line = line.replace("011 ", "• ")
    line = line.replace("1 53", "153")
    line = line.replace("1 52", "152")
    line = line.replace("1 €r", "1re")
    line = line.replace("Ve intention", "1re intention")
    line = line.replace("Item 1 53", "Item 153")
    line = line.replace("ptôthèse", "prothèse")
    line = line.replace("valve-in-valvë", "valve-in-valve")
    line = line.replace("Bjôrk", "Björk")
    line = line.replace("!NR", "INR")
    line = line.replace("INR0ble", "INR cible")
    line = line.replace("traitementjanticoagulant", "traitement anticoagulant")
    line = line.replace("1-2fois/semaine", "1–2 fois/semaine")
    line = line.replace("1 0 ans", "10 ans")
    line = line.replace("1 5 ans", "15 ans")
    line = line.replace("6e-1 2e", "6e–12e")
    line = line.replace("tableau 1 2", "tableau 10.2")
    line = line.replace("fig. 10.1 3", "fig. 10.13")
    line = line.replace("fig. 10.1 5", "fig. 10.15")
    line = line.replace("[ endocardite", "• endocardite")
    line = re.sub(r"^• 0 ", "• **Rang A.** ", line)
    line = re.sub(r"^II existe\b", "Il existe", line)
    for prefix, repl in (("• O ", "• **Rang A.** "), ("• □ ", "• **Rang B.** "), ("• Q ", "• **Rang A.** ")):
        if line.startswith(prefix):
            line = repl + line[len(prefix):]
            break
    for prefix, repl in (("□ ", "**Rang B.** "), ("O ", "**Rang A.** "), ("Q ", "**Rang A.** "), ("& ", "**Rang B.** "), ("D ", "**Rang B.** ")):
        if line.startswith(prefix):
            rest = line[len(prefix):]
            if rest and rest[0].islower():
                break
            line = repl + rest
            break
    return line


def match_section(cl):
    for sec, hdr in SECTION_MAP.items():
        if cl == sec or cl.startswith(sec):
            return hdr
    if cl.startswith("III. Complications"):
        return SECTION_MAP["III. Complications des prothèses valvulaires"]
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
            txt = cl.replace("Item 1 53", "Item 153").replace("Item 1 52", "Item 152")
            txt = txt.replace("Item 233", "Item 233").replace("Item 330", "Item 330")
            reflexes.append(txt if txt.startswith("•") else "• " + txt)
    return notions_ind, notions_inacc, reflexes


def extract_body():
    text = SRC.read_text(encoding="utf-8")
    stop_idx = text.find("===== PDF PAGE 292 =====")
    if stop_idx == -1:
        stop_idx = text.find("Item 238")
    chunk = text[:stop_idx] if stop_idx != -1 else text

    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False
    skip_flowchart = False
    table_mode = None
    table_10_1_done = False
    table_10_2_done = False
    table_10_3_done = False

    for line in chunk.splitlines():
        cl = clean_line(line)
        if cl is None:
            continue
        if skip_until_vignette:
            if cl.startswith("Vignette clinique") or cl.startswith("Un patient âgé"):
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
            in_points = True
            in_body = False
            continue
        hdr = match_section(cl)
        if hdr:
            lines_out.append(hdr)
            in_body = True
            in_points = False
            skip_flowchart = False
            table_mode = None
            continue
        if cl.startswith("Tableau 10.1"):
            if not table_10_1_done:
                lines_out.append(TABLE_10_1)
                table_10_1_done = True
            table_mode = "skip10.1"
            continue
        if cl.startswith("Tableau 10.2"):
            if not table_10_2_done:
                lines_out.append(TABLE_10_2)
                table_10_2_done = True
            table_mode = "skip10.2"
            continue
        if cl.startswith("Tableau 10.3"):
            if not table_10_3_done:
                lines_out.append(TABLE_10_3)
                table_10_3_done = True
            table_mode = "skip10.3"
            continue
        if table_mode == "skip10.1":
            if cl.startswith("ATCD :") or cl.startswith("Fig. 10.6") or cl.startswith("II. Physiopathologie"):
                table_mode = None
                if cl.startswith("II."):
                    lines_out.append(match_section(cl))
                elif cl.startswith("Fig. 10.6"):
                    skip_flowchart = True
                    lines_out.append(cl)
                else:
                    lines_out.append(cl)
            continue
        if table_mode == "skip10.2":
            if cl.startswith("Source :") or cl.startswith("Tableau 10.3") or cl.startswith("Maladies des valves"):
                continue
            if cl.startswith("B. Surveillance"):
                table_mode = None
                lines_out.append(f"\n## {cl}\n")
            continue
        if table_mode == "skip10.3":
            if cl.startswith("Source :") or cl.startswith("AAP :"):
                continue
            if cl.startswith("Maladies des valves") or cl.startswith("B. Surveillance"):
                table_mode = None
                if cl.startswith("B."):
                    lines_out.append(f"\n## {cl}\n")
            continue
        if skip_flowchart:
            fig_hit = any(k in cl for k in ("Fig. 10.6", "Fig. 10.13", "II. Physiopathologie", "2. Surveillance clinique"))
            if fig_hit:
                skip_flowchart = False
                if cl.startswith("Fig."):
                    pass
                elif cl.startswith("II.") or cl.startswith("2."):
                    if cl.startswith("II."):
                        lines_out.append(match_section(cl))
                    else:
                        lines_out.append(f"\n## {cl}\n")
                    continue
            else:
                continue
        if "Algorithme décisionnel" in cl and "fig. 10.6" in cl.lower():
            skip_flowchart = True
            lines_out.append(cl)
            continue
        if cl.startswith("Fig. 10.13") or (
            "Surveillance au long cours" in cl and "fig. 10.13" in cl.lower()
        ):
            skip_flowchart = True
        m = SUBSECTION_RE.match(cl)
        if m and in_body and not in_points and len(cl) < 120:
            lines_out.append(f"\n## {m.group(1)}\n")
            continue
        m2 = NUM_SUBSECTION_RE.match(cl)
        if m2 and in_body and not in_points and len(cl) < 120:
            lines_out.append(f"\n### {m2.group(1)}\n")
            continue
        fig_handled = False
        fig_m = re.match(r"^Fig\.\s*(10\.\d+)", cl, re.I)
        if fig_m:
            fig_key = f"Fig. {fig_m.group(1)}"
            if fig_key in FIG_MAP:
                fname, caption = FIG_MAP[fig_key]
                lines_out.append(f"\n![{caption}](./img/{fname})\n")
                cap = re.sub(r"^Fig\. 10\.\d+\.?\s*[0ODElQ©G]?\s*", "", cl)
                lines_out.append(f"\n**Fig. {fig_m.group(1)}.** {cap.lstrip('0123456789. ')}\n")
                fig_handled = True
        if fig_handled:
            continue
        if re.match(r"^\d+\.\s*doi:", cl, re.I) or re.match(r"^doi:10\.", cl, re.I):
            continue
        if cl == "•":
            continue
        if cl.startswith("Seule la partie concernant"):
            lines_out.append(f"> {cl}")
            continue
        if cl.startswith("- ") or cl.startswith("• "):
            lines_out.append(cl)
        elif cl.startswith("> "):
            lines_out.append(cl)
        elif cl.startswith(">"):
            lines_out.append("> " + cl[1:].strip())
        elif in_points and not cl.startswith("#"):
            lines_out.append(cl if cl.startswith("•") else "• " + cl)
        else:
            lines_out.append(cl)
    return "\n".join(lines_out)


def postprocess(text):
    text = re.sub(r">\s*\n+\s*", "> ", text)
    text = re.sub(r"\*\*Rang [AB]\.\*\*\s*\n+\*\*Rang [AB]\.\*\*", "**Rang A.**", text)
    text = re.sub(r"(# [^\n]+\n\n)\*\*Rang A\.\*\*\s*\n+\*\*Rang A\.\*\*", r"\1**Rang A.**", text)
    text = re.sub(r"(# [^\n]+\n\n)\*\*Rang B\.\*\*\s*\n+\*\*Rang B\.\*\*", r"\1**Rang B.**", text)
    fixes = [
        ("endocar- dite", "endocardite"), ("bio- logie", "biologie"), ("tho- racique", "thoracique"),
        ("écho- cardiographie", "échocardiographie"), ("cardio- logue", "cardiologue"),
        ("sympto- matique", "symptomatique"), ("anti- inflammatoire", "anti-inflammatoire"),
        ("trans- thoracique", "transthoracique"), ("trans- œsophagienne", "transœsophagienne"),
        ("hémody- namique", "hémodynamique"), ("cardio- pathie", "cardiopathie"),
        ("buccodo- dentaire", "buccodentaire"), ("rétrécisse- ment", "rétrécissement"),
        ("anti- agrégation", "antiagrégation"), ("endo- cardite", "endocardite"),
        ("thrombo- gènes", "thrombogènes"), ("totale- ment", "totalement"),
        ("endo- cardite infectieuse", "endocardite infectieuse"), ("(El)", "(EI)"), ("(El ", "(EI "),
        (" l'El ", " l'EI "), (" d'El ", " d'EI "), (" une El ", " une EI "), (" des El ", " des EI "),
        ("Item 1 53", "Item 153"), ("Item 1 52", "Item 152"), ("moyen>va|ves", "moyen : valves"),
        ("ifés aü", "liés au"), ("CB£ rentre", "doit entrer"), ("a ete", "a été"),
        ("dinical", "clinical"), ("artide", "article"), ("VaIve-in-valve", "Valve-in-valve"),
        ("oedème", "œdème"), ("transoesophagienne", "transœsophagienne"),
        ("II existe", "Il existe"), ("• 0 ", "• **Rang A.** "),
    ]
    for old, new in fixes:
        text = text.replace(old, new)
    text = re.sub(r"\s*===== PDF PAGE \d+ =====\s*", " ", text)
    text = re.sub(r"(?<=\w)-\s+(?=[a-zàâéèêëîïôùûü])", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\n-\s*\n\n", "\n\n• ", text)
    text = re.sub(r"\n-\s*\n", "\n• ", text)
    text = re.sub(r"Ce livre a été acheté.*?https://t\.me/Faille_V2\s*", " ", text, flags=re.S)
    text = re.sub(r"\n### \d+\.\s*doi:.*?\n", "\n", text)
    fig_10_1 = (
        "\n\n![Fig. 10.1 — Prothèses mécaniques (Starr®, Björk-Shiley®, St-Jude®)]"
        "(./img/fig_10_1_protheses_mecaniques.png)\n\n"
        "**Fig. 10.1.** Prothèses mécaniques : Starr® (bille), Björk-Shiley® (disque), St-Jude® (double ailette).\n"
    )
    if "fig_10_1_protheses_mecaniques.png" not in text:
        text = text.replace("(fig. 10.1).", "(fig. 10.1)." + fig_10_1, 1)
    fig_10_14 = (
        "\n\n![Fig. 10.14 — Carte d'intervention valvulaire](./img/fig_10_14_carte_intervention.png)\n\n"
        "**Fig. 10.14.** Carte d'intervention valvulaire et conseils pendant la durée du traitement anticoagulant.\n"
    )
    if "fig_10_14_carte_intervention.png" not in text:
        text = text.replace("(fig. 10.14)", "(fig. 10.14)" + fig_10_14, 1)
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
        if line.startswith(("#", "##", "###", "**", "-", "•", ">", "!", "|", "---", "![", "**Tableau")):
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

Questions isolées et corrigés : [Entrainement/QI/153_Surveillance_porteurs_valves_protheses.md](../../Entrainement/QI/153_Surveillance_porteurs_valves_protheses.md)
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
            if fig_num == "10.12" and len(hits) > 1:
                idx = 1
            elif fig_num == "10.14" and len(hits) > 1:
                idx = 1
            else:
                idx = 0
            r = hits[idx]
            tall = {"10.1", "10.6", "10.13", "10.14"}
            height = 480 if fig_num in tall else 400
            y1 = min(page.rect.height, r.y1 + height)
            clip = fitz.Rect(25, max(0, r.y0 - 15), page.rect.width - 25, y1)
        else:
            clip = page.rect
        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
        out = IMG_DIR / fname
        pix.save(str(out))
        print(f"Figure {fig_num} -> {out} ({out.stat().st_size} bytes)")
    doc.close()


def update_readme():
    text = README.read_text(encoding="utf-8")
    row = "| Fait | 153 Surveillance porteurs valves/prothèses | [II_Valves/153_Surveillance_porteurs_valves_protheses.md](./II_Valves/153_Surveillance_porteurs_valves_protheses.md) |\n"
    if "153 Surveillance" not in text:
        text = text.replace("| À faire | … | lots suivants |", row + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 153")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    sections = re.findall(r"^# [IVX]+\.", content, re.M)
    fig_count = len(list(IMG_DIR.glob("fig_10_*.png")))
    ok = size > 30_000 and len(sections) >= 4 and fig_count >= 15
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
