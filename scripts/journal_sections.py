"""Render the researched Journal without exposing editorial working notes."""
from html import escape
from math import ceil
from urllib.parse import urlsplit


def article_reading(article):
    lead = article['lead']
    sections = article['sections']
    words = len(' '.join([lead] + [p for s in sections for p in s['paragraphs']]).split())
    minutes = max(2, ceil(words / 180))
    body = '<article class="article-body"><p class="article-lead">' + escape(lead) + '</p>'
    if article.get('notice'):
        body += '<p class="article-note">' + escape(article['notice']) + '</p>'
    toc = '<aside class="journal-toc"><p class="eyebrow">NESTA LEITURA</p><nav aria-label="Índice do artigo">'
    for index, section in enumerate(sections, 1):
        anchor = f'leitura-{index:02}'
        title = escape(section['title'])
        toc += f'<a href="#{anchor}">{index:02} · {title}</a>'
        body += f'<section class="journal-section" id="{anchor}"><h2>{title}</h2>'
        body += ''.join('<p>' + escape(paragraph) + '</p>' for paragraph in section['paragraphs'])
        body += '</section>'
    toc += '</nav><a class="text-link" href="/retrato-news/">Voltar ao Journal</a></aside>'
    if article.get('sources'):
        body += '<section class="article-sources"><p class="eyebrow">FONTES PARA CONTINUAR A LEITURA</p><ul>'
        for source in article['sources']:
            url = urlsplit(source['url'])
            if url.scheme != 'https' or not url.hostname or url.hostname.removeprefix('www.') == 'agenciaretrato.com':
                raise ValueError('The Journal requires a verified external primary source.')
            body += '<li><a href="' + escape(source['url'], quote=True) + '" target="_blank" rel="noopener noreferrer">' + escape(source['title']) + '</a></li>'
        body += '</ul></section>'
    body += '</article>'
    return body + toc, minutes
