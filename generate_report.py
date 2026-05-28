#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import (
    HexColor, white, black, Color
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors
import os

# ─── COLOR PALETTE ─────────────────────────────────────────────────────────────
DARK_BG      = HexColor('#0A0A0F')
ACCENT_GREEN = HexColor('#00FF88')
ACCENT_GOLD  = HexColor('#FFD700')
CARD_BG      = HexColor('#12121A')
CARD_BORDER  = HexColor('#1E1E2E')
TEXT_PRIMARY = HexColor('#FFFFFF')
TEXT_SECONDARY = HexColor('#B0B0C0')
TEXT_MUTED   = HexColor('#606080')
RED_ALERT    = HexColor('#FF4444')
BLUE_ACCENT  = HexColor('#4488FF')
PURPLE       = HexColor('#8844FF')

PAGE_W, PAGE_H = A4

# ─── CUSTOM FLOWABLES ──────────────────────────────────────────────────────────

class ColoredRect(Flowable):
    def __init__(self, w, h, fill_color, radius=6):
        super().__init__()
        self.w = w
        self.h = h
        self.fill_color = fill_color
        self.radius = radius

    def draw(self):
        self.canv.setFillColor(self.fill_color)
        self.canv.roundRect(0, 0, self.w, self.h, self.radius, fill=1, stroke=0)

class SectionDivider(Flowable):
    def __init__(self, label, color=ACCENT_GREEN):
        super().__init__()
        self.label = label
        self.color = color
        self.width  = PAGE_W - 4*cm
        self.height = 36

    def wrap(self, *args):
        return self.width, self.height

    def draw(self):
        c = self.canv
        # background bar
        c.setFillColor(CARD_BG)
        c.roundRect(0, 0, self.width, self.height - 4, 5, fill=1, stroke=0)
        # left accent bar
        c.setFillColor(self.color)
        c.rect(0, 0, 6, self.height - 4, fill=1, stroke=0)
        # label
        c.setFillColor(self.color)
        c.setFont('Helvetica-Bold', 13)
        c.drawString(16, 10, self.label)

class KPIBox(Flowable):
    def __init__(self, value, label, color=ACCENT_GREEN, width=4*cm):
        super().__init__()
        self.value = value
        self.label = label
        self.color = color
        self.bw    = width
        self.bh    = 2.6*cm

    def wrap(self, *args):
        return self.bw, self.bh

    def draw(self):
        c = self.canv
        c.setFillColor(CARD_BG)
        c.roundRect(0, 0, self.bw, self.bh, 8, fill=1, stroke=0)
        c.setStrokeColor(self.color)
        c.setLineWidth(1.5)
        c.roundRect(0, 0, self.bw, self.bh, 8, fill=0, stroke=1)
        # value
        c.setFillColor(self.color)
        c.setFont('Helvetica-Bold', 16)
        c.drawCentredString(self.bw/2, self.bh - 1.1*cm, self.value)
        # label
        c.setFillColor(TEXT_SECONDARY)
        c.setFont('Helvetica', 7.5)
        # wrap label
        words = self.label.split()
        lines = []
        line  = ''
        for w in words:
            test = (line+' '+w).strip()
            if c.stringWidth(test, 'Helvetica', 7.5) < self.bw - 8:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        y = 0.85*cm
        for ln in reversed(lines):
            c.drawCentredString(self.bw/2, y, ln)
            y -= 10

# ─── STYLES ───────────────────────────────────────────────────────────────────

def build_styles():
    styles = getSampleStyleSheet()
    base = dict(fontName='Helvetica', textColor=TEXT_PRIMARY,
                spaceAfter=6, leading=14)

    s = {}
    s['cover_title'] = ParagraphStyle('cover_title',
        fontSize=32, fontName='Helvetica-Bold',
        textColor=ACCENT_GREEN, alignment=TA_CENTER,
        spaceAfter=10, leading=38)
    s['cover_sub'] = ParagraphStyle('cover_sub',
        fontSize=17, fontName='Helvetica-Bold',
        textColor=ACCENT_GOLD, alignment=TA_CENTER,
        spaceAfter=8, leading=22)
    s['cover_tagline'] = ParagraphStyle('cover_tagline',
        fontSize=11, fontName='Helvetica',
        textColor=TEXT_SECONDARY, alignment=TA_CENTER,
        spaceAfter=6, leading=16)
    s['h1'] = ParagraphStyle('h1',
        fontSize=20, fontName='Helvetica-Bold',
        textColor=ACCENT_GREEN, spaceBefore=18, spaceAfter=8, leading=24)
    s['h2'] = ParagraphStyle('h2',
        fontSize=14, fontName='Helvetica-Bold',
        textColor=ACCENT_GOLD, spaceBefore=12, spaceAfter=6, leading=18)
    s['h3'] = ParagraphStyle('h3',
        fontSize=11, fontName='Helvetica-Bold',
        textColor=TEXT_PRIMARY, spaceBefore=8, spaceAfter=4, leading=15)
    s['body'] = ParagraphStyle('body',
        fontSize=9.5, fontName='Helvetica',
        textColor=TEXT_SECONDARY, spaceAfter=5, leading=14,
        alignment=TA_JUSTIFY)
    s['body_white'] = ParagraphStyle('body_white',
        fontSize=9.5, fontName='Helvetica',
        textColor=TEXT_PRIMARY, spaceAfter=5, leading=14,
        alignment=TA_JUSTIFY)
    s['bullet'] = ParagraphStyle('bullet',
        fontSize=9.5, fontName='Helvetica',
        textColor=TEXT_SECONDARY, spaceAfter=3, leading=14,
        leftIndent=12, bulletIndent=0)
    s['highlight'] = ParagraphStyle('highlight',
        fontSize=10.5, fontName='Helvetica-Bold',
        textColor=ACCENT_GREEN, spaceAfter=4, leading=15)
    s['caption'] = ParagraphStyle('caption',
        fontSize=8, fontName='Helvetica-Oblique',
        textColor=TEXT_MUTED, spaceAfter=4, alignment=TA_CENTER)
    s['toc_item'] = ParagraphStyle('toc_item',
        fontSize=10, fontName='Helvetica',
        textColor=TEXT_PRIMARY, spaceAfter=6, leading=14)
    s['footer_txt'] = ParagraphStyle('footer_txt',
        fontSize=7.5, fontName='Helvetica',
        textColor=TEXT_MUTED, alignment=TA_CENTER)
    s['quote'] = ParagraphStyle('quote',
        fontSize=10, fontName='Helvetica-Oblique',
        textColor=ACCENT_GOLD, spaceAfter=6, leading=15,
        leftIndent=20, rightIndent=20, alignment=TA_CENTER)
    s['stat_big'] = ParagraphStyle('stat_big',
        fontSize=28, fontName='Helvetica-Bold',
        textColor=ACCENT_GREEN, alignment=TA_CENTER,
        spaceAfter=2, leading=32)
    s['stat_label'] = ParagraphStyle('stat_label',
        fontSize=9, fontName='Helvetica',
        textColor=TEXT_SECONDARY, alignment=TA_CENTER,
        spaceAfter=8, leading=12)
    return s

# ─── TABLE HELPERS ─────────────────────────────────────────────────────────────

def dark_table(data, col_widths, header_color=ACCENT_GREEN):
    tbl = Table(data, colWidths=col_widths)
    n   = len(data)
    style = TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), CARD_BG),
        ('TEXTCOLOR',   (0,0), (-1,0), header_color),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0), 9),
        ('TOPPADDING',  (0,0), (-1,0), 7),
        ('BOTTOMPADDING',(0,0),(-1,0), 7),
        ('BACKGROUND',  (0,1), (-1,-1), DARK_BG),
        ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_SECONDARY),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,1), (-1,-1), 8.5),
        ('TOPPADDING',  (0,1), (-1,-1), 5),
        ('BOTTOMPADDING',(0,1),(-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [DARK_BG, CARD_BG]),
        ('GRID',        (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('ALIGN',       (0,0), (-1,-1), 'LEFT'),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING',(0,0), (-1,-1), 8),
    ])
    tbl.setStyle(style)
    return tbl

# ─── PAGE TEMPLATE ─────────────────────────────────────────────────────────────

def on_page(canvas, doc):
    canvas.saveState()
    # dark background
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # top thin line
    canvas.setStrokeColor(ACCENT_GREEN)
    canvas.setLineWidth(1.5)
    canvas.line(2*cm, PAGE_H - 1.2*cm, PAGE_W - 2*cm, PAGE_H - 1.2*cm)
    # header text
    canvas.setFont('Helvetica-Bold', 7)
    canvas.setFillColor(ACCENT_GREEN)
    canvas.drawString(2*cm, PAGE_H - 1*cm,
                      'BLACK FOREST SUPPLEMENTS × VENEZUELA  |  ESTUDIO DE MERCADO CONFIDENCIAL 2026')
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawRightString(PAGE_W - 2*cm, PAGE_H - 1*cm, f'Pág. {doc.page}')
    # bottom line
    canvas.setStrokeColor(CARD_BORDER)
    canvas.setLineWidth(0.8)
    canvas.line(2*cm, 1.5*cm, PAGE_W - 2*cm, 1.5*cm)
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawCentredString(PAGE_W/2, 0.9*cm,
        'Uso interno confidencial · Preparado mayo 2026 · Datos verificados de fuentes públicas y de mercado')
    canvas.restoreState()

def on_cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # gradient-like green band at top
    canvas.setFillColor(HexColor('#001A0D'))
    canvas.rect(0, PAGE_H - 6*cm, PAGE_W, 6*cm, fill=1, stroke=0)
    canvas.setStrokeColor(ACCENT_GREEN)
    canvas.setLineWidth(3)
    canvas.line(0, PAGE_H - 6*cm, PAGE_W, PAGE_H - 6*cm)
    # bottom band
    canvas.setFillColor(HexColor('#001A0D'))
    canvas.rect(0, 0, PAGE_W, 4*cm, fill=1, stroke=0)
    canvas.setStrokeColor(ACCENT_GREEN)
    canvas.setLineWidth(2)
    canvas.line(0, 4*cm, PAGE_W, 4*cm)
    # bottom text
    canvas.setFillColor(TEXT_MUTED)
    canvas.setFont('Helvetica', 8)
    canvas.drawCentredString(PAGE_W/2, 2*cm,
        'CONFIDENCIAL · USO EXCLUSIVO DEL SOLICITANTE · MAYO 2026')
    canvas.setFillColor(ACCENT_GREEN)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawCentredString(PAGE_W/2, 1.2*cm,
        'Datos basados en fuentes públicas, reportes de mercado y análisis del sector')
    canvas.restoreState()

# ─── BUILD PDF ─────────────────────────────────────────────────────────────────

def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2.2*cm,
        title='Black Forest × Venezuela – Estudio de Mercado 2026',
        author='Análisis Estratégico'
    )

    S = build_styles()
    story = []
    W = PAGE_W - 4*cm  # usable width

    # ══════════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 3.5*cm))
    story.append(Paragraph('🌲 BLACK FOREST SUPPLEMENTS', S['cover_title']))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('ESTUDIO DE MERCADO VENEZUELA', S['cover_sub']))
    story.append(Spacer(1, 0.5*cm))

    # Decorative line
    story.append(HRFlowable(width=W, thickness=2, color=ACCENT_GREEN, spaceAfter=0.5*cm))

    story.append(Paragraph(
        'Plan de Entrada al Mercado · Análisis Competitivo · Estrategia de Ventas',
        S['cover_tagline']))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        'Ruta hacia el liderazgo en suplementos naturales premium en Venezuela 2026–2028',
        S['cover_tagline']))

    story.append(Spacer(1, 1.5*cm))

    # Cover KPI row
    kpi_data = [
        [KPIBox('31M', 'Población\nVenezuela', ACCENT_GREEN),
         KPIBox('$2.1B', 'Mercado Supl.\nLATAM 2025', ACCENT_GOLD),
         KPIBox('+125%', 'Crecimiento\nE-commerce VE', BLUE_ACCENT),
         KPIBox('+8.6%', 'CAGR Mercado\nLATAM 2025–35', PURPLE)],
    ]
    kpi_tbl = Table(kpi_data, colWidths=[W/4]*4)
    kpi_tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(kpi_tbl)

    story.append(Spacer(1, 1.5*cm))
    story.append(HRFlowable(width=W, thickness=1, color=CARD_BORDER))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph('Preparado: Mayo 2026', S['caption']))
    story.append(Paragraph('Clasificación: CONFIDENCIAL — Uso interno exclusivo', S['caption']))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('ÍNDICE DE CONTENIDOS', ACCENT_GOLD))
    story.append(Spacer(1, 0.4*cm))

    toc = [
        ('01', 'Resumen Ejecutivo', 'El caso de negocios en 60 segundos'),
        ('02', 'Black Forest Supplements — Análisis de la Marca', 'Historia, productos, modelo y ventajas competitivas'),
        ('03', 'Contexto Macroeconómico de Venezuela', 'PIB, inflación, tipo de cambio y oportunidades'),
        ('04', 'Perfil del Consumidor Venezolano 2026', 'Segmentos, hábitos, poder adquisitivo'),
        ('05', 'Mercado de Fitness & Suplementos en Venezuela', 'Tamaño, crecimiento, canales, actores'),
        ('06', 'Análisis de la Competencia', 'Marcas, precios, puntos débiles'),
        ('07', 'Análisis FODA Estratégico', 'Fortalezas, oportunidades, debilidades, amenazas'),
        ('08', 'Marco Regulatorio & Logístico', 'Importaciones, permisos, aduana, logística'),
        ('09', 'Estrategia de Entrada al Mercado', 'Canales, posicionamiento, pricing, go-to-market'),
        ('10', 'Plan de Marketing Digital', 'Instagram, TikTok, influencers, e-commerce'),
        ('11', 'Proyecciones Financieras', 'Inversión, revenue, ROI, punto de equilibrio'),
        ('12', 'Hoja de Ruta 2026–2028', 'Cronograma de implementación fase a fase'),
        ('13', 'Riesgos & Mitigaciones', 'Escenarios y planes de contingencia'),
        ('14', 'Conclusiones & Próximos Pasos', 'Acciones inmediatas para empezar'),
    ]

    for num, title, desc in toc:
        row_data = [[
            Paragraph(f'<font color="#00FF88"><b>{num}</b></font>', S['toc_item']),
            Paragraph(f'<b>{title}</b><br/><font color="#606080" size="8">{desc}</font>', S['toc_item'])
        ]]
        t = Table(row_data, colWidths=[1.2*cm, W-1.2*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 0.3, CARD_BORDER),
        ]))
        story.append(t)
        story.append(Spacer(1, 2))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 01 — RESUMEN EJECUTIVO
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('01  |  RESUMEN EJECUTIVO', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('El Caso de Negocios', S['h2']))
    story.append(Paragraph(
        'Venezuela está viviendo una transformación económica sin precedentes. Con un PIB que creció '
        '8.66% en 2025 y proyecciones de hasta 15% para 2026 según Ecoanalítica, el país emerge como '
        'uno de los mercados de mayor crecimiento en América Latina. Paralelamente, el e-commerce '
        'venezolano explotó un 125% en 2025 y el 92% de los usuarios de internet está activo en '
        'redes sociales. Este contexto crea una ventana de oportunidad única para Black Forest '
        'Supplements: una marca premium americana que llega antes que la competencia consolide el mercado.',
        S['body']))

    story.append(Spacer(1, 0.2*cm))

    exec_points = [
        ('OPORTUNIDAD', ACCENT_GREEN,
         'El mercado de suplementos deportivos en LATAM alcanzará $4.8B para 2035 (CAGR 8.6%). '
         'Venezuela, con crecimiento del sector fitness y una clase alta/media-alta creciente, '
         'representa un mercado virgen para suplementos naturales premium.'),
        ('VENTAJA ÚNICA', ACCENT_GOLD,
         'Black Forest tiene una ventaja cultural extraordinaria: sus fundadores son de origen '
         'latinoamericano y la empresa está en Miami (Hialeah, FL) — la ciudad más venezolana '
         'de EE.UU. Esto facilita conexiones, logística y credibilidad local.'),
        ('MODELO DE ENTRADA', BLUE_ACCENT,
         'Canal 100% digital vía Instagram + WhatsApp Business + tienda online propia. '
         'Sin necesidad de inversión en retail físico. Envíos directos desde Miami via '
         'casilleros/courier — mínima fricción burocrática.'),
        ('POTENCIAL', PURPLE,
         'Mercado objetivo: 400,000–600,000 venezolanos con poder adquisitivo >$500/mes. '
         'Objetivo año 1: capturar 1,500–3,000 clientes. Revenue potencial $300K–$600K USD en 24 meses.'),
    ]

    for label, color, text in exec_points:
        row = [[
            Paragraph(f'<font color="#{color.hexval()[2:]}"><b>{label}</b></font>',
                      S['h3']),
            Paragraph(text, S['body'])
        ]]
        t = Table(row, colWidths=[3.5*cm, W - 3.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 0.5, color),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 02 — BLACK FOREST SUPPLEMENTS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('02  |  BLACK FOREST SUPPLEMENTS — ANÁLISIS DE MARCA', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('Historia y Perfil Corporativo', S['h2']))
    story.append(Paragraph(
        'Black Forest Supplements (BFS) fue fundada el 13 de diciembre de 2021 y oficialmente '
        'constituida el 14 de diciembre de 2021. Su sede está en Hialeah, Florida — el corazón '
        'de la comunidad venezolana y latinoamericana en EE.UU. La empresa se auto-define como '
        '"America\'s Supplements Brand" y opera como un startup de e-commerce de alto crecimiento.',
        S['body']))

    story.append(Paragraph('Equipo Fundador', S['h2']))

    founders_data = [
        ['CARGO', 'NOMBRE', 'PERFIL'],
        ['CEO & Co-Fundador', 'Antonio Colmenares', 'Estudios en IE University. Emprendedor serial. Ex Davos Financial Group, Ex Inbox Attack.'],
        ['CMO & Co-Fundador', 'José Loreto Arismendi', 'Chief Marketing Officer. Apellido 100% venezolano. Estratega digital.'],
        ['COO & Managing Member', 'Vincenzo Passariello', 'Chief Operating Officer. Responsable de operaciones y cadena de suministro.'],
    ]
    story.append(dark_table(founders_data,
                            [3.5*cm, 4*cm, W-7.5*cm]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '⚡ DATO CLAVE: El equipo fundador tiene nombres y apellidos de origen venezolano/latinoamericano '
        '(Colmenares, Arismendi, Passariello). Esto no es casualidad — BFS fue construida por '
        'latinoamericanos desde el día uno. Esto da una ventaja cultural y de red para entrar '
        'al mercado venezolano que ningún competidor americano tiene.',
        S['highlight']))

    story.append(Paragraph('Línea de Productos Completa', S['h2']))

    products_data = [
        ['PRODUCTO', 'INGREDIENTE PRINCIPAL', 'PRECIO RETAIL', 'USO SUGERIDO'],
        ['Turkesterone 500mg', 'Turkesterona 95% pureza + beta-ciclodextrina', '$38.96–$64.99', 'Músculo natural sin hormonas'],
        ['Turkesterone & Tongkat Ali 1000mg', 'Turkesterona + Tongkat Ali 200:1', '$38.96–$64.99', 'Testosterona + masa muscular'],
        ['Cistanche Tubulosa + Tongkat Ali', 'Cistanche tubulosa + Tongkat Ali', '$45–$65', 'Energía + libido + longevidad'],
        ['NMN (Nicotinamide Mononucleotide)', 'NMN alta pureza', '$45–$70', 'Anti-envejecimiento + NAD+'],
        ['Akkermansia Muciniphila', 'Akkermansia muciniphila', '$50–$80', 'Microbioma + salud intestinal'],
        ['Ultimate Black Scout Bundle', 'Stack completo multi-producto', '$167.02 (desc.)', 'Pack de transformación total'],
    ]
    story.append(dark_table(products_data,
                            [4.5*cm, 4.5*cm, 2.5*cm, W-11.5*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Diferenciadores de Calidad', S['h2']))

    diff_items = [
        '✓  Fabricación en instalación registrada FDA (EE.UU.)',
        '✓  Testeo de terceros ANTES y DESPUÉS del encapsulado',
        '✓  Certificación GMP (Good Manufacturing Practices)',
        '✓  Turkesterona con beta-ciclodextrina: máxima biodisponibilidad (único en mercado)',
        '✓  95%+ pureza en extractos (vs. 40-60% de competidores)',
        '✓  Disponible en Amazon, Faire (mayorista), sitio propio y en EAU (Noon.com)',
        '✓  Invitado por la Natural Products Association al Capitolio de EE.UU.',
        '✓  Reuniones con Senadores Marco Rubio, Rick Scott y Congresista María Elvira Salazar',
    ]
    for item in diff_items:
        story.append(Paragraph(item, S['bullet']))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Posicionamiento de Marca', S['h2']))
    story.append(Paragraph(
        'BFS se posiciona como la marca de suplementos naturales más pura y poderosa del mercado. '
        'Su filosofía gira alrededor de la fortaleza física, mental y emocional. El marketing '
        'es aspiracional y masculino, con fuerte presencia en Instagram y comunidades fitness. '
        'Precio: premium mid-range (más económico que marcas ultra-premium pero mejor calidad '
        'que marcas masivas). TrustScore en Trustpilot: 3.8/5 con 182 reseñas.',
        S['body']))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 03 — MACROECONOMÍA VENEZUELA
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('03  |  CONTEXTO MACROECONÓMICO DE VENEZUELA 2025–2026', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('Indicadores Macroeconómicos Clave', S['h2']))

    macro_data = [
        ['INDICADOR', 'DATO', 'FUENTE / NOTA'],
        ['Población total', '~31 millones (2026)', 'Worldometer / Geodatos'],
        ['Crecimiento PIB 2025', '+8.66% anual', 'BCV (Banco Central Venezuela)'],
        ['Proyección PIB 2026', '+10–15%', 'Ecoanalítica / Economistas independientes'],
        ['CEPAL: Liderazgo LATAM', '#1 crecimiento AL 2025 (6.5%)', 'CEPAL 2026'],
        ['Inflación en bolívares', '~400–617% anual', 'Estimaciones independientes'],
        ['Inflación en dólares', '35–66% según categoría', 'Encuestas consumo 2025'],
        ['Salario mínimo', '~$0.50–$5/mes (formal)', 'Infobae / Bloomberg Línea'],
        ['Ingreso medio real', '$256/mes promedio', 'Análisis independent. 2026'],
        ['Consumo hogares 2025', '$18.32 B total', 'Atenas Consultores 2026'],
        ['Motor del crecimiento', 'Petróleo + remesas + servicios', 'UNDP / BCV'],
    ]
    story.append(dark_table(macro_data, [4.5*cm, 4*cm, W-8.5*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('La Paradoja Venezolana: Dualidad del Mercado', S['h2']))
    story.append(Paragraph(
        'Venezuela opera con una economía DUAL que crea oportunidades específicas para productos premium:',
        S['body']))

    paradox_data = [
        ['SEGMENTO', '% POBLACIÓN', 'INGRESO MENSUAL', 'RELEVANCIA PARA BFS'],
        ['Clase Alta / Empresarios', '~5%', '>$2,000/mes', 'Alta — compradores ideales'],
        ['Clase Media-Alta (diaspora + remesas)', '~24%', '$500–$2,000/mes', 'Muy Alta — core target'],
        ['Clase Media', '~5%', '$230–$500/mes', 'Media — compradores ocasionales'],
        ['Clase Popular', '~66%', '<$230/mes', 'Baja — fuera del target'],
    ]
    story.append(dark_table(paradox_data, [3.5*cm, 2.8*cm, 3*cm, W-9.3*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '→ El mercado objetivo real de BFS en Venezuela son los ~8–9 millones de personas '
        'en los segmentos medio-alto y alto, más los beneficiarios de remesas del exterior '
        '(principalmente de EE.UU., donde reside la mayor diáspora venezolana del mundo).',
        S['highlight']))

    story.append(Paragraph('Crecimiento del E-Commerce en Venezuela', S['h2']))

    ecom_stats = [
        ['MÉTRICA DIGITAL', 'DATO 2025–2026'],
        ['Crecimiento e-commerce 2025', '+125% (Cavecom-e)'],
        ['Usuarios activos en redes sociales', '92% de internautas'],
        ['Acceso a internet desde móvil', '80% de usuarios'],
        ['Canal de ventas #1 B2C', 'Instagram'],
        ['Crecimiento fibra óptica 2025', '+343% — expansión al interior'],
        ['Plataformas clave', 'Instagram, TikTok, Facebook, MercadoLibre'],
        ['Pago preferido', 'USD en efectivo / Binance / Zelle / Pago Móvil'],
    ]
    story.append(dark_table(ecom_stats, [6*cm, W-6*cm]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 04 — PERFIL DEL CONSUMIDOR
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('04  |  PERFIL DEL CONSUMIDOR VENEZOLANO 2026', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('El Consumidor Target de Black Forest en Venezuela', S['h2']))
    story.append(Paragraph(
        'El consumidor ideal de BFS en Venezuela es un perfil muy específico pero más numeroso '
        'de lo que parece: joven, urbano, conectado digitalmente, con ingresos en dólares '
        '(ya sea por empleo formal, negocio propio o remesas) y con una cultura fitness activa.',
        S['body']))

    story.append(Paragraph('Buyer Persona Principal: "El Fit Venezolano"', S['h2']))

    persona_data = [
        ['DIMENSIÓN', 'DESCRIPCIÓN'],
        ['Edad', '22–40 años'],
        ['Género', 'Primario: masculino. Secundario: femenino (creciente)'],
        ['Ubicación', 'Caracas, Maracaibo, Valencia, Barquisimeto, Maracay'],
        ['Ingresos', '$500–$3,000/mes (propio negocio, empresa privada, remesas, freelance)'],
        ['Educación', 'Universitaria o técnica superior'],
        ['Redes sociales', 'Instagram diario, TikTok, YouTube fitness, WhatsApp'],
        ['Actividad fitness', 'Asiste a gimnasio 3–5 días/semana. Paga $30–$100+/mes'],
        ['Ya compra suplementos', 'Sí: proteínas (Optimum, Dymatize), creatina, pre-entrenos'],
        ['Gasto mensual suplementos', '$30–$80/mes actualmente (productos genéricos)'],
        ['Pain point actual', 'No accede a marcas premium/naturales/exóticas localmente'],
        ['Aspiración', 'Looks, rendimiento, estatus. El suplemento es también un "lujo asequible"'],
        ['Influencia de compra', 'Influencers fitness IG/TikTok, recomendaciones de gym, coaches'],
        ['Método de pago', 'USD efectivo / Zelle / Binance / transferencia bancaria USD'],
    ]
    story.append(dark_table(persona_data, [4.5*cm, W-4.5*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Comportamiento de Compra Clave 2026', S['h2']))
    behavior = [
        '→ Compra por impulso en Instagram (stories + posts con link a WhatsApp)',
        '→ Alta confianza en recomendaciones de influencers fitness locales',
        '→ Sensible al precio pero dispuesto a pagar más por calidad/exclusividad percibida',
        '→ Prefiere pago en USD — desconfía del bolívar para transacciones grandes',
        '→ Compra frecuente de 1–2 meses (ciclos de suplementación)',
        '→ Recurre a Instagram DM o WhatsApp para preguntar antes de comprar',
        '→ Valora velocidad de entrega (24–48h en grandes ciudades)',
        '→ Comparte resultados en redes: efecto de marketing viral orgánico',
        '→ La cultura fitness en Venezuela ve el ejercicio como mejora estética y de estatus social',
    ]
    for b in behavior:
        story.append(Paragraph(b, S['bullet']))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 05 — MERCADO FITNESS & SUPLEMENTOS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('05  |  MERCADO FITNESS & SUPLEMENTOS EN VENEZUELA', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('El Sector Fitness en Venezuela: Datos Reales', S['h2']))
    story.append(Paragraph(
        'El mercado fitness venezolano está en plena expansión. La industria del fitness se ha '
        'convertido en uno de los motores de empleo y desarrollo en el país (Promar, 2025). '
        'El porcentaje de venezolanos que asiste al gimnasio ha aumentado significativamente en '
        'los últimos 5 años.',
        S['body']))

    fitness_data = [
        ['INDICADOR FITNESS', 'DATO', 'IMPLICACIÓN'],
        ['Gyms activos en Caracas', '100+ establecimientos identificados', 'Alta densidad de target'],
        ['Precio mensualidad gym Caracas', '$15 – $220/mes', 'Segmentación por nivel'],
        ['Powerhouse Gym', 'Presente en Caracas', 'Cadena premium internacional'],
        ["Gold's Gym Venezuela", 'Activo en redes (@goldsgymve)', 'Mercado premium existe'],
        ['Pase diario gym', '$5 – $20 por sesión', 'Cultura casual fitness'],
        ['Tendencias líderes', 'Yoga, Pilates, danza, bodybuilding, CrossFit', 'Diversidad de target'],
        ['Motivación cultural', 'Estético/hedonístico + salud preventiva', 'BFS: look + rendimiento'],
        ['Influencers fitness VE', '20+ con >100K seguidores (Favikon 2025)', 'Canal de distribución'],
    ]
    story.append(dark_table(fitness_data, [5.5*cm, 4*cm, W-9.5*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Mercado de Suplementos: Tamaño y Actores', S['h2']))
    story.append(Paragraph(
        'El mercado LATAM de suplementos nutricionales alcanzará $136.52B para 2035 '
        '(Nova One Advisor). En 2025, las ventas de sports nutrition en LATAM eran de $2.1B, '
        'con un CAGR proyectado del 8.6% hasta $4.8B en 2035. Venezuela, aunque no reporta '
        'cifras independientes, comparte la tendencia regional.',
        S['body']))

    market_size = [
        ['MERCADO', 'TAMAÑO 2025', 'CAGR', 'PROYECCIÓN 2035'],
        ['LATAM Sports Nutrition', '$2.1B', '~8.6%', '$4.8B'],
        ['South America Fitness Clubs', '$5.14B', '10.18%', '$9.2B (2031)'],
        ['Colombia Suplementos', '$206.99M', '7.2%', 'líder regional'],
        ['Perú Suplementos', '$190.71M', '7.6%', 'crecimiento más rápido'],
        ['LATAM Nutricionales total', '$82.17B (2030 est.)', 'alta', '$136.52B (2035)'],
        ['Venezuela (estimado)', '$30–80M', '>10%', 'Mercado emergente/virgen'],
    ]
    story.append(dark_table(market_size, [4.5*cm, 3*cm, 2*cm, W-9.5*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Canales de Distribución Actuales en Venezuela', S['h2']))
    channels = [
        '→ Tiendas online especializadas: SuplemFit, SuplementosVenezuela.com, RutaFit, FUSFIT',
        '→ MercadoLibre Venezuela: +6,500 listados de suplementos deportivos',
        '→ Farmacias: Farmatodo ofrece proteína whey online',
        '→ Instagram: canal #1 para ventas directas D2C (Direct to Consumer)',
        '→ WhatsApp Business: catálogos y pedidos informales',
        '→ Gyms: reventa en mostrador (marcas de contrabando y distribuidas)',
        '→ Casilleros/courier: compra personal desde EE.UU. (Aeropost, Tupaquetico, etc.)',
    ]
    for c in channels:
        story.append(Paragraph(c, S['bullet']))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 06 — COMPETENCIA
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('06  |  ANÁLISIS DE LA COMPETENCIA', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('Mapa Competitivo — Suplementos en Venezuela', S['h2']))

    comp_data = [
        ['COMPETIDOR', 'ORIGEN', 'PRODUCTOS', 'PRECIO APROX.', 'DEBILIDAD vs BFS'],
        ['Optimum Nutrition', 'EE.UU.', 'Whey, creatina, vitaminas', '$30–$60', 'No tiene extractos naturales premium (Turkesterona, NMN)'],
        ['Dymatize', 'EE.UU.', 'Proteínas, aminoácidos', '$25–$55', 'Enfoque solo en proteínas. Sin nicho natural/longevidad'],
        ['Muscletech', 'EE.UU./Canadá', 'Pre-entrenos, proteína', '$25–$60', 'Marca "old school". Sin ingredientes cutting-edge'],
        ['Nutrex Research', 'EE.UU.', 'Pre-entrenos, quemadores', '$30–$60', 'Sin stack de extractos naturales. Química sintética'],
        ['Herbacorp (local)', 'Venezuela', 'Herbal/natural básico', '$10–$25', 'Calidad inferior. Sin GMP ni 3rd party testing'],
        ['Nutrilite/Amway', 'EE.UU.', 'Vitaminas, básicos', '$25–$80', 'Modelo MLM. Sin productos fitness premium'],
        ['Marca gris (importación)', 'Varios', 'Mixto', 'Variable', 'Sin garantía de autenticidad ni servicio'],
        ['BLACK FOREST (BFS)', 'EE.UU./Miami', 'Extractos premium naturales', '$38–$80', '— ÚNICA con Turkesterona 95% + NMN + Akkermansia —'],
    ]
    story.append(dark_table(comp_data, [3.5*cm, 2*cm, 3*cm, 2*cm, W-10.5*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '🏆 VENTAJA COMPETITIVA DE BFS: Ningún competidor en Venezuela ofrece actualmente '
        'Turkesterona 95%, Akkermansia Muciniphila ni NMN de alta pureza con certificación GMP '
        'y testeo independiente. BFS puede ser el PRIMER MOVEDOR en este nicho — la ventaja '
        'del primero que llega es enorme en mercados emergentes.',
        S['highlight']))

    story.append(Paragraph('Mapa de Posicionamiento', S['h2']))
    pos_text = (
        'En el eje precio vs. naturalidad/pureza, BFS ocupa el cuadrante IDEAL: '
        'precio accessible-premium (no el más caro) con la mayor pureza y naturalidad del mercado. '
        'Los competidores o son cheap+bajo calidad (marcas locales) o expensive+sintético '
        '(farmacéuticas) o premium+convencional (ON, Dymatize). BFS es la única opción '
        'premium+natural+certificada+americana disponible.'
    )
    story.append(Paragraph(pos_text, S['body']))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 07 — FODA
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('07  |  ANÁLISIS FODA ESTRATÉGICO', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    foda_data = [
        [
            Paragraph('<font color="#00FF88"><b>FORTALEZAS</b></font>', S['h3']),
            Paragraph('<font color="#FFD700"><b>OPORTUNIDADES</b></font>', S['h3']),
        ],
        [
            Paragraph(
                '• Productos únicos en VE: Turkesterona 95%, NMN, Akkermansia\n'
                '• Fabricación FDA + GMP + 3rd party tested\n'
                '• Fundadores latinoamericanos en Miami\n'
                '• Proximidad logística Miami → Venezuela\n'
                '• Marca con presencia en Amazon + Faire (wholesale)\n'
                '• Representación política en NPA / Congreso USA\n'
                '• Precio competitivo vs. calidad superior\n'
                '• Disponible en EAU: presencia global emergente',
                S['body']),
            Paragraph(
                '• Mercado virgen: nadie vende extractos premium naturales en VE\n'
                '• E-commerce venezolano creció 125% en 2025\n'
                '• 92% usuarios activos en RRSS — canal de ventas directo\n'
                '• PIB venezolano +8-15%: más poder adquisitivo\n'
                '• Fitness cultura en alza — más venezolanos en gyms\n'
                '• Diáspora venezolana en Miami como canal de recomendación\n'
                '• Nicho anti-envejecimiento y biohacking emergente en VE\n'
                '• Ausencia de regulación específica para extractos naturales',
            ),
        ],
        [
            Paragraph('<font color="#FF4444"><b>DEBILIDADES</b></font>', S['h3']),
            Paragraph('<font color="#4488FF"><b>AMENAZAS</b></font>', S['h3']),
        ],
        [
            Paragraph(
                '• Marca desconocida en Venezuela actualmente\n'
                '• Sin distribuidor local establecido\n'
                '• Historial de problemas con envíos y atención al cliente\n'
                '• TrustScore 3.8/5 (mejorable)\n'
                '• Algunos productos en backorder frecuente\n'
                '• Sin material de marketing en español',
                S['body']),
            Paragraph(
                '• Inestabilidad política/económica venezolana\n'
                '• Cambios repentinos en regulación aduanera (reforma 2025)\n'
                '• Dificultad en repatriación de ganancias (divisas)\n'
                '• Competidores que copian productos similares\n'
                '• Inflación en dólares erosiona poder adquisitivo real\n'
                '• Restricciones de Meta/Facebook a anuncios pagados en VE',
            ),
        ],
    ]
    foda_tbl = Table(foda_data, colWidths=[W/2-2, W/2-2])
    foda_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), HexColor('#001A0D')),
        ('BACKGROUND', (1,0), (1,0), HexColor('#1A1A00')),
        ('BACKGROUND', (0,2), (0,2), HexColor('#1A0000')),
        ('BACKGROUND', (1,2), (1,2), HexColor('#000A1A')),
        ('BACKGROUND', (0,1), (0,1), CARD_BG),
        ('BACKGROUND', (1,1), (1,1), CARD_BG),
        ('BACKGROUND', (0,3), (0,3), CARD_BG),
        ('BACKGROUND', (1,3), (1,3), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, CARD_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(foda_tbl)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 08 — REGULATORIO & LOGÍSTICA
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('08  |  MARCO REGULATORIO & LOGÍSTICO', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('Regulación de Importación en Venezuela (2025–2026)', S['h2']))
    story.append(Paragraph(
        'El marco regulatorio venezolano fue reformado en junio de 2025 (Decreto 5.147). '
        'Para suplementos deportivos naturales (cápsulas/extractos) aplican requisitos específicos '
        'que son manejables con la asesoría correcta.',
        S['body']))

    reg_data = [
        ['REQUISITO', 'DETALLE', 'CÓMO CUMPLIRLO'],
        ['Clasificación arancelaria', 'HS Code 2106.90 (prep. alimenticias)', 'Agente aduanal especializado'],
        ['Registro como importador', 'RIF + registro en SENIAT', 'Socio local venezolano'],
        ['Permiso sanitario', 'SENCAMER / Ministerio Salud', 'COA + specs del producto'],
        ['COA (Certificado de Análisis)', 'Obligatorio para suplementos', 'BFS ya lo provee (3rd party tested)'],
        ['Certificado de Origen', 'Forma A o equivalente', 'Tramitar con proveedor USA'],
        ['Factura comercial', 'En USD, detallada', 'Estándar exportación EE.UU.'],
        ['IVA Venezuela', '16% sobre valor CIF', 'Incluir en pricing final'],
        ['Arancel importación', 'Variable según HS code (5–20%)', 'Consultar con agente aduanal'],
        ['COMEX (si aplica RL-9)', 'Permiso previo para +200 códigos', 'Verificar con agente si aplica'],
    ]
    story.append(dark_table(reg_data, [4.5*cm, 4*cm, W-8.5*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Estrategia Logística Recomendada', S['h2']))

    story.append(Paragraph('OPCIÓN A (Recomendada para inicio): Modelo Casillero/Courier Personal', S['h3']))
    casillero_steps = [
        '1. Cliente hace pedido vía Instagram DM o WhatsApp',
        '2. Paga en USD (Zelle, Binance, efectivo, transferencia)',
        '3. Proveedor (tú) ordena en BFS.com a dirección de casillero en Miami',
        '4. Empresa de casillero (Tupaquetico, Aeropost, Alaslatinas, etc.) recibe el paquete',
        '5. Envío aéreo Miami → Venezuela: 5–15 días hábiles, $8–15/lb aprox.',
        '6. Cliente retira o recibe en domicilio',
        '★ VENTAJA: Mínima inversión inicial. Sin inventario. Sin aduana compleja. Comienzas en 1 semana.',
    ]
    for s_text in casillero_steps:
        story.append(Paragraph(s_text, S['bullet']))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph('OPCIÓN B (Escala): Importación Directa en Volumen (6-12 meses)', S['h3']))
    directo_steps = [
        '1. Constitución de empresa importadora venezolana (sociedad anónima)',
        '2. Registro en SENIAT como importador',
        '3. Obtención de permisos sanitarios SENCAMER',
        '4. Compra al por mayor via Faire o directamente a BFS (wholesale)',
        '5. Envío marítimo Miami → Venezuela: FCL/LCL, 2–4 semanas',
        '6. Despacho en aduana con agente profesional',
        '7. Distribución local desde almacén propio o 3PL',
        '★ VENTAJA: Márgenes 60–80%. Control de inventario. Escalabilidad real.',
    ]
    for s_text in directo_steps:
        story.append(Paragraph(s_text, S['bullet']))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph('Empresas de Courier Verificadas Miami → Venezuela', S['h2']))
    courier_data = [
        ['EMPRESA', 'TIEMPO ESTIMADO', 'PRECIO APROX./LB', 'NOTA'],
        ['Tupaquetico', '7–15 días', '$7–12/lb', 'Especialista Venezuela-USA'],
        ['Aeropost', '5–10 días', '$8–15/lb', 'Red amplia en Venezuela'],
        ['Alaslatinas / Alasbox', '7–14 días', '$6–10/lb', 'Tarifa especial Venezuela'],
        ['Qwintry', '10–20 días', '$5–9/lb', 'Económico para volumen'],
        ['US Global Logistic', '7–15 días', '$8–14/lb', 'Especialistas importación VE'],
    ]
    story.append(dark_table(courier_data, [3.5*cm, 2.5*cm, 2.5*cm, W-8.5*cm]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 09 — ESTRATEGIA DE ENTRADA
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('09  |  ESTRATEGIA DE ENTRADA AL MERCADO', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('Propuesta de Valor para Venezuela', S['h2']))
    story.append(Paragraph(
        '"Los suplementos naturales más puros del mundo, directo desde Miami, '
        'certificados y probados, para el venezolano que entrena en serio."',
        S['quote']))

    story.append(Paragraph('Estrategia de Pricing para Venezuela', S['h2']))
    story.append(Paragraph(
        'El precio debe reflejar la exclusividad y calidad premium, mientras sigue '
        'siendo accesible para el target. Propuesta basada en costo real + margen apropiado:',
        S['body']))

    pricing_data = [
        ['PRODUCTO', 'COSTO BFS (wholesale)', 'COSTO ENVÍO (+15%)', 'PRECIO VE SUGERIDO', 'MARGEN BRUTO'],
        ['Turkesterone & Tongkat Ali', '~$22–28', '+$4–6', '$65–75 USD', '~50–60%'],
        ['Cistanche + Tongkat Ali', '~$25–32', '+$4–6', '$70–80 USD', '~50–60%'],
        ['NMN', '~$28–38', '+$5–7', '$75–90 USD', '~50–55%'],
        ['Akkermansia', '~$32–45', '+$5–8', '$85–100 USD', '~50–55%'],
        ['Ultimate Bundle (Stack)', '~$90–110', '+$12–16', '$200–230 USD', '~55–60%'],
    ]
    story.append(dark_table(pricing_data, [4*cm, 3*cm, 2.5*cm, 3*cm, W-12.5*cm]))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        '💰 Con un margen bruto del 50–60% y un pedido promedio de $70–80 USD, '
        'necesitas vender solo 4–5 unidades/mes para cubrir gastos operativos mínimos. '
        'A 50 unidades/mes ya generas un ingreso mensual de $1,500–2,000 USD libre.',
        S['highlight']))

    story.append(Paragraph('Modelo de Negocio Recomendado: D2C + Distribución Selectiva', S['h2']))

    model_data = [
        ['CANAL', 'MODELO', 'INVERSIÓN INICIAL', 'VENTAJA'],
        ['Instagram + WhatsApp', 'D2C directo', '$0 (orgánico)', 'Cero overhead, margen máximo'],
        ['Tienda Shopify/WooCommerce', 'E-commerce propio', '$200–500/año', 'Escala, credibilidad, automatización'],
        ['Distribución a gyms premium', 'B2B reventa', '$500–1,000 stock', 'Volumen, visibilidad en punto de uso'],
        ['Coaches/entrenadores', 'Afiliados 10–15%', '$0', 'Red de confianza, ventas recurrentes'],
        ['Influencers fitness locales', 'Barter + comisión', 'Producto ($30–80)', 'Alcance masivo sin costo fijo'],
        ['MercadoLibre Venezuela', 'Marketplace', '$0 + comisión ~12%', 'Tráfico existente, búsquedas activas'],
    ]
    story.append(dark_table(model_data, [3.5*cm, 2.8*cm, 2.5*cm, W-8.8*cm]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 10 — MARKETING DIGITAL
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('10  |  PLAN DE MARKETING DIGITAL', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('Ecosistema Digital Venezuela: La Oportunidad', S['h2']))
    story.append(Paragraph(
        'Venezuela tiene 92% de sus internautas activos en redes sociales. Instagram es el canal '
        '#1 de ventas para e-commerce. TikTok crece exponencialmente. El 80% compra desde móvil. '
        'Esto significa que con una buena cuenta de Instagram y WhatsApp Business, '
        'puedes construir un negocio de 6 cifras en USD sin tienda física.',
        S['body']))

    story.append(Paragraph('Estrategia Instagram (Canal Principal)', S['h2']))
    ig_strategy = [
        'CONTENIDO (70%):',
        '• Videos de transformación antes/después usando productos BFS',
        '• Reels educativos: "¿Qué es la Turkesterona y por qué es mejor que los esteroides?"',
        '• Stories diarias: testimoniales, unboxings, preguntas y respuestas',
        '• Posts de comparación: "BFS vs. la competencia" con datos de pureza',
        '• Educación: beneficios del NMN para anti-envejecimiento, Akkermansia para salud intestinal',
        '',
        'CONVERSIÓN (20%):',
        '• Stories con link directo a WhatsApp ("Escríbeme para pedir")',
        '• Posts de precio con urgencia ("Solo 5 unidades disponibles esta semana")',
        '• Ofertas exclusivas para seguidores activos',
        '',
        'COMUNIDAD (10%):',
        '• Repostear resultados de clientes (UGC)',
        '• Responder 100% de los comentarios y DMs',
        '• Crear grupo privado de WhatsApp para clientes: "Black Forest VE Elite"',
    ]
    for item in ig_strategy:
        if item.endswith(':') or item == '':
            if item:
                story.append(Paragraph(item, S['h3']))
        else:
            story.append(Paragraph(item, S['bullet']))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph('Top Influencers Fitness Venezuela (Target para Colaboración)', S['h2']))
    influencer_data = [
        ['INFLUENCER', 'PLATAFORMA', 'PERFIL', 'ESTRATEGIA DE COLABORACIÓN'],
        ['Jesús Guerrero (Chuyst)', 'TikTok + Instagram', 'Natural Bodybuilding Pro, humor y rutinas', 'Gifting + revenue share 15%'],
        ['Marly Valera', 'Instagram', 'CEO Marfit Moda, fitness lifestyle femenino', 'Gifting femenino (NMN/Akkermansia)'],
        ['Laura Fuentes', 'Instagram', 'Farmacéutica + entrenadora + Corpus Gym', 'Credibilidad científica + stack NMN'],
        ['Fitness influencers locales 50K+', 'Instagram/TikTok', 'Nutrición + entrenamientos', 'Kit de productos + 10–15% comisión'],
        ['Coaches/entrenadores gym', 'WhatsApp + IG', 'Red de entrenadores con clientes', 'Descuento mayorista + comisión por venta'],
    ]
    story.append(dark_table(influencer_data, [3.5*cm, 2.5*cm, 3.5*cm, W-9.5*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('TikTok Strategy Venezuela', S['h2']))
    tiktok_tips = [
        '→ Contenido viral: "Probé Turkesterona 30 días — esto pasó" (formato challenge)',
        '→ Duetos con influencers fitness venezolanos',
        '→ Educación rápida: "3 suplementos que cambian tu cuerpo naturalmente"',
        '→ Humor fitness: capitalizar el estilo de Chuyst (bodybuilding + humor)',
        '→ Tendencias locales: mezclar cultura fitness VE con productos BFS',
        '→ Links en bio a WhatsApp y tienda online',
    ]
    for t in tiktok_tips:
        story.append(Paragraph(t, S['bullet']))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph('Publicidad Pagada (Meta/Facebook Ads)', S['h2']))
    story.append(Paragraph(
        'Atención: Meta tiene restricciones para ads en Venezuela pero es manejable. '
        'Estrategia: segmentar por venezolanos EN Venezuela con poder adquisitivo + '
        'venezolanos en Miami/USA que quieran enviar a familiares. '
        'Budget inicial recomendado: $200–400/mes para pruebas de audiencia.',
        S['body']))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 11 — PROYECCIONES FINANCIERAS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('11  |  PROYECCIONES FINANCIERAS', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('Inversión Inicial Necesaria', S['h2']))
    inv_data = [
        ['RUBRO', 'COSTO ESTIMADO', 'NOTAS'],
        ['Stock inicial (30–50 unidades)', '$1,200–2,500', 'Wholesale via Faire o BFS directo'],
        ['Costo envío stock inicial a VE', '$200–400', 'Courier aéreo Miami → Caracas'],
        ['Tienda online (Shopify/WooCommerce)', '$200–500/año', 'Opcional al inicio'],
        ['Marketing digital inicial', '$300–600', 'Gifting influencers + ads básico'],
        ['WhatsApp Business + Instagram', '$0', 'Gratis — núcleo del negocio'],
        ['Registro empresa (si aplica)', '$300–800', 'Solo si se formaliza desde VE'],
        ['Total inversión mínima viable', '$2,000–4,800', 'Para arrancar profesionalmente'],
    ]
    story.append(dark_table(inv_data, [5*cm, 3*cm, W-8*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Proyección de Ventas — 3 Escenarios', S['h2']))

    proj_data = [
        ['MÉTRICA', 'AÑO 1 (CONSERVADOR)', 'AÑO 1 (REALISTA)', 'AÑO 2 (OPTIMISTA)'],
        ['Unidades vendidas/mes', '20–30', '50–80', '150–250'],
        ['Ticket promedio', '$70 USD', '$80 USD', '$85 USD'],
        ['Ingresos mensuales', '$1,400–2,100', '$4,000–6,400', '$12,750–21,250'],
        ['Ingresos anuales', '$16,800–25,200', '$48,000–76,800', '$153,000–255,000'],
        ['Costo productos (40%)', '$6,720–10,080', '$19,200–30,720', '$61,200–102,000'],
        ['Costo envíos (10%)', '$1,680–2,520', '$4,800–7,680', '$15,300–25,500'],
        ['Ganancia bruta estimada', '$8,400–12,600', '$24,000–38,400', '$76,500–127,500'],
        ['Margen bruto', '~50%', '~50%', '~50%'],
        ['Clientes únicos acumulados', '240–360', '600–960', '1,800–3,000'],
    ]
    story.append(dark_table(proj_data, [4.5*cm, 3.5*cm, 3.5*cm, W-11.5*cm]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '📊 PUNTO DE EQUILIBRIO: Con una inversión inicial de $3,000–5,000, '
        'el break-even se alcanza vendiendo solo 40–70 unidades en los primeros 2–3 meses. '
        'Es uno de los negocios de menor riesgo relativo por su modelo D2C sin inventario físico forzoso.',
        S['highlight']))

    story.append(Paragraph('Flujo de Caja Estimado Año 1 (Escenario Realista)', S['h2']))
    cashflow_data = [
        ['MES', 'INGRESOS', 'COSTOS', 'GANANCIA NETA', 'ACUMULADO'],
        ['Mes 1–2 (lanzamiento)', '$2,000', '$2,800', '-$800', '-$800'],
        ['Mes 3–4 (tracción)', '$4,000', '$2,200', '+$1,800', '+$1,000'],
        ['Mes 5–6 (crecimiento)', '$6,000', '$3,000', '+$3,000', '+$4,000'],
        ['Mes 7–9 (escala)', '$8,000', '$4,000', '+$4,000', '+$12,000'],
        ['Mes 10–12 (madurez)', '$12,000', '$5,500', '+$6,500', '+$31,500'],
        ['TOTAL AÑO 1', '~$60,000', '~$30,000', '~$30,000', '$30,000 neto'],
    ]
    story.append(dark_table(cashflow_data, [3.5*cm, 2.5*cm, 2.5*cm, 3*cm, W-11.5*cm]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 12 — HOJA DE RUTA
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('12  |  HOJA DE RUTA 2026–2028', ACCENT_GOLD))
    story.append(Spacer(1, 0.3*cm))

    phases = [
        ('FASE 1: PREPARACIÓN', '0–30 días', ACCENT_GREEN, [
            'Contactar a Black Forest Supplements (blackforestsupplements.com/contact) para propuesta de distribución',
            'Mencionar conexión latinoamericana con el equipo fundador (Colmenares, Arismendi)',
            'Abrir cuenta de Faire para acceder a precios de mayoreo',
            'Crear cuenta Instagram profesional enfocada en Venezuela',
            'Crear WhatsApp Business con catálogo inicial',
            'Comprar 20–30 unidades de los 2 productos estrella (Turkesterona & Tongkat Ali + NMN)',
            'Identificar y contactar 3–5 influencers fitness venezolanos para gifting',
            'Diseñar materiales visuales en español para IG (Canva o freelancer)',
        ]),
        ('FASE 2: LANZAMIENTO', '1–3 meses', ACCENT_GOLD, [
            'Lanzar perfil de Instagram con 10–15 posts iniciales de contenido educativo',
            'Activar colaboraciones con influencers: gifting + stories de review',
            'Primera ronda de ventas via DM + WhatsApp',
            'Probar modelo casillero/courier para los primeros pedidos',
            'Recopilar testimoniales y resultados de primeros clientes',
            'Lanzar tienda online básica (Shopify/Woocommerce)',
            'Activar anuncios Meta básicos ($200/mes) segmentando Caracas, Valencia, Maracaibo',
            'Establecer grupo WhatsApp "Black Forest VE — Comunidad Fitness" para clientes',
        ]),
        ('FASE 3: CRECIMIENTO', '3–9 meses', BLUE_ACCENT, [
            'Escalar a 50–80 unidades/mes mediante publicidad y boca a boca',
            'Ampliar catálogo: agregar Akkermansia + bundles',
            'Iniciar distribución B2B: negociar con 5–10 gyms premium de Caracas',
            'Red de coaches afiliados: 10–20 entrenadores con código de descuento',
            'Crear contenido educativo en TikTok (canal paralelo)',
            'Explorar apertura cuenta bancaria USD en Venezuela para facilitar pagos',
            'Contratar asistente part-time para manejo de pedidos y RRSS',
            'Optimizar logística: evaluar switch de casillero a importación pequeña directa',
        ]),
        ('FASE 4: ESCALA NACIONAL', '9–24 meses', PURPLE, [
            'Constituir empresa importadora formal en Venezuela',
            'Tramitar registro sanitario productos ante autoridades venezolanas',
            'Importación directa en volumen (LCL/FCL) desde Miami',
            'Expansión a Maracaibo, Valencia, Barquisimeto, Maracay',
            'Acuerdo de distribución exclusivo o semi-exclusivo con BFS para VE',
            'Participación en eventos fitness venezolanos (Expo Fitness, competencias bodybuilding)',
            'Revenue objetivo: $150K–250K USD anuales',
            'Team local de 3–5 personas: ventas, logística, marketing',
        ]),
    ]

    for phase_name, timeframe, color, items in phases:
        story.append(Spacer(1, 0.3*cm))
        header_row = [[
            Paragraph(f'<font color="#{color.hexval()[2:]}"><b>{phase_name}</b></font>',
                      S['h2']),
            Paragraph(f'<font color="#606080">{timeframe}</font>', S['h3'])
        ]]
        phase_header = Table(header_row, colWidths=[W*0.7, W*0.3])
        phase_header.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 1.5, color),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(phase_header)
        for item in items:
            story.append(Paragraph(f'  ✓  {item}', S['bullet']))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 13 — RIESGOS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('13  |  RIESGOS & MITIGACIONES', ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))

    risks_data = [
        ['RIESGO', 'PROBABILIDAD', 'IMPACTO', 'MITIGACIÓN'],
        ['Inestabilidad política/económica VE', 'Alta', 'Medio', 'Mantener operación ligera. No invertir en activos fijos. Modelo casillero elimina este riesgo.'],
        ['Restricciones aduaneras nuevas', 'Media', 'Alto', 'Diversificar rutas (courier personal + importación formal). Tener agente aduanal de confianza.'],
        ['BFS no aprueba distribución VE', 'Baja', 'Medio', 'Pueden operarse compras directas al retail. Acercarse con propuesta de valor en español.'],
        ['Inflación dolarizada erosiona demanda', 'Media', 'Medio', 'Ajustar pricing dinámicamente. Mantener segmento alto como core. Bundles con mejor valor percibido.'],
        ['Competidor copia el modelo', 'Media', 'Medio', 'Construir marca y comunidad local fuerte desde el inicio. First mover advantage + lealtad.'],
        ['Problemas de calidad/envío de BFS', 'Media', 'Alto', 'Mantener stock buffer local. Comunicar delays proactivamente. Excelente atención al cliente.'],
        ['Restricciones Meta para ads Venezuela', 'Alta', 'Medio', 'Priorizar orgánico. Usar influencers. Alternativa: ads desde cuenta USA segmentando VE.'],
        ['Fluctuación tipo de cambio', 'Alta', 'Bajo', 'Todo en USD. Diversificar métodos de pago (Zelle/Binance/efectivo).'],
    ]
    story.append(dark_table(risks_data, [4*cm, 2.2*cm, 1.8*cm, W-8*cm]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 14 — CONCLUSIONES & PRÓXIMOS PASOS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('14  |  CONCLUSIONES & PRÓXIMOS PASOS INMEDIATOS', ACCENT_GOLD))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('Veredicto Final del Mercado', S['h2']))
    story.append(Paragraph(
        'Venezuela en 2026 es un mercado imperfecto pero con una oportunidad real y tangible '
        'para Black Forest Supplements. La combinación de crecimiento económico acelerado, '
        'boom del e-commerce, cultura fitness en expansión y ausencia de competidores en el '
        'nicho de extractos naturales premium crea una ventana que no estará disponible '
        'indefinidamente.',
        S['body']))

    story.append(Spacer(1, 0.2*cm))

    conclusions = [
        ('TIMING PERFECTO', ACCENT_GREEN,
         'El mercado está en el punto inflexión: suficientemente maduro para comprar premium pero '
         'sin competidores establecidos en el nicho específico de BFS. Actuar en 2026 es actuar '
         'en el momento exacto.'),
        ('MODELO DE BAJO RIESGO', ACCENT_GOLD,
         'El modelo casillero/D2C digital requiere una inversión inicial de apenas $2,000–5,000 USD '
         'con retorno proyectado en 60–90 días. Es uno de los modelos de mayor ROI posible.'),
        ('VENTAJA CULTURAL ÚNICA', BLUE_ACCENT,
         'Los fundadores de BFS son latinoamericanos en Miami. Eres venezolano queriendo distribuir '
         'una marca venezolana-americana. Esto no es solo un negocio — es una historia que se vende sola.'),
        ('CAMINO A 7 CIFRAS', PURPLE,
         'En 24–36 meses, con ejecución correcta, el negocio puede generar $150K–500K+ anuales '
         'y posicionarte como el distribuidor exclusivo de BFS para Venezuela y potencialmente LATAM.'),
    ]

    for label, color, text in conclusions:
        row = [[
            Paragraph(f'<font color="#{color.hexval()[2:]}"><b>{label}</b></font>', S['h3']),
            Paragraph(text, S['body'])
        ]]
        t = Table(row, colWidths=[3.8*cm, W-3.8*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 1, color),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph('LAS 10 ACCIONES INMEDIATAS (HOY MISMO)', S['h1']))

    actions = [
        ('ACCIÓN #1 — HOY',
         'Ir a blackforestsupplements.com/pages/contact-us y enviar un email profesional en inglés '
         'proponiendo ser el distribuidor exclusivo de Venezuela. Mencionar el origen latinoamericano '
         'compartido y la oportunidad de mercado. Asunto: "Venezuela Distribution Partnership Proposal"'),
        ('ACCIÓN #2 — SEMANA 1',
         'Abrir cuenta en Faire.com y solicitar acceso wholesale a Black Forest Supplements. '
         'URL: faire.com/brand/b_gyq9phh3jj — Evaluar precios mayoristas y condiciones.'),
        ('ACCIÓN #3 — SEMANA 1',
         'Crear Instagram Business: @blackforestvzla o @bfsvenezuela con bio en español, '
         'link a WhatsApp Business. Empezar a seguir a todos los influencers fitness venezolanos.'),
        ('ACCIÓN #4 — SEMANA 1',
         'Crear WhatsApp Business con número venezolano. Configurar respuestas automáticas, '
         'catálogo con fotos y precios de los 3 productos principales de BFS.'),
        ('ACCIÓN #5 — SEMANA 2',
         'Comprar stock inicial: 10 × Turkesterona & Tongkat Ali + 5 × NMN + 5 × Cistanche. '
         'Enviar a casillero en Miami (Tupaquetico o Alaslatinas). Costo: ~$800–1,200 USD.'),
        ('ACCIÓN #6 — SEMANA 2',
         'Enviar DM a 5–10 influencers fitness venezolanos con >50K seguidores. '
         'Propuesta: "Te envío 1 ciclo gratis a cambio de stories honestas de tus resultados". '
         'Inversión: $40–80 por influencer.'),
        ('ACCIÓN #7 — SEMANA 3',
         'Publicar primeros 9 posts en Instagram: mezcla de educación sobre ingredientes, '
         'comparativas de pureza vs. competencia, y la historia de la marca BFS. '
         'Usar Canva para diseño profesional.'),
        ('ACCIÓN #8 — MES 1',
         'Primeras ventas: aceptar Zelle, Binance o USD efectivo. '
         'Documentar TODO para aprender qué convierte mejor. '
         'Objetivo: 10–15 primeros clientes en mes 1.'),
        ('ACCIÓN #9 — MES 2',
         'Con primeros testimoniales reales, lanzar primera campaña de Meta Ads: '
         '$200 presupuesto, segmentando Caracas 25–40 años, intereses fitness/gym/proteínas. '
         'Crear lookalike audience de primeros compradores.'),
        ('ACCIÓN #10 — MES 3',
         'Evaluar resultados, ajustar, escalar lo que funciona. '
         'Si las ventas justifican, abrir conversación formal con BFS para acuerdo de distribución exclusiva. '
         'Target: $5,000/mes en ventas antes de mes 3.'),
    ]

    for i, (action_label, action_text) in enumerate(actions):
        color = ACCENT_GREEN if i % 2 == 0 else ACCENT_GOLD
        row = [[
            Paragraph(f'<font color="#{color.hexval()[2:]}"><b>{action_label}</b></font>', S['h3']),
            Paragraph(action_text, S['body'])
        ]]
        t = Table(row, colWidths=[3.8*cm, W-3.8*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 0.5, color),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width=W, thickness=2, color=ACCENT_GREEN))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '"El mejor momento para plantar un árbol fue hace 20 años. El segundo mejor momento es ahora."',
        S['quote']))
    story.append(Paragraph(
        'Venezuela está creciendo. El fitness está creciendo. Los suplementos premium no tienen '
        'competencia seria. BFS está en Miami con fundadores latinoamericanos. '
        'Todo apunta a que este es el momento. El mercado no espera.',
        S['body']))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # ANEXO — FUENTES
    # ══════════════════════════════════════════════════════════════════════════
    story.append(SectionDivider('ANEXO  |  FUENTES Y REFERENCIAS', TEXT_MUTED))
    story.append(Spacer(1, 0.3*cm))

    sources = [
        ('Black Forest Supplements', [
            'blackforestsupplements.com (sitio oficial)',
            'Trustpilot: trustpilot.com/review/blackforestsupplements.com (182 reseñas)',
            'BBB: bbb.org/us/fl/hialeah/profile/.../the-black-forest-supplements-inc',
            'LinkedIn: Antonio Colmenares CEO, José Loreto Arismendi CMO, Vincenzo Passariello COO',
            'Amazon: amazon.com/Black-Forest-Turkesterone... (ASIN B0CZPKBFB2)',
            'Faire Wholesale: faire.com/brand/b_gyq9phh3jj',
            'ZoomInfo: zoominfo.com/c/black-forest-supplements/1312842074',
        ]),
        ('Mercado Global y LATAM', [
            'Future Market Insights: futuremarketinsights.com — Ventas sports nutrition LATAM',
            'Grand View Research: grandviewresearch.com — LATAM Nutritional Supplements Market',
            'Precedence Research: precedenceresearch.com — Sports Nutrition Market Size 2026–2035',
            'Nova One Advisor: novaoneadvisor.com — LATAM $136.52B por 2035',
            'Mordor Intelligence: mordorintelligence.com — South America Health & Fitness Club Market',
        ]),
        ('Venezuela: Economía y Consumidor', [
            'Atenas Consultores: atenasconsultores.com — Consumo Venezuela 2026',
            'Curadas: curadas.com — Consumidor venezolano 2026 (perfil y estudio)',
            'BCV: bcv.org.ve — PIB Q2 2025 +6.65%',
            'UNDP Venezuela: undp.org — Desempeño macroeconómico Q4 2024',
            'Infobae: infobae.com — Salario mínimo Venezuela 2025',
            'Bloomberg Línea: bloomberglinea.com — Salarios mínimos LATAM 2026',
            'Ecoanalítica (vía El Nacional): elnacional.com — PIB 2026 +15%',
            'El Diario Venezuela: eldiario.com — Gimnasios Caracas precios 2025–2026',
        ]),
        ('Venezuela: Digital y Fitness', [
            'Guayoyo Marketing: guayoyomarketing.com — Estadísticas digitales Venezuela 2026',
            'Favikon: favikon.com — Top 20 Fitness Influencers Venezuela 2025',
            'FMT Studio: fmtstudio.com — E-commerce Venezuela 2026',
            'Agencia Sincere Marketing: agenciasincemarketing.com — Marketing digital VE 2025',
            'Promar: promar.tv — Fitness como motor de empleo Venezuela 2025',
            'Powerhouse Gym Caracas: powerhousegym.com/locations/caracas-venezuela',
        ]),
        ('Venezuela: Regulación e Importación', [
            'SENIAT: declaraciones.seniat.gob.ve — Aranceles de Aduana',
            'SENCAMER: sencamer.gob.ve',
            'Lega Law: lega.law — Reforma Arancel Aduanas junio 2025 (Decreto 5.147)',
            'US Global Logistic: usglogistic.com — Importar Venezuela 2025',
            'Tupaquetico: tupaquetico.com — Envíos EE.UU. → Venezuela',
            'Alaslatinas/Alasbox: alasbox.alaslatinas.com — Tarifa Venezuela',
        ]),
        ('Suplementos Venezuela', [
            'SuplemFit: suplemfit.com — Tienda online suplementos Venezuela',
            'SuplementosVenezuela: suplementosvenezuela.com',
            'RutaFit: rutafit.com',
            'FUSFIT: fusfit.com',
            'MercadoLibre Venezuela: listado.mercadolibre.com.ve/deportes/suplementos-deportivos',
            'Farmatodo: farmatodo.com.ve — Proteína Whey Venezuela',
        ]),
    ]

    for section_title, items in sources:
        story.append(Paragraph(section_title, S['h3']))
        for item in items:
            story.append(Paragraph(f'• {item}', S['bullet']))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width=W, thickness=1, color=CARD_BORDER))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        'Este documento fue preparado con datos de fuentes públicas verificadas al 28 de mayo de 2026. '
        'Las proyecciones financieras son estimaciones basadas en benchmarks del sector y no constituyen '
        'garantía de resultados. Todo uso comercial de este documento es responsabilidad exclusiva del '
        'destinatario.',
        S['footer_txt']))

    # ══════════════════════════════════════════════════════════════════════════
    # BUILD
    # ══════════════════════════════════════════════════════════════════════════
    doc.build(story,
              onFirstPage=on_cover_page,
              onLaterPages=on_page)
    print(f"PDF generado: {output_path}")

if __name__ == '__main__':
    output = '/home/user/prime-/BlackForest_Venezuela_EstudioMercado_2026.pdf'
    build_pdf(output)
