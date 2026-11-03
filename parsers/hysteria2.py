import ipaddress
import tool,re
from urllib.parse import urlparse, parse_qs, unquote

def _flag_enabled(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ('1', 'true', 'yes')

def _is_ip_literal(host):
    if not host:
        return False
    try:
        ipaddress.ip_address(str(host).strip('[]'))
        return True
    except ValueError:
        return False

def _explicit_insecure(netquery):
    # Only the subscription may turn certificate checks off.
    for key in ('insecure', 'allowInsecure', 'skip-cert-verify', 'skip_cert_verify'):
        if _flag_enabled(netquery.get(key)):
            return True
    return False

def parse(data):
    info = data[:]
    server_info = urlparse(info)
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.query).items()
    )
    if server_info.path:
      server_info = server_info._replace(netloc=server_info.netloc + server_info.path, path="")
    ports_match = re.search(r',(\d+-\d+)', server_info.netloc) or re.search(r':(\d+-\d+)', server_info.netloc)
    server = re.sub(r"\[|\]", "", server_info.netloc.split("@")[-1].rsplit(":", 1)[0])
    sni = netquery.get('sni', netquery.get('peer', ''))
    if isinstance(sni, list):
        sni = sni[0]
    sni = unquote(str(sni)).strip() if sni else ''
    if sni.lower() == 'none':
        sni = ''
    if not sni and server and not _is_ip_literal(server):
        sni = server
    node = {
        'tag': unquote(server_info.fragment) or tool.genName()+'_hysteria2',
        'type': 'hysteria2',
        'server': server,
        'server_port': int(re.search(r'\d+', server_info.netloc.rsplit(":", 1)[-1].split(",")[0]).group()),
        "password": netquery['auth'] if netquery.get('auth') else server_info.netloc.split("@")[0].rsplit(":", 1)[-1],
        'tls': {
            'enabled': True,
            'insecure': _explicit_insecure(netquery)
        }
    }
    if sni:
        node['tls']['server_name'] = sni
    if netquery.get('upmbps'):
        node['up_mbps'] = int(re.search(r'\d+', netquery['upmbps']).group())
    if netquery.get('downmbps'):
        node['down_mbps'] = int(re.search(r'\d+', netquery['downmbps']).group())
    if ports_match:
        node['server_ports'] = [ports_match.group(1).replace('-', ':')]
    elif netquery.get('mport'):
        node['server_ports'] = [netquery['mport'].replace('-', ':')]
    node['tls']['alpn'] = (netquery.get('alpn') or "h3").strip('{}').split(',')
    if netquery.get('obfs', '') not in ['none', '']:
        node['obfs'] = {
            'type': netquery['obfs'],
            'password': netquery['obfs-password'],
        }
    return (node)
