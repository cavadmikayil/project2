# CCNA lab tapşırıqları — IP Services.

LABS = [
    {
        'slug': 'dhcp',
        'title': 'Router DHCP Server və DHCP Relay',
        'goal': 'Mərkəzi router-də iki VLAN üçün DHCP pool qurmaq və digər şəbəkədəki klientlərə relay (ip helper-address) ilə xidmət etmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '45 dəq',
        'topology': '''
 PC-A (VLAN 10) --\\
                   SW ==trunk== R1 (Gi0/0.10, Gi0/0.20) ---- 10.0.0.0/30 ---- R2 (DHCP server)
 PC-B (VLAN 20) --/
''',
        'addressing': [
            ['Cihaz', 'Interfeys', 'IP'],
            ['R1', 'Gi0/0.10 / Gi0/0.20', '192.168.10.1 · 192.168.20.1 /24'],
            ['R1', 'Gi0/1', '10.0.0.1 /30'],
            ['R2', 'Gi0/0', '10.0.0.2 /30'],
        ],
        'tasks': [
            'Router-on-a-stick ilə VLAN 10 və 20-ni R1-də marşrutlaşdırın; R2-yə hər iki LAN üçün statik marşrut yazın.',
            'R2-də iki pool yaradın: <code>VLAN10</code> və <code>VLAN20</code> — network, default-router, dns-server (8.8.8.8), domain-name, lease 2 gün.',
            'Hər pool-da ilk 10 ünvanı <code>ip dhcp excluded-address</code> ilə istisna edin.',
            'PC-ləri DHCP rejiminə keçirin — ünvan almırlar. Səbəbi izah edin (broadcast router-dən keçmir).',
            'R1-in hər iki subinterfeysində <code>ip helper-address 10.0.0.2</code> yazın və PC-lərdə <code>ipconfig /renew</code>.',
            'R2-də binding cədvəlinə və statistikaya baxın; DORA prosesini Simulation Mode-da izləyin.',
        ],
        'verify': '''
R2# show ip dhcp binding
R2# show ip dhcp pool
R2# show ip dhcp conflict
R1# show running-config | include helper
PC> ipconfig /all
''',
        'expect': [
            'PC-A 192.168.10.11+, PC-B 192.168.20.11+ ünvan alır; gateway və DNS düzgündür.',
            'Relay olmadan klientlər APIPA (169.254.x.x) alır.',
            'R2 relay-dən gələn sorğudakı giaddr-a görə düzgün pool-u seçir.',
        ],
        'solution': '''
R2(config)# ip dhcp excluded-address 192.168.10.1 192.168.10.10
R2(config)# ip dhcp excluded-address 192.168.20.1 192.168.20.10
R2(config)# ip dhcp pool VLAN10
R2(dhcp-config)# network 192.168.10.0 255.255.255.0
R2(dhcp-config)# default-router 192.168.10.1
R2(dhcp-config)# dns-server 8.8.8.8
R2(dhcp-config)# domain-name lab.local
R2(dhcp-config)# lease 2
R2(config)# ip dhcp pool VLAN20
R2(dhcp-config)# network 192.168.20.0 255.255.255.0
R2(dhcp-config)# default-router 192.168.20.1
R2(dhcp-config)# dns-server 8.8.8.8
R2(config)# ip route 192.168.10.0 255.255.255.0 10.0.0.1
R2(config)# ip route 192.168.20.0 255.255.255.0 10.0.0.1
R1(config)# interface gi0/0.10
R1(config-subif)# ip helper-address 10.0.0.2
R1(config)# interface gi0/0.20
R1(config-subif)# ip helper-address 10.0.0.2
''',
    },
    {
        'slug': 'nat',
        'title': 'PAT ilə İnternet və Static NAT ilə Veb Server',
        'goal': 'Ofis şəbəkəsini bir public IP ilə internetə çıxarmaq və daxili veb serveri xaricdən əlçatan etmək.',
        'tool': 'Cisco Packet Tracer',
        'time': '45 dəq',
        'topology': '''
 PC1, PC2 (192.168.1.0/24) --\\
                              SW --- (Gi0/0) R1 (Gi0/1 203.0.113.2/30) ---- ISP (203.0.113.1) --- Internet-PC 8.8.8.10
 Web Server 192.168.1.100 ---/
''',
        'tasks': [
            'R1-də daxili və xarici interfeysləri <code>ip nat inside</code> / <code>ip nat outside</code> ilə işarələyin; ISP-yə default route yazın.',
            'ISP router-də 192.168.1.0/24 üçün marşrut <strong>yazmayın</strong> — real internet kimi private şəbəkəni tanımasın.',
            'ACL 1 ilə daxili şəbəkəni seçib PAT (<code>overload</code>) qurun; PC1 və PC2-dən eyni vaxtda Internet-PC-yə ping edin.',
            '<code>show ip nat translations</code>-da eyni inside global IP-nin fərqli portlarla istifadə olunduğunu göstərin.',
            'Veb server üçün static NAT: <code>203.0.113.5</code> → <code>192.168.1.100</code> (ISP-də 203.0.113.5 üçün marşrut R1-ə). Internet-PC-nin brauzerindən açın.',
            'Yalnız 80 portunu açmaq üçün static PAT variantını sınayın.',
        ],
        'verify': '''
show ip nat translations
show ip nat statistics
show access-lists 1
debug ip nat
''',
        'expect': [
            'Daxili PC-lər ISP-də 203.0.113.2 kimi görünür.',
            'Veb server xaricdən 203.0.113.5 ünvanı ilə açılır.',
            'NAT statistikasında hits artır, misses yoxdur.',
        ],
        'solution': '''
R1(config)# interface gi0/0
R1(config-if)# ip nat inside
R1(config)# interface gi0/1
R1(config-if)# ip nat outside
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1
R1(config)# access-list 1 permit 192.168.1.0 0.0.0.255
R1(config)# ip nat inside source list 1 interface gi0/1 overload
R1(config)# ip nat inside source static 192.168.1.100 203.0.113.5
! və ya yalnız 80: ip nat inside source static tcp 192.168.1.100 80 203.0.113.5 80
ISP(config)# ip route 203.0.113.5 255.255.255.255 203.0.113.2
''',
    },
    {
        'slug': 'network-services',
        'title': 'NTP, Syslog və SNMP ilə İdarəetmə',
        'goal': 'Bütün cihazların vaxtını sinxronlaşdırmaq, log-ları mərkəzi serverə göndərmək və SNMP ilə monitorinqi aktivləşdirmək.',
        'tool': 'Cisco Packet Tracer (Server-PT: NTP, Syslog xidmətləri)',
        'time': '40 dəq',
        'topology': '''
 R1 ---- SW1 ---- Server (192.168.1.50: NTP + Syslog)
          |
         R2
''',
        'tasks': [
            'Server-PT-də NTP və Syslog xidmətlərini aktivləşdirin.',
            'R1 və R2-də <code>ntp server 192.168.1.50</code>, saat qurşağı <code>clock timezone AZT 4</code>.',
            '<code>service timestamps log datetime msec localtime</code>, <code>logging host 192.168.1.50</code>, <code>logging trap informational</code>.',
            'Bir interfeysi söndürüb yandırın — Server-in Syslog cədvəlində mesajın vaxtla göründüyünü yoxlayın.',
            'SNMP: <code>snmp-server community M0n1t0r RO</code>, <code>snmp-server location</code>, <code>contact</code>. PC-də MIB Browser ilə <code>sysUpTime</code> oxuyun.',
            'SNMPv2c-nin niyə təhlükəsiz olmadığını və SNMPv3-ün nə əlavə etdiyini yazın.',
        ],
        'verify': '''
show ntp status
show ntp associations
show clock detail
show logging
show snmp community
''',
        'expect': [
            'NTP statusu <code>synchronized</code>, saat server ilə eynidir.',
            'Syslog serverdə millisaniyəli vaxt damğası ilə mesajlar görünür.',
            'MIB Browser SNMP ilə cihaz məlumatını oxuyur.',
        ],
        'solution': '''
R1(config)# clock timezone AZT 4
R1(config)# ntp server 192.168.1.50
R1(config)# service timestamps log datetime msec localtime
R1(config)# logging host 192.168.1.50
R1(config)# logging trap informational
R1(config)# snmp-server community M0n1t0r RO
R1(config)# snmp-server location Baki-Server-Otagi
R1(config)# snmp-server contact noc@lab.local
''',
    },
    {
        'slug': 'qos-marking',
        'title': 'Trust Boundary və DSCP Marking',
        'goal': 'IP telefon trafikinin DSCP EF ilə işarələnməsini və switch-də etibar sərhədini qurmaq, Wireshark-da işarələri görmək.',
        'tool': 'Real Catalyst switch / CML və ya Packet Tracer (məhdud) + Wireshark',
        'time': '40 dəq',
        'level': 'Çətin',
        'tasks': [
            'Access switch-də IP telefon portunda <code>mls qos trust device cisco-phone</code> və <code>mls qos trust cos</code> (və ya yeni platformalarda <code>trust device</code>) konfiqurasiya edin.',
            'PC portunda etibar etməyin: PC-nin özünün qoyduğu DSCP-nin 0-a yenidən yazıldığını göstərin.',
            'Router-də class-map ilə RTP portlarını (<code>udp 16384–32767</code>) tanıyıb policy-map ilə <code>set dscp ef</code> tətbiq edin (inbound).',
            'Wireshark-da səs paketinin IP başlığında DSCP = 46 (EF), signaling üçün CS3 olduğunu yoxlayın.',
            'Təsnifat cədvəli hazırlayın: səs, video, iş tətbiqləri, qalan trafik — hər biri üçün DSCP.',
        ],
        'verify': '''
show mls qos interface fa0/5
show class-map
show policy-map interface gi0/0
Wireshark: ip.dsfield.dscp == 46
''',
        'expect': [
            'Telefon portunda trust aktivdir, PC portunda işarələr sıfırlanır.',
            'Policy-map sayğaclarında səs sinfi paketləri artır.',
            'Səs EF (46), signaling CS3 (24), qalan trafik default (0).',
        ],
        'solution': '''
class-map match-any VOICE
 match ip dscp ef
 match protocol rtp audio
policy-map MARK-IN
 class VOICE
  set dscp ef
 class class-default
  set dscp default
interface gi0/0
 service-policy input MARK-IN
''',
    },
    {
        'slug': 'qos-queuing',
        'title': 'WAN Linkində LLQ Siyasəti',
        'goal': 'Dar WAN linkində səs üçün prioritet növbə (LLQ), vacib tətbiqlər üçün zəmanətli bant və shaping qurmaq.',
        'tool': 'Real router / CML (Packet Tracer MQC-ni qismən dəstəkləyir)',
        'time': '45 dəq',
        'level': 'Çətin',
        'topology': '''
 LAN --- R1 (Gi0/1, provayder sürəti 20 Mbps, fiziki 1 Gbps) ---- WAN ---- R2 --- LAN
''',
        'tasks': [
            'Class-map-lar: <code>VOICE</code> (DSCP EF), <code>CRITICAL</code> (AF31 — ERP), <code>class-default</code>.',
            'Policy-map <code>WAN-QUEUE</code>: VOICE üçün <code>priority percent 20</code>, CRITICAL üçün <code>bandwidth percent 40</code>, default üçün <code>fair-queue</code>.',
            'Provayder yalnız 20 Mbps verdiyi üçün parent policy-də <code>shape average 20000000</code> və child policy olaraq WAN-QUEUE (hierarchical QoS).',
            'Policy-ni Gi0/1-ə <code>output</code> istiqamətində tətbiq edin.',
            'Yük generatoru (iperf) ilə linki doldurub səs sinfinin drop olmadığını, default sinfin drop olduğunu sayğaclarda göstərin.',
        ],
        'verify': '''
show policy-map interface gi0/1 output
show class-map
show queueing interface gi0/1
''',
        'expect': [
            'Sıxlıq zamanı VOICE sinfində drop sıfırdır.',
            'CRITICAL sinfi ayrılmış bantdan aşağı düşmür.',
            'Shaper çıxışı provayder sürətində saxlayır — provayderin policer-i paketləri atmır.',
        ],
        'solution': '''
class-map match-any VOICE
 match dscp ef
class-map match-any CRITICAL
 match dscp af31
policy-map WAN-QUEUE
 class VOICE
  priority percent 20
 class CRITICAL
  bandwidth percent 40
 class class-default
  fair-queue
policy-map WAN-SHAPE
 class class-default
  shape average 20000000
  service-policy WAN-QUEUE
interface gi0/1
 service-policy output WAN-SHAPE
''',
    },
]
