#!/usr/bin/env node
// Open Graph (paylaşım) şəkilləri — Telegram, WhatsApp, LinkedIn, Facebook, X-də linkin önizləməsi.
//
// İstifadə (repo kökündən):
//     node _dev/og.js            # yalnız yeni və ya adı/izahı dəyişmiş səhifələrin şəkillərini yaradır
//     node _dev/og.js --force    # hamısını yenidən yaradır
//
// Tələb: Playwright + Chromium (npm i -g playwright && npx playwright install chromium).
// Nəticə: assets/og/<səhifə yolu>.jpg (1200×630). build.py hər səhifənin <head>-inə uyğun şəkli yazır
// və "check" şəkli olmayan səhifəni göstərir. Dərs əlavə edəndə: python3 _dev/build.py && node _dev/og.js
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'assets', 'og');
const MANIFEST = path.join(__dirname, 'og-manifest.json');
const FORCE = process.argv.includes('--force');

function loadPlaywright() {
    for (const m of ['playwright', '/opt/node22/lib/node_modules/playwright']) {
        try { return require(m); } catch (e) { /* növbəti */ }
    }
    console.error('Playwright tapılmadı: npm i -g playwright && npx playwright install chromium');
    process.exit(2);
}

global.window = {};
for (const f of ['catalog.js', 'careers.js', 'tools-catalog.js']) require(path.join(ROOT, 'assets', f));
const { CATALOG, CAREERS, TOOLS } = global.window;

const sprite = fs.readFileSync(path.join(ROOT, 'assets', 'icons.svg'), 'utf8');
function svg(name, cls) {
    const m = sprite.match(new RegExp(`<symbol id="${name}" viewBox="([^"]+)">([\\s\\S]*?)</symbol>`));
    if (!m) throw new Error('ikon yoxdur: ' + name);
    const brand = name.startsWith('brand-');
    const paint = brand ? 'fill="currentColor"' : 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"';
    return `<svg class="${cls}" viewBox="${m[1]}" ${paint}>${m[2]}</svg>`;
}
// Inter şrifti lokal fayldan (npm: @fontsource/inter) — brauzerin internetə çıxışı olmasa da düzgün görünür
const FONT_DIR = path.join(__dirname, 'node_modules', '@fontsource', 'inter', 'files');
if (!fs.existsSync(FONT_DIR)) { console.error('Şrift yoxdur: cd _dev && npm install'); process.exit(2); }
const FONTS = [500, 600, 700, 800].map(w => ['latin', 'latin-ext'].map(sub => {
    const data = fs.readFileSync(path.join(FONT_DIR, `inter-${sub}-${w}-normal.woff2`)).toString('base64');
    return `@font-face { font-family: Inter; font-weight: ${w}; src: url(data:font/woff2;base64,${data}) format('woff2'); }`;
}).join('\n')).join('\n');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// ---- Hansı səhifə üçün hansı kart -------------------------------------------------
const cats = Object.fromEntries(CATALOG.categories.map(c => [c.id, c]));
const counts = {};
CATALOG.lessons.forEach(l => { counts[l.cat] = (counts[l.cat] || 0) + 1; });
const total = CATALOG.lessons.length;

const cards = [
    { page: 'index.html', eyebrow: 'Pulsuz IT təhsili', title: 'Cavad Mikayil Təlim Portalı', icon: 'graduation-cap',
      desc: `CCNA, Linux, Server, Cloud, DevOps, Təhlükəsizlik və AI üzrə ${total} interaktiv dərs, lab-lar, quiz və CCNA imtahan simulyatoru.`,
      chips: [`${total} dərs`, `${CATALOG.categories.length} istiqamət`, 'Quiz və lab'] },
    { page: 'tools.html', eyebrow: 'Tools', title: 'Şəbəkə və IT alətləri', icon: 'toolbox',
      desc: 'Cisco CLI simulyatoru, CCNA imtahan rejimi, subnet, VLSM, IPv6 və wildcard kalkulyatorları, flashcard-lar və port arayışı.',
      chips: [`${TOOLS.length} alət`, 'Brauzerdə işləyir', 'Qeydiyyatsız'] },
    { page: 'careers.html', eyebrow: 'Karyera yolları', title: 'IT-də hansı peşə sizin üçündür?', icon: 'route',
      desc: CAREERS.map(c => c.title).join(', ') + ' — addım-addım dərslər, sertifikatlar və irəliləyiş.',
      chips: [`${CAREERS.length} peşə`, 'Sertifikatlar', 'İrəliləyiş'] },
    { page: 'links.html', eyebrow: 'Faydalı linklər', title: 'IT öyrənmək üçün seçilmiş mənbələr', icon: 'library',
      desc: 'Rəsmi sənədlər, pulsuz kurslar, lab platformaları, simulyatorlar və sertifikat hazırlığı üçün yoxlanılmış keçidlər.',
      chips: ['Rəsmi sənədlər', 'Pulsuz kurslar', 'Lab-lar'] },
    { page: 'about.html', eyebrow: 'Haqqında', title: 'Cavad Mikayil', icon: 'user-round',
      desc: 'İnformasiya Texnologiyaları üzrə beynəlxalq sertifikatlı təlimçi, şəbəkə təhlükəsizliyi mühəndisi.',
      chips: ['Təlimçi', 'Network Security', 'YouTube'] },
];
for (const t of TOOLS) {
    if (!t.href.startsWith('tools/')) continue;
    cards.push({ page: t.href, eyebrow: 'Tools · ' + t.group, title: t.title, icon: t.icon, desc: t.desc,
                 chips: ['Pulsuz alət', 'Brauzerdə işləyir'] });
}
for (const l of CATALOG.lessons) {
    const c = cats[l.cat];
    const chips = [c.short, 'Dərs vəsaiti', 'Quiz'];
    if (l.cat === 'ccna') chips.push('Lab');
    cards.push({ page: l.href, eyebrow: `${c.label} · ${l.tag}`, title: l.title, icon: l.icon, desc: l.desc, chips });
}

// ---- Şablon -----------------------------------------------------------------------
function html(card) {
    return `<!DOCTYPE html><html lang="az"><head><meta charset="utf-8">
<style>
${FONTS}
* { box-sizing: border-box; margin: 0; }
html, body { width: 1200px; height: 630px; overflow: hidden; }
body { font-family: Inter, 'DejaVu Sans', sans-serif; color: #fafafa; background: #0a0a0a; position: relative; }
.glow { position: absolute; width: 760px; height: 760px; right: -220px; top: -260px; border-radius: 50%;
  background: radial-gradient(circle, rgba(245,158,11,.30), rgba(234,88,12,.10) 45%, transparent 70%); }
.wrap { position: absolute; inset: 0; padding: 56px 64px 0; display: flex; flex-direction: column; }
.brand { display: flex; align-items: center; gap: 16px; font-size: 26px; font-weight: 700; letter-spacing: -.01em; }
.mark { width: 56px; height: 56px; border-radius: 14px; background: #f59e0b; color: #0a0a0a;
  display: flex; align-items: center; justify-content: center; }
.mark svg { width: 32px; height: 32px; }
.main { flex: 1; min-height: 0; display: flex; align-items: center; gap: 48px; }
.text { flex: 1; min-width: 0; }
.eyebrow { display: inline-block; max-width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  font-size: 22px; font-weight: 600; color: #fbbf24; background: #2a2113; border: 1.5px solid #78350f;
  padding: 8px 18px; border-radius: 999px; margin-bottom: 26px; }
h1 { font-size: 68px; line-height: 1.08; font-weight: 800; letter-spacing: -.025em; margin-bottom: 22px; }
p { font-size: 27px; line-height: 1.42; color: #a3a3a3; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.art { width: 290px; height: 290px; flex: none; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  background: radial-gradient(circle at 35% 30%, #262626, #0a0a0a 70%); border: 2px solid #404040;
  box-shadow: 0 0 0 14px rgba(245,158,11,.08), 0 0 0 15px rgba(245,158,11,.35); color: #f59e0b; }
.art svg { width: 150px; height: 150px; stroke-width: 1.6; }
.foot { height: 104px; display: flex; align-items: center; justify-content: space-between; border-top: 1.5px solid #262626; }
.chips { display: flex; gap: 12px; }
.chip { font-size: 21px; font-weight: 600; color: #e5e5e5; background: #171717; border: 1.5px solid #333333; padding: 8px 16px; border-radius: 10px; }
.author { font-size: 21px; font-weight: 600; color: #737373; }
.author b { color: #d4d4d4; }
.bar { position: absolute; left: 0; right: 0; bottom: 0; height: 10px; background: linear-gradient(90deg, #f59e0b, #ea580c); }
</style></head><body>
<div class="glow"></div>
<div class="wrap">
  <div class="brand"><span class="mark">${svg('graduation-cap', '')}</span>Cavad Mikayil Təlim Portalı</div>
  <div class="main">
    <div class="text">
      <div class="eyebrow">${esc(card.eyebrow)}</div>
      <h1 id="t">${esc(card.title)}</h1>
      <p>${esc(card.desc)}</p>
    </div>
    <div class="art">${svg(card.icon, '')}</div>
  </div>
  <div class="foot">
    <div class="chips">${card.chips.map(c => `<span class="chip">${esc(c)}</span>`).join('')}</div>
    <div class="author">Müəllif: <b>Cavad Mikayil</b></div>
  </div>
</div>
<div class="bar"></div>
</body></html>`;
}

(async () => {
    const manifest = fs.existsSync(MANIFEST) ? JSON.parse(fs.readFileSync(MANIFEST, 'utf8')) : {};
    const hash = c => crypto.createHash('md5').update(JSON.stringify(c) + html.toString()).digest('hex').slice(0, 12);
    const todo = cards.filter(c => {
        const file = path.join(OUT, c.page.replace(/\.html$/, '.jpg'));
        return FORCE || manifest[c.page] !== hash(c) || !fs.existsSync(file);
    });
    const icons = [['favicon-32.png', 32], ['apple-touch-icon.png', 180]]
        .filter(([f]) => FORCE || !fs.existsSync(path.join(ROOT, 'assets', f)));
    if (!todo.length && !icons.length) { console.log(`og: ${cards.length} şəkil aktualdır`); return; }

    const { chromium } = loadPlaywright();
    const exe = ['/opt/pw-browsers/chromium'].find(p => fs.existsSync(p));
    const browser = await chromium.launch(exe ? { executablePath: exe } : {});
    const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
    for (const c of todo) {
        const file = path.join(OUT, c.page.replace(/\.html$/, '.jpg'));
        fs.mkdirSync(path.dirname(file), { recursive: true });
        await page.setContent(html(c), { waitUntil: 'networkidle' });
        await page.evaluate(async () => {
            await document.fonts.ready;
            // Uzun başlıq əvvəlcə 2 sətrə sığana qədər (52px-ə qədər), sonra blok sahəyə sığana qədər kiçildilir
            const t = document.getElementById('t'), text = t.parentElement, main = text.parentElement;
            let s = 68;
            const lines = () => Math.round(t.getBoundingClientRect().height / (s * 1.08));
            while (lines() > 2 && s > 52) { s -= 2; t.style.fontSize = s + 'px'; }
            while (text.scrollHeight > main.clientHeight - 16 && s > 40) { s -= 2; t.style.fontSize = s + 'px'; }
        });
        await page.screenshot({ path: file, type: 'jpeg', quality: 80 });
        manifest[c.page] = hash(c);
    }
    // Favicon-un PNG variantları (assets/favicon.svg-dən): köhnə brauzerlər və iOS ana ekranı üçün
    const favicon = fs.readFileSync(path.join(ROOT, 'assets', 'favicon.svg'), 'utf8');
    for (const [f, size] of icons) {
        const p = await browser.newPage({ viewport: { width: size, height: size } });
        // iOS ikonu özü yuvarlaqlaşdırır — apple-touch-icon kvadrat olmalıdır
        const src = size > 64 ? favicon.replace('rx="7"', 'rx="0"') : favicon;
        await p.setContent(`<body style="margin:0;background:transparent">${src.replace('<svg ', `<svg width="${size}" height="${size}" style="display:block" `)}</body>`);
        await p.screenshot({ path: path.join(ROOT, 'assets', f), omitBackground: true });
        await p.close();
    }
    await browser.close();
    const pages = new Set(cards.map(c => c.page));
    for (const k of Object.keys(manifest)) if (!pages.has(k)) delete manifest[k];
    fs.writeFileSync(MANIFEST, JSON.stringify(manifest, Object.keys(manifest).sort(), 1) + '\n');
    console.log(`og: ${todo.length} şəkil yaradıldı (cəmi ${cards.length})`);
})();
