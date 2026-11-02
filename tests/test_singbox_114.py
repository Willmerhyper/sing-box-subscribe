import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from parsers.clash2base64 import clash2v2ray
from parsers.hysteria2 import parse as parse_hysteria2
from template_order import DEFAULT_TEMPLATE, PINNED_TEMPLATES, default_template_index, list_templates


class TemplateOrderTest(unittest.TestCase):
    def test_pinned_file_numbers_do_not_shift(self):
        names = list_templates(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config_template"))
        self.assertEqual(names[:6], PINNED_TEMPLATES)
        self.assertEqual(names[5], "config_1.14")
        self.assertEqual(default_template_index(names), 5)
        self.assertEqual(DEFAULT_TEMPLATE, "config_1.14")


class Hysteria2TlsTest(unittest.TestCase):
    def test_missing_sni_uses_hostname_and_keeps_verify(self):
        node = parse_hysteria2("hysteria2://authpass@hy2.example.com:443?alpn=h3#HK")
        self.assertEqual(node["tls"]["server_name"], "hy2.example.com")
        self.assertFalse(node["tls"]["insecure"])

    def test_ip_without_sni_does_not_enable_insecure(self):
        node = parse_hysteria2("hysteria2://authpass@1.2.3.4:443#US")
        self.assertNotIn("server_name", node["tls"])
        self.assertFalse(node["tls"]["insecure"])

    def test_explicit_insecure_flags(self):
        for link in (
            "hysteria2://authpass@hy2.example.com:443?insecure=1#a",
            "hysteria2://authpass@hy2.example.com:443?allowInsecure=true#b",
            "hysteria2://authpass@hy2.example.com:443?skip-cert-verify=true#c",
        ):
            node = parse_hysteria2(link)
            self.assertTrue(node["tls"]["insecure"], link)
            self.assertEqual(node["tls"]["server_name"], "hy2.example.com")

    def test_explicit_sni_is_kept(self):
        node = parse_hysteria2("hysteria2://authpass@1.2.3.4:443?sni=example.com#US")
        self.assertEqual(node["tls"]["server_name"], "example.com")
        self.assertFalse(node["tls"]["insecure"])

    def test_clash_skip_cert_verify_is_explicit_only(self):
        base = {"name": "hy2", "type": "hysteria2", "server": "hy2.example.com", "port": 443, "password": "pw"}
        omitted = parse_hysteria2(clash2v2ray(dict(base)))
        self.assertFalse(omitted["tls"]["insecure"])
        self.assertEqual(omitted["tls"]["server_name"], "hy2.example.com")
        asked = parse_hysteria2(clash2v2ray(dict(base, **{"skip-cert-verify": True})))
        self.assertTrue(asked["tls"]["insecure"])


class AutoSetDnsTest(unittest.TestCase):
    def test_114_template_without_outbound_does_not_crash(self):
        config = {
            "dns": {
                "servers": [
                    {"tag": "dns-direct", "type": "https", "server": "223.5.5.5"},
                    {"tag": "dns-proxy", "type": "https", "server": "1.1.1.1", "detour": "proxy"},
                    {"tag": "dns-fakeip", "type": "fakeip", "inet4_range": "198.18.0.0/15", "inet6_range": "fc00::/18"},
                ],
                "rules": [
                    {"rule_set": "geosite-cn", "server": "dns-direct"},
                    {"query_type": ["A", "AAAA"], "action": "route", "server": "dns-fakeip"},
                ],
                "final": "dns-proxy",
            },
            "outbounds": [
                {"tag": "proxy", "type": "selector", "outbounds": ["direct"]},
                {"tag": "🎯 直连", "type": "direct"},
            ],
            "route": {
                "rules": [
                    {"action": "sniff"},
                    {"protocol": "dns", "action": "hijack-dns"},
                    {"clash_mode": "Global", "outbound": "proxy"},
                    {"ip_is_private": True, "outbound": "🎯 直连"},
                ]
            },
        }
        main.providers = {"auto_set_outbounds_dns": {"proxy": "dns-proxy", "direct": "dns-direct"}}
        self.assertTrue(main.set_proxy_rule_dns(config))
        cloned = [server for server in config["dns"]["servers"] if server.get("tag") == "proxy_dns"]
        self.assertEqual(len(cloned), 1)
        self.assertEqual(cloned[0]["type"], "https")
        self.assertEqual(cloned[0]["server"], "1.1.1.1")
        self.assertNotIn("address", cloned[0])
        self.assertEqual(cloned[0]["detour"], "proxy")
        servers_for_direct = [rule for rule in config["dns"]["rules"] if rule.get("clash_mode") == "Global"]
        self.assertEqual(servers_for_direct[0]["server"], "proxy_dns")
        self.assertEqual(servers_for_direct[0]["action"], "route")

    def test_fakeip_proxy_server_is_skipped(self):
        config = {
            "dns": {
                "servers": [
                    {"tag": "fake", "type": "fakeip", "inet4_range": "198.18.0.0/15"},
                    {"tag": "direct", "type": "udp", "server": "223.5.5.5"},
                ],
                "rules": [],
            },
            "outbounds": [{"tag": "direct", "type": "direct"}],
            "route": {"rules": [{"outbound": "proxy", "domain_suffix": [".example"]}]},
        }
        before = json.dumps(config)
        main.providers = {"auto_set_outbounds_dns": {"proxy": "fake", "direct": "direct"}}
        self.assertFalse(main.set_proxy_rule_dns(config))
        self.assertEqual(json.dumps(config), before)

    def test_legacy_address_server_still_copies(self):
        config = {
            "dns": {
                "servers": [
                    {"tag": "proxyDns", "address": "tls://8.8.8.8", "detour": "Proxy"},
                    {"tag": "localDns", "address": "https://223.5.5.5/dns-query", "detour": "direct"},
                ],
                "rules": [],
            },
            "outbounds": [{"tag": "direct", "type": "direct"}, {"tag": "Proxy", "type": "selector", "outbounds": ["direct"]}],
            "route": {"rules": [{"clash_mode": "global", "outbound": "Proxy"}]},
        }
        main.providers = {"auto_set_outbounds_dns": {"proxy": "proxyDns", "direct": "localDns"}}
        self.assertTrue(main.set_proxy_rule_dns(config))
        cloned = [server for server in config["dns"]["servers"] if server["tag"] == "Proxy_dns"][0]
        self.assertEqual(cloned["address"], "tls://8.8.8.8")
        self.assertEqual(cloned["detour"], "Proxy")


if __name__ == "__main__":
    unittest.main()
