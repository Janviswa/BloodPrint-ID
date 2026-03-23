# report_generator.py — Light mode professional PDF with logo
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect
from datetime import datetime
import os

REPORTS_DIR = 'reports'
os.makedirs(REPORTS_DIR, exist_ok=True)

# Support both 'Logo.png' (Windows/Git) and 'logo.png' (Linux/Render)
def _find_logo():
    base = os.path.dirname(os.path.abspath(__file__))
    for name in ('Logo.png', 'logo.png', 'LOGO.png'):
        p = os.path.join(base, name)
        if os.path.exists(p):
            return p
    return os.path.join(base, 'Logo.png')   # fallback (will fail gracefully)

LOGO_PATH = _find_logo()

# ── Light mode palette ────────────────────────────────────────
C = {
    'bg':        colors.HexColor('#ffffff'),
    'bg2':       colors.HexColor('#f8f9fc'),
    'bg3':       colors.HexColor('#f0f2f8'),
    'bg4':       colors.HexColor('#e8ebf5'),
    'b1':        colors.HexColor('#dde2f0'),
    'b2':        colors.HexColor('#c5cce8'),
    'red':       colors.HexColor('#e63946'),
    'red_light': colors.HexColor('#fde8ea'),
    'red2':      colors.HexColor('#c1121f'),
    'cyan':      colors.HexColor('#0077b6'),
    'cyan_light':colors.HexColor('#e0f4ff'),
    'gold':      colors.HexColor('#d4651a'),
    'gold_light':colors.HexColor('#fff3e8'),
    'green':     colors.HexColor('#1a7a42'),
    'green_light':colors.HexColor('#e8faf0'),
    'pink':      colors.HexColor('#d00060'),
    'text':      colors.HexColor('#1a1a2e'),
    'text2':     colors.HexColor('#4a5080'),
    'text3':     colors.HexColor('#8890b8'),
    'white':     colors.white,
    'dark':      colors.HexColor('#06060f'),
    'loop':      colors.HexColor('#0077b6'),
    'whorl':     colors.HexColor('#d00060'),
    'arch':      colors.HexColor('#1a7a42'),
}
BG_COL = {
    'O+': colors.HexColor('#27ae60'), 'O-': colors.HexColor('#1a7a42'),
    'A+': colors.HexColor('#2980b9'), 'A-': colors.HexColor('#1a5a8a'),
    'B+': colors.HexColor('#c0392b'), 'B-': colors.HexColor('#8a1a18'),
    'AB+':colors.HexColor('#7d3c98'), 'AB-':colors.HexColor('#5a2070'),
}
PAT_COL = {'loop': C['loop'], 'whorl': C['pink'], 'arch': C['green']}


# ── Custom Flowables ──────────────────────────────────────────
class HBar(Flowable):
    """Horizontal bar — shows ACTUAL percentage (not relative)."""
    def __init__(self, label, actual_pct, color, width=480, height=17, is_top=False):
        super().__init__()
        self.label      = label
        self.actual_pct = min(max(actual_pct, 0), 100)   # real % 0-100
        self.color      = color
        self.is_top     = is_top
        self._fixedWidth  = width
        self._fixedHeight = height + 8

    def wrap(self, aW, aH):
        return self._fixedWidth, self._fixedHeight

    def draw(self):
        cv     = self.canv
        h      = self._fixedHeight - 6
        y      = 4
        label_w = 40
        pct_w   = 46

        # Label
        cv.setFont('Helvetica-Bold' if self.is_top else 'Helvetica', 8.5)
        cv.setFillColor(C['gold'] if self.is_top else self.color)
        cv.drawString(0, y + 4, self.label)

        # Track
        tx = label_w + 4
        tw = self._fixedWidth - label_w - pct_w - 8
        cv.setFillColor(C['b1'])
        cv.roundRect(tx, y + 2, tw, h - 4, 3, fill=1, stroke=0)

        # Fill — scaled so 30% looks like 30% of track, not 100%
        # We use actual_pct / 35 * tw so max ~30% fills most of bar
        # but really: fill proportional to actual value, max bar = 35% full track
        fill_w = max(3, tw * self.actual_pct / 35)
        fill_w = min(fill_w, tw)  # never exceed track
        cv.setFillColor(self.color)
        cv.roundRect(tx, y + 2, fill_w, h - 4, 3, fill=1, stroke=0)

        # Highlight strip
        if fill_w > 8:
            cv.setFillColor(colors.Color(1, 1, 1, alpha=0.35))
            cv.roundRect(tx, y + (h - 4) * 0.6, fill_w, (h - 4) * 0.35, 2, fill=1, stroke=0)

        # Actual % text — always shows real number
        cv.setFont('Helvetica-Bold', 8.5)
        cv.setFillColor(C['gold'] if self.is_top else C['text2'])
        pct_str = f"{self.actual_pct:.1f}%"
        if self.is_top:
            pct_str += "  ◄"
        cv.drawRightString(self._fixedWidth, y + 4, pct_str)


class SectionHeader(Flowable):
    def __init__(self, title, width=530, accent=None):
        super().__init__()
        self.title        = title
        self.accent       = accent or C['red']
        self._fixedWidth  = width
        self._fixedHeight = 26

    def wrap(self, aW, aH):
        return self._fixedWidth, self._fixedHeight

    def draw(self):
        cv = self.canv
        w, h = self._fixedWidth, self._fixedHeight
        cv.setFillColor(C['bg3'])
        cv.roundRect(0, 0, w, h, 4, fill=1, stroke=0)
        cv.setFillColor(self.accent)
        cv.rect(0, 0, 3, h, fill=1, stroke=0)
        cv.setFont('Helvetica-Bold', 8.5)
        cv.setFillColor(C['text2'])
        cv.drawString(12, 8, self.title.upper())
        cv.setFillColor(self.accent)
        cv.circle(w - 12, h / 2, 3, fill=1, stroke=0)


class PatternBadge(Flowable):
    def __init__(self, pattern, full_name, confidence, low_conf, width=530):
        super().__init__()
        self.pattern   = pattern
        self.full_name = full_name
        self.conf      = confidence
        self.low_conf  = low_conf
        self._fixedWidth  = width
        self._fixedHeight = 62

    def wrap(self, aW, aH):
        return self._fixedWidth, self._fixedHeight

    def draw(self):
        cv  = self.canv
        w, h = self._fixedWidth, self._fixedHeight
        col  = PAT_COL.get(self.pattern, C['cyan'])

        cv.setFillColor(C['bg2'])
        cv.roundRect(0, 0, w, h, 6, fill=1, stroke=0)
        cv.setStrokeColor(C['b1'])
        cv.setLineWidth(0.8)
        cv.roundRect(0, 0, w, h, 6, fill=0, stroke=1)
        cv.setFillColor(col)
        cv.roundRect(0, 0, 4, h, 3, fill=1, stroke=0)

        cv.setFont('Helvetica-Bold', 22)
        cv.setFillColor(col)
        cv.drawString(16, h - 32, self.full_name)

        # Confidence chip
        conf_str = f"  {self.conf*100:.1f}%  {'LOW CONFIDENCE' if self.low_conf else 'HIGH CONFIDENCE'}  "
        chip_bg  = C['gold_light'] if self.low_conf else C['green_light']
        chip_col = C['gold']       if self.low_conf else C['green']
        cv.setFont('Helvetica-Bold', 7.5)
        tw = cv.stringWidth(conf_str, 'Helvetica-Bold', 7.5)
        cx = w - tw - 16
        cy = h - 28
        cv.setFillColor(chip_bg)
        cv.roundRect(cx - 4, cy - 3, tw + 8, 16, 4, fill=1, stroke=0)
        cv.setStrokeColor(chip_col)
        cv.setLineWidth(0.6)
        cv.roundRect(cx - 4, cy - 3, tw + 8, 16, 4, fill=0, stroke=1)
        cv.setFillColor(chip_col)
        cv.drawString(cx, cy + 1, conf_str.strip())

        cv.setFont('Helvetica', 8.5)
        cv.setFillColor(C['text3'])
        cv.drawString(16, 13, f"Pattern: {self.pattern.capitalize()}   ·   Blood Group Statistical Correlation")


class TopBGBadge(Flowable):
    def __init__(self, top_bg, top_3, width=530):
        super().__init__()
        self.top_bg = top_bg
        self.top_3  = top_3
        self._fixedWidth  = width
        self._fixedHeight = 58

    def wrap(self, aW, aH):
        return self._fixedWidth, self._fixedHeight

    def draw(self):
        cv  = self.canv
        w, h = self._fixedWidth, self._fixedHeight
        bc   = BG_COL.get(self.top_bg, C['cyan'])

        cv.setFillColor(C['bg2'])
        cv.roundRect(0, 0, w, h, 6, fill=1, stroke=0)
        cv.setStrokeColor(C['b1'])
        cv.setLineWidth(0.8)
        cv.roundRect(0, 0, w, h, 6, fill=0, stroke=1)
        cv.setFillColor(bc)
        cv.roundRect(0, 0, 4, h, 3, fill=1, stroke=0)

        # Circle
        cx, cy, r = 36, h / 2, 20
        cv.setFillColor(bc)
        cv.circle(cx, cy, r, fill=1, stroke=0)
        cv.setFillColor(colors.white)
        fs = 13 if len(self.top_bg) <= 2 else 10
        cv.setFont('Helvetica-Bold', fs)
        tw = cv.stringWidth(self.top_bg, 'Helvetica-Bold', fs)
        cv.drawString(cx - tw / 2, cy - fs * 0.38, self.top_bg)

        cv.setFont('Helvetica', 7.5)
        cv.setFillColor(C['text3'])
        cv.drawString(66, h - 16, 'TOP PREDICTION')
        cv.setFont('Helvetica-Bold', 20)
        cv.setFillColor(C['gold'])
        cv.drawString(66, h - 38, self.top_bg)
        cv.setFont('Helvetica', 8)
        cv.setFillColor(C['text2'])
        cv.drawString(66, 11, 'Top 3:  ' + '   |   '.join(self.top_3[:3]))


class InfoTable(Flowable):
    def __init__(self, rows, width=530, row_h=19):
        super().__init__()
        self.rows   = rows
        self.row_h  = row_h
        self._fixedWidth  = width
        self._fixedHeight = len(rows) * row_h

    def wrap(self, aW, aH):
        return self._fixedWidth, self._fixedHeight

    def draw(self):
        cv  = self.canv
        w   = self._fixedWidth
        rh  = self.row_h
        kw  = w * 0.30

        for i, (k, v) in enumerate(self.rows):
            y  = self._fixedHeight - (i + 1) * rh
            bg = C['bg3'] if i % 2 == 0 else C['bg2']
            cv.setFillColor(bg)
            cv.rect(0, y, w, rh, fill=1, stroke=0)
            cv.setFillColor(C['bg4'])
            cv.rect(0, y, kw, rh, fill=1, stroke=0)
            cv.setFont('Helvetica-Bold', 7.5)
            cv.setFillColor(C['cyan'])
            cv.drawString(8, y + 6, str(k).upper())
            cv.setFont('Helvetica', 8)
            cv.setFillColor(C['text'])
            cv.drawString(kw + 8, y + 6, str(v))
            cv.setStrokeColor(C['b1'])
            cv.setLineWidth(0.3)
            cv.line(0, y, w, y)

        cv.setStrokeColor(C['b2'])
        cv.setLineWidth(0.7)
        cv.roundRect(0, 0, w, self._fixedHeight, 4, fill=0, stroke=1)


# ── Page background + header/footer ──────────────────────────
def _draw_background(canvas_obj, doc):
    W, H = A4
    canvas_obj.saveState()

    # White background
    canvas_obj.setFillColor(C['bg'])
    canvas_obj.rect(0, 0, W, H, fill=1, stroke=0)

    # Subtle grid
    canvas_obj.setStrokeColor(colors.Color(0.88, 0.90, 0.96, alpha=1))
    canvas_obj.setLineWidth(0.3)
    grid = 24
    for x in range(0, int(W) + grid, grid):
        canvas_obj.line(x, 0, x, H)
    for y in range(0, int(H) + grid, grid):
        canvas_obj.line(0, y, W, y)

    # Faint red glow top right
    canvas_obj.setFillColor(colors.Color(0.9, 0.22, 0.27, alpha=0.04))
    canvas_obj.circle(W, H, 280, fill=1, stroke=0)

    # ── SINGLE WATERMARK per page — centered diagonal
    canvas_obj.saveState()
    canvas_obj.setFillColor(colors.Color(0.82, 0.85, 0.94, alpha=1))
    canvas_obj.setFont('Helvetica-Bold', 60)
    canvas_obj.translate(W / 2, H / 2)
    canvas_obj.rotate(35)
    tw = canvas_obj.stringWidth('BloodPrint ID', 'Helvetica-Bold', 60)
    canvas_obj.drawString(-tw / 2, 0, 'BloodPrint ID')
    canvas_obj.restoreState()

    # ── TOP HEADER BAR — dark
    canvas_obj.setFillColor(C['dark'])
    canvas_obj.rect(0, H - 30, W, 30, fill=1, stroke=0)
    canvas_obj.setFillColor(C['red'])
    canvas_obj.rect(0, H - 31, W, 1.5, fill=1, stroke=0)

    # Logo in header
    if os.path.exists(LOGO_PATH):
        try:
            canvas_obj.drawImage(
                LOGO_PATH, 14, H - 26,
                width=20, height=20,
                preserveAspectRatio=True, mask='auto'
            )
        except Exception:
            pass

    canvas_obj.setFont('Helvetica-Bold', 8)
    canvas_obj.setFillColor(colors.HexColor('#8890b8'))
    canvas_obj.drawString(40, H - 20, 'BLOODPRINT ID  |  FINGERPRINT PATTERN ANALYSIS REPORT')
    canvas_obj.setFont('Helvetica', 7.5)
    canvas_obj.drawRightString(W - 14, H - 20, f'Page {doc.page}  |  Research Tool - Not for Medical Use')

    # ── BOTTOM FOOTER
    canvas_obj.setFillColor(C['bg3'])
    canvas_obj.rect(0, 0, W, 22, fill=1, stroke=0)
    canvas_obj.setFillColor(C['b2'])
    canvas_obj.rect(0, 22, W, 0.7, fill=1, stroke=0)
    canvas_obj.setFont('Helvetica', 7)
    canvas_obj.setFillColor(C['text3'])
    canvas_obj.drawString(14, 7, 'BloodPrint ID  |  Educational & Research Purposes Only  |  Not a Medical Diagnostic Tool')
    canvas_obj.drawRightString(W - 14, 7, 'bloodprintid.research')

    canvas_obj.restoreState()


# ── Style helper ──────────────────────────────────────────────
def _p(text, fs=9, color=None, bold=False, align=TA_LEFT,
       leading=None, sb=0, sa=2):
    return Paragraph(text, ParagraphStyle('_',
        fontName  = 'Helvetica-Bold' if bold else 'Helvetica',
        fontSize  = fs,
        textColor = color or C['text'],
        alignment = align,
        spaceBefore=sb, spaceAfter=sa,
        leading   = leading or (fs * 1.45),
    ))


# ── Main ─────────────────────────────────────────────────────
def generate_pdf(result: dict, rid: int, display_name: str = None) -> str:
    pdf_path = os.path.join(REPORTS_DIR, f'BloodPrint_Report_{rid}.pdf')
    W, H     = A4
    margin   = 18 * mm
    usable   = W - 2 * margin

    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=13 * mm, bottomMargin=10 * mm,
    )

    pattern   = result.get('pattern', 'loop')
    info      = result.get('pattern_info', {})
    conf      = result.get('confidence', 0)
    low_conf  = result.get('low_confidence', False)
    bg_probs  = result.get('blood_group_probs', {})
    pat_probs = result.get('pattern_probs', {})
    top_bg    = result.get('top_blood_group', 'N/A')
    top_3     = result.get('top_3', [])
    quality   = result.get('image_quality', 'N/A')
    rdense    = result.get('ridge_density', 'N/A')
    clarity   = result.get('clarity_score', 0)
    density   = result.get('density_score', 0)
    edge      = result.get('edge_ratio', 0)
    valid     = result.get('valid_fingerprint', True)
    filename  = result.get('filename', 'unknown')
    created   = result.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    pat_col   = PAT_COL.get(pattern, C['cyan'])

    story = []
    story.append(Spacer(1, 4 * mm))

    # ── Title block with logo
    from reportlab.platypus import Image as RLImage

    logo_exists = os.path.exists(LOGO_PATH)
    if logo_exists:
        try:
            logo_img = RLImage(LOGO_PATH, width=40, height=40)
            hdr_tbl = Table([[
                logo_img,
                _p('<b>BloodPrint ID</b>', fs=24, color=C['dark']),
                _p(f'Report #{rid}', fs=10, color=C['text2'], align=TA_RIGHT),
            ]], colWidths=[48, usable * 0.5, usable - 48 - usable * 0.5])
        except Exception:
            logo_exists = False

    if not logo_exists:
        hdr_tbl = Table([[
            _p('<b>BloodPrint ID</b>', fs=24, color=C['dark']),
            _p(f'Report #{rid}', fs=10, color=C['text2'], align=TA_RIGHT),
        ]], colWidths=[usable * 0.6, usable * 0.4])

    hdr_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), C['bg']),
        ('TOPPADDING',    (0,0),(-1,-1), 0),
        ('BOTTOMPADDING', (0,0),(-1,-1), 6),
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (0,0),(-1,-1), 0),
        ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
        ('LINEBELOW',     (0,0),(-1,-1), 2, C['red']),
    ]))
    story.append(hdr_tbl)
    story.append(Spacer(1, 3 * mm))
    story.append(_p('Fingerprint Pattern &amp; Blood Group Statistical Analysis',
                    fs=8.5, color=C['text2'], sa=0))
    story.append(Spacer(1, 8 * mm))

    # ── Session info
    story.append(SectionHeader('Session Information', width=usable))
    story.append(Spacer(1, 2 * mm))
    story.append(InfoTable([
        ('Report ID',         f'#{rid}'),
        ('Patient / User',    display_name or result.get('username', 'N/A')),
        ('Filename',          filename),
        ('Generated',         created),
        ('Image Quality',     quality),
        ('Ridge Density',     rdense),
        ('Clarity Score',     f'{clarity}'),
        ('Density Score',     f'{density}'),
        ('Edge Ratio',        f'{edge}'),
        ('Valid Fingerprint', 'Yes' if valid else 'Uncertain'),
    ], width=usable))
    story.append(Spacer(1, 6 * mm))

    # ── Pattern analysis
    story.append(SectionHeader('Fingerprint Pattern Analysis', width=usable, accent=pat_col))
    story.append(Spacer(1, 2 * mm))
    story.append(PatternBadge(pattern, info.get('full_name', pattern.title()),
                              conf, low_conf, width=usable))
    story.append(Spacer(1, 4 * mm))

    story.append(_p(info.get('description', ''), fs=8.5, color=C['text2'],
                    align=TA_JUSTIFY, leading=13))
    story.append(Spacer(1, 3 * mm))

    story.append(_p('Key Characteristics', fs=8.5, color=C['cyan'], bold=True))
    story.append(Spacer(1, 2 * mm))
    char_rows = [[
        _p(f'<b>{i+1}.</b>', fs=8, color=pat_col, bold=True),
        _p(ch, fs=8.5, color=C['text2'], leading=12),
    ] for i, ch in enumerate(info.get('characteristics', []))]
    if char_rows:
        char_tbl = Table(char_rows, colWidths=[14, usable - 14])
        char_tbl.setStyle(TableStyle([
            ('TOPPADDING',    (0,0),(-1,-1), 3),
            ('BOTTOMPADDING', (0,0),(-1,-1), 3),
            ('LEFTPADDING',   (0,0),(-1,-1), 4),
            ('RIGHTPADDING',  (0,0),(-1,-1), 0),
            ('VALIGN',        (0,0),(-1,-1), 'TOP'),
            ('ROWBACKGROUNDS',(0,0),(-1,-1), [C['bg2'], C['bg3']]),
            ('LINEBELOW',     (0,0),(-2,-1), 0.3, C['b1']),
        ]))
        story.append(char_tbl)

    story.append(Spacer(1, 2 * mm))
    story.append(_p(f'Ridge Count:  {info.get("ridge_count","N/A")}',
                    fs=8, color=C['text3']))
    story.append(Spacer(1, 4 * mm))

    # Pattern prob bars — show actual %
    story.append(_p('Pattern Probability Distribution', fs=8.5, color=C['cyan'], bold=True))
    story.append(Spacer(1, 3 * mm))
    for p_name, prob in sorted(pat_probs.items(), key=lambda x: x[1], reverse=True):
        pc = PAT_COL.get(p_name, C['cyan'])
        story.append(HBar(
            label      = p_name.capitalize(),
            actual_pct = prob * 100,
            color      = pc,
            width      = usable,
            height     = 16,
            is_top     = (p_name == pattern),
        ))
        story.append(Spacer(1, 2 * mm))

    story.append(Spacer(1, 5 * mm))

    # ── PAGE BREAK — page 2 starts here
    from reportlab.platypus import PageBreak
    story.append(PageBreak())

    # ── Blood group
    story.append(SectionHeader('Blood Group Statistical Likelihood',
                               width=usable, accent=C['gold']))
    story.append(Spacer(1, 2 * mm))
    story.append(TopBGBadge(top_bg, top_3, width=usable))
    story.append(Spacer(1, 5 * mm))
    story.append(_p('All Blood Group Likelihoods  (actual research-based probabilities)',
                    fs=8.5, color=C['gold'], bold=True))
    story.append(Spacer(1, 3 * mm))

    # ── FIXED: use actual probability, NOT relative to max
    sorted_bg = sorted(bg_probs.items(), key=lambda x: x[1], reverse=True)
    for bg, prob in sorted_bg:
        bc = BG_COL.get(bg, C['cyan'])
        story.append(HBar(
            label      = bg,
            actual_pct = prob * 100,   # real % e.g. 28.0, 8.0, 5.0
            color      = bc,
            width      = usable,
            height     = 16,
            is_top     = (bg == top_bg),
        ))
        story.append(Spacer(1, 2 * mm))

    story.append(Spacer(1, 5 * mm))

    # ── References
    story.append(SectionHeader('Research References', width=usable, accent=C['text3']))
    story.append(Spacer(1, 3 * mm))
    for ref in [
        '[1] Dogra, T.D. et al. (2014). Fingerprint patterns and ABO blood group correlation. <i>Journal of Forensic Medicine and Toxicology.</i>',
        '[2] Nayak, V.C. et al. (2010). Correlating fingerprint patterns with blood groups. <i>Journal of Forensic and Legal Medicine.</i>',
        '[3] Igbigbi, P.S. &amp; Thumb, B. (2002). Dermatoglyphic patterns of Ugandan and Tanzanian subjects. <i>West African Journal of Medicine.</i>',
        '[4] Cummins, H. &amp; Midlo, C. (1961). <i>Finger Prints, Palms and Soles.</i> Dover Publications.',
    ]:
        story.append(_p(ref, fs=7.5, color=C['text3'], leading=11, sa=3))

    story.append(Spacer(1, 5 * mm))
    story.append(HRFlowable(width=usable, thickness=1.5, color=C['red']))
    story.append(Spacer(1, 3 * mm))

    # ── Disclaimer
    disc = Table([[_p(
        '<b>IMPORTANT DISCLAIMER</b><br/><br/>'
        'This report is for <b>EDUCATIONAL AND RESEARCH PURPOSES ONLY</b>. '
        'Blood group predictions are based on statistical correlations from published '
        'dermatoglyphic research and do NOT constitute a medical diagnosis.<br/><br/>'
        '<b>NOT a medical tool. Do NOT use for clinical decisions.</b><br/>'
        '<b>Always use a certified laboratory blood typing test for actual blood group determination.</b>',
        fs=8, color=C['text2'], align=TA_JUSTIFY, leading=12,
    )]], colWidths=[usable])
    disc.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), C['red_light']),
        ('LINEBEFORE',    (0,0),(-1,-1), 2.5, C['red']),
        ('TOPPADDING',    (0,0),(-1,-1), 10),
        ('BOTTOMPADDING', (0,0),(-1,-1), 10),
        ('LEFTPADDING',   (0,0),(-1,-1), 12),
        ('RIGHTPADDING',  (0,0),(-1,-1), 12),
    ]))
    story.append(disc)
    story.append(Spacer(1, 4 * mm))

    foot = Table([[
        _p('BloodPrint ID  |  Research Tool  |  Not for Medical Use',
           fs=7, color=C['text3']),
        _p(f'Report #{rid}  |  {created}',
           fs=7, color=C['text3'], align=TA_RIGHT),
    ]], colWidths=[usable / 2, usable / 2])
    foot.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), C['bg3']),
        ('TOPPADDING',    (0,0),(-1,-1), 6),
        ('BOTTOMPADDING', (0,0),(-1,-1), 6),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('RIGHTPADDING',  (0,0),(-1,-1), 8),
        ('LINEABOVE',     (0,0),(-1,-1), 0.5, C['b2']),
    ]))
    story.append(foot)

    doc.build(story,
              onFirstPage=_draw_background,
              onLaterPages=_draw_background)
    return pdf_path