#!/usr/bin/env python3
"""YouTube kurslarının siyahısını (Markdown) assets/videos.js-ə çevirir.

İstifadə (repo kökündən):
    python3 _dev/videos_import.py Kurslar.md

Markdown formatı (hər kurs üçün):
    ## 3. Fortigate Firewall Dərsləri
    🔗 [Kursa keçid](https://www.youtube.com/playlist?list=PL...)
    1. [Videonun adı](https://www.youtube.com/watch?v=VIDEO_ID&list=PL...)
    2. ...

Kursun qısa adı (id), izahı, ikonu və uyğun dərsləri aşağıdakı COURSE_META-dadır (playlist ID-yə görə).
Yeni playlist üçün META yoxdursa, ad başlıqdan, ikon "circle-play" götürülür — sonra META-ya əlavə edin.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'videos.js'

# playlist ID → (id, izah, ikon, portalın uyğun dərsləri)
COURSE_META = {
    'PLIWUHiy6unDu6EoViNjZUy18s9CgUY_JY': ('fortigate', 'FortiGate NGFW sıfırdan: interfeyslər, zone, VLAN, DHCP, policy, routing, web filter, LDAP, IPsec və SSL VPN, SD-WAN, backup və avtomatlaşdırma.', 'shield-check', ['firewall', 'vpn', 'nat']),
    'PLIWUHiy6unDudJPUg-w_M2paFUVk1cllf': ('ccna', 'Cisco cihazlarının idarəsi: Console, SSH, Telnet, Cisco ASA, site-to-site VPN və CCNA imtahanına hazırlıq təcrübəsi.', 'graduation-cap', ['ios-cli', 'ssh-security', 'vpn']),
    'PLIWUHiy6unDtnXgefD6mnHY0eqAWJHj_w': ('network', 'Müxtəlif vendorlar: Cisco, FortiGate, MikroTik, pfSense, SonicWall, Aruba, Ruijie, UniFi — switching, port forwarding, VPN, EVE-NG və ESXi.', 'network', ['switching-basics', 'vlan-types', 'nat', 'vpn']),
    'PLIWUHiy6unDv9fDQ6yCQXpHwfiO5OHvHc': ('windows-server', 'Windows Server və sistem administratoru: Active Directory, fayl və IIS serverləri, NAS/iSCSI, ESXi, Zabbix, AWS/Azure və Veeam backup.', 'server', ['windows-ad', 'dns-server', 'web-server', 'backup-dr']),
    'PLIWUHiy6unDulsq43o7RUtLz2cP0SIVws': ('helpdesk', 'Gündəlik kompüter və Windows işləri: istifadəçi hesabları, Wi-Fi parolu, flashkart, performans, Outlook imzası, Windows 11 və virtual kompüter.', 'monitor', ['windows-troubleshooting', 'pc-hardware', 'account-support']),
    'PLIWUHiy6unDtxugxA8w-nNZmLtPu_7t8u': ('virtualization', 'Virtuallaşdırma: VMware Workstation, ESXi (şəbəkə, disklər, icazələr, SSH), Hyper-V və üzərində Windows, Linux, firewall VM-ləri.', 'layers-2', ['virtualization', 'server-hardware']),
    'PLIWUHiy6unDuut8EG2a5RlK6b-y9OhQBr': ('eve-ng', 'EVE-NG ilə virtual laboratoriya: Cisco router və switch, FortiGate, Palo Alto, Cisco ASA, Windows və Linux VM-lər, FortiAnalyzer.', 'flask-conical', ['ios-cli', 'firewall']),
    'PLIWUHiy6unDtiMxeUbAbO0G2z7cN_yUtQ': ('voip', 'IP telefoniya: PBX nədir, 3CX-in Linux Debian və Windows üzərində quraşdırılması, ESXi-də VoIP şəbəkəsi.', 'phone', ['qos-marking']),
    'PLIWUHiy6unDuHWtz5ZP0rS2xNrYhCVtBf': ('backup', 'Veeam Backup & Replication 12: Hyper-V-də server, quraşdırma, backup repozitoriyaları, backup və restore job-ları.', 'hard-drive', ['backup-dr']),
    'PLIWUHiy6unDsbNMTtU4vI8EMFkwW9WB5r': ('pfsense', 'pfSense firewall: VM quraşdırılması, port forwarding, OpenVPN remote access və site-to-site VPN (FortiGate ilə də).', 'brick-wall', ['firewall', 'nat', 'vpn']),
    'PLIWUHiy6unDuJJRS_YXt_Kz03x6ga32T0': ('mikrotik', 'Kiçik ofis şəbəkəsi MikroTik ilə: router və Cap AC access point, port forwarding, PPTP, L2TP/IPsec və site-to-site VPN.', 'router', ['router-basics', 'nat', 'vpn', 'wireless']),
    'PLIWUHiy6unDvS3L5aQz32CiPxGi-HsB_J': ('cloud', 'Amazon AWS və Microsoft Azure: hesab, EC2 virtual serverlər, RDP ilə qoşulma, öz OpenVPN serveriniz, Azure-da Windows Server.', 'cloud', ['cloud-fundamentals', 'aws-core', 'azure-core']),
    'PLIWUHiy6unDt5eZgv1B5jF2IGdqPclo1i': ('monitoring', 'Şəbəkə monitorinqi: PRTG Network Monitor-a giriş, core serverin quraşdırılması, menyular və praktiki tövsiyələr.', 'activity', ['server-monitoring', 'observability']),
}

# Portalda göstərmə sırası (playlist ID) — siyahıda olmayanlar sona düşür
ORDER = ['PLIWUHiy6unDudJPUg-w_M2paFUVk1cllf', 'PLIWUHiy6unDu6EoViNjZUy18s9CgUY_JY', 'PLIWUHiy6unDtnXgefD6mnHY0eqAWJHj_w',
         'PLIWUHiy6unDv9fDQ6yCQXpHwfiO5OHvHc', 'PLIWUHiy6unDtxugxA8w-nNZmLtPu_7t8u', 'PLIWUHiy6unDuut8EG2a5RlK6b-y9OhQBr',
         'PLIWUHiy6unDuJJRS_YXt_Kz03x6ga32T0', 'PLIWUHiy6unDsbNMTtU4vI8EMFkwW9WB5r', 'PLIWUHiy6unDvS3L5aQz32CiPxGi-HsB_J',
         'PLIWUHiy6unDuHWtz5ZP0rS2xNrYhCVtBf', 'PLIWUHiy6unDtiMxeUbAbO0G2z7cN_yUtQ', 'PLIWUHiy6unDt5eZgv1B5jF2IGdqPclo1i',
         'PLIWUHiy6unDulsq43o7RUtLz2cP0SIVws']

EMOJI = re.compile('[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]')

HEADER = '''// Video Dərslər — YouTube kursları (videos.html buradan oxuyur).
// Bu fayl _dev/videos_import.py ilə Markdown siyahısından yaradılıb:
//     python3 _dev/videos_import.py Kurslar.md
// Kursun izahı, ikonu və uyğun dərslər _dev/videos_import.py-dəki COURSE_META-dadır.
//
// Hər kursda: id (linkdə: videos.html#id), title, desc, icon, playlist (YouTube linki),
// lessons (portalın uyğun dərsləri), videos — sırası ilə { id: YouTube video ID, title }.
// Eyni video bir neçə kursda ola bilər — "Baxdım" qeydi hamısında görünür.
'''


def parse(md):
    courses, cur = [], None
    for line in md.splitlines():
        h = re.match(r'^## \d+\.\s+(.+?)\s*$', line)
        if h:
            cur = {'title': h.group(1), 'list': None, 'videos': []}
            courses.append(cur)
            continue
        if cur is None:
            continue
        pl = re.search(r'\[Kursa keçid\]\(https?://[^)]*[?&]list=([\w-]+)', line)
        if pl:
            cur['list'] = pl.group(1)
            continue
        v = re.match(r'^\d+\.\s+\[(.+)\]\(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})', line)
        if v:
            title = re.sub(r'\s+', ' ', EMOJI.sub('', v.group(1))).strip()
            cur['videos'].append({'id': v.group(2), 'title': title})
    return [c for c in courses if c['list'] and c['videos']]


def render(courses):
    rank = {pl: i for i, pl in enumerate(ORDER)}
    courses = sorted(courses, key=lambda c: rank.get(c['list'], len(ORDER)))
    out = [HEADER, "window.VIDEO_CHANNEL = 'https://www.youtube.com/@cavadmikayil/courses';", '', 'window.VIDEO_COURSES = [']
    used = set()
    for c in courses:
        cid, desc, icon, lessons = COURSE_META.get(c['list'], (None, '', 'circle-play', []))
        if not cid:
            cid = re.sub(r'[^a-z0-9]+', '-', c['title'].lower()).strip('-')[:30] or c['list'][-8:].lower()
            print(f'Qeyd: {c["list"]} üçün COURSE_META yoxdur — id "{cid}" götürüldü')
        while cid in used:
            cid += '-2'
        used.add(cid)
        j = lambda s: json.dumps(s, ensure_ascii=False)
        out.append('    {')
        out.append(f'        id: {j(cid)},')
        out.append(f'        title: {j(c["title"])},')
        out.append(f'        desc: {j(desc)},')
        out.append(f'        icon: {j(icon)},')
        out.append(f'        playlist: {j("https://www.youtube.com/playlist?list=" + c["list"])},')
        out.append(f'        lessons: {j(lessons)},')
        out.append('        videos: [')
        out += [f'            {{ id: {j(v["id"])}, title: {j(v["title"])} }},' for v in c['videos']]
        out.append('        ]')
        out.append('    },')
    out.append('];')
    return '\n'.join(out) + '\n'


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    courses = parse(pathlib.Path(argv[0]).read_text(encoding='utf-8'))
    if not courses:
        print('Kurs tapılmadı — Markdown formatını yoxlayın')
        return 1
    OUT.write_text(render(courses), encoding='utf-8')
    total = sum(len(c['videos']) for c in courses)
    uniq = len({v['id'] for c in courses for v in c['videos']})
    print(f'{len(courses)} kurs, {total} video ({uniq} unikal) → {OUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
