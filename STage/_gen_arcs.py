# -*- coding: utf-8 -*-
"""Génère les ARC stage IMM + corrections collège R2C."""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "ARC"
OUT.mkdir(exist_ok=True)

ARCS = []


def add(**kw):
    ARCS.append(kw)


# ---------- 01 ----------
add(
    n=1,
    slug="01-douleur-thoracique-pied",
    title="Douleur thoracique — triage PIED",
    theme="Douleur thoracique",
    items=["230", "339", "226", "235"],
    niveau="Essentiel stage / oral",
    vignette="""Homme de 58 ans, tabagique 30 PA, HTA, diabète. Aux urgences à 2 h du matin pour oppression rétrosternale depuis 45 minutes, irradiant au bras gauche, sueurs, nausées. PA 145/88, FC 92/min, SpO2 97 % AA, apyrétique. Auscultation cardio-pulmonaire sans particularité. Pas d’œdème. Jambe gauche normale.""",
    questions=[
        ("I — Interrogatoire", "Quels éléments caractériser (LITHIASE) ? Quels FDR / traitements / allergies à chercher ?"),
        ("II — Examen", "Quels signes de gravité et différentiels cliniques rechercher ?"),
        ("III — Hypothèses", "Hiérarchise les hypothèses (PIED + autres)."),
        ("IV — Examens", "Quels examens en 1re intention, dans quel ordre ?"),
        ("V — Diagnostic", "Que décide-t-on avant même le résultat de la troponine ?"),
        ("VI — CAT", "Conduite immédiate ?"),
    ],
    correction="""**I.** Localisation rétrosternale, intensité EVA, type oppressif, horaire (début brutal / durée > 20 min), irradiation, facteurs aggravants/améliorants (effort, TNT, respiration, antéflexion), signes associés (sueurs, nausées, dyspnée, syncope). FDR : tabac, HTA, diabète, dyslipidémie, ATCD familiaux. Allergie iode. Traitements (aspirine, BB…).

**II.** Gravité : détresse, choc, SpO2 basse, asymétrie tensionnelle, souffle d’IA nouveau, signes d’IVD (TJ, RHJ), frottement, jambe rouge. Pouls périphériques.

**III. PIED** : Péricardite, Infarctus/SCA, Embolie pulmonaire, Dissection. Puis pneumothorax, pleurésie, digestif, anxiété (dernier).

**IV.** **ECG avant troponine**, idéalement < 10 min, **18 dérivations** si douleur. Puis troponine us (répétée), bio, ± radio thorax si pas STEMI évident. ETT / angioscanner / coro selon orientation.

**V.** Si ST+ systématisé + miroir → **STEMI** : reperfusion urgente **sans attendre** la troponine.

**VI.** Scope, O2 si besoin, voie veineuse, aspirine (sauf CI), appeler le 15 / filière SCA, antalgie. Ne pas rassurer « c’est gastrique » sans ECG.""",
    points=[
        "Urgences CV = **PIED** (item 230).",
        "**ECG avant troponine** ; 18D si douleur thoracique.",
        "ST+ persistant > 20 min de douleur → reperfusion urgente.",
        "Dissection : douleur déchirante postérieure, asymétrie TA, souffle d’IA.",
        "Péricardite : antéflexion, frottement, ST diffus concave sans miroir, sous-PQ.",
    ],
    indisp=["Ne pas appeler le 15 / retarder l’ECG devant une douleur thoracique suspecte."],
    inacc=["Attendre la troponine pour traiter un ST+.", "Éliminer un SCA sur un ECG unique normal."],
    message="Devant douleur thoracique : **ECG immédiat**, penser **PIED**, ne jamais attendre la tropo pour un STEMI.",
)

# ---------- 02 ----------
add(
    n=2,
    slug="02-sca-stemi",
    title="SCA ST+ — reperfusion",
    theme="SCA",
    items=["339", "230", "330"],
    niveau="Essentiel USIC",
    vignette="""Femme de 64 ans, HTA, dyslipidémie. Douleur rétrosternale depuis 90 minutes. ECG : sus-ST 3 mm en V2–V4 avec miroir en DII–DIII–aVF. PA 130/80, FC 88, SpO2 96 %. Pas de souffle. Troponine non encore revenue.""",
    questions=[
        ("I–II", "Résume motif + éléments cliniques clés."),
        ("III", "Diagnostic ECG ? Territoire ?"),
        ("IV", "Examens / infos indispensables avant coro ?"),
        ("V–VI", "CAT préhospitalière / urgences et délais de reperfusion ? Traitement antithrombotique de base ?"),
    ],
    correction="""**Diagnostic :** STEMI **antérieur** (V2–V4) — urgence de reperfusion.

**CAT :** filière SCA, aspirine + inhibiteur P2Y12 (ticagrelor/prasugrel selon contexte, sinon clopidogrel), anticoagulation parentérale selon protocole, antalgie, scope. **PCI primaire** = stratégie préférentielle ; délais collège : idéalement **PCI < 90 min** (selon filière ; connaître aussi fenêtre fibrinolyse si PCI impossible dans les délais).

**Ne pas attendre** la troponine. Chercher complications précoces (FV, BAV, choc, rupture).

**BASIC** en prévention secondaire après SCA : BB si indiqué, Antiagrégant, Statine, IEC/ARA2, Contrôle FDR.""",
    points=[
        "STEMI = ST+ systématisé + miroir ; reperfusion **urgente**.",
        "Délais PCI / fibrinolyse : item 339 — à coller.",
        "DAPT post-stent : connaître durées selon risque ischémique/hémorragique.",
        "LDL cible prévention secondaire / très haut risque : **< 0,55 g/L**.",
    ],
    indisp=["Reconnaître un STEMI et déclencher la reperfusion."],
    inacc=["Attendre la tropo.", "Confondre péricardite (ST diffus sans miroir) et STEMI."],
    message="STEMI = **montre** : filière + antiagrégants + PCI, tropo secondaire.",
)

# ---------- 03 ----------
add(
    n=3,
    slug="03-sca-nstemi",
    title="SCA ST− / NSTEMI — stratification",
    theme="SCA",
    items=["339", "330"],
    niveau="Essentiel",
    vignette="""Homme de 72 ans, diabétique, AOMI. Douleur thoracique d’effort depuis 48 h, épisode au repos de 30 min hier soir. ECG : sous-ST 1,5 mm V4–V6, ondes T négatives. Troponine us élevée ×2. PA 110/70, FC 78, pas de signe de choc. Créatinine 110 µmol/L.""",
    questions=[
        ("III", "STEMI ou NSTEMI ? Pourquoi ?"),
        ("IV", "Quels critères de haut risque poussent à une coro précoce ?"),
        ("VI", "Traitement initial ? Objectifs secondaires ?"),
    ],
    correction="""**NSTEMI** : ischémie ECG sans ST+ persistant + tropo élevée.

Stratifier le risque (instabilité, douleur récurrente, sous-ST profond, tropo, diabète, IR, GRACE…). Coro selon urgence (immédiate si instable, précoce sinon).

Traitement : AAP double (aspirine + P2Y12), anticoagulant, BB si besoin, statine forte dose, IEC. Surveillance USIC si haut risque.

Piège : angor instable = même famille SCA ST− avec tropo négative — ne pas banaliser.""",
    points=[
        "SCA ST− = NSTEMI ou angor instable selon tropo.",
        "Instabilité hémodynamique / électrique / douleur réfractaire → coro **urgente**.",
        "DAPT + anticoagulation selon protocole SCA.",
    ],
    indisp=["Stratifier le risque avant de « surveiller tranquillement »."],
    inacc=["Rassurer parce que « pas de ST+ »."],
    message="Pas de ST+ ≠ bénin : **tropo + risque** décident la vitesse de la coro.",
)

# ---------- 04 ----------
add(
    n=4,
    slug="04-sca-vd-choc",
    title="IDM inférieur + extension VD",
    theme="SCA",
    items=["339", "231"],
    niveau="Piège USIC",
    vignette="""Homme de 60 ans. Douleur + ST+ en DII–DIII–aVF. PA 85/55, FC 50, poumons clairs, jugulaires turgescentes. V3R–V4R : ST+. Internat propose des dérivés nitrés IV pour « OAP ».""",
    questions=[
        ("III", "Que suspectes-tu ? Triade ?"),
        ("IV", "Quelles dérivations manquent souvent ?"),
        ("VI", "Que faire / ne pas faire ?"),
    ],
    correction="""**IDM inférieur + extension VD.** Triade : hypotension + poumons clairs + TJ.

Enregistrer **V3R–V4R**. Remplissage prudent, reperfusion, éviter vasodilatateurs/nitrés et diurétiques en 1re intention (aggravent la précharge VD).

BAV nodal fréquent dans IDM inférieur → atropine si besoin.""",
    points=[
        "IDM inférieur → toujours penser VD (V3R–V4R).",
        "Triade IDM VD : hypoTA + poumons clairs + TJ.",
        "Nitrés **contre-indiqués** si IDM VD.",
    ],
    indisp=["Suspecter l’extension VD devant un IDM inférieur hypotendu."],
    inacc=["Nitrés / diurétiques en 1re intention sur IDM VD."],
    message="IDM inférieur hypotendu poumons clairs = **VD** jusqu’à preuve du contraire.",
)

# ---------- 05 ----------
add(
    n=5,
    slug="05-ep-intermediaire",
    title="Embolie pulmonaire — algo",
    theme="EP",
    items=["226", "203", "230"],
    niveau="Essentiel",
    vignette="""Femme de 45 ans, pilule, voyage avion 12 h il y a 3 jours. Dyspnée brutale, douleur pleurale droite, SpO2 93 %, PA 125/75, FC 110. Mollet gauche chaud, douloureux. Radio thorax presque normale. D-dimères demandés « pour gagner du temps ».""",
    questions=[
        ("III", "Probabilité clinique ? Score ?"),
        ("IV", "D-dimères utiles ici ? Quel examen de confirmation ?"),
        ("VI", "CAT selon stratification ?"),
    ],
    correction="""Probabilité **intermédiaire/forte** (pilule, voyage, tachycardie, dyspnée, TVP clinique) → **D-dimères inutiles** si forte ; si intermédiaire selon algo local, mais ne pas retarder. Confirmation : **angioscanner** (ou scintigraphie si CI). EDVMI utile.

Stratification : choc/hypotension = haut risque → USIC ± fibrinolyse. Sinon sPESI + signes VD (ETT, bio) pour intermédiaire haut/faible.

Traitement : AOD ou HBPM→AVK selon contexte ; HBPM prolongée si cancer.""",
    points=[
        "Triade Virchow ; TVP → EP fréquente.",
        "D-dimères **seulement** si proba faible/intermédiaire.",
        "Haut risque = choc/hypotension.",
        "Durée anticoagulation : 3 mois si facteur majeur transitoire, plus long si non provoquée.",
    ],
    indisp=["Évoquer EP devant dyspnée + radio normale + contexte."],
    inacc=["D-dimères si proba forte.", "Retarder l’angio devant une forte suspicion."],
    message="EP : **proba clinique d’abord**, D-dimères ensuite seulement si utiles.",
)

# ---------- 06 ----------
add(
    n=6,
    slug="06-ep-haut-risque",
    title="EP à haut risque — choc",
    theme="EP",
    items=["226", "331"],
    niveau="Urgence",
    vignette="""Homme de 70 ans, cancer colorectal. Dyspnée brutale, PA 75/40, marbrures, SpO2 88 %, TJ. ECG : tachycardie sinusale, S1Q3. ETT au lit : VD dilaté, septum paradoxe.""",
    questions=[
        ("V", "Stratification ?"),
        ("VI", "Lieu + traitement ? Rôle de la fibrinolyse ?"),
    ],
    correction="""**EP haut risque** (choc/hypotension + signes VD). USIC/réa, anticoagulation IV (HNF souvent), **fibrinolyse** si pas de CI majeure, discussion embolectomie/assistance si échec.

Ne pas perdre de temps en examens non nécessaires si le tableau est clair.""",
    points=[
        "Haut risque EP = instabilité hémodynamique.",
        "Fibrinolyse = option de sauvetage.",
        "Cancer : HBPM souvent préférées au long cours.",
    ],
    indisp=["Reconnaître le choc obstructif sur EP."],
    inacc=["Laisser en salle normale « en attendant l’angio » sans support."],
    message="EP + choc = **réa + anticoag + fibrinolyse** (sauf CI).",
)

# ---------- 07 ----------
add(
    n=7,
    slug="07-fa-anticoagulation",
    title="FA — CHA₂DS₂-VA et ACO",
    theme="FA",
    items=["232", "330"],
    niveau="Essentiel R2C",
    vignette="""Homme de 78 ans, HTA, diabète, AVC ischémique il y a 2 ans. FA permanente découverte, FC 78, asymptomatique. ETT : FEVG 55 %, OG dilatée. Créatinine normale. HAS-BLED 2.""",
    questions=[
        ("III", "Calculate CHA₂DS₂-VA (CNEC 3e éd.)."),
        ("VI", "Indication d’ACO ? AVK ou AOD ? Objectif FC ?"),
    ],
    correction="""Score (sans sexe) : C1 AVC=2, H=1, A âge≥75=2, D=1, V=0, A âge 65–74=0 → **CHA₂DS₂-VA ≥ 2** → **ACO indiqué**.

Préférer **AOD** sauf valve mécanique / RM modéré-sévère. Contrôle FC (BB, digoxine, inhib. calcique non dihydro selon FEVG). Traiter FDR.

Piège : ancienne CHA₂DS₂-VASc avec point femme — **CNEC = CHA₂DS₂-VA**.""",
    points=[
        "CHA₂DS₂-VA : 0 = pas d’ACO, 1 = discussion, ≥2 = ACO.",
        "AOD CI si prothèse mécanique ou sténose mitrale significative.",
        "Contrôle FC vs rythme selon symptômes / cœur structurel.",
    ],
    indisp=["Savoir calculer et indiquer l’ACO."],
    inacc=["Oublier l’ACO après AVC sur FA.", "AOD sur valve mécanique."],
    message="FA = rythme **et** risque embolique : **CHA₂DS₂-VA → ACO**.",
)

# ---------- 08 ----------
add(
    n=8,
    slug="08-fa-instable",
    title="FA rapide mal tolérée",
    theme="FA",
    items=["232", "231"],
    niveau="USIC",
    vignette="""Femme de 82 ans. Palpitations + dyspnée. PA 80/50, FC 165 irrégulière, crépitants, SpO2 90 %. ECG : FA à QRS fins. Début inconnu.""",
    questions=[
        ("V", "Contrôle FC ou cardioversion ?"),
        ("VI", "Anticoagulation autour de la CV ?"),
    ],
    correction="""**Instabilité** (choc, OAP, ischémie) → **cardioversion électrique** en urgence, ne pas « attendre le ralentissement ».

Si FA > 48 h ou durée inconnue : anticoaguer ; ETO pour exclure thrombus si CV programmée sans 3 semaines d’ACO. En urgence vitale : CV quand même + ACO.

Contrôle FC si stable (BB IV, digoxine si IC…).""",
    points=[
        "FA mal tolérée → CVE urgente.",
        "Règle 48 h / ETO / 3 semaines d’ACO.",
        "QRS fins irréguliers = FA jusqu’à preuve du contraire.",
    ],
    indisp=["Reconnaître l’indication de CVE."],
    inacc=["Persister à ralentir une FA en choc."],
    message="FA + instabilité = **choc électrique**, discussion anticoag en parallèle.",
)

# ---------- 09 ----------
add(
    n=9,
    slug="09-endocardite-suspicion",
    title="Endocardite — fièvre + souffle",
    theme="Endocardite",
    items=["152", "233IM"],
    niveau="Essentiel",
    vignette="""Homme de 55 ans, porteurs de bioprothèse aortique. Fièvre 38,8 °C depuis 8 jours, frissons. Nouveau souffle d’IA. Purpura jambier. CRP élevée. Internat veut « commencer amox pour pneumopathie » avant les hémocultures.""",
    questions=[
        ("III", "Pourquoi EI jusqu’à preuve du contraire ?"),
        ("IV", "Quels examens avant ATB ?"),
        ("VI", "Principes thérapeutiques ?"),
    ],
    correction="""**Fièvre + prothèse / souffle / emboles cutanés** = EI. Hémocultures **avant** ATB (sauf choc septique ultra-sévère avec prélèvements immédiats). ETT puis **ETO**. Critères de Duke. Chercher porte d’entrée.

ATB IV prolongée (4–6 sem), bactéricide, adaptée. Discuter chirurgie si IC, infection non contrôlée, risque embolique élevé. Heart Team.""",
    points=[
        "Haut risque EI : prothèses (TAVI inclus), ATCD EI, cyanogène, matériel réparé récent/shunt.",
        "Hémocultures + écho = piliers.",
        "Staph = germe le plus fréquent.",
        "Indications chir : hémodynamiques, infectieuses, emboliques.",
    ],
    indisp=["Évoquer EI si fièvre + souffle / cardiopathie à risque / embol."],
    inacc=["ATB avant hémocultures (hors extrême urgence).", "Ignorer fièvre chez porteur de prothèse."],
    message="Fièvre + valve = **hémocultures puis ETT/ETO**, ATB après.",
)

# ---------- 10 ----------
add(
    n=10,
    slug="10-endocardite-complications",
    title="Endocardite — complications",
    theme="Endocardite",
    items=["152", "236"],
    niveau="Hospitalier",
    vignette="""Patiente de 68 ans, EI mitrale à streptocoque en ATB depuis J5. Apparition d’un BAV 2 Mobitz 2, OAP, végétation 12 mm avec nouvelle IM sévère.""",
    questions=[
        ("III", "Quelles complications ?"),
        ("VI", "Que discuter en Heart Team ?"),
    ],
    correction="""Complications : **abcès septal** (BAV), **IC** sur IM aiguë, végétation emboligène. Indication chirurgicale probable (hémodynamique + infectieuse + embolique). Imagerie (ETO, scanner/TEP selon besoin). Ne pas attendre l’échec complet de l’ATB si instable.""",
    points=[
        "BAV nouveau sous EI → abcès jusqu’à preuve du contraire.",
        "Embolies, IC, infection persistante = flags chirurgicaux.",
    ],
    indisp=["Reconnaître les indications opératoires en phase active."],
    inacc=["Retarder la discussion chirurgicale devant IC / BAV / gros végétations."],
    message="EI qui se complique = **chirurgie + ATB**, pas ATB seule.",
)

# ---------- 11 ----------
add(
    n=11,
    slug="11-ra-serre",
    title="Rétrécissement aortique serré",
    theme="Valvulopathies",
    items=["233RA", "238"],
    niveau="Consult + hospit",
    vignette="""Homme de 79 ans. Dyspnée d’effort, lipothymies à la marche, angor. Souffle systolique rude 4/6 au foyer aortique irradiant aux carotides, B2 diminué. ETT : Vmax Ao 4,5 m/s, surface 0,7 cm², FEVG 55 %.""",
    questions=[
        ("III", "Sévérité ? Symptômes clés ?"),
        ("VI", "Surveillance ou intervention ? TAVI vs chirurgie ?"),
    ],
    correction="""**RA serré symptomatique** (dyspnée, syncope/lipothymie, angor) → indication de remplacement (chirurgie ou **TAVI** selon âge/risque/anatomie, Heart Team).

Éviter vasodilatateurs/hypotenseurs brutaux. Éducation : syncope d’effort = urgence. Bilan pré-TAVI : scanner, coronaires.""",
    points=[
        "Triade RA : dyspnée, angor, syncope.",
        "Serré : critères écho (Vmax, gradient, surface) — plusieurs paramètres.",
        "Symptomatique serré → intervention.",
        "TAVI si âge élevé / haut risque / anatomie favorable.",
    ],
    indisp=["Ne pas laisser un RA serré symptomatique en « surveillance seule »."],
    inacc=["Effort maximal / stress test dangereux sans avis si syncope d’effort."],
    message="RA serré + symptômes = **valve** (chir ou TAVI), pas d’attente.",
)

# ---------- 12 ----------
add(
    n=12,
    slug="12-im-indication",
    title="Insuffisance mitrale — quand opérer",
    theme="Valvulopathies",
    items=["233IM", "234"],
    niveau="Essentiel",
    vignette="""Femme de 62 ans, prolapsus mitral. Dyspnée NYHA II–III. Souffle holosystolique apexo-axillaire. ETT : IM grade III–IV primaire, FEVG 55 %, DTS-VG 42 mm, PAPS 55 mmHg. Pas de FA.""",
    questions=[
        ("III", "Primaire ou secondaire ?"),
        ("VI", "Indication opératoire ? Plastie vs remplacement ?"),
    ],
    correction="""**IM primaire** significative symptomatique → chirurgie, **plastie** préférée si prolapsus. Même asymptomatique : opérer si FEVG ≤ 60 %, DTS ≥ 40 mm, HTP, FA…

IM secondaire : traiter d’abord l’IC ; clip percutané sélectionné.

Coronarographie préop si FDR/âge.""",
    points=[
        "Opérer IM importante symptomatique (III–IV).",
        "Asymptomatique : seuils FEVG/DTS/PAPS/FA.",
        "Plastie > remplacement si possible.",
    ],
    indisp=["Savoir les indications chirurgicales IM primaire."],
    inacc=["Oublier l’éducation EI / fièvre chez patient avec IM.", "Ne pas référer un IM symptomatique."],
    message="IM primaire sévère + symptômes (ou retentissement écho) = **chirurgie, plastie d’abord**.",
)

# ---------- 13 ----------
add(
    n=13,
    slug="13-oap-ic-aigue",
    title="OAP — IC aiguë",
    theme="IC",
    items=["234", "203"],
    niveau="USIC",
    vignette="""Homme de 75 ans, HFrEF connue. Dyspnée brutale, orthopnée, TA 180/100, FC 110, SpO2 88 %, crépitants bilatéraux, œdèmes. ECG : sinusal. Tropo peu élevée. K+ 3,3 ; créat 130.""",
    questions=[
        ("III", "Congestion et/ou bas débit ?"),
        ("IV", "Examens ? Facteurs déclenchants ?"),
        ("VI", "CAT urgente ?"),
    ],
    correction="""**OAP hypertensif congestif** (pas de choc). O2 / VNI si besoin, **diurétique de l’anse IV**, dérivés nitrés si PA élevée et pas de CI, position demi-assise. Chercher trigger (infection, FA, ischémie, observance, HTA). BNP/ETT. Surveiller diurèse, poids, K+, créat.

Éviter AINS. Pas de vérapamil/diltiazem / flécaïne si HFrEF.""",
    points=[
        "IC aiguë = congestion ± bas débit + trigger.",
        "OAP = urgence : O2/VNI, diurétique, nitrés si HTA.",
        "CHAMPIT pour triggers (selon mnémo collège/USIC).",
    ],
    indisp=["Savoir la CAT OAP.", "Chercher un facteur déclenchant."],
    inacc=["AINS ; inhib. calcique brady / antiarythmiques I dans HFrEF."],
    message="OAP : **position + O2/VNI + diurétique ± nitrés**, puis trouver le trigger.",
)

# ---------- 14 ----------
add(
    n=14,
    slug="14-hfref-4-piliers",
    title="HFrEF — traitement de fond",
    theme="IC",
    items=["234"],
    niveau="Sortie / R2C",
    vignette="""Femme de 68 ans. HFrEF post-IDM, FEVG 32 %, NYHA II, euvolemic sous furosémide 40 mg. Sortie d’hospitalisation. Pas d’hyperK, créat OK, PA 118/70.""",
    questions=[
        ("VI", "Quelles classes « pronostiques » instaurer ? Rôle du diurétique ?"),
    ],
    correction="""**4 piliers HFrEF** : IEC/ARNI + BB + ARM + **SGLT2i (gliflozine)**. Diurétique d’anse = congestion (symptomatique), **pas** un 5e pilier pronostique.

Éducation : régime pauvre en sel, poids quotidien, vaccins, activité adaptée. DAI/CRT selon indications (FEVG, QRS, BBG…).

Gliflozines aussi utiles en HFpEF (recommandées).""",
    points=[
        "HFrEF = 4 piliers.",
        "Diurétique = congestion.",
        "Sortie = éducation + suivi + réadaptation.",
    ],
    indisp=["Connaître les 4 (ou 5 avec diurétique congestif) classes HFrEF."],
    inacc=["Oublier le régime sans sel / éducation.", "CI médicamenteuses méconnues."],
    message="HFrEF stable = **4 piliers** ; diurétique seulement si congestif.",
)

# ---------- 15 ----------
add(
    n=15,
    slug="15-syncope-bav",
    title="Syncope — BAV de haut degré",
    theme="Syncope / conduction",
    items=["342", "236", "231"],
    niveau="Urgence",
    vignette="""Homme de 78 ans. Syncope sans prodrome, traumatisme facial. ECG : BAV 3, FC 35, QRS larges 140 ms. PA 100/60.""",
    questions=[
        ("III", "Syncope à risque ?"),
        ("VI", "CAT ? Indication de stimulation ?"),
    ],
    correction="""Syncope **cardiogénique** à haut risque (pas de prodrome, traumatisme, BAV 3 QRS larges). Scope, isoprénaline/entraînement temporaire si mal toléré, **stimulation définitive** indiquée. Chercher cause (ischémie, médicaments, hyperK, EI si fièvre…).

Syncope d’effort = drapeau rouge (RA, HOCM, TV).""",
    points=[
        "BAV haut degré / pauses → pacemaker.",
        "QRS larges + BAV 3 = échappement bas, plus dangereux.",
        "Toujours ECG devant syncope.",
    ],
    indisp=["Reconnaître syncope rythmique et indiquer le PM."],
    inacc=["Rassurer « malaise vagal » devant BAV 3."],
    message="Syncope + BAV haut degré = **stimulation**, pas observation seule.",
)

# ---------- 16 ----------
add(
    n=16,
    slug="16-pericardite",
    title="Péricardite aiguë",
    theme="Douleur thoracique",
    items=["235", "230"],
    niveau="Consult / urgences",
    vignette="""Homme de 28 ans, sportif. Douleur thoracique positionnelle, améliorée en antéflexion, virose récente. Frottement. ECG : ST diffus concave, sous-PQ, pas de miroir. Tropo normale. ETT : épanchement minime.""",
    questions=[
        ("III", "Critères diagnostiques ? Différence STEMI ?"),
        ("VI", "Traitement ? Sport ? Hospitalisation ?"),
    ],
    correction="""Diagnostic si ≥ 2 critères : douleur typique, frottement, ECG typique, épanchement. Différencier STEMI (ST systématisé + miroir). Traitement : **AINS + colchicine**, repos, arrêt sport jusqu’à guérison. Hospitaliser si critères de gravité (fièvre, gros épanchement, myocardite, immunodépression, traumatisme…).""",
    points=[
        "ST diffus sans miroir + sous-PQ = péricardite.",
        "AINS + colchicine ; repos sportif.",
        "Tropo élevée → myopéricardite, ne pas manquer un SCA.",
    ],
    indisp=["Connaître critères et traitement de 1re intention."],
    inacc=["Autoriser la compétition trop tôt.", "Prendre une péricardite pour un STEMI (ou l’inverse)."],
    message="Péricardite : **clinique + ECG**, AINS+colchicine, **sport stoppé**.",
)

# ---------- 17 ----------
add(
    n=17,
    slug="17-tamponnade",
    title="Tamponnade",
    theme="Urgences",
    items=["235", "230", "342"],
    niveau="Urgence vitale",
    vignette="""Patiente de 54 ans, cancer sein. Dyspnée, PA 75/50, TJ, pouls paradoxal, bruits assourdis. ETT : épanchement 25 mm, compression OD, variations respiratoires mitrales.""",
    questions=[
        ("V", "Diagnostic ?"),
        ("VI", "CAT ?"),
    ],
    correction="""**Tamponnade** : clinique (Beck : hypoTA, TJ, bruits assourdis) + pouls paradoxal + ETT. Urgence : **drainage** (péricardiocentèse / chirurgical selon cause), remplissage prudent, éviter vasodilatation. Cause (néoplasie, post-IDM, EI, dissection…).""",
    points=[
        "Tamponnade = clinique + écho, pas seulement le mm d’épanchement.",
        "Drainage urgent.",
    ],
    indisp=["Reconnaître et faire drainer."],
    inacc=["Diurétiques / nitrés en 1re intention."],
    message="Tamponnade = **drainer**, pas « surveiller l’épanchement ».",
)

# ---------- 18 ----------
add(
    n=18,
    slug="18-tv-qrs-larges",
    title="Tachycardie à QRS larges",
    theme="Rythme",
    items=["231", "237", "331"],
    niveau="USIC",
    vignette="""Homme de 70 ans, IDM ancien. Palpitations, malaise. PA 75/45. ECG : tachycardie régulière 180/min, QRS 160 ms.""",
    questions=[
        ("III", "TV ou aberrance ? Attitude ?"),
        ("VI", "CAT si instable ?"),
    ],
    correction="""**Toute tachycardie régulière à QRS larges = TV jusqu’à preuve du contraire**, surtout si cardiopathie. Instable → **CVE**. Stable → amiodarone / procainamide selon protocole, jamais inhibiteurs calciques / adénosine à l’aveugle si TV probable.

Ne pas confondre avec BBG « chronique » asymptomatique.""",
    points=[
        "QRS larges réguliers = TV d’abord.",
        "Instabilité → choc électrique.",
        "BB vs TV : le bloc de branche ne fait pas de bradycardie.",
    ],
    indisp=["Traiter comme TV si doute."],
    inacc=["Adénosine / inhib. calcique sur TV."],
    message="QRS larges + régulier = **TV** ; mal toléré = **choc**.",
)

# ---------- 19 ----------
add(
    n=19,
    slug="19-dissection-aortique",
    title="Dissection aortique",
    theme="Douleur thoracique",
    items=["230", "225"],
    niveau="Piège mortel",
    vignette="""Homme de 55 ans, HTA mal contrôlée. Douleur thoracique en coup de poignard migrant vers le dos. PA 190/100 bras droit, 140/80 bras gauche. Souffle d’IA. ECG peu modifié.""",
    questions=[
        ("III", "Orientation ?"),
        ("IV", "Examen de confirmation ?"),
        ("VI", "Cible tensionnelle / CAT ?"),
    ],
    correction="""**Dissection aortique** (type A si aorte ascendante → chirurgie urgente). Angioscanner (ou ETO). Contrôle brutal de la PA (PAS < 120) et de la FC (BB d’abord puis vasodilatateurs). Ne pas thrombolyser / anticoaguler comme un SCA. Chercher complications (IA, tamponnade, ischémie d’organe).""",
    points=[
        "Douleur migratrice + asymétrie TA + IA = dissection.",
        "Type A = chirurgie.",
        "PAS cible < 120 mmHg rapidement.",
    ],
    indisp=["Évoquer la dissection dans le PIED."],
    inacc=["Fibrinolyse / PCI « SCA » sans y penser."],
    message="Douleur déchirante + asymétrie TA = **scanner**, pas tropo seule.",
)

# ---------- 20 ----------
add(
    n=20,
    slug="20-sortie-ic",
    title="Préparer une sortie d’IC",
    theme="IC / hospitalier",
    items=["234", "222"],
    niveau="Stage Cardio 4",
    vignette="""M. X, J5 pour décompensation HFrEF. −4 kg, plus de crépitants, œdèmes discrets. Créat stable, K+ 4,6. Traitements : bisoprolol, sacubitril/valsartan, spironolactone, dapagliflozine, furosémide 60 mg. Demande « je peux partir ? ».""",
    questions=[
        ("II", "Quels critères cliniques/bio avant sortie ?"),
        ("VI", "Conseils et suivi ?"),
    ],
    correction="""Sortie si congestion contrôlée, stabilité hémodynamique/rénale, traitements pronostiques en place ou planifiés, éducation faite (poids, symptômes, sel, observance), RDV cardio/MG, ordonnance claire, ± réadaptation. Vérifier pas d’hyperK/IR sous ARM/IEC. Expliquer quand reconsulter.""",
    points=[
        "Sortie IC = clinique + bio + éducation + suivi.",
        "4 piliers en place avant/après sortie.",
    ],
    indisp=["Éducation thérapeutique à la sortie."],
    inacc=["Sortir encore très congestif « pour faire de la place »."],
    message="Sortie IC = **sec + traité + éduqué + suivi calé**.",
)

# ---------- 21 ----------
add(
    n=21,
    slug="21-consult-souffle",
    title="Consultation — souffle à explorer",
    theme="Ambulatoire",
    items=["233RA", "233IM", "238"],
    niveau="Ambulatoire",
    vignette="""Mme Y, 70 ans, adressée pour souffle découvert par le MG. Asymptomatique. Souffle systolique 3/6 foyer aortique. ECG : HVG. Que proposes-tu en consultation structurée (présentation 2–3 min) ?""",
    questions=[
        ("I–II", "Interrogatoire et examen ciblés ?"),
        ("III–IV", "Hypothèses et examens ?"),
        ("VI", "Message au senior ?"),
    ],
    correction="""Interroger dyspnée, angor, syncope, capacité d’effort, FDR. Caractériser le souffle (temps, foyer, irradiation, B2). Hypothèse principale : **RA** (± IM, CMH). ECG, ETT en 1re intention. Synthèse : « Souffle aortique + HVG → ETT pour sévérité/FEVG ; si RA serré symptomatique → Heart Team. »

Présentation 2–3 min selon trame ambulatoire.""",
    points=[
        "Souffle → caractériser + ETT.",
        "Lien symptôme ↔ sévérité valve.",
    ],
    indisp=["Savoir quand une ETT est indiquée devant un souffle."],
    inacc=["Rassurer sans ETT si souffle organique suspect."],
    message="Souffle de l’adulte = **ETT**, puis sévérité + symptômes.",
)

# ---------- 22 ----------
add(
    n=22,
    slug="22-usic-externe-actif",
    title="USIC — externe actif devant douleur",
    theme="Savoir-être / USIC",
    items=["230", "339", "231"],
    niveau="Stage",
    vignette="""Tu es en USIC. Ton patient coronarien J1 post-stent sonne : « j’ai mal à la poitrine ». Scope : sinusal 90/min, PA 125/70 sur le moniteur. L’interne est en coro.""",
    questions=[
        ("Attitude", "Que fais-tu concrètement (externe actif) ?"),
        ("Clinique", "Que cherches-tu ?"),
        ("Examens", "Que demandes-tu avant/pendant l’appel ?"),
    ],
    correction="""**Externe actif :** aller au lit, interrogatoire LITHIASE, examen (gravité, auscultation, congestion), **demander un ECG 12–18D immédiatement**, noter constantes, appeler l’interne en disant : « douleur, ECG demandé/en cours, constantes X, pas de choc ».

Ne pas : rester au bureau à transmettre « il a mal ».  
Différentiel J1 : ischémie/stent, péricardite post-IDM, anxiété, digesto…

Surveiller complications mécaniques / rythmiques.""",
    points=[
        "Externe actif = voir + ECG + alerter avec données.",
        "Douleur post-SCA = toujours reprendre l’algo PIED/SCA.",
    ],
    indisp=["Savoir quand alerter en USIC."],
    inacc=["Déléguer sans voir le patient ni ECG."],
    message="USIC : **au lit → ECG → appel structuré**, jamais transmission passive seule.",
)


def render(arc: dict) -> str:
    qs = "\n".join(f"### {t}\n{q}\n" for t, q in arc["questions"])
    pts = "\n".join(f"- {p}" for p in arc["points"])
    ind = "\n".join(f"- {x}" for x in arc["indisp"])
    ina = "\n".join(f"- {x}" for x in arc["inacc"])
    items = ", ".join(f"item {i}" for i in arc["items"])
    return f"""# ARC {arc['n']:02d} — {arc['title']}

| | |
|---|---|
| **Thème IMM** | {arc['theme']} |
| **Items R2C / collège** | {items} |
| **Niveau** | {arc['niveau']} |

> Entraîne-toi d’abord **sans regarder** la correction (trame ARC : I→VI).

---

## Vignette

{arc['vignette']}

---

## Questions

{qs}
---

## Correction

{arc['correction']}

---

## Points collège / R2C (à coller)

{pts}

### Indispensables
{ind}

### Inacceptables
{ina}

---

## Message clé

**{arc['message']}**
"""


def main():
    index_rows = []
    for arc in ARCS:
        path = OUT / f"{arc['slug']}.md"
        path.write_text(render(arc), encoding="utf-8")
        index_rows.append(
            f"| {arc['n']:02d} | [{arc['title']}]({arc['slug']}.md) | {arc['theme']} | {arc['niveau']} |"
        )
        print("wrote", path.name)

    readme = f"""# ARC — Stage cardiologie IMM

**{len(ARCS)} ARC** pour devenir excellent : thèmes IMM + urgences USIC/consult + corrections collège R2C.

## Comment réviser
1. Lis la vignette, réponds à voix haute (trame I→VI du guide).
2. Corrige-toi avec la section **Correction**.
3. Recopie le **message clé** + indispensables / inacceptables.
4. Relie à l’app QCM (items indiqués).

## Index

| # | ARC | Thème | Niveau |
|---|---|---|---|
{chr(10).join(index_rows)}

## Couverture
- Thèmes IMM : SCA, endocardite, douleur thoracique, EP, FA, valvulopathies
- Bonus stage : IC/OAP, HFrEF, syncope/BAV, péricardite, tamponnade, TV, dissection, sortie, consult, posture USIC
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print("OK", len(ARCS), "ARCs")


if __name__ == "__main__":
    main()
