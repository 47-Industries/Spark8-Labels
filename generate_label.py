#!/usr/bin/env python3
"""
Spark 8 — Florida Hemp Product Label Generator (V4 — Clean Compliance)
White-background, lab-style compliance sticker labels.
Multiple sizes: small (1x2"), medium (2x3"), large (3x4").
"""

import argparse
import io
import os
import math

import qrcode
from reportlab.lib.pagesizes import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


# ── Colors — minimal ───────────────────────────────────────
BG = white
TXT = black
TXT2 = black                   # secondary
TXT3 = HexColor("#222222")    # tertiary
TXT4 = HexColor("#333333")    # faint (still readable on white)
BORDER = HexColor("#CCCCCC")
DIV = HexColor("#E0E0E0")
RED = HexColor("#CC0000")
RED_LIGHT = HexColor("#FFF0F0")
RED_BORDER = HexColor("#EECCCC")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PRODUCT_TYPES = {
    "cartridge": "VAPE CARTRIDGE",
    "disposable": "DISPOSABLE VAPE",
    "gummies": "GUMMIES",
    "preroll": "PRE-ROLL",
    "flower": "FLOWER",
    "concentrate": "CONCENTRATE",
    "tincture": "TINCTURE",
    "edible": "EDIBLE",
}

# ── Size presets ────────────────────────────────────────────
SIZES = {
    "small":  {"w": 2 * inch,   "h": 1 * inch,   "name": "Small (2×1 in)"},
    "medium": {"w": 3 * inch,   "h": 2 * inch,   "name": "Medium (3×2 in)"},
    "large":  {"w": 4 * inch,   "h": 3 * inch,   "name": "Large (4×3 in)"},
}


def generate_qr(url, box_size=3):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size=box_size, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def draw_thca_triangle(c, cx, cy, size):
    """Red triangle with ! — standard compliance symbol."""
    r = size / 2
    angles = [90, 210, 330]
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in angles]

    # Red outer
    p = c.beginPath()
    p.moveTo(pts[0][0], pts[0][1])
    p.lineTo(pts[1][0], pts[1][1])
    p.lineTo(pts[2][0], pts[2][1])
    p.close()
    c.setFillColor(RED)
    c.drawPath(p, fill=1, stroke=0)

    # White inner
    ir = r * 0.75
    ipts = [(cx + ir * math.cos(math.radians(a)), cy + ir * math.sin(math.radians(a))) for a in angles]
    p2 = c.beginPath()
    p2.moveTo(ipts[0][0], ipts[0][1])
    p2.lineTo(ipts[1][0], ipts[1][1])
    p2.lineTo(ipts[2][0], ipts[2][1])
    p2.close()
    c.setFillColor(white)
    c.drawPath(p2, fill=1, stroke=0)

    # ! mark
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", size * 0.22)
    c.drawCentredString(cx, cy + size * 0.04, "!")

    # THCa text
    c.setFont("Helvetica-Bold", size * 0.12)
    c.drawCentredString(cx, cy - size * 0.15, "THCa")


def hline(c, y, x1, x2):
    c.setStrokeColor(DIV)
    c.setLineWidth(0.3)
    c.line(x1, y, x2, y)


# ════════════════════════════════════════════════════════════
# SMALL LABEL (2" x 1") — compact compliance sticker
# ════════════════════════════════════════════════════════════
def generate_small(c, W, H, strain, thc_mg, serving_size, batch, exp_date, product_type):
    M = 4
    IW = W - 2 * M

    # Border
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.4)
    c.rect(1, 1, W - 2, H - 2, fill=0, stroke=1)

    y = H - M

    # Row 1: THCa triangle + strain + product type
    tri_size = 12
    tri_cx = M + 8
    tri_cy = y - 6
    draw_thca_triangle(c, tri_cx, tri_cy, tri_size)

    c.setFillColor(TXT)
    c.setFont("Helvetica-Bold", 7)
    strain_display = strain.upper()[:18]
    c.drawString(M + 16, y - 4, strain_display)

    ptype = PRODUCT_TYPES.get(product_type, product_type.upper())
    c.setFillColor(TXT3)
    c.setFont("Helvetica", 4)
    c.drawString(M + 16, y - 10, f"THCa {ptype}")

    y -= 15
    hline(c, y, M, W - M)
    y -= 1

    # Row 2: THCa mg | Serving | Batch | Exp — single line
    c.setFillColor(TXT3)
    c.setFont("Helvetica", 3.5)
    col_w = IW / 4
    fields = [
        ("THCa", f"{thc_mg}mg"),
        ("SERVING", serving_size),
        ("BATCH", batch),
        ("EXP", exp_date),
    ]
    for i, (label, val) in enumerate(fields):
        x = M + i * col_w
        c.setFillColor(TXT4)
        c.setFont("Helvetica", 3)
        c.drawString(x + 1, y - 3, label)
        c.setFillColor(TXT)
        c.setFont("Helvetica-Bold", 4)
        c.drawString(x + 1, y - 8, val)

    y -= 11
    hline(c, y, M, W - M)
    y -= 1

    # Row 3: Warning text + QR
    c.setFillColor(TXT4)
    c.setFont("Helvetica", 2.3)
    c.drawString(M + 1, y - 3, "SALE TO PERSONS UNDER 21 PROHIBITED. NOT FOR INGESTION. KEEP OUT OF REACH OF CHILDREN.")
    c.setFont("Helvetica", 2.3)
    c.drawString(M + 1, y - 6.5, "This product has not been evaluated by the FDA. Contains <0.3% Delta-9 THC per dry weight.")
    c.setFont("Helvetica", 2.3)
    c.drawString(M + 1, y - 10, "SPARK 8 · shopspark8.com · FL Rule 5K-4.034 · Store in cool, dry place.")

    # Small QR at far right
    qr_s = 14
    qr_img = generate_qr("https://shopspark8.com", box_size=2)
    c.drawImage(qr_img, W - M - qr_s - 1, y - qr_s + 2, width=qr_s, height=qr_s)


# ════════════════════════════════════════════════════════════
# MEDIUM LABEL (3" x 2") — standard compliance sticker
# ════════════════════════════════════════════════════════════
def generate_medium(c, W, H, strain, thc_mg, serving_size, batch, exp_date, product_type):
    M = 6
    IW = W - 2 * M

    # Border
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.rect(1, 1, W - 2, H - 2, fill=0, stroke=1)

    y = H - M

    # ── Header: THCa triangle + brand + product type ──
    tri_size = 18
    tri_cx = M + 12
    tri_cy = y - 10
    draw_thca_triangle(c, tri_cx, tri_cy, tri_size)

    c.setFillColor(TXT)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(M + 24, y - 6, "SPARK 8")
    ptype = PRODUCT_TYPES.get(product_type, product_type.upper())
    c.setFillColor(TXT3)
    c.setFont("Helvetica", 5)
    c.drawString(M + 24, y - 14, f"THCa {ptype}")

    y -= 22
    hline(c, y, M, W - M)
    y -= 2

    # ── Strain name — bold, prominent ──
    c.setFillColor(TXT)
    strain_upper = strain.upper()
    fs = 14 if len(strain_upper) <= 14 else 11 if len(strain_upper) <= 20 else 9
    c.setFont("Helvetica-Bold", fs)
    c.drawCentredString(W / 2, y - fs + 2, strain_upper)
    y -= (fs + 4)

    hline(c, y, M, W - M)
    y -= 2

    # ── Data grid 2x2 ──
    grid_h = 28
    grid_y = y - grid_h
    half_w = IW / 2
    mid_x = M + half_w
    half_h = grid_h / 2

    # Grid lines
    c.setStrokeColor(DIV)
    c.setLineWidth(0.25)
    c.line(mid_x, grid_y, mid_x, grid_y + grid_h)
    c.line(M, grid_y + half_h, W - M, grid_y + half_h)

    def cell(x, cy, label, value):
        c.setFillColor(TXT4)
        c.setFont("Helvetica", 4)
        c.drawString(x + 4, cy + half_h - 5, label)
        c.setFillColor(TXT)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x + 4, cy + 2, value)

    cell(M, grid_y + half_h, "THCa PER SERVING", f"{thc_mg} mg")
    cell(mid_x, grid_y + half_h, "SERVING SIZE", serving_size)
    cell(M, grid_y, "BATCH #", batch)
    cell(mid_x, grid_y, "EXP DATE", exp_date)

    y = grid_y - 3
    hline(c, y, M, W - M)
    y -= 2

    # ── Warning box ──
    warn_h = 28
    c.setFillColor(RED_LIGHT)
    c.setStrokeColor(RED_BORDER)
    c.setLineWidth(0.3)
    c.rect(M, y - warn_h, IW, warn_h, fill=1, stroke=1)

    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 4.5)
    c.drawString(M + 3, y - 6, "CONTAINS THCa — HEMP DERIVED PRODUCT")

    c.setFillColor(TXT2)
    c.setFont("Helvetica", 3.2)
    c.drawString(M + 3, y - 12, "THE SALE OF HEMP OR HEMP EXTRACT TO PERSONS UNDER 21 IS PROHIBITED.")
    c.setFont("Helvetica-Bold", 3.2)
    c.drawString(M + 3, y - 16.5, "PROOF OF AGE REQUIRED. NOT FOR INGESTION — DO NOT EAT.")
    c.setFont("Helvetica", 3)
    c.setFillColor(TXT3)
    c.drawString(M + 3, y - 21, "KEEP OUT OF REACH OF CHILDREN AND PETS. STORE IN A COOL, DRY PLACE.")
    c.drawString(M + 3, y - 25, "DO NOT USE IF PREGNANT OR NURSING. MAY CAUSE DROWSINESS.")

    y -= (warn_h + 3)
    hline(c, y, M, W - M)
    y -= 1

    # ── Footer: QR + dist + legal fine print ──
    qr_s = 18
    qr_img = generate_qr("https://shopspark8.com", box_size=2)
    c.drawImage(qr_img, M + 1, y - qr_s, width=qr_s, height=qr_s)

    ix = M + qr_s + 4
    c.setFillColor(TXT4)
    c.setFont("Helvetica", 3)
    c.drawString(ix, y - 3, "DISTRIBUTED BY")
    c.setFillColor(TXT)
    c.setFont("Helvetica-Bold", 4.5)
    c.drawString(ix, y - 8, "SPARK 8  ·  Smoke Shop & Lounge")
    c.setFillColor(TXT3)
    c.setFont("Helvetica", 3.5)
    c.drawString(ix, y - 13, "shopspark8.com  ·  Tampa Bay, FL")

    # Legal fine print below QR
    c.setFillColor(TXT4)
    c.setFont("Helvetica", 2)
    fp_y = y - qr_s - 3
    c.drawString(M + 1, fp_y, "This product has not been evaluated by the FDA. Not intended to diagnose, treat, cure, or prevent any disease.")
    c.drawString(M + 1, fp_y - 3, "Hemp derived. <0.3% Delta-9 THC. 2018 Farm Bill compliant. FL Rule 5K-4.034.")


# ════════════════════════════════════════════════════════════
# LARGE LABEL (4" x 3") — full compliance label
# ════════════════════════════════════════════════════════════
def generate_large(c, W, H, strain, thc_mg, serving_size, batch, exp_date, product_type):
    M = 8
    IW = W - 2 * M

    # Border
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.rect(2, 2, W - 4, H - 4, fill=0, stroke=1)

    y = H - M

    # ── Header ──
    tri_size = 24
    tri_cx = M + 16
    tri_cy = y - 14
    draw_thca_triangle(c, tri_cx, tri_cy, tri_size)

    c.setFillColor(TXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M + 32, y - 8, "SPARK 8")
    ptype = PRODUCT_TYPES.get(product_type, product_type.upper())
    c.setFillColor(TXT3)
    c.setFont("Helvetica", 6.5)
    c.drawString(M + 32, y - 18, f"THCa {ptype}")
    c.setFillColor(TXT4)
    c.setFont("Helvetica", 5)
    c.drawString(M + 32, y - 26, "Smoke Shop & Lounge  ·  Tampa Bay, FL")

    y -= 32
    hline(c, y, M, W - M)
    y -= 4

    # ── Strain name ──
    c.setFillColor(TXT)
    strain_upper = strain.upper()
    fs = 20 if len(strain_upper) <= 12 else 16 if len(strain_upper) <= 18 else 12
    c.setFont("Helvetica-Bold", fs)
    c.drawCentredString(W / 2, y - fs + 2, strain_upper)
    y -= (fs + 6)

    hline(c, y, M, W - M)
    y -= 4

    # ── Data grid 2x2 ──
    grid_h = 44
    grid_y = y - grid_h
    half_w = IW / 2
    mid_x = M + half_w
    half_h = grid_h / 2

    c.setStrokeColor(DIV)
    c.setLineWidth(0.3)
    c.line(mid_x, grid_y, mid_x, grid_y + grid_h)
    c.line(M, grid_y + half_h, W - M, grid_y + half_h)

    def cell(x, cy, label, value):
        c.setFillColor(TXT4)
        c.setFont("Helvetica", 5)
        c.drawString(x + 6, cy + half_h - 7, label)
        c.setFillColor(TXT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 6, cy + 3, value)

    cell(M, grid_y + half_h, "THCa PER SERVING", f"{thc_mg} mg")
    cell(mid_x, grid_y + half_h, "SERVING SIZE", serving_size)
    cell(M, grid_y, "BATCH #", batch)
    cell(mid_x, grid_y, "EXP DATE", exp_date)

    y = grid_y - 5
    hline(c, y, M, W - M)
    y -= 4

    # ── Warning box ──
    warn_h = 42
    c.setFillColor(RED_LIGHT)
    c.setStrokeColor(RED_BORDER)
    c.setLineWidth(0.4)
    c.rect(M, y - warn_h, IW, warn_h, fill=1, stroke=1)

    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(M + 5, y - 8, "CONTAINS THCa — HEMP DERIVED PRODUCT")

    c.setFillColor(TXT2)
    c.setFont("Helvetica", 4.5)
    c.drawString(M + 5, y - 16, "THE SALE OF HEMP OR HEMP EXTRACT INTENDED FOR HUMAN CONSUMPTION")
    c.drawString(M + 5, y - 22, "TO PERSONS UNDER THE AGE OF 21 IS PROHIBITED. PROOF OF AGE IS REQUIRED.")
    c.setFont("Helvetica-Bold", 4.5)
    c.drawString(M + 5, y - 28, "NOT INTENDED FOR INGESTION — DO NOT EAT.")
    c.setFont("Helvetica", 4)
    c.setFillColor(TXT3)
    c.drawString(M + 5, y - 34, "KEEP OUT OF REACH OF CHILDREN AND PETS. STORE IN A COOL, DRY PLACE.")
    c.drawString(M + 5, y - 39, "DO NOT USE IF PREGNANT OR NURSING. DO NOT OPERATE MACHINERY WHILE USING THIS PRODUCT.")

    y -= (warn_h + 4)
    hline(c, y, M, W - M)
    y -= 3

    # ── Footer: QR + dist ──
    qr_s = 28
    qr_img = generate_qr("https://shopspark8.com", box_size=3)
    c.drawImage(qr_img, M + 2, y - qr_s, width=qr_s, height=qr_s)

    ix = M + qr_s + 8
    c.setFillColor(TXT4)
    c.setFont("Helvetica", 4)
    c.drawString(ix, y - 5, "DISTRIBUTED BY")
    c.setFillColor(TXT)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(ix, y - 13, "SPARK 8")
    c.setFillColor(TXT2)
    c.setFont("Helvetica", 5)
    c.drawString(ix, y - 20, "Smoke Shop & Lounge  ·  Tampa Bay, FL")
    c.setFillColor(TXT3)
    c.setFont("Helvetica", 4.5)
    c.drawString(ix, y - 27, "shopspark8.com")

    # Legal fine print below QR
    c.setFillColor(TXT4)
    c.setFont("Helvetica", 2.5)
    fp_y = y - qr_s - 4
    c.drawString(M + 2, fp_y, "This product has not been evaluated by the FDA and is not intended to diagnose, treat, cure, or prevent any disease.")
    c.drawString(M + 2, fp_y - 4, "Hemp derived. <0.3% Delta-9 THC per dry weight. 2018 Farm Bill compliant. FL Rule 5K-4.034.")


# ════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ════════════════════════════════════════════════════════════
def generate_label(strain="Blue Dream", thc_mg="25", serving_size="1 cartridge (0.5g)",
                   batch="BT-2026-0401", exp_date="08/2027",
                   product_type="cartridge", label_size="medium", output_file=None):

    if output_file is None:
        safe_strain = strain.replace(" ", "_").replace("/", "-")
        output_file = f"label_{safe_strain}_{batch}.pdf"

    if os.path.isabs(output_file):
        out_path = output_file
    else:
        out_path = os.path.join(SCRIPT_DIR, output_file)

    size = SIZES.get(label_size, SIZES["medium"])
    W, H = size["w"], size["h"]

    c = canvas.Canvas(out_path, pagesize=(W, H))

    # White background
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Route to size-specific layout
    if label_size == "small":
        generate_small(c, W, H, strain, thc_mg, serving_size, batch, exp_date, product_type)
    elif label_size == "large":
        generate_large(c, W, H, strain, thc_mg, serving_size, batch, exp_date, product_type)
    else:
        generate_medium(c, W, H, strain, thc_mg, serving_size, batch, exp_date, product_type)

    c.save()
    print(f"Label generated: {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Spark 8 THCa product labels")
    parser.add_argument("--strain", default="Blue Dream", help="Strain name")
    parser.add_argument("--thca", default="25", help="THCa mg per serving")
    parser.add_argument("--serving", default="1 cartridge (0.5g)", help="Serving size")
    parser.add_argument("--batch", default="BT-2026-0401", help="Batch number")
    parser.add_argument("--exp", default="08/2027", help="Expiration date")
    parser.add_argument("--type", default="cartridge", help="Product type")
    parser.add_argument("--size", default="medium", choices=["small", "medium", "large"], help="Label size")
    parser.add_argument("--output", default=None, help="Output filename")
    args = parser.parse_args()

    generate_label(
        strain=args.strain, thc_mg=args.thca, serving_size=args.serving,
        batch=args.batch, exp_date=args.exp, product_type=args.type,
        label_size=args.size, output_file=args.output,
    )
