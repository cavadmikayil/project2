// İnteraktiv alətlərin siyahısı — Tools səhifəsi (tools.html) və dashboard buradan oxuyur.
// Yeni alət: tools/<ad>.html yaradın (mövcud alətlərdən birini kopyalayın) və aşağıya bir sətir əlavə edin.
window.TOOLS = [
    { id: 'exam', title: 'CCNA İmtahan Simulyatoru', desc: '100 qarışıq sual, 120 dəqiqəlik taymer, qeyd etmə və sonda 6 bölmə üzrə zəif tərəflərin hesabatı.', icon: 'timer', href: 'tools/exam.html', group: 'Məşq', featured: true },
    { id: 'cli', title: 'Cisco CLI Simulyatoru', desc: 'Brauzerdə IOS əmrlərini məşq edin: rejimlər, qısaltmalar, ? köməyi və 6 bələdçili tapşırıq (router və switch).', icon: 'square-terminal', href: 'tools/cli.html', group: 'Məşq', featured: true },
    { id: 'quiz', title: 'Quiz', desc: 'Bütün dərslər üzrə izahlı test sualları; kateqoriya və mövzu seçimi, ən yaxşı nəticənin saxlanması.', icon: 'notebook-pen', href: 'tools/quiz.html', group: 'Məşq', featured: true },
    { id: 'flashcards', title: 'Flashcard-lar', desc: 'Portlar, OSI, administrative distance, IOS əmrləri və terminlər — Leitner sistemi ilə təkrar.', icon: 'layers-2', href: 'tools/flashcards.html', group: 'Məşq', featured: true },
    { id: 'subnet', title: 'Subnet Kalkulyatoru', desc: 'Şəbəkə/broadcast ünvanı, host sayı, wildcard və binary görünüş, üstəlik subnetting məşqi.', icon: 'calculator', href: 'tools/subnet-calculator.html', group: 'Kalkulyatorlar', featured: true },
    { id: 'vlsm', title: 'VLSM Planlayıcı', desc: 'Əsas şəbəkə və host sayları verilir — alət subnet-ləri böyükdən kiçiyə ayırıb ünvan planı hazırlayır.', icon: 'list-tree', href: 'tools/vlsm.html', group: 'Kalkulyatorlar' },
    { id: 'ipv6', title: 'IPv6 Kalkulyatoru', desc: 'Qısaltma və genişləndirmə, prefiks və aralıq, ünvan növü və MAC-dan EUI-64.', icon: 'globe', href: 'tools/ipv6.html', group: 'Kalkulyatorlar' },
    { id: 'wildcard', title: 'Wildcard Mask Kalkulyatoru', desc: 'Maska ↔ wildcard ↔ CIDR, ACL və OSPF sətirləri, IP-nin ACL qaydasına uyğunluq testi.', icon: 'list-filter', href: 'tools/wildcard.html', group: 'Kalkulyatorlar' },
    { id: 'ports', title: 'Port və Protokol Arayışı', desc: '50 vacib TCP/UDP portu, IP protokol nömrələri və təhlükəsiz alternativlər — axtarışla.', icon: 'plug', href: 'tools/ports.html', group: 'Arayış' }
];
