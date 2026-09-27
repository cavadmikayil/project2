# CCNA lab tapşırıqları — Network Access.

LABS = [
    {
        'slug': 'switching-basics',
        'title': 'MAC Öyrənmə, Flooding və Switch İdarəetməsi',
        'goal': 'Switch-in MAC cədvəlini necə qurduğunu və naməlum unicast-ı necə flood etdiyini görmək; switch-ə idarəetmə IP-si vermək.',
        'tool': 'Cisco Packet Tracer (Simulation Mode)',
        'time': '30 dəq',
        'level': 'Başlanğıc',
        'topology': '''
 PC1 (Fa0/1) \\
 PC2 (Fa0/2) --- SW1 (Fa0/24) --- SW2 --- PC4 (Fa0/1)
 PC3 (Fa0/3) /
''',
        'addressing': [
            ['Cihaz', 'IP / maska'],
            ['PC1–PC4', '192.168.1.11–14 /24'],
            ['SW1 VLAN 1', '192.168.1.2 /24'],
            ['SW2 VLAN 1', '192.168.1.3 /24'],
        ],
        'tasks': [
            'Topologiyanı qurun; hər iki switch-də <code>clear mac address-table dynamic</code>.',
            'Simulation Mode-da PC1-dən PC4-ə ping: ilk frame-in (ARP broadcast) bütün portlardan flood olduğunu izləyin.',
            'Ping-dən sonra hər iki switch-də MAC cədvəlinə baxın — PC4-ün MAC-ı SW1-də hansı portda görünür?',
            'SW1-də <code>interface vlan 1</code>-ə IP verin, <code>ip default-gateway</code> yazın və PC1-dən switch-ə ping edin.',
            '<code>mac address-table aging-time 60</code> təyin edib bir dəqiqə gözləyin: qeydlər silinirmi?',
        ],
        'verify': '''
show mac address-table
show mac address-table aging-time
show interfaces vlan 1
show ip interface brief
''',
        'expect': [
            'Uzaq PC-lərin MAC-ları SW1-də uplink portunda (Fa0/24) görünür.',
            'SW1 ping-ə cavab verir — idarəetmə IP-si işləyir.',
            'Aging müddətindən sonra fəaliyyətsiz qeydlər cədvəldən silinir.',
        ],
    },
    {
        'slug': 'topologies',
        'title': 'Kiçik Ofis üçün Two-Tier Dizayn',
        'goal': 'Tələblərə görə collapsed core (two-tier) topologiya çəkmək, ehtiyat yolları və tək nöqtəli nasazlıqları müəyyənləşdirmək.',
        'tool': 'Kağız və ya draw.io + Packet Tracer',
        'time': '40 dəq',
        'tasks': [
            'Tələblər: 3 mərtəbə, hər mərtəbədə 40 istifadəçi, 1 server otağı, 2 internet provayderi, Wi-Fi.',
            'Two-tier (collapsed core) dizayn çəkin: 2 core/distribution switch, hər mərtəbədə access switch, hər access switch-dən iki core-a uplink.',
            'Hər link üçün növü (copper/fiber, 1G/10G) və funksiyanı (trunk, L3) yazın.',
            'Diaqramda <strong>single point of failure</strong> olan hər cihazı qırmızı ilə işarələyin və necə aradan qaldırılacağını yazın.',
            'Dizaynı Packet Tracer-də quraşdırın və bir core switch-i söndürdükdə istifadəçilərin hələ də serverə çatdığını göstərin (STP və ya L3 uplink).',
        ],
        'expect': [
            'Hər access switch-in iki müstəqil uplink-i var.',
            'İki provayder iki fərqli router/firewall-a qoşulub (və ya bir firewall klasterinə).',
            'Bir core switch sönəndə şəbəkə işləməyə davam edir.',
        ],
    },
    {
        'slug': 'cdp-lldp',
        'title': 'Kəşf Protokolları ilə Topologiya Xəritəsi',
        'goal': 'CDP və LLDP ilə naməlum şəbəkənin xəritəsini çıxarmaq və təhlükəsizlik üçün lazımsız yerlərdə söndürmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '30 dəq',
        'topology': '''
          R1 (Gi0/0)
           |
       (Gi0/1) SW1 (Gi0/2) ---- (Gi0/1) SW2 (Fa0/1) --- IP Phone
           |
       (Fa0/5) PC-Admin
''',
        'tasks': [
            'Topologiyanı qurun, cihazlara IP ünvanlar verin (switch-lərdə VLAN 1-də).',
            'SW1-də <code>show cdp neighbors</code> və <code>detail</code> ilə qonşuların modelini, portunu və IP-sini tapın.',
            'Hər iki switch və router-də <code>lldp run</code> aktivləşdirin, eyni məlumatı <code>show lldp neighbors detail</code> ilə alın.',
            'CDP timer-i 30 s, holdtime 90 s edin və <code>show cdp</code> ilə yoxlayın.',
            'PC-Admin portunda (Fa0/5) CDP və LLDP-ni söndürün; infrastruktur linklərində aktiv saxlayın.',
        ],
        'verify': '''
show cdp neighbors
show cdp neighbors detail
show lldp neighbors detail
show cdp interface fa0/5
show lldp interface fa0/5
''',
        'expect': [
            'Qonşu cədvəlindən tam topologiya diaqramı çəkilir.',
            'Fa0/5-də CDP/LLDP elanı göndərilmir.',
            'Uplink-lərdə hər iki protokol işləyir.',
        ],
        'solution': '''
SW1(config)# lldp run
SW1(config)# cdp timer 30
SW1(config)# cdp holdtime 90
SW1(config)# interface fa0/5
SW1(config-if)# no cdp enable
SW1(config-if)# no lldp transmit
SW1(config-if)# no lldp receive
''',
    },
    {
        'slug': 'dtp',
        'title': 'VLAN-lar, Access və Trunk Portlar',
        'goal': 'İki switch arasında 802.1Q trunk qurmaq, VLAN-ları yaratmaq və DTP-ni təhlükəsiz şəkildə söndürmək.',
        'tool': 'Cisco Packet Tracer və ya portalın CLI Simulyatoru (5-ci tapşırıq)',
        'time': '40 dəq',
        'topology': '''
 PC1 (VLAN 10) Fa0/1 \\                        / Fa0/1 PC3 (VLAN 10)
                      SW1 (Gi0/1)====(Gi0/1) SW2
 PC2 (VLAN 20) Fa0/2 /        trunk            \\ Fa0/2 PC4 (VLAN 20)
''',
        'addressing': [
            ['VLAN', 'Ad', 'Subnet', 'PC-lər'],
            ['10', 'MUHASIBAT', '192.168.10.0/24', 'PC1 .11, PC3 .13'],
            ['20', 'IT', '192.168.20.0/24', 'PC2 .12, PC4 .14'],
            ['99', 'NATIVE', '—', 'istifadə olunmur'],
        ],
        'tasks': [
            'Hər iki switch-də VLAN 10, 20, 99 yaradın və adlandırın.',
            'Fa0/1–2 portlarını access edib müvafiq VLAN-a təyin edin.',
            'Gi0/1-də əvvəlcə heç nə yazmadan <code>show interfaces gi0/1 switchport</code> ilə DTP-nin nəticəsinə baxın (dynamic auto + dynamic auto = ?).',
            'Gi0/1-i əl ilə trunk edin, native VLAN 99, icazə verilən VLAN-lar 10,20,99 və <code>switchport nonegotiate</code>.',
            'PC1 → PC3 (eyni VLAN) ping uğurlu, PC1 → PC2 (fərqli VLAN) uğursuz olmalıdır — izah edin.',
            'Bir tərəfdə native VLAN-ı 1 edib CDP-nin native VLAN mismatch xəbərdarlığını tapın, sonra düzəldin.',
        ],
        'verify': '''
show vlan brief
show interfaces trunk
show interfaces gi0/1 switchport
show dtp interface gi0/1
''',
        'expect': [
            'auto + auto nəticəsi access-dir — trunk yaranmır.',
            '<code>show interfaces trunk</code>-da Gi0/1 802.1q, native 99, allowed 10,20,99.',
            'Eyni VLAN-dakı PC-lər əlaqə qurur, fərqli VLAN-lar router olmadan qura bilmir.',
        ],
        'solution': '''
SW1(config)# vlan 10
SW1(config-vlan)# name MUHASIBAT
SW1(config-vlan)# vlan 20
SW1(config-vlan)# name IT
SW1(config-vlan)# vlan 99
SW1(config-vlan)# name NATIVE
SW1(config)# interface fa0/1
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config)# interface fa0/2
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 20
SW1(config)# interface gi0/1
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk native vlan 99
SW1(config-if)# switchport trunk allowed vlan 10,20,99
SW1(config-if)# switchport nonegotiate
! SW2 eyni
''',
    },
    {
        'slug': 'vlan-types',
        'title': 'Voice VLAN və Parking VLAN',
        'goal': 'IP telefon + kompüter portu konfiqurasiya etmək və istifadə olunmayan portları təhlükəsiz "parking" VLAN-a çıxarmaq.',
        'tool': 'Cisco Packet Tracer (7960 IP Phone, 2960 switch)',
        'time': '30 dəq',
        'topology': '''
 PC ---- [IP Phone] ---- (Fa0/5) SW1 (Gi0/1) ---- R1 (CME / DHCP)
''',
        'addressing': [
            ['VLAN', 'Ad', 'Subnet'],
            ['10', 'DATA', '192.168.10.0/24'],
            ['150', 'VOICE', '192.168.150.0/24'],
            ['999', 'PARKING', '— (shutdown)'],
        ],
        'tasks': [
            'SW1-də VLAN 10, 150, 999 yaradın.',
            'Fa0/5-i access VLAN 10, <code>switchport voice vlan 150</code>, <code>spanning-tree portfast</code> edin.',
            'Telefonu switch-ə, PC-ni telefonun PC portuna qoşun (telefona enerji: PoE və ya adapter).',
            '<code>show interfaces fa0/5 switchport</code> ilə Voice VLAN-ı yoxlayın, CDP ilə telefonun VLAN-ı necə öyrəndiyini izah edin.',
            'Fa0/10–24 portlarını <code>interface range</code> ilə VLAN 999-a təyin edib söndürün.',
        ],
        'verify': '''
show vlan brief
show interfaces fa0/5 switchport
show cdp neighbors detail
show interfaces status
''',
        'expect': [
            'Fa0/5-də Access VLAN 10 və Voice VLAN 150 görünür.',
            'Telefon trafiki tag-lı (150), PC trafiki tag-sız (10) gedir.',
            'İstifadə olunmayan portlar <code>disabled</code> və VLAN 999-dadır.',
        ],
        'solution': '''
SW1(config)# vlan 10
SW1(config-vlan)# name DATA
SW1(config-vlan)# vlan 150
SW1(config-vlan)# name VOICE
SW1(config-vlan)# vlan 999
SW1(config-vlan)# name PARKING
SW1(config)# interface fa0/5
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# switchport voice vlan 150
SW1(config-if)# spanning-tree portfast
SW1(config)# interface range fa0/10 - 24
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport access vlan 999
SW1(config-if-range)# shutdown
''',
    },
    {
        'slug': 'vtp',
        'title': 'VTP Domeni və Revision Təhlükəsi',
        'goal': 'VTP server/client qurmaq, VLAN yayılmasını görmək və yüksək revision nömrəli switch-in VLAN-ları necə silə biləcəyini göstərmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '35 dəq',
        'topology': '''
 SW1 (server) ====trunk==== SW2 (client) ====trunk==== SW3 (transparent)
''',
        'tasks': [
            'Hər üç switch arasında trunk qurun. SW1: domen <code>LAB</code>, server; SW2: client; SW3: transparent. Parol <code>vtp123</code>.',
            'SW1-də VLAN 10, 20, 30 yaradın — SW2-də avtomatik göründüyünü, SW3-də isə görünmədiyini təsdiqləyin.',
            'SW3-də lokal VLAN 50 yaradın — digərlərinə yayılmadığını göstərin.',
            'Ayrıca SW4-ü "lab-dan gətirilmiş" switch kimi hazırlayın: domen LAB, server, çoxlu VLAN yaradıb silərək revision-u 20+ edin, yalnız VLAN 1 qalsın.',
            'SW4-ü SW2-yə trunk ilə qoşun və nə baş verdiyini müşahidə edin (SW1 və SW2-nin VLAN-ları).',
            'Nəticəni yazın və bu riskin qarşısını almağın iki yolunu göstərin.',
        ],
        'verify': '''
show vtp status
show vtp password
show vlan brief
show interfaces trunk
''',
        'expect': [
            'Client switch server-in VLAN-larını alır, transparent almır, amma ötürür.',
            'Yüksək revision-lu SW4 qoşulanda VLAN 10/20/30 domendən silinir.',
            'Qoruma: yeni switch-i transparent rejimdə qoşmaq və ya domen adını dəyişib revision-u sıfırlamaq; VTPv3 primary server.',
        ],
    },
    {
        'slug': 'inter-vlan-routing',
        'title': 'Router-on-a-Stick və Layer 3 Switch',
        'goal': 'VLAN-lar arası marşrutlaşdırmanı əvvəlcə router subinterfeysləri, sonra L3 switch SVI-ləri ilə qurmaq.',
        'tool': 'Cisco Packet Tracer (2911 router, 3650 multilayer switch)',
        'time': '50 dəq',
        'topology': '''
Hissə A:  PC10 --\\
                  SW1 (Gi0/1) ==trunk== (Gi0/0) R1
          PC20 --/

Hissə B:  PC10 --\\
                  SW-L3 (SVI Vlan10, Vlan20, ip routing)
          PC20 --/
''',
        'addressing': [
            ['Cihaz', 'Interfeys', 'IP / maska'],
            ['R1', 'Gi0/0.10', '192.168.10.1 /24'],
            ['R1', 'Gi0/0.20', '192.168.20.1 /24'],
            ['PC10', 'NIC', '192.168.10.10 /24, gw .1'],
            ['PC20', 'NIC', '192.168.20.10 /24, gw .1'],
        ],
        'tasks': [
            '<strong>A:</strong> SW1-də VLAN 10, 20, access portlar və router-ə trunk qurun.',
            'R1-də <code>Gi0/0.10</code> və <code>Gi0/0.20</code> subinterfeysləri yaradın, <code>encapsulation dot1Q</code> və IP ünvanlar verin; fiziki interfeysi <code>no shutdown</code>.',
            'PC10 → PC20 ping edin; <code>show ip route</code>-da iki connected şəbəkəni göstərin.',
            '<strong>B:</strong> Eyni tapşırığı L3 switch-də SVI-lərlə edin: <code>ip routing</code>, <code>interface vlan 10/20</code>.',
            'İki üsulu müqayisə edin: performans, tək nöqtəli nasazlıq, miqyas.',
        ],
        'verify': '''
R1# show ip interface brief
R1# show interfaces gi0/0.10
R1# show ip route connected
SW-L3# show ip route
SW-L3# show interfaces vlan 10
''',
        'expect': [
            'Hər iki üsulda VLAN-lar arası ping uğurludur.',
            'Subinterfeys üçün <code>encapsulation dot1Q</code> VLAN nömrəsi switch-dəki VLAN-la eynidir.',
            'L3 switch-də <code>ip routing</code> olmadan SVI-lər arasında marşrutlaşdırma olmur.',
        ],
        'solution': '''
! Hissə A
R1(config)# interface gi0/0
R1(config-if)# no shutdown
R1(config)# interface gi0/0.10
R1(config-subif)# encapsulation dot1Q 10
R1(config-subif)# ip address 192.168.10.1 255.255.255.0
R1(config)# interface gi0/0.20
R1(config-subif)# encapsulation dot1Q 20
R1(config-subif)# ip address 192.168.20.1 255.255.255.0
SW1(config)# interface gi0/1
SW1(config-if)# switchport mode trunk
! Hissə B
SW-L3(config)# ip routing
SW-L3(config)# interface vlan 10
SW-L3(config-if)# ip address 192.168.10.1 255.255.255.0
SW-L3(config-if)# no shutdown
SW-L3(config)# interface vlan 20
SW-L3(config-if)# ip address 192.168.20.1 255.255.255.0
SW-L3(config-if)# no shutdown
''',
    },
    {
        'slug': 'stp',
        'title': 'Root Bridge Seçkisi və Bloklanan Port',
        'goal': 'Üçbucaq topologiyada STP-nin root bridge və port rollarını proqnozlaşdırmaq, sonra root-u özünüz təyin etmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '40 dəq',
        'topology': '''
              SW1
            /     \\
       Gi0/1       Gi0/2
         /           \\
      SW2 ---------- SW3
          Gi0/2  Gi0/1
''',
        'tasks': [
            'Üç switch-i üçbucaq kimi birləşdirin (bütün linklər 1 Gbps). Konfiqurasiyadan əvvəl hər switch-in MAC-ına baxıb root bridge-i və bloklanacaq portu <strong>proqnozlaşdırın</strong>.',
            '<code>show spanning-tree</code> ilə proqnozunuzu yoxlayın: root, root port-lar, designated və alternate portlar.',
            'SW1-i VLAN 1 üçün root edin: <code>spanning-tree vlan 1 root primary</code>; SW2-ni secondary.',
            'Port rollarının necə dəyişdiyini yazın.',
            'Rapid-PVST+ rejiminə keçin və root port linkini söndürüb konvergensiya vaxtını 802.1D ilə müqayisə edin (ping -t ilə itən paketlərin sayı).',
        ],
        'verify': '''
show spanning-tree
show spanning-tree vlan 1
show spanning-tree root
show spanning-tree summary
''',
        'expect': [
            'Ən kiçik BID-li switch root-dur və bütün portları designated-dir.',
            'Root-dan ən uzaq linkdə bir port alternate/blocking-dir.',
            'Rapid-PVST+ ilə konvergensiya saniyələr, 802.1D ilə 30–50 saniyə çəkir.',
        ],
        'solution': '''
SW1(config)# spanning-tree mode rapid-pvst
SW1(config)# spanning-tree vlan 1 root primary
SW2(config)# spanning-tree mode rapid-pvst
SW2(config)# spanning-tree vlan 1 root secondary
SW3(config)# spanning-tree mode rapid-pvst
''',
    },
    {
        'slug': 'stp-advanced',
        'title': 'PortFast, BPDU Guard və Root Guard',
        'goal': 'Access portlarını sürətləndirmək və icazəsiz switch-in STP topologiyasını pozmasının qarşısını almaq.',
        'tool': 'Cisco Packet Tracer',
        'time': '35 dəq',
        'topology': '''
  SW1 (root) ==== SW2 (Fa0/1) --- PC
                      (Fa0/2) --- "Rogue" SW3 (priority 0)
''',
        'tasks': [
            'SW1-i root edin. SW2-nin Fa0/1-Fa0/2 portlarında <code>spanning-tree portfast</code> və <code>bpduguard enable</code> konfiqurasiya edin.',
            'PC-ni Fa0/1-ə qoşun: port dərhal forwarding olur (30 saniyə gözləmədən).',
            'Fa0/2-yə priority 0 olan SW3 qoşun: BPDU Guard portu <code>err-disabled</code> edir — log mesajını tapın.',
            'Alternativ: Fa0/2-də BPDU Guard əvəzinə <code>spanning-tree guard root</code> sınayın — port <code>root-inconsistent</code> olur.',
            '<code>errdisable recovery cause bpduguard</code> ilə avtomatik bərpanı qurun.',
        ],
        'verify': '''
show spanning-tree interface fa0/1 portfast
show interfaces status err-disabled
show spanning-tree inconsistentports
show errdisable recovery
show logging | include BPDU
''',
        'expect': [
            'PortFast portu dərhal forwarding olur.',
            'BPDU gələn access portu err-disabled olur, root dəyişmir.',
            'Root Guard ilə root bridge SW1 olaraq qalır.',
        ],
        'solution': '''
SW2(config)# interface range fa0/1 - 2
SW2(config-if-range)# switchport mode access
SW2(config-if-range)# spanning-tree portfast
SW2(config-if-range)# spanning-tree bpduguard enable
SW2(config)# errdisable recovery cause bpduguard
SW2(config)# errdisable recovery interval 60
! Root Guard variantı
SW2(config)# interface fa0/2
SW2(config-if)# no spanning-tree bpduguard enable
SW2(config-if)# spanning-tree guard root
''',
    },
    {
        'slug': 'etherchannel',
        'title': 'LACP EtherChannel və L3 Port-channel',
        'goal': 'İki switch arasında LACP ilə Layer 2 trunk EtherChannel və multilayer switch-lər arasında routed Port-channel qurmaq.',
        'tool': 'Cisco Packet Tracer (3650 switch)',
        'time': '40 dəq',
        'topology': '''
 SW1 (Gi1/0/1-2) ==Po1 LACP trunk== (Gi1/0/1-2) SW2
 SW1 (Gi1/0/3-4) ==Po2 L3 10.0.0.0/30== (Gi1/0/3-4) SW2
''',
        'tasks': [
            'Gi1/0/1-2 portlarını <code>channel-group 1 mode active</code> ilə Po1-ə birləşdirin, Po1-i trunk edin.',
            '<code>show etherchannel summary</code> ilə <code>SU</code> və <code>(P)</code> bayraqlarını tapın; STP-də Po1-in tək port kimi göründüyünü göstərin.',
            'Bir tərəfdə <code>passive</code>, sonra hər iki tərəfdə <code>passive</code> edin — hansı halda channel qurulmur?',
            'Bir üzv portunda speed-i dəyişib <code>(s)</code> suspended vəziyyətini yaradın, sonra düzəldin.',
            'Gi1/0/3-4 ilə L3 EtherChannel qurun: <code>no switchport</code>, Po2-yə 10.0.0.1/30 və 10.0.0.2/30, ping edin.',
            'Bir fiziki linki söndürün — ping davam edirmi?',
        ],
        'verify': '''
show etherchannel summary
show etherchannel port-channel
show lacp neighbor
show interfaces port-channel 1 trunk
show spanning-tree vlan 1
''',
        'expect': [
            'Po1 — <code>SU</code>, Po2 — <code>RU</code>, üzv portlar <code>(P)</code>.',
            'passive + passive kombinasiyasında channel qurulmur.',
            'Bir link kəsiləndə trafik digər linklə davam edir.',
        ],
        'solution': '''
SW1(config)# interface range gi1/0/1 - 2
SW1(config-if-range)# channel-group 1 mode active
SW1(config)# interface port-channel 1
SW1(config-if)# switchport mode trunk
SW1(config)# interface range gi1/0/3 - 4
SW1(config-if-range)# no switchport
SW1(config-if-range)# channel-group 2 mode active
SW1(config)# interface port-channel 2
SW1(config-if)# no switchport
SW1(config-if)# ip address 10.0.0.1 255.255.255.252
! SW2 eyni, 10.0.0.2
''',
    },
    {
        'slug': 'poe',
        'title': 'PoE Büdcəsinin Planlaşdırılması',
        'goal': 'Access switch-in PoE güc büdcəsini hesablamaq və portlarda gücü idarə etmək.',
        'tool': 'Kalkulyator + Packet Tracer (və ya real Catalyst switch)',
        'time': '30 dəq',
        'addressing': [
            ['Cihaz', 'Say', 'Sinif / güc'],
            ['IP telefon', '24', 'Class 2 — 7 W'],
            ['Wi-Fi 6 access point', '4', '802.3at — 25.5 W'],
            ['PTZ kamera', '2', '802.3bt — 51 W'],
        ],
        'tasks': [
            'Cədvəldəki cihazlar üçün ümumi PoE tələbatını hesablayın.',
            'Switch-in PoE büdcəsi 370 W-dırsa, kifayətdirmi? 740 W modeli nə vaxt lazımdır?',
            'Hansı portların <strong>802.3bt</strong> dəstəkləməli olduğunu müəyyənləşdirin.',
            'Kritik cihazlar (AP-lər) üçün port prioritetini düşünün: büdcə çatmayanda hansı cihaz söndürülməlidir?',
            'Real switch-də (və ya sənəddə) <code>show power inline</code> çıxışını oxuyun və <code>power inline never</code> ilə PoE-ni lazımsız portda söndürün.',
        ],
        'verify': '''
show power inline
show power inline gi1/0/10 detail
''',
        'expect': [
            'Tələbat: 24×7 + 4×25.5 + 2×51 = 168 + 102 + 102 = <strong>372 W</strong> — 370 W büdcəni azca aşır.',
            'Həll: 740 W model, ikinci switch və ya kameraları ayrıca PoE injector-a çıxarmaq.',
            'PoE lazım olmayan portlarda (PC-lər) enerji söndürülüb.',
        ],
    },
    {
        'slug': 'wireless',
        'title': 'WLC ilə Korporativ və Qonaq SSID',
        'goal': 'Wireless LAN Controller üzərində iki SSID yaratmaq, onları VLAN-lara bağlamaq və lightweight AP-ləri qoşmaq.',
        'tool': 'Cisco Packet Tracer (WLC-2504, LAP-PT)',
        'time': '50 dəq',
        'level': 'Çətin',
        'topology': '''
  LAP1 ---\\
            SW1 (trunk) ---- WLC        SW1 ---- R1 (DHCP, gateway)
  LAP2 ---/
''',
        'addressing': [
            ['VLAN', 'Məqsəd', 'Subnet'],
            ['99', 'İdarəetmə (WLC, AP)', '10.99.0.0/24'],
            ['10', 'Korporativ SSID "CORP"', '10.10.0.0/24'],
            ['30', 'Qonaq SSID "GUEST"', '10.30.0.0/24'],
        ],
        'tasks': [
            'SW1-də VLAN 99, 10, 30; WLC portunu trunk edin; R1-də subinterfeyslər və hər VLAN üçün DHCP pool (AP-lər üçün VLAN 99-da).',
            'WLC-ə idarəetmə IP-si verin, veb interfeysə daxil olun.',
            'Dynamic interface-lər yaradın: <code>corp</code> → VLAN 10, <code>guest</code> → VLAN 30.',
            'WLAN-lar: <code>CORP</code> (WPA2/WPA3-Personal, sonra Enterprise sınağı üçün), <code>GUEST</code> (ayrı parol). Hər birini uyğun interfeysə bağlayın.',
            'AP-lərin WLC-ə qoşulduğunu (CAPWAP) yoxlayın, noutbukları hər iki SSID-yə qoşun.',
            'Qonaq klientin korporativ şəbəkəyə (10.10.0.0/24) çata bilmədiyini R1-də ACL ilə təmin edin.',
        ],
        'verify': '''
WLC: Monitor → Access Points / Clients
R1# show ip dhcp binding
R1# show access-lists
Noutbuk> ipconfig
''',
        'expect': [
            'AP-lər WLC-də <code>Registered</code> görünür.',
            'CORP klientləri 10.10.0.x, GUEST klientləri 10.30.0.x ünvan alır.',
            'Qonaq şəbəkədən korporativ şəbəkəyə ping bloklanır, internet (və ya R1) əlçatandır.',
        ],
    },
    {
        'slug': 'wireless-security',
        'title': 'WPA2-Enterprise: RADIUS ilə Wi-Fi',
        'goal': 'Paylaşılan parol əvəzinə hər istifadəçinin öz hesabı ilə Wi-Fi-a qoşulmasını (802.1X) qurmaq.',
        'tool': 'Cisco Packet Tracer (WRT300N və ya WLC + Server-PT AAA)',
        'time': '40 dəq',
        'topology': '''
  Noutbuk ~~~ (Wi-Fi) ~~~ [AP / Wireless Router] ---- SW ---- [RADIUS Server 192.168.1.100]
''',
        'tasks': [
            'Server-PT-də <strong>AAA</strong> xidmətini aktivləşdirin: klient (AP) IP-si, shared secret <code>Radius!23</code>, istifadəçilər <code>ali/Pa55</code>, <code>leyla/Pa55</code>.',
            'Wireless router-də təhlükəsizlik rejimini <strong>WPA2-Enterprise</strong> edin, RADIUS server IP və secret yazın.',
            'Noutbukda WPA2-Enterprise profili ilə <code>ali</code> hesabı ilə qoşulun.',
            'Səhv parol ilə qoşulmağa cəhd edin — nəticə nədir?',
            'Eyni şəbəkəni WPA2-Personal ilə müqayisə edin: işçi işdən çıxanda nə etmək lazımdır?',
        ],
        'expect': [
            'Yalnız RADIUS-da olan istifadəçilər qoşula bilir.',
            'Səhv parolla autentifikasiya rədd edilir.',
            'Enterprise rejimdə bir işçinin hesabını söndürmək kifayətdir — hamının parolunu dəyişmək lazım deyil.',
        ],
    },
]
