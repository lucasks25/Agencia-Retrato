"""Audit generated navigation and local resources without opening a browser."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json

root=Path(__file__).resolve().parents[1]/'dist'
issues=[]
pages=list(root.rglob('*.html'))
class Audit(HTMLParser):
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='img' and 'alt' not in a:issues.append((str(page.relative_to(root)),'image without alt'))
        for key in ('href','src'):
            value=a.get(key,'')
            if not value:continue
            u=urlsplit(value)
            if key=='href' and u.hostname and u.hostname.removeprefix('www.')=='agenciaretrato.com':
                issues.append((str(page.relative_to(root)),'navigation to old site: '+value))
            if u.scheme or u.netloc or not u.path:continue
            target=root/unquote(u.path).lstrip('/') if u.path.startswith('/') else page.parent/unquote(u.path)
            if not target.exists():issues.append((str(page.relative_to(root)),'missing resource: '+value))
        if tag=='a' and 'destination-card' in a.get('class',''):
            if not a.get('href','').startswith('/destinos/') or a.get('target')=='_blank':
                issues.append((str(page.relative_to(root)),'destination must navigate internally'))
for page in pages:Audit().feed(page.read_text())
print(json.dumps({'pages':len(pages),'issues':len(issues),'examples':issues[:5]},ensure_ascii=False))
raise SystemExit(bool(issues))
