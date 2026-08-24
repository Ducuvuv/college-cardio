# -*- coding: utf-8 -*-
"""Génère des tracés ECG SVG pédagogiques — SANS spoil du diagnostic sur l'image."""
from __future__ import annotations

import random
from pathlib import Path

OUT = Path(__file__).resolve().parent / "images" / "ecg"


def grid(w: int, h: int) -> str:
    lines = []
    for x in range(0, w, 10):
        c = "#fde8e8" if x % 50 == 0 else "#fef5f5"
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{c}" stroke-width="1"/>')
    for y in range(0, h, 10):
        c = "#fde8e8" if y % 50 == 0 else "#fef5f5"
        lines.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{c}" stroke-width="1"/>')
    return "\n".join(lines)


def wave(points: list[tuple[float, float]], color: str = "#b91c1c", width: float = 2.0) -> str:
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" points="{pts}"/>'


def flat(y: float, x0: float, x1: float, step: float = 4) -> list[tuple[float, float]]:
    return [(x, y) for x in frange(x0, x1, step)]


def frange(a: float, b: float, s: float):
    x = a
    while x <= b + 1e-9:
        yield x
        x += s


def beat(
    x0: float,
    y: float,
    *,
    p: bool = True,
    p_h: float = 8,
    qrs_w: float = 14,
    qrs_h: float = 38,
    qrs_sign: float = 1.0,
    st: float = 0,
    t_h: float = 16,
    t_sign: float = 1.0,
    pr_gap: float = 18,
    fibril: bool = False,
    delta: bool = False,
    flutter_f: bool = False,
) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    x = x0
    if fibril:
        rng = random.Random(int(x0 * 10) % 997)
        for _ in range(18):
            x += 4
            pts.append((x, y + rng.uniform(-5, 5)))
        return pts
    if flutter_f:
        for _ in range(3):
            pts += [(x, y), (x + 6, y - 10), (x + 12, y), (x + 18, y + 8), (x + 24, y)]
            x += 24
        pts += [(x, y + 4 * qrs_sign), (x + 4, y + qrs_h * qrs_sign), (x + qrs_w, y - qrs_h * 0.3 * qrs_sign), (x + qrs_w + 5, y)]
        return pts

    pts.extend(flat(y, x, x + 10))
    x += 10
    if p:
        pts += [(x, y), (x + 5, y - p_h), (x + 10, y), (x + pr_gap, y)]
        x += pr_gap
    else:
        pts.extend(flat(y, x, x + 10))
        x += 10

    if delta:
        pts += [(x, y), (x + 6, y - 4 * qrs_sign), (x + 12, y + qrs_h * 0.15 * qrs_sign),
                (x + 18, y + qrs_h * qrs_sign), (x + qrs_w + 8, y - qrs_h * 0.25 * qrs_sign), (x + qrs_w + 14, y)]
        x += qrs_w + 14
    else:
        pts += [(x, y + 3 * qrs_sign), (x + 4, y + qrs_h * qrs_sign), (x + qrs_w, y - qrs_h * 0.35 * qrs_sign), (x + qrs_w + 5, y)]
        x += qrs_w + 5

    if st:
        pts += [(x, y - st), (x + 14, y - st), (x + 26, y)]
        x += 26
    else:
        pts.extend(flat(y, x, x + 14))
        x += 14

    if t_h:
        pts += [(x, y), (x + 8, y - t_h * t_sign), (x + 18, y)]
        x += 18
    pts.extend(flat(y, x, x + 16))
    return pts


def compose(n: int, baseline: float = 55, **kw) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    x = 8.0
    irregular = bool(kw.pop("irregular", False))
    fibril = bool(kw.get("fibril", False))
    for i in range(n):
        if fibril:
            # ligne de base fibrillatoire puis QRS sans P
            rng = random.Random(int(x * 7 + i) % 997)
            for _ in range(10 + (i % 3) * 3):
                x += 3.5
                pts.append((x, baseline + rng.uniform(-5, 5)))
            kw_q = {**kw, "fibril": False, "p": False}
            seg = beat(x, baseline, **kw_q)
            pts.extend(seg)
            x = pts[-1][0] + (14 if irregular and i % 2 == 0 else 4)
            continue
        seg = beat(x, baseline, **kw)
        pts.extend(seg)
        x = pts[-1][0] + (16 if irregular and i % 3 == 0 else 6)
    return pts


def strip_svg(lead: str, points: list[tuple[float, float]], w: int = 380, h: int = 90) -> str:
    """Une bande dérivation : label de dérivation seulement, pas de diagnostic."""
    # rescale x into strip width
    if not points:
        points = [(0, h / 2), (w, h / 2)]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    minx, maxx = min(xs), max(xs)
    span = max(maxx - minx, 1)
    scaled = [((p[0] - minx) / span * (w - 50) + 40, p[1] * (h / 110)) for p in points]
    return f"""<g>
  <rect x="0" y="0" width="{w}" height="{h}" fill="#fff"/>
  {grid(w, h)}
  <text x="6" y="14" font-family="system-ui,sans-serif" font-size="11" font-weight="700" fill="#334">{lead}</text>
  {wave(scaled, width=1.8)}
</g>"""


def lead_morph(diag: str, lead: str) -> dict:
    """Morphologie pédagogique simplifiée par dérivation."""
    base = {"p": True, "st": 0, "t_h": 12, "qrs_h": 28, "qrs_w": 12, "qrs_sign": 1.0, "t_sign": 1.0}
    if lead == "aVR":
        base["qrs_sign"] = -1.0
        base["t_sign"] = -1.0
        base["p_h"] = 4

    if diag == "normal":
        if lead in ("V1", "V2"):
            base["qrs_h"] = 18
            base["t_h"] = 6
        elif lead in ("V5", "V6", "DI", "aVL"):
            base["qrs_h"] = 34
        return base

    if diag == "fa":
        return {**base, "p": False, "fibril": True, "qrs_h": 26, "irregular": True}

    if diag == "flutter":
        return {**base, "p": False, "flutter_f": True, "qrs_h": 24}

    if diag == "stemi-ant":
        if lead in ("V1", "V2", "V3", "V4"):
            return {**base, "st": 16, "t_h": 6, "qrs_h": 30}
        if lead in ("DII", "DIII", "aVF"):
            return {**base, "st": -8, "t_h": 8}  # miroir approximatif via st négatif = underdraw
        return base

    if diag == "stemi-inf":
        if lead in ("DII", "DIII", "aVF"):
            return {**base, "st": 14, "t_h": 6}
        if lead in ("DI", "aVL"):
            return {**base, "st": -6, "t_h": 8}
        return base

    if diag == "pericardite":
        # diffus concave-ish ST up, not territorial
        if lead != "aVR":
            return {**base, "st": 10, "t_h": 10, "p_h": 5}
        return {**base, "st": -6, "qrs_sign": -1, "t_sign": -1}

    if diag == "bav3":
        return {**base, "p": True, "qrs_h": 22, "pr_gap": 8}  # visual handled specially

    if diag == "mobitz2":
        return {**base, "p": True, "qrs_w": 18, "qrs_h": 30}

    if diag == "lbbb":
        if lead in ("V1", "V2"):
            return {**base, "qrs_w": 26, "qrs_h": 22, "qrs_sign": -1, "t_sign": 1, "st": 4}
        return {**base, "qrs_w": 26, "qrs_h": 32, "t_sign": -1, "st": -3}

    if diag == "rbbb":
        if lead in ("V1", "V2"):
            return {**base, "qrs_w": 24, "qrs_h": 28, "t_sign": -1}
        return {**base, "qrs_w": 22, "qrs_h": 26}

    if diag == "vt":
        return {**base, "p": False, "qrs_w": 28, "qrs_h": 36, "t_h": 0, "st": 0}

    if diag == "hyperk":
        return {**base, "p": False, "qrs_w": 20, "qrs_h": 22, "t_h": 26, "t_sign": 1}

    if diag == "wpw":
        return {**base, "p": True, "delta": True, "pr_gap": 8, "qrs_w": 20, "qrs_h": 30}

    if diag == "ep":
        if lead in ("V1", "V2", "V3"):
            return {**base, "t_sign": -1, "t_h": 14, "qrs_h": 20}
        if lead == "DI":
            return {**base, "qrs_h": 18}
        if lead == "DIII":
            return {**base, "qrs_h": 16, "p_h": 10}
        return {**base, "qrs_h": 22}

    return base


def bav3_strip(baseline: float = 55) -> list[tuple[float, float]]:
    pts = []
    x = 8.0
    # P waves regular + QRS independent
    p_times = [8, 40, 72, 104, 136, 168, 200, 232, 264]
    q_times = [20, 90, 160, 230]
    for t in sorted(set(p_times + q_times)):
        if t in p_times:
            pts += [(t, baseline), (t + 5, baseline - 7), (t + 10, baseline)]
        if t in q_times:
            pts += [(t, baseline + 3), (t + 4, baseline + 28), (t + 12, baseline - 10), (t + 18, baseline)]
    # fill flats
    if not pts:
        return flat(baseline, 0, 300)
    # sort by x and reconnect
    pts = sorted(pts, key=lambda p: p[0])
    out = []
    for i, p in enumerate(pts):
        if i and p[0] - pts[i - 1][0] > 8:
            out.extend(flat(baseline, pts[i - 1][0], p[0], 4))
        out.append(p)
    return out


def mobitz_strip(baseline: float = 55) -> list[tuple[float, float]]:
    pts = []
    x = 8.0
    for i in range(5):
        pts.extend(beat(x, baseline, p=True, qrs_w=16, qrs_h=28))
        x = pts[-1][0] + 8
        if i == 2:
            # blocked P
            pts += [(x, baseline), (x + 5, baseline - 8), (x + 10, baseline)]
            pts.extend(flat(baseline, x + 10, x + 45))
            x += 45
    return pts


LEADS_12 = ["DI", "aVR", "V1", "V2", "DII", "aVL", "V3", "V4", "DIII", "aVF", "V5", "V6"]


def make_12lead(diag: str, a11y_title: str) -> str:
    cell_w, cell_h = 200, 100
    cols, rows = 4, 3
    W, H = cols * cell_w, rows * cell_h + 28
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">',
        f"<title>{a11y_title}</title>",
        f'<desc>ECG 12 dérivations — schéma pédagogique. Diagnostic masqué pour entraînement.</desc>',
        f'<rect width="{W}" height="{H}" fill="#fff"/>',
        f'<text x="8" y="18" font-family="system-ui,sans-serif" font-size="12" font-weight="700" fill="#445">ECG 12 dérivations · lis le tracé</text>',
    ]
    for i, lead in enumerate(LEADS_12):
        r, c = divmod(i, cols) if False else (i // cols, i % cols)
        # i // 4 = row, i % 4 = col — wait LEADS_12 is row-major with 4 cols
        row, col = i // cols, i % cols
        ox, oy = col * cell_w, 28 + row * cell_h
        morph = lead_morph(diag, lead)
        if diag == "bav3":
            pts = bav3_strip()
        elif diag == "mobitz2":
            pts = mobitz_strip()
        else:
            n = 3 if not morph.get("fibril") else 4
            pts = compose(n, **{k: v for k, v in morph.items()})
        # local strip then translate
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        minx, maxx = min(xs), max(xs)
        span = max(maxx - minx, 1)
        scaled = [
            (ox + 36 + (p[0] - minx) / span * (cell_w - 44), oy + p[1] * (cell_h / 110))
            for p in pts
        ]
        parts.append(f'<rect x="{ox}" y="{oy}" width="{cell_w}" height="{cell_h}" fill="#fff" stroke="#e8d0d0" stroke-width="0.5"/>')
        # mini grid
        for gx in range(ox, ox + cell_w, 10):
            cc = "#fde8e8" if (gx - ox) % 50 == 0 else "#fef5f5"
            parts.append(f'<line x1="{gx}" y1="{oy}" x2="{gx}" y2="{oy + cell_h}" stroke="{cc}" stroke-width="1"/>')
        for gy in range(oy, oy + cell_h, 10):
            cc = "#fde8e8" if (gy - oy) % 50 == 0 else "#fef5f5"
            parts.append(f'<line x1="{ox}" y1="{gy}" x2="{ox + cell_w}" y2="{gy}" stroke="{cc}" stroke-width="1"/>')
        parts.append(f'<text x="{ox + 6}" y="{oy + 14}" font-family="system-ui,sans-serif" font-size="11" font-weight="700" fill="#334">{lead}</text>')
        parts.append(wave(scaled, width=1.6))
    parts.append("</svg>")
    return "\n".join(parts)


def make_single(diag: str, lead: str, a11y: str) -> str:
    morph = lead_morph(diag, lead)
    if diag == "bav3":
        pts = bav3_strip(70)
    elif diag == "mobitz2":
        pts = mobitz_strip(70)
    else:
        n = 5 if not morph.get("fibril") else 6
        pts = compose(n, baseline=70, **{k: v for k, v in morph.items()})
    w, h = 800, 140
    xs = [p[0] for p in pts]
    minx, maxx = min(xs), max(xs)
    span = max(maxx - minx, 1)
    scaled = [((p[0] - minx) / span * (w - 60) + 40, p[1]) for p in pts]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img">
  <title>{a11y}</title>
  <desc>Tracé pédagogique sans diagnostic affiché. Dérivation {lead}.</desc>
  <rect width="{w}" height="{h}" fill="#fff"/>
  {grid(w, h)}
  <text x="12" y="20" font-family="system-ui,sans-serif" font-size="13" font-weight="700" fill="#445">{lead}</text>
  <text x="12" y="36" font-family="system-ui,sans-serif" font-size="11" fill="#889">Schéma pédagogique — lis le tracé</text>
  {wave(scaled)}
</svg>"""


CASES = [
    ("normal", "normal.svg", "12lead-normal.svg", "DII", "ECG schéma (diagnostic masqué)"),
    ("fa", "fa.svg", "12lead-fa.svg", "DII", "ECG schéma (diagnostic masqué)"),
    ("stemi-ant", "stemi-anterior.svg", "12lead-stemi-ant.svg", "V3", "ECG schéma (diagnostic masqué)"),
    ("stemi-inf", "stemi-inferior.svg", "12lead-stemi-inf.svg", "DII", "ECG schéma (diagnostic masqué)"),
    ("pericardite", "pericardite.svg", "12lead-pericardite.svg", "DII", "ECG schéma (diagnostic masqué)"),
    ("bav3", "bav3.svg", "12lead-bav3.svg", "DII", "ECG schéma (diagnostic masqué)"),
    ("mobitz2", "mobitz2.svg", "12lead-mobitz2.svg", "DII", "ECG schéma (diagnostic masqué)"),
    ("lbbb", "lbbb.svg", "12lead-lbbb.svg", "V6", "ECG schéma (diagnostic masqué)"),
    ("rbbb", "rbbb.svg", "12lead-rbbb.svg", "V1", "ECG schéma (diagnostic masqué)"),
    ("flutter", "flutter.svg", "12lead-flutter.svg", "DII", "ECG schéma (diagnostic masqué)"),
    ("vt", "vt.svg", "12lead-vt.svg", "V1", "ECG schéma (diagnostic masqué)"),
    ("hyperk", "hyperkalemia.svg", "12lead-hyperk.svg", "V3", "ECG schéma (diagnostic masqué)"),
    ("ep", "ep.svg", "12lead-ep.svg", "V1", "ECG schéma (diagnostic masqué)"),
    ("wpw", "wpw.svg", "12lead-wpw.svg", "DII", "ECG schéma (diagnostic masqué)"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for diag, single, twelve, lead, a11y in CASES:
        (OUT / single).write_text(make_single(diag, lead, a11y), encoding="utf-8")
        (OUT / twelve).write_text(make_12lead(diag, a11y), encoding="utf-8")
    (OUT / "README.txt").write_text(
        "Tracés ECG SVG pédagogiques (création originale).\n"
        "Les fichiers affichés à l'écran ne contiennent PAS le diagnostic — uniquement les dérivations.\n"
        "12lead-*.svg = feuille 12 dérivations pour mode « je lis puis je devine ».\n"
        "Schémas simplifiés, non destinés au diagnostic clinique.\n",
        encoding="utf-8",
    )
    print(f"Écrit {len(list(OUT.glob('*.svg')))} SVG dans {OUT}")


if __name__ == "__main__":
    main()
