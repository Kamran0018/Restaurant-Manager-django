"""
receipt_generator.py
────────────────────
Generates a professional A4 PDF receipt for a given Order using ReportLab.

Usage:
    from orders.receipt_generator import build_receipt_pdf
    pdf_bytes = build_receipt_pdf(order)
"""

from io import BytesIO
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable,
)

# ── Restaurant branding (edit freely) ────────────────────────────────────────
RESTAURANT_NAME    = "Restro"
RESTAURANT_TAGLINE = "✦  Premium Dining Experience  ✦"
RESTAURANT_ADDRESS = "123 Gourmet Street, Foodville, India – 560001"
RESTAURANT_PHONE   = "+91 98765 43210"
RESTAURANT_EMAIL   = "hello@restro.com"
RESTAURANT_GST     = "GSTIN: 29ABCDE1234F1Z5"

# ── Colour palette ────────────────────────────────────────────────────────────
C_ORANGE    = colors.HexColor("#FF6F00")
C_ORANGE_LT = colors.HexColor("#FF8F00")
C_RED       = colors.HexColor("#DC2626")
C_DARK      = colors.HexColor("#1A1A2E")
C_WARM_BG   = colors.HexColor("#FFF8F0")
C_ROW_ALT   = colors.HexColor("#FFF3E0")
C_BORDER    = colors.HexColor("#E0E0E0")
C_TEXT      = colors.HexColor("#212529")
C_MUTED     = colors.HexColor("#6C757D")
C_WHITE     = colors.white
C_GREEN     = colors.HexColor("#198754")
C_AMBER     = colors.HexColor("#FFC107")
C_HEADER_BG = colors.HexColor("#FF6F00")   # solid orange banner


# ── Styles ────────────────────────────────────────────────────────────────────
def _s():
    def ps(name, **kw):
        kw.setdefault("fontName",  "Helvetica")
        kw.setdefault("textColor", C_TEXT)
        return ParagraphStyle(name, **kw)

    return {
        # ── Header banner ────────────────────────────────────────
        "brand_name": ps(
            "BrandName",
            fontName="Helvetica-Bold",
            fontSize=32,
            textColor=C_WHITE,
            alignment=TA_CENTER,
            leading=36,
        ),
        "brand_fire": ps(
            "BrandFire",
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=colors.HexColor("#FFE0B2"),
            alignment=TA_CENTER,
            leading=18,
        ),
        "brand_tagline": ps(
            "BrandTagline",
            fontName="Helvetica-Oblique",
            fontSize=10,
            textColor=colors.HexColor("#FFE0B2"),
            alignment=TA_CENTER,
            leading=14,
        ),
        "brand_contact": ps(
            "BrandContact",
            fontSize=8,
            textColor=colors.HexColor("#FFCCBC"),
            alignment=TA_CENTER,
            leading=12,
        ),

        # ── Receipt title strip ───────────────────────────────────
        "receipt_title": ps(
            "ReceiptTitle",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=C_WHITE,
            alignment=TA_CENTER,
        ),

        # ── Section headings ─────────────────────────────────────
        "section_head": ps(
            "SectionHead",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=C_ORANGE,
            spaceBefore=10,
            spaceAfter=5,
        ),

        # ── Info table ───────────────────────────────────────────
        "lbl": ps("Lbl", fontSize=8.5, textColor=C_MUTED),
        "val": ps("Val", fontName="Helvetica-Bold", fontSize=9),

        # ── Items table ──────────────────────────────────────────
        "th": ps("TH", fontName="Helvetica-Bold", fontSize=9,
                 textColor=C_WHITE, alignment=TA_CENTER),
        "td_c": ps("TDC", fontSize=9, alignment=TA_CENTER),
        "td_r": ps("TDR", fontSize=9, alignment=TA_RIGHT),
        "td_l": ps("TDL", fontSize=9, alignment=TA_LEFT),

        # ── Summary & footer ─────────────────────────────────────
        "body":  ps("Body",  fontSize=9),
        "small": ps("Small", fontSize=8,  textColor=C_MUTED),
        "footer": ps(
            "Footer", fontSize=9, textColor=C_MUTED,
            alignment=TA_CENTER, spaceBefore=4,
        ),
        "footer_bold": ps(
            "FooterBold", fontName="Helvetica-Bold", fontSize=11,
            textColor=C_ORANGE, alignment=TA_CENTER, spaceBefore=4,
        ),
        "disclaimer": ps(
            "Disclaimer", fontName="Helvetica-Oblique",
            fontSize=7.5, textColor=C_MUTED,
            alignment=TA_CENTER, spaceBefore=6,
        ),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def _hr(color=C_BORDER, thickness=0.5, before=3, after=3):
    return HRFlowable(
        width="100%", thickness=thickness,
        color=color, spaceBefore=before, spaceAfter=after,
    )


def _info_table(left_pairs, right_pairs, s, col_w=(30, 58, 30, 52)):
    """Two-column label / value grid."""
    rows, n = [], max(len(left_pairs), len(right_pairs))
    for i in range(n):
        lk, lv = left_pairs[i]  if i < len(left_pairs)  else ("", "")
        rk, rv = right_pairs[i] if i < len(right_pairs) else ("", "")
        rows.append([
            Paragraph(lk, s["lbl"]), Paragraph(lv, s["val"]),
            Paragraph(rk, s["lbl"]), Paragraph(rv, s["val"]),
        ])
    t = Table(rows, colWidths=[w*mm for w in col_w])
    t.setStyle(TableStyle([
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
    ]))
    return t


# ── Main builder ─────────────────────────────────────────────────────────────
def build_receipt_pdf(order) -> bytes:
    """Return PDF bytes for the given Order."""
    buf = BytesIO()
    s   = _s()
    MARGIN = 15 * mm
    CONTENT_W = A4[0] - 2 * MARGIN      # usable width in points

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN,  bottomMargin=MARGIN,
        title=f"Receipt – RST{order.pk:04d}",
        author=RESTAURANT_NAME,
    )

    story = []

    # ═══════════════════════════════════════════════════════════════════════
    # 1.  BRANDED HEADER BANNER
    #     Full-width orange table — name + tagline + contact in one block.
    # ═══════════════════════════════════════════════════════════════════════
    # Decorative dots row above name
    deco_top = Paragraph(
        "— ✦ ✦ ✦ —",
        ParagraphStyle("DecoTop", fontName="Helvetica",
                       fontSize=10, textColor=colors.HexColor("#FFE0B2"),
                       alignment=TA_CENTER, leading=14),
    )
    brand_name = Paragraph(
        f"🔥  {RESTAURANT_NAME.upper()}",
        s["brand_name"],
    )
    brand_tagline = Paragraph(RESTAURANT_TAGLINE, s["brand_tagline"])
    brand_contact = Paragraph(
        f"{RESTAURANT_ADDRESS}<br/>"
        f"Tel: {RESTAURANT_PHONE}  |  {RESTAURANT_EMAIL}<br/>"
        f"{RESTAURANT_GST}",
        s["brand_contact"],
    )

    header_inner = Table(
        [[deco_top], [brand_name], [brand_tagline],
         [Spacer(1, 3)], [brand_contact]],
        colWidths=[CONTENT_W],
    )
    header_inner.setStyle(TableStyle([
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 0),
    ]))

    # Outer banner with orange background + rounded appearance via padding
    header_banner = Table(
        [[header_inner]],
        colWidths=[CONTENT_W],
    )
    header_banner.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_HEADER_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("LINEABOVE",     (0,0), (-1,0),  4, C_RED),
        ("LINEBELOW",     (0,-1),(-1,-1), 4, C_RED),
    ]))
    story.append(header_banner)
    story.append(Spacer(1, 1.5*mm))

    # ═══════════════════════════════════════════════════════════════════════
    # 2.  "TAX INVOICE" TITLE STRIP  (dark navy band)
    # ═══════════════════════════════════════════════════════════════════════
    title_strip = Table(
        [[Paragraph("TAX INVOICE  /  ORDER RECEIPT", s["receipt_title"])]],
        colWidths=[CONTENT_W],
    )
    title_strip.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 0),
    ]))
    story.append(title_strip)
    story.append(Spacer(1, 4*mm))

    # ═══════════════════════════════════════════════════════════════════════
    # 3.  ORDER INFORMATION
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("▌ ORDER INFORMATION", s["section_head"]))
    story.append(_hr(C_ORANGE, thickness=1, before=0, after=4))

    try:
        payment    = order.payment
        pay_method = payment.get_payment_method_display()
        pay_status = payment.payment_status.title()
        txn_id     = str(payment.transaction_id)[:22]
    except Exception:
        pay_method = "N/A"
        pay_status = order.payment_status.title()
        txn_id     = "—"

    order_ref = f"RST{order.pk:04d}"

    story.append(_info_table(
        left_pairs=[
            ("Order No.",     order_ref),
            ("Order Date",    order.order_date.strftime("%d %b %Y, %I:%M %p")),
            ("Order Status",  order.get_order_status_display()),
        ],
        right_pairs=[
            ("Payment Method", pay_method),
            ("Payment Status", pay_status),
            ("Transaction ID", txn_id),
        ],
        s=s,
    ))
    story.append(Spacer(1, 3*mm))
    story.append(_hr())

    # ═══════════════════════════════════════════════════════════════════════
    # 4.  CUSTOMER DETAILS
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("▌ CUSTOMER DETAILS", s["section_head"]))
    story.append(_hr(C_ORANGE, thickness=1, before=0, after=4))

    customer  = order.customer
    full_name = customer.get_full_name() or customer.username

    story.append(_info_table(
        left_pairs=[
            ("Name",  full_name),
            ("Email", customer.email or "—"),
        ],
        right_pairs=[
            ("Phone",   getattr(customer, "phone", None) or "—"),
            ("User ID", f"#{customer.pk}"),
        ],
        s=s,
    ))
    story.append(Spacer(1, 2*mm))

    if order.delivery_address:
        addr = order.delivery_address.strip().replace("\n", "  |  ")
        addr_t = Table(
            [[Paragraph("Delivery Address", s["lbl"]),
              Paragraph(addr, s["val"])]],
            colWidths=[30*mm, CONTENT_W - 30*mm],
        )
        addr_t.setStyle(TableStyle([
            ("LEFTPADDING",  (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING",   (0,0), (-1,-1), 2),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ]))
        story.append(addr_t)

    story.append(Spacer(1, 3*mm))
    story.append(_hr())

    # ═══════════════════════════════════════════════════════════════════════
    # 5.  ORDERED ITEMS TABLE
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("▌ ORDERED ITEMS", s["section_head"]))
    story.append(_hr(C_ORANGE, thickness=1, before=0, after=4))

    order_items = order.items.select_related("menu_item").all()

    col_w = [10*mm, 83*mm, 15*mm, 28*mm, 29*mm]
    tdata = [[
        Paragraph("#",          s["th"]),
        Paragraph("Item Name",  s["th"]),
        Paragraph("Qty",        s["th"]),
        Paragraph("Unit Price", s["th"]),
        Paragraph("Total",      s["th"]),
    ]]
    for idx, item in enumerate(order_items, 1):
        name = item.menu_item.name if item.menu_item else "Deleted Item"
        tdata.append([
            Paragraph(str(idx),            s["td_c"]),
            Paragraph(name,                s["td_l"]),
            Paragraph(str(item.quantity),  s["td_c"]),
            Paragraph(f"₹{item.price:.2f}",    s["td_r"]),
            Paragraph(f"₹{item.subtotal:.2f}", s["td_r"]),
        ])

    items_t = Table(tdata, colWidths=col_w, repeatRows=1)
    items_t.setStyle(TableStyle([
        # Header row
        ("BACKGROUND",    (0,0),  (-1,0),  C_ORANGE),
        ("LINEBELOW",     (0,0),  (-1,0),  2, C_RED),
        ("TOPPADDING",    (0,0),  (-1,0),  8),
        ("BOTTOMPADDING", (0,0),  (-1,0),  8),
        # Data rows
        ("ROWBACKGROUNDS",(0,1),  (-1,-1), [C_WHITE, C_ROW_ALT]),
        ("FONTSIZE",      (0,1),  (-1,-1), 9),
        ("TOPPADDING",    (0,1),  (-1,-1), 5),
        ("BOTTOMPADDING", (0,1),  (-1,-1), 5),
        # Common
        ("LEFTPADDING",   (0,0),  (-1,-1), 6),
        ("RIGHTPADDING",  (0,0),  (-1,-1), 6),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
        # Grid
        ("GRID",          (0,0),  (-1,-1), 0.4, C_BORDER),
        ("LINEBELOW",     (0,-1), (-1,-1), 1.5, C_ORANGE),
    ]))
    story.append(items_t)
    story.append(Spacer(1, 4*mm))

    # ═══════════════════════════════════════════════════════════════════════
    # 6.  PRICING SUMMARY
    # ═══════════════════════════════════════════════════════════════════════
    subtotal    = order.total_amount / Decimal("1.05")
    tax         = order.total_amount - subtotal
    grand_total = order.total_amount

    def _ps(name, **kw):
        kw.setdefault("fontName", "Helvetica")
        kw.setdefault("textColor", C_TEXT)
        return ParagraphStyle(name, **kw)

    sum_lbl  = _ps("SumLbl", fontSize=9)
    sum_val  = _ps("SumVal", fontSize=9, alignment=TA_RIGHT)
    tot_lbl  = _ps("TotLbl", fontName="Helvetica-Bold", fontSize=11)
    tot_val  = _ps("TotVal", fontName="Helvetica-Bold", fontSize=12,
                   textColor=C_ORANGE, alignment=TA_RIGHT)
    free_val = _ps("FreeVal", fontName="Helvetica-Bold", fontSize=9,
                   textColor=C_GREEN, alignment=TA_RIGHT)

    sum_data = [
        [Paragraph("Subtotal",                         sum_lbl), Paragraph(f"₹{subtotal:.2f}", sum_val)],
        [Paragraph("GST & Restaurant Charges (5%)",    sum_lbl), Paragraph(f"₹{tax:.2f}",      sum_val)],
        [Paragraph("Delivery Charges",                 sum_lbl), Paragraph("FREE",              free_val)],
        [Paragraph("GRAND TOTAL",                      tot_lbl), Paragraph(f"₹{grand_total:.2f}", tot_val)],
    ]

    sum_t = Table(sum_data, colWidths=[100*mm, 65*mm])
    sum_t.setStyle(TableStyle([
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("LINEABOVE",     (0,-1), (-1,-1), 1.5, C_ORANGE),
        ("BACKGROUND",    (0,-1), (-1,-1),  C_WARM_BG),
    ]))

    # Push summary to the right
    wrapper = Table([[None, sum_t]], colWidths=[CONTENT_W - 165*mm, 165*mm])
    wrapper.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
    ]))
    story.append(wrapper)
    story.append(Spacer(1, 5*mm))

    # ═══════════════════════════════════════════════════════════════════════
    # 7.  SPECIAL INSTRUCTIONS (if any)
    # ═══════════════════════════════════════════════════════════════════════
    if order.special_instructions and order.special_instructions.strip():
        story.append(_hr())
        story.append(Paragraph("▌ SPECIAL INSTRUCTIONS", s["section_head"]))
        story.append(_hr(C_ORANGE, thickness=1, before=0, after=4))
        story.append(Paragraph(order.special_instructions.strip(), s["body"]))
        story.append(Spacer(1, 3*mm))

    # ═══════════════════════════════════════════════════════════════════════
    # 8.  FOOTER BANNER
    # ═══════════════════════════════════════════════════════════════════════
    footer_content = Table(
        [
            [Paragraph("🙏  Thank You for Dining with Us!", s["footer_bold"])],
            [Paragraph(
                "We hope you enjoyed your meal. We look forward to serving you again!",
                s["footer"],
            )],
            [Spacer(1, 4)],
            [Paragraph(
                f"{RESTAURANT_NAME}  •  {RESTAURANT_PHONE}  •  {RESTAURANT_EMAIL}",
                s["footer"],
            )],
            [Paragraph(
                "✦  Visit us again soon  ✦",
                ParagraphStyle("VisitAgain", fontName="Helvetica-Oblique",
                               fontSize=9, textColor=C_ORANGE,
                               alignment=TA_CENTER, spaceBefore=2),
            )],
        ],
        colWidths=[CONTENT_W],
    )
    footer_content.setStyle(TableStyle([
        ("TOPPADDING",    (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 0),
    ]))

    footer_banner = Table([[footer_content]], colWidths=[CONTENT_W])
    footer_banner.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_WARM_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("LINEABOVE",     (0,0), (-1,0),  3, C_ORANGE),
        ("LINEBELOW",     (0,-1),(-1,-1), 3, C_ORANGE),
    ]))
    story.append(footer_banner)
    story.append(Spacer(1, 3*mm))

    # Disclaimer line
    story.append(Paragraph(
        "This is a computer-generated receipt and does not require a signature.",
        s["disclaimer"],
    ))

    # ── Build ────────────────────────────────────────────────────────────────
    doc.build(story)
    return buf.getvalue()
