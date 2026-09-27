# CCNA lab tapşırıqları — IP Connectivity.

LABS = [
    {
        'slug': 'router-basics',
        'title': 'Marşrut Cədvəlini Oxumaq və Longest Match',
        'goal': 'Router-in paketi hansı marşrutla göndərəcəyini longest match, AD və metrika qaydalarına görə proqnozlaşdırmaq.',
        'tool': 'Cisco Packet Tracer',
        'time': '35 dəq',
        'topology': '''
                      /-- (Gi0/1) R2 --- LAN 10.1.1.0/24
 PC --- R1 (Gi0/0) --
                      \\-- (Gi0/2) R3 --- LAN 10.1.0.0/16
''',
        'tasks': [
            'R1-də iki statik marşrut yazın: <code>10.1.0.0/16 → R3</code> və <code>10.1.1.0/24 → R2</code>.',
            'Proqnozlaşdırın və <code>show ip route 10.1.1.50</code> ilə yoxlayın: 10.1.1.50 hansı yolla gedəcək? 10.1.2.50?',
            '<code>0.0.0.0/0 → R2</code> default route əlavə edin; 8.8.8.8 və 10.2.0.1 üçün seçimi izah edin.',
            '10.1.1.0/24 üçün R3-ə ikinci statik marşrutu AD 5 ilə yazın — cədvəldə hansı qalır?',
            '<code>show ip route</code> çıxışındakı kodları (C, L, S, S*, O) və <code>[AD/metric]</code> formatını izah edin.',
        ],
        'verify': '''
show ip route
show ip route 10.1.1.50
show ip route 10.1.2.50
show ip route static
''',
        'expect': [
            '10.1.1.50 → R2 (/24 daha uzun prefiksdir), 10.1.2.50 → R3 (/16).',
            'Siyahıda olmayan şəbəkələr default route ilə gedir.',
            'Eyni prefiks üçün AD-si kiçik olan marşrut cədvələ düşür, digəri floating (ehtiyat) qalır.',
        ],
    },
    {
        'slug': 'static-routing',
        'title': 'Statik, Default və Floating Static Marşrut',
        'goal': 'Filial ilə mərkəz arasında əsas və ehtiyat linki olan statik marşrutlaşdırma qurmaq.',
        'tool': 'Cisco Packet Tracer',
        'time': '45 dəq',
        'topology': '''
 LAN-B 192.168.2.0/24 --- BRANCH (Gi0/1) ---- 10.0.0.0/30 (əsas) ---- (Gi0/1) HQ --- LAN-HQ 192.168.1.0/24
                                 (Gi0/2) ---- 10.0.0.4/30 (ehtiyat) --- (Gi0/2)       \\
                                                                                        ISP 203.0.113.0/30
''',
        'addressing': [
            ['Cihaz', 'Interfeys', 'IP'],
            ['BRANCH', 'Gi0/0 / Gi0/1 / Gi0/2', '192.168.2.1 · 10.0.0.1 /30 · 10.0.0.5 /30'],
            ['HQ', 'Gi0/0 / Gi0/1 / Gi0/2 / Gi0/3', '192.168.1.1 · 10.0.0.2 · 10.0.0.6 · 203.0.113.2 /30'],
            ['ISP', 'Gi0/0', '203.0.113.1 /30 (+ Loopback 8.8.8.8/32)'],
        ],
        'tasks': [
            'BRANCH-da HQ LAN-ı üçün statik marşrut (next-hop 10.0.0.2) və default route yazın.',
            'HQ-da BRANCH LAN-ı üçün marşrut və ISP-yə default route yazın; ISP-də hər iki LAN üçün marşrut (NAT olmadığından).',
            'BRANCH-da ehtiyat link üzərindən <strong>floating static</strong> marşrutlar (AD 200) əlavə edin; HQ-da da eyni.',
            'PC-B-dən 8.8.8.8-ə ping və traceroute edin.',
            'Əsas linki söndürün (BRANCH Gi0/1 shutdown). <code>show ip route</code>-da floating marşrutun aktivləşdiyini göstərin, ping davam etsin.',
            'Linki qaytarın və əsas marşrutun geri qayıtdığını təsdiqləyin.',
        ],
        'verify': '''
show ip route
show ip route static
show ip interface brief
traceroute 8.8.8.8
''',
        'expect': [
            'Normal halda trafik 10.0.0.0/30 üzərindən gedir.',
            'Əsas link kəsiləndə [200/0] marşrutu cədvələ düşür və trafik ehtiyat linkə keçir.',
            'Qeyd: floating static yalnız interfeys <em>down</em> olanda işləyir — uzaqdakı nasazlığı görmək üçün IP SLA lazımdır.',
        ],
        'solution': '''
BRANCH(config)# ip route 192.168.1.0 255.255.255.0 10.0.0.2
BRANCH(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.2
BRANCH(config)# ip route 192.168.1.0 255.255.255.0 10.0.0.6 200
BRANCH(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.6 200
HQ(config)# ip route 192.168.2.0 255.255.255.0 10.0.0.1
HQ(config)# ip route 192.168.2.0 255.255.255.0 10.0.0.5 200
HQ(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1
ISP(config)# ip route 192.168.0.0 255.255.252.0 203.0.113.2
''',
    },
    {
        'slug': 'dynamic-routing',
        'title': 'RIP, OSPF və EIGRP-ni Eyni Topologiyada Müqayisə',
        'goal': 'Eyni şəbəkədə üç protokolu növbə ilə işə salıb seçilən yolları, AD-ni və konvergensiya sürətini müqayisə etmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '60 dəq',
        'level': 'Çətin',
        'topology': '''
          R1 ------ 1 Gbps ------ R2
          |  \\                    |
       10 Mbps  \\ 100 Mbps        | 1 Gbps
          |       \\               |
          R4 ------ 1 Gbps ------ R3 --- LAN 172.16.3.0/24
''',
        'tasks': [
            'Linkləri ünvanlayın (/30) və R1-də <code>bandwidth</code> dəyərlərini sxemə uyğun təyin edin.',
            '<strong>RIPv2</strong> qurun: R1-dən 172.16.3.0/24-ə hansı yol seçilir (hop sayı)?',
            'RIP-i saxlayaraq <strong>OSPF</strong> əlavə edin: marşrut cədvəlində hansı protokol qalır və niyə (AD 110 vs 120)?',
            'OSPF-in seçdiyi yolu cost ilə izah edin; <code>auto-cost reference-bandwidth 10000</code> yazıb fərqi görün.',
            '<strong>EIGRP</strong> əlavə edin: indi hansı protokol qalib gəlir? <code>show ip eigrp topology</code>-də feasible successor varmı?',
            'R1–R2 linkini söndürüb hər protokolun konvergensiya vaxtını (ping -t ilə itən paketlər) müqayisə edin.',
        ],
        'verify': '''
show ip protocols
show ip route
show ip route 172.16.3.0
show ip ospf interface brief
show ip eigrp topology
''',
        'expect': [
            'RIP hop sayına görə 10 Mbps linki də seçə bilir; OSPF/EIGRP bant genişliyini nəzərə alır.',
            'Bir neçə protokol olduqda ən kiçik AD-li (EIGRP 90) marşrut cədvələ düşür.',
            'EIGRP feasible successor olduqda keçid demək olar ki, anidir.',
        ],
    },
    {
        'slug': 'ospf',
        'title': 'Single-Area OSPF, DR/BDR və Default Route',
        'goal': 'Üç router arasında OSPF area 0 qurmaq, DR/BDR seçkisinə təsir etmək və default route-u OSPF ilə yaymaq.',
        'tool': 'Cisco Packet Tracer və ya portalın CLI Simulyatoru (4-cü tapşırıq)',
        'time': '50 dəq',
        'topology': '''
      R1 (Gi0/0) ---\\
                     SW (10.0.123.0/24, broadcast seqment)
      R2 (Gi0/0) ---/|
      R3 (Gi0/0) ----/
 Hər router-də LAN: 192.168.X.0/24 (Gi0/1), R1-də əlavə: ISP-yə default
''',
        'addressing': [
            ['Router', 'Gi0/0', 'Gi0/1 (LAN)', 'Router ID'],
            ['R1', '10.0.123.1 /24', '192.168.1.1 /24', '1.1.1.1'],
            ['R2', '10.0.123.2 /24', '192.168.2.1 /24', '2.2.2.2'],
            ['R3', '10.0.123.3 /24', '192.168.3.1 /24', '3.3.3.3'],
        ],
        'tasks': [
            'Hər router-də OSPF prosesi 1, router-id və <code>network</code> əmrləri ilə bütün interfeysləri area 0-a daxil edin.',
            'LAN interfeyslərini <code>passive-interface</code> edin.',
            '<code>show ip ospf neighbor</code>: kim DR, kim BDR? Seçkini izah edin.',
            'R3-ü DR etmək üçün Gi0/0-da <code>ip ospf priority 255</code>, R1-də 0 yazın; qonşuluğu <code>clear ip ospf process</code> ilə yeniləyin.',
            'R1-də <code>ip route 0.0.0.0 0.0.0.0 Null0</code> (ISP simulyasiyası) və <code>default-information originate</code>; R2/R3-də <code>O*E2</code> marşrutunu tapın.',
            'Bütün LAN-lar arasında ping edin.',
        ],
        'verify': '''
show ip ospf neighbor
show ip ospf interface gi0/0
show ip route ospf
show ip protocols
show ip ospf database
''',
        'expect': [
            'Qonşuluqlar FULL/DR, FULL/BDR, 2WAY/DROTHER vəziyyətindədir.',
            'Priority dəyişikliyindən sonra R3 DR-dir, R1 heç vaxt DR olmur.',
            'R2 və R3-də <code>O*E2 0.0.0.0/0</code> görünür.',
        ],
        'solution': '''
R1(config)# router ospf 1
R1(config-router)# router-id 1.1.1.1
R1(config-router)# network 10.0.123.0 0.0.0.255 area 0
R1(config-router)# network 192.168.1.0 0.0.0.255 area 0
R1(config-router)# passive-interface gi0/1
R1(config-router)# default-information originate
R1(config)# ip route 0.0.0.0 0.0.0.0 Null0
R1(config)# interface gi0/0
R1(config-if)# ip ospf priority 0
R3(config)# interface gi0/0
R3(config-if)# ip ospf priority 255
R1# clear ip ospf process
''',
    },
    {
        'slug': 'ospf-multiarea',
        'title': 'Multi-Area OSPF və Qonşuluq Problemləri',
        'goal': 'ABR ilə iki area qurmaq və qəsdən yaradılmış 4 qonşuluq xətasını tapıb düzəltmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '60 dəq',
        'level': 'Çətin',
        'topology': '''
  R1 (area 1) ---- 10.1.12.0/30 ---- R2 (ABR) ---- 10.0.23.0/30 ---- R3 (area 0)
  LAN 172.16.1.0/24                                                  LAN 172.16.3.0/24
''',
        'tasks': [
            'R1–R2 linkini area 1, R2–R3 linkini area 0-a daxil edin; LAN-lar öz area-sında.',
            'R3-də <code>O IA</code> marşrutunu tapın, R2-nin ABR olduğunu <code>show ip ospf border-routers</code> və <code>show ip protocols</code> ilə göstərin.',
            'Qonşuluq xətaları yaradın və hər birinin simptomunu yazın: (1) R1-də hello interval 5; (2) R1–R2-də fərqli area; (3) fərqli subnet maskası; (4) R3-də duplicate router-id.',
            'Hər xəta üçün <code>show ip ospf interface</code> və <code>debug ip ospf adj</code> çıxışında ipucunu tapın, sonra düzəldin.',
            'R2-də area 1 üçün xülasə: <code>area 1 range 172.16.0.0 255.255.252.0</code> (əlavə LAN-lar yaradaraq).',
        ],
        'verify': '''
show ip ospf neighbor
show ip ospf interface brief
show ip ospf interface gi0/0
show ip route ospf
debug ip ospf adj
''',
        'expect': [
            'R3-də area 1 şəbəkələri <code>O IA</code> kimi görünür.',
            'Hello/dead uyğunsuzluğu, area mismatch və maska fərqi qonşuluğu qurmur; duplicate router-id log mesajı verir.',
            'Xülasədən sonra area 0-da bir <code>/22</code> marşrutu qalır.',
        ],
    },
    {
        'slug': 'summarization',
        'title': 'Filial Marşrutlarının Xülasəsi',
        'goal': 'Bir neçə filial şəbəkəsini bir xülasə marşrutuna birləşdirmək və marşrut cədvəlinin ölçüsünü azaltmaq.',
        'tool': 'Kağız + Cisco Packet Tracer',
        'time': '35 dəq',
        'topology': '''
 BRANCH (Loopback 10.10.0.1/24 ... 10.10.7.1/24) ---- HQ ---- CORE
''',
        'tasks': [
            'BRANCH-da 8 loopback yaradın: <code>10.10.0.1/24</code> … <code>10.10.7.1/24</code>.',
            'Kağız üzərində bu 8 şəbəkənin ən kiçik xülasəsini binar üsulla tapın.',
            'HQ-da əvvəlcə 8 ayrı statik marşrut yazın, sonra onları bir xülasə marşrutu ilə əvəz edin; CORE-da HQ-ya yalnız bir marşrut göndərin.',
            '10.10.8.0/24 əlavə etsəniz, xülasəni necə dəyişmək lazımdır? Xülasə hansı artıq ünvanları əhatə etməyə başlayır?',
            'Xülasə marşrutu olan router-də <code>Null0</code>-a marşrutun niyə tövsiyə olunduğunu (routing loop) izah edin.',
        ],
        'verify': '''
show ip route
show ip route 10.10.5.1
ping 10.10.7.1 source <CORE interfeysi>
''',
        'expect': [
            'Xülasə: <strong>10.10.0.0/21</strong> (255.255.248.0).',
            '10.10.8.0 əlavə olunarsa, /20 lazımdır və 10.10.9–15.x də əhatə olunur.',
            'CORE-un marşrut cədvəlində 8 əvəzinə 1 qeyd var.',
        ],
        'solution': '''
HQ(config)# ip route 10.10.0.0 255.255.248.0 <BRANCH next-hop>
CORE(config)# ip route 10.10.0.0 255.255.248.0 <HQ next-hop>
BRANCH(config)# ip route 10.10.0.0 255.255.248.0 Null0   ! loop qoruması (istəyə bağlı)
''',
    },
    {
        'slug': 'fhrp',
        'title': 'HSRP ilə Ehtiyat Gateway',
        'goal': 'İki router arasında HSRP qurmaq, interfeys izləməsi ilə uplink kəsiləndə Active rolunun keçdiyini görmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '45 dəq',
        'topology': '''
            ISP (Lo 8.8.8.8)
           /            \\
   (Gi0/1) R1          R2 (Gi0/1)
   (Gi0/0)  \\          /  (Gi0/0)
              ---- SW ----
                    |
                   PC (gateway 192.168.1.1)
''',
        'addressing': [
            ['Cihaz', 'Gi0/0 (LAN)', 'Qeyd'],
            ['R1', '192.168.1.2 /24', 'HSRP priority 110, preempt'],
            ['R2', '192.168.1.3 /24', 'HSRP priority 100'],
            ['Virtual IP', '192.168.1.1', 'PC-lərin gateway-i'],
        ],
        'tasks': [
            'Hər iki router-də LAN interfeysində HSRP qrup 1, versiya 2, virtual IP 192.168.1.1 qurun; R1 priority 110 + preempt.',
            'PC-dən <code>arp -a</code>: gateway-in MAC-ı <code>0000.0c9f.f001</code> (HSRPv2) — virtual MAC-dır.',
            'R1-də <code>track 1 interface gi0/1 line-protocol</code> və <code>standby 1 track 1 decrement 20</code>.',
            'PC-dən <code>ping -t 8.8.8.8</code> işlədərkən R1 Gi0/1-i söndürün: R2 Active olur, neçə paket itir?',
            'Gi0/1-i qaytarın — preempt sayəsində R1 yenidən Active olur.',
        ],
        'verify': '''
show standby brief
show standby
show track
PC> arp -a
''',
        'expect': [
            'Normal halda R1 Active, R2 Standby.',
            'Uplink kəsiləndə R1 priority 90-a düşür və R2 Active olur.',
            'PC-nin gateway ayarı və ARP cədvəli heç dəyişmir.',
        ],
        'solution': '''
R1(config)# track 1 interface gi0/1 line-protocol
R1(config)# interface gi0/0
R1(config-if)# standby version 2
R1(config-if)# standby 1 ip 192.168.1.1
R1(config-if)# standby 1 priority 110
R1(config-if)# standby 1 preempt
R1(config-if)# standby 1 track 1 decrement 20
R2(config)# interface gi0/0
R2(config-if)# standby version 2
R2(config-if)# standby 1 ip 192.168.1.1
R2(config-if)# standby 1 preempt
''',
    },
    {
        'slug': 'wan',
        'title': 'GRE Tunel ilə Filialları Birləşdirmək',
        'goal': 'İnternet üzərində iki ofis arasında GRE tunel qurmaq və tunel üzərindən OSPF işlətmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '45 dəq',
        'topology': '''
 LAN 192.168.1.0/24 --- HQ (Gi0/1 203.0.113.2) ---- ISP ---- (Gi0/1 198.51.100.2) BRANCH --- LAN 192.168.2.0/24
                          Tunnel0 172.16.0.1/30 ============= Tunnel0 172.16.0.2/30
''',
        'tasks': [
            'ISP router-i ilə hər iki ofisin public IP-lərini qurun, ofislərdə ISP-yə default route yazın; public IP-lər arasında ping olmalıdır.',
            'HQ və BRANCH-da <code>interface Tunnel0</code> yaradın: tunel IP-si, <code>tunnel source</code> və <code>tunnel destination</code>.',
            'Tunel üzərindən ping edin (<code>172.16.0.2</code>).',
            'OSPF-i yalnız tunel və LAN interfeyslərində işlədin (public interfeysləri daxil etməyin!).',
            'PC-HQ → PC-BRANCH ping və traceroute: tunelin tək hop kimi göründüyünü izah edin.',
            'Bu tunelin şifrələnmədiyini qeyd edin — real həyatda GRE over IPsec lazımdır.',
        ],
        'verify': '''
show interfaces tunnel 0
show ip interface brief | include Tunnel
show ip ospf neighbor
show ip route ospf
traceroute 192.168.2.10
''',
        'expect': [
            'Tunnel0 <code>up/up</code>, OSPF qonşuluğu tunel üzərindən FULL.',
            'LAN marşrutları next-hop kimi tunel IP-si ilə öyrənilir.',
            'Public interfeyslər OSPF-ə daxil edilmədiyi üçün recursive routing problemi yaranmır.',
        ],
        'solution': '''
HQ(config)# interface tunnel 0
HQ(config-if)# ip address 172.16.0.1 255.255.255.252
HQ(config-if)# tunnel source gi0/1
HQ(config-if)# tunnel destination 198.51.100.2
HQ(config)# router ospf 1
HQ(config-router)# network 172.16.0.0 0.0.0.3 area 0
HQ(config-router)# network 192.168.1.0 0.0.0.255 area 0
! BRANCH: 172.16.0.2, destination 203.0.113.2, network 192.168.2.0
''',
    },
]
