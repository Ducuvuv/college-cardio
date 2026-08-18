# -*- coding: utf-8 -*-
import re
from pathlib import Path

p = Path(r"C:\Users\gestu\Documents\college cardio\Cours\VI_Divers\331_Arret_cardiocirculatoire.md")
text = p.read_text(encoding="utf-8")

seen = set()
lines = []
for line in text.splitlines():
    m = re.search(r"!\[.*\]\(\./img/(fig_[^)]+)\)", line)
    if m:
        if m.group(1) in seen:
            continue
        seen.add(m.group(1))
    lines.append(line)
text = "\n".join(lines)

garbage_patterns = [
    r"^after out-of-hospital",
    r"^of resuscitation and favorable",
    r"^X\. Witnemd",
    r"^BystonderCPR",
    r"^No bystenderCPR",
    r"^Systander CPA",
    r"^V4 n J aVK",
    r"^7 .*Probabilité de survie",
    r"^peuvent différer\. Les causes.*\bil$",
]
out = []
for line in text.splitlines():
    if any(re.search(g, line) for g in garbage_patterns):
        continue
    out.append(line)
text = "\n".join(out)

replacements = [
    (
        "**Rang A.** Les recommandations actuelles de prise en charge de l'arrêt cardiocirculatoire (ou arrêt\n\ncardiaque) en France reposent sur les recommandations européennes de 2021 du Comité européen de réanimation (ERC) regroupant les Sociétés européennes de cardiologie et de réa- nimation, les recommandations de la Société européenne de cardiologie de 2022 et les recom- mandations américaines de 2020. La Société française de réanimation et la Société française de médecine d'urgence adoptent ces recommandations. Les arrêts cardiaques extrahospitaliers sont à l'origine de 300 000 décès par an aux États-Unis. En Europe, les décès sont évalués à 500 000 par an. En France, la fréquence des décès par arrêt cardiaque est de 40 000 par an, soit une incidence de 0,75 %o dans la population générale. décès du patient. Au-delà de 5 minutes d'arrêt cardiaque, la survie est de l'ordre de 7 à 8 %.",
        "**Rang A.** Les recommandations actuelles de prise en charge de l'arrêt cardiocirculatoire (ou arrêt cardiaque) en France reposent sur les recommandations européennes de 2021 du Comité européen de réanimation (ERC), les recommandations de la Société européenne de cardiologie de 2022 et les recommandations américaines de 2020. La Société française de réanimation et la Société française de médecine d'urgence adoptent ces recommandations.\n\nLes arrêts cardiaques extrahospitaliers sont à l'origine de 300 000 décès par an aux États-Unis. En Europe, les décès sont évalués à 500 000 par an. En France, la fréquence des décès par arrêt cardiaque est de 40 000 par an, soit une incidence de 0,75 ‰ dans la population générale.\n\nL'arrêt cardiaque, s'il est prolongé au-delà de quelques minutes, aboutit très rapidement au décès du patient. Au-delà de 5 minutes d'arrêt cardiaque, la survie est de l'ordre de 7 à 8 %. Au-delà de 10 minutes, elle est proche de 0 (fig. 21.1).",
    ),
    ("ne réponds", "ne répond"),
    ("**Fig. • Exemple", "**Fig. 21.5 — Exemple"),
    ("fig. 21 .4", "fig. 21.4"),
    ("survie et faible", "survie est faible"),
    (
        "# VII. Conditionnement hospitalier et pronostic à la phase hospitalière\n\n**Rang A** · **Rang B**.\n\nà la phase hospitalière Après",
        "# VII. Conditionnement hospitalier et pronostic à la phase hospitalière\n\n**Rang A** · **Rang B**.\n\nAprès",
    ),
    ("A. Préservation de la fonction cardiaque Dans", "## A. Préservation de la fonction cardiaque\n\nDans"),
    ("B. Préservation cérébrale et pronostic cérébral (encadré 21.4) Le", "## B. Préservation cérébrale et pronostic cérébral (encadré 21.4)\n\nLe"),
]
for old, new in replacements:
    text = text.replace(old, new)

text = re.sub(r"\n{3,}", "\n\n", text)
p.write_text(text, encoding="utf-8")
print("cleaned", p.stat().st_size)
