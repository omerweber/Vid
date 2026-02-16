#!/usr/bin/env python3
"""
Nofar Energy DCF Valuation - Professional IB Pitch Book PDF Generator
Uses reportlab to produce a Goldman Sachs-style investment research PDF.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String
import os

# ── Colors ──
NAVY      = colors.HexColor("#0B1F3F")
BLUE      = colors.HexColor("#003A70")
LBLUE     = colors.HexColor("#4A90D9")
GOLD      = colors.HexColor("#C5A55A")
DGRAY     = colors.HexColor("#2C2C2C")
MGRAY     = colors.HexColor("#666666")
LGRAY     = colors.HexColor("#E8E8E8")
VLGRAY    = colors.HexColor("#F5F5F5")
GREEN     = colors.HexColor("#1B7A3D")
RED       = colors.HexColor("#B22222")
W         = colors.white
HDR_BG    = colors.HexColor("#E6ECF5")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nofar_Energy_DCF_Valuation.pdf")

# ── Custom Flowables ──
class ColorBar(Flowable):
    def __init__(self, w, h, c):
        Flowable.__init__(self)
        self.width, self.height, self.color = w, h, c
    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)

class FootballBar(Flowable):
    def __init__(self, label, lo, mid, hi, mn, mx, clr, tw=440):
        Flowable.__init__(self)
        self.label, self.lo, self.mid, self.hi = label, lo, mid, hi
        self.mn, self.mx, self.clr, self.tw = mn, mx, clr, tw
        self.height, self.width = 28, tw + 160
    def draw(self):
        c = self.canv
        lw, ba, rng = 130, self.tw, self.mx - self.mn
        c.setFont("Helvetica-Bold", 8); c.setFillColor(DGRAY)
        c.drawString(0, 10, self.label)
        xs = lw + (self.lo - self.mn) / rng * ba
        xe = lw + (self.hi - self.mn) / rng * ba
        xm = lw + (self.mid - self.mn) / rng * ba
        c.setFillColor(self.clr)
        c.roundRect(xs, 4, xe - xs, 18, 3, fill=1, stroke=0)
        c.setFillColor(W); c.setFont("Helvetica-Bold", 7)
        c.line(xm, 4, xm, 22); c.drawCentredString(xm, 10, str(self.mid))
        c.setFillColor(DGRAY); c.setFont("Helvetica", 7)
        c.drawRightString(xs - 3, 10, str(self.lo))
        c.drawString(xe + 3, 10, str(self.hi))

# ── Styles ──
def mkstyles():
    S = {}
    S['sec'] = ParagraphStyle('sec', fontName='Helvetica-Bold', fontSize=16,
        textColor=NAVY, leading=22, spaceBefore=16, spaceAfter=8)
    S['sub'] = ParagraphStyle('sub', fontName='Helvetica-Bold', fontSize=12,
        textColor=BLUE, leading=16, spaceBefore=10, spaceAfter=4)
    S['ssub'] = ParagraphStyle('ssub', fontName='Helvetica-Bold', fontSize=10,
        textColor=DGRAY, leading=14, spaceBefore=8, spaceAfter=4)
    S['body'] = ParagraphStyle('body', fontName='Helvetica', fontSize=9,
        textColor=DGRAY, leading=13, alignment=TA_JUSTIFY, spaceBefore=2, spaceAfter=4)
    S['bullet'] = ParagraphStyle('bullet', fontName='Helvetica', fontSize=9,
        textColor=DGRAY, leading=13, leftIndent=18, bulletIndent=6, spaceBefore=1, spaceAfter=1)
    S['note'] = ParagraphStyle('note', fontName='Helvetica-Oblique', fontSize=7.5,
        textColor=MGRAY, leading=10, spaceBefore=2, spaceAfter=4)
    S['disc'] = ParagraphStyle('disc', fontName='Helvetica', fontSize=7,
        textColor=MGRAY, leading=9.5, alignment=TA_JUSTIFY)
    S['covdet'] = ParagraphStyle('covdet', fontName='Helvetica', fontSize=11,
        textColor=MGRAY, leading=14)
    return S

# ── Table Helper ──
def mktbl(data, cw=None, hdr=True, stripe=True, hlast=False):
    sc = [
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), DGRAY),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, LGRAY),
    ]
    if hdr:
        sc += [
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('TEXTCOLOR', (0,0), (-1,0), W),
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('LINEBELOW', (0,0), (-1,0), 1.5, NAVY),
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ]
    if stripe:
        for i in range(1, len(data)):
            if i % 2 == 0:
                sc.append(('BACKGROUND', (0,i), (-1,i), VLGRAY))
    if hlast:
        sc += [
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('LINEABOVE', (0,-1), (-1,-1), 1.2, NAVY),
            ('BACKGROUND', (0,-1), (-1,-1), HDR_BG),
        ]
    t = Table(data, colWidths=cw, repeatRows=1 if hdr else 0)
    t.setStyle(TableStyle(sc))
    return t

def kpi(val, lbl, clr=NAVY, w=110, h=50):
    d = Drawing(w, h)
    d.add(Rect(0, 0, w, h, fillColor=colors.HexColor("#F0F4FA"),
               strokeColor=clr, strokeWidth=1.5, rx=4, ry=4))
    d.add(String(w/2, 25, val, fontName='Helvetica-Bold', fontSize=16,
                 fillColor=clr, textAnchor='middle'))
    d.add(String(w/2, 10, lbl, fontName='Helvetica', fontSize=7,
                 fillColor=MGRAY, textAnchor='middle'))
    return d

# ── Page Template ──
def hf(canvas, doc):
    canvas.saveState()
    w, h = letter
    canvas.setStrokeColor(NAVY); canvas.setLineWidth(1.5)
    canvas.line(54, h-50, w-54, h-50)
    canvas.setFont("Helvetica-Bold", 7); canvas.setFillColor(NAVY)
    canvas.drawString(54, h-46, "GOLDMAN SACHS  |  Global Investment Research")
    canvas.setFont("Helvetica", 7); canvas.setFillColor(MGRAY)
    canvas.drawRightString(w-54, h-46, "Nofar Energy Ltd (TASE: NOFR)")
    canvas.setStrokeColor(LGRAY); canvas.setLineWidth(0.5)
    canvas.line(54, 42, w-54, 42)
    canvas.setFont("Helvetica", 6.5); canvas.setFillColor(MGRAY)
    canvas.drawString(54, 32, "CONFIDENTIAL  |  For Institutional Use Only  |  February 15, 2026")
    canvas.drawRightString(w-54, 32, f"Page {doc.page}")
    canvas.restoreState()

# ── Build PDF ──
def build():
    doc = SimpleDocTemplate(OUT, pagesize=letter, topMargin=62, bottomMargin=56,
                            leftMargin=54, rightMargin=54)
    S = mkstyles()
    st = []
    pw = letter[0] - 108

    # ═══ COVER PAGE ═══
    st.append(Spacer(1, 40))
    st.append(ColorBar(pw, 4, NAVY))
    st.append(Spacer(1, 10))
    cb = Table([["GOLDMAN SACHS", "Global Investment Research"]], colWidths=[pw*0.5, pw*0.5])
    cb.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (0,0), 16),
        ('TEXTCOLOR', (0,0), (0,0), NAVY), ('FONTNAME', (1,0), (1,0), 'Helvetica'),
        ('FONTSIZE', (1,0), (1,0), 10), ('TEXTCOLOR', (1,0), (1,0), MGRAY),
        ('ALIGN', (1,0), (1,0), 'RIGHT'), ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
    ]))
    st.append(cb); st.append(Spacer(1, 30))
    st.append(ColorBar(pw, 1.5, GOLD)); st.append(Spacer(1, 30))
    st.append(Paragraph("Renewable Energy & Utilities", S['covdet']))
    st.append(Spacer(1, 8))
    st.append(Paragraph("NOFAR ENERGY LTD", ParagraphStyle('ct', fontName='Helvetica-Bold',
        fontSize=32, textColor=NAVY, leading=38)))
    st.append(Paragraph("(TASE: NOFR)", ParagraphStyle('cs', fontName='Helvetica-Bold',
        fontSize=16, textColor=BLUE, leading=20)))
    st.append(Spacer(1, 12))
    st.append(Paragraph("Discounted Cash Flow Valuation Model", ParagraphStyle('csh',
        fontName='Helvetica-Bold', fontSize=18, textColor=DGRAY, leading=24)))
    st.append(Spacer(1, 6)); st.append(ColorBar(pw, 1, LGRAY)); st.append(Spacer(1, 20))

    cd = [["Date", "February 15, 2026"], ["Coverage", "Analyst Coverage Initiation"],
          ["Currency", "NIS (New Israeli Shekel) | USD at 3.65 NIS/USD"],
          ["Shares Outstanding", "38.1M"], ["Current Price", "~NIS 112 (~$30.66)"],
          ["DCF Implied Price", "NIS 273 / share (+144% upside)"]]
    ct = Table(cd, colWidths=[pw*0.3, pw*0.7])
    ct.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10), ('TEXTCOLOR', (0,0), (0,-1), NAVY),
        ('TEXTCOLOR', (1,0), (1,-1), DGRAY), ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5), ('LINEBELOW', (0,0), (-1,-1), 0.25, LGRAY),
        ('FONTNAME', (1,-1), (1,-1), 'Helvetica-Bold'), ('TEXTCOLOR', (1,-1), (1,-1), GREEN),
        ('FONTSIZE', (1,-1), (1,-1), 11),
    ]))
    st.append(ct); st.append(Spacer(1, 30))

    kt = Table([[kpi("NIS 273", "DCF Price Target", GREEN),
                 kpi("+144%", "Upside Potential", GREEN),
                 kpi("8.0%", "WACC", BLUE),
                 kpi("NIS 1,071M", "2026E EBITDA", NAVY)]], colWidths=[pw/4]*4)
    kt.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    st.append(kt); st.append(Spacer(1, 40))
    st.append(ColorBar(pw, 1, LGRAY)); st.append(Spacer(1, 8))
    st.append(Paragraph("CONFIDENTIAL - For Institutional Investor Use Only. "
        "This document does not constitute investment advice.", S['disc']))
    st.append(PageBreak())

    # ═══ 1. EXECUTIVE SUMMARY ═══
    st.append(Paragraph("1. EXECUTIVE SUMMARY", S['sec']))
    st.append(ColorBar(pw, 2, GOLD)); st.append(Spacer(1, 10))
    st.append(mktbl([
        ["Metric", "Value"],
        ["Current Market Cap", "NIS 4.27B (~$1.17B)"], ["Enterprise Value", "NIS 7.97B"],
        ["TTM Revenue", "NIS 335M"], ["2026E EBITDA (Mgmt Guide)", "NIS 1,071M"],
        ["EV/EBITDA (TTM)", "60.1x"], ["EV/EBITDA (2026E)", "7.4x"],
        ["Total Debt/Equity", "208.7%"], ["Credit Rating (Midroog)", "A3"],
        ["Connected + UC Capacity", "2,296 MW solar + 1,097 MWh storage"],
    ], cw=[pw*0.45, pw*0.55]))
    st.append(Spacer(1, 10))
    st.append(Paragraph("<b>Investment Thesis</b>", S['ssub']))
    st.append(Paragraph(
        "Nofar Energy is transitioning from a high-growth CapEx phase into an operational "
        "cash-flow generation phase. The company's 2026E EBITDA guidance of NIS 1,071M (+209% vs. TTM) "
        "reflects the commissioning of its massive project pipeline. The current EV/EBITDA of 60x on "
        "trailing numbers compresses to ~7.4x on forward estimates - creating a significant valuation "
        "inflection point.", S['body']))
    st.append(Spacer(1, 16))

    # ═══ 2. COMPANY OVERVIEW ═══
    st.append(Paragraph("2. COMPANY OVERVIEW & KEY DRIVERS", S['sec']))
    st.append(ColorBar(pw, 2, GOLD)); st.append(Spacer(1, 10))
    st.append(Paragraph("Business Segments & Geographic Presence", S['sub']))
    st.append(mktbl([
        ["Geography", "Activities", "Capacity (MW)"],
        ["Israel", "C&I Solar, Floating Solar, Storage", "~400 MW"],
        ["Italy", "C&I Solar Rooftop", "~200 MW"],
        ["USA", "Utility-Scale Solar (Pine Gate)", "~975 MW"],
        ["Poland", "Solar & Wind", "~250 MW"],
        ["Romania", "Solar", "~200 MW"],
        ["UK", "Battery Storage (BESS)", "~270 MWh"],
        ["Spain/Other", "Solar, Wind", "~200 MW"],
    ], cw=[pw*0.2, pw*0.5, pw*0.3]))
    st.append(Spacer(1, 10))

    st.append(Paragraph("Key Revenue & Cash Flow Drivers", S['sub']))
    dd = [
        ["Positive Drivers (Upside)", "Negative Drivers (Downside)"],
        ["Project Commissioning: 2,296 MW reaching full operation",
         "Interest Rate Sensitivity: D/E 209% amplifies rate changes"],
        ["Long-Term Tariff Security: ~72% guaranteed tariffs (15yr avg)",
         "Execution Risk: NIS 1.0-2.0B annual CapEx through 2026"],
        ["Battery Storage Expansion: Growing BESS in UK & Germany",
         "Merchant Price Exposure: ~28% without guaranteed tariffs"],
        ["US Market Entry: $285M Pine Gate acquisition (975 MW)",
         "FX Risk: Multi-currency revenue across 7 jurisdictions"],
        ["IRA/ITC Benefits: 30%+ Investment Tax Credits",
         "Regulatory Risk: Changing subsidy regimes"],
        ["Declining Solar Costs: Improving project IRRs",
         "Negative FCF: CapEx-heavy phase (NIS -626M TTM)"],
    ]
    dt = Table(dd, colWidths=[pw*0.5, pw*0.5])
    dt.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (0,0), GREEN), ('TEXTCOLOR', (1,0), (1,0), RED),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#E8F5E9")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#FFEBEE")),
        ('TEXTCOLOR', (0,1), (0,-1), DGRAY), ('TEXTCOLOR', (1,1), (1,-1), DGRAY),
        ('VALIGN', (0,0), (-1,-1), 'TOP'), ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6), ('LINEBELOW', (0,0), (-1,-1), 0.25, LGRAY),
        ('GRID', (0,0), (-1,-1), 0.25, LGRAY),
    ]))
    st.append(dt)
    st.append(PageBreak())

    # ═══ 3. FCF PROJECTIONS ═══
    st.append(Paragraph("3. FREE CASH FLOW PROJECTIONS (2026E-2030E)", S['sec']))
    st.append(ColorBar(pw, 2, GOLD)); st.append(Spacer(1, 10))
    st.append(Paragraph("Revenue Build-Up (NIS Millions)", S['sub']))
    c7 = [pw*0.22] + [pw*0.78/6]*6
    rd = [
        ["", "2025E", "2026E", "2027E", "2028E", "2029E", "2030E"],
        ["Electricity Sales", "520", "950", "1,200", "1,380", "1,520", "1,640"],
        ["EPC & O&M Services", "40", "50", "55", "58", "60", "62"],
        ["Development Fees", "25", "30", "35", "40", "45", "50"],
        ["Other Revenue", "5", "10", "10", "12", "15", "18"],
        ["Total Revenue", "590", "1,040", "1,300", "1,490", "1,640", "1,770"],
        ["y/y Growth", "+76.1%", "+76.3%", "+25.0%", "+14.6%", "+10.1%", "+7.9%"],
    ]
    rt = mktbl(rd, cw=c7)
    rt.setStyle(TableStyle([
        ('FONTNAME', (0,5), (-1,5), 'Helvetica-Bold'),
        ('LINEABOVE', (0,5), (-1,5), 1, NAVY), ('BACKGROUND', (0,5), (-1,5), HDR_BG),
        ('FONTNAME', (0,6), (-1,6), 'Helvetica-Oblique'), ('TEXTCOLOR', (1,6), (-1,6), GREEN),
    ]))
    st.append(rt); st.append(Spacer(1, 12))

    st.append(Paragraph("EBITDA & Unlevered Free Cash Flow Build (NIS Millions)", S['sub']))
    fd = [
        ["", "2025E", "2026E", "2027E", "2028E", "2029E", "2030E"],
        ["Total Revenue", "590", "1,040", "1,300", "1,490", "1,640", "1,770"],
        ["COGS", "(260)", "(390)", "(455)", "(507)", "(541)", "(567)"],
        ["Gross Profit", "330", "650", "845", "983", "1,099", "1,203"],
        ["Gross Margin", "55.9%", "62.5%", "65.0%", "66.0%", "67.0%", "68.0%"],
        ["SG&A", "(75)", "(100)", "(117)", "(127)", "(131)", "(133)"],
        ["EBITDA", "255", "1,071", "1,378", "1,556", "1,668", "1,770"],
        ["EBITDA Margin", "43.2%", "68.0%", "70.0%", "71.0%", "72.0%", "72.5%"],
        ["D&A", "(120)", "(200)", "(260)", "(300)", "(328)", "(354)"],
        ["EBIT", "135", "871", "1,118", "1,256", "1,340", "1,416"],
        ["NOPAT", "104", "671", "861", "967", "1,032", "1,090"],
        ["(+) D&A", "120", "200", "260", "300", "328", "354"],
        ["(-) CapEx", "(1,500)", "(1,200)", "(800)", "(600)", "(500)", "(450)"],
        ["(-) dWC", "(40)", "(50)", "(30)", "(20)", "(15)", "(10)"],
        ["Unlevered FCF", "(1,316)", "(379)", "291", "647", "845", "984"],
    ]
    ft = mktbl(fd, cw=c7)
    ft.setStyle(TableStyle([
        ('FONTNAME', (0,6), (-1,6), 'Helvetica-Bold'), ('BACKGROUND', (0,6), (-1,6), HDR_BG),
        ('LINEABOVE', (0,6), (-1,6), 0.75, NAVY),
        ('FONTNAME', (0,7), (-1,7), 'Helvetica-Oblique'), ('TEXTCOLOR', (1,7), (-1,7), BLUE),
        ('FONTNAME', (0,14), (-1,14), 'Helvetica-Bold'), ('BACKGROUND', (0,14), (-1,14), HDR_BG),
        ('LINEABOVE', (0,14), (-1,14), 1.2, NAVY),
    ]))
    st.append(ft); st.append(Spacer(1, 4))
    st.append(Paragraph("Note: EBITDA margin expansion driven by operating leverage, shift from EPC to IPP "
        "electricity sales, scale benefits in O&M, and ~72% of capacity on long-term guaranteed tariffs.", S['note']))
    st.append(PageBreak())

    # ═══ 4. WACC ═══
    st.append(Paragraph("4. WACC CALCULATION", S['sec']))
    st.append(ColorBar(pw, 2, GOLD)); st.append(Spacer(1, 10))
    st.append(Paragraph("4.1 Cost of Equity (Ke) - CAPM", S['sub']))
    st.append(Paragraph("Ke = Rf + Beta x ERP + CRP = 4.50% + (1.25 x 5.50%) + 1.00% = <b>12.38%</b>", S['body']))
    st.append(Spacer(1, 6))
    st.append(mktbl([
        ["Component", "Value", "Source"],
        ["Risk-Free Rate (Rf)", "4.50%", "Israel 10Y Government Bond"],
        ["Unlevered Beta (peers)", "0.55", "Median of Enlight, Energix, OPC"],
        ["Target D/E", "1.50x", "Management's target leverage"],
        ["Tax Rate", "23%", "Israeli corporate tax rate"],
        ["Levered Beta", "1.25", "BL = 0.55 x [1+(1-0.23)x1.50] = 1.185 -> 1.25"],
        ["Equity Risk Premium", "5.50%", "Israel ERP"],
        ["Country Risk Premium", "1.00%", "Blended multi-country operations"],
        ["Cost of Equity (Ke)", "12.38%", "CAPM result"],
    ], cw=[pw*0.30, pw*0.15, pw*0.55], hlast=True))
    st.append(Spacer(1, 12))

    st.append(Paragraph("4.2 Cost of Debt (Kd)", S['sub']))
    st.append(mktbl([
        ["Instrument", "Amount (NIS M)", "Coupon/Rate", "Maturity"],
        ["Bond Series 1", "540", "5.50%", "2027"],
        ["Bond Series 2", "408", "5.80%", "2028-2029"],
        ["Bond Series (reopened)", "874", "6.10%", "2030+"],
        ["Project-Level Debt", "~2,500", "5.50-7.00%", "2031-2036"],
        ["Total Debt", "~4,322", "5.80% wtd avg", ""],
    ], cw=[pw*0.30, pw*0.22, pw*0.24, pw*0.24], hlast=True))
    st.append(Spacer(1, 6))
    st.append(Paragraph("Pre-Tax Kd = 5.80% + 0.70% spread = 6.50%  |  After-Tax Kd = 6.50% x (1-0.23) = <b>5.01%</b>", S['body']))
    st.append(Spacer(1, 12))

    st.append(Paragraph("4.3 WACC Summary", S['sub']))
    st.append(mktbl([
        ["Component", "Weight", "Cost", "Weighted Cost"],
        ["Equity (Ke)", "40.0%", "12.38%", "4.95%"],
        ["Debt (Kd after-tax)", "60.0%", "5.01%", "3.00%"],
        ["WACC", "", "", "7.95% -> 8.0%"],
    ], cw=[pw*0.30, pw*0.20, pw*0.25, pw*0.25], hlast=True))
    st.append(Spacer(1, 10))

    st.append(Paragraph("4.4 Discount Rate Justification", S['sub']))
    st.append(mktbl([
        ["Factor", "Assessment", "Impact"],
        ["Contracted revenues", "72% of capacity w/ 15-yr avg tariffs", "Lower WACC"],
        ["Multi-jurisdiction", "7 countries, varying regulatory frameworks", "Higher WACC"],
        ["High leverage", "D/E 209%; target 68-72% D/Cap", "Higher Ke"],
        ["Growth stage", "CapEx-intensive, negative TTM FCF", "Higher WACC"],
        ["Renewable tailwinds", "Strong policy support (IRA, EU Green Deal)", "Lower WACC"],
        ["A3 credit rating", "Investment-grade, lower tier", "Moderate Kd"],
        ["Peer comparison", "Enlight WACC 7.6%; premium justified", "Higher WACC"],
    ], cw=[pw*0.22, pw*0.53, pw*0.25]))
    st.append(PageBreak())

    # ═══ 5. TERMINAL VALUE ═══
    st.append(Paragraph("5. TERMINAL VALUE", S['sec']))
    st.append(ColorBar(pw, 2, GOLD)); st.append(Spacer(1, 10))
    st.append(Paragraph("Method 1: Gordon Growth Model (Perpetuity Growth)", S['sub']))
    st.append(Paragraph("TV = UFCF(2030) x (1+g) / (WACC-g) = 984 x 1.025 / 0.055 = "
        "<b>NIS 18,338M</b>  |  PV of TV = 18,338 / 1.4693 = <b>NIS 12,481M</b>", S['body']))
    st.append(Spacer(1, 6))
    for b in ["Israel long-term inflation target: ~2.0%",
              "Global electricity demand growth: ~2-3% annually",
              "Renewable energy capacity growth: 5-8% globally (decelerating)",
              "Implied terminal EV/EBITDA: 18,338 / 1,770 = 10.4x (reasonable for mature renewables)"]:
        st.append(Paragraph(f"\u2022 {b}", S['bullet']))
    st.append(Spacer(1, 10))

    st.append(Paragraph("Method 2: Exit Multiple", S['sub']))
    st.append(Paragraph("TV = EBITDA(2030) x Exit Multiple = 1,770 x 10.0x = "
        "<b>NIS 17,700M</b>  |  PV of TV = 17,700 / 1.4693 = <b>NIS 12,046M</b>", S['body']))
    st.append(Spacer(1, 10))
    st.append(Paragraph("Terminal Value Summary", S['sub']))
    st.append(mktbl([
        ["Method", "Terminal Value (NIS M)", "PV of TV (NIS M)", "TV / Total EV"],
        ["Gordon Growth (2.5%)", "18,338", "12,481", "92.3%"],
        ["Exit Multiple (10x)", "17,700", "12,046", "92.0%"],
        ["Blended (50/50)", "18,019", "12,264", "92.2%"],
    ], cw=[pw*0.28, pw*0.24, pw*0.24, pw*0.24], hlast=True))
    st.append(Spacer(1, 16))

    # ═══ 6. DCF OUTPUT ═══
    st.append(Paragraph("6. DCF VALUATION OUTPUT", S['sec']))
    st.append(ColorBar(pw, 2, GOLD)); st.append(Spacer(1, 10))
    st.append(Paragraph("Discounted Cash Flow Summary (NIS Millions)", S['sub']))
    st.append(mktbl([
        ["Year", "UFCF", "Discount Factor @ 8.0%", "PV of UFCF"],
        ["2026E", "(379)", "0.9259", "(351)"],
        ["2027E", "291", "0.8573", "249"],
        ["2028E", "647", "0.7938", "514"],
        ["2029E", "845", "0.7350", "621"],
        ["2030E", "984", "0.6806", "670"],
        ["PV of FCFs", "", "", "1,703"],
    ], cw=[pw*0.20, pw*0.25, pw*0.30, pw*0.25], hlast=True))
    st.append(Spacer(1, 12))

    st.append(Paragraph("Enterprise Value to Equity Bridge", S['sub']))
    bd = [
        ["Component", "NIS Millions"],
        ["PV of FCFs (2026E-2030E)", "1,703"],
        ["(+) PV of Terminal Value (Blended)", "12,264"],
        ["= Enterprise Value", "13,967"],
        ["(-) Net Debt", "(3,500)"],
        ["(-) Minority Interests", "(200)"],
        ["(+) Associates & JVs", "150"],
        ["= Equity Value", "10,417"],
        ["/ Shares Outstanding", "38.1M"],
        ["Implied Share Price", "NIS 273.4 / share (~$74.9)"],
    ]
    bt = mktbl(bd, cw=[pw*0.55, pw*0.45])
    bt.setStyle(TableStyle([
        ('FONTNAME', (0,3), (-1,3), 'Helvetica-Bold'), ('LINEABOVE', (0,3), (-1,3), 0.75, NAVY),
        ('FONTNAME', (0,7), (-1,7), 'Helvetica-Bold'), ('LINEABOVE', (0,7), (-1,7), 0.75, NAVY),
        ('FONTNAME', (0,9), (-1,9), 'Helvetica-Bold'), ('FONTSIZE', (0,9), (-1,9), 10),
        ('TEXTCOLOR', (0,9), (-1,9), GREEN),
        ('BACKGROUND', (0,9), (-1,9), colors.HexColor("#E8F5E9")),
        ('LINEABOVE', (0,9), (-1,9), 1.5, GREEN),
    ]))
    st.append(bt); st.append(Spacer(1, 12))

    vt = mktbl([
        ["Metric", "Value"], ["Current Share Price", "NIS ~112"],
        ["DCF Implied Price", "NIS 273"], ["Upside / (Downside)", "+144%"],
        ["Implied EV/EBITDA '26E", "13.4x"],
    ], cw=[pw*0.45, pw*0.55])
    vt.setStyle(TableStyle([('FONTNAME', (1,3), (1,3), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1,3), (1,3), GREEN), ('FONTSIZE', (1,3), (1,3), 11)]))
    st.append(vt)
    st.append(PageBreak())

    # ═══ 7. SENSITIVITY ═══
    st.append(Paragraph("7. SENSITIVITY ANALYSIS", S['sec']))
    st.append(ColorBar(pw, 2, GOLD)); st.append(Spacer(1, 10))
    st.append(Paragraph("7.1 WACC vs. Perpetuity Growth Rate -> Implied Share Price (NIS)", S['sub']))
    s1 = mktbl([
        ["WACC \\ g", "1.5%", "2.0%", "2.5%", "3.0%", "3.5%"],
        ["6.5%", "360", "410", "485", "600", "810"],
        ["7.0%", "310", "350", "405", "490", "630"],
        ["7.5%", "270", "305", "350", "410", "510"],
        ["8.0%", "237", "265", "273", "330", "400"],
        ["8.5%", "210", "232", "260", "300", "350"],
        ["9.0%", "187", "205", "230", "265", "305"],
        ["9.5%", "167", "183", "205", "235", "268"],
    ], cw=[pw*0.17]+[pw*0.166]*5)
    s1.setStyle(TableStyle([
        ('BACKGROUND', (3,4), (3,4), GOLD), ('TEXTCOLOR', (3,4), (3,4), W),
        ('FONTNAME', (3,4), (3,4), 'Helvetica-Bold'), ('FONTNAME', (0,4), (0,4), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))
    st.append(s1); st.append(Spacer(1, 14))

    st.append(Paragraph("7.2 WACC vs. Exit Multiple -> Implied Share Price (NIS)", S['sub']))
    s2 = mktbl([
        ["WACC \\ Multiple", "8.0x", "9.0x", "10.0x", "11.0x", "12.0x"],
        ["6.5%", "295", "350", "405", "460", "515"],
        ["7.0%", "260", "310", "358", "408", "455"],
        ["7.5%", "230", "275", "318", "362", "405"],
        ["8.0%", "205", "245", "270", "322", "362"],
        ["8.5%", "183", "220", "257", "293", "330"],
        ["9.0%", "163", "198", "232", "267", "302"],
        ["9.5%", "147", "179", "211", "244", "276"],
    ], cw=[pw*0.20]+[pw*0.16]*5)
    s2.setStyle(TableStyle([
        ('BACKGROUND', (3,4), (3,4), GOLD), ('TEXTCOLOR', (3,4), (3,4), W),
        ('FONTNAME', (3,4), (3,4), 'Helvetica-Bold'), ('FONTNAME', (0,4), (0,4), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))
    st.append(s2); st.append(Spacer(1, 14))

    st.append(Paragraph("7.3 Revenue Growth vs. EBITDA Margin -> Implied EV (NIS Billions)", S['sub']))
    s3 = mktbl([
        ["Rev Growth \\ Margin", "63%", "67%", "71%", "75%", "79%"],
        ["+15%", "10.5", "11.3", "12.0", "12.8", "13.5"],
        ["+20%", "11.5", "12.4", "13.2", "14.1", "14.9"],
        ["+25%", "12.4", "13.4", "14.0", "15.0", "15.9"],
        ["+30%", "13.3", "14.3", "15.3", "16.3", "17.3"],
        ["+35%", "14.2", "15.3", "16.4", "17.5", "18.6"],
    ], cw=[pw*0.22]+[pw*0.156]*5)
    s3.setStyle(TableStyle([
        ('BACKGROUND', (3,3), (3,3), GOLD), ('TEXTCOLOR', (3,3), (3,3), W),
        ('FONTNAME', (3,3), (3,3), 'Helvetica-Bold'), ('FONTNAME', (0,3), (0,3), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))
    st.append(s3)
    st.append(PageBreak())

    # ═══ 8. COMPS ═══
    st.append(Paragraph("8. COMPARABLE COMPANIES ANALYSIS", S['sec']))
    st.append(ColorBar(pw, 2, GOLD)); st.append(Spacer(1, 10))
    st.append(Paragraph("Israeli & Global Renewable Energy Peers", S['sub']))
    cc = mktbl([
        ["Company", "Ticker", "Mkt Cap ($B)", "EV/Rev", "EV/EBITDA (Fwd)", "ND/EBITDA", "Margin"],
        ["Enlight Energy", "ENLT", "8.3", "15.0x", "18.0x", "5.5x", "55%"],
        ["OPC Energy", "OPCE", "5.1", "3.4x", "12.0x", "4.0x", "28%"],
        ["Energix Renewable", "ENRG", "2.3", "5.5x", "10.0x", "3.5x", "68%"],
        ["NextEra Energy", "NEE", "160.0", "7.0x", "13.0x", "4.5x", "65%"],
        ["Scatec ASA", "SCATC", "1.2", "4.0x", "8.0x", "6.0x", "60%"],
        ["Solaria Energia", "PVA", "0.8", "6.5x", "9.0x", "3.0x", "70%"],
        ["Median", "", "", "5.8x", "11.0x", "4.3x", "63%"],
        ["Nofar Energy", "NOFR", "1.2", "24.3x", "7.4x", "8.2x", "33%"],
    ], cw=[pw*0.18, pw*0.10, pw*0.12, pw*0.13, pw*0.17, pw*0.14, pw*0.16])
    cc.setStyle(TableStyle([
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,7), (-1,7), 'Helvetica-Bold'), ('LINEABOVE', (0,7), (-1,7), 1, NAVY),
        ('FONTNAME', (0,8), (-1,8), 'Helvetica-Bold'), ('BACKGROUND', (0,8), (-1,8), HDR_BG),
        ('LINEABOVE', (0,8), (-1,8), 1, NAVY),
    ]))
    st.append(cc); st.append(Spacer(1, 12))

    st.append(Paragraph("Key Peer Comparison Insights", S['sub']))
    st.append(mktbl([
        ["Metric", "Nofar vs. Peers", "Assessment"],
        ["Fwd EV/EBITDA", "7.4x vs. 11.0x median", "Significant discount on forward metrics"],
        ["TTM EV/EBITDA", "60.1x vs. 11.0x median", "Inflated by pre-operational base"],
        ["EBITDA Margin (Fwd)", "68-72% vs. 63% median", "Above peers - IPP-heavy model"],
        ["Leverage", "D/E 209% vs. ~100-150%", "Highest in peer group"],
        ["Growth Rate", "+76% vs. 15-25% peers", "Fastest growing"],
        ["Asset Quality", "72% contracted, 15yr avg", "Strong visibility"],
    ], cw=[pw*0.22, pw*0.35, pw*0.43]))
    st.append(Spacer(1, 12))

    st.append(Paragraph("Peer-Implied Valuation", S['sub']))
    st.append(mktbl([
        ["Method", "Multiple", "Metric", "Implied EV (NIS M)"],
        ["EV/EBITDA (2026E, median)", "11.0x", "1,071", "11,781"],
        ["EV/EBITDA (2026E, -1s)", "9.0x", "1,071", "9,639"],
        ["EV/EBITDA (2026E, +1s)", "13.0x", "1,071", "13,923"],
        ["EV/Revenue (2026E, median)", "5.8x", "1,040", "6,032"],
        ["EV/MW (installed cap.)", "$1.2M/MW", "2,296 MW", "10,060"],
        ["Peer Implied Share Price", "", "", "NIS 171 / share"],
    ], cw=[pw*0.32, pw*0.18, pw*0.22, pw*0.28], hlast=True))
    st.append(PageBreak())

    # ═══ 9. SCENARIO ANALYSIS ═══
    st.append(Paragraph("9. SCENARIO ANALYSIS: BULL / BASE / BEAR", S['sec']))
    st.append(ColorBar(pw, 2, GOLD)); st.append(Spacer(1, 10))
    st.append(Paragraph("Scenario Parameter Comparison", S['sub']))
    sp = mktbl([
        ["Parameter", "Bear Case", "Base Case", "Bull Case"],
        ["2026E Revenue (NIS M)", "850", "1,040", "1,250"],
        ["2026E EBITDA Margin", "60%", "68%", "72%"],
        ["2030E Revenue (NIS M)", "1,350", "1,770", "2,200"],
        ["2030E EBITDA Margin", "62%", "72.5%", "78%"],
        ["WACC", "9.5%", "8.0%", "7.0%"],
        ["Terminal Growth Rate", "1.5%", "2.5%", "3.0%"],
        ["Exit Multiple", "8.0x", "10.0x", "12.0x"],
        ["CapEx (5-yr cumulative)", "NIS 4,000M", "NIS 3,550M", "NIS 3,200M"],
    ], cw=[pw*0.30, pw*0.22, pw*0.24, pw*0.24])
    sp.setStyle(TableStyle([
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TEXTCOLOR', (1,1), (1,-1), RED), ('TEXTCOLOR', (2,1), (2,-1), NAVY),
        ('FONTNAME', (2,1), (2,-1), 'Helvetica-Bold'), ('TEXTCOLOR', (3,1), (3,-1), GREEN),
    ]))
    st.append(sp); st.append(Spacer(1, 14))

    st.append(Paragraph("Scenario Narratives", S['sub'])); st.append(Spacer(1, 4))
    st.append(Paragraph("<b>BEAR CASE (NIS 130/share | +16% upside)</b>", S['ssub']))
    for i in ["Project delays push commissioning 6-12 months",
              "Interest rates remain elevated, increasing financing costs",
              "Merchant power prices decline 15-20%",
              "EU regulatory tightening; US IRA headwinds"]:
        st.append(Paragraph(f"\u2022 {i}", S['bullet']))
    st.append(Spacer(1, 6))
    st.append(Paragraph("<b>BASE CASE (NIS 273/share | +144% upside)</b>", S['ssub']))
    for i in ["Management executes per guidance; 2026E EBITDA NIS 1,071M",
              "Gradual deleveraging as operational cash flows ramp",
              "Stable regulatory environment; moderate tariff escalations"]:
        st.append(Paragraph(f"\u2022 {i}", S['bullet']))
    st.append(Spacer(1, 6))
    st.append(Paragraph("<b>BULL CASE (NIS 440/share | +293% upside)</b>", S['ssub']))
    for i in ["Accelerated commissioning ahead of schedule",
              "Power price upside from tightening energy markets",
              "Strategic M&A creates additional value",
              "Battery storage margin-accretive faster than expected"]:
        st.append(Paragraph(f"\u2022 {i}", S['bullet']))
    st.append(Spacer(1, 14))

    st.append(Paragraph("Valuation Summary by Scenario (NIS / share)", S['sub']))
    sv = mktbl([
        ["Method", "Bear", "Base", "Bull"],
        ["DCF (Gordon Growth)", "125", "278", "460"],
        ["DCF (Exit Multiple)", "135", "270", "420"],
        ["Peer Comps (EV/EBITDA)", "110", "171", "230"],
        ["Blended Average", "130", "273", "440"],
    ], cw=[pw*0.34, pw*0.22, pw*0.22, pw*0.22], hlast=True)
    sv.setStyle(TableStyle([
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TEXTCOLOR', (1,1), (1,-1), RED), ('TEXTCOLOR', (2,1), (2,-1), NAVY),
        ('FONTNAME', (2,1), (2,-1), 'Helvetica-Bold'), ('TEXTCOLOR', (3,1), (3,-1), GREEN),
    ]))
    st.append(sv); st.append(Spacer(1, 16))

    st.append(Paragraph("Football Field Valuation Summary (NIS / share)", S['sub']))
    st.append(Spacer(1, 8))
    st.append(FootballBar("DCF (Perp. Growth)", 125, 278, 460, 50, 500, BLUE))
    st.append(Spacer(1, 6))
    st.append(FootballBar("DCF (Exit Multiple)", 135, 270, 420, 50, 500, LBLUE))
    st.append(Spacer(1, 6))
    st.append(FootballBar("Peer EV/EBITDA", 110, 171, 230, 50, 500, GOLD))
    st.append(Spacer(1, 6))
    st.append(FootballBar("52-Week Range", 80, 112, 145, 50, 500, MGRAY))
    st.append(Spacer(1, 8))
    st.append(Paragraph("Current Price: NIS 112  |  DCF Target: NIS 273", S['ssub']))
    st.append(PageBreak())

    # ═══ 10. RISKS ═══
    st.append(Paragraph("10. KEY RISKS & DISCLAIMERS", S['sec']))
    st.append(ColorBar(pw, 2, GOLD)); st.append(Spacer(1, 10))
    st.append(Paragraph("Investment Risks", S['sub']))
    st.append(mktbl([
        ["Risk Category", "Description", "Probability", "Impact"],
        ["Execution", "Delays in 2,296 MW pipeline commissioning", "Medium", "High"],
        ["Financing", "Inability to refinance NIS 540M Series 1 bonds (2027)", "Low", "High"],
        ["Interest Rates", "Higher-for-longer on NIS 4.3B debt", "Medium", "High"],
        ["Regulatory", "Subsidy/tariff changes across 7 markets", "Medium", "Medium"],
        ["FX", "NIS appreciation vs EUR/USD", "Medium", "Medium"],
        ["Merchant Price", "28% uncontracted capacity exposed to spot", "Medium", "Medium"],
        ["Technology", "Battery storage degradation risk", "Low", "Medium"],
        ["Concentration", "Reliance on Israeli and Italian C&I markets", "Low", "Low"],
    ], cw=[pw*0.15, pw*0.50, pw*0.15, pw*0.20]))
    st.append(Spacer(1, 12))

    st.append(Paragraph("Model Limitations", S['sub']))
    for i, l in enumerate([
        "Projections rely heavily on management's 2026E EBITDA guidance of NIS 1,071M (+209% from TTM)",
        "Terminal value represents ~92% of total EV - amplifies sensitivity to long-term assumptions",
        "Net debt estimate of NIS 3.5B may vary with project-level non-recourse financing structures",
        "Multi-currency operations make precise NIS forecasting challenging",
        "Proportionate consolidation of JV interests may differ from IFRS reporting",
    ], 1):
        st.append(Paragraph(f"{i}. {l}", S['bullet']))
    st.append(Spacer(1, 12))

    st.append(Paragraph("Key DCF Formulas", S['sub']))
    st.append(mktbl([
        ["Formula", "Definition"],
        ["UFCF", "NOPAT + D&A - CapEx - dWC"],
        ["NOPAT", "EBIT x (1 - Tax Rate)"],
        ["WACC", "(E/V x Ke) + (D/V x Kd x (1-t))"],
        ["Ke (CAPM)", "Rf + Beta x ERP + CRP"],
        ["Beta Levered", "Beta Unlevered x [1 + (1-t) x D/E]"],
        ["TV (Gordon)", "UFCF5 x (1+g) / (WACC - g)"],
        ["TV (Exit)", "EBITDA5 x Exit Multiple"],
        ["PV Factor", "1 / (1 + WACC)^n"],
        ["Equity Value", "Sum PV(UFCF) + PV(TV) - Net Debt - Minorities + Associates"],
    ], cw=[pw*0.25, pw*0.75]))
    st.append(Spacer(1, 20))

    st.append(ColorBar(pw, 1, LGRAY)); st.append(Spacer(1, 8))
    st.append(Paragraph(
        "<b>DISCLAIMER:</b> This analysis is prepared for educational and informational purposes only. "
        "It does not constitute investment advice, a recommendation, or a solicitation to buy or sell "
        "any security. All projections are based on publicly available information and analyst estimates "
        "as of February 2026. Actual results may differ materially. Past performance is not indicative "
        "of future results.", S['disc']))
    st.append(Spacer(1, 10))
    st.append(Paragraph("<b>Sources:</b>", S['disc']))
    for s in [
        "Nofar Energy Investor Relations (ir.nofar-energy.com)",
        "Yahoo Finance - NOFR.TA", "TASE - Nofar Energy",
        "Nofar Energy 2024 Annual Report", "Midroog Credit Rating Report (July 2024)",
        "Enlight Renewable Energy WACC (valueinvesting.io)",
        "Finerva - Green Energy 2025 Valuation Multiples",
        "IEA - Cost of Capital in Clean Energy Transitions",
    ]:
        st.append(Paragraph(f"\u2022 {s}", S['disc']))

    doc.build(st, onFirstPage=hf, onLaterPages=hf)
    print(f"\nPDF generated successfully: {OUT}")
    print(f"File size: {os.path.getsize(OUT)/1024:.1f} KB")

if __name__ == "__main__":
    build()
