# CCNA lab tapşırıqları — Network Management və Network Design.

LABS = [
    {
        'slug': 'ios-filesystem',
        'title': 'Konfiqurasiya Backup-ı və IOS Yeniləməsi',
        'goal': 'TFTP ilə konfiqurasiya və IOS image-ın backup-ını almaq, yeni image-ı yükləyib boot sırasını dəyişmək.',
        'tool': 'Cisco Packet Tracer (Server-PT: TFTP xidməti)',
        'time': '40 dəq',
        'topology': '''
 R1 (Gi0/0 192.168.1.1) ---- SW ---- TFTP Server 192.168.1.100
''',
        'tasks': [
            '<code>show flash:</code> və <code>show version</code> ilə cari image-ı, flash ölçüsünü və config register-i yazın.',
            'Running-config-i TFTP-yə kopyalayın: <code>copy running-config tftp:</code> (fayl adı <code>R1-2027-01-15.cfg</code>).',
            'Cari IOS image-ın backup-ını TFTP-yə kopyalayın.',
            'Konfiqurasiyada dəyişiklik edib (məs. hostname), sonra TFTP-dəki faylı <code>copy tftp: running-config</code> ilə geri yükləyin — birləşmə (merge) davranışını izah edin.',
            'TFTP-də olan başqa image-ı flash-a kopyalayın, <code>boot system flash:&lt;yeni&gt;</code> yazın, köhnəni ehtiyat kimi saxlayın.',
            'Reload edib <code>show version</code> ilə yeni image-dan açıldığını təsdiqləyin.',
        ],
        'verify': '''
show flash:
show version
show boot
dir flash:
show running-config | include boot
''',
        'expect': [
            'TFTP serverdə config və image faylları var.',
            '<code>copy tftp: running-config</code> konfiqurasiyanı əvəz etmir, birləşdirir.',
            'Router yeni image ilə açılır; köhnə image ehtiyat boot seçimi kimi qalır.',
        ],
    },
    {
        'slug': 'password-recovery',
        'title': 'Router Parolunun Bərpası',
        'goal': 'Unudulmuş enable secret-i config register vasitəsilə konfiqurasiyanı itirmədən bərpa etmək.',
        'tool': 'Cisco Packet Tracer (fiziki router, konsol kabeli)',
        'time': '30 dəq',
        'tasks': [
            'R1-ə naməlum <code>enable secret</code> qoyun (yoldaşınız qoysun), konfiqurasiyanı yadda saxlayın.',
            'Router-i söndürüb yandırın və açılışın ilk 60 saniyəsində <strong>Break</strong> (Ctrl+Break) göndərib ROMMON-a keçin.',
            '<code>confreg 0x2142</code> — startup-config-i nəzərə almadan açılış; <code>reset</code>.',
            'Açılışda setup dialoqundan imtina edin, <code>enable</code>, sonra <code>copy startup-config running-config</code>.',
            'Yeni <code>enable secret</code> təyin edin, interfeyslərin <code>no shutdown</code> olduğunu yoxlayın.',
            '<code>config-register 0x2102</code>, <code>copy running-config startup-config</code>, reload — konfiqurasiyanın yerində olduğunu göstərin.',
        ],
        'verify': '''
rommon 1 > confreg 0x2142
rommon 2 > reset
Router# show version | include register
Router# show ip interface brief
''',
        'expect': [
            'Köhnə konfiqurasiya (IP-lər, routing) itmədən parol dəyişdirilib.',
            'Config register sonda 0x2102-dir.',
            'Bu prosesin fiziki giriş tələb etdiyini və <code>no service password-recovery</code>-nin nə etdiyini izah edirsiniz.',
        ],
    },
    {
        'slug': 'campus-design',
        'title': 'Kampus Şəbəkəsinin Dizaynı',
        'goal': 'Real tələblər üzrə three-tier kampus dizaynı hazırlamaq: topologiya, VLAN və IP planı, ehtiyat mexanizmləri.',
        'tool': 'draw.io və ya kağız + Packet Tracer (kiçik prototip)',
        'time': '90 dəq',
        'level': 'Çətin',
        'tasks': [
            'Tələblər: 2 bina, cəmi 8 mərtəbə, 600 istifadəçi, 300 IP telefon, 60 AP, data mərkəzi otağı, 2 provayder.',
            'Topologiya: core (2 switch), hər binada distribution cütü, hər mərtəbədə access switch stack-ı. Hər linkin sürətini və növünü yazın.',
            'VLAN planı: data, voice, Wi-Fi korporativ, Wi-Fi qonaq, idarəetmə, printerlər, kameralar — hər bina üçün.',
            '<code>10.0.0.0/16</code> blokundan VLSM ilə IP planı və xülasə sərhədləri (distribution-da summarization).',
            'Ehtiyat: L3 access və ya HSRP/VRRP, EtherChannel uplink-lər, STP root planı, iki provayder üçün həll.',
            'Kiçik prototipi (1 core, 1 distribution cütü, 2 access) Packet Tracer-də qurub bir uplinkin kəsilməsini sınayın.',
        ],
        'expect': [
            'Hər access switch-in iki distribution-a uplink-i var; single point of failure yoxdur.',
            'IP planı böyüməyə 30–50% yer saxlayır və bina səviyyəsində xülasə edilə bilir.',
            'Dizayn sənədi: diaqram, VLAN cədvəli, IP cədvəli, ehtiyat mexanizmlərinin izahı.',
        ],
    },
]
