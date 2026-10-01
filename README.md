# Cavad Mikayil Təlim Portalı

Şəbəkə, CCNA, Server, Helpdesk, Təhlükəsizlik və AI üzrə Azərbaycan dilində pulsuz təlim portalı.

**Canlı sayt:** https://portal.cavadmikayil.com/ (köhnə ünvan cavadmikayil.github.io/project2 avtomatik bura yönləndirilir)

| Kateqoriya | Dərs sayı |
|---|---|
| CCNA Dərsləri | 50 |
| Server Dərsləri | 10 |
| Helpdesk Dərsləri | 10 |
| Təhlükəsizlik Dərsləri | 10 |
| AI Dərsləri | 10 |

Bundan əlavə: izahlı quiz (270+ sual), Subnet Kalkulyatoru, Faydalı Linklər və Haqqında səhifələri.

---

## 1. Texnologiyalar

| Nə | Necə |
|---|---|
| Hosting | **GitHub Pages** — `main` branch-ə push edilən kimi sayt avtomatik yenilənir |
| Səhifələr | Sadə **HTML + CSS + JavaScript** (framework, server, verilənlər bazası yoxdur) |
| Dizayn | **Tailwind CSS** (CDN) + `assets/theme.css`, `assets/lesson.css`; rənglər yalnız ağ, qara və sarı-narıncı |
| İkonlar | Bir **SVG sprite** faylı: `assets/icons.svg` — [Lucide](https://lucide.dev) (ISC) və sosial şəbəkələr üçün Font Awesome Free brand ikonları (CC BY 4.0). Emoji istifadə olunmur |
| Tələbə profili | Parolsuz lokal profil — ad, irəliləyiş və test nəticələri brauzerin `localStorage`-ində saxlanılır (`assets/student.js`) |
| Tema | İşıqlı / qaranlıq rejim (`assets/theme.js`) |
| Build aləti | `_dev/build.py` (Python 3) — dərs mənbələrini HTML səhifələrə çevirir və yoxlamalar edir |

`_dev/` qovluğu saytda **dərc olunmur** (GitHub Pages `_` ilə başlayan qovluqları buraxır).

## 2. Qovluq quruluşu

```
index.html                 Dashboard: giriş, kateqoriya tabları, dərs kartları, statistika
lessons.html               Dərslər: bütün dərslərin başlıqları; klikləyəndə bölmələr, quiz, lab, video
links.html                 Faydalı səhifəsi (linklər faylın içindəki CATEGORIES siyahısındadır)
about.html                 Haqqında + Bələdçi (portal necə işləyir) + məlumatların yedəyi/bərpası/silinməsi
lessons/*.html             Dərs səhifələri (hazır, saytda açılan fayllar)
careers.html               Karyera yolları (məlumat assets/careers.js-dədir)
videos.html                Video Dərslər — YouTube kursları (siyahı assets/videos.js-dədir)
tools.html                 Tools səhifəsi (alətlərin siyahısı assets/tools-catalog.js-dədir)
tools/*.html               Alətlər: quiz, CCNA imtahan simulyatoru, CLI simulyatoru, flashcard-lar,
                           subnet, VLSM, IPv6, wildcard kalkulyatorları, port arayışı
assets/catalog.js          Bütün kateqoriyalar və dərslərin siyahısı (dashboard və quiz buradan oxuyur)
assets/questions.js        Bütün quiz sualları
assets/lesson-sections.js  Hər dərsin bölmələri (build.py yaradır — Dərslər səhifəsi üçün)
assets/notes/<dərs>/       Müəllimin Qeydləri dərslərinin şəkilləri (WebP, Word fayllarından çıxarılıb)
assets/glossary.js         IT terminləri lüğəti (Tools → IT Terminləri Lüğəti): termin, tam ad, izah, kateqoriya
assets/glossary-index.js   Hər terminin keçdiyi dərslər (build.py dərs mətnlərindən özü tapır)
assets/icons.svg           İkon sprite-ı
assets/theme.css/.js       Ümumi dizayn, menyu, footer, qaranlıq rejim
assets/lesson.css/.js      Dərs komponentləri (kartlar, cədvəllər, tab-lar, "Kopyala" düyməsi)
assets/student.js          Tələbə profilləri (localStorage)
assets/og/**.jpg           Paylaşım (Open Graph) şəkilləri — hər səhifə üçün, node _dev/og.js yaradır
assets/favicon.svg (+png)  Sayt ikonu
sitemap.xml, robots.txt    Axtarış sistemləri üçün (build.py yaradır)
_dev/build.py              Build aləti
_dev/og.js                 Paylaşım şəkillərinin generatoru (Playwright)
_dev/lessons/*.html        Dərslərin mənbə faylları (dərsi burada yazırsınız)
_dev/labs/*.py             CCNA lab tapşırıqları (build dərsə əlavə edir)
_dev/TEMPLATE-lesson.html  Yeni dərs üçün şablon
```

## 3. Sayt necə işləyir?

1. `index.html` açılır → `assets/student.js` tələbə profilini yoxlayır, yoxdursa giriş formu göstərilir.
2. Dashboard `assets/catalog.js`-dəki `CATEGORIES` və `lessons` siyahısından tabları, bölmə çiplərini və dərs kartlarını qurur. Kataloqdakı sıra = tövsiyə olunan öyrənmə ardıcıllığı.
3. "Oxudum" işarələri və quiz nəticələri tələbənin profilinə (localStorage) yazılır — başqa brauzerdə görünmür.
4. `tools/quiz.html` mövzuları kataloqdan, sualları `assets/questions.js`-dən götürür. Hər dərsin `quiz` açarı suallardakı `t` sahəsi ilə eynidir.
   `tools/exam.html` (CCNA imtahan simulyatoru) eyni bankdan CCNA suallarını dərsin `tag`-ına görə 6 imtahan bölməsinə ayırır və çəkilərə uyğun (20/20/25/10/15/10%) seçir — yeni CCNA sualı əlavə etdikdə imtahan avtomatik zənginləşir.
5. `index.html#server`, `#helpdesk`, `#security`, `#ai`, `#ccna` — birbaşa həmin tabı açır.

## 4. Kompüterdə işə salmaq

```bash
git clone https://github.com/cavadmikayil/project2.git
cd project2
python3 -m http.server 8000
# brauzerdə: http://localhost:8000
```

`index.html`-i birbaşa fayl kimi (`file://`) açmaq da işləyir, amma yerli server daha etibarlıdır.

## 5. Yeni dərs necə əlavə olunur?

1. **Şablonu kopyalayın:** `_dev/TEMPLATE-lesson.html` → `_dev/lessons/linux-networking.html` (fayl adı kiçik hərflərlə, tire ilə).
2. **Mətni yazın.** Yuxarıdakı `<!--PAGE ...-->` markerində `title`, `icon`, `badge` (məs. `Server · Linux`) və `nav` doldurun. Hazır komponentlər şablondadır: kartlar, cədvəl, addımlar, qeyd qutusu, kod bloku, tab-lar. Şablondakı şərh blokunu silin.
3. **Kataloqa əlavə edin** — `assets/catalog.js`-də uyğun kateqoriyanın sonuna bir sətir:
   ```js
   {"cat": "server", "title": "Linux Şəbəkə Konfiqurasiyası", "desc": "Qısa izah...", "icon": "network", "tag": "Linux", "href": "lessons/linux-networking.html", "quiz": "linuxnet"},
   ```
   `quiz` açarı unikal olmalıdır; `tag` dashboard-dakı bölmə çipinin adıdır.
4. **Quiz sualları** (ən azı 6) — `assets/questions.js`-in sonuna:
   ```js
   { t: 'linuxnet', q: 'Sual mətni?', a: ['DÜZGÜN cavab', 'səhv 1', 'səhv 2', 'səhv 3'], e: 'İzah.' },
   ```
   İlk cavab həmişə düzgün olandır — quiz cavabları özü qarışdırır.
5. **Build edin:**
   ```bash
   python3 _dev/build.py
   ```
   Skript dərsi `lessons/` qovluğuna yazır, footer-ləri yeniləyir və yoxlayır. Sonda `yoxlama: problem yoxdur` görməlisiniz. Problem varsa, nə edəcəyinizi yazır (məs. çatışmayan ikon).
6. **Paylaşım şəkli:** `node _dev/og.js` — yeni dərsin Telegram/WhatsApp/LinkedIn önizləmə şəklini yaradır (bölmə 8a). Unudulsa, `build.py` xəbər verir.
7. **Yoxlayın** (`python3 -m http.server 8000`) və **publish edin** (bölmə 9).

> Bütün 150 dərsin mənbəyi `_dev/lessons/` qovluğundadır. `lessons/` qovluğundakı faylları birbaşa redaktə etməyin — növbəti build dəyişikliyi silər.
>
> Dərsə xas CSS və ya JavaScript lazımdırsa (məs. qrafik, axtarış), mənbə faylına iki istəyə bağlı blok əlavə edin:
> ```html
> <!--HEAD-->
>     <style> .menim-klasim { ... } </style>
>     <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
> <!--/HEAD-->
> ...
> <!--END-->
> <!--FOOT-->
>     <script> /* lesson.js və theme.js-dən sonra işləyir */ </script>
> <!--/FOOT-->
> ```
> Nümunələr: `dynamic-routing.html` (Chart.js qrafiki), `cisco-commands.html` (axtarışlı əmr siyahısı).

### CCNA lab tapşırıqları

Hər CCNA dərsinin sonunda **Lab** bölməsi var. Lab-lar `_dev/labs/` qovluğundakı Python fayllarında məlumat kimi saxlanılır (`fundamentals.py`, `access.py`, `connectivity.py`, `services.py`, `security.py`, `management.py`); build onları dərsin fayl adına (`slug`) görə dərsin sonuna əlavə edir və menyuya "Lab" linki qoyur.

```python
{
    'slug': 'ospf',                       # _dev/lessons/ospf.html
    'title': 'Single-Area OSPF',
    'goal': 'Nə öyrəniləcək',
    'tool': 'Cisco Packet Tracer',
    'time': '45 dəq', 'level': 'Orta',    # Başlanğıc / Orta / Çətin
    'topology': '''ASCII sxem''',          # istəyə bağlı
    'addressing': [['Cihaz', 'IP'], ['R1', '10.0.0.1/24']],   # istəyə bağlı, ilk sətir başlıqdır
    'tasks': ['Addım 1', 'Addım 2'],      # HTML (<code>, <strong>) olar
    'verify': '''show ip ospf neighbor''', # istəyə bağlı
    'expect': ['Uğur meyarı'],             # istəyə bağlı
    'solution': '''konfiqurasiya''',       # istəyə bağlı — səhifədə gizli açılır
}
```

"Labı bitirdim" düyməsi tələbənin brauzerində saxlanılır və dashboard-dakı kartda göstərilir. `build.py check` hər CCNA dərsində lab olduğunu yoxlayır.

## 6. Yeni kateqoriya

`assets/catalog.js`-də `categories` siyahısına əlavə edin:

```js
{"id": "devops", "label": "DevOps Dərsləri", "short": "DevOps", "icon": "workflow", "desc": "Qısa izah."},
```

Dərslərdə `"cat": "devops"` yazın. Dərs səhifəsindəki "Portal" düyməsinin bu taba qayıtması üçün `_dev/build.py`-dəki `BADGE_TO_CATEGORY`-yə `'DevOps': 'devops'` əlavə edin və badge-i `DevOps · ...` kimi yazın.

### Karyera yolları

`assets/careers.js`-də 4 yol var (Helpdesk, Şəbəkə mühəndisi, Sistem administratoru, SOC analitiki). Hər yolun mərhələləri dərs fayllarının adları ilə yazılır:

```js
{ title: 'Routing', lessons: ['router-basics', 'static-routing', 'ospf'] }
```

İrəliləyiş tələbənin "Oxudum" qeydlərindən hesablanır; seçilmiş yol dashboard-da göstərilir. `build.py check` yollardakı hər dərsin kataloqda olduğunu yoxlayır — yeni yol əlavə etmək üçün eyni formatda bir obyekt yazmaq kifayətdir.

### Video Dərslər (YouTube kursları)

Kurslar və videolar `assets/videos.js`-dədir (13 kurs, 257 video). Fayl Markdown siyahısından yaradılır:

```bash
python3 _dev/videos_import.py Kurslar.md
```

Markdown formatı — hər kurs üçün başlıq, playlist linki və videolar sırası ilə:

```markdown
## 3. Fortigate Firewall Dərsləri
🔗 [Kursa keçid](https://www.youtube.com/playlist?list=PL...)
1. [Videonun adı](https://www.youtube.com/watch?v=VIDEO_ID&list=PL...)
```

Kursun qısa adı (linkdə `videos.html#fortigate`), izahı, ikonu, sırası və uyğun dərs vəsaitləri `_dev/videos_import.py`-dəki `COURSE_META` və `ORDER`-dədir. Yeni video çəkəndə siyahını yeniləyib skripti yenidən işlədin.

Hər video öz ID-si ilə ayrıca açılır (YouTube-un playlist funksiyasından asılı deyil); iframe `referrerpolicy="strict-origin-when-cross-origin"` və `origin` ilə yaradılır — YouTube bunları tələb edir, olmasa "Error 153" verir. Tələbə "Növbəti" ilə irəliləyir, "Baxdım" ilə qeyd edir; sona qədər baxılan video avtomatik qeyd olunur və növbəti açılır, portal qaldığı videodan davam edir. Eyni video bir neçə kursdadırsa, "Baxdım" hamısında görünür.

### IT terminləri lüğəti

Yeni termin: `assets/glossary.js`-ə bir sətir — `{ t: 'VLAN', f: 'Virtual Local Area Network', d: 'Qısa Azərbaycanca izah', c: 'net' }` — və `python3 _dev/build.py`. Terminin hansı dərslərdə keçdiyini build özü tapır (dərsin adında keçənlər əvvəl, sonra ən çox işləndiyi dərslər); Azərbaycan şəkilçiləri də nəzərə alınır (routerlər, switch-ə). Başqa yazılışlar üçün `m: ['...']`, termin başqa mənada işlənən dərslər üçün `x: ['dərs-adı']`. Heç bir dərsdə keçməyən termin build-də xəta verir — istisna `e: ['secplus', 'netplus', ...]` ilə işarələnmiş CompTIA akronimləridir — termin həmin imtahanın rəsmi akronim siyahısındadır (imtahanlar `window.GLOSSARY_EXAMS`-da, lüğətdə hər biri üçün ayrıca filtr).

## 7. Faydalı link əlavə etmək

`links.html` faylında `const CATEGORIES = [` siyahısını tapın və uyğun bölməyə əlavə edin:

```js
{ n: 'Saytın adı', u: 'https://...', t: 'Kurs', d: 'Qısa izah (Azərbaycan dilində).' },
```

`t` (növ): `Alət`, `Sayt`, `Kurs`, `Kitab`, `Video`, `Kanal`, `Repo`, `İcma`. Seçimlər: `f: 1` — seçilmiş (sarı xətt), `lang: 'Türkcə'` — dil işarəsi. Yeni bölmə üçün `{ id, name, icon, desc, items: [...] }` obyekti əlavə edin. CCNA tabındakı "Faydalı Mənbələr" isə `index.html`-dəki `resources` siyahısındadır.

## 8. Sosial linklər, menyu, ikonlar

- **Sosial şəbəkələr və menyu:** `_dev/build.py`-nin əvvəlindəki `SOCIALS` və `NAV` siyahıları → sonra `python3 _dev/build.py` (bütün footer-lər və Haqqında səhifəsi yenilənir).
- **Yeni ikon:** ad seçin (https://lucide.dev/icons), sonra:
  ```bash
  cd _dev && npm install && cd ..        # yalnız bir dəfə
  python3 _dev/build.py icons add cloud-rain
  ```
  Brend ikonu üçün `brand-` prefiksi: `python3 _dev/build.py icons add brand-github`.
- **Dizayn qaydaları:** yalnız ağ, qara və sarı-narıncı rənglər; emoji yox — həmişə ikon. Mətn Azərbaycan dilində, IT terminləri orijinal ingiliscə.

## 8a. SEO və paylaşım (Open Graph)

`python3 _dev/build.py` hər səhifənin `<head>`-inə `<!--SEO-->...<!--/SEO-->` bloku yazır — onu əl ilə redaktə etməyin:

- **meta description** — dərslər üçün `assets/catalog.js`-dəki `desc`-dən avtomatik; digər səhifələrdə `<title>`-dan sonrakı `<meta name="description">` sətrindən (yeni səhifə yaradanda onu yazın);
- **canonical**, **Open Graph** və **Twitter** tag-ları (linki paylaşanda başlıq, izah və şəkil görünür);
- **JSON-LD** (schema.org): ana səhifə `WebSite`, dərslər `LearningResource`, alətlər `WebApplication`;
- favicon və `theme-color`; kök qovluqda `sitemap.xml` və `robots.txt`.

Saytın ünvanı `_dev/build.py`-dəki **`SITE_URL`**-dadır. Repo adı dəyişəndə və ya öz domen qoşulanda yalnız onu dəyişin və build edin — bütün linklər və sitemap yenilənir.

**Paylaşım şəkilləri** (1200×630, qara-sarı dizayn, hər səhifə üçün ayrıca):

```bash
cd _dev && npm install && cd ..          # bir dəfə (Inter şrifti)
npm i -g playwright && npx playwright install chromium   # bir dəfə
node _dev/og.js                          # yalnız yeni/dəyişmiş səhifələr
node _dev/og.js --force                  # hamısı (dizaynı dəyişəndə)
```

**Google Search Console:** https://search.google.com/search-console → *Add property* → *URL prefix* → `SITE_URL` → *HTML tag* üsulu → verilən `content` dəyərini `GOOGLE_SITE_VERIFICATION`-a yazıb build və publish edin → *Verify* → *Sitemaps* bölməsində `sitemap.xml` göndərin. Öz domen qoşulandan sonra *Domain* property-ni DNS TXT qeydi ilə təsdiqləmək daha yaxşıdır.

## 8b. Təhlükəsizlik

Sayt statikdir (server, baza, parol yoxdur), amma brauzer tərəfində bunlar tətbiq olunur:

- **Üçüncü tərəf skripti yoxdur.** Tailwind CSS build zamanı `assets/tailwind.css`-ə yığılır (əvvəl `cdn.tailwindcss.com` skripti hər ziyarətçidə işləyirdi), Inter şrifti `assets/fonts/`-dan, Chart.js `assets/vendor/`-dan (4.5.1, npm-in sha512 hash-i ilə yoxlanılıb) yüklənir. Yalnız Video Dərslər səhifəsi YouTube pleyerini yükləyir.
- **Content-Security-Policy** hər səhifədə `<!--CSP-->` blokunda: skriptlər yalnız saytın özündən və səhifədəki daxili skriptlərin **sha256 hash-i** ilə icazəlidir; `object-src 'none'`, `base-uri 'self'`, `form-action 'self'`, iframe yalnız videos.html-də YouTube üçün. Blok `build.py` tərəfindən yaradılır — daxili skripti dəyişəndə **mütləq** `python3 _dev/build.py` işlədin, yoxsa brauzer skripti bloklayır (CI bunu yoxlayır).
- **Referrer-Policy** `strict-origin-when-cross-origin` (YouTube embed-i üçün də lazımdır).
- İstifadəçinin daxil etdiyi mətn (ad, axtarış, CLI əmrləri) HTML kimi yox, mətn kimi göstərilir; yedəkdən bərpa yalnız `edu-portal-*` açarlarını qəbul edir.
- `.well-known/security.txt` — zəiflik bildirmək üçün əlaqə.
- GitHub Actions: action-lar commit SHA-sı ilə bağlanıb, `persist-credentials: false`, minimal icazələr; build alətləri `package-lock.json` ilə (`npm ci`) quraşdırılır; Dependabot həftəlik yeniləmə PR-ları açır.

GitHub Pages HTTP başlıqlarını (HSTS, X-Frame-Options və s.) dəyişməyə imkan vermir — bunlar yalnız `<meta>` ilə mümkün olanlarla məhdudlaşır. Settings → Pages → **Enforce HTTPS** açıq olmalıdır.

Build alətləri (bir dəfə): `cd _dev && npm ci && cd ..` — bundan sonra `python3 _dev/build.py` Tailwind CSS-i də yenidən qurur.

## 9. Publish (dərc etmək)

```bash
python3 _dev/build.py          # "yoxlama: problem yoxdur" olmalıdır (GitHub Actions da eyni yoxlamanı edir)
git add -A
git commit -m "Yeni dərs: Linux şəbəkə konfiqurasiyası"
git push origin main
```

GitHub **Actions** tabında "pages build and deployment" yaşıl olduqdan 1–2 dəqiqə sonra dəyişiklik saytda görünür. Brauzer köhnə versiyanı göstərirsə — `Ctrl+F5`.

GitHub Pages parametri: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)`**.

## 10. Avtomatik yoxlama (GitHub Actions)

`.github/workflows/site.yml` hər push və pull request-də işləyir:

1. `python3 _dev/build.py check` — ikonlar, kataloq, quiz sualları və **bütün daxili linklər** (fayl və `#bölmə` keçidləri).
2. Qurulmuş səhifələrin `_dev` mənbələri ilə eyni olduğunu yoxlayır (build-i unutmusunuzsa, xəbər verir).
3. Yoxlama keçərsə, `main`-dəki saytı GitHub Pages-ə dərc edir.

**Səhvli dəyişikliyin sayta çıxmaması üçün bir dəfə:** Settings → Pages → Build and deployment → Source: **GitHub Actions** seçin. Bundan sonra sayt yalnız yoxlamadan keçən commit-lərdən dərc olunur. Yoxlama qırmızıdırsa, Actions tabında səbəbi yazılır.

`.github/workflows/external-links.yml` həftədə bir dəfə xarici linkləri yoxlayır (dərci bloklamır). Lokal: `python3 _dev/build.py links --external`.

## 11. Lisenziyalar

- İkonlar: [Lucide](https://lucide.dev) — ISC; brend ikonları: [Font Awesome Free](https://fontawesome.com/license/free) — CC BY 4.0.
- Faydalı Linklər siyahısı [LuNiZz/siber-guvenlik-sss](https://github.com/LuNiZz/siber-guvenlik-sss) əsasında Azərbaycan dilinə uyğunlaşdırılıb.

© 2027 Cavad Mikayil
