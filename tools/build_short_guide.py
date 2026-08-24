# -*- coding: utf-8 -*-
"""Коротка інструкція на дві сторінки А4: сторінка для механіка, сторінка для адміністратора."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, FrameBreak, NextPageTemplate)

FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DJ',   FD + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DJ-B', FD + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('DJ', normal='DJ', bold='DJ-B')

GREEN  = colors.HexColor('#059669')
DARK   = colors.HexColor('#065f46')
MINT   = colors.HexColor('#ecfdf5')
INK    = colors.HexColor('#111827')
GREY   = colors.HexColor('#6b7280')
LINE   = colors.HexColor('#e5e7eb')
BLUE   = colors.HexColor('#1d4ed8')
BLUE_L = colors.HexColor('#eff6ff')
RED    = colors.HexColor('#b91c1c')
RED_L  = colors.HexColor('#fef2f2')
AMB    = colors.HexColor('#b45309')
AMB_L  = colors.HexColor('#fffbeb')
SLATE  = colors.HexColor('#334155')

def mk(name, **kw):
    d = dict(name=name, fontName='DJ', fontSize=9.4, leading=13.4, textColor=INK, spaceAfter=3.5)
    d.update(kw); return ParagraphStyle(**d)

S = {
 'h':    mk('h',    fontName='DJ-B', fontSize=11.8, leading=15, textColor=DARK,
                    spaceBefore=8, spaceAfter=4.5, keepWithNext=1),
 'p':    mk('p'),
 'li':   mk('li',   leftIndent=9, bulletIndent=1, spaceAfter=2),
 'tiny': mk('tiny', fontSize=8.2, leading=11.4, textColor=GREY),
 'cell': mk('cell', fontSize=8.9, leading=12.4, spaceAfter=0),
 'cellb':mk('cellb',fontName='DJ-B', fontSize=8.9, leading=12.4, spaceAfter=0),
 'num':  mk('num',  fontName='DJ-B', fontSize=9.5, leading=12, textColor=colors.white,
                    alignment=1, spaceAfter=0),
 'stepH':mk('stepH',fontName='DJ-B', fontSize=9.4, leading=12.6, spaceAfter=1),
 'stepP':mk('stepP',fontSize=8.9, leading=12.2, textColor=SLATE, spaceAfter=0),
}
def P(t, s='p'): return Paragraph(t, S[s])
def B(t):        return Paragraph(t, S['li'], bulletText='•')

COL = 82*mm

def callout(title, lines, tint, edge):
    inner = []
    if title:
        inner.append(Paragraph('<font color="%s"><b>%s</b></font>' % (edge.hexval(), title), S['cell']))
        inner.append(Spacer(1, 2))
    for i, l in enumerate(lines):
        inner.append(Paragraph(l, S['cell']))
        if i < len(lines) - 1: inner.append(Spacer(1, 2))
    t = Table([[inner]], colWidths=[COL])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), tint),
        ('LINEBEFORE', (0,0), (-1,-1), 2.2, edge),
        ('BOX',        (0,0), (-1,-1), 0.4, colors.HexColor('#00000018')),
        ('LEFTPADDING',(0,0), (-1,-1), 7), ('RIGHTPADDING',(0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING',(0,0),(-1,-1), 5),
    ]))
    return t

def steps(items, start=1):
    rows = []
    for i, (head, sub) in enumerate(items, start):
        chip = Table([[Paragraph(str(i), S['num'])]], colWidths=[6.2*mm], rowHeights=[6.2*mm])
        chip.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), GREEN), ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
            ('TOPPADDING',(0,0),(-1,-1),1), ('BOTTOMPADDING',(0,0),(-1,-1),0),
            ('ROUNDEDCORNERS',[3,3,3,3]),
        ]))
        body = [Paragraph(head, S['stepH'])]
        if sub: body.append(Paragraph(sub, S['stepP']))
        rows.append([chip, body])
    t = Table(rows, colWidths=[8*mm, COL - 8*mm])
    t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(0,-1),0), ('LEFTPADDING',(1,0),(1,-1),3),
        ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),2.5), ('BOTTOMPADDING',(0,0),(-1,-1),2.5),
    ]))
    return t

def grid(rows, widths, head=True, zebra=True):
    data = [[Paragraph(c, S['cellb'] if (head and r == 0) else S['cell']) for c in row]
            for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths)
    stl = [('VALIGN',(0,0),(-1,-1),'TOP'),
           ('LEFTPADDING',(0,0),(-1,-1),5), ('RIGHTPADDING',(0,0),(-1,-1),5),
           ('TOPPADDING',(0,0),(-1,-1),3.5), ('BOTTOMPADDING',(0,0),(-1,-1),3.5),
           ('LINEBELOW',(0,0),(-1,-2),0.4, LINE)]
    if head:
        stl += [('BACKGROUND',(0,0),(-1,0), MINT), ('LINEBELOW',(0,0),(-1,0),0.8, GREEN)]
    if zebra:
        for i in range(1 if head else 0, len(data)):
            if i % 2 == (1 if head else 0):
                stl.append(('BACKGROUND',(0,i),(-1,i), colors.HexColor('#fafafa')))
    t.setStyle(TableStyle(stl))
    return t

def dots(rows):
    """Плашка стану: кольорова крапка + текст."""
    data = []
    for color, label, text in rows:
        dot = Table([['']], colWidths=[3.4*mm], rowHeights=[3.4*mm])
        dot.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1), color),
                                 ('ROUNDEDCORNERS',[1.7,1.7,1.7,1.7]),
                                 ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
                                 ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
        data.append([dot, Paragraph('<b>%s</b> — %s' % (label, text), S['cell'])])
    t = Table(data, colWidths=[5.5*mm, COL - 5.5*mm])
    t.setStyle(TableStyle([
        ('VALIGN',(0,0),(0,-1),'TOP'), ('VALIGN',(1,0),(1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),2.6), ('BOTTOMPADDING',(0,0),(-1,-1),2.6),
        ('TOPPADDING',(0,0),(0,-1),3.4),
    ]))
    return t

# ================= сторінка 1: механік =================
story = []
A = story.append

A(P('Що це', 'h'))
A(P('Замість того щоб писати від руки, хто що взяв зі складу, ви відкриваєте застосунок, '
    'знаходите деталь і натискаєте кнопку. Застосунок сам зменшує залишок і записує, '
    'хто, що, коли і куди поставив.'))

A(P('Вхід', 'h'))
A(P('Введіть свій <b>PIN</b> — і застосунок відкриється. Вхід тримається до 12 годин, '
    'але якщо не торкатися екрана <b>10 хвилин</b>, він вийде сам. Це щоб залишений на верстаті '
    'планшет не був відкритим складом.'))
A(Spacer(1, 2))
A(P('PIN у вас особистий. Усе, що ви зробите, підпишеться вашим іменем — підставити чуже '
    'неможливо.', 'tiny'))

A(P('Що на екрані', 'h'))
for label, text in [
    ('Ім’я вгорі',      'хто зараз працює. Поруч кнопка «Вийти»'),
    ('Список категорій','Підшипники, ЗІП на лінії, Електрика…'),
    ('Пошук',           'шукає за назвою, обладнанням і місцем зберігання'),
    ('Картка деталі',   'залишок, мінімум, де лежить, постачальник. Червона позначка — залишок нижче мінімуму'),
]:
    A(Paragraph('<b>%s</b> — %s' % (label, text), S['li'], bulletText='•'))

A(P('Списати деталь — 5 кроків', 'h'))
A(steps([
    ('Знайдіть деталь', 'Через категорію або пошук. Шукає і за назвою, і за місцем зберігання.'),
    ('Натисніть на неї', 'Відкриється вікно операції.'),
    ('Кількість', 'Тільки цілі штуки.'),
    ('Де використано', '«Лінія 1, мотор конвеєра». Пишіть так, щоб через місяць було зрозуміло.'),
    ('«Зареєструвати видачу»', 'Готово. Залишок зменшився, запис пішов у журнал.'),
]))

A(P('Подивитись, що вже списано', 'h'))
A(P('Дві кнопки під заголовком: <b>«Мої за сьогодні»</b> — лише ваші записи за цей день, '
    '<b>«Всі списання»</b> — загальна історія по всіх.'))

A(FrameBreak())

A(P('Кольорова плашка вгорі', 'h'))
A(P('Показує, чи все надіслано на сервер.', 'tiny'))
A(Spacer(1, 1))
A(dots([
    (GREEN,                       'Онлайн',        'усе гаразд, нічого не чекає'),
    (colors.HexColor('#2563eb'),  'Черга 3',       'три записи чекають на зв’язок. Нічого робити не треба'),
    (colors.HexColor('#dc2626'),  'Помилок 1',     'сервер щось відхилив. Натисніть плашку і оберіть рішення'),
    (colors.HexColor('#9ca3af'),  'Немає зв’язку', 'працюйте далі, записи збережуться'),
]))

A(P('Якщо застосунок сперечається', 'h'))
A(callout('«На складі лише 2 шт, а ви списуєте 5»', [
    'Оберіть один із варіантів: <b>списати наявні 2</b> (найчастіше так і треба), '
    '<b>списати більше і пояснити чому</b>, або <b>лишити в черзі</b> і розібратись потім.',
], AMB_L, AMB))
A(Spacer(1, 4))
A(callout('«Залишок не інвентаризовано»', [
    'Означає, що кількість цієї деталі ніхто не рахував. Від невідомого числа не можна віднімати, '
    'тому видача не проходить. Скажіть адміністратору — він перерахує позицію.',
], AMB_L, AMB))

A(P('Помилились?', 'h'))
A(P('Відкрийте «Мої за сьогодні», знайдіть запис і натисніть <b>«Скасувати»</b> — '
    'протягом доби. Залишок повернеться. Нічого не стирайте в таблиці руками.'))

A(P('Без інтернету', 'h'))
A(P('Застосунок працює й без мережі: запис зберігається в телефоні й піде сам, щойно '
    'з’явиться зв’язок.'))
A(Spacer(1, 3))
A(callout('Одне важливе правило', [
    'Якщо застосунок сказав <b>«Запис збережено на пристрої»</b> — не робіть операцію вдруге. '
    'Вона вже в черзі. Повторний запис спише деталь двічі.',
], RED_L, RED))

A(P('Коротко', 'h'))
for t in ['Списуємо <b>в застосунку</b>, а не в таблиці.',
          'Кількість — <b>цілими штуками</b>.',
          'Помилку виправляємо <b>«Скасувати»</b>, а не правкою таблиці.',
          'Синя плашка — нормально. Червона — покличте адміністратора.']:
    A(Paragraph(t, S['li'], bulletText='•'))

# ================= сторінка 2: адміністратор =================
A(NextPageTemplate('admin'))
from reportlab.platypus import PageBreak
A(PageBreak())

A(P('Що додається до ролі адміністратора', 'h'))
A(grid([
    ['Дія', 'Мех.', 'Адмін'],
    ['Видача деталі', '✓', '✓'],
    ['Скасувати свою операцію (доба)', '✓', '✓'],
    ['Поповнення складу', '—', '✓'],
    ['Інвентаризація', '—', '✓'],
    ['Місце зберігання', '—', '✓'],
    ['Звіт на пошту', '—', '✓'],
    ['Скасувати чужу операцію, будь-коли', '—', '✓'],
], [48*mm, 15*mm, 19*mm]))

A(P('Дві додаткові операції', 'h'))
A(P('У вікні позиції вгорі — перемикач. Це три різні дії:'))
A(Spacer(1, 2))
A(callout('Поповнення', [
    'Деталі привезли. У полі «де використано» пишіть номер накладної. Залишок збільшиться.',
], MINT, GREEN))
A(Spacer(1, 3))
A(callout('Інвентаризація', [
    'Перерахували руками. Ви кажете: «тут насправді стільки». Це число стає новою точкою '
    'відліку. Стара історія не зникає — застосунок покаже, наскільки облік розійшовся з фактом.',
], MINT, GREEN))
A(Spacer(1, 3))
A(P('Саме інвентаризацією виправляють дивний залишок. Не правкою клітинки в таблиці.', 'tiny'))

A(P('Місце зберігання', 'h'))
A(P('Кнопка «Змінити» у вікні позиції. Пишіть так, щоб деталь знайшли не питаючи: '
    '«Контейнер 1, стелаж B, полиця 3». Адреса потрапляє в пошук і в листи про дефіцит.'))

A(P('Скасування чужих операцій', 'h'))
A(P('Механік може скасувати лише свій запис і лише протягом доби. Ви — <b>будь-чий і будь-коли</b>. '
    'Кнопка «Скасувати» є в «Усіх списаннях» біля кожного запису.'))
A(Spacer(1, 2))
A(P('Скасування нічого не стирає: початковий рядок помічається як «(скасовано)», поруч '
    'додається рядок скасування. Залишок повертається.', 'tiny'))

A(FrameBreak())

A(P('Звіт на пошту', 'h'))
A(P('Щопонеділка о 8:00 приходить лист: що замовити, що потребує інвентаризації, від’ємні '
    'залишки, надлишок і рух за тиждень. Кнопка <b>«Надіслати звіт»</b> робить те саме будь-коли.'))
A(Spacer(1, 2))
A(P('Отримують усі, хто має право на звіт і чия пошта вказана в кадровому довіднику.', 'tiny'))

A(P('У таблиці «ЗІП мех служба»', 'h'))
A(callout('Чого робити не можна', [
    '<b>Не виправляйте залишок руками</b> — наступна операція перерахує його з журналу '
    'і ваша правка зникне.',
    '<b>Не видаляйте рядки журналу</b> — з них рахується залишок.',
    '<b>Не міняйте назви аркушів і порядок колонок.</b>',
], RED_L, RED))
A(Spacer(1, 3))
A(callout('А це — можна', [
    'Вставляти й сортувати рядки, дописувати нові позиції. Застосунок упізнає деталь за парою '
    '«номер + назва», а не за номером рядка.',
], BLUE_L, BLUE))

A(P('Раз на тиждень', 'h'))
A(P('У таблиці: <b>Розширення → Apps Script</b>, оберіть функцію і натисніть <b>Виконати</b>.'))
A(Spacer(1, 2))
for fn, why in [
    ('auditSheetSync()',    'звіряє аркуші з журналом. «Аркуші збігаються з журналом» = усе гаразд'),
    ('rebuildOperations()', 'запускати, лише якщо попередня знайшла розходження'),
    ('auditEvents(7)',      'помилки застосунку за тиждень — перше, куди дивитись при скаргах'),
    ('auditPins()',         'чи немає однакових PIN. Після кожної зміни в довіднику'),
    ('auditRecipients()',   'хто отримує звіт і в кого не вказано пошту'),
]:
    A(Paragraph('<b>%s</b> — %s' % (fn, why), S['li'], bulletText='•'))

A(P('Що робити, коли…', 'h'))
for q, a in [
    ('Механік не може увійти',           'auditPins() — можливо, у двох однаковий PIN'),
    ('Списання є в журналі, немає в аркуші', 'auditSheetSync(), потім rebuildOperations()'),
    ('Залишок виглядає дивно',           'інвентаризація, а не правка клітинки'),
    ('Не приходять листи',               'auditRecipients() — перевірити пошту в довіднику'),
]:
    A(Paragraph('<b>%s</b> → %s' % (q, a), S['li'], bulletText='•'))

A(Spacer(1, 6))
A(P('Питання й проблеми — до адміністратора системи. '
    'Детальна інструкція: «ЗІП-інструкція-адміністратора.pdf».', 'tiny'))

# ================= збірка =================
MARG_X, TOP_BAND, BOTTOM = 14*mm, 26*mm, 12*mm
GAP = 6*mm
W, H = A4
col_w = (W - 2*MARG_X - GAP) / 2
frame_y = BOTTOM
frame_h = H - TOP_BAND - BOTTOM - 4*mm

def band(canvas, doc, title, subtitle, tag):
    canvas.saveState()
    canvas.setFillColor(GREEN)
    canvas.rect(0, H - TOP_BAND, W, TOP_BAND, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont('DJ-B', 15)
    canvas.drawString(MARG_X, H - 15*mm, title)
    canvas.setFont('DJ', 8.6)
    canvas.setFillColor(colors.HexColor('#d1fae5'))
    canvas.drawString(MARG_X, H - 21*mm, subtitle)
    # ярлик сторінки праворуч
    canvas.setFont('DJ-B', 8.6)
    tw = canvas.stringWidth(tag, 'DJ-B', 8.6)
    canvas.setFillColor(DARK)
    canvas.roundRect(W - MARG_X - tw - 9, H - 18.6*mm, tw + 9, 6.4*mm, 3.2, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.drawString(W - MARG_X - tw - 4.5, H - 16.8*mm, tag)
    # підвал
    canvas.setFont('DJ', 7.2)
    canvas.setFillColor(GREY)
    canvas.drawString(MARG_X, 7*mm, 'Облік ЗІП: Механік · серпень 2026')
    canvas.drawRightString(W - MARG_X, 7*mm, 'стор. %d з 2' % canvas.getPageNumber())
    canvas.setStrokeColor(LINE); canvas.setLineWidth(0.4)
    canvas.line(MARG_X, 10*mm, W - MARG_X, 10*mm)
    # роздільник колонок
    canvas.setStrokeColor(colors.HexColor('#eceff3'))
    canvas.line(W/2, BOTTOM + 2*mm, W/2, H - TOP_BAND - 4*mm)
    canvas.restoreState()

def p1(c, d): band(c, d, 'Як користуватися застосунком', 'Облік запчастин механічної служби', 'ДЛЯ ВСІХ')
def p2(c, d): band(c, d, 'Що вміє адміністратор', 'Додатково до того, що на першій сторінці', 'ДЛЯ АДМІНА')

frames = [Frame(MARG_X, frame_y, col_w, frame_h, id='l', leftPadding=0, rightPadding=0,
                topPadding=0, bottomPadding=0),
          Frame(MARG_X + col_w + GAP, frame_y, col_w, frame_h, id='r', leftPadding=0,
                rightPadding=0, topPadding=0, bottomPadding=0)]

OUT = '/home/user/spare-parts-mechanic-service/docs/ЗІП-коротка-інструкція.pdf'
doc = BaseDocTemplate(OUT, pagesize=A4,
                      leftMargin=MARG_X, rightMargin=MARG_X, topMargin=TOP_BAND, bottomMargin=BOTTOM,
                      title='Облік ЗІП: Механік — коротка інструкція',
                      author='Механічна служба', subject='Як користуватися застосунком')
doc.addPageTemplates([
    PageTemplate(id='mech',  frames=[f for f in frames], onPage=p1),
    PageTemplate(id='admin', frames=[Frame(MARG_X, frame_y, col_w, frame_h, id='l2', leftPadding=0,
                                           rightPadding=0, topPadding=0, bottomPadding=0),
                                     Frame(MARG_X + col_w + GAP, frame_y, col_w, frame_h, id='r2',
                                           leftPadding=0, rightPadding=0, topPadding=0,
                                           bottomPadding=0)], onPage=p2),
])
doc.build(story)
print('готово:', OUT)
