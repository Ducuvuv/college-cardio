# -*- coding: utf-8 -*-
"""Génère des tracés ECG SVG pédagogiques (domaine public — création originale)."""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent / "images" / "ecg"


def grid(w: int = 800, h: int = 140) -> str:
    lines = []
    for x in range(0, w, 10):
        c = "#fde8e8" if x % 50 == 0 else "#fef5f5"
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{c}" stroke-width="1"/>')
    for y in range(0, h, 10):
        c = "#fde8e8" if y % 50 == 0 else "#fef5f5"
        lines.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{c}" stroke-width="1"/>')
    return "\n".join(lines)


def wave(points: list[tuple[float, float]], color: str = "#b91c1c", width: float = 2.2) -> str:
    pts = " ".join(f"{x},{y}" for x, y in points)
    return f'<polyline fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" points="{pts}"/>'


def flat(y: float, x0: float, x1: float, step: float = 4) -> list[tuple[float, float]]:
    return [(x, y) for x in frange(x0, x1, step)]


def frange(a: float, b: float, s: float):
    x = a
    while x <= b:
        yield x
        x += s


def beat(
    x0: float,
    y: float,
    *,
    p: bool = True,
    qrs_w: float = 14,
    qrs_h: float = 38,
    st: float = 0,
    t_h: float = 16,
    fibril: bool = False,
) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    x = x0
    if fibril:
        import random

        rng = random.Random(int(x0))
        for _ in range(int(70 / 4)):
            x += 4
            pts.append((x, y + rng.uniform(-6, 6)))
        return pts
    pts.extend(flat(y, x, x + 18))
    x += 18
    if p:
        pts += [(x, y), (x + 6, y - 8), (x + 12, y), (x + 18, y)]
        x += 18
    else:
        pts.extend(flat(y, x, x + 12))
        x += 12
    pts += [(x, y + 4), (x + 4, y + qrs_h), (x + qrs_w, y - qrs_h * 0.35), (x + qrs_w + 6, y)]
    x += qrs_w + 6
    if st:
        pts += [(x, y - st), (x + 16, y - st), (x + 28, y)]
        x += 28
    else:
        pts.extend(flat(y, x, x + 20))
        x += 20
    pts += [(x, y), (x + 10, y - t_h), (x + 22, y)]
    x += 22
    pts.extend(flat(y, x, x + 24))
    return pts


def compose(beats: list, baseline: float = 70) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    x = 20
    for spec in beats:
        if isinstance(spec, dict):
            seg = beat(x, baseline, **spec)
        else:
            seg = spec(x, baseline)
        pts.extend(seg)
        x = pts[-1][0] + 8
    return pts


def svg(title: str, subtitle: str, points: list[tuple[float, float]], extra: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 140" role="img">
  <title>{title}</title>
  <desc>{subtitle}</desc>
  <rect width="800" height="140" fill="#fff"/>
  {grid()}
  {wave(points)}
  {extra}
  <text x="12" y="18" font-family="Manrope, sans-serif" font-size="13" font-weight="700" fill="#1a2a22">{title}</text>
  <text x="12" y="34" font-family="Manrope, sans-serif" font-size="11" fill="#5a6a60">{subtitle}</text>
</svg>"""


def write(name: str, content: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")


def main() -> None:
    write(
        "normal.svg",
        svg(
            "ECG normal — rythme sinusal",
            "Onde P visible, QRS fin, ST isoélectrique · DII",
            compose([{"p": True, "st": 0}] * 5),
        ),
    )
    write(
        "fa.svg",
        svg(
            "Fibrillation atriale",
            "Absence d'ondes P, RR irréguliers, ligne de base fibrillatoire · DII",
            compose([{"p": False, "fibril": True, "qrs_h": 32}] * 6),
        ),
    )
    write(
        "stemi-anterior.svg",
        svg(
            "IDM ST+ antérieur",
            "Sus-décalage ST concave vers le haut en V2–V4 (schéma) · dérivations précordiales",
            compose([{"p": True, "st": 22, "t_h": 10}] * 4),
        ),
    )
    write(
        "stemi-inferior.svg",
        svg(
            "IDM ST+ inférieur",
            "Sus-décalage ST en DII–DIII–aVF · réciproque antérieur possible",
            compose([{"p": True, "st": 18, "t_h": 8}] * 5),
        ),
    )
    write(
        "pericardite.svg",
        svg(
            "Péricardite aiguë",
            "Sus-décalage ST diffus concave, sous-décalage PQ · pas de miroir",
            compose([{"p": True, "st": 14, "t_h": 12}] * 5),
        ),
    )
    pts_bav3 = []
    x = 20
    for _ in range(4):
        p = [(x, 70), (x + 8, 62), (x + 16, 70)]
        x += 16
        pts_bav3.extend(p + flat(70, x, x + 30))
        x += 30
        qrs = [(x, 74), (x + 5, 108), (x + 14, 40), (x + 20, 70)]
        pts_bav3.extend(qrs + flat(70, x + 20, x + 55))
        x += 55
    write(
        "bav3.svg",
        svg(
            "BAV du 3e degré",
            "Dissociation auriculo-ventriculaire · QRS fins, échappement jonctionnel",
            pts_bav3,
        ),
    )
    mobitz = []
    x = 20
    for i in range(5):
        mobitz.extend(beat(x, 70, p=True, st=0))
        x = mobitz[-1][0] + 10
        if i == 2:
            mobitz.extend(flat(70, x, x + 40))
            x += 40
    write(
        "mobitz2.svg",
        svg(
            "BAV 2 Mobitz 2",
            "Ondes P bloquées soudainement · QRS larges possibles",
            mobitz,
        ),
    )
    write(
        "lbbb.svg",
        svg(
            "BBG complet",
            "QRS ≥ 120 ms, notch latéral, HBAG · schéma",
            compose([{"p": True, "qrs_w": 26, "qrs_h": 34, "st": 0}] * 4),
        ),
    )
    write(
        "rbbb.svg",
        svg(
            "BBD complet",
            "QRS ≥ 120 ms, aspect rSR' en V1 · schéma",
            compose([{"p": True, "qrs_w": 24, "qrs_h": 36, "st": 0}] * 4),
        ),
    )
    flutter_pts = []
    x = 20
    for _ in range(8):
        for _ in range(3):
            flutter_pts += [(x, 70), (x + 8, 58), (x + 16, 70), (x + 24, 82), (x + 32, 70)]
            x += 32
        flutter_pts.extend(beat(x, 70, p=False, qrs_h=30, st=0))
        x = flutter_pts[-1][0] + 12
    write(
        "flutter.svg",
        svg(
            "Flutter atrial",
            "Ondes F en dents de scie · conduction AV variable",
            flutter_pts,
        ),
    )
    write(
        "vt.svg",
        svg(
            "Tachycardie ventriculaire",
            "QRS larges réguliers ~160/min · dissociation AV possible",
            compose([{"p": False, "qrs_w": 28, "qrs_h": 42, "st": 0, "t_h": 0}] * 8),
        ),
    )
    write(
        "hyperkalemia.svg",
        svg(
            "Hyperkaliémie sévère",
            "Ondes T pointues symétriques, QRS élargi · schéma",
            compose([{"p": False, "qrs_w": 22, "qrs_h": 28, "st": 0, "t_h": 28}] * 5),
        ),
    )
    ep_pts = compose([{"p": True, "st": 0, "t_h": 14}] * 3)
    write(
        "ep.svg",
        svg(
            "EP — signes indirects",
            "Tachycardie sinusale, S1Q3, T négatives antérieures · schéma",
            ep_pts,
            extra='<text x="620" y="120" font-size="10" fill="#5a6a60">S1Q3 · T inv V1-V3</text>',
        ),
    )
    wpw = []
    x = 20
    for _ in range(4):
        wpw += [(x, 70), (x + 4, 68), (x + 10, 66), (x + 16, 78), (x + 24, 38), (x + 32, 70)]
        x += 40
        wpw.extend(flat(70, x, x + 30))
        x += 30
    write(
        "wpw.svg",
        svg(
            "Syndrome de Wolff-Parkinson-White",
            "PR court, onde delta en début de QRS · schéma",
            wpw,
        ),
    )
    (OUT / "README.txt").write_text(
        "Tracés ECG SVG — création originale pour révision personnelle (domaine public).\n"
        "Schémas pédagogiques simplifiés, non destinés au diagnostic clinique.\n",
        encoding="utf-8",
    )
    print(f"Écrit {len(list(OUT.glob('*.svg')))} SVG dans {OUT}")


if __name__ == "__main__":
    main()
