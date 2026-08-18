# -*- coding: utf-8 -*-
"""Generate item 152 endocardite infectieuse markdown + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item152.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Cours" / "II_Valves" / "152_Endocardite_infectieuse.md"
IMG_DIR = OUT.parent / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "152_Endocardite_infectieuse.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Maladies des valves\s*$",
    r"^Item 152\s*$",
    r"^Item 152 - Endocardite infectieuse\s*$",
    r"^Item 1 52.*Endocardite infectieuse\s*$",
    r"^Endocardite infectieuse\s*$",
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
    r"^Vidéo 9\.\d+.*",
    r"^10\s*$",
    r"^9\s*$",
    r"^[\d\s\.ÏHWMflBï\.]+$",
]

FLOWCHART_GARBAGE = {
    "Situation à risque", "Bactériémie/fongémie", "Cardiopathie à risque", "v ____",
    "Végétations", "Inflammation", "systémique", "Abcès", "Désinsertion", "de prothèse",
    "Destruction", "valvulaire", "BAV", "I - Embolies systémiques", "(El cœur gauche)",
    "- Embolies pulmonaires", "(El cœur droit)", "Cl 53Hz", "0 5cm", "v>", "69%", "C 50",
    "P Bas", "Ger", "123bpm", "S» 1002", "lm:1", "m.", "RJH", "PHI", "2.85", "' 0", "HR",
    "228", "rétrécissement mitral", "Fédération", "Cardiologie",
    "Cette carie doit être systématiquement montrée à votre médecin et/ou votre dentiste",
    "Votre cardiopathie NE nécessite PAS d'antibiotique à visée préventive",
    "en cas de soin dentaire",
    "MAIS les mesures suivantes d'hygiène cutanée et bucco-dentaire sont indispensables",
    "Pour une prévention efficace",
    "- brossez-vous les dents 2 à 3 fois/ jour",
    "- consultez votre dentiste 2 fois par an",
    "En cas de fièvre (avec ou sans soin dentaire préalable) :",
    "■ prévenez systématiquement votre médecin",
    "- présentez-lui cette carte",
    "- ne prenez pas d'antibiotiques sans son avis et/ou avant la recherche",
    "de germes dans le sang par une hémoculture",
    "Nom, prénom :", "Remis parle Dr :",
}

SECTION_MAP = {
    "I. Définition": "\n\n# I. Définition\n\n**Rang A.**",
    "II. Épidémiologie": "\n\n---\n\n# II. Épidémiologie\n\n**Rang A.**",
    "III. Micro-organismes en cause": "\n\n---\n\n# III. Micro-organismes en cause\n\n**Rang A.**",
    "IV. Physiopathologie": "\n\n---\n\n# IV. Physiopathologie\n\n**Rang A** · **Rang B**.",
    "V. Prise en charge multidisciplinaire": "\n\n---\n\n# V. Prise en charge multidisciplinaire\n\n**Rang B.**",
    "VI. Diagnostic": "\n\n---\n\n# VI. Diagnostic\n\n**Rang A** · **Rang B**.",
    "VII. Complications et pronostic": "\n\n---\n\n# VII. Complications et pronostic\n\n**Rang A** · **Rang B**.",
    "VIII. Traitement": "\n\n---\n\n# VIII. Traitement\n\n**Rang A** · **Rang B**.",
    "IX. Prévention": "\n\n---\n\n# IX. Prévention\n\n**Rang A** · **Rang B**.",
}

FIG_MAP = {
    "Fig. 9.1": ("fig_9_1_mecanisme_ei.png", "Fig. 9.1 — Séquence physiopathologique de l'EI et complications"),
    "Fig. 9.2": ("fig_9_2_vegetation_eto.png", "Fig. 9.2 — Végétation volumineuse en échographie transœsophagienne"),
    "Fig. 9.3": ("fig_9_3_scanner_abcès.png", "Fig. 9.3 — Abcès paraprothétique au scanner cardiaque"),
    "Fig. 9.4": ("fig_9_4_tep_prothese.png", "Fig. 9.4 — Hyperfixation TEP-FDG sur prothèse mécanique aortique"),
    "Fig. 9.5": ("fig_9_5_angiographie_mycotique.png", "Fig. 9.5 — Anévrisme infectieux (mycotique)"),
    "Fig. 9.6": ("fig_9_6_ei_coeur_droit.png", "Fig. 9.6 — EI du cœur droit : végétation tricuspidienne et embolies pulmonaires"),
    "Fig. 9.7": ("fig_9_7_cartes_prevention.png", "Fig. 9.7 — Cartes de prévention de l'EI"),
}

FIGURES = [
    ("9.1", "fig_9_1_mecanisme_ei.png", 251),
    ("9.2", "fig_9_2_vegetation_eto.png", 254),
    ("9.3", "fig_9_3_scanner_abcès.png", 255),
    ("9.4", "fig_9_4_tep_prothese.png", 256),
    ("9.5", "fig_9_5_angiographie_mycotique.png", 256),
    ("9.6", "fig_9_6_ei_coeur_droit.png", 257),
    ("9.7", "fig_9_7_cartes_prevention.png", 261),
]

SUBSECTION_RE = re.compile(r"^([A-G]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")
ENCADRE_RE = re.compile(r"^Encadré 9\.\d")

TABLE_9_1 = """
**Tableau 9.1.** Micro-organismes le plus souvent en cause dans l'endocardite infectieuse avec leurs portes d'entrée potentielles.

| Micro-organisme (germe) | Fréquence (%) | Porte d'entrée |
|---|---|---|
| *Staphylococcus aureus* | 30 | Cutanée (plaies, cathéter veineux, cathéter de dialyse, toxicomanie IV, peropératoire, stimulateur/défibrillateur implantables, etc.) |
| Streptocoques oraux (*S. sanguis*, *S. mitis*, *S. salivarius*, *S. mutans*) | 20 | Buccodentaire |
| Streptocoques du groupe D (*S. gallolyticus* ou bovis) | 13 | Digestive (cancer, polypes, diverticules coliques) |
| Staphylocoques coagulase négative (*S. epidermidis*, *S. lugdunensis*, etc.) | 10 | Cutanée (plaies, cathéter veineux, cathéter de dialyse, toxicomanie IV, peropératoire, stimulateur/défibrillateur implantables, etc.) |
| Entérocoques (*E. faecalis*, *E. faecium*) | 10 | Digestive (cancer, polypes, diverticules coliques) ; urinaire |
| Bactéries du groupe HACEK | 5 | Buccodentaire |
| *Candida* et autres champignons | < 5 | Cutanée (immunosuppression, cathéter veineux, cathéter de dialyse, toxicomanie IV, peropératoire, stimulateur/défibrillateur implantables, etc.) |
| Autres (*Coxiella burnetii*, *Bartonella*, *Brucella*, *Chlamydia*, *Tropheryma whipplei*, etc.) | < 5 | Spécifique à chaque germe |
| Non retrouvé par différentes techniques | 5–10 | — |

HACEK : *Haemophilus* spp., *Aggregatibacter actinomycetemcomitans*, *Cardiobacterium hominis*, *Eikenella corrodens*, *Kingella kingae* ; IV : intraveineux.
"""

TABLE_9_2 = """
**Tableau 9.2.** Résumé de l'antibiothérapie IV des principales endocardites infectieuses.

| Micro-organisme en cause | Absence d'allergie à la pénicilline | Allergie à la pénicilline |
|---|---|---|
| Non identifié (probabiliste), EI communautaire sur valve native ou prothèse > 1 an | Ampicilline + ceftriaxone (ou oxacilline) + gentamicine | Céfazoline ou vancomycine + gentamicine |
| Non identifié (probabiliste), EI non communautaire ou prothèse < 1 an | Vancomycine (ou daptomycine) + gentamicine + rifampicine | Idem |
| Staphylocoques méthicilline-sensibles, valve native | Cloxacilline (ou céfazoline) 4 à 6 semaines | Céfazoline 4 à 6 semaines |
| Staphylocoques méthicilline-sensibles, prothèse | Cloxacilline (ou céfazoline) + rifampicine 6 semaines + gentamicine 2 semaines | Céfazoline + rifampicine 6 semaines + gentamicine 2 semaines |
| Staphylocoques méthicilline-résistants, valve native | Vancomycine 4–6 semaines | Idem |
| Staphylocoques méthicilline-résistants, prothèse | Vancomycine + rifampicine 6 semaines + gentamicine 2 semaines | Idem |
| Streptocoques oraux et *Streptococcus gallolyticus*, valve native | Pénicilline G (ou amoxicilline ou ceftriaxone) 4 semaines (+ gentamicine 2 semaines si résistance à la pénicilline) | Vancomycine 4 semaines |
| Streptocoques oraux et *Streptococcus gallolyticus*, prothèse | Pénicilline G (ou amoxicilline ou ceftriaxone) 6 semaines | Vancomycine 6 semaines + gentamicine 2 semaines |
| Entérocoques, valve native | Amoxicilline (ou ampicilline) + ceftriaxone 6 semaines (ou remplacer ceftriaxone par gentamicine 2 semaines) | Vancomycine 6 semaines + gentamicine 2 semaines |
| Entérocoques, prothèse | Amoxicilline (ou ampicilline) + ceftriaxone 6 semaines (ou remplacer ceftriaxone par gentamicine 2 semaines) | Vancomycine 6 semaines + gentamicine 2 semaines |
| Entérocoques résistants à la gentamicine, valve native ou prothèse | Amoxicilline (ou ampicilline) + ceftriaxone 6 semaines | Vancomycine 6 semaines + gentamicine 2 semaines |
| Entérocoques résistants aux bêtalactamines, valve native ou prothèse | Vancomycine 6 semaines + gentamicine 2 semaines | Idem |
| Entérocoques résistants à la vancomycine, valve native ou prothèse | Daptomycine + ampicilline (ou fosfomycine) 6 semaines | Daptomycine + fosfomycine 6 semaines |

Le détail des doses est disponible dans les recommandations européennes ESC 2023.
"""

HEADER = '''# Item 152 — Endocardite infectieuse

> **Collège CNEC / SFC** · 3e édition (2025) · p. 218–236 · R2C  
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

20 Découverte d'anomalies à l'auscultation pulmonaire.  
21 Asthénie.  
44 Hyperthermie/fièvre.  
50 Malaise/perte de connaissance.  
54 Œdème localisé ou diffus.  
58 Splénomégalie.  
89 Purpura/ecchymose/hématome.  
102 Hématurie.  
121 Déficit neurologique sensitif et/ou moteur.  
160 Détresse respiratoire aiguë.  
161 Douleur thoracique.  
162 Dyspnée.  
165 Palpitations.  
166 Tachycardie.  
186 Syndrome inflammatoire aigu ou chronique.  
187 Bactérie multirésistante à l'antibiogramme.  
203 Élévation de la protéine C-réactive (CRP).  
217 Baisse de l'hémoglobine.  
228 Découverte d'une anomalie osseuse et articulaire à l'examen d'imagerie médicale.  
232 Demande d'explication d'un patient sur le déroulement, les risques et les bénéfices attendus d'un examen d'imagerie.  
238 Demande et préparation aux examens endoscopiques (bronchiques, digestifs).  
239 Explication préopératoire et recueil de consentement d'un geste invasif diagnostique ou thérapeutique.  
248 Prescription et suivi d'un traitement par anticoagulant et/ou antiagrégant.  
253 Prescrire des diurétiques.  
255 Prescrire un anti-infectieux.  
271 Prescription et surveillance d'une voie d'abord vasculaire.  
285 Consultation de suivi éducation thérapeutique d'un patient avec antécédents cardiovasculaires.  
311 Prévention des infections liées aux soins.  
320 Prévention des maladies cardiovasculaires.  
352 Expliquer un traitement au patient (adulte/enfance/adolescent).  
354 Évaluation de l'observance thérapeutique.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | Définition d'une endocardite infectieuse | |
| **A** | Épidémiologie | Épidémiologie de l'EI | |
| **A** | Épidémiologie | Situations à risque d'EI (cardiopathie groupe A, matériel intracardiaque, bactériémie à cocci Gram+) | |
| **A** | Étiologies | Principaux agents infectieux (bactéries, levures) | |
| **A** | Physiopathologie | Portes d'entrée selon l'agent infectieux | |
| **B** | Physiopathologie | Cardiopathies à risque d'EI du groupe B | |
| **A** | Diagnostic positif | Signes cliniques évocateurs | |
| **A** | Diagnostic positif | Démarche initiale du diagnostic microbiologique | |
| **B** | Diagnostic positif | Démarche si hémocultures initiales négatives | |
| **A** | Diagnostic positif | Démarche initiale de l'échocardiographie | |
| **B** | Diagnostic positif | Arguments échocardiographiques | |
| **A** | Examens complémentaires | Hiérarchisation des examens selon l'état clinique | |
| **B** | Examens complémentaires | Principales localisations emboliques | |
| **A** | Identifier une urgence | Antibiothérapie probabiliste | |
| **B** | Prise en charge | Prise en charge multidisciplinaire (équipe endocardite) | |
| **A** | Prise en charge | Principes du traitement antibiotique | |
| **A** | Prise en charge | Posologie des antibiothérapies | |
| **A** | Prise en charge | Antibiothérapie ambulatoire et voie orale | |
| **B** | Prise en charge | Prise en charge de la porte d'entrée | |
| **A** | Prise en charge | Éducation à la santé après un épisode d'EI | |
| **A** | Prise en charge | Principes de l'antibioprophylaxie | |
| **B** | Prise en charge | Posologies d'antibioprophylaxie si allergie à la pénicilline | |
| **A** | Prise en charge | Principales complications | Cardiaques, emboliques, infectieuses |
| **A** | Prise en charge | Délai de la prise en charge chirurgicale | |

---

## Parcours Rang A

- [I. Définition](#i-définition)
- [III. Micro-organismes en cause](#iii-micro-organismes-en-cause)
- [VI. Diagnostic](#vi-diagnostic)
- [VIII. Traitement](#viii-traitement)
- [IX. Prévention](#ix-prévention)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Définition](#i-définition)
- [II. Épidémiologie](#ii-épidémiologie)
- [III. Micro-organismes en cause](#iii-micro-organismes-en-cause)
- [IV. Physiopathologie](#iv-physiopathologie)
- [V. Prise en charge multidisciplinaire](#v-prise-en-charge-multidisciplinaire)
- [VI. Diagnostic](#vi-diagnostic)
- [VII. Complications et pronostic](#vii-complications-et-pronostic)
- [VIII. Traitement](#viii-traitement)
- [IX. Prévention](#ix-prévention)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/152_Endocardite_infectieuse.md)

---

'''

QI_CONTENT = '''# Entraînement — Item 152 Endocardite infectieuse

> Collège CNEC 3e éd. · Chapitre 9 · corrigés p. 581  
> Cours : [152 Endocardite infectieuse](../../Cours/II_Valves/152_Endocardite_infectieuse.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRM 1

Quelles sont les cardiopathies considérées à haut risque d'endocardite infectieuse ?

- A. Bicuspidie aortique
- B. Prolapsus valvulaire mitral
- C. Antécédent d'endocardite infectieuse
- D. Prothèse valvulaire
- E. Cardiopathie congénitale cyanogène non corrigée

**Réponse : C, D, E**

Haut risque : antécédent d'EI, prothèse valvulaire (chirurgicale ou percutanée), cardiopathie congénitale cyanogène non corrigée ou réparée avec matériel prothétique (< 6 mois ou shunt résiduel). Bicuspidie aortique et PVM relèvent du **risque intermédiaire** (**A**, **B** faux).

---

## QRM 2

Quelles sont les causes possibles d'endocardites à hémocultures négatives ?

- A. Hémocultures prélevées avant la mise sous antibiotiques
- B. Endocardite à *Coxiella burnetii* (agent de la fièvre Q)
- C. Endocardite liée à un lupus ou un syndrome des anticorps antiphospholipides
- D. Endocardite à champignons
- E. Aucune de ces réponses

**Réponse : B, C, D, E**

Hémocultures négatives : germes à croissance lente/difficile (HACEK, champignons), germes intracellulaires (*Coxiella*, *Bartonella*, etc.), endocardites **non infectieuses** (lupus, SAPL, cancers). **A** faux : les antibiotiques avant prélèvement faussent les cultures mais ne constituent pas une « cause » d'EI à HC négatives au sens de l'item. **E** faux car B, C et D sont exactes.

---

## QRM 3

Concernant l'imagerie cardiaque lors d'une endocardite infectieuse, quelles sont les réponses exactes ?

- A. Le TEP-scanner est l'examen de référence
- B. L'échocardiographie transœsophagienne peut être normale
- C. L'échocardiographie doit être répétée lors de la surveillance du traitement
- D. Le scanner cardiaque peut mettre en évidence un abcès
- E. L'échocardiographie transœsophagienne est systématique en cas de prothèse valvulaire

**Réponse : B, C, D, E**

Le TEP-FDG n'est pas l'examen de référence ; il est utile surtout si doute persistant sur prothèse ou matériel (**A** faux). L'ETO peut être normale au début ; elle doit être répétée en surveillance (**B**, **C**). Scanner cardiaque : abcès, végétations non vues à l'écho (**D**). ETO systématique si prothèse ou matériel intracardiaque (**E**).

---

## QRM 4

Concernant le traitement antibiotique des endocardites infectieuses, quelles sont les réponses exactes ?

- A. Dans certains cas, il peut durer moins d'une semaine
- B. En cas d'endocardite à *Enterococcus faecalis*, une association amoxicilline + ceftriaxone peut être proposée
- C. La gentamicine a une toxicité rénale
- D. L'amoxicilline a une toxicité rénale
- E. En cas de prothèse valvulaire implantée depuis moins d'un an, la suspicion d'endocardite doit faire prescrire une association vancomycine + gentamicine + rifampicine en attendant le résultat des hémocultures

**Réponse : B, C, D, E**

Durée habituelle 4–6 semaines IV ; pas < 1 semaine (**A** faux). Entérocoques : amoxicilline + ceftriaxone (**B**). Toxicité rénale des aminosides (**C**) et de l'amoxicilline (cristallurie, réactions immuno-allergiques) (**D**). Prothèse < 1 an : probabiliste large vancomycine + gentamicine + rifampicine (**E**).

---

## QRM 5

Concernant la prévention des endocardites infectieuses, quelles sont les réponses exactes ?

- A. Elle est indiquée pour toutes les cardiopathies à risque
- B. Les piercings peuvent constituer une porte d'entrée infectieuse
- C. Une perfusion peut constituer une porte d'entrée infectieuse
- D. Une antibioprophylaxie est indiquée en cas de coloscopie chez un patient porteur de prothèse
- E. Une antibioprophylaxie est indiquée en cas de soins dentaires touchant la gencive et la région périapicale chez un patient porteur d'un prolapsus valvulaire mitral avec fuite sévère

**Réponse : B, C**

Éducation non spécifique pour **toutes** les cardiopathies à risque ; antibioprophylaxie seulement pour le **haut risque** devant soins dentaires avec effraction muqueuse (**A** faux : confond mesures générales et antibioprophylaxie). Piercings et perfusions IV = portes d'entrée cutanées (**B**, **C**). Coloscopie : pas d'antibioprophylaxie systématique (**D** faux). PVM avec fuite = risque intermédiaire, pas d'antibioprophylaxie (**E** faux).
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
    if re.match(r"^(218|219|220|221|222|223|224|225|226|227|228|229|230|231|232|233|234|235|236)$", line):
        return None
    if re.match(r"^[A-E]$", line):
        return None
    if line.startswith("El "):
        line = "• " + line[3:]
    line = line.replace("011 ", "• ")
    line = line.replace("1 52", "152")
    line = line.replace("1 53", "153")
    line = line.replace("1 €r", "1re")
    line = line.replace("Ve intention", "1re intention")
    line = line.replace("Douléùr", "Douleur")
    line = line.replace("66 Tachycardie", "166 Tachycardie")
    line = line.replace("Item 1 52", "Item 152")
    line = line.replace("dindamycine", "clindamycine")
    line = line.replace("Stæptococcus", "Streptococcus")
    line = line.replace("5. ", "S. ")
    line = line.replace("enterococcus", "Enterococcus")
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


def match_section(cl):
    for sec, hdr in SECTION_MAP.items():
        if cl == sec or cl.startswith(sec):
            return hdr
    cl_norm = re.sub(r"^VIL\b", "VII", cl)
    for sec, hdr in SECTION_MAP.items():
        if cl_norm == sec or cl_norm.startswith(sec):
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
            txt = cl.replace("Item 1 52", "Item 152").replace("Item 1 53", "Item 153")
            txt = txt.replace("Item 1 51", "Item 151").replace("Item 1 56", "Item 156")
            txt = txt.replace("Item 1 57", "Item 157").replace("Item 1 58", "Item 158")
            reflexes.append(txt if txt.startswith("•") else "• " + txt)
    return notions_ind, notions_inacc, reflexes


def extract_body():
    text = SRC.read_text(encoding="utf-8")
    stop_idx = text.find("===== PDF PAGE 268 =====")
    if stop_idx == -1:
        stop_idx = text.find("Item 153")
    chunk = text[:stop_idx] if stop_idx != -1 else text

    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False
    skip_flowchart = False
    table_mode = None
    table_9_2_done = False
    in_encadre_91 = False

    for line in chunk.splitlines():
        cl = clean_line(line)
        if cl is None:
            continue
        if skip_until_vignette:
            if cl.startswith("Vignette clinique") or cl.startswith("Monsieur H"):
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
        if ENCADRE_RE.match(cl):
            in_encadre_91 = cl.startswith("Encadré 9.1")
            lines_out.append(f"\n### {cl}\n")
            continue
        if in_encadre_91 and cl.startswith("Les lésions infectieuses endocardiques"):
            in_encadre_91 = False
            lines_out.append(cl)
            continue
        if in_encadre_91 and cl.startswith("-") and "végétations" in cl:
            in_encadre_91 = False
        if cl.startswith("Tableau 9.1"):
            lines_out.append(TABLE_9_1)
            table_mode = "skip9.1"
            continue
        if cl.startswith("Tableau 9.2"):
            if table_9_2_done:
                table_mode = "skip9.2"
                continue
            lines_out.append(TABLE_9_2)
            table_9_2_done = True
            table_mode = "skip9.2"
            continue
        if table_mode == "skip9.1":
            if cl.startswith("HACEK :") or cl.startswith("IV. Physiopathologie"):
                table_mode = None
                if cl.startswith("IV."):
                    lines_out.append(match_section(cl))
                else:
                    lines_out.append(cl)
            continue
        if table_mode == "skip9.2":
            if cl.startswith("Le détail de l'antibiothérapie") or cl.startswith("• O La durée"):
                table_mode = None
                if cl.startswith("• O La durée"):
                    lines_out.append(cl)
            continue
        if cl.startswith("Tableaux cliniques évoquant"):
            lines_out.append(f"\n**{cl}**\n")
            continue
        if skip_flowchart:
            if any(k in cl for k in ("Encadré 9.1", "Fig. 9.1", "Les lésions infectieuses")):
                skip_flowchart = False
            else:
                continue
        if cl.startswith("La séquence du mécanisme général") and "figure 9.1" in cl.lower():
            skip_flowchart = True
            lines_out.append(cl)
            continue
        m = SUBSECTION_RE.match(cl)
        if m and in_body and not in_points and len(cl) < 100:
            lines_out.append(f"\n## {m.group(1)}\n")
            continue
        m2 = NUM_SUBSECTION_RE.match(cl)
        if m2 and in_body and not in_points and len(cl) < 100:
            lines_out.append(f"\n### {m2.group(1)}\n")
            continue
        fig_handled = False
        for fig_key, (fname, caption) in FIG_MAP.items():
            if fig_key.lower() in cl.lower() and cl.lower().startswith("fig."):
                lines_out.append(f"\n![{caption}](./img/{fname})\n")
                cap = re.sub(r"^Fig\. 9\.\d+\.?\s*[0-9ODElQ©G]?\s*", "", cl)
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
            lines_out.append(cl if cl.startswith("•") else "• " + cl)
        else:
            lines_out.append(cl)
    return "\n".join(lines_out)


def postprocess(text):
    text = re.sub(r">\s*\n+\s*", "> ", text)
    text = re.sub(r"\*\*Rang [AB]\.\*\*\s*\n+\*\*Rang [AB]\.\*\*", "**Rang A.**", text)
    text = re.sub(r"(# [^\n]+\n\n)\*\*Rang A\.\*\*\s*\n+\*\*Rang A\.\*\*", r"\1**Rang A.**", text)
    text = re.sub(r"(# [^\n]+\n\n)\*\*Rang B\.\*\*\s*\n+\*\*Rang B\.\*\*", r"\1**Rang B.**", text)
    ei_fixes = [
        ("• du cœur", "EI du cœur"), ("des • ", "des EI "), ("l'• ", "l'EI "),
        ("d'• ", "d'EI "), ("une • ", "une EI "), ("Certaines • ", "Certaines EI "),
        ("des • aortiques", "des EI aortiques"), ("traitement des • ", "traitement des EI "),
        ("(El)", "(EI)"), ("(El ", "(EI "), (" l'El ", " l'EI "), (" d'El ", " d'EI "),
        (" une El ", " une EI "), (" des El ", " des EI "), (" l'El.", " l'EI."),
    ]
    for old, new in ei_fixes:
        text = text.replace(old, new)
    fixes = [
        ("endocar- dite", "endocardite"), ("bio- logie", "biologie"), ("tho- racique", "thoracique"),
        ("écho- cardiographie", "échocardiographie"), ("cardio- logue", "cardiologue"),
        ("sympto- matique", "symptomatique"), ("anti- inflammatoire", "anti-inflammatoire"),
        ("trans- thoracique", "transthoracique"), ("trans- œsophagienne", "transœsophagienne"),
        ("sigmoï- des", "sigmoïdes"), ("hémody- namique", "hémodynamique"),
        ("cardio- pathie", "cardiopathie"), ("buccodo- dentaire", "buccodentaire"),
        ("220 j", ""), ("Item 1 52", "Item 152"), ("Item 1 53", "Item 153"),
        ("{polymerase chain reaction [PCR]}", "(polymerase chain reaction [PCR])"),
        ("OQ Groupes", "**Rang A.** Groupes"), ("O O Principales", "**Rang A.** Principales"),
        ("® _______________________________", ""),
        ("c\n- les prothèses", "- les prothèses"),
        ("amoxicilline ou clindamycine", "amoxicilline ou clindamycine"),
    ]
    for old, new in fixes:
        text = text.replace(old, new)
    text = re.sub(r"\s*===== PDF PAGE \d+ =====\s*", " ", text)
    text = re.sub(r"(?<=\w)-\s+(?=[a-zàâéèêëîïôùûü])", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Close encadré 9.1 before physiopathology continuation
    text = re.sub(
        r"(6 premiers mois suivant l'implantation)\. Les lésions infectieuses",
        r"\1.\n\n---\n\nLes lésions infectieuses",
        text,
    )
    text = re.sub(r"\n-\s*\n\n", "\n\n• ", text)
    text = re.sub(r"\n-\s*\n", "\n• ", text)
    # Remove duplicate Tableau 9.2 block if OCR triggered twice
    dup = re.search(
        r"(\*\*Tableau 9\.2\.\*\*.*?(?=\n\nLe détail des doses))",
        text,
        re.S,
    )
    if dup:
        block = dup.group(1)
        if text.count(block.strip()) > 1:
            text = text.replace(block.strip() + "\n\n" + block.strip(), block.strip(), 1)
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

Questions isolées et corrigés : [Entrainement/QI/152_Endocardite_infectieuse.md](../../Entrainement/QI/152_Endocardite_infectieuse.md)
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
            height = 450 if fig_num in ("9.1", "9.6", "9.7") else 380
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
    row = "| Fait | 152 Endocardite infectieuse | [II_Valves/152_Endocardite_infectieuse.md](./II_Valves/152_Endocardite_infectieuse.md) |\n"
    if "152 Endocardite infectieuse" not in text:
        text = text.replace("| À faire | … | lots suivants |", row + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 152")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    sections = re.findall(r"^# [IVX]+\.", content, re.M)
    ok = size > 25_000 and len(sections) >= 9
    print(f"Course size: {size} bytes, section headers: {len(sections)} ({sections})")
    print(f"Figures: {len(list(IMG_DIR.glob('fig_9_*.png')))} PNGs")
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
