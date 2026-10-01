"""Check navigation targets and the shared travel-planning form."""
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Structure(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.stack = []
        self.errors = []
        self.ids = []
        self.controls = []
        self.fragments = []
        self.options = {}
        self.select = None
        self.option = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if attrs.get('aria-controls'):
            self.controls.extend(attrs['aria-controls'].split())
        if tag == 'a' and attrs.get('href', '').startswith('#') and len(attrs['href']) > 1:
            self.fragments.append(attrs['href'][1:])
        if tag == 'select':
            self.select = attrs.get('id')
            self.options[self.select] = []
        if tag == 'option':
            self.option = [attrs.get('value'), '']
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append('Unexpected closing tag: ' + tag)
        else:
            self.stack.pop()
        if tag == 'option' and self.option is not None:
            self.options[self.select].append(self.option[0] or self.option[1])
            self.option = None
        if tag == 'select':
            self.select = None

    def handle_data(self, data):
        if self.option is not None:
            self.option[1] += data


class SharedMarkup(unittest.TestCase):
    def test_travel_service_pages_keep_the_main_header_button(self):
        for route in ['contato', 'retrato-chip', 'seguro-viagem', 'members', 'retratonews/seguro-viagem-retrato-universal-assistance']:
            with self.subTest(route=route):
                header = (ROOT / 'dist' / route / 'index.html').read_text().split('<header', 1)[1].split('</header>', 1)[0]
                self.assertEqual(header.count('class="header-cta"'), 1)

    def test_planning_offers_every_destination_and_traveler_group(self):
        page = Structure((ROOT / 'dist/index.html').read_text())
        self.assertEqual(page.options['trip-destination'], ['Ainda quero descobrir', 'Milagres, Alagoas', 'Praia do Preá, Ceará', 'Rio de Janeiro', 'Maldivas', 'Roma, Itália', 'Outro destino'])
        self.assertEqual(len(page.options['trip-travelers']), 5)

    def test_all_pages_have_balanced_markup_and_real_control_targets(self):
        for path in (ROOT / 'dist').rglob('*.html'):
            with self.subTest(page=str(path.relative_to(ROOT / 'dist'))):
                page = Structure(path.read_text())
                self.assertEqual(page.errors, [])
                self.assertEqual(page.stack, [])
                self.assertEqual(len(page.ids), len(set(page.ids)))
                self.assertEqual(set(page.controls) - set(page.ids), set())
                self.assertEqual(set(page.fragments) - set(page.ids), set())


if __name__ == '__main__':
    unittest.main()
