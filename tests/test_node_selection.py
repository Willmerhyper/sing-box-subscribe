import copy
import json
import unittest
from pathlib import Path
import main


def node(name):
    return {'type': 'anytls', 'tag': name, 'server': '192.0.2.1',
            'server_port': 443, 'password': 'test-only', 'tls': {'enabled': True}}


class NodeSelectionTests(unittest.TestCase):
    def setUp(self):
        self.template = json.loads(Path('config_template/hyperchem-1.14.json').read_text())
        main.providers = {}

    def test_limits_span_subscription_groups_and_preserve_order(self):
        data = {'a': [node('🇭🇰 Hong Kong 03'), node('🇸🇬 Singapore 07')],
                'b': [node('🇭🇰 Hong Kong 01'), node('🇭🇰 Hong Kong 02'),
                      node('🇸🇬 Singapore 08'), node('🇸🇬 Singapore 09'),
                      node('🇺🇸 USA Seattle 01'), node('🇺🇸 USA Seattle 010'),
                      node('🇺🇸 USA Seattle 02'),
                      node('🇺🇸 USA Los Angeles 01 [DIP USA-Los Angeles]'),
                      node('🇺🇸 USA Los Angeles 99'), node('🇯🇵 Japan 01')]}
        result = main.combin_to_config(copy.deepcopy(self.template), data)
        self.assertNotIn('_node_selection', result)
        names = [o['tag'] for o in result['outbounds'] if o['type'] == 'anytls']
        self.assertEqual(names, ['🇭🇰 Hong Kong 03', '🇸🇬 Singapore 07', '🇭🇰 Hong Kong 01',
                                '🇸🇬 Singapore 08', '🇺🇸 USA Seattle 01',
                                '🇺🇸 USA Los Angeles 01 [DIP USA-Los Angeles]',
                                '🇺🇸 USA Los Angeles 99'])
        for outbound in result['outbounds']:
            if outbound['tag'] in ['Proxy', 'Auto', 'Anthropic', 'OpenAI']:
                self.assertTrue(set(outbound['outbounds']).issubset(set(names) | {'Proxy', 'Auto'}))

    def test_anthropic_is_pinned_with_matching_dns_detour(self):
        target = '🇺🇸 USA Los Angeles 01 [DIP USA-Los Angeles]'
        result = main.combin_to_config(copy.deepcopy(self.template),
                                      {'a': [node(target), node('🇭🇰 Hong Kong 01')]})
        group = next(o for o in result['outbounds'] if o['tag'] == 'Anthropic')
        self.assertEqual(group['outbounds'], [target])
        self.assertEqual(group['default'], target)
        rule = next(r for r in result['route']['rules'] if r.get('rule_set') == 'anthropic')
        self.assertEqual(rule['outbound'], 'Anthropic')
        self.assertEqual(result['dns']['rules'][0]['server'], 'dns-anthropic')
        dns = next(s for s in result['dns']['servers'] if s['tag'] == 'dns-anthropic')
        self.assertEqual(dns['detour'], 'Anthropic')

    def test_empty_match_fails_instead_of_generating_direct_only_config(self):
        with self.assertRaises(ValueError):
            main.combin_to_config(copy.deepcopy(self.template), {'a': [node('Japan 01')]})

    def test_templates_without_selection_keep_all_nodes(self):
        template = copy.deepcopy(self.template)
        template.pop('_node_selection')
        result = main.combin_to_config(template, {'a': [node('Japan 01')]})
        self.assertIn('Japan 01', [o['tag'] for o in result['outbounds']])


if __name__ == '__main__':
    unittest.main()
