"""Read the public sitemap and article metadata; retain a compact source index."""
import concurrent.futures
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import time

ROOT = Path(__file__).resolve().parents[1]
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'i': 'http://www.google.com/schemas/sitemap-image/1.1'}

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__(); self.meta = {}; self.h1 = ''; self.in_h1 = False; self.iframe = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta': self.meta[a.get('property', a.get('name', ''))] = a.get('content', '')
        if tag == 'h1': self.in_h1 = True
        if tag == 'iframe' and a.get('src'): self.iframe.append(a['src'])
    def handle_endtag(self, tag):
        if tag == 'h1': self.in_h1 = False
    def handle_data(self, data):
        if self.in_h1: self.h1 += data

def fetch(entry):
    parts = urlsplit(entry['source'])
    url = urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe='/%'), parts.query, ''))
    cache = Path('/private/tmp') / ('retrato-src-' + hashlib.sha256(url.encode()).hexdigest()[:16] + '.html')
    try:
        if cache.exists(): raw = cache.read_text()
        else:
            time.sleep(1.5)
            with urlopen(Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=35) as r:
                raw = r.read().decode('utf-8', 'replace')
            cache.write_text(raw)
        parser = Metadata(); parser.feed(raw)
        title = parser.h1.strip() or parser.meta.get('og:title', '')
        title = title.split('|')[0].strip()
        return {**entry, 'title': title, 'description': parser.meta.get('description',''), 'published':parser.meta.get('article:published_time', ''), 'modified':parser.meta.get('article:modified_time',''), 'iframes':parser.iframe}
    except Exception as exc:
        return {**entry, 'error':str(exc)}

entries = []
for node in ET.parse('/private/tmp/retrato-blog-posts.xml').getroot().findall('s:url', NS):
    entries.append({'source':node.findtext('s:loc', namespaces=NS), 'lastmod':node.findtext('s:lastmod', namespaces=NS), 'image':node.findtext('i:image/i:loc', namespaces=NS), 'image_alt':node.findtext('i:image/i:title', default='', namespaces=NS)})
extras = ['sobre','agencia-boutique','roteiros','retrato-chip','members','política-de-privacidade','política-de-cookies','termos-e-condições']
entries += [{'source':'https://www.agenciaretrato.com/'+slug, 'type':'page'} for slug in extras]
results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
    for entry in pool.map(fetch, entries):
        results.append(entry)
        if len(results) % 20 == 0: print(f'Read {len(results)}/{len(entries)} public pages', flush=True)
(ROOT/'sources'/'inventory.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
print(json.dumps({'pages':len(results),'failures':[r['source'] for r in results if 'error' in r]}, ensure_ascii=False), flush=True)
