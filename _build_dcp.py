# -*- coding: utf-8 -*-
"""Extract Chapitre 23 DCP ECG figures (Fig. 23.1–23.4) into Entrainement/img/."""
import re
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # noqa: F401

ROOT = Path(r"C:\Users\gestu\Documents\college cardio")
PDF = ROOT / "CARDIO 3e.pdf"
OUT = ROOT / "Entrainement" / "23_DCP.md"
IMG_DIR = ROOT / "Entrainement" / "img"
README = ROOT / "Cours" / "README.md"

# PDF printed ~587–597 → 0-based indexes 586–596. Clip above highest-y0 caption.
FIGURES = [
    ("23.1", "fig_23_1.png", 586, 280),
    ("23.2", "fig_23_2.png", 587, 320),
    ("23.3", "fig_23_3.png", 595, 300),
    ("23.4", "fig_23_4.png", 596, 360),
]


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
            y1 = min(page.rect.height, r.y1 + 14)
            y0 = max(0, r.y0 - height)
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
    row = "| Fait | 23 DCP | [../Entrainement/23_DCP.md](../Entrainement/23_DCP.md) |"
    old = "| À faire | … | lots suivants |"
    if "23 DCP" not in text and old in text:
        README.write_text(text.replace(old, row), encoding="utf-8")
        print("Updated README.md")
    else:
        print("README already contains 23 DCP or placeholder missing")


def verify():
    content = OUT.read_text(encoding="utf-8")
    size = OUT.stat().st_size
    dcps = re.findall(r"^## DCP \d+", content, re.M)
    qs = re.findall(r"^### Question \d+", content, re.M)
    reps = re.findall(r"\*\*Réponse :", content)
    figs = list(IMG_DIR.glob("fig_23_*.png"))
    print(f"MD {size} bytes, {len(dcps)} DCP, {len(qs)} questions, {len(reps)} réponses, {len(figs)} figures")
    if size < 40_000:
        print("WARN: file < 40 KB")
    if "Chapitre 24" in content or "Item 221" in content:
        print("WARN: chapter leak")
    if "Faille" in content or "amis-med" in content:
        print("WARN: watermark")


def main():
    extract_figures()
    update_readme()
    verify()


if __name__ == "__main__":
    main()
