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
  5. Yoxlayır: istifadə olunan ikonlar sprite-da var, kataloqdakı dərs faylları mövcuddur,
     hər dərsin quiz sualı var.
"""
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

NAV = [
    ('home', 'Ana Səhifə', 'index.html', 'house'),
    ('ccna', 'CCNA', 'index.html#ccna', 'graduation-cap'),
    ('tools', 'Tools', 'tools.html', 'toolbox'),
    ('links', 'Faydalı Linklər', 'links.html', 'library'),
    ('about', 'Haqqında', 'about.html', 'user-round'),
]

# Hansı səhifədə menyunun hansı bəndi aktivdir (fayl adı → NAV id)
NAV_ACTIVE = {'index.html': 'home', 'tools.html': 'tools', 'videos.html': 'videos',
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
def lesson_head(attrs, extra_head=''):
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
    <title>{attrs["title"]} — Dərs Vəsaiti</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/lesson.css">
    <link rel="stylesheet" href="../assets/theme.css">{extra_head}
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
    labs = load_labs()
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
        m = re.search(r'<!--PAGE (.*?)-->\n?', text, re.S)
        text = text[:m.start()] + lesson_head(attrs, blocks['HEAD']) + text[m.end():]
        if '<!--END-->' not in text:
            raise SystemExit(f'{src.name}: <!--END--> markeri yoxdur')
        text = text.replace('<!--END-->', lesson_end(blocks['FOOT']))
        text = re.sub(r'\{\{i:([a-z0-9-]+)\}\}', lambda mm: icon('../', mm.group(1)), text)
        if '{{i:' in text:
            raise SystemExit(f'{src.name}: açılmamış {{{{i:...}}}} markeri')
        (OUT / src.name).write_text(text)
        count += 1
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
JS_ROUTE_PAGES = {'index.html'}
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
    script = ("global.window={};require(process.argv[1]);require(process.argv[2]);"
              "console.log(JSON.stringify({c:window.CATALOG,q:window.QUESTIONS}))")
    try:
        out = subprocess.run(['node', '-e', script, str(ROOT / 'assets/catalog.js'), str(ROOT / 'assets/questions.js')],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        print('Qeyd: node tapılmadı və ya kataloq oxunmadı — kataloq yoxlaması ötürüldü', getattr(e, 'stderr', ''))
        return None, None
    data = json.loads(out)
    return data['c'], data['q']


def check():
    problems = []
    symbols = set(re.findall(r'<symbol id="([a-z0-9-]+)"', SPRITE.read_text()))
    used = {}
    for f in all_pages() + sorted((ROOT / 'assets').glob('*.js')):
        for name in re.findall(r'icons\.svg(?:\?v=[0-9a-f]+)?#([a-z0-9-]+)', f.read_text()):
            used.setdefault(name, f.relative_to(ROOT))
    for src in SRC.glob('*.html'):
        text = src.read_text()
        for name in re.findall(r'\{\{i:([a-z0-9-]+)\}\}', text) + re.findall(r'icon="([a-z0-9-]+)"', text):
            used.setdefault(name, src.relative_to(ROOT))
    catalog, questions = load_catalog()
    if catalog:
        for item in catalog['categories']:
            used.setdefault(item['icon'], 'assets/catalog.js')
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
    return 0 if check() else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
