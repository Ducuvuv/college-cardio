# -*- coding: utf-8 -*-
"""Generate item 226 TVP et embolie pulmonaire markdown + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item226.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Cours" / "V_MTEV" / "226_TVP_embolie_pulmonaire.md"
IMG_DIR = OUT.parent / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "226_TVP_embolie_pulmonaire.md"
README = ROOT / "Cours" / "README.md"

WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"Pour avoir plus d’exclusivités.*",
    r"© 2025 Elsevier.*",
    r"Connaissances\s*$",
    r"^CHAPITRE\s*$",
    r"^CHAPITf\s*$",
    r"^19\s*$",
    r"^20\s*$",
    r"^v Item 226\s*$",
    r"^Item 226\s*$",
    r"^Item 226 -.*",
    r"^Thrombose veineuse\s*$",
    r"^profonde et embolie\s*$",
    r"^pulmonaire\s*$",
    r"^Maladie thromboembolique veineuse\s*$",
    r"^Maladie\s*$",
    r"^thromboembolique\s*$",
    r"^veineuse\s*$",
    r"^Situations de départ\s*$",
    r"^Hiérarchisation des connaissances\s*$",
    r"^Rang Rubrique\s*$",
    r"^Intitulé\s*$",
    r"^Descriptif\s*$",
    r"^Rang\s*$",
    r"^Rubrique\s*$",
    r"^Variable\s*$",
    r"^Points\s*$",
    r"^► Entraînement.*",
    r"^Les corrigés sont.*",
    r"^Pour en savoir plus\s*$",
    r"^Entraînement\s*$",
    r"^► Compléments.*",
    r"^Des compléments numériques.*",
    r"^par des flashcodes.*",
    r"^consulte\.com.*",
    r"^clés\s*$",
    r"^===== PDF PAGE \d+ =====$",
    r"^O QRM\s*\d+.*",
    r"^0 QRM\s*\d+.*",
    r"^G QRM\s*\d+.*",
    r"^GQRM.*",
    r"^QQRU.*",
    r"^QRM\s*\d+.*",
    r"^QRU\s*\d+.*",
    r"^Médecine cardiovasculaire\s*$",
    r"^à l'entraînement de l'intelligence artificielle.*",
    r"^!St strictement interdite.*",
    r"^: sur https://t\.me/Faille_V2\s*$",
    r"^Faille_V2\s*$",
    r"^Item 235\s*$",
    r"^Péricardite aiguë\s*$",
    r"^Divers\s*$",
    r"^VI\s*$",
    r"^V\s*$",
    r"^I «7\s*$",
    r"^f 489\s*$",
    r"^HBPM : héparine.*",
    r"^sPESI : simplified.*",
    r"^llsic : unité.*",
    r"^Source : Konstantinides.*",
    r"^Group\. 2019 ESC Guidelines.*",
    r"^collaboration with the European.*",
    r"^Score de Genève :.*",
    r"^Geneva score\..*",
    r"^Score de Wells simplifié :.*",
    r"^embolism\. Thromb Haemost.*",
    r"^Source : Wells PS.*",
    r"^doi:10\.1016/s0140-6736.*",
    r"^Source : Sanchez O.*",
    r"^en charge de la maladie veineuse.*",
    r"^1\. La durée optimale proposée peut être raccourcie à 3 mois.*",
    r"^2\. La durée optimale proposée peut être raccourcie à 6 mois.*",
    r"^3\. Dans cette situation, la durée de traitement est modulable.*",
    r"^4\. Valable pour l'édoxaban.*",
    r"^AOD : anticoagulant oral direct.*",
    r"^des antiphospholipides.*",
    r"^Score HERDOO2 :.*",
    r"^de thrombose veineuse, D-dimères.*",
    r"^2, âge > 65 ans\)\.\s*$",
    r"^EP : embolie pulmonaire; Ml :.*",
    r"^ATCD : antécédent.*",
    r"^Facteurs prédisposants\s*$",
    r"^Signes cliniques\s*$",
    r"^Symptômes\s*$",
    r"^Interprétation\s*$",
    r"^Probabilité clinique \(3 niveaux\)\s*$",
    r"^Probabilité clinique \(2 niveaux\)\s*$",
    r"^Total\s*$",
    r"^Faible <10%\s*$",
    r"^Intermédiaire 30-40 %\s*$",
    r"^Forte > 60 %\s*$",
    r"^Probable\s*$",
    r"^Peu probable\s*$",
    r"^Score révisé de Genève\s*$",
    r"^Score de Wells\s*$",
]

PAGE_NUM_RE = re.compile(
    r"^(463|464|465|466|467|468|469|470|471|472|473|474|475|476|477|478|"
    r"479|480|481|482|483|484|485|486|487|488|489|490|491|492|493|494|"
    r"495|496)\s*[j|]?\s*$"
)

FLOW_GARBAGE = {
    "Échodoppler veineux systématique",
    "Dans les 24-48 heures",
    "Ou si possible en urgence",
    "Pas de TVP",
    "Probabilité clinique forte",
    "Probabilité clinique faible",
    "ou intermédiaire",
    "Traitement anticoagulant",
    "curatif et contention",
    "Surveillance clinique",
    "± Traitement anticoagulant",
    "curatif et contention",
    "± Échodoppler à 48 heures",
    "Diagnostic de TVP éliminé",
    "Recherche du diagnostic",
    "différentiel",
    "EP suspectée à haut risque",
    "EP suspectée non à haut risque",
    "Sans choc ou hypotension",
    "Score de probabilité clinique EP",
    "Wells ou Genève révisé",
    "EP « probable »",
    "EP «non probable»",
    "EP « non probable »",
    "D-dimères",
    "Pas de traitement Scanner multicoupe",
    "Pas de traitement",
    "Scanner multicoupe",
    "Scanner",
    "Négatif",
    "Positif",
    "Oui",
    "Non",
    "Chercher une",
    "autre cause",
    "Thrombolyse/",
    "embolectomie",
    "non justifiées",
    "Traitement spécifique",
    "EP justifié",
    "Thrombolyse ou",
    "embolectomie",
    "Scanner disponible",
    "Et patient stable",
    "Pas d’autres examens disponibles",
    "Ou patient instable",
    "RISQUE",
    "INTERMÉDIAIRE",
    "EP confirmée",
    "Troponine",
    "Négative",
    "Positive et VD+",
    "INTERMÉDIAIRE HAUT",
    "INTERMÉDIAIRE FAIBLE",
    "FAIBLE",
    "HAUT",
    "Reperfusion",
    "Réanimation/",
    "Usic",
    "Anticoagulant",
    "Réanimation/Usic",
    "Surveillance, envisager",
    "reperfusion si détérioration",
    "Hospitalisation en",
    "médecine",
    "Hospitalisation",
    "courte ou",
    "ambulatoire",
    "Score sPESI",
    "sPESI =",
    "sPESI >1 ou VD+",
    "Suspicion d’EP",
    "Suspicion d'EP",
    "Choc/hypotension",
    "Qui",
    "Algorithme",
    "diagnostique",
    "EP confirmée",
    "etVD-",
    "et VD-",
}

SECTION_MAP = {
    "I. Définitions": "\n\n# I. Définitions\n\n**Rang A.**",
    "II. Épidémiologie": "\n\n---\n\n# II. Épidémiologie\n\n**Rang A.**",
    "III. Facteurs prédisposants": (
        "\n\n---\n\n# III. Facteurs prédisposants\n\n**Rang A.**"
    ),
    "IV. Physiopathologie": "\n\n---\n\n# IV. Physiopathologie\n\n**Rang A** · **Rang B.**",
    "V. Histoire naturelle": "\n\n---\n\n# V. Histoire naturelle\n\n**Rang A.**",
    "VI. Thrombose veineuse profonde": (
        "\n\n---\n\n# VI. Thrombose veineuse profonde\n\n**Rang A** · **Rang B.**"
    ),
    "VII. Embolie pulmonaire": (
        "\n\n---\n\n# VII. Embolie pulmonaire\n\n**Rang A** · **Rang B.**"
    ),
    "VIII. Traitement curatif": (
        "\n\n---\n\n# VIII. Traitement curatif\n\n**Rang A** · **Rang B.**"
    ),
    "IX. Traitement préventif": (
        "\n\n---\n\n# IX. Traitement préventif\n\n**Rang A.**"
    ),
}

FIG_MAP = {
    "Fig. 19.1": (
        "fig_19_1_algo_tvp.png",
        "Fig. 19.1 — Stratégies diagnostiques devant une suspicion de TVP",
    ),
    "Fig. 19.2": (
        "fig_19_2_algo_ep_haut_risque.png",
        "Fig. 19.2 — Algorithme décisionnel pour une EP suspectée à haut risque",
    ),
    "Fig. 19.3": (
        "fig_19_3_algo_ep_non_haut_risque.png",
        "Fig. 19.3 — Algorithme décisionnel pour une EP suspectée non à haut risque",
    ),
    "Fig. 19.4": (
        "fig_19_4_algo_pec_ep.png",
        "Fig. 19.4 — Algorithme de prise en charge de l'embolie pulmonaire",
    ),
}

FIGURES = [
    ("19.1", "fig_19_1_algo_tvp.png", 499, 530),
    ("19.2", "fig_19_2_algo_ep_haut_risque.png", 507, 360),
    ("19.3", "fig_19_3_algo_ep_non_haut_risque.png", 507, 330),
    ("19.4", "fig_19_4_algo_pec_ep.png", 510, 360),
]

SUBSECTION_RE = re.compile(r"^([A-I]\.\s+[A-ZÉÈÀÔÎÂÙÛÇŒ«].+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s+[A-ZÉÈÀÔÎÂÙÛÇŒ«].+)$")

ENCADRE_19_1 = """
**Encadré 19.1 — Principaux facteurs prédisposants de MTEV**

**Facteurs temporaires majeurs**
- Chirurgie avec anesthésie générale > 30 minutes dans les 3 derniers mois
- Fracture des membres inférieurs dans les 3 derniers mois
- Immobilisation > 3 jours pour motif médical aigu dans les 3 derniers mois
- Contraception œstroprogestative, grossesse, post-partum, traitement hormonal de la ménopause

**Facteurs temporaires mineurs**
- Chirurgie avec anesthésie générale < 30 minutes dans les 2 derniers mois
- Traumatisme d'un membre inférieur non plâtré avec mobilité réduite > 3 jours
- Immobilisation < 3 jours pour motif médical aigu dans les 2 derniers mois
- Voyage > 6 heures

**Facteurs permanents**
- Cancer actif
- Maladies inflammatoires chroniques digestives ou articulaires (Crohn, rectocolite hémorragique)
"""

TABLE_19_1 = """
**Tableau 19.1.** Score de Wells simplifié — probabilité clinique de TVP.

| Variable | Points |
|---|---|
| Parésie, paralysie ou immobilisation plâtrée récente d'un MI | 1 |
| Chirurgie récente < 4 semaines ou alitement récent > 3 jours | 1 |
| Cancer évolutif connu (traitement en cours ou < 6 mois ou palliatif) | 1 |
| Antécédent de TVP (ou d'EP) | 1 |
| Sensibilité le long du trajet veineux profond | 1 |
| Œdème généralisé du MI | 1 |
| Œdème du mollet > 3 cm vs controlatéral (10 cm sous la TTA) | 1 |
| Œdème unilatéral prenant le godet | 1 |
| Circulation collatérale superficielle non variqueuse | 1 |
| Diagnostic différentiel au moins aussi probable que la TVP | −2 |

Interprétation en 3 niveaux : **faible** (0), **intermédiaire** (1 ou 2), **forte** (≥ 3).
"""

TABLE_19_2 = """
**Tableau 19.2.** Scores de probabilité clinique d'EP : Genève révisé et Wells simplifié.

| Score révisé de Genève | Pts | Score de Wells simplifié | Pts |
|---|---|---|---|
| Âge > 65 ans | 1 | ATCD de TVP ou d'EP | 1 |
| ATCD de TVP ou d'EP | 1 | Chirurgie ou immobilisation < 4 semaines | 1 |
| Chirurgie récente ou fracture dans le mois | 1 | Néoplasie active | 1 |
| Cancer actif | 1 | Hémoptysie | 1 |
| Hémoptysie | 1 | FC > 100 bpm | 1 |
| Douleur unilatérale du MI | 1 | Signes cliniques de TVP | 1 |
| FC 75–94 bpm | 1 | Diagnostic différentiel peu probable | 1 |
| FC ≥ 95 bpm | 2 | | |
| Douleur à la palpation du MI (trajet veineux) et œdème unilatéral | 1 | | |

**Genève (3 niveaux)** : faible 0–1 (~10 %) · intermédiaire 2–4 (~30–40 %) · forte ≥ 5 (~60 %).  
**Genève (2 niveaux)** : peu probable 0–2 · probable ≥ 3.  
**Wells simplifié (2 niveaux)** : peu probable 0–1 · probable ≥ 2.
"""

TABLE_19_3 = """
**Tableau 19.3.** Durée du traitement anticoagulant dans la MTEV (d'après SPLF 2019).

| Risque de récidive | Situation | Durée | Molécules |
|---|---|---|---|
| **Faible** | MTEV provoquée par un facteur transitoire **majeur** (chirurgie AG > 30 min / 3 mois, fracture MI / 3 mois, COP–grossesse–post-partum–THM oral) | **3 mois** | AVK (INR 2–3) ou AOD pleine dose |
| **Faible** | Femme, 1er épisode non provoqué par un facteur transitoire majeur et HERDOO2 < 1, ou femme < 50 ans | **3–6 mois** | AVK ou AOD pleine dose |
| **Modéré** | Homme, 1er épisode non provoqué sans facteur persistant majeur ; femme, 1er épisode non provoqué, HERDOO2 ≥ 2 | **6 mois ou non limitée** | AVK ou AOD pleine dose (après 6 mois : même molécules) |
| **Élevé** | Cancer actif | **Non limitée** | 6 premiers mois : HBPM (AOD si intolérance) ; ensuite HBPM, AVK ou AOD |
| **Élevé** | SAPL | **Non limitée** | AVK (INR 2–3) |
| **Élevé** | MTEV récidivante non provoquée ; 1er épisode + thrombophilie sévère (déficit en AT) ; 1re EP à haut risque non provoquée ; HTP-TEC | **Non limitée** | AVK (INR 2–3) et/ou AOD selon le contexte |

Score **HERDOO2** (récidive chez la femme) : signes de TVP, D-dimères > 250 µg/L, IMC > 30 kg/m², âge > 65 ans.  
La durée peut être raccourcie (3 ou 6 mois) si le risque hémorragique est élevé.
"""

POINTS_BLOCK = """
### Thrombose veineuse profonde

• La triade de Virchow (stase veineuse, lésion pariétale, anomalie de l'hémostase) explique la formation du thrombus.

• Le point de départ est le plus souvent distal ; le thrombus peut s'étendre, s'occlure ou migrer vers le poumon. Une lyse spontanée est possible si le thrombus est peu volumineux et si le facteur étiologique disparaît.

• Les TVP distales, souvent asymptomatiques, sont rarement responsables d'une EP cliniquement importante, mais environ 25 % s'étendent en proximal. La récidive d'une TVP distale est deux fois moins fréquente que celle d'une TVP proximale.

• Une TVP proximale est symptomatique dans 80 % des cas et s'associe fréquemment à une EP. Sans anticoagulant, une TVP proximale symptomatique récidive une fois sur deux dans les 3 mois.

• Le diagnostic clinique seul est insuffisant : score de Wells, D-dimères (si probabilité faible/intermédiaire), échodoppler veineux.

• Traitement : HBPM (sauf IR sévère) avec relais AVK dès J1 (chevauchement ≥ 5 jours et 2 INR efficaces) **ou** AOD anti-Xa d'emblée (rivaroxaban, apixaban). Durée 3 mois si facteur transitoire majeur, 6 mois si non provoquée, illimitée si facteur persistant majeur ou récidive.

• Contention classe 3 dès l'anticoagulation, pendant 2 ans. Lever précoce. Filtre cave si contre-indication à l'anticoagulation.

### Embolie pulmonaire

• L'EP est le plus souvent (70 %) secondaire à une TVP. Près de 10 % des EP sont mortelles dans l'heure. Choc dans 5–10 % des cas ; dysfonction VD une fois sur deux.

• Devant une dyspnée, une douleur thoracique ou une syncope : évoquer l'EP. Scores de Genève / Wells. Algorithme selon choc/hypotension (haut risque) ou non.

• Angioscanner : examen de confirmation. Scintigraphie V/Q, échodoppler veineux et ETT selon le contexte. D-dimères inutiles si probabilité clinique **forte**.

• Stratification : haut risque (choc/hypotension) → USIC + fibrinolyse ; intermédiaire haut (sPESI ≥ 1 et ≥ 2 signes de souffrance VD) → USIC + anticoagulant ; intermédiaire faible → hospitalisation + anticoagulant ; bas risque (sPESI = 0) → anticoagulant, séjour court ou ambulatoire.

• HBPM + AVK ou AOD anti-Xa. HNF si IR sévère, instabilité, fibrinolyse. HBPM prolongée si cancer. Durée 3 mois si facteur réversible, > 3 mois si non provoquée, illimitée si récidive ou thrombophilie.
"""

HEADER = '''# Item 226 — Thrombose veineuse profonde et embolie pulmonaire

> **Collège CNEC / SFC** · 3e édition (2025) · p. 463–496 · R2C  
> Partie V — Maladie thromboembolique veineuse

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

160 Détresse respiratoire aiguë.  
161 Douleur thoracique.  
162 Dyspnée.  
257 Œdèmes des membres inférieurs localisés ou généralisés.  
350 Grosse jambe rouge aiguë.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Définition | TVP / EP | TVP proximale vs distale ; EP ; EP à haut risque |
| **A** | Étiologie | Facteurs de MTEV | Circonstances, facteurs temporaires et persistants |
| **B** | Physiopathologie | MTEV | Triade de Virchow, formes familiales |
| **A** | Diagnostic positif | Stratégie MTEV | Clinique, scores, paraclinique, diagnostics différentiels |
| **A** | Identifier une urgence | EP à haut risque | Choc / hypotension : démarche diagnostique |
| **A** | Diagnostic positif | D-dimères | Indications TVP/EP ; seuil ajusté à l'âge dans l'EP |
| **A** | Examens complémentaires | Échodoppler veineux | Place et limites (TVP, EP) |
| **A** | Examens complémentaires | Imagerie de l'EP | Angio-TDM, scintigraphie V/Q, ETT |
| **A** | Prise en charge | Gravité / ambulatoire | Signes de gravité ; patients éligibles à une PEC ambulatoire |
| **A** | Prise en charge | Traitement initial | Principes du traitement d'une TVP/EP non grave |
| **A** | Prise en charge | Compression élastique | Indications et contre-indications (TVP des MI) |
| **A** | Prise en charge | Contraception | Contraceptions contre-indiquées après MTEV |
| **A** | Prise en charge | Prévention | Situations nécessitant une prévention de la MTEV |
| **B** | Prise en charge | Durée d'anticoagulation | TVP proximale, EP |
| **B** | Étiologies | Cancer occulte | Indication d'une recherche de cancer |
| **B** | Suivi / pronostic | Complications tardives | Syndrome post-thrombotique, HTAP |
| **B** | Suivi / pronostic | Avant arrêt de l'AC | Complication à dépister avant d'arrêter un anticoagulant pour EP |
| **A** | Prise en charge | TV superficielle | Principes de prise en charge |

---

## Parcours Rang A

- [I. Définitions](#i-définitions)
- [II. Épidémiologie](#ii-épidémiologie)
- [III. Facteurs prédisposants](#iii-facteurs-prédisposants)
- [IV. Physiopathologie](#iv-physiopathologie)
- [V. Histoire naturelle](#v-histoire-naturelle)
- [VI. Thrombose veineuse profonde](#vi-thrombose-veineuse-profonde)
- [VII. Embolie pulmonaire](#vii-embolie-pulmonaire)
- [VIII. Traitement curatif](#viii-traitement-curatif)
- [IX. Traitement préventif](#ix-traitement-préventif)

---

## Sommaire

- [Vignette clinique](#vignette-clinique)
- [I. Définitions](#i-définitions)
- [II. Épidémiologie](#ii-épidémiologie)
- [III. Facteurs prédisposants](#iii-facteurs-prédisposants)
- [IV. Physiopathologie](#iv-physiopathologie)
- [V. Histoire naturelle](#v-histoire-naturelle)
- [VI. Thrombose veineuse profonde](#vi-thrombose-veineuse-profonde)
- [VII. Embolie pulmonaire](#vii-embolie-pulmonaire)
- [VIII. Traitement curatif](#viii-traitement-curatif)
- [IX. Traitement préventif](#ix-traitement-préventif)
- [Points](#points)
- [Notions indispensables et inacceptables](#notions-indispensables-et-inacceptables)
- [Réflexes transversalité](#réflexes-transversalité)
- [Entraînement](../../Entrainement/QI/226_TVP_embolie_pulmonaire.md)

---

'''

QI_CONTENT = '''# Entraînement — Item 226 Thrombose veineuse profonde et embolie pulmonaire

> Collège CNEC 3e éd. · Chapitre 19 · corrigés p. 586  
> Cours : [226 TVP et embolie pulmonaire](../../Cours/V_MTEV/226_TVP_embolie_pulmonaire.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRM 1

Au sujet de la maladie veineuse thromboembolique, quelles sont les réponses justes ?

- A. Une thrombose veineuse fémorale est une thrombose distale
- B. Le risque en l'absence de traitement d'une thrombose veineuse est l'insuffisance cardiaque droite
- C. Le retentissement respiratoire de l'embolie pulmonaire associe effet espace mort et effet shunt
- D. La thrombose veineuse est plus fréquente et plus grave que l'embolie pulmonaire
- E. Une chirurgie dans le mois qui précède une thrombose veineuse est un facteur déclenchant majeur permanent

**Réponse : B, C**

Une TV fémorale est **proximale** (distale = sous-poplitée) (**A** faux). Sans traitement, le risque est l'EP, qui peut se compliquer de cœur pulmonaire et d'insuffisance cardiaque droite (**B**). Le retentissement respiratoire associe effet espace mort et effet shunt (zones ventilées non perfusées) (**C**). La TVP est plus fréquente mais **moins grave** que l'EP (**D** faux). Une chirurgie dans le mois est un facteur déclenchant majeur **temporaire** (**E** faux).

---

## QRM 2

Au sujet du diagnostic de la maladie veineuse thromboembolique, quelles sont les réponses justes ?

- A. Le diagnostic positif de la thrombose veineuse associe œdème et D-dimères positifs
- B. Le diagnostic positif de l'embolie pulmonaire associe dyspnée et D-dimères positifs
- C. Le diagnostic positif de la maladie veineuse thromboembolique intègre le calcul du score de probabilité clinique
- D. Si la probabilité clinique de l'embolie pulmonaire est forte, un dosage des D-dimères doit être pratiqué
- E. Si la probabilité clinique de la thrombose veineuse est forte, un échodoppler veineux doit être pratiqué

**Réponse : C, E**

Le diagnostic intègre le score de probabilité (Wells ou Genève) (**C**). Les D-dimères ont surtout une VPN élevée si la probabilité est **faible ou intermédiaire** ; ils sont **inutiles** si la probabilité d'EP est forte (**D** faux). Œdème + D-dimères, ou dyspnée + D-dimères, ne suffisent pas au diagnostic positif (**A**, **B** faux). Si la probabilité de TVP est forte, un échodoppler veineux s'impose (**E**).

---

## QRU 3

Au sujet de la gravité de l'embolie pulmonaire, quelle est la réponse juste ?

- A. Une pression artérielle > 180 mmHg de systolique est un signe de gravité
- B. Des cavités droites dilatées en échocardiographie sont un signe constant en cas d'embolie pulmonaire
- C. Une tachycardie > 110 bpm est un élément de gravité
- D. Un dosage du BNP négatif élimine une embolie pulmonaire grave
- E. Une embolie pulmonaire avec état de choc est un mode de révélation fréquent

**Réponse : C**

Une tachycardie > 110 bpm entre dans le score PESI simplifié (**C**). La gravité hémodynamique est l'**hypotension** (PAS < 100 mmHg), pas l'HTA (**A** faux). La dilatation des cavités droites est un facteur de gravité mais **n'est pas constante** (**B** faux). Un BNP négatif n'élimine pas une EP grave (**D** faux). Le choc n'est pas un mode de révélation fréquent (5–10 %) (**E** faux).

---

## QRM 4

Au sujet de l'évolution de la maladie veineuse thromboembolique, quelles sont les réponses justes ?

- A. L'embolie pulmonaire peut évoluer vers une insuffisance cardiaque droite
- B. Une thrombose veineuse profonde peut évoluer vers un œdème chronique
- C. Le risque hémorragique du traitement anticoagulant est négligeable
- D. La récidive d'embolie pulmonaire est une complication très rare
- E. La complication la plus fréquente de l'embolie pulmonaire est l'insuffisance respiratoire chronique

**Réponse : A, B**

L'EP peut évoluer vers un cœur pulmonaire aigu ou chronique (**A**). Une TVP peut évoluer vers un œdème chronique : **syndrome post-thrombotique**, qui justifie la contention (**B**). Le risque hémorragique n'est pas négligeable (**C** faux). La récidive n'est pas très rare (**D** faux). L'insuffisance respiratoire chronique n'est pas la complication la plus fréquente (**E** faux).

---

## QRM 5

Au sujet du traitement de la maladie veineuse thromboembolique, quelles sont les réponses justes ?

- A. La base du traitement est la prise en charge en soins intensifs en urgence
- B. Le traitement diurétique doit être débuté en urgence
- C. L'oxygénothérapie est indispensable en cas d'embolie pulmonaire
- D. Le traitement thrombolytique doit être débuté en urgence en cas d'embolie pulmonaire à haut risque
- E. Le lever précoce dès que le traitement anticoagulant est efficace est recommandé après une thrombose veineuse des membres inférieurs

**Réponse : D, E**

Thrombolyse en urgence si EP **à haut risque** (choc / hypotension), en l'absence de contre-indication (**D**). Lever précoce dès que l'anticoagulation est efficace (**E**). L'USIC dépend de la gravité, ce n'est pas la règle pour toute MTEV (**A** faux). Les diurétiques ne font pas partie du traitement immédiat (**B** faux). L'oxygène dépend de la saturation, il n'est pas systématique (**C** faux).
'''

SUB_I_HEADERS = {
    "I. Formes cliniques particulières",
    "I. TVP distales",
}


def clean_line(raw):
    line = raw.strip()
    if not line:
        return None
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return None
    if PAGE_NUM_RE.match(line):
        return None
    if line in FLOW_GARBAGE:
        return None
    if re.match(r"^[A-G]$", line) and len(line) == 1:
        return None
    if re.match(r"^[\d\.]{1,6}$", line):
        return None
    line = line.replace("• 0 ", "• **Rang A.** ")
    for prefix, repl in (
        ("• O ", "• **Rang A.** "),
        ("• □ ", "• **Rang B.** "),
        ("• Q ", "• **Rang B.** "),
        ("• D ", "• **Rang B.** "),
        ("• El ", "• **Rang B.** "),
    ):
        if line.startswith(prefix):
            line = repl + line[len(prefix):]
            break
    for prefix, repl in (
        ("El ", "**Rang B.** "),
        ("□ ", "**Rang B.** "),
        ("O ", "**Rang A.** "),
        ("Q ", "**Rang B.** "),
        ("0 ", "**Rang A.** "),
    ):
        if line.startswith(prefix):
            rest = line[len(prefix):]
            if prefix == "0 " and rest and rest[0].isdigit():
                break
            line = repl + rest
            break
    if line.startswith("D ") and not line.startswith("D. ") and line[2:3].isupper():
        line = "**Rang B.** " + line[2:]
    return line


def match_section(cl):
    for sec, hdr in sorted(SECTION_MAP.items(), key=lambda x: -len(x[0])):
        if cl == sec or cl.startswith(sec + " "):
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
    stop_markers = ("► Entraînement", "GQRM", "O QRM", "===== PDF PAGE 523", "Item 235")
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
        stop = text.find("===== PDF PAGE 522")
    if stop == -1:
        stop = text.find("Item 235")
    chunk = text[:stop] if stop != -1 else text

    lines_out = []
    skip_until_vignette = True
    in_body = False
    in_points = False
    seen_ix = False
    pending_bullet = None
    pending_header = None
    skip_mode = None
    enc1 = tab1 = tab2 = tab3 = False
    inserted_figs = set()

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
                last = lines_out[-1].rstrip() if lines_out else ""
                smashable = (
                    lines_out
                    and not cl.startswith(("#", "!", "|"))
                    and not last.startswith(("**Fig.", "![", "#", "|"))
                )
                if smashable:
                    lines_out[-1] = last + cl
                    pending_bullet = None
                    continue
            elif not cl.startswith(("• ", "- ", "#", "**Rang")):
                cl = pending_bullet + cl
            pending_bullet = None

        if pending_header:
            if (cl[0].islower() or cl.startswith("(") or cl.startswith("ou ")
                    or cl.startswith("avec ")):
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
        if cl.startswith("Réflexes transversalité"):
            break
        if in_body and seen_ix and cl == "Thrombose veineuse profonde":
            flush_header()
            lines_out.append("\n\n---\n\n## Points\n")
            lines_out.append(POINTS_BLOCK)
            in_points = True
            continue
        if in_points:
            continue

        if skip_mode == "enc1":
            if cl.startswith("Le niveau de risque"):
                skip_mode = None
            else:
                continue
        if skip_mode == "tab1":
            if cl.startswith("D. Diagnostic paraclinique") or cl.startswith("### D."):
                skip_mode = None
            else:
                continue
        if skip_mode == "tab2":
            if cl.startswith("C. Diagnostic paraclinique") or cl.startswith("### C."):
                skip_mode = None
            else:
                continue
        if skip_mode == "tab3":
            if cl.startswith("**Rang A.** La préférence") or cl.startswith("La préférence du patient"):
                skip_mode = None
            else:
                continue
        if skip_mode == "fig1":
            if cl.startswith("F. Diagnostic étiologique") or cl.startswith("### F."):
                skip_mode = None
            else:
                continue
        if skip_mode == "fig2":
            if cl.startswith("Fig. 19.3") or cl.startswith("E. Diagnostic"):
                skip_mode = None
            else:
                continue
        if skip_mode == "fig3":
            if (
                cl.startswith("E. Diagnostic")
                or cl.startswith("### E.")
                or "L'EP est grave" in cl
            ):
                skip_mode = None
            else:
                continue
        if skip_mode == "fig4":
            if (
                cl.startswith("Fig. 19.4")
                or cl.startswith("1. Héparine")
                or cl.startswith("### 1.")
            ):
                skip_mode = None
            else:
                continue

        hdr = match_section(cl)
        if hdr:
            flush_header()
            lines_out.append(hdr)
            in_body = True
            if cl.startswith("IX."):
                seen_ix = True
            continue

        if any(cl.startswith(h) for h in SUB_I_HEADERS):
            start_header(2, cl)
            continue

        if cl.startswith("Encadré 19.1"):
            if not enc1:
                lines_out.append(ENCADRE_19_1)
                enc1 = True
            skip_mode = "enc1"
            continue
        if cl.startswith("Tableau 19.1"):
            if not tab1:
                lines_out.append(TABLE_19_1)
                tab1 = True
            skip_mode = "tab1"
            continue
        if cl.startswith("Tableau 19.2"):
            if not tab2:
                lines_out.append(TABLE_19_2)
                tab2 = True
            skip_mode = "tab2"
            continue
        if cl.startswith("Tableau 19.3"):
            if not tab3:
                lines_out.append(TABLE_19_3)
                tab3 = True
            skip_mode = "tab3"
            continue

        if cl.startswith("Fig. 19.1"):
            if "Fig. 19.1" not in inserted_figs:
                insert_fig(lines_out, "Fig. 19.1")
                inserted_figs.add("Fig. 19.1")
                skip_mode = "fig1"
            continue
        if cl.startswith("Fig. 19.2"):
            if "Fig. 19.2" not in inserted_figs:
                insert_fig(lines_out, "Fig. 19.2")
                inserted_figs.add("Fig. 19.2")
                skip_mode = "fig2"
            continue
        if cl.startswith("Fig. 19.3"):
            if "Fig. 19.3" not in inserted_figs:
                insert_fig(lines_out, "Fig. 19.3")
                inserted_figs.add("Fig. 19.3")
                skip_mode = "fig3"
            continue
        if cl.startswith("Fig. 19.4"):
            if "Fig. 19.4" not in inserted_figs:
                insert_fig(lines_out, "Fig. 19.4")
                inserted_figs.add("Fig. 19.4")
                skip_mode = "fig4"
            continue
        if cl.startswith("Suspicion d") and "EP" in cl:
            skip_mode = "fig4"
            continue

        m = SUBSECTION_RE.match(cl)
        if m and in_body and len(cl) < 160 and not cl.startswith(("I. Définitions", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII.", "IX.")):
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
        ("1 0 000", "10 000"),
        ("L’ECC retrouve", "L'ECG retrouve"),
        ("L'ECC retrouve", "L'ECG retrouve"),
        ("lymphcedème", "lymphœdème"),
        ("oedème", "œdème"),
        ("Q II s'agit", "**Rang B.** Il s'agit"),
        ("**Rang B.** II s'agit", "**Rang B.** Il s'agit"),
        ("Usic", "USIC"),
        ("llsic", "USIC"),
        ("Ml ", "MI "),
        ("du Ml", "du MI"),
        ("un Ml", "un MI"),
        ("Fil et V", "FII et FV"),
        ("0,4 mL/24 h", "0,4 mL/24 h"),
        ("tinzaparine à la dose de 175 Ul/j", "tinzaparine à la dose de 175 UI/kg/j"),
        ("500 Ul/kg/j", "500 UI/kg/j"),
        ("2 000 Ul/j", "2 000 UI/j"),
        ("4 000 Ul/j", "4 000 UI/j"),
        ("175 Ul/j", "175 UI/kg/j"),
        ("Q II ", "**Rang B.** Il "),
        ("**Rang A.** II ", "**Rang A.** Il "),
        ("I 161", "161"),
        ("J 463", ""),
        ("phlegma- tia", "phlegmatia"),
        ("dinical", "clinical"),
        ("Le Gai G", "Le Gal G"),
        ("7 1.", "71."),
        ("diagnostic d'ER ", "diagnostic d'EP. "),
        ("d'ER Outre", "d'EP. Outre"),
        ("VL Thrombose", "VI. Thrombose"),
        ("suffit©", "suffire"),
        ("surchargeas", "surcharge des"),
        ("eXisfénce", "existence"),
        ("un le diagnostic", "un score clinique faible permet d'exclure le diagnostic"),
        ("1 5 %", "15 %"),
        ("1, 5-2,5", "1,5–2,5"),
        ("UI/kg/1 2 h", "UI/kg/12 h"),
        ("500 pg/L", "500 µg/L"),
        ("En l'absence de choc, la présence de ces si risque intermédiaire. imet de classer le patient comme étant à",
         "En l'absence de choc, la présence de ces signes permet de classer le patient comme étant à risque intermédiaire."),
        ("**Rang A.** \\Angiographie pulmonaire conventionnelle Cet examen n'est plus pratiqué.",
         "### 4. Angiographie pulmonaire conventionnelle\n\nCet examen n'est plus pratiqué."),
        ("**Rang A.** \\ monaire conventionnelle Angiographie Cet examen n'est plus pratiqué.",
         "### 4. Angiographie pulmonaire conventionnelle\n\nCet examen n'est plus pratiqué."),
        ("Choc ou hypotension Scanner disponible immédiatement Échocardiographie Dysfonction VD r", ""),
        ("lorsqu'ils sont présent :", "lorsqu'ils sont présents :"),
    ]
    for a, b in fixes:
        text = text.replace(a, b)
    text = re.sub(
        r"\*\*Rang A\.\*\*.{0,50}Angiographie Cet examen n'est plus pratiqué\.",
        "### 4. Angiographie pulmonaire conventionnelle\n\nCet examen n'est plus pratiqué.",
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
        "• Toujours évoquer l'EP devant une dyspnée aiguë ou d'apparition récente, un malaise ou une syncope, une douleur thoracique.\n"
        "• Examens d'orientation : radiographie thoracique, gazométrie artérielle et ECG.\n"
        "• L'angioscanner pulmonaire permet de confirmer le diagnostic.\n"
        "• Devant une EP, reconnaître rapidement une hypotension ou un choc : cela guide la stratégie."
    )
    inacc = "\n".join(n if n.startswith("•") else "• " + n for n in notions_inacc) or (
        "• Méconnaître une EP devant une dyspnée isolée (la douleur thoracique est inconstante).\n"
        "• Doser les D-dimères lorsque la probabilité clinique d'EP est forte.\n"
        "• Omettre la thrombolyse devant une EP à haut risque sans contre-indication."
    )
    refl = "\n".join(r if r.startswith("•") else "• " + r for r in reflexes)
    extra_refl = [
        "• Item 203 — Dyspnée aiguë et chronique.",
        "• Item 230 — Douleur thoracique aiguë.",
        "• Item 234 — Insuffisance cardiaque.",
    ]
    if "203" not in refl:
        refl = (refl + "\n" if refl else "") + "\n".join(extra_refl)
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

Questions isolées et corrigés : [Entrainement/QI/226_TVP_embolie_pulmonaire.md](../../Entrainement/QI/226_TVP_embolie_pulmonaire.md)
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
        valid = []
        for h in hits:
            probe = fitz.Rect(h.x0, h.y0, min(page.rect.width, h.x1 + 40), h.y1 + 2)
            t = page.get_text("text", clip=probe)
            if re.search(rf"Fig\.\s*{re.escape(fig_num)}(?!\d)", t):
                valid.append(h)
        hits = valid or hits
        if hits:
            r = max(hits, key=lambda x: x.y0)
            y1 = min(page.rect.height, r.y1 + (55 if fig_num == "19.4" else 12))
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
    row = "| Fait | 226 TVP / embolie pulmonaire | [V_MTEV/226_TVP_embolie_pulmonaire.md](./V_MTEV/226_TVP_embolie_pulmonaire.md) |\n"
    if "226 TVP" not in text:
        text = text.replace("| À faire | … | lots suivants |", row + "| À faire | … | lots suivants |")
        README.write_text(text, encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains item 226")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    sections = re.findall(r"^# [IVX]+\.", content, re.M)
    fig_count = len(list(IMG_DIR.glob("fig_19_*.png")))
    print(f"Course size: {size} bytes, section headers: {len(sections)} ({sections})")
    print(f"Figures: {fig_count} PNGs")
    if size < 40_000:
        print("WARN: course < 40 KB")
    if len(sections) < 9:
        print("WARN: missing section headers")
    if fig_count < 4:
        print("WARN: fewer than 4 figures")
    if "Item 235" in content or "Péricardite aiguë" in content.split("## Réflexes")[0]:
        print("WARN: Item 235 leak")
    else:
        print("No Item 235 leak")
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
