// Karyera yolları — careers.html və dashboard buradan oxuyur.
// Mərhələlərdəki "lessons" — dərs fayllarının adıdır (lessons/<ad>.html); build.py check hamısının mövcudluğunu yoxlayır.
window.CAREERS = [
    {
        id: 'helpdesk',
        title: 'Helpdesk mütəxəssisi',
        icon: 'headset',
        level: 'Başlanğıc · 3–6 ay',
        summary: 'İT-yə ən sürətli giriş yolu: istifadəçilərin kompüter, hesab, printer və şəbəkə problemlərini həll etmək, ticket sistemi ilə işləmək və düzgün ünsiyyət qurmaq.',
        duties: ['Ticket-lərin qəbulu, prioritetləşdirilməsi və həlli', 'Windows, Microsoft 365 və printer problemləri', 'Parol sıfırlama, hesab və icazələr', 'Uzaqdan dəstək və yeni işçinin kompüterinin hazırlanması'],
        certs: [
            { name: 'CompTIA A+', desc: 'Hardware, OS, şəbəkə əsasları və troubleshooting — helpdesk üçün standart sertifikat.' },
            { name: 'ITIL 4 Foundation', desc: 'İT xidmət idarəetməsi: incident, request, change prosesləri.' },
            { name: 'Microsoft 365 Fundamentals (MS-900)', desc: 'M365 xidmətləri, lisenziyalar və təhlükəsizlik əsasları.' }
        ],
        next: 'Sistem administratoru və ya şəbəkə mühəndisi',
        stages: [
            { title: 'Kompüter və əməliyyat sistemi', lessons: ['pc-hardware', 'windows-troubleshooting', 'printer-support', 'aplus-core1'] },
            { title: 'Dəstək prosesi və ünsiyyət', lessons: ['helpdesk-itil', 'helpdesk-communication', 'troubleshooting', 'aplus-troubleshooting'] },
            { title: 'Şəbəkə əsasları', lessons: ['osi-model', 'ipv4-subnetting', 'user-network-issues', 'dhcp'] },
            { title: 'Hesablar və bulud xidmətləri', lessons: ['account-support', 'windows-ad', 'm365-support', 'remote-support'] },
            { title: 'Təhlükəsizlik və səmərəlilik', lessons: ['email-security', 'endpoint-security', 'aplus-core2', 'ai-for-it'] }
        ],
        tools: ['tools/quiz.html', 'tools/ports.html', 'tools/flashcards.html']
    },
    {
        id: 'network',
        title: 'Şəbəkə mühəndisi',
        icon: 'network',
        level: 'Orta · 6–12 ay',
        summary: 'Kampus və filial şəbəkələrinin qurulması, switching və routing, təhlükəsizlik və getdikcə daha çox avtomatlaşdırma. CCNA bu yolun təməlidir.',
        duties: ['Switch, router, firewall və Wi-Fi konfiqurasiyası', 'VLAN, OSPF, NAT, VPN və ACL-lərin qurulması', 'Şəbəkə problemlərinin diaqnostikası və monitorinq', 'Dəyişikliklərin planlaşdırılması və sənədləşdirilməsi'],
        certs: [
            { name: 'Cisco CCNA 200-301', desc: 'Şəbəkə mühəndisinin əsas sertifikatı — bu portalın 50 CCNA dərsi, lab-ları və imtahan simulyatoru ona hazırlayır.' },
            { name: 'CompTIA Network+', desc: 'Vendor-neytral alternativ və ya əlavə.' },
            { name: 'CCNP Enterprise / Fortinet FCP', desc: 'Növbəti səviyyə: dərin routing, SD-WAN, firewall.' }
        ],
        next: 'Network security mühəndisi, network automation mühəndisi',
        stages: [
            { title: 'Şəbəkə əsasları', lessons: ['osi-model', 'ethernet-cabling', 'tcp-udp', 'mac-arp', 'icmp', 'binary-hex', 'ipv4-subnetting', 'ipv6', 'ios-cli'] },
            { title: 'Switching', lessons: ['switching-basics', 'dtp', 'vlan-types', 'inter-vlan-routing', 'stp', 'stp-advanced', 'etherchannel', 'wireless'] },
            { title: 'Routing', lessons: ['router-basics', 'static-routing', 'dynamic-routing', 'ospf', 'ospf-multiarea', 'summarization', 'fhrp', 'wan'] },
            { title: 'Xidmətlər və təhlükəsizlik', lessons: ['dhcp', 'nat', 'network-services', 'acl', 'port-security', 'dhcp-snooping', 'ssh-security', 'vpn'] },
            { title: 'Avtomatlaşdırma', lessons: ['netauto-intro', 'python-basics', 'netmiko', 'rest-api', 'sdn-controllers'] }
        ],
        tools: ['tools/exam.html', 'tools/cli.html', 'tools/subnet-calculator.html', 'tools/vlsm.html']
    },
    {
        id: 'sysadmin',
        title: 'Sistem administratoru',
        icon: 'server',
        level: 'Orta · 6–12 ay',
        summary: 'Linux və Windows serverlərinin, Active Directory-nin, virtualizasiyanın və backup-ın idarə olunması; cloud və avtomatlaşdırma ilə DevOps-a körpü.',
        duties: ['Linux və Windows serverlərin qurulması və yenilənməsi', 'Active Directory, DNS, DHCP, fayl və veb serverlər', 'Virtualizasiya, konteynerlər və backup', 'Monitorinq, performans və təhlükəsizlik (hardening)'],
        certs: [
            { name: 'RHCSA / CompTIA Linux+', desc: 'Linux administrasiyası üzrə praktiki sertifikat.' },
            { name: 'Microsoft AZ-800 / AZ-104', desc: 'Windows Server hybrid və Azure administratoru.' },
            { name: 'CompTIA Server+', desc: 'Vendor-neytral server hardware və idarəetmə.' }
        ],
        next: 'Cloud mühəndisi, DevOps mühəndisi',
        stages: [
            { title: 'Server əsasları', lessons: ['server-hardware', 'virtualization', 'linux-basics', 'linux-filesystem', 'linux-permissions'] },
            { title: 'Linux administrasiyası', lessons: ['linux-services', 'linux-boot', 'linux-storage', 'linux-networking', 'bash-scripting'] },
            { title: 'Windows və identity', lessons: ['windows-ad', 'dns-server', 'dhcp', 'identity-security'] },
            { title: 'Xidmətlər və etibarlılıq', lessons: ['web-server', 'docker', 'backup-dr', 'server-monitoring', 'linux-performance', 'linux-security'] },
            { title: 'Cloud və avtomatlaşdırma', lessons: ['cloud-fundamentals', 'azure-core', 'git-basics', 'ansible', 'terraform'] }
        ],
        tools: ['tools/quiz.html', 'tools/subnet-calculator.html', 'tools/ports.html']
    },
    {
        id: 'soc',
        title: 'SOC analitiki',
        icon: 'shield-check',
        level: 'Orta · 9–12 ay',
        summary: 'Təhlükəsizlik əməliyyat mərkəzində alert-lərin təhlili, insidentlərə cavab və təhdid ovu. Güclü şəbəkə və OS bilikləri üzərində qurulur.',
        duties: ['SIEM alert-lərinin triage-i və araşdırılması', 'Log analizi: Windows Event, firewall, proxy, EDR', 'Insident cavabı və eskalasiya', 'Zəifliklərin izlənməsi və hesabatlar'],
        certs: [
            { name: 'CompTIA Security+', desc: 'Təhlükəsizliyin əsas sertifikatı — portalın Security+ dərsləri.' },
            { name: 'CompTIA CySA+ / BTL1', desc: 'SOC analitiki üçün praktiki blue team sertifikatları.' },
            { name: 'Microsoft SC-200 / Splunk Core', desc: 'Konkret SIEM platformaları üzrə.' }
        ],
        next: 'Incident responder, threat hunter, təhlükəsizlik mühəndisi',
        stages: [
            { title: 'Texniki baza', lessons: ['osi-model', 'tcp-udp', 'ipv4-subnetting', 'linux-basics', 'linux-text', 'windows-ad'] },
            { title: 'Təhlükəsizlik konsepsiyaları', lessons: ['security-threats', 'crypto-pki', 'identity-security', 'secplus-concepts', 'secplus-threats'] },
            { title: 'Müdafiə texnologiyaları', lessons: ['firewall', 'acl', 'vpn', 'endpoint-security', 'email-security', 'web-app-security'] },
            { title: 'SOC əməliyyatları', lessons: ['siem-logs', 'incident-response', 'vuln-management', 'secplus-operations'] },
            { title: 'Cloud və idarəetmə', lessons: ['cloud-security', 'risk-compliance', 'devsecops', 'ai-safety'] }
        ],
        tools: ['tools/quiz.html', 'tools/ports.html', 'tools/wildcard.html']
    }
];
