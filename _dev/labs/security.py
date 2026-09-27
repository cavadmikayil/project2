# CCNA lab tapşırıqları — Security Fundamentals.

LABS = [
    {
        'slug': 'security-threats',
        'title': 'Şəbəkə Təhlükəsizliyi Auditi',
        'goal': 'Konfiqurasiya olunmuş şəbəkədə zəif nöqtələri tapmaq, risk səviyyəsinə görə sıralamaq və düzəliş planı hazırlamaq.',
        'tool': 'Cisco Packet Tracer (müəllimin və ya yoldaşınızın "zəif" topologiyası) + audit cədvəli',
        'time': '45 dəq',
        'tasks': [
            'Router və switch-lərdə <code>show running-config</code>-u oxuyun: Telnet açıqdırmı, parollar açıq mətndədirmi, <code>enable password</code> yoxsa <code>enable secret</code>?',
            'İstifadə olunmayan portlar açıqdırmı, VLAN 1-də istifadəçi varmı, trunk-larda DTP işləyirmi?',
            'CDP internetə baxan interfeysdə aktivdirmi? HTTP server açıqdırmı (<code>ip http server</code>)?',
            'Port security, DHCP snooping, BPDU Guard varmı?',
            'Hər tapıntını cədvələ yazın: təhdid, nəticə, risk (yüksək/orta/aşağı), düzəliş əmri.',
            'Ən yüksək riskli 5 problemi düzəldin və yenidən yoxlayın.',
        ],
        'verify': '''
show running-config | include password|secret|transport|http
show ip interface brief
show interfaces status
show interfaces trunk
show cdp interface
''',
        'expect': [
            'Ən azı 8 zəif nöqtə tapılıb və təsnif edilib.',
            'Telnet, açıq mətnli parollar və DTP ilə trunk düzəldilib.',
            'Audit hesabatı texniki olmayan menecerin də başa düşəcəyi dildə yazılıb.',
        ],
    },
    {
        'slug': 'ssh-security',
        'title': 'SSH-only İdarəetmə və Login Qoruması',
        'goal': 'Cihazı yalnız SSHv2 ilə, yerli hesablar və idarəetmə şəbəkəsi məhdudiyyəti ilə idarə olunan hala gətirmək.',
        'tool': 'Cisco Packet Tracer və ya portalın CLI Simulyatoru (3-cü tapşırıq)',
        'time': '35 dəq',
        'topology': '''
 Admin-PC 10.0.99.10 --- SW --- (Gi0/0 10.0.99.1) R1 (Gi0/1 192.168.1.1) --- User-PC 192.168.1.10
''',
        'tasks': [
            'R1-də hostname, <code>ip domain-name lab.local</code>, <code>crypto key generate rsa modulus 2048</code>, <code>ip ssh version 2</code>.',
            '<code>username admin privilege 15 secret ...</code> yaradın, <code>security passwords min-length 10</code>.',
            'VTY xətlərində <code>login local</code>, <code>transport input ssh</code>, <code>exec-timeout 5 0</code>.',
            'Yalnız 10.0.99.0/24-dən girişə icazə verən ACL yazıb <code>access-class</code> ilə tətbiq edin.',
            '<code>login block-for 120 attempts 3 within 60</code> — User-PC-dən 3 səhv cəhddən sonra blokun işlədiyini göstərin.',
            'Admin-PC-dən <code>ssh -l admin 10.0.99.1</code> uğurlu, Telnet və User-PC-dən SSH uğursuz olmalıdır.',
        ],
        'verify': '''
show ip ssh
show ssh
show login
show running-config | section line vty
show access-lists
''',
        'expect': [
            'SSH version 2 aktivdir, Telnet rədd edilir.',
            'İdarəetmə şəbəkəsindən kənar SSH cəhdləri ACL-də match olur.',
            'Brute force cəhdindən sonra router quiet-mode-a keçir.',
        ],
        'solution': '''
R1(config)# ip domain-name lab.local
R1(config)# crypto key generate rsa modulus 2048
R1(config)# ip ssh version 2
R1(config)# username admin privilege 15 secret Adm1n-Parol!
R1(config)# security passwords min-length 10
R1(config)# ip access-list standard MGMT
R1(config-std-nacl)# permit 10.0.99.0 0.0.0.255
R1(config)# line vty 0 4
R1(config-line)# login local
R1(config-line)# transport input ssh
R1(config-line)# exec-timeout 5 0
R1(config-line)# access-class MGMT in
R1(config)# login block-for 120 attempts 3 within 60
''',
    },
    {
        'slug': 'aaa',
        'title': 'AAA: TACACS+ Server və Yerli Fallback',
        'goal': 'Cihaz girişini mərkəzi TACACS+ serverinə bağlamaq və server əlçatmaz olanda yerli hesabla girişi saxlamaq.',
        'tool': 'Cisco Packet Tracer (Server-PT AAA xidməti)',
        'time': '40 dəq',
        'topology': '''
 Admin-PC --- SW --- R1 (192.168.1.1) --- AAA Server (192.168.1.100, TACACS+)
''',
        'tasks': [
            'Server-PT-də AAA: network configuration-a R1-i əlavə edin (IP, key <code>Tacacs!23</code>, TACACS), istifadəçi <code>netadmin</code> yaradın.',
            'R1-də <code>aaa new-model</code>, TACACS+ server tərifi və key.',
            '<code>aaa authentication login default group tacacs+ local</code> — əvvəl server, əlçatmazdırsa yerli baza.',
            'Yerli ehtiyat hesabı <code>username breakglass secret ...</code> yaradın.',
            'Admin-PC-dən <code>netadmin</code> ilə SSH/Telnet girişini yoxlayın.',
            'Serveri söndürün və <code>breakglass</code> ilə girişin işlədiyini göstərin.',
        ],
        'verify': '''
show aaa servers
show tacacs
show running-config | section aaa
debug aaa authentication
''',
        'expect': [
            'Server işləyəndə yalnız TACACS+ hesabları qəbul olunur.',
            'Server əlçatmaz olanda yerli hesabla giriş mümkündür.',
            'Konsol xəttinin də eyni siyahı ilə qorunduğu yoxlanılıb (özünüzü kilidləməyin!).',
        ],
        'solution': '''
R1(config)# username breakglass privilege 15 secret Br3ak-Gl4ss!
R1(config)# aaa new-model
R1(config)# tacacs server TAC1
R1(config-server-tacacs)# address ipv4 192.168.1.100
R1(config-server-tacacs)# key Tacacs!23
R1(config)# aaa authentication login default group tacacs+ local
R1(config)# aaa authorization exec default group tacacs+ local
R1(config)# line vty 0 4
R1(config-line)# login authentication default
! Köhnə Packet Tracer versiyalarında: tacacs-server host 192.168.1.100 key Tacacs!23
''',
    },
    {
        'slug': 'port-security',
        'title': 'Sticky MAC və Violation Rejimləri',
        'goal': 'İstifadəçi portlarında port security qurmaq və üç violation rejiminin fərqini praktikada görmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '35 dəq',
        'topology': '''
 PC1 (Fa0/1) \\
 PC2 (Fa0/2) --- SW1 --- R1
 Hub (Fa0/3) --- PC3, PC4, PC5
''',
        'tasks': [
            'Fa0/1–3 portlarını access edin və port security aktivləşdirin: maximum 1, sticky.',
            'PC1 ilə ping edin — MAC-ın running-config-ə sticky kimi yazıldığını göstərin.',
            'PC1-i ayırıb başqa PC qoşun (fərqli MAC): shutdown rejimində port <code>err-disabled</code> olur.',
            'Fa0/3-də hub arxasında 3 PC: maximum 2, violation <code>restrict</code> — üçüncü PC-nin trafikinin atıldığını və sayğacın artdığını göstərin.',
            'Eyni portda <code>protect</code> rejimini sınayın — sayğac artmır.',
            'err-disabled portu əl ilə və avtomatik (errdisable recovery) bərpa edin.',
        ],
        'verify': '''
show port-security
show port-security interface fa0/1
show port-security address
show interfaces status err-disabled
show running-config interface fa0/1
''',
        'expect': [
            'Sticky MAC config-də görünür və <code>write</code>-dan sonra daimi olur.',
            'Restrict: port açıq, Security Violation Count artır; Protect: sayğac artmır; Shutdown: err-disabled.',
            'Recovery-dən sonra port avtomatik açılır.',
        ],
        'solution': '''
SW1(config)# interface range fa0/1 - 2
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport port-security
SW1(config-if-range)# switchport port-security maximum 1
SW1(config-if-range)# switchport port-security mac-address sticky
SW1(config)# interface fa0/3
SW1(config-if)# switchport mode access
SW1(config-if)# switchport port-security
SW1(config-if)# switchport port-security maximum 2
SW1(config-if)# switchport port-security violation restrict
SW1(config)# errdisable recovery cause psecure-violation
SW1(config)# errdisable recovery interval 60
''',
    },
    {
        'slug': 'dhcp-snooping',
        'title': 'Rogue DHCP Serveri Dayandırmaq',
        'goal': 'Şəbəkəyə qoşulmuş saxta DHCP serverin klientlərə ünvan paylamasını DHCP snooping ilə bloklamaq.',
        'tool': 'Cisco Packet Tracer',
        'time': '35 dəq',
        'topology': '''
 R1 (DHCP server, 192.168.1.1) ---(Gi0/1)--- SW1 ---(Fa0/1)--- PC1
                                              |---(Fa0/2)--- PC2
                                              |---(Fa0/3)--- Rogue-Server (DHCP: 10.66.66.0/24)
''',
        'tasks': [
            'R1-də 192.168.1.0/24 üçün DHCP pool qurun. Rogue-Server-də DHCP xidmətini aktivləşdirin (pool 10.66.66.0/24, gateway 10.66.66.1).',
            'PC-lərdə bir neçə dəfə <code>ipconfig /renew</code> — bəziləri saxta ünvan alır. Nəticəni yazın.',
            'SW1-də <code>ip dhcp snooping</code>, <code>ip dhcp snooping vlan 1</code>, Gi0/1-də <code>trust</code>.',
            'Packet Tracer/Cisco-da Option 82 problemi olmaması üçün <code>no ip dhcp snooping information option</code>.',
            'Access portlarda <code>limit rate 10</code>. PC-lərdə yenidən renew — hamısı yalnız R1-dən ünvan alır.',
            'Binding cədvəlinə baxın və DAI üçün bu cədvəlin əhəmiyyətini izah edin.',
        ],
        'verify': '''
show ip dhcp snooping
show ip dhcp snooping binding
show ip dhcp snooping statistics
R1# show ip dhcp binding
''',
        'expect': [
            'Snooping-dən sonra bütün PC-lər 192.168.1.x alır.',
            'Rogue serverin OFFER paketləri untrusted portda atılır.',
            'Binding cədvəlində hər PC-nin IP, MAC, VLAN və portu var.',
        ],
        'solution': '''
SW1(config)# ip dhcp snooping
SW1(config)# ip dhcp snooping vlan 1
SW1(config)# no ip dhcp snooping information option
SW1(config)# interface gi0/1
SW1(config-if)# ip dhcp snooping trust
SW1(config)# interface range fa0/1 - 3
SW1(config-if-range)# ip dhcp snooping limit rate 10
''',
    },
    {
        'slug': 'l2-security',
        'title': 'Dynamic ARP Inspection',
        'goal': 'DHCP snooping binding cədvəli əsasında ARP spoofing-in qarşısını almaq.',
        'tool': 'Real switch / CML (Packet Tracer DAI-ni məhdud dəstəkləyir)',
        'time': '40 dəq',
        'level': 'Çətin',
        'topology': '''
 R1 (gateway 192.168.10.1, DHCP) ---(Gi0/1 trust)--- SW1 ---(Fa0/1)--- PC1 (DHCP)
                                                       |---(Fa0/2)--- Attacker (Kali: arpspoof)
                                                       |---(Fa0/3)--- Printer (statik 192.168.10.50)
''',
        'tasks': [
            'Əvvəlki labdakı kimi DHCP snooping-i VLAN 10 üçün aktivləşdirin.',
            '<code>ip arp inspection vlan 10</code>; uplink-i <code>ip arp inspection trust</code> edin.',
            'Statik IP-li printer ARP inspection tərəfindən bloklanır — səbəbini izah edin və <strong>ARP ACL</strong> ilə icazə verin.',
            'Attacker-dən gateway-i saxtalaşdıran ARP (<code>arpspoof -i eth0 -t 192.168.10.11 192.168.10.1</code>) göndərin — log-da <code>%SW_DAI-4-DHCP_SNOOPING_DENY</code> mesajını tapın.',
            'Əlavə: <code>ip arp inspection validate src-mac dst-mac ip</code>.',
        ],
        'verify': '''
show ip arp inspection
show ip arp inspection statistics vlan 10
show ip dhcp snooping binding
show logging | include DAI
''',
        'expect': [
            'Saxta ARP paketləri atılır, PC1-in ARP cədvəlində gateway-in real MAC-ı qalır.',
            'Printer ARP ACL sayəsində işləyir.',
            'Statistikada Dropped sayğacı artır.',
        ],
        'solution': '''
SW1(config)# ip dhcp snooping
SW1(config)# ip dhcp snooping vlan 10
SW1(config)# ip arp inspection vlan 10
SW1(config)# arp access-list STATIC-HOSTS
SW1(config-arp-nacl)# permit ip host 192.168.10.50 mac host <printer-MAC>
SW1(config)# ip arp inspection filter STATIC-HOSTS vlan 10
SW1(config)# interface gi0/1
SW1(config-if)# ip dhcp snooping trust
SW1(config-if)# ip arp inspection trust
''',
    },
    {
        'slug': 'acl',
        'title': 'Standart, Genişləndirilmiş və VTY ACL',
        'goal': 'Tələblərə uyğun ACL yazmaq, düzgün interfeys və istiqamətə tətbiq etmək və hər qaydanı sınaqdan keçirmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '50 dəq',
        'topology': '''
 VLAN 10 İşçilər 192.168.10.0/24 --\\
 VLAN 20 Qonaq   192.168.20.0/24 --- R1 (router-on-a-stick) --- (Gi0/1) Server-LAN 10.0.0.0/24
 VLAN 99 Admin   192.168.99.0/24 --/                               Web 10.0.0.10, DNS 10.0.0.53
''',
        'tasks': [
            'Tələb 1: <strong>Qonaq</strong> şəbəkəsi Server-LAN-a heç çıxmasın, yalnız DNS (UDP 53) istifadə edə bilsin.',
            'Tələb 2: <strong>İşçilər</strong> Web serverə yalnız HTTP/HTTPS ilə çatsın, ping icazəlidir.',
            'Tələb 3: Router-ə SSH yalnız <strong>Admin</strong> VLAN-dan.',
            'Hər tələb üçün ACL növünü, adını, interfeysi və istiqaməti planlaşdırın (mənbəyə yaxın).',
            'Named extended ACL-lər yazın, qaydaları <code>remark</code> ilə izah edin və tətbiq edin.',
            'Hər qaydanı PC-lərdən sınayın və <code>show access-lists</code>-də match sayğaclarını izləyin.',
        ],
        'verify': '''
show access-lists
show ip interface gi0/0.20 | include access list
show running-config | section access-list
''',
        'expect': [
            'Qonaq PC-dən web server açılmır, DNS sorğusu işləyir.',
            'İşçi PC-dən web açılır, FTP/Telnet bloklanır.',
            'Yalnız Admin VLAN-dan SSH mümkündür.',
        ],
        'solution': '''
ip access-list extended GUEST-IN
 remark Qonaq: yalniz DNS, server LAN-a qalan hec ne
 permit udp 192.168.20.0 0.0.0.255 host 10.0.0.53 eq 53
 deny   ip 192.168.20.0 0.0.0.255 10.0.0.0 0.0.0.255
 permit ip 192.168.20.0 0.0.0.255 any
ip access-list extended STAFF-IN
 permit tcp 192.168.10.0 0.0.0.255 host 10.0.0.10 eq 80
 permit tcp 192.168.10.0 0.0.0.255 host 10.0.0.10 eq 443
 permit icmp 192.168.10.0 0.0.0.255 10.0.0.0 0.0.0.255
 permit udp 192.168.10.0 0.0.0.255 host 10.0.0.53 eq 53
 deny   ip 192.168.10.0 0.0.0.255 10.0.0.0 0.0.0.255
 permit ip 192.168.10.0 0.0.0.255 any
ip access-list standard MGMT
 permit 192.168.99.0 0.0.0.255
interface gi0/0.20
 ip access-group GUEST-IN in
interface gi0/0.10
 ip access-group STAFF-IN in
line vty 0 4
 access-class MGMT in
''',
    },
    {
        'slug': 'time-acl',
        'title': 'İş Saatlarına Görə İnternet Girişi',
        'goal': 'Time-range ilə qonaq şəbəkəsinə internet girişini yalnız iş saatlarında açmaq.',
        'tool': 'Cisco Packet Tracer (router saatı əl ilə təyin olunur)',
        'time': '30 dəq',
        'tasks': [
            'R1-də saatı təyin edin (<code>clock set</code>) və ya NTP qurun.',
            '<code>time-range WORK-HOURS</code>: <code>periodic weekdays 9:00 to 18:00</code>.',
            'Extended ACL: qonaq şəbəkəsindən HTTP/HTTPS yalnız bu time-range-də icazəli, qalanı deny.',
            'Saatı 10:00 edib sınayın (icazə), sonra 20:00 edib sınayın (bloklanır).',
            '<code>show time-range</code> ilə vəziyyətin <code>active</code>/<code>inactive</code> dəyişdiyini göstərin.',
        ],
        'verify': '''
show clock
show time-range
show access-lists GUEST-TIME
''',
        'expect': [
            'İş saatlarında ACL qaydası aktivdir, sonra (inactive) qeydi görünür.',
            'Saat düzgün deyilsə, time-based ACL gözlənilməz işləyir — NTP-nin vacibliyi.',
        ],
        'solution': '''
R1(config)# time-range WORK-HOURS
R1(config-time-range)# periodic weekdays 9:00 to 18:00
R1(config)# ip access-list extended GUEST-TIME
R1(config-ext-nacl)# permit udp 192.168.20.0 0.0.0.255 any eq 53
R1(config-ext-nacl)# permit tcp 192.168.20.0 0.0.0.255 any eq 80 time-range WORK-HOURS
R1(config-ext-nacl)# permit tcp 192.168.20.0 0.0.0.255 any eq 443 time-range WORK-HOURS
R1(config-ext-nacl)# deny ip any any
R1(config)# interface gi0/0.20
R1(config-if)# ip access-group GUEST-TIME in
''',
    },
    {
        'slug': 'firewall',
        'title': 'Zone-Based Firewall: Inside, Outside, DMZ',
        'goal': 'Router-də zone-based firewall qurmaq: daxildən internetə stateful icazə, internetdən yalnız DMZ veb serverə.',
        'tool': 'Cisco Packet Tracer (ISR 4331/2911, securityk9 lisenziyası)',
        'time': '60 dəq',
        'level': 'Çətin',
        'topology': '''
 INSIDE 192.168.1.0/24 --- (Gi0/0) R1 (Gi0/2) --- OUTSIDE (ISP, Internet-PC)
                                   (Gi0/1)
                                      |
                              DMZ 172.16.1.0/24 — Web 172.16.1.10
''',
        'tasks': [
            '<code>license boot module c2900 technology-package securityk9</code> (lazımdırsa) və reload.',
            'Üç zona yaradın: INSIDE, OUTSIDE, DMZ; interfeysləri zonalara təyin edin.',
            'Class-map: INSIDE → OUTSIDE üçün tcp, udp, icmp; policy-map-da <code>inspect</code>.',
            'OUTSIDE → DMZ: yalnız HTTP (tcp 80) web serverə — ACL + class-map + inspect.',
            'Zone-pair-lər yaradıb policy-ləri tətbiq edin.',
            'Sınaq: daxildən internet işləyir (cavab trafiki avtomatik icazəlidir), internetdən DMZ web açılır, internetdən INSIDE-a ping bloklanır.',
        ],
        'verify': '''
show zone security
show zone-pair security
show policy-map type inspect zone-pair sessions
''',
        'expect': [
            'Stateful inspection sayəsində daxildən başlanan bağlantıların cavabları keçir.',
            'Xaricdən yalnız DMZ-dəki veb serverin 80 portu əlçatandır.',
            'Zone-pair olmayan istiqamətlərdə trafik defolt olaraq bloklanır.',
        ],
        'solution': '''
zone security INSIDE
zone security OUTSIDE
zone security DMZ
class-map type inspect match-any IN-OUT-CLASS
 match protocol tcp
 match protocol udp
 match protocol icmp
policy-map type inspect IN-OUT-POLICY
 class type inspect IN-OUT-CLASS
  inspect
ip access-list extended TO-WEB
 permit tcp any host 172.16.1.10 eq 80
class-map type inspect match-all OUT-DMZ-CLASS
 match access-group name TO-WEB
policy-map type inspect OUT-DMZ-POLICY
 class type inspect OUT-DMZ-CLASS
  inspect
zone-pair security IN-OUT source INSIDE destination OUTSIDE
 service-policy type inspect IN-OUT-POLICY
zone-pair security OUT-DMZ source OUTSIDE destination DMZ
 service-policy type inspect OUT-DMZ-POLICY
interface gi0/0
 zone-member security INSIDE
interface gi0/1
 zone-member security DMZ
interface gi0/2
 zone-member security OUTSIDE
''',
    },
    {
        'slug': 'vpn',
        'title': 'Site-to-Site IPsec VPN',
        'goal': 'İnternet üzərindən iki ofis arasında IKE/IPsec tunel qurmaq və yalnız ofislərarası trafiki şifrələmək.',
        'tool': 'Cisco Packet Tracer (securityk9)',
        'time': '60 dəq',
        'level': 'Çətin',
        'topology': '''
 LAN 192.168.1.0/24 --- R1 (Gi0/1 203.0.113.2) ---- ISP ---- (Gi0/1 198.51.100.2) R3 --- LAN 192.168.3.0/24
''',
        'tasks': [
            'ISP üzərindən public IP-lər arasında əlçatanlığı təmin edin (default route-lar).',
            'Maraqlı trafik ACL-i: <code>192.168.1.0/24 → 192.168.3.0/24</code> (R3-də əksinə).',
            'ISAKMP policy (phase 1): AES 256, SHA, pre-share, DH group 14; <code>crypto isakmp key</code>.',
            'Transform-set (phase 2): <code>esp-aes 256 esp-sha-hmac</code>; crypto map ilə peer, transform-set və ACL-i birləşdirib xarici interfeysə tətbiq edin.',
            'LAN-dan LAN-a ping — ilk paket itə bilər (tunel qurulur). Sayğacların artdığını göstərin.',
            'LAN-dan internetə (ISP loopback) gedən trafikin şifrələnmədiyini izah edin.',
        ],
        'verify': '''
show crypto isakmp sa
show crypto ipsec sa
show crypto map
show access-lists 110
''',
        'expect': [
            'ISAKMP SA <code>QM_IDLE</code> vəziyyətindədir.',
            '<code>#pkts encaps/decaps</code> sayğacları ping ilə artır.',
            'Yalnız ACL-ə düşən trafik tunelə girir.',
        ],
        'solution': '''
R1(config)# access-list 110 permit ip 192.168.1.0 0.0.0.255 192.168.3.0 0.0.0.255
R1(config)# crypto isakmp policy 10
R1(config-isakmp)# encryption aes 256
R1(config-isakmp)# hash sha
R1(config-isakmp)# authentication pre-share
R1(config-isakmp)# group 14
R1(config)# crypto isakmp key VpnKey!23 address 198.51.100.2
R1(config)# crypto ipsec transform-set TS esp-aes 256 esp-sha-hmac
R1(config)# crypto map VPN-MAP 10 ipsec-isakmp
R1(config-crypto-map)# set peer 198.51.100.2
R1(config-crypto-map)# set transform-set TS
R1(config-crypto-map)# match address 110
R1(config)# interface gi0/1
R1(config-if)# crypto map VPN-MAP
! R3 əks istiqamətdə: ACL 192.168.3.0 → 192.168.1.0, peer 203.0.113.2
''',
    },
]
