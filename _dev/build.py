#!/usr/bin/env python3
"""Cavad Mikayil Təlim Portalı — build aləti.

İstifadə (repo kökündən):
    python3 _dev/build.py                 # dərsləri qur, footer-ləri yenilə, yoxla
    python3 _dev/build.py icons add NAME  # sprite-a Lucide ikonu əlavə et (əvvəlcə: cd _dev && npm install)
    python3 _dev/build.py check           # yalnız yoxlama (heç nə yazmır): ikonlar, kataloq, suallar, daxili linklər
    python3 _dev/build.py links --external  # xarici linkləri yoxla (internet lazımdır)

Nə edir:
  1. _dev/lessons/*.html mənbələrini lessons/*.html səhifələrinə çevirir
     (<!--PAGE ...-->, <!--END--> və {{i:ikon}} markerləri).
  2. Bütün səhifələrdə footer-i (sosial ikonlarla) eyni saxlayır.
  3. about.html-dəki sosial kartları SOCIALS siyahısından yeniləyir.
  4. icons.svg keçidlərinə versiya (?v=hash) əlavə edir ki, brauzer köhnə sprite göstərməsin.
  4a. Hər səhifənin <head>-inə SEO bloku (description, canonical, Open Graph, Twitter, JSON-LD) yazır,
      sitemap.xml və robots.txt yaradır (SITE_URL). Paylaşım şəkilləri: node _dev/og.js
  5. Yoxlayır: istifadə olunan ikonlar sprite-da var, kataloqdakı dərs faylları mövcuddur,
     hər dərsin quiz sualı var.
"""
import base64
import hashlib
import json
import pathlib
import re
import subprocess
import sys

DEV = pathlib.Path(__file__).resolve().parent
ROOT = DEV.parent
SRC = DEV / 'lessons'
OUT = ROOT / 'lessons'
SPRITE = ROOT / 'assets' / 'icons.svg'
NODE = DEV / 'node_modules'

# ---------------------------------------------------------------------------
# Sayt məlumatları — sosial linklər və menyu buradan dəyişdirilir
# ---------------------------------------------------------------------------
SOCIALS = [
    # id, ad, url, ikon, qısa izah (Haqqında səhifəsində)
    ('instagram', 'Instagram', 'https://instagram.com/cavadmikayil.com_', 'brand-instagram', '@cavadmikayil.com_'),
    ('youtube', 'YouTube kanalı', 'https://youtube.com/@cavadmikayil', 'brand-youtube', '@cavadmikayil'),
    ('linkedin', 'LinkedIn', 'https://az.linkedin.com/in/cavad-mikayil-0a8153212', 'brand-linkedin-in', 'Peşəkar profil'),
    ('blog', 'Blog sayt', 'https://cavadmikayil.com', 'globe', 'cavadmikayil.com'),
    ('telegram', 'Telegram', 'https://t.me/cavadmikayil', 'brand-telegram', '@cavadmikayil'),
    ('tiktok', 'TikTok', 'https://tiktok.com/@cavadmikayil', 'brand-tiktok', '@cavadmikayil'),
    ('email', 'Email', 'mailto:info@cavadmikayil.com', 'mail', 'info@cavadmikayil.com'),
]

# Saytın ünvanı — canonical, Open Graph, sitemap.xml və robots.txt buradan qurulur.
# Repo adı dəyişəndə və ya öz domen qoşulanda yalnız bunu dəyişib "python3 _dev/build.py" işlədin.
SITE_URL = 'https://portal.cavadmikayil.com/'
SITE_NAME = 'Cavad Mikayil Təlim Portalı'
AUTHOR = 'Cavad Mikayil'
# Google Search Console → "HTML tag" üsulu ilə verilən content dəyəri (boşdursa tag əlavə olunmur)
GOOGLE_SITE_VERIFICATION = ''

NAV = [
    ('home', 'Ana Səhifə', 'index.html', 'house'),
    ('lessons', 'Dərslər', 'lessons.html', 'book-open'),
    ('tools', 'Tools', 'tools.html', 'toolbox'),
    ('videos', 'Video Dərslər', 'videos.html', 'circle-play'),
    ('links', 'Faydalı', 'links.html', 'library'),
    ('about', 'Haqqında', 'about.html', 'user-round'),
]

# Hansı səhifədə menyunun hansı bəndi aktivdir (fayl adı → NAV id)
NAV_ACTIVE = {'index.html': 'home', 'lessons.html': 'lessons', 'tools.html': 'tools', 'videos.html': 'videos',
              'links.html': 'links', 'about.html': 'about'}

# Dərsin badge-i ilə başlayan söz → dashboard-da açılacaq kateqoriya (Portal düyməsi)
BADGE_TO_CATEGORY = {
    'CCNA': 'ccna',
    'Server': 'server',
    'Helpdesk': 'helpdesk',
    'Təhlükəsizlik': 'security',
    'AI': 'ai',
    'Cloud': 'cloud',
    'DevOps': 'devops',
    'Automation': 'automation',
    'CompTIA': 'comptia',
    'Linux': 'linux',
}


# ---------------------------------------------------------------------------
# İkonlar
# ---------------------------------------------------------------------------
def icon(prefix, name, extra=''):
    cls = f'icon {extra}'.strip()
    return f'<svg class="{cls}" aria-hidden="true"><use href="{prefix}assets/icons.svg#{name}"></use></svg>'


def _brand_svg(name):
    path = NODE / '@fortawesome/fontawesome-free/svgs/brands' / f'{name}.svg'
    if path.exists():
        return path.read_text()
    return None


def _sprite_symbol(name):
    """Sprite-dakı simvolun viewBox və içini qaytarır (inline SVG üçün)."""
    m = re.search(rf'<symbol id="{re.escape(name)}" viewBox="([^"]+)">(.*?)</symbol>', SPRITE.read_text(), re.S)
    if not m:
        raise SystemExit(f'İkon sprite-da yoxdur: {name}')
    return m.group(1), m.group(2)


def inline_svg(name, cls='icon'):
    """Sosial ikonlar sprite keşindən asılı olmasın deyə səhifəyə birbaşa yazılır."""
    view_box, inner = _sprite_symbol(name)
    return f'<svg class="{cls}" viewBox="{view_box}" aria-hidden="true">{inner}</svg>'


def icons_add(names):
    """Lucide (ISC) və ya Font Awesome brand (CC BY 4.0, 'brand-' prefiksi) ikonlarını sprite-a əlavə edir."""
    lucide = NODE / 'lucide-static/icons'
    if not lucide.exists():
        raise SystemExit('Əvvəlcə ikon paketlərini quraşdırın:  cd _dev && npm install')
    text = SPRITE.read_text()
    existing = set(re.findall(r'<symbol id="([a-z0-9-]+)"', text))
    new = []
    for name in names:
        if name in existing:
            print('artıq var:', name)
            continue
        if name.startswith('brand-'):
            src = _brand_svg(name[6:])
            if not src:
                raise SystemExit(f'Font Awesome brand ikonu tapılmadı: {name[6:]}')
            view_box = re.search(r'viewBox="([^"]+)"', src).group(1)
            inner = ''.join(f'<path fill="currentColor" stroke="none" d="{d}"/>'
                            for d in re.findall(r'<path[^>]*\sd="([^"]+)"', src))
        else:
            path = lucide / f'{name}.svg'
            if not path.exists():
                raise SystemExit(f'Lucide ikonu tapılmadı: {name} (siyahı: https://lucide.dev/icons)')
            view_box = '0 0 24 24'
            inner = re.sub(r'\s+', ' ', re.search(r'<svg[^>]*>(.*)</svg>', path.read_text(), re.S).group(1)).strip()
        new.append(f'<symbol id="{name}" viewBox="{view_box}">{inner}</symbol>')
        print('əlavə olundu:', name)
    if new:
        body = text.rstrip()
        assert body.endswith('</svg>')
        SPRITE.write_text(body[:-len('</svg>')] + '\n'.join(new) + '\n</svg>\n')


# ---------------------------------------------------------------------------
# Ümumi hissələr: menyu, footer
# ---------------------------------------------------------------------------
def ext_attrs(url):
    return '' if url.startswith('mailto:') else ' target="_blank" rel="noopener noreferrer"'


def nav(prefix, active='', on_dark=False, extra_cls=''):
    act = ' class="active" aria-current="page"'
    items = '\n'.join(
        f'                    <a href="{prefix}{href}" data-nav="{i}"{act if i == active else ""}>{icon(prefix, ic)} {label}</a>'
        for i, label, href, ic in NAV)
    cls = 'site-nav' + (' on-dark' if on_dark else '') + (' ' + extra_cls if extra_cls else '')
    return f'<nav class="{cls}" aria-label="Sayt menyusu">\n{items}\n                </nav>'


def site_header(prefix, active):
    """Portalın ümumi səhifələri (Tools, Video Dərslər, Linklər, Haqqında) üçün yuxarı başlıq."""
    return f'''<header class="bg-white shadow-md sticky top-0 z-50" data-site-header>
        <div class="container mx-auto px-6 py-3 flex flex-wrap gap-x-3 gap-y-2 justify-between items-center">
            <a href="{prefix}index.html" class="flex items-center gap-2 text-lg font-extrabold text-neutral-900">
                <span class="site-logo">{icon(prefix, 'graduation-cap')}</span> Cavad Mikayil Təlim Portalı
            </a>
            {nav(prefix, active, extra_cls='order-last md:order-none md:ml-auto')}
            <button class="theme-toggle-btn" aria-label="Tema dəyiş">{icon(prefix, 'moon')}</button>
        </div>
    </header>'''


def page_active(page):
    if page.parent.name == 'tools':
        return 'tools'
    return NAV_ACTIVE.get(page.name, '')


def refresh_navs():
    """Bütün səhifələrdə menyunu (site header və dashboard menyusu) NAV siyahısından yenidən qurur."""
    head_pat = re.compile(r'<header class="bg-white shadow-md sticky top-0 z-50" data-site-header>[\s\S]*?</header>')
    nav_pat = re.compile(r'<nav class="(site-nav[^"]*)" aria-label="Sayt menyusu">[\s\S]*?</nav>')
    for page in all_pages():
        prefix = '' if page.parent == ROOT else '../'
        text = page.read_text()
        new = head_pat.sub(lambda m: site_header(prefix, page_active(page)), text)
        if 'data-site-header' not in new:
            def repl(m):
                classes = m.group(1).split()
                on_dark = 'on-dark' in classes
                extra = ' '.join(c for c in classes if c not in ('site-nav', 'on-dark'))
                return nav(prefix, page_active(page), on_dark, extra)
            new = nav_pat.sub(repl, new)
        if new != text:
            page.write_text(new)


def footer(prefix, cls='brand-footer'):
    links = '\n'.join(f'                    <a href="{prefix}{href}">{label}</a>' for _, label, href, _ in NAV)
    social = '\n'.join(
        f'                    <a href="{url}"{ext_attrs(url)} title="{name}" aria-label="{name}" data-social="{sid}">{inline_svg(ic)}</a>'
        for sid, name, url, ic, _ in SOCIALS)
    return f'''<footer class="{cls}">
        <div class="brand-footer-inner">
            <div class="brand-footer-top">
                <div>
                    <a href="{prefix}index.html" class="brand-footer-name">{icon(prefix, 'graduation-cap')} Cavad Mikayil Təlim Portalı</a>
                    <p class="brand-footer-tagline">İnformasiya Texnologiyaları üzrə beynəlxalq sertifikatlı təlimçi, şəbəkə təhlükəsizliyi mühəndisi</p>
                </div>
                <nav class="brand-footer-links" aria-label="Footer keçidləri">
{links}
                    <a href="https://www.cavadmikayil.com" target="_blank" rel="noopener">www.cavadmikayil.com</a>
                </nav>
            </div>
            <div class="brand-footer-social-wrap">
                <div class="brand-footer-social" aria-label="Sosial şəbəkələr">
{social}
                </div>
            </div>
            <p class="brand-footer-copy">&copy; 2027 <strong>Cavad Mikayil</strong>. Bütün hüquqlar qorunur.</p>
        </div>
    </footer>'''


# ---------------------------------------------------------------------------
# Dərs mənbələrinin qurulması
# ---------------------------------------------------------------------------
def lesson_head(attrs, extra_head='', category=''):
    links = '\n'.join(
        f'                <a href="#{i}" class="nav-link">{label}</a>'
        for i, label in (item.split(':', 1) for item in attrs['nav'].split('|')))
    badge_text = attrs.get('badge', '')
    badge = f'\n                <span class="lesson-badge">{badge_text}</span>' if badge_text else ''
    cat = BADGE_TO_CATEGORY.get(badge_text.split(' ')[0], '') if badge_text else ''
    back = f'#{cat}' if cat else ''
    return f'''<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{attrs["title"]} — {category or 'Dərs Vəsaiti'} | {SITE_NAME}</title>
    <link rel="stylesheet" href="../assets/fonts.css">
    <link rel="stylesheet" href="../assets/lesson.css">
    <link rel="stylesheet" href="../assets/theme.css">{extra_head}
    <link rel="stylesheet" href="../assets/tailwind.css">
</head>
<body class="antialiased">

    <header class="bg-white shadow-md sticky top-0 z-50">
        <nav class="container mx-auto px-6 py-4 flex flex-wrap gap-3 justify-between items-center">
            <div class="flex items-center gap-3 flex-wrap">
                <h1 class="text-2xl font-bold flex items-center gap-2">{icon("../", attrs["icon"], "text-amber-600")} {attrs["title"]}</h1>{badge}
            </div>
            <div class="flex flex-wrap items-center gap-4">
{links}
                <a href="../index.html{back}" class="portal-home-link">{icon("../", "arrow-left")} Portal</a>
                <button class="theme-toggle-btn" aria-label="Tema dəyiş">{icon("../", "moon")}</button>
            </div>
        </nav>
    </header>

    <main class="container mx-auto px-6 py-8 max-w-6xl">
'''


def lesson_end(extra_foot=''):
    return f'''    </main>

    {footer("../")}

    <script src="../assets/student.js"></script>
    <script src="../assets/lesson.js"></script>
    <script src="../assets/theme.js"></script>{extra_foot}
</body>
</html>
'''


# ---------------------------------------------------------------------------
# CCNA lab tapşırıqları (_dev/labs/*.py) — dərsin sonuna "Lab" bölməsi kimi əlavə olunur
# ---------------------------------------------------------------------------
def load_labs():
    import importlib.util
    labs = {}
    for f in sorted((DEV / 'labs').glob('*.py')):
        spec = importlib.util.spec_from_file_location(f'labs_{f.stem}', f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for lab in mod.LABS:
            for key in ('slug', 'title', 'goal', 'tool', 'time', 'tasks'):
                if key not in lab:
                    raise SystemExit(f'{f.name}: {lab.get("slug", "?")} lab-ında "{key}" yoxdur')
            if lab['slug'] in labs:
                raise SystemExit(f'lab təkrarlanır: {lab["slug"]} ({f.name})')
            labs[lab['slug']] = lab
    return labs


def _esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def render_lab(lab):
    def ico(name):
        return '{{i:' + name + '}}'

    def code(text):
        return _esc(text.strip('\n'))

    out = []
    out.append(f'        <section id="lab" class="section-card lab-section" data-lab="{lab["slug"]}">')
    out.append(f'            <h2 class="section-title">{ico("flask-conical")} Lab: {lab["title"]}</h2>')
    out.append('            <div class="card-grid mb-6">')
    out.append(f'                <div class="info-card accent"><h3>{ico("target")} Məqsəd</h3><p class="text-neutral-700">{lab["goal"]}</p></div>')
    out.append(f'                <div class="info-card"><h3>{ico("wrench")} Alət</h3><p class="text-neutral-700">{lab["tool"]}</p></div>')
    out.append(f'                <div class="info-card dark"><h3>{ico("timer")} Müddət</h3><p>{lab["time"]} · {lab.get("level", "Orta")}</p></div>')
    out.append('            </div>')
    if lab.get('topology'):
        out.append('            <h3 class="text-xl font-bold mb-3">Topologiya</h3>')
        out.append('            <div class="code-block lab-topology mb-6">')
        out.append(f'                <pre><code>{code(lab["topology"])}</code></pre>')
        out.append('            </div>')
    if lab.get('addressing'):
        head, *rows = lab['addressing']
        out.append('            <h3 class="text-xl font-bold mb-3">Ünvanlama cədvəli</h3>')
        out.append('            <div class="table-wrap mb-6">')
        out.append('                <table class="data-table">')
        out.append('                    <thead><tr>' + ''.join(f'<th>{c}</th>' for c in head) + '</tr></thead>')
        out.append('                    <tbody>')
        for r in rows:
            out.append('                        <tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>')
        out.append('                    </tbody>')
        out.append('                </table>')
        out.append('            </div>')
    out.append('            <h3 class="text-xl font-bold mb-3">Tapşırıqlar</h3>')
    out.append('            <ol class="steps max-w-3xl mx-auto mb-6">')
    for t in lab['tasks']:
        out.append(f'                <li><p class="text-neutral-700">{t}</p></li>')
    out.append('            </ol>')
    if lab.get('verify'):
        out.append('            <h3 class="text-xl font-bold mb-3">Yoxlama</h3>')
        out.append('            <div class="code-block mb-6">')
        out.append('                <button class="copy-btn">Kopyala</button>')
        out.append(f'                <pre><code>{code(lab["verify"])}</code></pre>')
        out.append('            </div>')
    if lab.get('expect'):
        out.append('            <h3 class="text-xl font-bold mb-3">Uğur meyarları</h3>')
        out.append('            <div class="feature-grid mb-6">')
        for e in lab['expect']:
            out.append(f'                <div class="feature-item">{ico("circle-check")}<p class="text-neutral-700">{e}</p></div>')
        out.append('            </div>')
    if lab.get('solution'):
        out.append('            <details class="lab-solution mb-6">')
        out.append(f'                <summary>{ico("key-round")} Həll — əvvəlcə özünüz cəhd edin</summary>')
        out.append('                <div class="code-block mt-3">')
        out.append('                    <button class="copy-btn">Kopyala</button>')
        out.append(f'                    <pre><code>{code(lab["solution"])}</code></pre>')
        out.append('                </div>')
        out.append('            </details>')
    note = lab.get('note', 'Packet Tracer faylı (.pkt) verilmir — topologiyanı özünüz qurmaq labın bir hissəsidir.')
    out.append('            <div class="lab-footer">')
    out.append(f'                <p class="text-sm text-neutral-600">{note}</p>')
    out.append(f'                <button type="button" class="lab-done-btn" data-lab="{lab["slug"]}" aria-pressed="false">{ico("circle-dot")} Labı bitirdim</button>')
    out.append('            </div>')
    out.append('        </section>')
    return '\n'.join(out) + '\n'


def build_lessons():
    count = 0
    sections = {}
    labs = load_labs()
    catalog, _ = load_catalog()
    cat_label = {}
    if catalog:
        labels = {c['id']: c['label'] for c in catalog['categories']}
        cat_label = {l['href'].split('/')[-1]: labels[l['cat']] for l in catalog['lessons']}
    used = set()
    for src in sorted(SRC.glob('*.html')):
        text = src.read_text()
        m = re.search(r'<!--PAGE (.*?)-->\n?', text, re.S)
        if not m:
            raise SystemExit(f'{src.name}: <!--PAGE ...--> markeri yoxdur')
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        for key in ('title', 'icon', 'nav'):
            if key not in attrs:
                raise SystemExit(f'{src.name}: PAGE markerində "{key}" yoxdur')
        # İstəyə bağlı: <!--HEAD-->...<!--/HEAD--> (səhifəyə xas CSS/skript <head>-ə)
        # və <!--FOOT-->...<!--/FOOT--> (səhifəyə xas skriptlər lesson.js-dən sonra)
        blocks = {}
        for name in ('HEAD', 'FOOT'):
            bm = re.search(rf'\n?<!--{name}-->\n?(.*?)<!--/{name}-->\n?', text, re.S)
            blocks[name] = ('\n' + bm.group(1).rstrip()) if bm else ''
            if bm:
                text = text[:bm.start()] + text[bm.end():]
        lab = labs.get(src.stem)
        if lab:
            used.add(src.stem)
            attrs['nav'] += '|lab:Lab'
            text = text.replace('<!--END-->', render_lab(lab) + '<!--END-->', 1)
        sections[src.stem] = [item.split(':', 1) for item in attrs['nav'].split('|')]
        m = re.search(r'<!--PAGE (.*?)-->\n?', text, re.S)
        text = text[:m.start()] + lesson_head(attrs, blocks['HEAD'], cat_label.get(src.name, '')) + text[m.end():]
        if '<!--END-->' not in text:
            raise SystemExit(f'{src.name}: <!--END--> markeri yoxdur')
        text = text.replace('<!--END-->', lesson_end(blocks['FOOT']))
        text = re.sub(r'\{\{i:([a-z0-9-]+)\}\}', lambda mm: icon('../', mm.group(1)), text)
        if '{{i:' in text:
            raise SystemExit(f'{src.name}: açılmamış {{{{i:...}}}} markeri')
        (OUT / src.name).write_text(text)
        count += 1
    _write_if_changed(ROOT / 'assets' / 'lesson-sections.js',
        '// Hər dərsin bölmələri (lessons.html "materiallar" siyahısı üçün) — build.py avtomatik yaradır, əl ilə dəyişməyin.\n'
        'window.LESSON_SECTIONS = ' + json.dumps(sections, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + ';\n')
    unknown = set(labs) - used
    if unknown:
        raise SystemExit(f'lab-ın dərsi yoxdur: {", ".join(sorted(unknown))}')
    print(f'{count} dərs quruldu (_dev/lessons → lessons/), {len(used)} lab')


# ---------------------------------------------------------------------------
# Əl ilə yazılmış səhifələrdə footer və Haqqında kartları
# ---------------------------------------------------------------------------
def all_pages():
    return sorted(ROOT.glob('*.html')) + sorted((ROOT / 'lessons').glob('*.html')) + sorted((ROOT / 'tools').glob('*.html'))


def refresh_footers():
    pat = re.compile(r'<footer class="(brand-footer[^"]*)">[\s\S]*?</footer>')
    for page in all_pages():
        prefix = '' if page.parent == ROOT else '../'
        text = page.read_text()
        new, n = pat.subn(lambda m: footer(prefix, m.group(1)), text)
        if n != 1:
            print(f'XƏBƏRDARLIQ: {page.relative_to(ROOT)} səhifəsində footer tapılmadı')
        if new != text:
            page.write_text(new)


def refresh_about():
    page = ROOT / 'about.html'
    cards = '\n'.join(f'''                    <a class="social-card" href="{url}"{ext_attrs(url)} data-social="{sid}">
                        <span class="social-icon">{inline_svg(ic)}</span>
                        <span class="min-w-0">
                            <span class="social-name">{name}</span>
                            <span class="social-handle">{handle}</span>
                        </span>
                        {icon('', 'external-link' if not url.startswith('mailto:') else 'arrow-right')}
                    </a>''' for sid, name, url, ic, handle in SOCIALS)
    text = page.read_text()
    new, n = re.subn(r'(<div class="social-grid">\n)[\s\S]*?(\n            </div>\n        </section>)',
                     lambda m: m.group(1) + cards + m.group(2), text, count=1)
    if n == 1 and new != text:
        page.write_text(new)


# ---------------------------------------------------------------------------
# SEO: meta description, canonical, Open Graph, Twitter, JSON-LD, sitemap.xml, robots.txt
# ---------------------------------------------------------------------------
SEO_BLOCK = re.compile(r'\n[ \t]*<!--SEO-->[\s\S]*?<!--/SEO-->')
DESC_META = re.compile(r'\n[ \t]*<meta name="description" content="([^"]*)">')


def page_url(rel):
    return SITE_URL if rel == 'index.html' else SITE_URL + rel


def og_image(rel):
    return 'assets/og/' + rel[:-5] + '.jpg'


def _attr(text):
    return text.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


def _unattr(text):
    return text.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')


def lesson_desc(lesson, label):
    extra = 'lab tapşırıqları və quiz' if lesson['cat'] == 'ccna' else 'quiz sualları'
    return f'{lesson["desc"]} {label}: Azərbaycan dilində pulsuz dərs vəsaiti, {extra}.'


def seo_block(rel, title, desc, kind, prefix):
    url = page_url(rel)
    image = SITE_URL + og_image(rel)
    person = {'@type': 'Person', 'name': AUTHOR, 'url': SITE_URL + 'about.html',
              'jobTitle': 'İT təlimçisi, şəbəkə təhlükəsizliyi mühəndisi',
              'sameAs': [u for _, _, u, _, _ in SOCIALS if u.startswith('http')]}
    if rel == 'index.html':
        ld = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': SITE_NAME, 'url': SITE_URL,
              'inLanguage': 'az', 'description': desc, 'image': image, 'author': person, 'publisher': person}
    elif kind == 'lesson':
        ld = {'@context': 'https://schema.org', '@type': 'LearningResource', 'name': title.split(' — ')[0],
              'description': desc, 'url': url, 'image': image, 'inLanguage': 'az',
              'learningResourceType': 'Dərs vəsaiti', 'isAccessibleForFree': True, 'author': person,
              'isPartOf': {'@type': 'WebSite', 'name': SITE_NAME, 'url': SITE_URL}}
    elif kind == 'tool':
        ld = {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': title.split(' — ')[0],
              'description': desc, 'url': url, 'image': image, 'inLanguage': 'az',
              'applicationCategory': 'EducationalApplication', 'operatingSystem': 'Any',
              'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'AZN'},
              'author': person}
    else:
        ld = None
    # Sosial kartda sayt adı og:site_name ilə ayrıca göstərilir — başlıqda təkrarlanmır
    short = title if kind == 'page' else re.sub(rf'\s*[|—]\s*{SITE_NAME}$', '', title)
    t, d = _attr(short), _attr(desc)
    lines = [
        '<!--SEO-->',
        f'<meta name="description" content="{d}">',
        f'<link rel="canonical" href="{url}">',
        '<meta name="theme-color" content="#0a0a0a">',
        f'<meta name="author" content="{AUTHOR}">',
        f'<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">',
        f'<link rel="icon" href="{prefix}assets/favicon-32.png" type="image/png" sizes="32x32">',
        f'<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">',
    ]
    if GOOGLE_SITE_VERIFICATION and rel == 'index.html':
        lines.append(f'<meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">')
    lines += [
        f'<meta property="og:type" content="{"article" if kind == "lesson" else "website"}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        '<meta property="og:locale" content="az_AZ">',
        f'<meta property="og:title" content="{t}">',
        f'<meta property="og:description" content="{d}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image}">',
        '<meta property="og:image:type" content="image/jpeg">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{t}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{t}">',
        f'<meta name="twitter:description" content="{d}">',
        f'<meta name="twitter:image" content="{image}">',
    ]
    if ld:
        lines.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>')
    lines.append('<!--/SEO-->')
    return ''.join('\n    ' + line for line in lines)


def refresh_seo():
    catalog, _ = load_catalog()
    lessons = {}
    if catalog:
        labels = {c['id']: c['label'] for c in catalog['categories']}
        lessons = {l['href']: lesson_desc(l, labels[l['cat']]) for l in catalog['lessons']}
    urls = []
    for page in all_pages():
        rel = page.relative_to(ROOT).as_posix()
        prefix = '' if page.parent == ROOT else '../'
        kind = 'lesson' if rel.startswith('lessons/') else 'tool' if rel.startswith('tools/') else 'page'
        text = page.read_text()
        m = DESC_META.search(text)  # əl ilə yazılmış səhifədə description SEO blokunun içindədir — əvvəl oxunur
        text = SEO_BLOCK.sub('', text)
        desc = lessons.get(rel) or (_unattr(m.group(1)) if m else '')
        text = DESC_META.sub('', text)
        tm = re.search(r'<title>([^<]*)</title>', text)
        if not tm or not desc:
            print(f'XƏBƏRDARLIQ: {rel} — <title> və ya meta description yoxdur')
            continue
        title = _unattr(tm.group(1))
        text = text[:tm.end()] + seo_block(rel, title, desc, kind, prefix) + text[tm.end():]
        if text != page.read_text():
            page.write_text(text)
        urls.append(page_url(rel))
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f'  <url><loc>{u}</loc></url>' for u in urls]
    sitemap.append('</urlset>')
    _write_if_changed(ROOT / 'sitemap.xml', '\n'.join(sitemap) + '\n')
    _write_if_changed(ROOT / 'robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n')
    print(f'SEO: {len(urls)} səhifə, sitemap.xml və robots.txt')


def _write_if_changed(path, content):
    if not path.exists() or path.read_text() != content:
        path.write_text(content)


def check_seo():
    problems = []
    titles = {}
    for page in all_pages():
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text()
        if len(SEO_BLOCK.findall(text)) != 1:
            problems.append(f'{rel}: SEO bloku yoxdur — python3 _dev/build.py')
            continue
        m = DESC_META.search(text)
        if not m or not 50 <= len(_unattr(m.group(1))) <= 220:
            problems.append(f'{rel}: meta description 50–220 simvol olmalıdır')
        if not (ROOT / og_image(rel)).exists():
            problems.append(f'{rel}: paylaşım şəkli yoxdur ({og_image(rel)}) — node _dev/og.js')
        title = re.search(r'<title>([^<]*)</title>', text).group(1)
        if title in titles:
            problems.append(f'{rel}: <title> {titles[title]} ilə eynidir')
        titles[title] = rel
    for f in ('favicon.svg', 'favicon-32.png', 'apple-touch-icon.png'):
        if not (ROOT / 'assets' / f).exists():
            problems.append(f'assets/{f} yoxdur — node _dev/og.js')
    return problems


# ---------------------------------------------------------------------------
# Təhlükəsizlik: Tailwind CSS build-də, xarici skript/şrift yoxdur, Content-Security-Policy
# ---------------------------------------------------------------------------
TAILWIND = NODE / '.bin' / 'tailwindcss'
CSP_BLOCK = re.compile(r'\n[ \t]*<!--CSP-->[\s\S]*?<!--/CSP-->')
INLINE_SCRIPT = re.compile(r'<script(\s[^>]*)?>([\s\S]*?)</script>')
# Səhifəyə görə əlavə icazələr (yalnız lazım olan səhifədə)
CSP_EXTRA = {
    'videos.html': {
        'script-src': ['https://www.youtube.com', 'https://s.ytimg.com'],   # YouTube IFrame Player API
        'frame-src': ['https://www.youtube.com'],                          # pleyer iframe-i
        'connect-src': ['https://www.youtube.com'],                        # oEmbed (video adı, playlist rejimi)
        'img-src': ['https://i.ytimg.com'],
    },
}


def build_tailwind():
    """Səhifələrdə istifadə olunan Tailwind class-larını assets/tailwind.css-ə yığır (minify)."""
    if not TAILWIND.exists():
        print('Qeyd: Tailwind CLI yoxdur (cd _dev && npm ci) — assets/tailwind.css yenilənmədi')
        return
    out = ROOT / 'assets' / 'tailwind.css'
    subprocess.run([str(TAILWIND), '-c', str(DEV / 'tailwind.config.js'), '-i', str(DEV / 'tailwind.input.css'),
                    '-o', str(out), '--minify'], check=True, capture_output=True)
    print(f'tailwind.css: {out.stat().st_size // 1024} KB')


def refresh_head_assets():
    """Tailwind CDN və Google Fonts sətirlərini silir; yerli fonts.css və tailwind.css qoşur (tailwind — sonuncu)."""
    for page in all_pages():
        prefix = '' if page.parent == ROOT else '../'
        text = page.read_text()
        new = re.sub(r'\n[ \t]*<script src="https://cdn\.tailwindcss\.com"></script>', '', text)
        new = re.sub(r'\n[ \t]*<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>', '', new)
        new = re.sub(r'\n[ \t]*<link href="https://fonts\.googleapis\.com/[^"]*" rel="stylesheet">', '', new)
        new = re.sub(r'\n[ \t]*<link rel="stylesheet" href="(?:\.\./)?assets/tailwind\.css">', '', new)
        if 'assets/fonts.css"' not in new:
            new = re.sub(r'(\n[ \t]*)(<link rel="stylesheet" href="(?:\.\./)?assets/)', rf'\1<link rel="stylesheet" href="{prefix}assets/fonts.css">\1\2', new, count=1)
        new = new.replace('\n</head>', f'\n    <link rel="stylesheet" href="{prefix}assets/tailwind.css">\n</head>', 1)
        if new != text:
            page.write_text(new)


def _inline_hashes(text):
    hashes = []
    for m in INLINE_SCRIPT.finditer(text):
        attrs = m.group(1) or ''
        if 'src=' in attrs or 'application/ld+json' in attrs:
            continue
        digest = base64.b64encode(hashlib.sha256(m.group(2).encode('utf-8')).digest()).decode()
        hashes.append(f"'sha256-{digest}'")
    return sorted(set(hashes))


def csp_policy(rel, text):
    extra = CSP_EXTRA.get(rel, {})
    d = {
        'default-src': ["'self'"],
        'script-src': ["'self'"] + _inline_hashes(text) + extra.get('script-src', []),
        # style="" atributları və səhifə daxili <style> blokları üçün 'unsafe-inline' (skript deyil — risk aşağıdır)
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", 'data:'] + extra.get('img-src', []),
        'font-src': ["'self'"],
        'connect-src': ["'self'"] + extra.get('connect-src', []),
        'frame-src': extra.get('frame-src', ["'none'"]),
        'object-src': ["'none'"],
        'base-uri': ["'self'"],
        'form-action': ["'self'"],
    }
    return '; '.join(f'{k} {" ".join(v)}' for k, v in d.items()) + '; upgrade-insecure-requests'


def refresh_csp():
    """Hər səhifəyə Content-Security-Policy (daxili skriptlərin sha256 hash-ləri ilə) və Referrer-Policy yazır.
    Ən sonda işləyir: səhifədəki skript dəyişsə, hash yenidən hesablanır."""
    for page in all_pages():
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text()
        base = CSP_BLOCK.sub('', text)
        base = re.sub(r'\n[ \t]*<meta name="referrer" content="[^"]*">', '', base)
        block = ('\n    <!--CSP-->'
                 f'\n    <meta http-equiv="Content-Security-Policy" content="{csp_policy(rel, base)}">'
                 '\n    <meta name="referrer" content="strict-origin-when-cross-origin">'
                 '\n    <!--/CSP-->')
        m = re.search(r'<meta name="viewport"[^>]*>', base)
        new = base[:m.end()] + block + base[m.end():]
        if new != text:
            page.write_text(new)


def check_security():
    problems = []
    for page in all_pages():
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text()
        for url in re.findall(r'<script[^>]+src="(https?:[^"]+)"', text):
            problems.append(f'{rel}: xarici skript ({url}) — skriptlər saytın özündən yüklənməlidir')
        for url in re.findall(r'<link[^>]+href="(https?:[^"]+)"[^>]*rel="stylesheet"|<link rel="stylesheet" href="(https?:[^"]+)"', text):
            problems.append(f'{rel}: xarici stylesheet ({"".join(url)})')
        blocks = CSP_BLOCK.findall(text)
        if len(blocks) != 1:
            problems.append(f'{rel}: CSP bloku yoxdur — python3 _dev/build.py')
            continue
        m = re.search(r'content="([^"]+)"', blocks[0])
        if not m or m.group(1) != csp_policy(rel, CSP_BLOCK.sub('', text)):
            problems.append(f'{rel}: CSP köhnədir (daxili skript dəyişib) — python3 _dev/build.py')
    if not (ROOT / 'assets' / 'tailwind.css').exists():
        problems.append('assets/tailwind.css yoxdur — cd _dev && npm ci && cd .. && python3 _dev/build.py')
    return problems


def version_sprite_refs():
    h = hashlib.md5(SPRITE.read_bytes()).hexdigest()[:8]
    pat = re.compile(r"icons\.svg(?:\?v=[0-9a-f]+)?(?=[#'\"])")
    files = all_pages() + sorted((ROOT / 'assets').glob('*.js'))
    for f in files:
        text = f.read_text()
        new = pat.sub(f'icons.svg?v={h}', text)
        if new != text:
            f.write_text(new)
    print(f'ikon sprite versiyası: {h}')



# ---------------------------------------------------------------------------
# Link yoxlaması
# ---------------------------------------------------------------------------
# Dashboard-da JavaScript ilə açılan tab keçidləri (#ccna və s.) id deyil — yoxlanılmır
JS_ROUTE_PAGES = {'index.html', 'lessons.html', 'videos.html'}
SKIP_SCHEMES = ('http://', 'https://', 'mailto:', 'tel:', 'javascript:', 'data:', '//')


def _ids(path, cache={}):
    if path not in cache:
        cache[path] = set(re.findall(r'\sid="([^"]+)"', path.read_text()))
    return cache[path]


def check_internal_links():
    """Bütün səhifələrdəki href/src keçidlərinin mövcud fayla və id-yə aparmasını yoxlayır."""
    problems = []
    for page in all_pages():
        text = page.read_text()
        for attr, url in re.findall(r'\s(href|src)="([^"]*)"', text):
            if not url or url.startswith(SKIP_SCHEMES) or '${' in url or url.startswith('{'):
                continue
            path_part, _, anchor = url.partition('#')
            path_part = path_part.split('?', 1)[0]
            target = (page.parent / path_part).resolve() if path_part else page
            where = page.relative_to(ROOT)
            if not target.exists():
                problems.append(f'qırıq link: {where} → {url}')
                continue
            if anchor and target.suffix == '.html' and target.name not in JS_ROUTE_PAGES:
                if anchor not in _ids(target):
                    problems.append(f'mövcud olmayan bölmə (#{anchor}): {where} → {url}')
            if anchor and target.suffix == '.svg' and not re.search(rf'<symbol id="{re.escape(anchor)}"', target.read_text()):
                problems.append(f'ikon yoxdur: {where} → {url}')
    return problems


def check_external_links():
    """Xarici linkləri (http/https) yoxlayır. Şəbəkə tələb edir; yalnız xəbərdarlıq üçündür."""
    import concurrent.futures
    import urllib.request
    urls = {}
    for f in all_pages() + [ROOT / 'assets/catalog.js']:
        for url in re.findall(r'https?://[^\s"\'<>`)]+', f.read_text()):
            if any(h in url for h in ('fonts.googleapis', 'fonts.gstatic', 'cdn.tailwindcss', 'cdn.jsdelivr',
                                      'w3.org', 'localhost', '127.0.0.1', '10.0.', 'example.az', 'example.com')):
                continue
            urls.setdefault(url.rstrip('.,;'), f.relative_to(ROOT))

    def probe(url):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (link-check)'})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return url, r.status
        except Exception as e:  # noqa: BLE001
            return url, getattr(e, 'code', None) or type(e).__name__

    bad = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        for url, status in ex.map(probe, sorted(urls)):
            # 401/403/429 — saytlar botları tez-tez bloklayır, qırıq sayılmır
            if not (isinstance(status, int) and (status < 400 or status in (401, 403, 405, 429, 999))):
                bad.append(f'{status}  {url}  ({urls[url]})')
    print(f'{len(urls)} xarici link yoxlandı, {len(bad)} problem')
    for b in bad:
        print('  -', b)
    return not bad

# ---------------------------------------------------------------------------
# Yoxlamalar
# ---------------------------------------------------------------------------
def load_catalog():
    """assets/catalog.js-i node ilə oxuyur (node yoxdursa yoxlama ötürülür)."""
    script = ("global.window={};require(process.argv[1]);require(process.argv[2]);require(process.argv[3]);"
              "console.log(JSON.stringify({c:window.CATALOG,q:window.QUESTIONS,k:window.CAREERS}))")
    try:
        out = subprocess.run(['node', '-e', script, str(ROOT / 'assets/catalog.js'), str(ROOT / 'assets/questions.js'),
                              str(ROOT / 'assets/careers.js')],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        print('Qeyd: node tapılmadı və ya kataloq oxunmadı — kataloq yoxlaması ötürüldü', getattr(e, 'stderr', ''))
        return None, None
    data = json.loads(out)
    data['c']['careers'] = data['k']
    return data['c'], data['q']


def check():
    problems = []
    symbols = set(re.findall(r'<symbol id="([a-z0-9-]+)"', SPRITE.read_text()))
    used = {}
    for f in all_pages() + sorted((ROOT / 'assets').glob('*.js')):
        text = f.read_text()
        # HTML-dəki <use href="...#ad"> və JS-dəki icon('ad') / ico('ad') çağırışları
        for name in re.findall(r'icons\.svg(?:\?v=[0-9a-f]+)?#([a-z0-9-]+)', text) + \
                re.findall(r'\bico(?:n)?\([\'"]([a-z0-9-]+)[\'"]\)', text) + \
                re.findall(r"\bicon: '([a-z0-9-]+)'", text):
            used.setdefault(name, f.relative_to(ROOT))
    for src in SRC.glob('*.html'):
        text = src.read_text()
        for name in re.findall(r'\{\{i:([a-z0-9-]+)\}\}', text) + re.findall(r'icon="([a-z0-9-]+)"', text):
            used.setdefault(name, src.relative_to(ROOT))
    catalog, questions = load_catalog()
    if catalog:
        for item in catalog['categories']:
            used.setdefault(item['icon'], 'assets/catalog.js')
        hrefs = {l['href'] for l in catalog['lessons']}
        for path in catalog.get('careers') or []:
            used.setdefault(path['icon'], 'assets/careers.js')
            for stage in path['stages']:
                for slug in stage['lessons']:
                    if f'lessons/{slug}.html' not in hrefs:
                        problems.append(f'karyera yolunda ({path["id"]}) naməlum dərs: {slug}')
        keys = set()
        for lesson in catalog['lessons']:
            used.setdefault(lesson['icon'], 'assets/catalog.js')
            if not (ROOT / lesson['href']).exists():
                problems.append(f'kataloqda fayl yoxdur: {lesson["href"]}')
            if lesson['quiz'] in keys:
                problems.append(f'təkrarlanan quiz açarı: {lesson["quiz"]}')
            keys.add(lesson['quiz'])
            if lesson['cat'] not in {c['id'] for c in catalog['categories']}:
                problems.append(f'naməlum kateqoriya: {lesson["cat"]} ({lesson["href"]})')
            if lesson['cat'] == 'ccna' and (ROOT / lesson['href']).exists() \
                    and 'id="lab"' not in (ROOT / lesson['href']).read_text():
                problems.append(f'CCNA dərsinin lab-ı yoxdur: {lesson["href"]} → _dev/labs/')
        counts = {}
        for q in questions:
            counts[q['t']] = counts.get(q['t'], 0) + 1
            if q['t'] not in keys:
                problems.append(f'sualın mövzusu kataloqda yoxdur: {q["t"]}')
            if len(q['a']) != 4 or len(set(q['a'])) != 4:
                problems.append(f'sualda 4 fərqli cavab olmalıdır: {q["q"][:50]}')
        for k in keys:
            if counts.get(k, 0) < 2:
                problems.append(f'mövzuda 2-dən az sual var: {k}')
        listed = {l['href'] for l in catalog['lessons']}
        for f in (ROOT / 'lessons').glob('*.html'):
            if f'lessons/{f.name}' not in listed:
                problems.append(f'dərs faylı kataloqda yoxdur: lessons/{f.name}')
        print(f'kataloq: {len(catalog["categories"])} kateqoriya, {len(catalog["lessons"])} dərs, {len(questions)} sual')
    problems += check_internal_links()
    problems += check_seo()
    problems += check_security()
    for name, where in sorted(used.items()):
        if name not in symbols:
            problems.append(f'ikon sprite-da yoxdur: {name} ({where}) → python3 _dev/build.py icons add {name}')
    if problems:
        print('\nPROBLEMLƏR:')
        for p in problems:
            print('  -', p)
        return False
    print('yoxlama: problem yoxdur')
    return True


def main(argv):
    if argv[:2] == ['icons', 'add'] and len(argv) > 2:
        icons_add(argv[2:])
        version_sprite_refs()
        return 0
    if argv == ['check']:
        return 0 if check() else 1
    if argv == ['links', '--external']:
        return 0 if check_external_links() else 1
    if argv:
        print(__doc__)
        return 2
    build_lessons()
    refresh_navs()
    refresh_footers()
    refresh_about()
    version_sprite_refs()
    refresh_seo()
    refresh_head_assets()
    build_tailwind()
    refresh_csp()
    return 0 if check() else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
