# CCNA lab tapşırıqları — Network Fundamentals.
# Hər lab dərsin fayl adı (slug) ilə bağlanır və build zamanı dərsin sonuna əlavə olunur.
# Sahələr: slug, title, goal, tool, time, level, topology, addressing, tasks, verify, expect, solution, note
# tasks / expect / goal içində HTML (<code>, <strong>) istifadə etmək olar; topology / verify / solution düz mətndir.

LABS = [
    {
        'slug': 'osi-model',
        'title': 'Wireshark ilə Qatları Görmək',
        'goal': 'Bir veb sorğusunun Ethernet, IP, TCP və HTTP başlıqlarını real paketdə tapmaq və OSI qatlarına uyğunlaşdırmaq.',
        'tool': 'Wireshark (kompüterinizdə) və ya Packet Tracer Simulation Mode',
        'time': '30 dəq',
        'level': 'Başlanğıc',
        'topology': '''
[Kompüteriniz] ---- [Ev/ofis router] ---- (İnternet) ---- [neverssl.com]
   Wireshark
''',
        'tasks': [
            'Wireshark-ı işə salın, aktiv interfeysi (Wi-Fi və ya Ethernet) seçib tutmağa başlayın.',
            'Brauzerdə <code>http://neverssl.com</code> açın (şifrələnməmiş HTTP — başlıqları görmək üçün), sonra tutmanı dayandırın.',
            'Filtr sahəsinə <code>http.request</code> yazın və ilk <code>GET</code> paketini seçin.',
            'Paket detallarında qatları tapın: <strong>Ethernet II</strong> (L2 — mənbə və təyinat MAC), <strong>Internet Protocol</strong> (L3 — IP-lər, TTL), <strong>TCP</strong> (L4 — portlar, seq/ack), <strong>HTTP</strong> (L7 — Host, User-Agent).',
            'Təyinat MAC ünvanının saytın deyil, <strong>router-inizin</strong> MAC-ı olduğunu <code>arp -a</code> ilə yoxlayın və səbəbini izah edin.',
            'Filtr <code>tcp.flags.syn == 1</code> ilə 3-way handshake-in üç paketini tapın.',
        ],
        'verify': '''
ipconfig /all          (Windows)  |  ip a        (Linux/macOS)
arp -a                 — gateway-in MAC ünvanı
Wireshark filtrləri:   http.request    tcp.flags.syn == 1    ip.addr == <server IP>
''',
        'expect': [
            'Hər qatın başlığını adlandırıb əsas sahəsini (MAC, IP, port, Host) göstərə bilirsiniz.',
            'Təyinat MAC = default gateway-in MAC-ı — L2 ünvanı yalnız lokal seqmentdə etibarlıdır.',
            'SYN → SYN-ACK → ACK ardıcıllığı və təsadüfi mənbə portu (49152+) görünür.',
        ],
    },
    {
        'slug': 'ethernet-cabling',
        'title': 'Kabel Növləri və Interfeys Xətaları',
        'goal': 'Düzgün kabel növünü seçmək, speed/duplex uyğunsuzluğunu yaratmaq və interfeys sayğaclarında tapmaq.',
        'tool': 'Cisco Packet Tracer',
        'time': '30 dəq',
        'level': 'Başlanğıc',
        'topology': '''
 PC1 ---(Fa0/1) SW1 (Gi0/1)=====(Gi0/1) SW2 (Fa0/1)--- PC2
                 |
               R1 (Gi0/0 — Fa0/24)
''',
        'addressing': [
            ['Cihaz', 'Interfeys', 'IP / maska'],
            ['PC1', 'NIC', '192.168.1.10 /24'],
            ['PC2', 'NIC', '192.168.1.20 /24'],
            ['R1', 'Gi0/0', '192.168.1.1 /24'],
        ],
        'tasks': [
            'Cihazları yerləşdirin və <strong>Automatic</strong> kabel seçimindən istifadə etmədən hər link üçün düzgün kabeli özünüz seçin (PC–SW, SW–SW, SW–R).',
            'Ünvanlama cədvəlinə görə IP-ləri təyin edin, PC1-dən PC2 və R1-ə ping edin.',
            'SW1 və SW2-nin Gi0/1 portlarında <code>description</code> yazın.',
            'SW2 Gi0/1-də <code>speed 100</code> və <code>duplex half</code>, SW1-də <code>duplex full</code> təyin edin (uyğunsuzluq).',
            'Hər iki tərəfdə <code>show interfaces gi0/1</code> ilə duplex, CRC, late collision sayğaclarını müqayisə edin; CDP-nin duplex mismatch xəbərdarlığını tapın.',
            'Hər iki tərəfi <code>speed auto</code> / <code>duplex auto</code> qaytarın və sayğacları <code>clear counters</code> ilə sıfırlayın.',
        ],
        'verify': '''
show interfaces status
show interfaces gi0/1 | include duplex|CRC|collision
show cdp neighbors detail
''',
        'expect': [
            'PC–SW və SW–R üçün straight-through, SW–SW üçün (Auto-MDIX olmasa) crossover seçilib.',
            'Duplex mismatch zamanı half tərəfdə late collision, full tərəfdə CRC/runt artır.',
            'Auto rejimə qayıtdıqdan sonra interfeys <code>Full-duplex</code> və sayğaclar artmır.',
        ],
        'solution': '''
SW1(config)# interface gi0/1
SW1(config-if)# description Uplink-SW2
SW2(config)# interface gi0/1
SW2(config-if)# description Uplink-SW1
SW2(config-if)# speed 100
SW2(config-if)# duplex half
! ... müşahidədən sonra
SW2(config-if)# speed auto
SW2(config-if)# duplex auto
SW2# clear counters gi0/1
''',
    },
    {
        'slug': 'tcp-udp',
        'title': 'TCP Handshake, Portlar və UDP',
        'goal': 'TCP bağlantısının qurulub bağlanmasını və UDP-nin bağlantısız işləməsini paketlərdə müşahidə etmək.',
        'tool': 'Wireshark və terminal (və ya Packet Tracer Simulation)',
        'time': '35 dəq',
        'tasks': [
            'Wireshark-da tutmaya başlayın, <code>curl -I https://example.com</code> işlədin.',
            'Filtr <code>tcp.port == 443</code>: SYN, SYN-ACK, ACK paketlərini, sonra FIN/ACK ilə bağlanmanı tapın.',
            'İlk SYN-də <strong>MSS</strong> və <strong>Window Size</strong> dəyərlərini yazın.',
            'Filtr <code>dns</code>: <code>nslookup cisco.com</code> sorğusunun UDP 53 üzərindən iki paketlə (sorğu–cavab) getdiyini göstərin.',
            '<code>netstat -an</code> (və ya <code>ss -tan</code>) ilə ESTABLISHED və LISTEN vəziyyətlərini tapın; hər biri üçün yerli və uzaq portu izah edin.',
            'Nəticələri cədvəlləşdirin: protokol, port, bağlantı qurulurmu, təsdiq varmı.',
        ],
        'verify': '''
curl -I https://example.com
nslookup cisco.com
netstat -an | findstr ESTABLISHED      (Windows)
ss -tan state established               (Linux)
Wireshark: tcp.flags.syn==1   tcp.flags.fin==1   dns
''',
        'expect': [
            'TCP-də məlumatdan əvvəl üç paketlik handshake, sonda FIN ilə bağlanma görünür.',
            'DNS sorğusu handshake olmadan bir sorğu və bir cavab ilə tamamlanır.',
            'Klient tərəfində mənbə portu dinamik (49152–65535), server tərəfində məlum port (443, 53).',
        ],
    },
    {
        'slug': 'mac-arp',
        'title': 'ARP Prosesi və MAC Cədvəli',
        'goal': 'ARP sorğu/cavabını və switch-in MAC öyrənməsini addım-addım izləmək; uzaq şəbəkəyə gedəndə MAC-ların necə dəyişdiyini görmək.',
        'tool': 'Cisco Packet Tracer (Simulation Mode)',
        'time': '35 dəq',
        'topology': '''
 PC1 ----\\                                   /---- PC3
          SW1 (Fa0/24) ---- (Gi0/0) R1 (Gi0/1) ---- SW2
 PC2 ----/                                   \\
''',
        'addressing': [
            ['Cihaz', 'Interfeys', 'IP / maska', 'Gateway'],
            ['PC1', 'NIC', '192.168.10.11 /24', '192.168.10.1'],
            ['PC2', 'NIC', '192.168.10.12 /24', '192.168.10.1'],
            ['R1', 'Gi0/0', '192.168.10.1 /24', '—'],
            ['R1', 'Gi0/1', '192.168.20.1 /24', '—'],
            ['PC3', 'NIC', '192.168.20.13 /24', '192.168.20.1'],
        ],
        'tasks': [
            'Topologiyanı qurun və ünvanlayın. PC-lərdə <code>arp -d</code>, SW1-də <code>clear mac address-table dynamic</code> ilə cədvəlləri təmizləyin.',
            'Simulation Mode-da filtrdə yalnız ARP və ICMP saxlayın. PC1-dən PC2-yə ping edin: ARP broadcast-ın hansı portlardan çıxdığını izləyin.',
            'SW1-də <code>show mac address-table</code>: hansı MAC-lar hansı portlarda öyrənilib?',
            'PC1-dən PC3-ə ping edin. PC1 kimin MAC-ını soruşur — PC3-ün, yoxsa gateway-in?',
            'Paketi R1-dən çıxan anda açın: mənbə/təyinat MAC dəyişib, IP-lər isə dəyişməyib — göstərin.',
            'R1-də <code>show ip arp</code> ilə hər iki şəbəkənin ARP qeydlərini tapın.',
        ],
        'verify': '''
PC> arp -a
SW1# show mac address-table dynamic
R1# show ip arp
R1# show interfaces gi0/0 | include address
''',
        'expect': [
            'ARP sorğusu broadcast (ffff.ffff.ffff), cavabı unicast-dır.',
            'Uzaq şəbəkə üçün PC gateway-in MAC-ını soruşur və öz ARP cədvəlində yalnız gateway görünür.',
            'Hər router hop-unda L2 başlığı yenidən yazılır, L3 ünvanları sabit qalır.',
        ],
    },
    {
        'slug': 'icmp',
        'title': 'Ping və Traceroute ilə Nasazlığı Tapmaq',
        'goal': 'Əlçatanlıq problemini ping, extended ping və traceroute nəticələrinə görə dəqiq hop-a qədər lokalizə etmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '40 dəq',
        'topology': '''
 PC1 --- R1 (Gi0/1) 10.0.12.0/30 (Gi0/0) R2 (Gi0/1) 10.0.23.0/30 (Gi0/0) R3 --- Server
 192.168.1.0/24                                                        192.168.3.0/24
''',
        'addressing': [
            ['Cihaz', 'Interfeys', 'IP / maska'],
            ['R1', 'Gi0/0 / Gi0/1', '192.168.1.1 /24 · 10.0.12.1 /30'],
            ['R2', 'Gi0/0 / Gi0/1', '10.0.12.2 /30 · 10.0.23.1 /30'],
            ['R3', 'Gi0/0 / Gi0/1', '10.0.23.2 /30 · 192.168.3.1 /24'],
            ['PC1 / Server', 'NIC', '192.168.1.10 · 192.168.3.10 (gateway .1)'],
        ],
        'tasks': [
            'Topologiyanı qurun və statik marşrutlarla tam əlçatanlıq təmin edin; PC1-dən Server-ə ping və <code>tracert</code> işlədin.',
            'R2-də R3-ə gedən marşrutu silin (<code>no ip route 192.168.3.0 ...</code>). PC1-dən yenidən ping: hansı cavab gəlir (<code>Destination host unreachable</code> yoxsa timeout) və kim göndərir?',
            '<code>tracert</code> ilə problemin hansı hop-da olduğunu göstərin.',
            'Marşrutu qaytarın, R3-də isə geriyə (192.168.1.0) marşrutu silin. Ping nə göstərir və niyə traceroute R3-ə qədər çatır, amma cavab qayıtmır?',
            'R1-də extended ping ilə mənbə interfeysini <code>Gi0/0</code> seçib Server-ə 100 paket göndərin, <code>size 1500</code> və <code>df-bit</code> sınayın.',
        ],
        'verify': '''
PC1> ping 192.168.3.10
PC1> tracert 192.168.3.10
R1# ping
Protocol [ip]:  Target IP address: 192.168.3.10  Repeat count [5]: 100
Extended commands [n]: y   Source address or interface: GigabitEthernet0/0
R1# traceroute 192.168.3.10 source gi0/0
R2# show ip route
''',
        'expect': [
            'Marşrut yoxdursa router <strong>Destination unreachable</strong> qaytarır (Cisco-da <code>U</code>), geri marşrut yoxdursa — timeout (<code>.</code>).',
            'Traceroute problemi dəqiq hop-a qədər göstərir.',
            'Extended ping-də mənbə interfeysini seçməyin nə üçün vacib olduğunu izah edə bilirsiniz.',
        ],
        'solution': '''
R1(config)# ip route 192.168.3.0 255.255.255.0 10.0.12.2
R1(config)# ip route 10.0.23.0 255.255.255.252 10.0.12.2
R2(config)# ip route 192.168.1.0 255.255.255.0 10.0.12.1
R2(config)# ip route 192.168.3.0 255.255.255.0 10.0.23.2
R3(config)# ip route 192.168.1.0 255.255.255.0 10.0.23.1
R3(config)# ip route 10.0.12.0 255.255.255.252 10.0.23.1
''',
    },
    {
        'slug': 'binary-hex',
        'title': 'Çevirmə Sürəti Məşqi',
        'goal': 'Onluq, binar və hex çevirmələrini kağız üzərində, kalkulyatorsuz, dəqiq və sürətlə etmək.',
        'tool': 'Kağız, qələm və taymer; yoxlamaq üçün portalın Subnet Kalkulyatoru',
        'time': '25 dəq',
        'level': 'Başlanğıc',
        'tasks': [
            '128–64–32–16–8–4–2–1 cədvəlini yaddaşdan 3 dəfə yazın.',
            'Binara çevirin (taymer: 3 dəqiqə): <code>172</code>, <code>200</code>, <code>99</code>, <code>255</code>, <code>10</code>, <code>224</code>.',
            'Onluğa çevirin: <code>11000000</code>, <code>10101000</code>, <code>11111100</code>, <code>01111111</code>.',
            'Hex-ə çevirin: <code>192</code>, <code>168</code>, <code>254</code>; onluğa: <code>0xAC</code>, <code>0x1F</code>, <code>0xFE</code>.',
            'Maskaları prefiksə çevirin: <code>255.255.255.224</code>, <code>255.255.248.0</code>, <code>255.192.0.0</code>.',
            'MAC ünvanı <code>00:1A:2B:3C:4D:5E</code>-nin ilk baytını binar yazın və 7-ci bitin (U/L) nə olduğunu tapın.',
        ],
        'expect': [
            'Onluq ↔ binar çevirmə bir oktet üçün 15 saniyədən az çəkir.',
            'Cavablar: 172 = 10101100, 200 = 11001000, 99 = 01100011, 224 = 11100000; 11111100 = 252; 0xAC = 172; /27, /21, /10.',
            'Hex ↔ binar çevirmədə hər hex simvolun 4 bit olduğunu istifadə edirsiniz.',
        ],
    },
    {
        'slug': 'ipv4-subnetting',
        'title': 'VLSM ilə Ofis Ünvan Planı',
        'goal': 'Verilmiş blokdan müxtəlif ölçülü şəbəkələr üçün israfsız VLSM planı qurmaq və router-də tətbiq edib yoxlamaq.',
        'tool': 'Kağız + Cisco Packet Tracer; yoxlama üçün portalın VLSM Planlayıcısı',
        'time': '45 dəq',
        'topology': '''
          [LAN-A 100 host]   [LAN-B 50 host]
                  \\              /
                   R1 --------- R2 ---- [LAN-C 25 host]
                       WAN /30      \\
                                     [LAN-D 10 host]
''',
        'tasks': [
            'Blok: <code>172.16.0.0/24</code>. Tələbat: LAN-A 100, LAN-B 50, LAN-C 25, LAN-D 10 host və bir point-to-point WAN.',
            'Şəbəkələri böyükdən kiçiyə sıralayıb hər biri üçün prefiks, şəbəkə ünvanı, ilk/son host və broadcast-ı cədvəldə yazın.',
            'Planınızı portalın VLSM Planlayıcısı ilə müqayisə edin.',
            'R1-də LAN-A və LAN-B (iki interfeys), R2-də LAN-C və LAN-D, R1–R2 arasında WAN ünvanlarını konfiqurasiya edin.',
            'Hər LAN-a bir PC qoşun (ilk host = gateway, son host = PC) və statik marşrutlarla bütün LAN-lar arasında ping təmin edin.',
        ],
        'expect': [
            'LAN-A 172.16.0.0/25, LAN-B 172.16.0.128/26, LAN-C 172.16.0.192/27, LAN-D 172.16.0.224/28, WAN 172.16.0.240/30.',
            'Heç bir subnet üst-üstə düşmür, istifadə olunmamış yer 172.16.0.244–255 qalır.',
            'Bütün PC-lər bir-birini ping edir.',
        ],
        'verify': '''
R1# show ip interface brief
R1# show ip route connected
R2# show ip route static
PC> ping <digər LAN-dakı PC>
''',
        'solution': '''
! R1 (Gi0/0 LAN-A, Gi0/1 LAN-B, Gi0/2 WAN)
interface gi0/0
 ip address 172.16.0.1 255.255.255.128
interface gi0/1
 ip address 172.16.0.129 255.255.255.192
interface gi0/2
 ip address 172.16.0.241 255.255.255.252
ip route 172.16.0.192 255.255.255.224 172.16.0.242
ip route 172.16.0.224 255.255.255.240 172.16.0.242
! R2 (Gi0/0 LAN-C, Gi0/1 LAN-D, Gi0/2 WAN)
interface gi0/0
 ip address 172.16.0.193 255.255.255.224
interface gi0/1
 ip address 172.16.0.225 255.255.255.240
interface gi0/2
 ip address 172.16.0.242 255.255.255.252
ip route 172.16.0.0 255.255.255.128 172.16.0.241
ip route 172.16.0.128 255.255.255.192 172.16.0.241
''',
    },
    {
        'slug': 'ipv6',
        'title': 'Dual-Stack, SLAAC və OSPFv3',
        'goal': 'İki router arasında IPv6 ünvanlama, SLAAC ilə host konfiqurasiyası və OSPFv3 marşrutlaşdırması qurmaq.',
        'tool': 'Cisco Packet Tracer',
        'time': '45 dəq',
        'topology': '''
 PC1 --- (Gi0/0) R1 (Gi0/1) ------ (Gi0/1) R2 (Gi0/0) --- PC2
 2001:db8:1:1::/64     2001:db8:1:12::/64      2001:db8:1:2::/64
''',
        'addressing': [
            ['Cihaz', 'Interfeys', 'IPv6', 'Link-local'],
            ['R1', 'Gi0/0', '2001:db8:1:1::1/64', 'fe80::1'],
            ['R1', 'Gi0/1', '2001:db8:1:12::1/64', 'fe80::1'],
            ['R2', 'Gi0/1', '2001:db8:1:12::2/64', 'fe80::2'],
            ['R2', 'Gi0/0', '2001:db8:1:2::1/64', 'fe80::2'],
            ['PC1 / PC2', 'NIC', 'SLAAC (Auto Config)', 'avtomatik'],
        ],
        'tasks': [
            'Hər iki router-də <code>ipv6 unicast-routing</code> aktivləşdirin və cədvələ görə ünvanları, link-local-ları təyin edin.',
            'PC-lərdə IPv6 konfiqurasiyasını <strong>Auto Config</strong> edin: prefiks və gateway-in (link-local) SLAAC ilə gəldiyini yoxlayın.',
            'PC1-dən R1-in link-local ünvanına ping edin.',
            'OSPFv3 prosesi 1 qurun (router-id R1 = 1.1.1.1, R2 = 2.2.2.2) və bütün interfeysləri area 0-a daxil edin.',
            'PC1-dən PC2-yə ping edin; <code>show ipv6 route ospf</code>-da next-hop-un link-local olduğunu göstərin.',
            'Əlavə: R1–R2 linkinə IPv4 də əlavə edib (dual-stack) hər iki protokolun eyni vaxtda işlədiyini göstərin.',
        ],
        'verify': '''
show ipv6 interface brief
show ipv6 route
show ipv6 ospf neighbor
show ipv6 neighbors
PC> ipconfig /all
PC> ping 2001:db8:1:2::<PC2>
''',
        'expect': [
            'PC-lər <code>2001:db8:1:x::/64</code> prefiksli ünvan və gateway kimi <code>fe80::1</code> / <code>fe80::2</code> alır.',
            'OSPFv3 qonşuluğu FULL, marşrut cədvəlində <code>O</code> marşrutu və link-local next-hop var.',
            'PC1 ↔ PC2 ping uğurludur.',
        ],
        'solution': '''
R1(config)# ipv6 unicast-routing
R1(config)# ipv6 router ospf 1
R1(config-rtr)# router-id 1.1.1.1
R1(config)# interface gi0/0
R1(config-if)# ipv6 address 2001:db8:1:1::1/64
R1(config-if)# ipv6 address fe80::1 link-local
R1(config-if)# ipv6 ospf 1 area 0
R1(config-if)# no shutdown
R1(config)# interface gi0/1
R1(config-if)# ipv6 address 2001:db8:1:12::1/64
R1(config-if)# ipv6 address fe80::1 link-local
R1(config-if)# ipv6 ospf 1 area 0
R1(config-if)# no shutdown
! R2 eyni qayda ilə: ::2 ünvanları, fe80::2, router-id 2.2.2.2
''',
    },
    {
        'slug': 'ios-cli',
        'title': 'İlk Konfiqurasiya: Router-i Sıfırdan Hazırlamaq',
        'goal': 'Yeni router-ə əsas təhlükəsizlik və idarəetmə konfiqurasiyasını yazmaq, yadda saxlamaq və reload-dan sonra yoxlamaq.',
        'tool': 'Portalın Cisco CLI Simulyatoru (1-ci tapşırıq) və ya Packet Tracer',
        'time': '30 dəq',
        'level': 'Başlanğıc',
        'tasks': [
            'Konsol kabeli ilə qoşulun, <code>enable</code> → <code>configure terminal</code>.',
            'Hostname <code>R1-BAKU</code>, <code>no ip domain-lookup</code>, <code>enable secret</code>.',
            'Konsol xəttinə parol, <code>login</code>, <code>logging synchronous</code>, <code>exec-timeout 10 0</code>.',
            '<code>banner motd</code> ilə xəbərdarlıq mesajı və <code>service password-encryption</code>.',
            'Gi0/0-a IP ünvanı və <code>description</code> verin, <code>no shutdown</code>.',
            '<code>show running-config</code>-u yoxlayın, <code>copy running-config startup-config</code>, sonra <code>reload</code> və konfiqurasiyanın qaldığını təsdiqləyin.',
        ],
        'verify': '''
show running-config
show startup-config
show ip interface brief
show version | include uptime|register
''',
        'expect': [
            'Reload-dan sonra hostname, parollar və IP ünvanı yerindədir.',
            'Running-config-də parollar açıq mətn deyil (<code>7</code> və ya <code>5/9</code> formatında).',
            'Yazı səhvi olan əmr terminalı DNS axtarışı ilə dondurmur.',
        ],
        'solution': '''
Router> enable
Router# configure terminal
Router(config)# hostname R1-BAKU
R1-BAKU(config)# no ip domain-lookup
R1-BAKU(config)# enable secret Cisco123!
R1-BAKU(config)# line console 0
R1-BAKU(config-line)# password Kons0l!
R1-BAKU(config-line)# login
R1-BAKU(config-line)# logging synchronous
R1-BAKU(config-line)# exec-timeout 10 0
R1-BAKU(config-line)# exit
R1-BAKU(config)# banner motd # Yalniz selahiyyetli giris! #
R1-BAKU(config)# service password-encryption
R1-BAKU(config)# interface gi0/0
R1-BAKU(config-if)# description LAN
R1-BAKU(config-if)# ip address 192.168.1.1 255.255.255.0
R1-BAKU(config-if)# no shutdown
R1-BAKU(config-if)# end
R1-BAKU# copy running-config startup-config
R1-BAKU# reload
''',
        'note': 'Bu labı brauzerdə portalın <a class="font-semibold underline" href="../tools/cli.html">Cisco CLI Simulyatorunda</a> da edə bilərsiniz — tapşırıqlar avtomatik yoxlanılır.',
    },
    {
        'slug': 'cisco-commands',
        'title': 'Show Əmrləri ilə Şəbəkəni "Oxumaq"',
        'goal': 'Tanış olmayan şəbəkədə yalnız show əmrləri ilə topologiyanı, ünvanları və vəziyyəti sənədləşdirmək.',
        'tool': 'Cisco Packet Tracer (hazır və ya yoldaşınızın qurduğu topologiya)',
        'time': '40 dəq',
        'tasks': [
            'Yoldaşınızdan və ya müəllimdən 2 router + 2 switch-li konfiqurasiya olunmuş topologiya alın (sxemə baxmadan).',
            '<code>show cdp neighbors detail</code> ilə fiziki topologiyanı kağıza çəkin: hansı port hansı cihaza gedir.',
            '<code>show ip interface brief</code> və <code>show ip route</code> ilə bütün subnet-ləri və routing protokolunu müəyyənləşdirin.',
            'Switch-lərdə <code>show vlan brief</code> və <code>show interfaces trunk</code> ilə VLAN-ları və trunk-ları əlavə edin.',
            '<code>show running-config | section</code> filtrlərindən istifadə edib ən azı 3 konfiqurasiya xüsusiyyəti tapın (məs. ACL, NAT, DHCP).',
            'Nəticə: tam şəbəkə diaqramı və ünvan cədvəli — sonra real sxemlə müqayisə edin.',
        ],
        'verify': '''
show cdp neighbors detail
show ip interface brief
show ip route
show vlan brief
show interfaces trunk
show running-config | section router|interface Vlan|access-list
show running-config | include hostname|ip route
''',
        'expect': [
            'Diaqramınız real topologiya ilə 100% uyğun gəlir.',
            'Hər subnet üçün gateway və VLAN müəyyənləşdirilib.',
            '<code>| include</code>, <code>| section</code>, <code>| begin</code> filtrlərini sərbəst istifadə edirsiniz.',
        ],
    },
    {
        'slug': 'power-supply',
        'title': 'Server Otağı üçün Enerji Hesablaması',
        'goal': 'Real rack üçün güc sərfiyyatını, UPS ölçüsünü, backup müddətini və soyutma tələbini hesablamaq.',
        'tool': 'Kalkulyator və istehsalçı datasheet-ləri (APC/Eaton runtime cədvəlləri)',
        'time': '30 dəq',
        'level': 'Başlanğıc',
        'addressing': [
            ['Avadanlıq', 'Say', 'Güc (W)'],
            ['1U server', '3', '350'],
            ['48 port PoE switch', '1', '150 + PoE 370'],
            ['Router / firewall', '2', '60'],
            ['NAS', '1', '120'],
        ],
        'tasks': [
            'Cədvəldəki avadanlıqların ümumi gücünü hesablayın (W).',
            'Power factor 0.9 qəbul edərək VA-nı hesablayın və 25% ehtiyatla UPS ölçüsünü seçin.',
            'İstehsalçının runtime cədvəlindən (məs. 3 kVA line-interactive UPS) bu yük üçün təxmini backup müddətini tapın. 15 dəqiqə üçün hansı əlavə batareya paketi lazımdır?',
            'İstilik yükünü BTU/saat ilə hesablayın (1 W ≈ 3.41 BTU/h) və kondisioner gücünü müəyyənləşdirin.',
            '230 V şəbəkədə ümumi cərəyanı (A) hesablayın — 16 A avtomat kifayətdirmi?',
            'Nəticəni bir səhifəlik "enerji planı" kimi yazın: sxem (şəbəkə → stabilizator → UPS → rack), seçimlər və əsaslandırma.',
        ],
        'expect': [
            'Ümumi güc: 3×350 + 520 + 2×60 + 120 = <strong>1810 W</strong>; VA ≈ 2011; ehtiyatla ≈ 2.5 kVA → 3 kVA UPS.',
            'İstilik ≈ 6 170 BTU/h; cərəyan ≈ 7.9 A — 16 A xətt kifayətdir.',
            'Planınızda UPS növünün (line-interactive və ya online) seçimi əsaslandırılıb.',
        ],
    },
]
