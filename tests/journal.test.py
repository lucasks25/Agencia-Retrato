"""Ensure the published archive contains its actual articles and usable reading links."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Reading(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.text = []
        self.ids = []
        self.anchors = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id', '').startswith('leitura-'):
            self.ids.append(attrs['id'])
        if tag == 'a' and attrs.get('href', '').startswith('#leitura-'):
            self.anchors.append(attrs['href'][1:])

    def handle_data(self, data):
        self.text.append(data)


class JournalContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.articles = json.loads((ROOT / 'sources/journal-articles.json').read_text())

    def test_every_article_contains_its_complete_reading(self):
        self.assertEqual(len(self.articles), 119)
        for article in self.articles:
            with self.subTest(article=article['slug']):
                page = Reading((ROOT / 'dist/retratonews' / article['slug'] / 'index.html').read_text())
                text = ' '.join(' '.join(page.text).split())
                for paragraph in [article['lead']] + [p for s in article['sections'] for p in s['paragraphs']]:
                    self.assertTrue(' '.join(paragraph.split()) in text, 'Missing article paragraph: ' + article['slug'])
                if article.get('notice'):
                    self.assertIn(article['notice'], text)
                if article.get('note'):
                    self.assertNotIn(article['note'], text)

    def test_reading_index_reaches_each_section_once(self):
        for article in self.articles:
            with self.subTest(article=article['slug']):
                page = Reading((ROOT / 'dist/retratonews' / article['slug'] / 'index.html').read_text())
                self.assertEqual(len(page.ids), len(article['sections']))
                self.assertEqual(page.anchors, page.ids)
                self.assertEqual(len(set(page.ids)), len(page.ids))


if __name__ == '__main__':
    unittest.main()
