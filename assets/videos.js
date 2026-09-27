// Video Dərslər — YouTube kursları (videos.html buradan oxuyur).
//
// Yeni kurs əlavə etmək üçün YouTube-da kursun (playlist-in) linkini kopyalayıb aşağıya bir blok yazın:
//
//     {
//         id: 'ccna',                                   // qısa ad, latın hərfləri ilə (linkdə görünür: videos.html#ccna)
//         title: 'CCNA 200-301 tam kurs',
//         desc: 'Kurs haqqında 1–2 cümlə.',
//         icon: 'graduation-cap',                       // assets/icons.svg-dəki ikon adı
//         playlist: 'https://www.youtube.com/playlist?list=PL...',
//         lessons: ['osi-model', 'ipv4-subnetting'],    // istəyə bağlı: portalın uyğun dərsləri (lessons/<ad>.html)
//         notes: { 'VIDEO_ID': 'Bu videoda nə var — qısa izah.' }  // istəyə bağlı
//     },
//
// Videoların siyahısı, sırası və adları səhifə açılanda YouTube-dan avtomatik gəlir —
// playlist-ə yeni video əlavə edəndə portalda heç nə dəyişmək lazım deyil.
// Playlist əvəzinə videoları özünüz sıralamaq istəsəniz: videos: ['VIDEO_ID_1', 'VIDEO_ID_2', ...]
window.VIDEO_CHANNEL = 'https://www.youtube.com/@cavadmikayil/courses';

window.VIDEO_COURSES = [
    {
        id: 'fortigate',
        title: 'FortiGate',
        desc: 'Fortinet FortiGate firewall: quraşdırma, konfiqurasiya və idarəetmə üzrə tam kurs.',
        icon: 'shield-check',
        playlist: 'https://www.youtube.com/playlist?list=PLIWUHiy6unDu6EoViNjZUy18s9CgUY_JY',
    },
];
