# -*- coding: utf-8 -*-
"""Generate item 236 troubles de conduction markdown + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item236.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Cours" / "III_Rythmologie" / "236_Troubles_conduction.md"
IMG_DIR = OUT.parent / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "236_Troubles_conduction.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^Rythmologie\s*$",
    r"^CHAPITRE\s*$",
    r"^14\s*$",
    r"^15\s*$",
    r"^Item 236\s*$",
    r"^Item 236 -.*",
    r"^Item 236 -Troubles.*",
    r"^Troubles de la conduction\s*$",
    r"^intracardiaque\s*$",
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
    r"^clés\s*$",
    r"^i H-H\s*$",
    r"^ilttB\s*$",
    r"^===== PDF PAGE \d+ =====$",
    r"^O QRM\s*\d+.*",
    r"^O QRU\s*\d+.*",
    r"^QRU\s*\d+.*",
    r"^QRM\s*\d+.*",
    r"^QQRM5.*",
    r"^Médecine cardiovasculaire\s*$",
    r"^Source : Glikson.*",
    r"^Guidelines on cardiac pacing.*",
    r"^Item 231\s*$",
    r"^Électrocardiogramme\s*$",
    r"^■w Item 236.*",
]

FLOW_GARBAGE = {
    "Nœud sinusal", "Faisceaux inter-", "nodaux", "Nœud", "atrioventriculaire",
    "Faisceaux de His", "Branche droite", "Faisceaux", "de Bachmann",
    "Branche gauche", "Hémibranche", "antérieure", "postérieure", "Réseau",
    "de Purkinje", "Bradycardie sinusale", "BSA 2e degré", "Pause sinusale",
    "BSA 3e degré permanent", "Pause sinusale", "post-réductionelle",
    "sinusale.", "BSA : bloc sinoatrial.", "QRS", "Onde P", "Jonction AV",
    "BAV 2e degré 2/1 Jonction AV", "BAV haut degré Jonction AV",
    "BAV 3e degré Jonction AV", "Nodal (QRS fins)", "Infranodal (QRS larges)",
    "BAV 3e degré", "et flutter atrial/FA", "Dysfonction sinusale", "BAV",
    "FA permanente", "Rythme sinusal", "FEVG", "<40 %", "normale",
    "Stimulateur double", "chambre", "Stimulateur", "simple", "chambre VVI",
    "biventriculaire", "double chambre",
    "Jîr", "S", "f!>",
}

SECTION_MAP = {
    "I. Définitions": "\n\n# I. Définitions\n\n**Rang B.**",
    "II. Dysfonction sinusale": "\n\n---\n\n# II. Dysfonction sinusale\n\n**Rang A** · **Rang B**.",
    "III. Blocs atrioventriculaires": "\n\n---\n\n# III. Blocs atrioventriculaires\n\n**Rang A** · **Rang B**.",
    "IV. Blocs de branche": "\n\n---\n\n# IV. Blocs de branche\n\n**Rang A** · **Rang B**.",
    "V. Thérapeutique et suivi du patient": "\n\n---\n\n# V. Thérapeutique et suivi du patient\n\n**Rang A** · **Rang B**.",
}

FIG_MAP = {
    "Fig. 14.1": ("fig_14_1_voies_conduction.png", "Fig. 14.1 — Voies de conduction intracardiaques"),
    "Fig. 14.2": ("fig_14_2_pause_bsa.png", "Fig. 14.2 — Pause sinusale et blocs sinoatriaux"),
    "Fig. 14.3": ("fig_14_3_degres_bsa.png", "Fig. 14.3 — Différents degrés de bloc sinoatrial (BSA)"),
    "Fig. 14.4": ("fig_14_4_torsade_bav.png", "Fig. 14.4 — Torsade de pointes sur BAV complet"),
    "Fig. 14.5": ("fig_14_5_degres_bav.png", "Fig. 14.5 — Degrés et manifestations ECG des BAV"),
    "Fig. 14.6": ("fig_14_6_types_pacemaker.png", "Fig. 14.6 — Principaux types de stimulateur endocavitaire"),
    "Fig. 14.7": ("fig_14_7_choix_pacemaker.png", "Fig. 14.7 — Type de stimulateur selon le trouble conductif"),
}

FIGURES = [
    ("14.1", "fig_14_1_voies_conduction.png", 343),
    ("14.2", "fig_14_2_pause_bsa.png", 346),
    ("14.3", "fig_14_3_degres_bsa.png", 347),
    ("14.4", "fig_14_4_torsade_bav.png", 349),
    ("14.5", "fig_14_5_degres_bav.png", 352),
    ("14.6", "fig_14_6_types_pacemaker.png", 358),
    ("14.7", "fig_14_7_choix_pacemaker.png", 361),
    ("14.8", "fig_14_8_qi_bav.png", 364),
    ("14.9", "fig_14_9_qi_bsa.png", 365),
]

SUBSECTION_RE = re.compile(r"^([A-E]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")

ENCADRE_14_1 = """
**Encadré 14.1 — Principales étiologies de la dysfonction sinusale**

**Causes extrinsèques**
- Prise médicamenteuse (bêtabloquant, inhibiteur calcique bradycardisant, amiodarone ou autre antiarythmique, ivabradine, digitalique, clonidine, etc.)
- Origine vagale : hypertonie vagale (athlète), réflexe vagal, hypersensibilité sinocarotidienne
- Atteinte du SNC : HIC, syndromes méningés
- Troubles hydroélectrolytiques (hyperkaliémie)
- Hypoxie, hypercapnie ou acidose sévères, SAOS
- Hypothermie, hypothyroïdie, ictère rétentionnel sévère

**Causes intrinsèques**
- Âge, vieillissement
- Maladie coronarienne chronique et aiguë
- Cardiomyopathies, myocardites, cardiopathies congénitales, tumeurs
- Maladies infiltratives (sarcoïdose, amylose, hémochromatose) ou systémiques
- Post-chirurgicales (valvulaire, CIA, transplantation)
- Troubles conductifs héréditaires, dystrophies neuromusculaires
"""

ENCADRE_14_2 = """
**Encadré 14.2 — Principales étiologies des blocs atrioventriculaires**

**Causes extrinsèques**
- Médicaments bradycardisants (bêtabloquant, inhibiteur calcique, amiodarone, digitalique)
- Hypertonie vagale (athlète) ou réflexe vagal
- Troubles hydroélectrolytiques (hyperkaliémie)

**Causes intrinsèques**
- Âge : dégénérescence fibreuse ± calcifications (maladie de Lenègre)
- Maladie coronarienne chronique
- IDM : nodal dans l'infarctus inférieur (souvent régressif) ; hissien/infrahissien dans l'infarctus antérieur (mauvais pronostic)
- RA calcifié dégénératif ; TAVI, chirurgie valvulaire
- Infectieuses : endocardite (abcès d'anneau), Lyme, myocardites virales
- Infiltratives (sarcoïdose, amylose), radique, BAV congénital, héréditaire
"""

TABLE_14_1 = """
**Tableau 14.1.** Classification des blocs atrioventriculaires (BAV).

| Degré | Siège | QRS | Symptômes |
|---|---|---|---|
| **BAV 1er degré** | Généralement nodal (exceptionnellement intrahissien) | Fins sauf BB associé | Non (sauf PR très long) |
| **BAV 2e degré Mobitz 1** | Toujours nodal | Fins sauf BB associé | ± |
| **BAV 2e degré Mobitz 2** | Toujours hissien ou infrahissien | Fins (intrahissien) ou plus souvent larges | ± |
| **BAV de haut degré** | Hissien ou infrahissien (rarement nodal) | Larges ; fins si nodal/intrahissien | Oui |
| **BAV 3e degré (complet)** | Nodal, hissien ou infrahissien | Fins si nodal/intrahissien ; larges si infrahissien | Oui |

BB : bloc de branche.
"""

TABLE_14_2 = """
**Tableau 14.2.** Indications de stimulation cardiaque définitive (ESC 2021) — résumé.

**Maladie du nœud sinusal**

| Recommandation | Classe | Niveau |
|---|---|---|
| Indiquée si symptômes clairement attribuables à la bradycardie | I | B |
| Peut être proposée si symptômes probablement liés, sans preuve définitive | IIb | C |
| Indiquée dans le syndrome brady-tachy symptomatique | I | B |
| À considérer si insuffisance chronotrope et symptômes d'effort | IIa | B |
| Non indiquée si asymptomatique ou cause réversible | III | C |

**Blocs atrioventriculaires**

| Recommandation | Classe | Niveau |
|---|---|---|
| Indiquée : BAV Mobitz 2, 3e degré, infranodal 2/1 ou haut degré, rythme sinusal, ± symptômes | I | C |
| Indiquée : FA + BAV 3e degré ou haut degré, ± symptômes | I | C |
| Recommandée : bloc de branche alternant ± symptômes | I | C |
| Recommandée : Mobitz 1 symptomatique ou intra/infrahissien à l'EEP | IIa | C |
| À envisager : syndrome du pacemaker, BAV 1er degré PR > 300 ms | IIa | C |
| Non recommandée si cause réversible | III | C |

**Syncope et troubles conductifs**

| Recommandation | Classe | Niveau |
|---|---|---|
| Recommandée si syncope récurrente sévère > 40 ans et pauses > 6 s (ou > 3 s symptomatiques), sinus carotidien, asystolie au tilt-test | I | A |
| Recommandée si syncope et HV > 70 ms ou BAV 2e/3e intra/infrahissien à l'EEP | I | B |
| Peut être proposée d'emblée si syncope inexpliquée + bloc bifasciculaire à haut risque de chute | IIb | B |
| Non recommandée si BBD/bifasciculaire asymptomatique | III | B |
"""

POINTS_BLOCK = """
• **Rang A.** Les troubles de la conduction appartiennent à trois cadres nosologiques : la dysfonction sinusale, les blocs atrioventriculaires et les blocs de branche.

• Les troubles de conduction peuvent être des marqueurs de la présence d'une cardiopathie, qui doit être recherchée.

• Une bradycardie prolongée s'accompagne d'un rythme d'échappement situé en aval de la zone lésée : NAV en cas de dysfonction sinusale, faisceau de His en cas de BAV nodal, etc.

• Plus la lésion est distale dans le tissu de conduction, plus le rythme d'échappement est instable et lent, et donc plus le tableau est grave.

• Le diagnostic ECG est obligatoire :
  - dysfonction sinusale : pas d'onde P bloquée ;
  - BAV : classification en trois degrés ; le 2e degré en plusieurs types ; le bloc 2/1 est inclassable en Mobitz 1 ou 2. La largeur du QRS et la fréquence de l'échappement indiquent le siège du bloc en cas de BAV complet.

• L'hémibloc antérieur gauche est fréquent, l'hémibloc postérieur gauche est plus rare et potentiellement plus grave.

• Causes aiguës à rechercher : SCA ST+, médicaments, hyperkaliémie. Les causes neurovégétatives (vagales) sont bénignes. Cause chronique la plus fréquente : dégénérescence fibreuse liée à l'âge.

• Examens de référence : holter pour la dysfonction sinusale ; EEP pour les blocs infrahissiens/hissiens (syncope + bloc de branche).

• Bradycardie mal tolérée si : angor, IC, hypotension, choc, syncope, bas débit neurologique, torsade de pointes.

• Hospitalisation urgente : BAV 3, Mobitz 2, haut degré, blocs alternants, BSA 3, syncopes avec troubles conductifs ECG. Un BAV complet est toujours plus grave qu'une dysfonction sinusale.

• Traiter la cause : infarctus, arrêt d'un bradycardisant, correction d'une hyperkaliémie. En urgence : atropine, isoprénaline, ou stimulation temporaire.

• Stimulateur si dysfonction sinusale **symptomatique** sans cause réversible ; BAV Mobitz 2, 3e degré ou haut degré sans cause curable.
"""

HEADER = '''# Item 236 — Troubles de la conduction intracardiaque

> **Collège CNEC / SFC** · 3e édition (2025) · p. 312–336 · R2C  
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
21 Asthénie.  
27 Chute de la personne âgée.  
28 Coma et troubles de conscience.  
38 État de mort apparente.  
43 Découverte d'une hypotension artérielle.  
50 Malaise/perte de connaissance.  
64 Vertige et sensation vertigineuse.  
159 Bradycardie.  
161 Douleur thoracique.  
162 Dyspnée.  
178 Demande/prescription raisonnée et choix d'un examen diagnostique.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
201 Dyskaliémie.  
204 Élévation des enzymes cardiaques.  
285 Consultation de suivi et éducation thérapeutique d'un patient avec un antécédent cardiovasculaire.  
327 Annonce d'un diagnostic de maladie grave au patient et/ou à sa famille.  
328 Annonce d'une maladie chronique.  
334 Demande de traitement et investigation inappropriés.  
352 Expliquer un traitement au patient (adulte/enfant/adolescent).  
355 Organisation de la sortie d'hospitalisation.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Physiopathologie | Dysfonction sinusale, BAV, bloc de branche | Anatomie, vascularisation, caractéristiques tissulaires |
| **A** | Diagnostic positif | Évoquer dysfonction sinusale ou trouble de conduction | Symptômes, contextes et formes cliniques |
| **B** | Étiologies | Principales étiologies | Ionique, médicaments, infarctus, dégénératif, valvulopathies |
| **A** | Examens complémentaires | Examens de 1re intention | Enquête étiologique |
| **A** | Identifier une urgence | Mauvaise tolérance d'une bradycardie | Sémiologie, hyperkaliémie, SCA |
| **A** | Prise en charge | Médicaments tachycardisants et urgence | Atropine, isoprénaline, stimulation temporaire |
| **A** | Prise en charge | Indications de stimulateur définitif | Dysfonction sinusale, BAV, blocs de branche |

---

## Parcours Rang A

- [II. Dysfonction sinusale](#ii-dysfonction-sinusale)
- [III. Blocs atrioventriculaires](#iii-blocs-atrioventriculaires)
- [IV. Blocs de branche](#iv-blocs-de-branche)
- [V. Thérapeutique et suivi du patient](#v-thérapeutique-et-suivi-du-patient)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Définitions](#i-définitions)
- [II. Dysfonction sinusale](#ii-dysfonction-sinusale)
- [III. Blocs atrioventriculaires](#iii-blocs-atrioventriculaires)
- [IV. Blocs de branche](#iv-blocs-de-branche)
- [V. Thérapeutique et suivi du patient](#v-thérapeutique-et-suivi-du-patient)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/236_Troubles_conduction.md)

---

'''

QI_CONTENT = '''# Entraînement — Item 236 Troubles de la conduction intracardiaque

> Collège CNEC 3e éd. · Chapitre 14 · corrigés p. 584  
> Cours : [236 Troubles de la conduction](../../Cours/III_Rythmologie/236_Troubles_conduction.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRU 1

Un homme de 81 ans se présente au SAU à la suite d'un malaise sans perte de connaissance. Il décrit également une dyspnée sans douleur thoracique. Il est traité au long cours par amiodarone et apixaban pour une arythmie cardiaque. L'infirmière vous apporte l'ECG suivant (fig. 14.8). Parmi les propositions suivantes, quelle proposition est juste ?

![Fig. 14.8 — ECG du patient](../../Cours/III_Rythmologie/img/fig_14_8_qi_bav.png)

- A. Il s'agit d'un BAV du 2e degré Mobitz 1
- B. Il s'agit d'un BAV du 2e degré Mobitz 2
- C. Il s'agit d'un BAV 2/1
- D. Il s'agit d'un BAV du 3e degré
- E. Il s'agit d'extrasystoles atriales bloquées

**Réponse : D**

Dissociation complète atrioventriculaire (pseudo-espaces PR variables, QRS réguliers) = **BAV du 3e degré**. L'activité atriale est régulière.

---

## QRM 2

Concernant les investigations à faire en urgence, quelles propositions sont justes ?

- A. Il faut doser les D-dimères en urgence
- B. Il faut doser la troponine en urgence
- C. Il faut faire un ionogramme sanguin en urgence
- D. Il faut faire une échographie cardiaque
- E. Il faut faire une coronarographie en urgence

**Réponse : B, C, D**

Devant un BAV 3 : éliminer une cause secondaire (ischémie → troponine, hyperkaliémie → ionogramme). L'ETT recherche une cardiopathie et évalue la FEVG (en pratique après transfert en cardiologie). Les D-dimères n'ont pas d'intérêt (**A** faux). Pas de coronarographie en urgence sans douleur thoracique évocatrice d'IDM ni sus-décalage ST (**E** faux).

---

## QRM 3

La pression artérielle est à 105/65 mmHg. Le patient est conscient et bien orienté. Le bilan biologique est normal, ainsi que l'échographie cardiaque. Quels traitements mettez-vous en place en urgence ?

- A. Accélération de la fréquence cardiaque par isoprénaline en perfusion continue
- B. Accélération de la fréquence cardiaque par atropine en perfusion continue
- C. Mise en place d'une sonde d'entraînement externe
- D. Scope ECG
- E. Suspension de l'apixaban

**Réponse : A, D, E**

BAV relativement bien toléré : isoprotérénol en perfusion continue, scope, arrêt de l'anticoagulant en vue du stimulateur. L'atropine a une demi-vie courte et n'est **pas** utilisée en perfusion continue (**B** faux). Pas de sonde d'entraînement d'emblée si bonne tolérance (geste à risque) (**C** faux).

---

## QRU 4

Aucune cause n'est retrouvée, vous concluez à un BAV dégénératif du sujet âgé. Quel traitement proposez-vous ?

- A. Mise en place d'un stimulateur définitif simple chambre AAI
- B. Mise en place d'un stimulateur définitif simple chambre VVI
- C. Mise en place d'un stimulateur définitif double chambre DDD
- D. Mise en place d'un stimulateur définitif triple chambre
- E. Mise en place d'un défibrillateur définitif double chambre

**Réponse : C**

Indication de stimulateur **double chambre** (synchronisation ventriculaire à la fréquence sinusale). VVI plutôt si FA permanente ; AAI réservé à la dysfonction sinusale pure (souvent remplacé par DDD). Pas de triple chambre si FEVG normale, pas de DAI pour un BAV isolé.

---

## QRM 5

Le patient vous demande les précautions à prendre après la pose du stimulateur et la surveillance du dispositif. Quelles propositions sont justes ?

- A. Un suivi au moins annuel est recommandé
- B. Un suivi par télésurveillance est possible
- C. Les IRM sont contre-indiquées
- D. Un écoulement au niveau de la cicatrice ne doit pas l'inquiéter
- E. Il faut qu'il porte son carnet ou sa carte indiquant les caractéristiques du stimulateur en permanence sur lui

**Réponse : A, B, E**

L'IRM n'est pas contre-indiquée : circuit dédié, programmation « mode IRM » puis reprogrammation (**C** faux). Un écoulement ou une rougeur de cicatrice doit faire consulter (infection de matériel) (**D** faux).

---

## QRM 6

Une patiente de 71 ans, traitée par bisoprolol 10 mg pour une hypertension artérielle, se présente aux urgences pour asthénie. L'ECG est le suivant (fig. 14.9). Quelles propositions sont justes ?

![Fig. 14.9 — ECG de la patiente](../../Cours/III_Rythmologie/img/fig_14_9_qi_bsa.png)

- A. Il s'agit d'une bradycardie sinusale
- B. Il s'agit d'un BAV du 3e degré
- C. Il s'agit d'un bloc sinoatrial du 3e degré
- D. Il faut arrêter le bisoprolol
- E. Il faut implanter un stimulateur cardiaque définitif d'emblée

**Réponse : C, D**

BSA du 3e degré : pas d'ondes P visibles, échappement à QRS fins. Arrêter le bisoprolol et le remplacer par un antihypertenseur non bradycardisant. Stimulateur seulement si pas d'amélioration à l'arrêt du bêtabloquant (**E** faux).
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
    if re.match(r"^(312|313|314|315|316|317|318|319|320|321|322|323|324|325|326|327|328|329|330|331|332|333|334|335|336)$", line):
        return None
    if re.match(r"^[A-G]$", line) and len(line) == 1:
        return None
    line = line.replace("Item 236 -Troubles", "Item 236 - Troubles")
    line = line.replace("1 2D", "12D")
    line = line.replace("2 e degré", "2e degré")
    line = line.replace("3 e degré", "3e degré")
    line = line.replace("1 er degré", "1er degré")
    line = line.replace("< 1 20", "< 120")
    line = line.replace("OUn bloc", "Un bloc")
    line = line.replace("Wl", "VVI")
    line = line.replace("nodal(>", "nodal (>")
    line = line.replace("fig. 14>§", "fig. 14.5")
    line = line.replace("• 0 ", "• **Rang A.** ")
    line = line.replace("• 13 ", "• ")
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
    return None


def extract_footer(text):
    notions_ind, notions_inacc, reflexes = [], [], []
    mode = None
    for raw in text.splitlines():
        raw_s = raw.strip()
        if raw_s.startswith("► Entraînement") or raw_s.startswith("O QRU") or raw_s.startswith("Item 231"):
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


def insert_fig(lines_out, key):
    fname, caption = FIG_MAP[key]
    num = key.replace("Fig. ", "")
    lines_out.append(f"\n![{caption}](./img/{fname})\n")
    lines_out.append(f"\n**{key}.** {caption.split('—', 1)[-1].strip()}\n")


def extract_body():
    text = SRC.read_text(encoding="utf-8")
    stop = text.find("► Entraînement")
    chunk = text[:stop] if stop != -1 else text

    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False
    pending_bullet = None
    skip_mode = None
    enc1 = enc2 = tab1 = tab2 = False
    fig2_done = False

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

        if skip_mode == "anatomy":
            if cl.startswith("B. Sur le plan"):
                skip_mode = None
            else:
                continue
        if skip_mode == "enc1":
            if cl.startswith("3. Diagnostic") or cl.startswith("### 3"):
                skip_mode = None
            else:
                continue
        if skip_mode == "enc2":
            if cl.startswith("3. Diagnostic") or "Du fait de sa faible" in cl:
                skip_mode = None
            else:
                continue
        if skip_mode == "tab1":
            if cl.startswith("•") or cl.startswith("Le diagnostic"):
                skip_mode = None
            else:
                continue
        if skip_mode == "tab2":
            if cl.startswith("•") or cl.startswith("En cas de dysfonction"):
                skip_mode = None
            else:
                continue
        if skip_mode == "fig5":
            if cl.startswith("4. Quelques") or cl.startswith("BAV dégénératif"):
                skip_mode = None
            else:
                continue
        if skip_mode == "fig7":
            if cl.startswith("D. Traitement") or cl.startswith("BAV :"):
                skip_mode = None
            else:
                continue

        hdr = match_section(cl)
        if hdr:
            lines_out.append(hdr)
            in_body = True
            continue

        if cl.startswith("Encadré 14.1"):
            if not enc1:
                lines_out.append(ENCADRE_14_1)
                enc1 = True
            skip_mode = "enc1"
            continue
        if cl.startswith("Encadré 14.2"):
            if not enc2:
                lines_out.append(ENCADRE_14_2)
                enc2 = True
            skip_mode = "enc2"
            continue
        if cl.startswith("Tableau 14.1"):
            if not tab1:
                lines_out.append(TABLE_14_1)
                tab1 = True
            skip_mode = "tab1"
            continue
        if cl.startswith("Tableau 14.2"):
            if not tab2:
                lines_out.append(TABLE_14_2)
                tab2 = True
            skip_mode = "tab2"
            continue

        if cl.startswith("Fig. 14.1"):
            insert_fig(lines_out, "Fig. 14.1")
            skip_mode = "anatomy"
            continue
        if cl.startswith("Fig. 14.3"):
            insert_fig(lines_out, "Fig. 14.3")
            continue
        if cl.startswith("Fig. 14.4"):
            insert_fig(lines_out, "Fig. 14.4")
            continue
        if cl.startswith("Fig. 14.5"):
            insert_fig(lines_out, "Fig. 14.5")
            skip_mode = "fig5"
            continue
        if cl.startswith("Fig. 14.6"):
            insert_fig(lines_out, "Fig. 14.6")
            continue
        if cl.startswith("Fig. 14.7"):
            insert_fig(lines_out, "Fig. 14.7")
            skip_mode = "fig7"
            continue

        if "fig. 14.2" in cl.lower() and not fig2_done:
            lines_out.append(cl)
            insert_fig(lines_out, "Fig. 14.2")
            fig2_done = True
            continue

        m = SUBSECTION_RE.match(cl)
        if m and in_body and len(cl) < 140:
            lines_out.append(f"\n## {m.group(1)}\n")
            continue
        m2 = NUM_SUBSECTION_RE.match(cl)
        if m2 and in_body and len(cl) < 120:
            lines_out.append(f"\n### {m2.group(1)}\n")
            continue
        if cl.startswith("Pause ou arrêt sinusal"):
            lines_out.append(f"\n### {cl}\n")
            continue
        if cl.startswith("Bloc sinoatrial"):
            lines_out.append(f"\n### {cl}\n")
            continue
        if cl.startswith("BAV dégénératif") or cl.startswith("BAV complet sur infarctus"):
            lines_out.append(f"\n### {cl}\n")
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
    fixes = [
        ("**Rang A.** II faut", "**Rang A.** Il faut"),
        ("O II faut", "**Rang A.** Il faut"),
        ("noeud sinusal", "nœud sinusal"),
        ("en cas angor", "en cas d'angor"),
        ("simple chambre VVI", "simple chambre VVI"),
        ("stimulateur simple chambre VVI", "stimulateur simple chambre VVI"),
    ]
    for old, new in fixes:
        text = text.replace(old, new)
    text = re.sub(r"Pour avoir plus d'exclusivités.*?Faille_V2\s*", " ", text)
    text = re.sub(r"Ce livre a été acheté.*?Faille_V2\s*", " ", text, flags=re.S)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(
        r"(> Quel examen proposez-vous immédiatement \? Quelles sont les hypothèses diagnostiques les plus)\n\n(probables)",
        r"\1 \2",
        text,
    )
    text = re.sub(
        r"(> S'agit-il d'une situation d'urgence \? Faut-il hospitaliser le patient \? Quel peut-être le risque)\n\n(immédiat)",
        r"\1 \2",
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
    ind = (
        "• Ne pas oublier l'ECG.\n"
        "• Pour les blocs de branche : ne pas s'attarder sur les blocs incomplets de faible valeur clinique, considérer les blocs complets.\n"
        "• Association fréquente de la dysfonction sinusale à la FA dans le cadre de la maladie rythmique atriale."
    )
    inacc = (
        "• Oublier de rechercher une cause curable devant un trouble de conduction.\n"
        "• Ne pas rechercher de cardiopathie sous-jacente devant la découverte d'un BBG.\n"
        "• Méconnaître la conduite à tenir en urgence devant une bradycardie et les troubles conductifs à risque vital."
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

Questions isolées et corrigés : [Entrainement/QI/236_Troubles_conduction.md](../../Entrainement/QI/236_Troubles_conduction.md)
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
    for fig_num, fname, page_idx in FIGURES:
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
            y0 = max(0, r.y0 - 320)
            y1 = min(page.rect.height, r.y1 + 28)
            clip = fitz.Rect(18, y0, page.rect.width - 18, y1)
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
    row = "| Fait | 236 Troubles de la conduction | [III_Rythmologie/236_Troubles_conduction.md](./III_Rythmologie/236_Troubles_conduction.md) |\n"
    if "236 Troubles" not in text:
        text = text.replace("| À faire | … | lots suivants |", row + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 236")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    sections = re.findall(r"^# [IVX]+\.", content, re.M)
    fig_count = len(list(IMG_DIR.glob("fig_14_*.png")))
    print(f"Course size: {size} bytes, section headers: {len(sections)} ({sections})")
    print(f"Figures: {fig_count} PNGs")
    if size < 25_000 or len(sections) < 5:
        print("WARN: verification thresholds not met")


def main():
    build_course()
    build_qi()
    extract_figures()
    update_readme()
    verify()


if __name__ == "__main__":
    main()
