# -*- coding: utf-8 -*-
"""Generate item 231 ECG: index + 7 sous-fichiers + QI + figures."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
SRC = ROOT / "_tmp_item231.txt"
PDF = ROOT / "CARDIO 3e.pdf"
OUT_DIR = ROOT / "Cours" / "III_Rythmologie"
IMG_DIR = OUT_DIR / "img"
QI_OUT = ROOT / "Entrainement" / "QI" / "231_ECG.md"
README = ROOT / "Cours" / "README.md"

# Do NOT put section titles I/II/A/B/C in WATERMARK_PATTERNS.
WATERMARK_PATTERNS = [
    r"Ce livre a été acheté.*",
    r"Pour avoir plus d'exclusivités.*",
    r"© 2025 Elsevier.*",
    r"^Connaissances\s*$",
    r"^Rythmologie\s*$",
    r"^Rythmologîe\s*$",
    r"^CHAPITRE\s*$",
    r"^15\s*$",
    r"^Item 231\s*$",
    r"^Item 231 -.*",
    r"^Électrocardiogramme\s*$",
    r"^Situations de départ\s*$",
    r"^Hiérarchisation des connaissances\s*$",
    r"^Hiérarchisât.*",
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
    r"^clésl\s*$",
    r"^clés\?\s*$",
    r"^nts\s*$",
    r"^à l'entraînement de l'intelligence artificielle.*",
    r"^!St strictement interdite.*",
    r"^: sur https://t\.me/Faille_V2\s*$",
    r"^===== PDF PAGE \d+ =====$",
    r"^O QRM\s*\d+.*",
    r"^© QRM\s*\d+.*",
    r"^G QRM\s*\d+.*",
    r"^0 QRM\s*\d+.*",
    r"^QRM\s*\d+.*",
    r"^QRU\s*\d+.*",
    r"^Médecine cardiovasculaire\s*$",
    r"^Dessin de Carole Fumât\.?\s*$",
    r"^Source : Kennedy A,.*",
    r"^from the 12-lead electrocardiogram\..*",
    r"^Item 237\s*$",
    r"^Palpitations\s*$",
    r"^■w Item 231.*",
]

PAGE_NUM_RE = re.compile(r"^(337|338|339|340|341|342|343|344|345|346|347|348|349|350|351|352|353|354|355|356|357|358|359|360|361|362|363|364|365|366|367|368|369|370|371|372|373|374|375|376|377|378|379|380|381|382|383|384|385|386|387)$")

KEEP_SHORT = {
    "Attention", "Attention :", "Pour comprendre", "Point sémantique",
    "À connaître", "Conseils d'interprétation", "Conseil d'interprétation",
    "Cf. chapitre 13.", "Cf. chapitre 14.", "Cf. chapitre 5.", "Cf. chapitre 4.",
    "Cf. chapitre 12.", "Normal", "Diagnostics différentiels",
    "Syndromes avec sus-décalage de ST", "Ondes Q de nécrose",
    "Analyse de la repolarisation", "Syndromes coronariens aigus sans sus-décalage de ST",
}

DIAGRAM_LABELS = {
    "Nœud sinusal", "Nœud", "atrioventriculaire", "His", "Branche gauche",
    "Branche droite", "BBD", "BBG", "V1", "V2", "V3", "V4", "V5", "V6",
    "VI", "VII", "aVL", "aVR", "aVF", "aVl", "DI", "D2", "D3", "II", "III",
    "QRS", "Onde P", "NAV", "mV", "Notch", "Réentrée", "Hyperautomatisme",
    "Mécanismes complexes", "Pacemaker", "Défibrillateur", "Bradycardie",
    "Cellules contractiles", "« sodiques »", "Myocytes atriaux et ventriculaires",
    "Cellules nodales « calciques »", "= cellules pacemaker",
    "Nœud sinusal et NAV", "Caractéristiques intermédiaires :",
    "His/branches/Purkinje", "Repolarisation", "Dépolarisation",
    "Pas de pente", "Potentiel", "seuil", "Pente", "de phase 4",
    "Cellule", "Modified Lewis lead", "Ligne", "médioclaviculaire",
    "droite", "gauche", "moyenne gauche", "Ligne axillaire",
    "Résau électrique spécialisé", "Plan d’isolation électrique",
    "atrioventriculaire", "BAV1", "BAV3", "BAV2/1", "Normal",
    "Allongement constant", "du PR", "suprahissien", "infrahissien",
    "ou", "Cicatrice d’infarctus", "Préexcitation", "Problème rythmique",
    "Problème hémodynamique", "(insuffisance cardiaque)",
    "Sondes de stimulation", "Resynchronisation cardiaque",
}

LEAD_LINE_RE = re.compile(
    r"^(V[1-9R]*|aV[RLFrl]|D[I123]|DI|DII|DIII|II+|III|VI+|mV|QRS|His|NAV|"
    r"BBD|BBG|HBAG|HBPG|K\*|Na\+|Ca2\+|A|H|J|L|I|F|:a2\+|Na \+’)\s*$",
    re.I,
)

SUBSECTION_RE = re.compile(r"^([A-F]\.\s.+)$")
NUM_SUBSECTION_RE = re.compile(r"^(\d+\.\s.+)$")
FIG_CAPTION_RE = re.compile(r"^Fig\.\s*15\.(\d+)\.?\s*(?:[0OQ©□] )?\s*(.*)$", re.I)
FIG_ANY_RE = re.compile(r"(?:Fig\.|fig\.|figure)\s*1\s*5\.(\d+)", re.I)

FIG_CAPTIONS = {
    1: "Potentiels d'action et canaux ioniques des cellules myocytaires",
    2: "Réseau électrique cardiaque",
    3: "Polarité du signal électrocardiographique en fonction de l'orientation de l'influx électrique",
    4: "Positionnement des électrodes précordiales",
    5: "Construction des dérivations frontales",
    6: "Dérivations de Lewis",
    7: "Territoires cardiaques selon les dérivations ECG",
    9: "Électrocardiogramme normal",
    10: "Bloc de branche droite (BBD) et bloc de branche gauche (BBG) complets",
    11: "ECG de bloc de branche droit complet",
    12: "ECG de bloc de branche gauche complet",
    13: "Notch",
    14: "Discordance appropriée",
    15: "Hémiblocs antérieur gauche (HBAG) et postérieur gauche (HBPG)",
    16: "Hémibloc antérieur gauche (axe hypergauche)",
    17: "Aspect d'hémibloc antérieur gauche (axe hypergauche avec négativité D2, D3, aVF)",
    18: "Localisations possibles du ralentissement atrioventriculaire (bloc bifasciculaire + BAV1)",
    19: "Bloc de branche droit interrompu par deux battements à aspect de BBG = bloc alternant",
    20: "Résumé de la sémiologie des blocs atrioventriculaires (BAV)",
    21: "Aspect de bloc atrioventriculaire du 1er degré, allongement fixe et constant de PR",
    22: "Aspect de bloc atrioventriculaire du 2e degré, de type Mobitz I (Luciani-Wenckebach)",
    23: "Aspect de bloc atrioventriculaire complet ou du 3e degré",
    24: "Aspect de bloc sinoatrial du 2e degré",
    25: "Aspect d'échappement jonctionnel traduisant une dysfonction sinusale",
    26: "Différents aspects de dysfonction sinusale en pratique clinique",
    27: "Algorithme diagnostique devant une bradycardie",
    28: "Mécanismes des troubles du rythme (réentrée, hyperautomatisme, mécanismes complexes)",
    29: "Fibrillation atriale à petites mailles, bien visibles sur le long tracé D2, et BBG complet",
    30: "Mécanisme de la fibrillation atriale",
    31: "Fibrillation atriale et différents niveaux de conduction atrioventriculaire",
    32: "Fibrillation atriale à petites mailles, trémulation en D2, D3 et aVF",
    33: "Mécanisme du flutter atrial",
    34: "Flutter atrial typique : ondes F négatives en D2, D3 et aVF, positives en V1 et négatives en V6",
    35: "Mécanisme des tachycardies atriales focales",
    36: "Mécanisme des tachycardies jonctionnelles",
    37: "Tachycardie jonctionnelle, régulière à QRS fins, sans activité atriale visible",
    38: "Schéma présentant l'aspect des extrasystoles en fonction de l'origine",
    39: "Extrasystole atriale",
    40: "Réentrée autour d'une cicatrice d'infarctus (mécanisme de TV)",
    41: "Aspect de tachycardie ventriculaire non soutenue",
    42: "Tachycardie ventriculaire : QRS larges, régulière, dissociation ventriculoatriale",
    43: "Schéma d'une capture et d'une fusion pendant une tachycardie ventriculaire",
    44: "Tachycardie ventriculaire régulière à QRS larges avec fusions",
    45: "Tachycardie ventriculaire : QRS larges, concordance positive dans les précordiales",
    46: "Tachycardie ventriculaire à QRS très large, QRS de fusion",
    47: "Fibrillation ventriculaire en larges fuseaux, puis retour en rythme sinusal par choc",
    48: "Électrocardiogramme d'une fibrillation ventriculaire (FV) en 12D",
    49: "Torsades de pointes sur QT long",
    50: "Torsades de pointes avec QT normal, déclenchées par deux extrasystoles ventriculaires",
    51: "Algorithme décisionnel devant une tachycardie",
    52: "De gauche à droite : onde P normale, hypertrophie atriale droite, hypertrophie atriale gauche",
    53: "Hypertrophie ventriculaire gauche, Sokolow à 40 mm, « pseudo » sus-décalage ST en V1-V2, onde T négative en D1, aVL, V6",
    54: "ECG pendant une embolie pulmonaire, déviation axiale droite, S1Q3, fibrillation atriale",
    55: "Hyperkaliémie avec dysfonction sinusale et échappement jonctionnel",
    56: "Péricardite au stade initial",
    57: "Préexcitation : compétition NAV / voie accessoire, origine de l'onde delta",
    58: "Préexcitation ventriculaire (onde delta) et anomalies de repolarisation",
    59: "Tachycardie irrégulière à QRS larges de taille variable, dits « en accordéon » (super-Wolff)",
    60: "Les différentes prothèses cardiaques",
    61: "Électroentraînement ventriculaire, spike unipolaire devant les QRS",
    62: "Électroentraînement ventriculaire, spike bipolaire devant les QRS",
    63: "ECG (QRM 2)",
    64: "ECG (QRM 4)",
}

SECTIONS = [
    {
        "key": "normal",
        "marker": "A. ECG normal",
        "file": "231_ECG_normal.md",
        "title": "I.A — ECG normal",
        "rang": "**Rang A.**",
    },
    {
        "key": "conduction",
        "marker": "B. Troubles de conduction",
        "file": "231_ECG_conduction.md",
        "title": "I.B — Troubles de conduction",
        "rang": "**Rang A** · **Rang B.**",
    },
    {
        "key": "sv",
        "marker": "C. Troubles du rythme supraventriculaire",
        "file": "231_ECG_SV.md",
        "title": "I.C — Troubles du rythme supraventriculaire",
        "rang": "**Rang A** · **Rang B.**",
    },
    {
        "key": "ventriculaire",
        "marker": "D. Troubles du rythme ventriculaire",
        "file": "231_ECG_ventriculaire.md",
        "title": "I.D — Troubles du rythme ventriculaire",
        "rang": "**Rang A** · **Rang B.**",
    },
    {
        "key": "hypertrophies",
        "marker": "E. Hypertrophies",
        "file": "231_ECG_hypertrophies.md",
        "title": "I.E — Hypertrophies",
        "rang": "**Rang A.**",
    },
    {
        "key": "autres",
        "marker": "F. Autres pathologies",
        "file": "231_ECG_autres.md",
        "title": "I.F — Autres pathologies",
        "rang": "**Rang A** · **Rang B.**",
    },
    {
        "key": "indications",
        "marker": "II. Indications",
        "file": "231_ECG_indications.md",
        "title": "II. — Indications",
        "rang": "**Rang A** · **Rang B.**",
    },
]

TABLE_15_1 = """
**Tableau 15.1.** Schématisation des actions des médicaments antiarythmiques.

| Classe | Arythmies atriales | Arythmies ventriculaires | Ralentisseurs du NAV | Principales DCI |
|---|---|---|---|---|
| Classe I : canaux sodiques | X | X | | Flécaïnide |
| Classe II : bêtabloquants | X | X | X | Bisoprolol |
| Classe III : canaux potassiques | X | X | | Amiodarone, sotalol |
| Classe IV : canaux calciques | | | X | Vérapamil |
| Digitaliques | | | X | Digoxine |

DCI : dénomination commune internationale ; NAV : nœud atrioventriculaire.
"""

TABLE_15_2 = """
**Tableau 15.2.** Résumé des valeurs normales.

| Onde, intervalle | Valeurs normales |
|---|---|
| Fréquence cardiaque (FC) | 60–100 bpm |
| Durée de P | < 120 ms |
| Axe de P | 60° (D2) |
| Amplitude de P | < 2,5 mm (en D2) |
| PR | 120–200 ms |
| Durée de QRS | 70–110 ms |
| Axe de QRS | −30 à +90° |
| Onde Q physiologique | < 1/3 amplitude QRS et < 40 ms de durée |
| QT corrigé (variable avec FC) | < 450 ms à 60 bpm, en pratique 470–480 ms |
"""

ENCADRE_15_1 = """
> **Encadré 15.1 — Comment créer un bloc atrioventriculaire transitoire (= intensifier le filtre AV)**
>
> **Manœuvres vagales**
> - Manœuvre de Valsalva (expiration forcée à glotte fermée)
> - Compression carotidienne unilatérale (contre-indiquée en cas d'athérome important ou de souffle carotidien)
> - Boire un grand verre d'eau froide
>
> NB. La manœuvre de compression oculaire bilatérale n'est plus recommandée (risque de décollement de rétine en cas de myopie).
>
> **Adénosine IV** (en cas d'inefficacité des manœuvres vagales)
> - Mécanisme vagomimétique via les récepteurs purinergiques
> - Administration en flash intraveineux
> - Durée d'effet d'une dizaine de secondes
>
> Contre-indications : asthme (bronchospasme intense transitoire possible, même chez un non-asthmatique) ; hypotension artérielle. Comme les manœuvres vagales, l'adénosine sert aussi au diagnostic différentiel des tachycardies.
"""

ENCADRE_15_2 = """
> **Encadré 15.2 — Diagnostic d'une tachycardie ventriculaire**
>
> **Arguments de certitude**
> - **Rang A.** Dissociation ventriculoatriale (ondes P habituellement plus lentes et dissociées des QRS). S'il y a plus de QRS que d'ondes P, la tachycardie vient forcément du ventricule. À ne pas confondre avec la dissociation atrioventriculaire du bloc complet (fig. 15.42).
> - Complexes de capture ou de fusion : QRS fins précédés d'une onde P, intercalés dans le tracé (fig. 15.43). Certaines ondes P passent par les voies de conduction et capturent le ventricule (QRS fin) ou donnent un QRS intermédiaire (fusion) (fig. 15.44). Ils ne peuvent être présents que s'il y a dissociation ventriculoatriale.
>
> **Arguments en faveur d'une TV**
> - Cardiopathie sous-jacente +++ (la plupart des TV sont favorisées par une cardiopathie)
> - Concordance positive ou négative : QRS entièrement positif (R) ou entièrement négatif (QS) de V1 à V6 (fig. 15.45)
> - Déviation axiale extrême (QRS positif en aVR) (fig. 15.46)
> - QRS larges avec aspect différent d'un bloc de branche habituel
"""

POINTS_BLOCK = """
• On détermine si le rythme est trop lent (bradycardie < 60 bpm) ou trop rapide (tachycardie > 100 bpm), on détermine si le rythme est sinusal ou non.

• On détermine les temps de conduction (PR, QRS, QT), l'axe électrique des QRS et on analyse la repolarisation.

• En cas de bradycardie, on recherche une dysfonction sinusale (activité atriale lente ou inexistante) et/ou un BAV (intervalle PR trop long ou ondes P bloquées), puis on précise le degré et le type.

• Le diagnostic de bloc de branche se fait sur la durée du QRS (positif V1 = droit, négatif V1 = gauche), le diagnostic d'hémibloc se fait sur l'axe du QRS. Les blocs de branche ne donnent pas de bradycardie.

• Devant un QRS large, on ne doit pas confondre le diagnostic de bloc de branche (sans conséquence immédiate) avec celui de TV (mortelle si non prise en charge).

• En cas de tachycardie, on examine la largeur des QRS et la régularité, puis on utilise dans la majorité des cas des manœuvres vagales ou de l'adénosine.

• La fibrillation atriale est le seul diagnostic en cas de tachycardie complètement irrégulière à QRS fins.

• L'activité atriale du flutter est monomorphe.

• Toute tachycardie régulière à QRS larges est une TV jusqu'à preuve du contraire.

• L'indice de Sokolow est à retenir comme bon marqueur d'hypertrophie ventriculaire gauche, en se souvenant que ce diagnostic peut s'associer à des anomalies de repolarisation.

• Au cours des SCA avec ST, il ne faut pas confondre la lésion et son miroir, une onde de Pardee avec un élargissement de QRS, ou évoquer à tort une péricardite aiguë.
"""

INDEX_HEADER = '''# Item 231 — Électrocardiogramme

> **Collège CNEC / SFC** · 3e édition (2025) · p. 337–387 · R2C  
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

4 Douleur abdominale.  
21 Asthénie.  
42 Hypertension artérielle.  
43 Découverte d'une hypotension artérielle.  
50 Malaise/perte de connaissance.  
121 Déficit neurologique sensitif et/ou moteur.  
159 Bradycardie.  
160 Détresse respiratoire aiguë.  
161 Douleur thoracique.  
162 Dyspnée.  
165 Palpitations.  
166 Tachycardie.  
178 Demande/prescription raisonnée et choix d'un examen diagnostique.  
185 Réalisation et interprétation d'un électrocardiogramme (ECG).  
200 Dyscalcémie.  
201 Dyskaliémie.  
204 Élévation des enzymes cardiaques.  
266 Consultation de suivi d'un patient polymédiqué.  
287 Consultation de suivi et éducation thérapeutique d'un patient insuffisant cardiaque.

---

## Hiérarchisation des connaissances

| Rang | Rubrique | Intitulé | Descriptif |
|---|---|---|---|
| **A** | Diagnostic positif | ECG normal | Morphologies normales et paramètres numériques |
| **A** | Identifier une urgence | Signes de gravité de l'ECG | Anomalies imposant une réponse thérapeutique urgente |
| **A** | Diagnostic positif | Hypertrophies atriales | Formes droites et gauches |
| **A** | Diagnostic positif | Hypertrophie ventriculaire droite | Y compris aspect d'embolie pulmonaire (S1Q3) |
| **A** | Diagnostic positif | Hypertrophie ventriculaire gauche | Deux formes principales ; indice de Sokolow |
| **A** | Diagnostic positif | Blocs complets de branche, hémiblocs, blocs bifasciculaires | BBD, BBG complets, HBAG, HBPG et associations |
| **B** | Diagnostic positif | Blocs incomplets et blocs fonctionnels | BBD/BBG incomplet, aberrations de conduction |
| **A** | Diagnostic positif | BAV en rythme sinusal | 3e degré et tous types, haut degré, blocs rythmés |
| **A** | Diagnostic positif | BAV associés aux troubles du rythme | BAV 3e degré + FA ou flutter |
| **A** | Diagnostic positif | Dysfonction sinusale | Reconnaître une dysfonction sinusale |
| **B** | Diagnostic positif | Mécanismes et variantes de dysfonction sinusale | BSA du 2e degré, maladie de l'oreillette |
| **A** | Diagnostic positif | Tachycardie sinusale vs TSV non sinusale | Diagnostic positif et différentiel |
| **A** | Diagnostic positif | Fibrillation atriale | Identifier la FA |
| **A** | Diagnostic positif | Flutters atriaux | Reconnaître un flutter atrial |
| **A** | Diagnostic positif | Tachycardies jonctionnelles | |
| **B** | Diagnostic positif | Manœuvres vagales / adénosine | Réalisation et apport diagnostique |
| **A** | Diagnostic positif | Extrasystoles | ESA ou ESV |
| **A** | Diagnostic positif | Tachycardie ventriculaire | Reconnaître une TV |
| **A** | Diagnostic positif | Fibrillation ventriculaire | Reconnaître une FV |
| **B** | Diagnostic positif | Torsades de pointes | TdP et allongement de QT hors hypokaliémie |
| **A** | Diagnostic positif | Dyskaliémies | Anomalies ECG y compris QT long |
| **A** | Diagnostic positif | Allongement de QT | Médicamenteux, congénital, ionique |
| **B** | Diagnostic positif | Péricardites aiguës | Différences ECG péricardite vs SCA |
| **A** | Diagnostic positif | Maladie coronarienne et SCA | Ondes Q, territoires, ST, T, séquelles |
| **A** | Diagnostic positif | Wolff-Parkinson-White | Préexcitation, onde delta |
| **A** | Diagnostic positif | Électroentraînement | Atrial, ventriculaire ou séquentiel |
| **A** | Diagnostic positif | Indications d'un ECG | Cardioscopes, ECG 12–15–18D, urgences |
| **B** | Examens complémentaires | Méthode Holter | Enregistrements externes de longue durée ; outils connectés |

---

## Sommaire

Ce chapitre est découpé en sous-fichiers (item long, ~50 pages).

- [I.A ECG normal](./231_ECG_normal.md) — électrophysiologie, dérivations, valeurs numériques
- [I.B Troubles de conduction](./231_ECG_conduction.md) — blocs de branche, hémiblocs, BAV, dysfonction sinusale
- [I.C Troubles du rythme supraventriculaire](./231_ECG_SV.md) — FA, flutter, TAF, tachycardies jonctionnelles, extrasystoles
- [I.D Troubles du rythme ventriculaire](./231_ECG_ventriculaire.md) — TV, FV, torsades de pointes
- [I.E Hypertrophies](./231_ECG_hypertrophies.md) — atriales, HVG, HVD
- [I.F Autres pathologies](./231_ECG_autres.md) — dyskaliémies, péricardites, préexcitation/WPW, SCA, pacemakers
- [II. Indications](./231_ECG_indications.md) — monitorage, ECG 12D, holter, outils connectés

'''

INDEX_FOOTER = f'''
---

## Points

{POINTS_BLOCK.strip()}

---

## Réflexes transversalité

• Item 232 — Fibrillation atriale  
• Item 236 — Troubles de la conduction intracardiaque  
• Item 237 — Palpitations  
• Item 339 — Syndromes coronariens aigus  
• Item 342 — Malaises, perte de connaissance, crise convulsive de l'adulte

---

## Entraînement

Questions isolées et corrigés : [Entrainement/QI/231_ECG.md](../../Entrainement/QI/231_ECG.md)
'''

QI_CONTENT = r'''# Entraînement — Item 231 Électrocardiogramme

> Collège CNEC 3e éd. · Chapitre 15 · corrigés p. 584  
> Cours : [231 ECG](../../Cours/III_Rythmologie/231_ECG.md)

Les corrigés sont **sous** chaque question. Faire d'abord sans regarder.

---

## QRM 1

Citez les réponses exactes concernant un ECG de cœur sain :

- A. Une onde Q dans le territoire antéroseptal peut être retrouvée
- B. En rythme sinusal, l'onde P est positive en D2
- C. L'axe normal du cœur est compris entre 0 et −90°
- D. Une onde T négative peut être présente en V1
- E. DI et aVL sont les dérivations rapportées au territoire inférieur du ventricule gauche

**Réponse : B, D**

Cœur sain : en rythme sinusal, l'onde P est positive en D2 (**B**) ; une onde T négative est fréquente en V1 (**D**). Une onde Q dans le territoire antéroseptal doit être considérée comme anormale (**A** faux). L'axe normal est compris entre **−30 et +90°**, pas 0 et −90° (**C** faux). DI et aVL sont les dérivations **latérales hautes**, pas inférieures (**E** faux).

---

## QRM 2

Devant l'ECG de la figure 15.63, quelles sont les réponses exactes ?

![Fig. 15.63 — ECG](../../Cours/III_Rythmologie/img/fig_15_63.png)

- A. Il existe un bloc de branche droit complet
- B. Il existe un bloc de branche gauche complet
- C. Il existe une fibrillation ventriculaire
- D. Il existe une tachycardie jonctionnelle
- E. Il existe un hémibloc antérieur gauche

**Réponse : A, E**

BBD complet : QRS > 120 ms et aspect rSR' en V1 (**A**). HBAG : déviation axiale gauche < −30° et négativité prédominante en D2 (**E**). Les QRS sont tous identiques : ce n'est pas une FV (**C** faux). Le rythme est irrégulier : une FA est probable, pas une tachycardie jonctionnelle (**D** faux). Pas de BBG (**B** faux).

---

## QRM 3

Quelles sont les propositions exactes concernant les caractéristiques ECG de la péricardite ?

- A. Le sus-décalage est diffus, concave vers le haut avec absence de miroir
- B. On peut observer une alternance électrique en cas d'épanchement péricardique abondant
- C. Le microvoltage est constant
- D. Le sous-décalage du segment PQ est très évocateur
- E. Le S1Q3 est évocateur mais inconstant

**Réponse : A, B, D**

Péricardite : ST diffus concave sans miroir (**A**), alternance électrique si épanchement abondant (**B**), sous-décalage PQ très évocateur (**D**). Le microvoltage n'est **pas** constant (**C** faux). Le S1Q3 oriente vers une **embolie pulmonaire**, pas une péricardite (**E** faux).

---

## QRM 4

Une femme de 76 ans est amenée aux urgences parce qu'elle se sent dyspnéique depuis le matin. Son ECG est le suivant (fig. 15.64). Quelles sont les réponses exactes ?

![Fig. 15.64 — ECG](../../Cours/III_Rythmologie/img/fig_15_64.png)

- A. Le diagnostic est un BAV2 Mobitz 2
- B. L'étiologie la plus fréquente est une atteinte dégénérative du tissu de conduction cardiaque
- C. Une dyskaliémie doit être systématiquement recherchée
- D. Le nœud sinusal fonctionne normalement
- E. En absence de cause réversible, il y a une indication à l'implantation d'un stimulateur cardiaque

**Réponse : B, C, D, E**

Il s'agit d'un **BAV du 3e degré** (pas de lien fixe entre les ondes P et les QRS), pas d'un Mobitz 2 (**A** faux). Étiologie dégénérative fréquente (**B**), dyskaliémie à chercher (**C**), nœud sinusal fonctionnel (ondes P présentes et régulières) (**D**), indication de pacemaker si le trouble n'est pas réversible (**E**).

---

## QRM 5

Parmi les affirmations suivantes, quelles sont celles qui sont exactes ?

- A. En présence d'un bloc de branche gauche complet, la durée de QRS est > 110 ms
- B. La mesure de l'intervalle PR se fait du début de l'onde P au début du QRS
- C. Un intervalle > 160 ms définit un bloc atrioventriculaire du 1er degré
- D. L'intervalle QT normal doit être < 0,44 seconde
- E. En présence d'un bloc de branche droit, il existe un aspect rSR' en V1

**Réponse : B, D, E**

PR = début de P → début du QRS (**B**). QT normal < 0,44 s (**D**). BBD = aspect rSR' en V1 (**E**). BBG complet : QRS **> 120 ms**, pas 110 ms (**A** faux). BAV du 1er degré : PR **> 200 ms**, pas 160 ms (**C** faux).
'''

BOX_TITLES = {
    "Attention", "Pour comprendre", "Point sémantique", "À connaître",
    "Conseils d'interprétation", "Conseil d'interprétation en cas de bradycardie",
    "Conseil d'interprétation",
}


def fig_md(n, rel="./img"):
    cap = FIG_CAPTIONS.get(n, f"Fig. 15.{n}")
    fname = f"fig_15_{n}.png"
    return f"\n![{cap}]({rel}/{fname})\n\n**Fig. 15.{n}.** {cap}.\n"


def is_watermark(line):
    for pat in WATERMARK_PATTERNS:
        if re.match(pat, line, re.I):
            return True
    if PAGE_NUM_RE.match(line):
        return True
    return False


def is_ecg_garbage(line):
    s = line.strip()
    if not s:
        return True
    if s in KEEP_SHORT or s in BOX_TITLES:
        return False
    if s.startswith(("Fig.", "fig.", "Tableau", "Encadré", "•", "- ", "#", "**Rang", ">")):
        return False
    if SUBSECTION_RE.match(s) or NUM_SUBSECTION_RE.match(s):
        return False
    if s.startswith(("Item 17", "Item 18", "Cinq étiologies")):
        return False
    if s in DIAGRAM_LABELS:
        return True
    if LEAD_LINE_RE.match(s):
        return True
    letters = len(re.findall(r"[A-Za-zÀ-ÿ]", s))
    if letters < 3:
        return True
    if letters < 8 and len(s) < 28:
        if re.search(r"[▲►→←⇒=\\/\|•\*~_<>]{2,}", s):
            return True
        if re.match(r"^[\W\d_]+$", s):
            return True
        if re.match(r"^[A-Za-z]{1,3}\s*$", s):
            return True
    if letters / max(len(s), 1) < 0.30 and len(s) < 50:
        return True
    if re.match(r"^[\W\d\s\.ÏHWMflBï■□▪▫●○►▲▼]+$", s):
        return True
    if re.search(r"(tf ){2,}|t{4,}|MHt|•épolarisation|iiràiii|KillE", s):
        return True
    if "Coil de défibrillation" in s or "Désynchronisation des parois" in s:
        return True
    if "iatrioventriculaire" in s or "Siatrioventriculaire" in s:
        return True
    if s.startswith("**Rang A.** Nœud"):
        return True
    return False


def apply_rang(line):
    line = re.sub(r"^• 0 ", "• **Rang A.** ", line)
    line = line.replace("El ", "• **Rang B.** ", 1) if line.startswith("El ") else line
    for prefix, repl in (
        ("• O ", "• **Rang A.** "),
        ("• □ ", "• **Rang B.** "),
        ("• Q ", "• **Rang A.** "),
        ("• D ", "• **Rang B.** "),
        ("• El ", "• **Rang B.** "),
        ("• 0 ", "• **Rang A.** "),
    ):
        if line.startswith(prefix):
            return repl + line[len(prefix):]
    for prefix, repl in (
        ("□ ", "**Rang B.** "),
        ("O ", "**Rang A.** "),
        ("Q ", "**Rang A.** "),
        ("D ", "**Rang B.** "),
        ("0 ", "**Rang A.** "),
        ("El ", "**Rang B.** "),
    ):
        if line.startswith(prefix):
            rest = line[len(prefix):]
            if rest and rest[0].islower() and len(rest) < 12:
                break
            return repl + rest
    return line


def clean_line(line):
    line = line.strip()
    if not line:
        return None
    if is_watermark(line):
        return None
    line = line.replace("fig. 1 5", "fig. 15").replace("Fig. 1 5", "Fig. 15")
    line = line.replace("figure 1 5", "figure 15").replace("Figure 1 5", "Figure 15")
    line = line.replace("1 5.2", "15.2").replace("1 5.1", "15.1")
    line = line.replace("tableau. 15.1", "tableau 15.1")
    line = line.replace("Môbitz", "Mobitz").replace("Mòbitz", "Mobitz")
    line = line.replace("coo/ clown", "cool down")
    line = line.replace("onde 5 »", "onde δ »")
    line = line.replace("décrémentiez", "décrémentielle")
    line = line.replace("(et. supra)", "(cf. supra)")
    line = line.replace("l’ECC", "l'ECG").replace("l'ECC", "l'ECG")
    line = line.replace("négativité de DU", "négativité de D2")
    line = line.replace("dans le BBC", "dans le BBG")
    line = line.replace("aVR, aVL et aVR", "aVR, aVL et aVF")
    line = line.replace("SCAa cST", "SCA ST+")
    line = line.replace("1 20 ms", "120 ms").replace("1 10 ms", "110 ms")
    line = line.replace("1 50 bpm", "150 bpm").replace("> 1 20", "> 120")
    line = line.replace("entre 1 5 et", "entre 15 et")
    line = line.replace("3 e degré", "3e degré").replace("2 e degré", "2e degré")
    line = line.replace("1 er degré", "1er degré")
    line = line.replace("fig. 15.1 1", "fig. 15.11")
    line = line.replace("O II ", "**Rang A.** Il ").replace("□ II ", "**Rang B.** Il ")
    line = apply_rang(line)
    if is_ecg_garbage(line) and not FIG_CAPTION_RE.match(line) and not line.startswith("**Rang"):
        return None
    return line


def parse_section(raw_text, inserted_figs=None):
    if inserted_figs is None:
        inserted_figs = set()
    lines_out = []
    pending_bullet = None
    skip_table = None
    skip_encadre = None
    skip_until_real = 0
    in_box = None
    box_buf = []

    def flush_box():
        nonlocal in_box, box_buf
        if in_box and box_buf:
            body = " ".join(box_buf)
            lines_out.append(f"\n> **{in_box}.** {body}\n")
        in_box = None
        box_buf = []

    raw_lines = raw_text.splitlines()
    i = 0
    while i < len(raw_lines):
        stripped = raw_lines[i].strip()
        if stripped in ("•", "-", "–", "• "):
            pending_bullet = "• " if "•" in stripped else "- "
            i += 1
            continue
        cl = clean_line(raw_lines[i])
        i += 1
        if cl is None:
            continue
        if pending_bullet and not cl.startswith(("• ", "- ", "#", "**Rang", ">", "![")):
            cl = pending_bullet + cl
            pending_bullet = None
        else:
            pending_bullet = None

        if any(cl == s["marker"] for s in SECTIONS):
            continue

        if skip_encadre:
            if cl.startswith("Fig. 15.") or cl.startswith("1. Tachycardie sinusale") or cl.startswith("2. Fibrillation ventriculaire"):
                skip_encadre = None
            else:
                continue
        if skip_table == "15.1":
            if cl.startswith("Fig. 15.2") or cl.startswith("2. Électrogenèse"):
                skip_table = None
            else:
                continue
        if skip_table == "15.2":
            if cl.startswith("Rythme cardiaque") or cl.startswith("5.") or cl.startswith("B. Troubles"):
                skip_table = None
            else:
                continue

        mfig = FIG_CAPTION_RE.match(cl)
        if mfig:
            flush_box()
            n = int(mfig.group(1))
            if n not in inserted_figs:
                lines_out.append(fig_md(n))
                inserted_figs.add(n)
            if n == 10 and 11 not in inserted_figs:
                lines_out.append(fig_md(11))
                inserted_figs.add(11)
            skip_until_real = 3
            continue

        # Uncaptioned figures referenced in the text (extracted from PDF).
        for n in (11, 12, 28, 64):
            if n in inserted_figs:
                continue
            if re.search(rf"(?:fig\.|figure)\s*15\.{n}\b", cl, re.I) or re.search(rf"15\.{n}\b", cl):
                lines_out.append(cl)
                lines_out.append(fig_md(n))
                inserted_figs.add(n)
                cl = None
                break
        if cl is None:
            continue

        if cl.startswith("Encadré 15.1"):
            flush_box()
            lines_out.append(ENCADRE_15_1)
            skip_encadre = "15.1"
            continue
        if cl.startswith("Encadré 15.2"):
            flush_box()
            lines_out.append(ENCADRE_15_2)
            skip_encadre = "15.2"
            continue
        if cl.startswith("Tableau 15.1"):
            flush_box()
            lines_out.append(TABLE_15_1)
            skip_table = "15.1"
            continue
        if cl.startswith("Tableau 15.2"):
            flush_box()
            lines_out.append(TABLE_15_2)
            skip_table = "15.2"
            continue

        if cl in BOX_TITLES or cl.startswith("Conseil d'interprétation") or cl.startswith("Conseils d'interprétation"):
            flush_box()
            in_box = cl.rstrip(".")
            continue
        if cl.startswith("Item 17.") or cl.startswith("Item 18."):
            flush_box()
            in_box = cl.split(".")[0] + "." + cl.split(".", 1)[1].split(".")[0].strip() if cl.count(".") >= 1 else cl
            box_buf = []
            rest = cl.split(".", 2)
            if len(rest) >= 3 and rest[2].strip():
                box_buf = [rest[2].strip()]
            continue
        if cl.startswith("Cinq étiologies"):
            flush_box()
            in_box = "Cinq étiologies de sus-décalage du segment ST"
            continue

        if in_box:
            if (
                cl.startswith("• ")
                or cl.startswith("- ")
                or cl.startswith("Le bloc")
                or cl.startswith("Les tachycardies")
                or cl.startswith("Les troubles")
                or SUBSECTION_RE.match(cl)
                or NUM_SUBSECTION_RE.match(cl)
                or cl.startswith("Fig.")
                or cl.startswith("**Rang A.**")
            ):
                flush_box()
            else:
                box_buf.append(cl.lstrip("•- ").strip())
                continue

        if skip_until_real:
            skip_until_real -= 1
            if len(re.findall(r"[A-Za-zÀ-ÿ]", cl)) < 18 and not cl.startswith(("•", "-", "**Rang", "#", "Fig", "Attention", "###", "##")):
                continue

        m = SUBSECTION_RE.match(cl)
        if m and len(cl) < 140:
            flush_box()
            lines_out.append(f"\n## {m.group(1)}\n")
            continue
        m2 = NUM_SUBSECTION_RE.match(cl)
        if m2 and len(cl) < 140:
            flush_box()
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

    flush_box()
    return "\n".join(lines_out), inserted_figs


def postprocess(text):
    text = re.sub(r"\s*===== PDF PAGE \d+ =====\s*", " ", text)
    text = re.sub(r"(?<=\w)-\s+(?=[a-zàâéèêëîïôùûü])", "", text)
    fixes = [
        ("élec- trique", "électrique"),
        ("atrioven- triculaire", "atrioventriculaire"),
        ("électro- cardiogramme", "électrocardiogramme"),
        ("électrocardio- graphique", "électrocardiographique"),
        ("trans- membranaires", "transmembranaires"),
        ("myocar- diques", "myocardiques"),
        ("auto- matisme", "automatisme"),
        ("antiaryth- miques", "antiarythmiques"),
        ("dépolari- sation", "dépolarisation"),
        ("repolari- sation", "repolarisation"),
        ("ventricu- laire", "ventriculaire"),
        ("supraventricu- laire", "supraventriculaire"),
        ("tachycar- die", "tachycardie"),
        ("bradycar- die", "bradycardie"),
        ("manœuvres vaga- les", "manœuvres vagales"),
        ("hypoka- liémie", "hypokaliémie"),
        ("hyperka- liémie", "hyperkaliémie"),
        ("péricar- dite", "péricardite"),
        ("préexci- tation", "préexcitation"),
        ("pace- maker", "pacemaker"),
        ("stimu- lation", "stimulation"),
        ("hypertro- phie", "hypertrophie"),
        ("embolie pulmo- naire", "embolie pulmonaire"),
        ("syndrome corona- rien", "syndrome coronarien"),
        ("**Rang A.** II ", "**Rang A.** Il "),
        ("**Rang B.** II ", "**Rang B.** Il "),
        ("O II ", "**Rang A.** Il "),
        ("bloquée innopinée", "bloquée inopinée"),
        ("semblable àu sus-décalage présent dans le SC", "semblable au sus-décalage du SCA ST+"),
        ("vers lejraùtians miroir", "vers le haut, sans miroir"),
        ("Ellesfont", "Elles font"),
        ("heurtais", "heure, mais"),
        ("Vtprtxqu'une", "à tort qu'une"),
        ("en V2-V3-w\\ O", "en V2-V3."),
        ("<£► Elles", "**Rang B.** Elles"),
        ("<£►", ""),
        ("fJ 266", "266"),
        ("1 162", "162"),
        ("1 10°", "110°"),
        ("1 10 et", "110 et"),
        ("1 30 à", "130 à"),
        ("15.1 1", "15.11"),
        ("RsR1", "rSR'"),
        ("dans le BBC", "dans le BBG"),
        (" 'i i ü", ""),
        ("fig. 1 5.62", "fig. 15.62"),
        ("(fig. 15.61 et 1 5.62)", "(fig. 15.61 et 15.62)"),
        ("ST en V1 et V2, onde T négative en D1, aVL, V6. L'étiologie", "L'étiologie"),
    ]
    for old, new in fixes:
        text = text.replace(old, new)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"Ce livre a été acheté.*?https://t\.me/Faille_V2\s*", " ", text, flags=re.S)
    return text


def merge_paragraphs(body):
    paragraphs = []
    buf = []

    def flush():
        if buf:
            paragraphs.append(" ".join(buf))
            buf.clear()

    for line in body.splitlines():
        if not line.strip():
            flush()
            continue
        if line.startswith("|"):
            flush()
            if paragraphs and paragraphs[-1].startswith("|"):
                paragraphs[-1] += "\n" + line
            else:
                paragraphs.append(line)
            continue
        if line.startswith(">"):
            flush()
            if paragraphs and paragraphs[-1].startswith(">"):
                paragraphs[-1] += "\n" + line
            else:
                paragraphs.append(line)
            continue
        if (
            line.startswith(("#", "##", "###", "**Tableau", "**Encadré", "- ", "• ", "!", "---"))
            or re.match(r"^\s+- ", line)
            or line.startswith("![")
        ):
            flush()
            paragraphs.append(line)
            continue
        if not buf and paragraphs and paragraphs[-1].startswith(("• ", "- ")):
            last = paragraphs[-1].rstrip()
            nxt = line.strip()
            if last.endswith((";", ",", ":", "»", "à", "de", "du", "et", "ou")) or nxt[:1].islower():
                paragraphs[-1] = last + " " + nxt
                continue
        buf.append(line.strip())
    flush()
    return "\n\n".join(p for p in paragraphs if p)


def subfile_header(cfg):
    return (
        f"# {cfg['title']}\n\n"
        f"> Retour à l'index : [Item 231 — Électrocardiogramme](./231_ECG.md)  \n"
        f"> Collège CNEC / SFC · 3e éd. · p. 337–387 · Partie III — Rythmologie\n\n"
        f"{cfg['rang']}\n\n---\n\n"
    )


def body_chunk(text):
    first = text.find("A. ECG normal")
    second = text.find("A. ECG normal", first + 1) if first != -1 else -1
    start = second if second != -1 else first
    if start == -1:
        start = text.find("1. Notions succinctes")
    end_candidates = []
    for token in ("\nPoints\n", "\nRéflexes transversalité", "\n► Entraînement"):
        p = text.find(token, start if start != -1 else 0)
        if p != -1:
            end_candidates.append(p)
    end = min(end_candidates) if end_candidates else len(text)
    # Hard stop before Item 237
    leak = text.find("Item 237", start if start != -1 else 0)
    if leak != -1 and leak < end:
        end = leak
    leak2 = text.find("===== PDF PAGE 418", start if start != -1 else 0)
    if leak2 != -1 and leak2 < end:
        end = leak2
    return text[start:end]


def split_sections(chunk):
    positions = []
    for cfg in SECTIONS:
        idx = chunk.find(cfg["marker"])
        if idx == -1:
            raise RuntimeError(f"Missing split marker: {cfg['marker']}")
        positions.append((idx, cfg))
    positions.sort(key=lambda x: x[0])
    parts = {}
    for i, (idx, cfg) in enumerate(positions):
        stop = positions[i + 1][0] if i + 1 < len(positions) else len(chunk)
        parts[cfg["key"]] = chunk[idx:stop]
    return parts


def build_course():
    text = SRC.read_text(encoding="utf-8")
    chunk = body_chunk(text)
    parts = split_sections(chunk)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inserted = set()
    sizes = {}
    for cfg in SECTIONS:
        raw = parts[cfg["key"]]
        body, inserted = parse_section(raw, inserted)
        body = postprocess(body)
        body = merge_paragraphs(body)
        body = re.sub(rf"^## {re.escape(cfg['marker'])}\s*", "", body.lstrip(), count=1)
        body = re.sub(rf"^{re.escape(cfg['marker'])}\s*", "", body.lstrip(), count=1)
        body = re.sub(r"ST en V1 et V2, onde T négative en D1, aVL, V6\.\s*", "", body)
        body = re.sub(r"\nOrientation de l’influx électrique.*?(?=\n!\[)", "\n", body)
        content = subfile_header(cfg) + body
        path = OUT_DIR / cfg["file"]
        path.write_text(content, encoding="utf-8")
        sizes[cfg["file"]] = path.stat().st_size
        print(f"Written {path} ({sizes[cfg['file']]} bytes)")

    index = INDEX_HEADER + INDEX_FOOTER
    idx_path = OUT_DIR / "231_ECG.md"
    idx_path.write_text(index, encoding="utf-8")
    print(f"Written {idx_path} ({idx_path.stat().st_size} bytes)")
    return sizes


def build_qi():
    QI_OUT.parent.mkdir(parents=True, exist_ok=True)
    QI_OUT.write_text(QI_CONTENT, encoding="utf-8")
    print(f"Written {QI_OUT} ({QI_OUT.stat().st_size} bytes)")


def _exact_fig_hits(page, n):
    """Prefix-safe search: Fig. 15.1 must not match Fig. 15.10."""
    hits = []
    for label in (f"Fig. 15.{n}", f"fig. 15.{n}", f"Fig.15.{n}"):
        for r in page.search_for(label):
            clip = fitz.Rect(r.x0, r.y0 - 2, min(page.rect.width, r.x1 + 36), r.y1 + 2)
            nearby = page.get_text("text", clip=clip).replace("\n", " ")
            m = re.search(r"15\.(\d+)", nearby)
            if m and int(m.group(1)) != n:
                continue
            hits.append(r)
    return hits


def extract_figures():
    if not PDF.exists():
        print(f"PDF not found: {PDF}")
        return []
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF)

    captions = {}  # n -> (page_idx, rect, is_caption)
    for i in range(366, min(417, len(doc))):
        page = doc[i]
        for b in page.get_text("blocks"):
            t = b[4].replace("\n", " ").strip()
            m = re.match(r"^Fig\.\s*15\.(\d+)", t)
            if not m:
                continue
            n = int(m.group(1))
            rect = fitz.Rect(b[0], b[1], b[2], b[3])
            prev = captions.get(n)
            if prev is None or rect.y0 > prev[1].y0:
                captions[n] = (i, rect, True)

    # Fallbacks for figures whose caption block does not start with "Fig."
    for n in range(1, 65):
        if n in captions:
            continue
        best = None
        for i in range(366, min(417, len(doc))):
            hits = _exact_fig_hits(doc[i], n)
            if not hits:
                continue
            r = max(hits, key=lambda x: x.y0)
            if best is None or r.y0 > best[1].y0:
                best = (i, r, False)
        if best:
            page = doc[best[0]]
            r = best[1]
            nearby = page.get_text(
                "text",
                clip=fitz.Rect(max(0, r.x0 - 8), r.y0 - 2, min(page.rect.width, r.x1 + 60), r.y1 + 2),
            ).strip()
            is_cap = nearby.startswith("Fig.") or nearby.startswith("fig.")
            captions[n] = (best[0], r, is_cap)

    # Special placements (no caption / ECG below stem / QI crop)
    special = {
        11: (378, 490, 810),   # ECG BBD under fig 15.10 on p.379
        12: (379, 165, 688),   # ECG BBG above fig 15.13 on p.380
        28: (388, 655, 812),   # mechanism diagram p.389
        63: (415, 400, 678),   # QRM 2 ECG p.416
        64: (416, 250, 478),   # QRM 4 ECG below stem p.417
    }
    written = []
    for n in range(1, 65):
        page_idx = None
        clip = None
        if n in special and n not in captions:
            page_idx, y0, y1 = special[n]
            page = doc[page_idx]
            clip = fitz.Rect(18, y0, page.rect.width - 18, y1)
        elif n in captions:
            page_idx, rect, is_caption = captions[n]
            page = doc[page_idx]
            if n == 64 and not is_caption:
                clip = fitz.Rect(18, 250, page.rect.width - 18, 478)
            elif is_caption:
                y1 = min(page.rect.height - 40, rect.y1 + 22)
                y0 = max(36, rect.y0 - 330)
                # Do not overlap a previous caption on the same page
                same = [
                    (m, captions[m][1])
                    for m in captions
                    if captions[m][0] == page_idx and m != n and captions[m][2]
                ]
                for _, other in same:
                    if other.y1 < rect.y0:
                        y0 = max(y0, other.y1 + 6)
                clip = fitz.Rect(16, y0, page.rect.width - 16, y1)
            else:
                y1 = min(page.rect.height - 40, rect.y1 + 20)
                y0 = max(36, rect.y0 - 300)
                clip = fitz.Rect(16, y0, page.rect.width - 16, y1)
        elif n in special:
            page_idx, y0, y1 = special[n]
            page = doc[page_idx]
            clip = fitz.Rect(18, y0, page.rect.width - 18, y1)
        else:
            continue

        # Skip in-text-only hits that are not real captions (except specials).
        if n in captions and not captions[n][2] and n not in special:
            continue

        if clip.y1 - clip.y0 < 40:
            continue
        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
        out = IMG_DIR / f"fig_15_{n}.png"
        pix.save(str(out))
        written.append(n)
        print(f"Figure 15.{n} -> {out.name} ({out.stat().st_size} bytes) page {page_idx + 1}")

    # Specials always overwrite (correct crop).
    for n, (page_idx, y0, y1) in special.items():
        page = doc[page_idx]
        clip = fitz.Rect(18, y0, page.rect.width - 18, y1)
        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
        out = IMG_DIR / f"fig_15_{n}.png"
        pix.save(str(out))
        if n not in written:
            written.append(n)
        print(f"Figure 15.{n} (special) -> {out.name} ({out.stat().st_size} bytes) page {page_idx + 1}")

    doc.close()
    return sorted(set(written))


def update_readme():
    text = README.read_text(encoding="utf-8")
    row = (
        "| Fait | 231 Électrocardiogramme | "
        "[III_Rythmologie/231_ECG.md](./III_Rythmologie/231_ECG.md) "
        "(index + 7 sous-fichiers) |\n"
    )
    if "231 Électrocardiogramme" in text or "231_ECG.md" in text:
        print("README already contains item 231")
        return
    if "| Fait | 232 Fibrillation atriale |" in text:
        text = text.replace(
            "| Fait | 232 Fibrillation atriale |",
            row.rstrip("\n") + "\n| Fait | 232 Fibrillation atriale |",
        )
    else:
        text = text.replace(
            "| À faire | … | lots suivants |",
            row + "| À faire | … | lots suivants |",
        )
    README.write_text(text, encoding="utf-8")
    print("Updated README.md")


def verify():
    idx = OUT_DIR / "231_ECG.md"
    ok = True
    if not idx.exists():
        print("FAIL: index missing")
        return False
    idx_text = idx.read_text(encoding="utf-8")
    for cfg in SECTIONS:
        if cfg["file"] not in idx_text:
            print(f"FAIL: index missing link to {cfg['file']}")
            ok = False
        p = OUT_DIR / cfg["file"]
        if not p.exists():
            print(f"FAIL: missing {cfg['file']}")
            ok = False
            continue
        sz = p.stat().st_size
        if sz < 3000:
            print(f"FAIL: {cfg['file']} too small ({sz} bytes)")
            ok = False
        body = p.read_text(encoding="utf-8")
        if "Item 237" in body and "Réflexes" not in body.split("Item 237")[0][-80:]:
            # allowed only as reflex
            if "Palpitations" in body and "# Item 237" in body:
                print(f"FAIL: Item 237 leaked into {cfg['file']}")
                ok = False
        if "Vignette clinique" in body.split("# I")[0] if False else False:
            pass
    combined = sum((OUT_DIR / c["file"]).stat().st_size for c in SECTIONS if (OUT_DIR / c["file"]).exists())
    combined += idx.stat().st_size
    figs = list(IMG_DIR.glob("fig_15_*.png"))
    print(f"Combined course: {combined} bytes")
    print(f"Figures: {len(figs)} PNGs")
    if combined < 40_000:
        print("FAIL: combined course < 40 KB")
        ok = False
    if len(figs) < 40:
        print("FAIL: fewer than 40 figures")
        ok = False
    for n in (63, 64):
        if not (IMG_DIR / f"fig_15_{n}.png").exists():
            print(f"FAIL: missing QI figure 15.{n}")
            ok = False
    qi = QI_OUT.read_text(encoding="utf-8") if QI_OUT.exists() else ""
    for ans in ("**Réponse : B, D**", "**Réponse : A, E**", "**Réponse : A, B, D**",
                "**Réponse : B, C, D, E**", "**Réponse : B, D, E**"):
        if ans not in qi:
            print(f"FAIL: QI missing {ans}")
            ok = False
    if "Vignette" in idx_text:
        print("WARN: vignette present in index (source had none)")
    if not ok:
        print("WARN: verification thresholds not met")
    else:
        print("VERIFY OK")
    return ok


def main():
    build_course()
    build_qi()
    extract_figures()
    update_readme()
    verify()


if __name__ == "__main__":
    main()
