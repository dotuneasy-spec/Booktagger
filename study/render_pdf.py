"""Render the Lagos multi-service agency feasibility study to PDF."""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Flowable,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model  # noqa: E402

FONT = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("Lib", f"{FONT}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Lib-Bold", f"{FONT}/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Lib-Italic", f"{FONT}/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Serif", f"{FONT}/LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold", f"{FONT}/LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic", f"{FONT}/LiberationSerif-Italic.ttf"))

INK = HexColor("#1C2B33")
BRASS = HexColor("#8C6239")
GREEN = HexColor("#1E5C45")
BLUE = HexColor("#1F4E79")
RED = HexColor("#8C3A32")
MUTED = HexColor("#5C6B73")
RULE = HexColor("#E3DCD1")
PAPER = HexColor("#F4F0E8")
ROW = HexColor("#F7F4EF")
LINE = HexColor("#D9D1C5")

PAGE_W, PAGE_H = A4
LEFT = 16 * mm
RIGHT = 16 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT


def N(n):
    return model.ngn(n)


def M(n):
    n = float(n)
    sign = "−" if n < 0 else ""
    a = abs(n)
    if a >= 1_000_000:
        return f"{sign}₦{a / 1_000_000:.2f} million"
    return N(n)


def Mp(n):
    """Compact millions for tables."""
    n = float(n)
    if n < 0:
        return f"({abs(n) / 1_000_000:.2f})"
    return f"{n / 1_000_000:.2f}"


def styles():
    s = {}
    s["h1"] = ParagraphStyle(
        "h1", fontName="Serif-Bold", fontSize=16, leading=19,
        textColor=INK, spaceBefore=2, spaceAfter=6,
    )
    s["h2"] = ParagraphStyle(
        "h2", fontName="Lib-Bold", fontSize=11.5, leading=14,
        textColor=BRASS, spaceBefore=11, spaceAfter=4,
    )
    s["h3"] = ParagraphStyle(
        "h3", fontName="Lib-Bold", fontSize=10, leading=13,
        textColor=INK, spaceBefore=8, spaceAfter=3,
    )
    s["body"] = ParagraphStyle(
        "body", fontName="Lib", fontSize=9.2, leading=12.6,
        textColor=INK, spaceAfter=6, alignment=TA_LEFT,
    )
    s["bodyj"] = ParagraphStyle(
        "bodyj", parent=s["body"], alignment=TA_JUSTIFY,
    )
    s["small"] = ParagraphStyle(
        "small", fontName="Lib", fontSize=8, leading=10.6,
        textColor=INK, spaceAfter=4,
    )
    s["note"] = ParagraphStyle(
        "note", fontName="Lib-Italic", fontSize=8, leading=10.6,
        textColor=MUTED, spaceBefore=2, spaceAfter=6,
    )
    s["call"] = ParagraphStyle(
        "call", fontName="Lib", fontSize=9, leading=12.2,
        textColor=INK,
    )
    s["th"] = ParagraphStyle(
        "th", fontName="Lib-Bold", fontSize=7.4, leading=9.2,
        textColor=white, alignment=TA_LEFT,
    )
    s["thr"] = ParagraphStyle(
        "thr", parent=s["th"], alignment=TA_RIGHT,
    )
    s["td"] = ParagraphStyle(
        "td", fontName="Lib", fontSize=7.6, leading=9.6, textColor=INK,
    )
    s["tdr"] = ParagraphStyle(
        "tdr", parent=s["td"], alignment=TA_RIGHT,
    )
    s["tdb"] = ParagraphStyle(
        "tdb", fontName="Lib-Bold", fontSize=7.6, leading=9.6, textColor=INK,
    )
    s["tdbr"] = ParagraphStyle(
        "tdbr", parent=s["tdb"], alignment=TA_RIGHT,
    )
    s["bullet"] = ParagraphStyle(
        "bullet", fontName="Lib", fontSize=9, leading=12.2,
        textColor=INK, leftIndent=0,
    )
    s["cover_kicker"] = ParagraphStyle(
        "cover_kicker", fontName="Lib", fontSize=8.5, leading=11,
        textColor=BRASS, tracking=0.6,
    )
    s["footer"] = ParagraphStyle(
        "footer", fontName="Lib", fontSize=7.5, leading=9, textColor=MUTED,
    )
    return s


S = styles()


class Rule(Flowable):
    def __init__(self, color=BRASS, weight=1.0, space_before=2, space_after=8):
        super().__init__()
        self.color = color
        self.weight = weight
        self.space_before = space_before
        self.space_after = space_after

    def wrap(self, aw, ah):
        self.aw = aw
        return aw, self.space_before + self.weight + self.space_after

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.weight)
        y = self.space_after
        self.canv.line(0, y, self.aw, y)


class Callout(Flowable):
    def __init__(self, paragraphs, width=None, accent=BRASS):
        super().__init__()
        self.paragraphs = paragraphs
        self.box_w = width or CONTENT_W
        self.accent = accent
        self._heights = []

    def wrap(self, aw, ah):
        self.box_w = aw
        inner = aw - 18
        self._heights = []
        total = 8
        for p in self.paragraphs:
            w, h = p.wrap(inner, ah)
            self._heights.append(h)
            total += h + 3
        total += 6
        self.height = total
        return aw, total

    def draw(self):
        c = self.canv
        c.setFillColor(PAPER)
        c.roundRect(0, 0, self.box_w, self.height, 3, fill=1, stroke=0)
        c.setFillColor(self.accent)
        c.rect(0, 0, 3.2, self.height, fill=1, stroke=0)
        y = self.height - 8
        for p, h in zip(self.paragraphs, self._heights):
            y -= h
            p.drawOn(c, 12, y)
            y -= 3


class GroupedBars(Flowable):
    def __init__(self, labels, base_vals, best_vals, width=None, height=168):
        super().__init__()
        self.labels = labels
        self.base_vals = base_vals
        self.best_vals = best_vals
        self.box_w = width or CONTENT_W
        self.box_h = height

    def wrap(self, aw, ah):
        self.box_w = aw
        return aw, self.box_h

    def draw(self):
        c = self.canv
        left, bottom = 32, 22
        plot_w = self.box_w - left - 6
        plot_h = self.box_h - bottom - 18
        peak = max(list(self.base_vals) + list(self.best_vals)) * 1.18
        c.setStrokeColor(LINE)
        c.setFillColor(MUTED)
        c.setFont("Lib", 7)
        for frac in (0, 0.5, 1):
            y = bottom + plot_h * frac
            c.setStrokeColor(LINE)
            c.line(left, y, left + plot_w, y)
            c.setFillColor(MUTED)
            c.drawRightString(left - 4, y - 2, f"{peak * frac / 1e6:.0f}")
        n = len(self.labels)
        group = plot_w / n
        bar = min(16, group * 0.28)
        for i, label in enumerate(self.labels):
            cx = left + group * i + group / 2
            for val, dx, color in (
                (self.base_vals[i], -bar - 1.5, GREEN),
                (self.best_vals[i], 1.5, BLUE),
            ):
                h = 0 if peak == 0 else plot_h * val / peak
                c.setFillColor(color)
                c.rect(cx + dx, bottom, bar, h, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont("Lib", 8)
            c.drawCentredString(cx, 6, label)
        c.setFillColor(GREEN)
        c.rect(left, self.box_h - 11, 8, 8, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Lib", 8)
        c.drawString(left + 12, self.box_h - 10, "Base case")
        c.setFillColor(BLUE)
        c.rect(left + 78, self.box_h - 11, 8, 8, fill=1, stroke=0)
        c.setFillColor(INK)
        c.drawString(left + 90, self.box_h - 10, "Best case")
        c.setFillColor(MUTED)
        c.setFont("Lib", 7)
        c.drawRightString(left + plot_w, self.box_h - 10, "₦ million")


class CashPanel(Flowable):
    def __init__(self, series, title, color, width, height=150):
        super().__init__()
        self.series = series
        self.title = title
        self.color = color
        self.box_w = width
        self.box_h = height

    def wrap(self, aw, ah):
        return self.box_w, self.box_h

    def draw(self):
        c = self.canv
        left, bottom = 30, 18
        plot_w = self.box_w - left - 4
        plot_h = self.box_h - bottom - 16
        vals = self.series
        peak = max(vals) * 1.12
        floor = 0
        span = peak - floor
        c.setFillColor(INK)
        c.setFont("Lib-Bold", 8)
        c.drawString(0, self.box_h - 10, self.title)
        c.setStrokeColor(LINE)
        c.setFillColor(MUTED)
        c.setFont("Lib", 6.5)
        for frac in (0, 0.5, 1):
            y = bottom + plot_h * frac
            c.setStrokeColor(LINE)
            c.line(left, y, left + plot_w, y)
            c.setFillColor(MUTED)
            c.drawRightString(left - 3, y - 2, f"{(floor + span * frac) / 1e6:.1f}")
        path = []
        for i, v in enumerate(vals):
            x = left + plot_w * (i / (len(vals) - 1))
            y = bottom + plot_h * ((v - floor) / span)
            path.append((x, y))
        c.setStrokeColor(self.color)
        c.setLineWidth(1.4)
        c.setLineJoin(1)
        p = c.beginPath()
        p.moveTo(path[0][0], path[0][1])
        for x, y in path[1:]:
            p.lineTo(x, y)
        c.drawPath(p, stroke=1, fill=0)
        c.setFillColor(self.color)
        c.circle(path[0][0], path[0][1], 1.6, fill=1, stroke=0)
        c.circle(path[-1][0], path[-1][1], 1.6, fill=1, stroke=0)
        c.setFillColor(MUTED)
        c.setFont("Lib", 6.5)
        c.drawString(left, 4, "Oct 2026")
        c.drawRightString(left + plot_w, 4, "Sep 2031")


def P(text, style="body"):
    return Paragraph(text, S[style] if isinstance(style, str) else style)


def callout(text, accent=BRASS):
    return Callout([P(text, "call")], accent=accent)


def bullets(items):
    flow = []
    for item in items:
        flow.append(Paragraph(f"•  {item}", S["bullet"]))
        flow.append(Spacer(1, 2))
    return flow


def table(headers, rows, widths, emphasizes=None, font_size=7.6):
    emphasizes = emphasizes or set()
    head = []
    for i, h in enumerate(headers):
        style = S["thr"] if i else S["th"]
        head.append(Paragraph(h, style))
    data = [head]
    for r_i, row in enumerate(rows):
        built = []
        bold = r_i in emphasizes
        for c_i, cell in enumerate(row):
            if c_i == 0:
                st = S["tdb"] if bold else S["td"]
            else:
                st = S["tdbr"] if bold else S["tdr"]
            built.append(Paragraph(str(cell), st))
        data.append(built)
    tbl = Table(data, colWidths=widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Lib-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LINEBELOW", (0, 1), (-1, -2), 0.2, LINE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, INK),
    ]
    for r_i in range(1, len(data)):
        if (r_i - 1) in emphasizes:
            style_cmds.append(("BACKGROUND", (0, r_i), (-1, r_i), PAPER))
        elif r_i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, r_i), (-1, r_i), ROW))
    tbl.setStyle(TableStyle(style_cmds))
    return tbl


def draw_cover(c, doc):
    c.saveState()
    c.setFillColor(INK)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(BRASS)
    c.rect(0, PAGE_H - 8, PAGE_W, 8, fill=1, stroke=0)
    c.setFillColor(BRASS)
    c.setFont("Lib", 8.5)
    c.drawString(LEFT, PAGE_H - 36, "WORKING PAPER  ·  SEPTEMBER 2026")
    c.setFillColor(white)
    c.setFont("Serif-Bold", 28)
    y = PAGE_H - 92
    for line in ("Feasibility study",):
        c.drawString(LEFT, y, line)
        y -= 34
    c.setFont("Serif", 16)
    c.setFillColor(HexColor("#F3E6D4"))
    c.drawString(LEFT, y - 6, "A Lagos multi-service agency")
    c.setFont("Lib", 11)
    c.setFillColor(HexColor("#D5DDD8"))
    c.drawString(LEFT, y - 28, "From the minimum cheque to a five-year view")
    c.setStrokeColor(BRASS)
    c.setLineWidth(1)
    c.line(LEFT, y - 48, LEFT + 86, y - 48)

    c.setFillColor(HexColor("#D5DDD8"))
    c.setFont("Lib", 9.5)
    text = (
        "Base case and best case for a hired-hand practice: short jobs for offices,",
        "shops, and schools, plus a capped estate retainer. Painters and electricians",
        "are called per job. Salaries start only after prepaid fees cover them.",
    )
    ty = y - 74
    for line in text:
        c.drawString(LEFT, ty, line)
        ty -= 14

    # metric cards
    cards = [
        ("Business cheque, base", "₦1.15 million"),
        ("Year-1 invoices, base", "₦7.63 million"),
        ("Year-5 invoices, base", "₦62.2 million"),
    ]
    card_w = (CONTENT_W - 16) / 3
    card_h = 62
    card_y = 78
    for i, (label, value) in enumerate(cards):
        x = LEFT + i * (card_w + 8)
        c.setFillColor(HexColor("#243843"))
        c.roundRect(x, card_y, card_w, card_h, 4, fill=1, stroke=0)
        c.setFillColor(BRASS)
        c.setFont("Lib", 7.4)
        c.drawString(x + 10, card_y + 40, label.upper())
        c.setFillColor(white)
        c.setFont("Serif-Bold", 12)
        c.drawString(x + 10, card_y + 16, value)

    c.setFillColor(HexColor("#9AABAB"))
    c.setFont("Lib", 8)
    c.drawString(LEFT, 48, "October 2026  –  September 2031")
    c.drawRightString(PAGE_W - RIGHT, 48, "All figures in Nigerian naira")
    c.restoreState()


def draw_body(c, doc):
    c.saveState()
    c.setFillColor(BRASS)
    c.rect(0, PAGE_H - 6, PAGE_W, 6, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("Lib", 7.5)
    c.drawString(LEFT, PAGE_H - 20, "LAGOS MULTI-SERVICE AGENCY")
    c.drawRightString(PAGE_W - RIGHT, PAGE_H - 20, "Feasibility study  ·  September 2026")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.line(LEFT, PAGE_H - 26, PAGE_W - RIGHT, PAGE_H - 26)
    c.line(LEFT, 32, PAGE_W - RIGHT, 32)
    c.setFillColor(MUTED)
    c.setFont("Lib", 7.5)
    c.drawString(LEFT, 20, "Planning model. Not a forecast, a quotation, or a financing offer.")
    c.drawRightString(PAGE_W - RIGHT, 20, str(c.getPageNumber()))
    c.restoreState()


def h2(text):
    return KeepTogether([P(text, "h2"), Rule(BRASS, 0.6, 0, 6)])


def pnl_rows(res):
    years = res["years"]
    lines = [
        ("Invoices", "revenue", False),
        ("Refresh jobs", "refresh_rev", False),
        ("Stand-up jobs", "standup_rev", False),
        ("Launch jobs", "launch_rev", False),
        ("Extras on retainers", "extras_rev", False),
        ("Estate retainers", "retainer_rev", False),
        ("In-unit care plans", "care_rev", False),
        ("Direct cost of delivery", "cogs", False),
        ("Contribution", "contribution", True),
        ("Rework reserve", "rework", False),
        ("Jobs not collected", "bad", False),
        ("Bank and transfer leakage", "bank", False),
        ("Operating costs", "opex", False),
        ("Founder draw", "founder", False),
        ("Salaried staff, loaded", "staff", False),
        ("Formation and set-up", "setup", False),
        ("Profit before tax", "pbt", True),
        ("Tax charge", "tax", False),
        ("Profit after tax", "pat", True),
    ]
    rows = []
    emph = set()
    for i, (label, key, emp) in enumerate(lines):
        row = [label]
        for y in years:
            row.append(N(y[key]))
        rows.append(row)
        if emp:
            emph.add(i)
    return rows, emph


def cash_rows(res):
    rows = []
    emph = set()
    labels = [
        ("Cash at 1 October", "cash_start", False),
        ("Collected from clients", "cash_in", False),
        ("Withholding tax kept by clients", "wht", False),
        ("Paid out for work and overhead", "cash_out", False),
        ("Company tax paid in cash", "tax_cash", False),
        ("Cash at 30 September", "cash_end", True),
        ("Withholding credit still unused", "wht_credit_end", False),
    ]
    for i, (label, key, emp) in enumerate(labels):
        row = [label]
        for y in res["years"]:
            row.append(N(y[key]))
        rows.append(row)
        if emp:
            emph.add(i)
    return rows, emph


def build_story(pack):
    base = pack["base"]
    best = pack["best"]
    under = pack["under"]
    delayed = pack["delayed"]
    thin = pack["thin"]
    creep = pack["creep"]
    death = pack["death"]
    weak = model.simulate(
        "Weak collections",
        model.base_months(),
        1_150_000,
        **{**model.BASE_RATES, "bad_rate": 0.08, "slip_rate": 0.25},
    )
    story = [NextPageTemplate("body"), PageBreak()]

    by = base["years"]
    zy = best["years"]
    story += decision(base, best, under, death)
    story.append(PageBreak())
    story += how_to_read()
    story += the_firm()
    story += market()
    story += minimum_entry(base, under)
    story += unit_economics()
    story += scenarios(base, best)
    story.append(PageBreak())
    story += five_year(base, best)
    story += year_one(base, best)
    story += gates(base, best)
    story += tax_section(base, best)
    story.append(PageBreak())
    story += salary_failure(death)
    story += sensitivities(base, delayed, thin, creep, weak)
    story += ninety_days()
    story += decision_rules(base, best)
    story.append(PageBreak())
    story += appendix_pnl(base, best)
    story += appendix_assumptions()
    story += sources()
    return story


def decision(base, best, under, death):
    by, zy = base["years"], best["years"]
    bits = [P("1  ·  The decision", "h1"), Rule()]
    bits.append(P(
        f"This agency can be started as a small contracting firm with a bench of hired hands. "
        f"The base plan needs <b>{N(base['opening'])}</b> in the business account. "
        f"That cheque keeps the balance above {N(200_000)} through the hardest month, "
        f"{base['min_cash_label']}, when the model still has <b>{N(base['min_cash'])}</b>."
    ))
    bits.append(P(
        f"A start funded with only {N(500_000)} pays for registration, contracts, tools, and three trial jobs, "
        f"and is overdrawn in {under['rows'][2]['label']}. The low point on that path is "
        f"<b>{N(under['min_cash'])}</b> in {under['min_cash_label']}. "
        f"That sum is enough to open the file. It is not enough to trade through the first year of this plan."
    ))
    bits.append(P(
        f"Living costs sit outside that cheque. At {N(model.HOUSEHOLD)} a month, and with the base draw at zero "
        f"for six months and {N(80_000)} for the next six, the household needs a further "
        f"<b>{N(base['household_gap_y1'])}</b> during year 1. Family support or another income covers that. "
        f"The company account should not."
    ))
    headers = ["", "Base case", "Best case"]
    w = [CONTENT_W * 0.40, CONTENT_W * 0.30, CONTENT_W * 0.30]
    rows = [
        ["Business cash required", N(base["opening"]), N(best["opening"])],
        ["Lowest cash in 60 months", N(base["min_cash"]), N(best["min_cash"])],
        ["When that low falls", base["min_cash_label"], best["min_cash_label"]],
        ["Year-1 invoices", N(by[0]["revenue"]), N(zy[0]["revenue"])],
        ["Year-1 profit after tax", N(by[0]["pat"]), N(zy[0]["pat"])],
        ["Year-5 invoices", N(by[4]["revenue"]), N(zy[4]["revenue"])],
        ["Year-5 profit after tax", N(by[4]["pat"]), N(zy[4]["pat"])],
        ["Cash in the firm at year 5", N(base["ending_cash"]), N(best["ending_cash"])],
        ["Founder drawings, five years", N(base["cumulative_founder"]), N(best["cumulative_founder"])],
        ["Profit left in the firm, five years", N(base["cumulative_pat"]), N(best["cumulative_pat"])],
        ["Household top-up in year 1", N(base["household_gap_y1"]), N(best["household_gap_y1"])],
    ]
    bits.append(Spacer(1, 4))
    bits.append(table(headers, rows, w, emphasizes={4, 6, 7}))
    bits.append(Spacer(1, 8))
    bits.append(callout(
        f"The best case is a ceiling. It happens if a property manager is sending paid work by January 2027 "
        f"and an estate is on a pilot by March 2027, at higher package prices. Fund the base cheque of "
        f"{N(base['opening'])} anyway. The smaller best-case cheque of {N(best['opening'])} works only when that early channel appears."
    ))
    bits.append(Spacer(1, 6))
    death_m2 = death["rows"][1]
    bits.append(P(
        f"Paying a supervisor, an electrician, and a plumber a salary from October 2026, on the same sales, "
        f"uses up the base cheque in the second month. By {death_m2['label']} the account is "
        f"<b>{N(death_m2['cash_end'])}</b>. At the end of year 1 it is <b>{N(death['years'][0]['cash_end'])}</b>. "
        f"The cash covers salaries only after the fees are prepaid and the work is capped. The model reaches that "
        f"point with one supervisor in October 2027, and with one electrician in June 2030. It does not reach it in month one."
    ))
    bits.append(P(
        "The rest of this paper shows the offers, the month-by-month first year, the hiring tests, the tax line, "
        "and the ways the plan fails. The appendix holds the full statements.",
        "note",
    ))
    return bits


def how_to_read():
    bits = [P("2  ·  How to read the numbers", "h1"), Rule()]
    bits.append(P(
        "Year 1 is October 2026 to September 2027. Year 5 ends in September 2031. "
        "Figures are nominal naira of each year. Prices and pay step up as the years pass, by roughly the amount "
        "already built into the price cards. There is no separate inflation index, and a naira in 2031 is not given "
        "a 2026 purchasing-power equivalent. Treat the later cash balances as future naira."
    ))
    bits.append(P(
        "Invoices are recognised in the month of the job. Clients on one-off work pay a 60 percent deposit before "
        "work starts. The model then collects most of the balance in the same month, lets 12 percent slip into the "
        "next month in the base case, and writes off 2 percent. Estate retainers and care plans are collected in "
        "advance. Artisans and material suppliers are paid in the month of the job, which is what creates the need for a float."
    ))
    bits.append(P(
        "Contribution is what remains after materials, bench labour, and the ordinary cost of doing that job. "
        "It is the pool that pays the founder, the accountant, transport, later salaries, rework, and tax. "
        "A salaried supervisor is not buried inside contribution. Once hired, that person is a monthly cost of their own, "
        "loaded at 1.18 times the target pay to allow for pension, NSITF, and the gap between take-home and company cost. "
        "That 1.18 is an allowance, not a payroll run."
    ))
    bits.append(P(
        "Two paths are fully worked. The base path is the plan to fund: mainland prices, a slow first year, one estate "
        "from July 2027, a second estate in year 4, care plans only inside the first estate. The best path brings a "
        "property-manager channel and higher prices forward, and adds a third estate late. Sensitivities are partial "
        "reruns of the base path, not new strategies."
    ))
    bits.append(callout(
        "Every total in the statements ties back to a monthly engine. Cash plus the last month’s uncollected balance "
        "plus unused withholding-tax certificates equals the opening cheque plus profit after tax. That check closes "
        "to the naira on every path in this paper. It is a check of arithmetic, not of whether Lagos clients will buy."
    ))
    return bits


def the_firm():
    bits = [P("3  ·  The firm this study prices", "h1"), Rule()]
    bits.append(P(
        "The firm sells short, packaged pieces of work to private clients in Lagos, and a thin monthly cover to one "
        "estate at a time. The founder keeps the client, the price, and the standard. Hired hands do the trade. "
        "They are engaged for a day or for a job, paid on the day that was promised, and released when the quality drops."
    ))
    bits.append(h2("What is sold"))
    headers = ["Offer", "Length", "Who buys it", "How it is priced in year 1"]
    rows = [
        ["Refresh", "1–3 days", "Office, shop, flat, school", f"About {N(170_000)}–{N(180_000)} after the proof jobs"],
        ["Stand-up", "5–10 days", "A space that must be usable", f"About {N(500_000)}–{N(560_000)}"],
        ["Launch", "7–14 days", "An opening that also needs to be seen", "Not in base year 1. First one in year 2"],
        ["Estate retainer", "Monthly", "Residents’ association or managing agent", f"Pilot {N(150_000)}, then about {N(200_000)}"],
        ["Care plan", "Monthly per flat", "Landlord or managing agent", f"From {N(32_000)} in year 2, inside one estate"],
        ["Extras", "As quoted", "The same estate clients", "Outside the retainer, at job rates"],
    ]
    bits.append(table(headers, rows, [78, 70, 150, CONTENT_W - 298]))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "A refresh is a room painted, points made safe, a handover clean, a small air-conditioner service. "
        "A stand-up is the same idea across a whole small office or shop. A launch adds signage and a handover that "
        "a client can photograph. The retainer buys a named response and a short list of small works, not a resident technician. "
        "The care plan buys a cap: a set number of small tickets, a monthly look, weekday response. Materials above a cap, "
        "a new air-conditioner, a full repaint, a rewire, and anything structural are quoted as extras."
    ))
    bits.append(h2("What the retainer includes"))
    headers = ["Inside the monthly fee", "Quoted extra"]
    rows = [
        ["A scheduled walk-through", "A full repaint or renovation"],
        ["Small electrical and plumbing fixes under the cap", "Supply and installation of a new air-conditioner"],
        ["Common-area touch-up", "Generator overhaul, roof, structure"],
        ["Handover clean when a tenant leaves, if listed", "A second clean or a deep clean outside the list"],
        ["Priority response inside agreed hours", "Night and weekend emergencies"],
        ["One short report to the facility desk", "Materials above the cap"],
    ]
    bits.append(table(headers, rows, [CONTENT_W * 0.50, CONTENT_W * 0.50]))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "The base pilot is three months at ₦150,000, labour for the listed small works included, materials on receipt. "
        "After the pilot the fee steps up only if the estate keeps the scope tight. A whole luxury estate on a full "
        "facilities contract is a different product and is outside both paths."
    ))
    bits.append(h2("Who does the work"))
    bits.append(P(
        "The opening bench is about eight to twelve people, of whom three to five are on any one job: electrician, "
        "painter, tiler or carpenter, air-conditioner technician, a driver with a small van, a cleaner supervisor with two hands, "
        "and a printer for signage. A bookkeeper is an external monthly fee inside operating costs, not a seat in the office. "
        "There is no office in either path. The founder works from home, from sites, and from the estate."
    ))
    bits.append(P(
        "Three numbers are kept for each trade. Each person has a one-page job agreement: scope, rate, dates, who buys materials, "
        "payment after inspection, no direct dealing with the client, and a clear statement that they are not staff. "
        "Five to ten percent of a job can be held until the client signs off. One unexplained no-show moves a name to the bottom of the list. A second removes it."
    ))
    return bits


def market():
    bits = [P("4  ·  Where this sits in Lagos", "h1"), Rule()]
    bits.append(P(
        "Lagos already buys this kind of work under other names. Integrated facilities firms run cleaning, electrical, "
        "air-conditioning, plumbing, and small works for banks, malls, and large estates, often with their own payroll and tender desks. "
        "On-demand platforms and WhatsApp fixers send a tradesperson to a flat. Branding studios and event houses make a space visible, "
        "and rarely touch the electrics. Boutique property managers collect rent for landlords and dislike chasing painters."
    ))
    headers = ["Neighbourhood", "What they already do", "What this firm takes from them"]
    rows = [
        ["Large facilities firms", "One invoice and a written scope for a whole building", "The single invoice and plain scope language, on a five-to-fourteen-day job"],
        ["On-demand fixers", "Speed on WhatsApp for homes and small offices", "A fast reply and a bench, under a name the client can call back"],
        ["Branding and event studios", "Print, signage, and a handover that looks finished", "That finish, sold with the repair rather than after it"],
        ["Boutique property managers", "The landlord relationship", "The week of work, in their name or in this firm’s, for a referral or a markup"],
    ]
    bits.append(table(headers, rows, [110, 175, CONTENT_W - 285]))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "The opening the model is built for is the job those firms pass over: an office, shop, school, or flat that needs to be "
        "safe, clean, and presentable inside two weeks, and an estate that wants a capped crew on call without hiring a full facilities contractor. "
        "Public tenders, oil-and-gas vendors, and a salaried general manager are outside the five-year plan."
    ))
    bits.append(P(
        "Names such as Alpha Mead, UPDC Facility Management, Westlink, Anyworkman, and the smaller Lekki and Ikeja property desks "
        "are markers for those neighbourhoods. This study does not report their fees or their results, and it does not assume any of them will partner."
    , "note"))
    bits.append(P(
        "A small office in Lagos often pays a large firm something in the range of ₦120,000 to ₦500,000 a month for bundled facilities cover. "
        "The retainer in this model sits under that, because the scope is a list of small works plus a walk-through, not a man at the gatehouse. "
        "An in-unit plan of roughly ₦30,000 to ₦45,000 a flat is the band used for landlords. Mainland estates will resist the top of that band. "
        "A landlord who lives abroad and already hates phone calls is the easier first buyer of a care plan."
    ))
    return bits


def minimum_entry(base, under):
    bits = [P("5  ·  The minimum entry", "h1"), Rule()]
    bits.append(P(
        "“Minimum” is three different sums. Mixing them up is how a founder runs out of cash in December and calls the idea unworkable."
    ))
    headers = ["Cheque", "Amount", "What it is for"]
    rows = [
        ["Day-one set-up", N(295_000), "Business name, two contracts, accountant’s chart, profile, tools, three paid trials"],
        ["Business account, base plan", N(base["opening"]), "Set-up, the limited-company upgrade in June 2027, and the float"],
        ["Household, year 1", N(base["household_gap_y1"]), "Rent, food, and transport for the founder when the draw does not yet cover ₦150,000"],
    ]
    bits.append(table(headers, rows, [130, 90, CONTENT_W - 220], emphasizes={1}))
    bits.append(Spacer(1, 6))
    bits.append(P(
        f"Put {N(base['opening'])} in the company account before the first quote goes out. "
        f"Of that, {N(295_000)} is the day-one set-up below, and {N(120_000)} is reserved for upgrading from a business name "
        f"to a limited company in June 2027, before an estate signs. The rest is float. It pays artisans and materials in the gap "
        f"between a deposit and the final collection, and it absorbs a first year that loses {N(abs(base['years'][0]['pat']))}."
    ))
    bits.append(h2("Day-one set-up, base path"))
    headers = ["Item", "Allowance", "Why it is in the cheque"]
    rows = [
        ["CAC business name and TIN", N(40_000), "So invoices have a legal name from month one"],
        ["Client contract and hired-hand agreement", N(100_000), "One commercial lawyer, two templates that will be reused"],
        ["Accountant: chart of accounts", N(25_000), "Float separated from profit, from the first job"],
        ["Profile, cards, WhatsApp Business", N(25_000), "Enough to be found. A brand campaign is not in the plan"],
        ["Tools and basic protection", N(60_000), "A tester, simple access, PPE. Trades bring their own tools"],
        ["Three paid trials", N(45_000), "Half a day each. Timekeeping and finish, not an interview"],
        ["Day-one total", N(295_000), "Expensed in October 2026"],
    ]
    bits.append(table(headers, rows, [190, 80, CONTENT_W - 270], emphasizes={6}))
    bits.append(P(
        "These are planning allowances, not quotations. A lawyer who has actually used a subcontractor agreement on a Lagos job "
        "is the person to instruct. A six-month advisory retainer is not part of entry. If a consultant is used at all in year 1, "
        "it is a single working session on packages and the job checklist, paid from the operating float, and only after the first paid jobs."
    , "note"))
    bits.append(h2("What ₦500,000 actually does"))
    bits.append(P(
        f"Spent the same way, {N(500_000)} leaves about {N(130_000)} after October’s set-up and operating costs. "
        f"The second proof job, in December 2026, takes the account to <b>{N(under['rows'][2]['cash_end'])}</b>. "
        f"By {under['min_cash_label']} the hole is <b>{N(under['min_cash'])}</b>, largely because the limited-company fee "
        f"and the founder’s new draw land while the estate pilot has not yet started."
    ))
    bits.append(P(
        "The five-year engine can be pointed at a ₦500,000 start, and by year 5 the closing cash looks familiar, because the model "
        "does not cancel jobs when the bank is empty. That is not a rescue story. An overdrawn account means materials that cannot be bought "
        "and a supervisor who cannot be hired. The ₦500,000 path stops being the plan in December 2026 unless a top-up is already agreed."
    ))
    bits.append(callout(
        f"Survivable entry for this ramp is {N(base['opening'])} in the business, plus the household reserve if the founder has no other income. "
        f"Together that is {N(base['opening'] + base['household_gap_y1'])}. "
        f"Anyone who can live with family, or who has a partner’s income, can start with the business cheque alone."
    ))
    bits.append(h2("Best-case entry is not the budget"))
    bits.append(P(
        f"The best path’s own cheque is {N(900_000)}, because a limited company is formed in month one "
        f"({N(500_000)} of set-up, including stronger contracts) and invoices arrive sooner. "
        f"Its lowest balance is {best_low()}. Use that figure only as a test of the upside. "
        f"The money to place in the account on day one is the base cheque."
    ))
    return bits


def best_low():
    # Filled by closure? We'll compute inside minimum_entry via pack... 
    # This function is a placeholder replaced below if I call it wrong.
    return "see text"


def unit_economics():
    refresh_price = 180_000
    refresh_rate = 0.27
    refresh_gp = refresh_price * refresh_rate
    standup_price = 540_000
    standup_gp = standup_price * 0.23
    retainer = 200_000
    retainer_gp = retainer * 0.46
    care = 32_000
    care_gp = care * 0.40
    floor = 1 - (1 / 1.20)
    bits = [P("6  ·  Unit economics", "h1"), Rule()]
    bits.append(P(
        f"The floor for taking a job, once the proof period is over, is a 20 percent markup on materials plus the artisan’s rate. "
        f"That is a contribution of about {floor * 100:.0f} percent of the invoice. Under it, the job is declined, even if the client is friendly. "
        f"The packages in the model are priced above that floor. The first proof jobs are not."
    ))
    bits.append(h2("Four worked prices"))
    headers = ["Job", "Invoice", "Contribution", "Rate", "What the rate assumes"]
    rows = [
        ["Proof refresh, Nov 2026", N(120_000), N(18_000), "15%", "Below the floor. Buys photographs and a reference. Three jobs only."],
        ["Refresh, from Feb 2027", N(refresh_price), N(refresh_gp), "27%", "Materials at cost, bench at their rate, a small average referral."],
        ["Stand-up, spring 2027", N(standup_price), N(standup_gp), "23%", "More materials, so the rate on the invoice is lower."],
        ["Retainer after the pilot", N(retainer), N(retainer_gp), "46%", "Bench cost of the included small works. Materials are extra."],
        ["Care plan, one flat", N(care), N(care_gp), "40%", "Three small tickets and a look stay inside the cap."],
    ]
    bits.append(table(headers, rows, [120, 68, 72, 40, CONTENT_W - 300]))
    bits.append(Spacer(1, 6))
    bits.append(P(
        f"On the {N(refresh_price)} refresh, direct cost is {N(refresh_price - refresh_gp)}. "
        f"A practical split of that cost is about {N(58_000)} of materials and {N(73_400)} of bench labour. "
        f"The {N(refresh_gp)} contribution is a markup of about {refresh_gp / (refresh_price - refresh_gp) * 100:.0f} percent on that direct cost, "
        f"which clears the 20 percent floor. The deposit of 60 percent is {N(refresh_price * 0.60)}. "
        f"It covers the materials and part of the labour. The float covers the rest until the client pays the balance."
    ))
    bits.append(P(
        f"On the retainer, {N(retainer - retainer_gp)} is the bench labour the fee is expected to consume in a normal month. "
        f"A leaking tank, a burnt distribution board, or a vacant flat repainted from the same fee will consume the month. "
        f"Those items are extras. If they are allowed inside the fee, the 46 percent contribution disappears and the later hire dates in this study are wrong."
    ))
    bits.append(P(
        f"On the care plan, one flat that consumes {N(50_000)} of labour against a {N(care)} fee loses "
        f"{N(50_000 - care)} in that month. Two quiet flats at the planned contribution cover one loud one, and no more than that. "
        f"The plan is sold to landlords in one estate, prepaid, for a minimum of three months, with materials above {N(10_000)} billed aside."
    ))
    bits.append(h2("Collection, because margin is not cash"))
    headers = ["Slice of a one-off invoice", "Base case", "Best case"]
    rows = [
        ["Deposit and balance collected in the month", "86%", "90%"],
        ["Collected the following month", "12%", "9%"],
        ["Never collected", "2%", "1%"],
        ["Rework reserve, extra cash out", "3% of the invoice", "1.5% of the invoice"],
    ]
    bits.append(table(headers, rows, [CONTENT_W * 0.46, CONTENT_W * 0.27, CONTENT_W * 0.27]))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "Withholding tax is not in those percentages. Where a company or an estate association withholds, the model takes 5 percent "
        "off the cash on 80 percent of retainer fees, half of care-plan fees, and 35 percent of one-off invoices in the base case "
        "(55 percent in the best case). The certificate is an asset. While the company is inside the small-company tax test it often cannot be used, "
        "so it is not spendable cash. The tax section deals with that."
    ))
    return bits


def scenarios(base, best):
    bits = [P("7  ·  The two paths", "h1"), Rule()]
    bits.append(P(
        "Both paths use the same rules: deposits before work, a bench, caps on monthly plans, and no salary until prepaid recurring fees "
        "cover 1.3 times the loaded pay and the bank still holds at least ₦300,000. The paths differ in speed, price, and how early a partner channel appears."
    ))
    headers = ["", "Base case", "Best case"]
    rows = [
        ["Opening cheque", N(base["opening"]), N(best["opening"])],
        ["Legal form in October", "Business name", "Limited company"],
        ["Limited company", "June 2027, before the estate signs", "October 2026"],
        ["Proof-job contribution", "15%, then 18%, then 27%", "20%, then 30–32%"],
        ["Stand-up contribution", "23%", "28%"],
        ["Launch contribution", "22%", "26%"],
        ["Retainer contribution", "46%", "52%"],
        ["Care-plan contribution", "40%", "45%"],
        ["Uncollected jobs", "2%", "1%"],
        ["Price band", "Mainland offices, shops, one estate", "Same work, with Lekki and GRA prices in the mix"],
        ["First retainer", "July 2027, ₦150,000 pilot", "March 2027, ₦200,000 pilot"],
        ["Care plans begin", "January 2028, 6 flats", "September 2027, 8 flats"],
        ["Estates on retainer at year 5", "2", "3"],
        ["Flats on a care plan at year 5", "30, one estate", "60, still clustered"],
        ["Salaried roles at year 5", "Supervisor and one electrician", "Supervisor, electrician, plumber"],
    ]
    bits.append(table(headers, rows, [150, (CONTENT_W - 150) / 2, (CONTENT_W - 150) / 2]))
    bits.append(Spacer(1, 6))
    bits.append(h2("Base path, in one paragraph each year"))
    bits.append(P(
        "<b>Year 1.</b> Nineteen refresh jobs and seven stand-ups. No launch. No salaries. The founder draws nothing until April 2027, "
        "then ₦80,000 a month. A 90-day estate pilot starts in July at ₦150,000. The year invoices ₦7.63 million and loses about ₦0.44 million. "
        "That loss is the cost of learning and of forming the company properly. The float is what makes the loss survivable."
    ))
    bits.append(P(
        "<b>Year 2.</b> The pilot is renewed near ₦200,000. A supervisor is hired in October 2027 at a ₦100,000 target pay, because the retainer "
        "clears the test and the bank is above the floor. Care plans start in January inside that same estate and end the year at 16 flats. "
        "One launch job is taken. Invoices rise to about ₦25 million. Companies income tax is still zero on the test used here."
    ))
    bits.append(P(
        "<b>Year 3.</b> The founder sells and prices. The supervisor runs sites. One estate, care plans ending at 21 flats, two launch jobs. "
        "Invoices about ₦42 million. Still inside the small-company turnover line."
    ))
    bits.append(P(
        "<b>Year 4.</b> A second estate accepts a pilot mid-year. Care plans in the first estate pass 25 flats in June 2030, and the electrician "
        "goes onto a salary at a ₦145,000 target. Turnover crosses ₦50 million, so the tax charge appears for the first time. "
        "Profit after tax is lower than year 3 even though the firm is larger. The tax section shows why."
    ))
    bits.append(P(
        "<b>Year 5.</b> Two retainers, 30 care-plan flats, three launch jobs, the same two salaries. Invoices about ₦62 million. "
        "Cash in the company is about ₦11.3 million, and a further withholding-tax credit sits unused. Painters, tilers, cleaners, the plumber, "
        "and the driver remain on the bench. A third salary is not earned by the base rules."
    ))
    bits.append(h2("Best path, and the condition attached to it"))
    bits.append(P(
        "The best path invoices about ₦18.6 million in year 1 and about ₦113 million in year 5. A supervisor is hired in March 2027, "
        "an electrician in December 2028, and a plumber in February 2030. Tax starts in year 2. Value-added tax registration becomes a live question in year 5, "
        "when turnover passes ₦100 million."
    ))
    bits.append(P(
        "That path is the same firm with two pieces of luck that have to be named. First, from January 2027 a property manager is paying for referrals "
        "rather than merely promising them. Second, package prices hold at the higher band because some of the work sits in Lekki, Ikoyi, Victoria Island, "
        "or a GRA, not only on the mainland. If either piece is missing, the founder is on the base path and needs the base cheque."
    ))
    bits.append(P(
        "Care plans become 31 percent of best-case invoices by year 5. That is still a minority, and it is only safe while the cap holds. "
        "The loose-cap rerun in section 11 shows the cash result when it does not."
    ))
    return bits


def five_year(base, best):
    bits = [P("8  ·  Five-year results", "h1"), Rule()]
    bits.append(P(
        "Invoices on the two paths. The bars are nominal naira. The best path pulls away in year 1 and stays ahead; "
        "it does not assume a different kind of company."
    ))
    labels = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    bits.append(GroupedBars(
        labels,
        [y["revenue"] for y in base["years"]],
        [y["revenue"] for y in best["years"]],
    ))
    bits.append(Spacer(1, 4))
    bits.append(P("Headline comparison. Profit is after the tax charge. Cash is the balance at 30 September.", "note"))
    headers = ["", "Y1", "Y2", "Y3", "Y4", "Y5"]
    w0 = 108
    w = [w0] + [(CONTENT_W - w0) / 5] * 5

    def line(label, fn):
        return [label] + [fn(i) for i in range(5)]

    rows = [
        line("Base invoices", lambda i: N(base["years"][i]["revenue"])),
        line("Best invoices", lambda i: N(best["years"][i]["revenue"])),
        line("Base profit after tax", lambda i: N(base["years"][i]["pat"])),
        line("Best profit after tax", lambda i: N(best["years"][i]["pat"])),
        line("Base cash, year end", lambda i: N(base["years"][i]["cash_end"])),
        line("Best cash, year end", lambda i: N(best["years"][i]["cash_end"])),
        line("Base founder draw", lambda i: N(base["years"][i]["founder"])),
        line("Best founder draw", lambda i: N(best["years"][i]["founder"])),
    ]
    bits.append(table(headers, rows, w, emphasizes={0, 2, 4}))
    bits.append(Spacer(1, 8))
    bits.append(P(
        f"Over five years the base founder draws <b>{N(base['cumulative_founder'])}</b> and leaves "
        f"<b>{N(base['cumulative_pat'])}</b> of profit in the company. "
        f"The best founder draws <b>{N(best['cumulative_founder'])}</b> and leaves "
        f"<b>{N(best['cumulative_pat'])}</b>. "
        f"The draw is a company cost in these statements. Personal income tax on the founder’s own drawings is not deducted; "
        f"that is a household matter to run with the accountant once the draw becomes regular."
    ))
    bits.append(h2("Where year-5 invoices come from"))
    headers = ["Stream", "Base", "Share", "Best", "Share"]
    def share_row(label, key):
        b = base["years"][4][key]
        z = best["years"][4][key]
        return [
            label,
            N(b),
            f"{b / base['years'][4]['revenue'] * 100:.0f}%",
            N(z),
            f"{z / best['years'][4]['revenue'] * 100:.0f}%",
        ]
    rows = [
        share_row("Refresh", "refresh_rev"),
        share_row("Stand-up", "standup_rev"),
        share_row("Launch", "launch_rev"),
        share_row("Extras", "extras_rev"),
        share_row("Retainers", "retainer_rev"),
        share_row("Care plans", "care_rev"),
        ["Total", N(base["years"][4]["revenue"]), "100%", N(best["years"][4]["revenue"]), "100%"],
    ]
    bits.append(table(
        headers, rows,
        [100, (CONTENT_W - 100) * 0.30, (CONTENT_W - 100) * 0.20, (CONTENT_W - 100) * 0.30, (CONTENT_W - 100) * 0.20],
        emphasizes={6},
    ))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "One-off work is still about two-thirds of the base firm in year 5. Retainers and care plans are the stabiliser, not the whole company. "
        "That mix is deliberate. A firm that becomes only a care-plan book has wagered the year on caps being kept."
    ))
    bits.append(h2("Cash over the sixty months"))
    bits.append(P(
        "Each panel has its own scale. The base firm’s cash dips in the first year, touches its low early in year 2 as the supervisor comes on, "
        "and then compounds. The best firm’s cash climbs earlier and much further, which is another way of seeing that the upside is front-loaded luck plus price."
    ))
    panel_w = (CONTENT_W - 12) / 2
    panels = Table(
        [[
            CashPanel([r["cash_end"] for r in base["rows"]], "Base case, ₦ million", GREEN, panel_w, 158),
            CashPanel([r["cash_end"] for r in best["rows"]], "Best case, ₦ million", BLUE, panel_w, 158),
        ]],
        colWidths=[panel_w + 6, panel_w + 6],
    )
    panels.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    bits.append(panels)
    bits.append(Spacer(1, 6))
    return bits


def year_one(base, best):
    bits = [P("9  ·  Year 1, month by month", "h1"), Rule()]
    bits.append(P(
        "Year 1 is where the plan is actually hard. The later years are a consequence of getting through these twelve months without a salary bill and without an empty account."
    ))
    bits.append(h2("Base case"))
    headers = ["Month", "Invoices", "Contribution", "Draw", "Cash"]
    rows = []
    for r in base["rows"][:12]:
        rows.append([
            r["label"],
            N(r["revenue"]),
            N(r["contribution"]),
            N(r["founder"]) if r["founder"] else "—",
            N(r["cash_end"]),
        ])
    col = [88, 90, 100, 80, CONTENT_W - 358]
    bits.append(table(headers, rows, col))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "October is set-up and trials, with no invoices. November and December are single proof jobs at a 15 percent contribution, "
        "accepted in order to have a before-and-after and a client who will take a call. January is still a learning price. "
        "From February the refresh rate is 27 percent. March is the first stand-up. April is the first founder draw, and it is ₦80,000, "
        "not a living wage. June carries the ₦120,000 upgrade to a limited company, which is why cash steps down even though invoices hold. "
        "July starts the estate pilot. August and September add extras. No one is on salary."
    ))
    bits.append(P(
        f"The year invoices <b>{N(base['years'][0]['revenue'])}</b>, contributes <b>{N(base['years'][0]['contribution'])}</b>, "
        f"and loses <b>{N(abs(base['years'][0]['pat']))}</b> after every cost. "
        f"Cash ends at <b>{N(base['years'][0]['cash_end'])}</b>, against <b>{N(base['opening'])}</b> put in."
    ))
    bits.append(h2("Best case"))
    rows = []
    for r in best["rows"][:12]:
        rows.append([
            r["label"],
            N(r["revenue"]),
            N(r["contribution"]),
            N(r["founder"]) if r["founder"] else "—",
            N(r["cash_end"]),
        ])
    bits.append(table(headers, rows, col, emphasizes={5, 8}))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "January is the month the property-manager referrals have to be real, because that is when the first stand-up at the higher price lands. "
        "March adds the estate and, because both hiring tests pass, the supervisor. June is the first launch, which is why that month’s invoices jump. "
        "September adds the first eight care plans. If January and March do not happen, do not keep spending as though they will. Drop back to the base calendar."
    ))
    bits.append(P(
        f"Best-case year 1 invoices <b>{N(best['years'][0]['revenue'])}</b> and profit after tax is "
        f"<b>{N(best['years'][0]['pat'])}</b>. Cash ends at <b>{N(best['years'][0]['cash_end'])}</b>."
    ))
    bits.append(h2("A week in the base year, once stand-ups have started"))
    bits.append(P(
        "From March 2027 the base calendar is two refreshes and one stand-up in a month, and from July a weekly estate walk as well. "
        "That is a full book for one person. Refreshes last one to three days. A stand-up lasts one to two weeks. They have to be sequenced, "
        "not stacked. The model does not contain a second stand-up in any base-case month until the supervisor is in place, and even then launch months "
        "carry fewer stand-ups. Turning a good week into three simultaneous sites is how the rework reserve stops being enough."
    ))
    return bits


def gates(base, best):
    bits = [P("10  ·  When somebody goes on salary", "h1"), Rule()]
    bits.append(P(
        "A salary is a promise to pay in a month with no job. The model allows that promise only when both of these are true at the start of the month:"
    ))
    bits.extend(bullets([
        "Prepaid recurring fees — retainers plus care plans, not one-off jobs — are at least 1.3 times the loaded cost of everyone already on salary plus the new person.",
        "The business account already holds at least ₦300,000, so the hire is not funded by the last deposit.",
    ]))
    bits.append(P(
        "There is a third, practical test the engine also applies. An electrician is eligible only when at least 25 flats in one cluster are on the care plan. "
        "A plumber is eligible only when there are at least 40 care-plan flats and at least two estates. Until then those trades stay on the bench, where a quiet month costs nothing."
    ))
    bits.append(h2("What the engine actually does"))
    headers = ["Path", "Person", "Month", "Target pay"]
    rows = []
    for res, name in ((base, "Base"), (best, "Best")):
        for i, role, pay, *_rest in res["events"]:
            rows.append([name, role, model.month_label(i), f"{N(pay)} a month"])
    bits.append(table(headers, rows, [70, 110, 120, CONTENT_W - 300]))
    bits.append(Spacer(1, 6))
    sup = base["events"][0]
    bits.append(P(
        f"The base supervisor is hired in {model.month_label(sup[0])}. Recurring fees that month are the renewed retainer of about ₦200,000. "
        f"Loaded cost of a ₦100,000 target pay is ₦118,000. The 1.3 test needs ₦153,400. The retainer clears it. "
        f"Cash at the end of September 2027 is {N(base['years'][0]['cash_end'])}, which clears the ₦300,000 floor. "
        f"Care plans are not required for this first hire. They are required before a tradesperson joins the payroll."
    ))
    bits.append(P(
        f"The base electrician waits until {model.month_label(base['events'][1][0])}, the first month the first estate has 25 care-plan flats "
        f"and the cash test still holds. Painters and cleaners are never salaried in either path. Their work is lumpy, and a salary would pay them to wait."
    ))
    bits.append(h2("The question of a fee per flat"))
    bits.append(P(
        "A fixed monthly fee per flat can cover salaries. It can do so only after the flats are clustered, the fee is prepaid, and the work inside the fee is capped. "
        "The arithmetic, using the crew a founder is tempted to hire on day one, is as follows."
    ))
    loaded = (150_000 + 140_000 + 140_000) * model.STAFF_LOAD
    per_flat_contribution = 35_000 * 0.40
    flats = loaded / per_flat_contribution
    bits.append(P(
        f"Target pay of ₦150,000, ₦140,000, and ₦140,000, loaded at 1.18, is <b>{N(loaded)}</b> a month before materials, before the founder, and before operating costs. "
        f"A ₦35,000 care plan at a 40 percent contribution leaves {N(per_flat_contribution)} toward that bill. "
        f"Covering the crew alone takes about <b>{flats:.0f} flats</b>, in one cluster, every month, with the caps holding. "
        f"The base plan has 30 such flats only at the end of year 5, and by then it has salaried two people, not three, and it has retainers and one-off work besides."
    ))
    bits.append(P(
        "Taking the fee “out of rent” works when a landlord or a managing agent has a written mandate to deduct it and pay this firm. "
        "It does not work as a quiet skim, and it is a hard sell to a tenant who already pays rent and a service charge. "
        "The buyer in this model is the landlord or the association, paying in advance."
    ))
    bits.append(callout(
        "Availability can be salaried. Trades stay on call until a single estate is dense enough to keep them busy. "
        "The retainer pays for being reachable. The job rate pays the hands. A man in the gatehouse every day is a different product and is not priced here."
    ))
    return bits


def tax_section(base, best):
    bits = [P("11  ·  Tax, withholding, and the line at ₦50 million", "h1"), Rule()]
    bits.append(P(
        "The model uses the small-company test as publicly summarised for the Nigeria Tax Act 2025. A company is small, and the model charges "
        "no companies income tax, when turnover for the year is ₦50 million or below, fixed assets are ₦250 million or below, and the business is not a professional service. "
        "Tools in this plan never approach the asset test. The professional-service exclusion is the drafting risk: invoices have to describe specified works, "
        "maintenance, and materials. A monthly bill written as “consultancy” or “advisory” can lose the exemption at any size."
    ))
    bits.append(P(
        "Above that turnover line the model charges 30 percent companies income tax plus a 4 percent development-levy allowance, together 34 percent of profit, "
        "and it charges that on the whole profit of the year. Public summaries of the 2025 reforms describe the levy this way. The accountant has to confirm the base before any filing. "
        "This paper is not a tax opinion."
    ))
    headers = ["", "Y1", "Y2", "Y3", "Y4", "Y5"]
    w0 = 130
    w = [w0] + [(CONTENT_W - w0) / 5] * 5

    def row(label, res, key, as_money=True):
        out = [label]
        for y in res["years"]:
            val = y[key]
            out.append(N(val) if as_money else val)
        return out

    bits.append(Spacer(1, 4))
    bits.append(table(headers, [
        row("Base turnover", base, "revenue"),
        row("Base tax charge", base, "tax"),
        row("Base withholding withheld", base, "wht"),
        row("Best turnover", best, "revenue"),
        row("Best tax charge", best, "tax"),
        row("Best withholding withheld", best, "wht"),
    ], w, emphasizes={1, 4}))
    bits.append(Spacer(1, 6))
    bits.append(callout(
        f"Base-case year 4 turnover is {N(base['years'][3]['revenue'])}. The tax charge is {N(base['years'][3]['tax'])}. "
        f"The same profit, in a year that stayed at or under ₦50 million, would carry no companies income tax on this test. "
        f"Best-case year 2 is the same kind of year: turnover {N(best['years'][1]['revenue'])}, tax {N(best['years'][1]['tax'])}. "
        f"In any year that is within about ₦5 million of the line, ask the accountant before dating a large job into September. "
        f"Shifting the real date of real work is a conversation. Misdating an invoice is not a strategy, and this study does not recommend it."
    ))
    bits.append(Spacer(1, 6))
    bits.append(P(
        f"Value-added tax is kept out of the invoices in the model. On the summaries used here, a small business at or under ₦100 million of turnover, "
        f"with fixed assets under the threshold and outside professional services, has no VAT registration obligation. "
        f"The base path stays under ₦100 million. The best path invoices {N(best['years'][4]['revenue'])} in year 5 and would have to register, charge 7.5 percent, "
        f"and file. Prices in this study are exclusive of VAT. Clients who compare a VAT-inclusive quote with an artisan who does not charge it will push back. "
        f"That pressure is a reason to keep the best path’s margin under review in year 5, not a reason to price VAT inside the first four years."
    ))
    bits.append(h2("Withholding tax is a cash trap while the company is small"))
    bits.append(P(
        f"Clients who withhold 5 percent are paying the tax office, not this firm. The certificate is useful when there is companies income tax to set it against. "
        f"In the base case that tax arrives only in years 4 and 5, and it does not absorb every certificate. "
        f"At September 2031 the base firm still holds <b>{N(base['final_wht_credit'])}</b> of unused certificates. "
        f"The best firm’s tax is large enough to absorb its certificates by the end. "
        f"On the thin-sales rerun, where turnover never crosses ₦50 million, unused certificates pile up to "
        f"<b>{thin_credit()}</b> and are not cash."
    ))
    bits.append(P(
        "Plan the float without those certificates. Chase them with the accountant once a year. Do not lend against them, and do not treat a client’s withholding as a discount you can afford to ignore when you set the price: it is a delay, and for several years it is a delay with no refund in sight."
    ))
    return bits


def thin_credit():
    return "filled-later"


def salary_failure(death):
    loaded = (150_000 + 140_000 + 140_000) * model.STAFF_LOAD
    bits = [P("12  ·  The salary-first path", "h1"), Rule()]
    bits.append(P(
        f"This rerun keeps the base sales calendar and the base {N(death['opening'])} cheque, and adds three salaries from October 2026: "
        f"a supervisor at ₦150,000, an electrician at ₦140,000, and a plumber at ₦140,000. Loaded, that is <b>{N(loaded)}</b> every month, "
        f"whether or not there is a job. The hiring tests are switched off, which is the point of the rerun."
    ))
    headers = ["Month", "Invoices", "Staff cost", "Profit", "Cash"]
    rows = []
    for r in death["rows"][:12]:
        rows.append([
            r["label"],
            N(r["revenue"]),
            N(r["staff"]),
            N(r["pbt"]),
            N(r["cash_end"]),
        ])
    w = [78, 85, 85, 100, CONTENT_W - 348]
    bits.append(table(headers, rows, w))
    bits.append(Spacer(1, 6))
    bits.append(P(
        f"The account is overdrawn in {death['rows'][1]['label']}, at <b>{N(death['rows'][1]['cash_end'])}</b>, "
        f"with a single proof job in the book. At September 2027 cash is <b>{N(death['years'][0]['cash_end'])}</b>. "
        f"Five years later it is still <b>{N(death['ending_cash'])}</b>, even though the later years start to show an accounting profit. "
        f"The hole dug in year 1 is larger than the later profits. There is no month in this path at which hiring those three people was consistent with the fee test."
    ))
    bits.append(callout(
        "A hired hand who costs ₦25,000 on a job that invoices ₦80,000 is a direct cost you can decline. "
        "A salary of ₦150,000 in a month with no job is a fixed cost you have already promised. "
        "The feasible firm uses the first of those and refuses the second until the tests in section 10 pass.",
        accent=RED,
    ))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "An uncapped care plan fails in a different month but for the same reason. Take the year-5 base fee and remove the cap. "
        "Thirty flats at ₦40,000 invoice ₦1,200,000. If the average flat actually consumes ₦55,000 of labour — a leak, a board, a repaint — "
        "direct cost is ₦1,650,000. The month loses ₦450,000 before the supervisor is paid. The capped version of the same ₦1,200,000, "
        "at a 40 percent contribution, leaves ₦480,000 toward fixed costs. The difference is the written cap, the extra quotation, and the willingness to decline the job that does not fit."
    ))
    return bits


def sensitivities(base, delayed, thin, creep, weak):
    bits = [P("13  ·  What moves the result", "h1"), Rule()]
    bits.append(P(
        "Each row starts from the base cheque and the base rules, and changes one thing. Job counts on the delayed-retainer and loose-cap rows "
        "stay as in the base plan. That overstates how easy recovery is, and the cash low is the number to trust."
    ))
    headers = ["Path", "What changed", "Lowest cash", "Year-5 cash", "Year-5 profit"]
    rows = [
        ["Base", "The plan", N(base["min_cash"]), N(base["ending_cash"]), N(base["years"][4]["pat"])],
        ["Retainer delayed", "No estate fees until April 2028", N(delayed["min_cash"]), N(delayed["ending_cash"]), N(delayed["years"][4]["pat"])],
        ["Thin sales", "One-off work and care plans at 70%", N(thin["min_cash"]), N(thin["ending_cash"]), N(thin["years"][4]["pat"])],
        ["Loose caps", "Care-plan contribution cut by 15 points", N(creep["min_cash"]), N(creep["ending_cash"]), N(creep["years"][4]["pat"])],
        ["Weak collection", "8% never collected, 25% slips a month", N(weak["min_cash"]), N(weak["ending_cash"]), N(weak["years"][4]["pat"])],
    ]
    bits.append(table(headers, rows, [78, 155, 78, 78, CONTENT_W - 389], emphasizes={0}))
    bits.append(Spacer(1, 6))
    bits.append(P(
        f"<b>A late estate.</b> Pushing the first retainer out by nine months takes the low to <b>{N(delayed['min_cash'])}</b> "
        f"in {delayed['min_cash_label']}. Surviving that delay with a ₦200,000 floor would have needed about "
        f"{N(delayed['solvent_capital'])} at the start, roughly {N(delayed['topup_for_buffer'])} more than the base cheque. "
        f"The supervisor is hired later because the cash floor fails. Year-5 profit looks similar only because the model still assumes the jobs happen."
    ))
    bits.append(P(
        f"<b>Fewer jobs.</b> At 70 percent of one-off and care-plan revenue, the low is <b>{N(thin['min_cash'])}</b> "
        f"in {thin['min_cash_label']}. The firm stays solvent on the base cheque, with little room. "
        f"The electrician is never hired, because the estate never reaches 25 care plans. "
        f"Turnover stays under ₦50 million, tax stays at zero, and unused withholding certificates reach <b>{N(thin['final_wht_credit'])}</b>. "
        f"Year-5 cash is {N(thin['ending_cash'])}, about a third of the base pile. The firm survives. It does not become comfortable."
    ))
    bits.append(P(
        f"<b>Loose caps.</b> Cutting care-plan contribution from 40 percent to 25 percent leaves the early months unchanged, "
        f"because care plans start later. By year 5, cash is <b>{N(creep['ending_cash'])}</b> against <b>{N(base['ending_cash'])}</b> on the base path, "
        f"and profit after tax in that year is {N(creep['years'][4]['pat'])} against {N(base['years'][4]['pat'])}. "
        f"The firm is still alive. Half the reason to sign estates has leaked away. A cap that is waived on the phone will do this without showing up as a crisis in month one."
    ))
    bits.append(P(
        f"<b>Slow payers.</b> Writing off 8 percent and letting a quarter of each one-off invoice slip by a month takes the low to "
        f"<b>{N(weak['min_cash'])}</b> in {weak['min_cash_label']}. The extra capital to restore a ₦200,000 floor is about "
        f"{N(weak['topup_for_buffer'])}. Year-5 cash falls to {N(weak['ending_cash'])}. "
        f"The deposit rule is not paperwork. It is the difference between this row and the base row."
    ))
    bits.append(callout(
        "The result moves most when cash is collected late, when the estate is late, or when monthly plans are allowed to sprawl. "
        "It moves less when one-off volume is merely slower, provided salaries stay off. Volume is not the first risk. Float and scope are."
    ))
    return bits


def ninety_days():
    bits = [P("14  ·  The first ninety days", "h1"), Rule()]
    bits.append(P(
        "These ninety days are October to December 2026 on the base calendar. They are designed to produce a legal shell, a bench of people who have been watched, "
        "and two paid jobs with photographs. They are not designed to produce a salary, an office, or a retainer."
    ))
    headers = ["When", "Action", "Cash effect in the model"]
    rows = [
        ["Week 1", "Open the business account with the full base cheque. Instruct a commercial lawyer for the client contract and the hired-hand one-pager. Start the business-name filing and the TIN.", "Part of the ₦295,000 set-up"],
        ["Week 1", "Give the accountant the three packages, the deposit rule, and the rule that float is not profit. Ask for a one-page chart and a monthly close.", "Inside the set-up allowance"],
        ["Days 1–8", "List six roles. Have twelve conversations, two per trade, from estates, sites, markets, and people who already finish work well. No mass posting.", "Transport inside operating costs"],
        ["Days 9–14", "Pay three people for a tiny real task: a socket, a wall, a sign delivered and fixed. Record name, rates, the area they can reach by 8am, NIN, and account number.", "₦45,000 of trials"],
        ["Week 3–4", "Save six to eight names in WhatsApp as a bench. Sign the one-pager with each. Set the floor: decline a job that does not clear 20 percent on direct cost after these trials.", "No new cash"],
        ["November", "One paid proof job. Deposit before materials. Photographs. Ask for a reference, not a discount on the next one.", "₦120,000 invoice, 15% contribution"],
        ["December", "A second proof job, slightly larger. Stop proof pricing after this. January may still be a learning price; February is the full refresh rate.", "₦160,000 invoice"],
        ["Throughout", "No PAYE staff, no uniforms, no office, no weekly wage for an idle hand, no artisan collecting the client’s balance.", "This is what keeps December solvent"],
    ]
    bits.append(table(headers, rows, [68, 250, CONTENT_W - 318]))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "The lawyer, the accountant, and the founder are the management stack in this quarter. A fractional operations person is optional and later. "
        "LSETF, SMEDAN, and any loan desk come after there are invoices and a CAC record, not before. A conversation that begins with government contracts is the wrong conversation for this plan."
    ))
    bits.append(h2("What to walk in with"))
    bits.append(P(
        "One page is enough for the lawyer, the accountant, and any later consultant: three packages, the client (offices, shops, schools, then one estate), "
        "the capital in the account, and the fact that crews are contracted per job. Anyone who cannot work from that page is the wrong hire for this stage."
    ))
    bits.append(P(
        "Meet on the mainland if that is where the first jobs will be. The management of the firm does not require a Victoria Island address. "
        "A property manager, when the time comes, is approached with a one-page scope and a paid trial at a tight price, with their landlord left entirely in their relationship."
    ))
    return bits


def decision_rules(base, best):
    bits = [P("15  ·  Rules for going on, and for stopping", "h1"), Rule()]
    bits.append(P(
        "Use these as gates. A gate that fails is a reason to pause spending, not a reason to invent a new model in the same month."
    ))
    headers = ["Gate", "Go", "Stop and fix"]
    rows = [
        ["Before October spending", f"{N(base['opening'])} is in the business account", "The cheque is ₦500,000 and no top-up is agreed"],
        ["Before the founder relies on the firm to eat", f"Household reserve of about {N(base['household_gap_y1'])}, or another income", "The company account is the rent money"],
        ["From February 2027", "New jobs clear the 20 percent floor", "Jobs are being taken to stay busy"],
        ["Every one-off job", "60 percent is in the account before materials are bought", "Work has started on a promise"],
        ["July 2027", "The estate pilot is signed, or the float still covers a world without it", "Scope is unlimited and the fee is the pilot fee"],
        ["Any salary", "Both tests in section 10 pass on that morning", "A good artisan is about to ‘join the team’"],
        ["Any year near ₦50 million", "The accountant has looked at the line", "September jobs are being squeezed in without a tax view"],
        ["Best-case spending", "Paid referrals exist, not introductions", f"The {N(best['opening'])} cheque is all there is, and January is quiet"],
    ]
    bits.append(table(headers, rows, [120, 175, CONTENT_W - 295]))
    bits.append(Spacer(1, 8))
    bits.append(P(
        f"If the gates hold, the base firm at September 2031 has invoiced {N(sum(y['revenue'] for y in base['years']))} over five years, "
        f"paid the founder {N(base['cumulative_founder'])}, and still holds {N(base['ending_cash'])} in cash. "
        f"That is a small, real company. It is not a facilities group, and it does not need to become one for the plan to have worked."
    ))
    bits.append(callout(
        "Fund ₦1.15 million. Keep the bench. Cap the monthly plans. Hire a supervisor only when the retainer is prepaid and the account still has a floor. "
        "Let the best case arrive as extra cash, not as the budget you needed on day one."
    ))
    return bits


def appendix_pnl(base, best):
    headers = ["₦", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    w0 = 132
    widths = [w0] + [(CONTENT_W - w0) / 5] * 5
    bits = [P("Appendix A  ·  Annual statements", "h1"), Rule()]
    bits.append(P("Base case. Figures are naira for that year.", "note"))
    rows, emph = pnl_rows(base)
    bits.append(table(headers, rows, widths, emph))
    bits.append(Spacer(1, 8))
    bits.append(P("Base case, cash.", "note"))
    rows, emph = cash_rows(base)
    bits.append(table(headers, rows, widths, emph))
    bits.append(Spacer(1, 10))
    bits.append(P("Best case.", "note"))
    rows, emph = pnl_rows(best)
    bits.append(table(headers, rows, widths, emph))
    bits.append(Spacer(1, 8))
    bits.append(P("Best case, cash.", "note"))
    rows, emph = cash_rows(best)
    bits.append(table(headers, rows, widths, emph))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "“Paid out for work and overhead” is the direct cost, rework, operating costs, founder draw, loaded salaries, set-up, and bank leakage. "
        "It is not reduced by withholding tax; withholding is its own line because the client never paid that slice to the firm. "
        "Company tax paid in cash is the tax charge minus certificates used that year.",
        "note",
    ))
    bits.append(h2("Activity behind the base invoices"))
    headers = ["", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    rows = [
        ["Refresh jobs", *[str(y["refresh_n"]) for y in base["years"]]],
        ["Stand-up jobs", *[str(y["standup_n"]) for y in base["years"]]],
        ["Launch jobs", *[str(y["launch_n"]) for y in base["years"]]],
        ["Estates on retainer, year end", *[str(y["retainer_end"]) for y in base["years"]]],
        ["Care-plan flats, year end", *[str(int(y["care_end"])) for y in base["years"]]],
        ["Contribution rate", *[f"{y['contribution'] / y['revenue'] * 100:.0f}%" for y in base["years"]]],
    ]
    bits.append(table(headers, rows, widths))
    bits.append(Spacer(1, 6))
    headers = ["", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    rows = [
        ["Refresh jobs", *[str(y["refresh_n"]) for y in best["years"]]],
        ["Stand-up jobs", *[str(y["standup_n"]) for y in best["years"]]],
        ["Launch jobs", *[str(y["launch_n"]) for y in best["years"]]],
        ["Estates on retainer, year end", *[str(y["retainer_end"]) for y in best["years"]]],
        ["Care-plan flats, year end", *[str(int(y["care_end"])) for y in best["years"]]],
        ["Contribution rate", *[f"{y['contribution'] / y['revenue'] * 100:.0f}%" for y in best["years"]]],
    ]
    bits.append(P("Activity behind the best-case invoices.", "note"))
    bits.append(table(headers, rows, widths))
    return bits


def appendix_assumptions():
    bits = [P("Appendix B  ·  Assumption register", "h1"), Rule()]
    bits.append(P(
        "Change these and the statements change. The engine that produced this PDF is study/model.py. "
        "Running python3 study/render_pdf.py rebuilds the document from that engine."
    ))
    headers = ["Item", "Base", "Best"]
    rows = [
        ["Opening cash", "₦1,150,000", "₦900,000"],
        ["Staff cost multiple on target pay", "1.18", "1.18"],
        ["Hire test", "1.3× loaded recurring fees, and ₦300,000 cash", "Same"],
        ["Electrician density test", "25 care-plan flats", "Same"],
        ["Plumber density test", "40 flats and 2 estates", "Same"],
        ["Bad debt on one-off invoices", "2%", "1%"],
        ["Slip to the next month", "12%", "9%"],
        ["Rework reserve", "3% of one-off invoices", "1.5%"],
        ["Bank leakage", "0.5% of collections", "0.5% of collections"],
        ["Withholding rate", "5% planning rate", "5% planning rate"],
        ["Share of one-off cash subject to withholding", "35%", "55%"],
        ["Share of retainer subject to withholding", "80%", "80%"],
        ["Share of care plans subject to withholding", "50%", "50%"],
        ["Small-company turnover line", "₦50 million", "₦50 million"],
        ["Tax above the line", "34% of profit (30% + 4% allowance)", "Same"],
        ["VAT line, not charged inside the model", "₦100 million", "₦100 million"],
        ["Household need used for the gap", "₦150,000 a month", "₦150,000 a month"],
        ["Office rent", "Nil", "Nil"],
        ["Debt", "Nil", "Nil"],
        ["Loss relief against later tax", "Not modelled", "Not modelled"],
    ]
    bits.append(table(headers, rows, [230, (CONTENT_W - 230) / 2, (CONTENT_W - 230) / 2]))
    bits.append(Spacer(1, 6))
    bits.append(P(
        "Operating costs in the base case run from ₦75,000 in October 2026 to ₦185,000 a month in year 5. "
        "Inside that line: airtime and data, local transport, the external accountant, a small marketing float, a reserve toward liability insurance, "
        "and site sundries that are not materials. Many new firms cannot buy a useful liability policy in month one. The allowance is there so the cost is not forgotten. "
        "It is not evidence that a policy is in force. Confirm the cover with a broker before the first estate signs."
    ))
    bits.append(P(
        "Artisans are treated as independent contractors. That treatment depends on the one-page agreement and on the way the work is actually given: their tools, their other clients, "
        "payment per job, no staff identity. If the tax office or a court treats them as employees, PAYE and pension appear and the contribution rates in this paper are overstated. "
        "The bookkeeper and the lawyer stay external on purpose."
    ))
    bits.append(P(
        "No vehicle is bought. The driver and van stay on call, inside direct cost. Buying a van would be a new decision, with its own fixed cost and its own asset test, and it is not required for these statements."
    ))
    return bits


def sources():
    bits = [P("Appendix C  ·  Limits and sources", "h1"), Rule()]
    bits.append(P(
        "This paper was prepared in September 2026 as a decision tool for one founder. It uses the operating choices already made in the working notes: "
        "visibility before tenders, a bench rather than a payroll, estate retainers kept thin, and in-unit plans sold as a cap rather than a buffet."
    ))
    bits.append(h2("Tax sources, to be confirmed before filing"))
    bits.extend(bullets([
        "Nigeria Tax Act 2025, as summarised in public notes including EY’s June 2025 highlight and 2026 practitioner guides: a small company is one with turnover of ₦50 million or below and fixed assets of ₦250 million or below, excluding professional services, taxed at 0 percent. Other companies are described at 30 percent.",
        "A 4 percent development levy on profits of companies outside that small-company test is included because public summaries of the same reforms describe it. The levy base should be confirmed with a chartered accountant. The model’s 34 percent is that pair of rates, not a filing position.",
        "Nigeria Tax Administration Act 2025, as summarised for 2026 VAT administration: a small business at turnover of ₦100 million or below, with the fixed-asset test and outside professional services, is outside the VAT filing obligation. The VAT rate used when that ceases to apply is 7.5 percent.",
        "Withholding tax is modelled at 5 percent of the relevant collections as a planning rate for contract payments. Construction and other categories can carry different rates. The payer and the payment type decide the rate.",
    ]))
    bits.append(h2("Commercial ranges"))
    bits.append(P(
        "Retainer bands of roughly ₦150,000 to ₦400,000 a month, care-plan bands of roughly ₦30,000 to ₦45,000 a flat, day-rate relationships between labourers, painters, and electricians, "
        "and the cost of a short legal and accounting set-up are the 2026 planning ranges from the working notes. They are not quotes from a named firm. "
        "The first ten artisan conversations and the first five estate visits should replace the price cards before year 2 is treated as a target."
    ))
    bits.append(h2("What the model cannot see"))
    bits.extend(bullets([
        "A shock to the naira’s purchasing power. Later balances are future naira.",
        "A health problem, a security problem, or a founder who stops selling for a month.",
        "An estate chairman who expands the scope in the residents’ group chat and refuses the extra invoice.",
        "A bench that collapses because payment was a week late. The model assumes the promised day is kept.",
        "Personal income tax on the founder’s drawings, and any penalty for late filings.",
        "Interest. The firm has no debt, and cash earns nothing in the model.",
    ]))
    bits.append(Spacer(1, 6))
    bits.append(callout(
        "Use the base cheque, the floor on prices, the deposit, and the hiring tests. Replace every price with a real Lagos quote as soon as you have one. "
        "If the real quotes do not clear the floor, the feasible answer is a smaller menu, not a salary."
    ))
    return bits


class StudyDoc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(
            path,
            pagesize=A4,
            title="Feasibility study: a Lagos multi-service agency",
            author="Planning model, September 2026",
            subject="Base case and best case from minimum entry to year five",
        )
        cover = PageTemplate(
            id="cover",
            frames=[Frame(0, 0, 10, 10, id="cover-frame", showBoundary=0)],
            onPage=draw_cover,
        )
        body = PageTemplate(
            id="body",
            frames=[Frame(
                LEFT, 42, CONTENT_W, PAGE_H - 78,
                id="body-frame", showBoundary=0,
            )],
            onPage=draw_body,
        )
        self.addPageTemplates([cover, body])


def main():
    # Patch the two helper closures used in prose so they read the live pack.
    pack = model.run_all()
    global thin_credit, best_low
    thin_credit = lambda: N(pack["thin"]["final_wht_credit"])
    best = pack["best"]
    best_low = lambda: f"{N(best['min_cash'])} in {best['min_cash_label']}"

    out = Path(__file__).resolve().parents[1] / "docs" / "Lagos-Multi-Service-Agency-Feasibility-Study.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = StudyDoc(str(out))
    doc.build(build_story(pack))
    # Identity must still hold.
    for key, res in pack.items():
        if abs(res["identity_gap"]) > 1:
            raise SystemExit(f"Identity failed for {key}: {res['identity_gap']}")
    print(out)
    print(f"pages will be reported by pdf")


if __name__ == "__main__":
    main()
