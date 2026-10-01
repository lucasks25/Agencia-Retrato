"""Render verified review, service and legal content without runtime API dependencies."""
import json,re
from html import escape as h
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
CONTACT='https://wa.me/551132880015'
def load(name):return json.loads((ROOT/'sources'/name).read_text())
def google_wordmark():
    return '<span class="google-wordmark" aria-label="Google"><span>G</span><span>o</span><span>o</span><span>g</span><span>l</span><span>e</span></span>'
def crop_image(review,rect,alt,cls=''):
    x,y,w,ht=rect;sw,sh=review['size']
    # CSS crops the exact supplied pixels; no portrait or travel image is invented.
    style=f'width:{sw/w*100:.6f}%;left:{-x/w*100:.6f}%;top:{-y/ht*100:.6f}%;'
    return f'<span class="review-image-crop {cls}"><img src="/assets/reviews/{h(review["id"])}.png" width="{sw}" height="{sh}" style="{style}" alt="{h(alt)}" loading="lazy"></span>'
def review_person(review):
    avatar=crop_image(review,review['avatar'],'Foto do perfil de '+review['name'],'review-avatar') if review.get('avatar') else f'<span class="review-initial" aria-hidden="true">{h(review["name"][0].upper())}</span>'
    return f'<div class="review-person">{avatar}<div><h3>{h(review["name"])}</h3><span>Avaliação no Google</span></div></div>'
def review_section():
    data=load('google-reviews.json');cards=[]
    for review in data['reviews']:
        rid=review['id'];text=review['text'];paragraphs=''.join('<p>'+h(p)+'</p>' for p in text.split('\n'))
        photos=''.join(crop_image(review,rect,f'Foto {i} da viagem compartilhada por {review["name"]}') for i,rect in enumerate(review.get('photos',[]),1))
        caption='Trecho da avaliação' if review.get('excerpt_only') else 'Relato publicado no Google'
        full=f'{review_person(review)}<p class="review-stars" aria-label="5 de 5 estrelas">★★★★★</p><blockquote>{paragraphs}</blockquote>'+ (f'<div class="review-full-gallery">{photos}</div>' if photos else '')+f'<p class="review-source-note">{caption}</p>'
        cards.append(f'<li class="review-card"><div class="review-card-top"><p class="review-stars" aria-label="5 de 5 estrelas">★★★★★</p><span class="review-score">5/5</span></div><p class="review-tag">{h(review["tag"])}</p><blockquote class="review-preview">{h(text)}</blockquote>'+ (f'<div class="review-mini-gallery" aria-label="Fotos da viagem de {h(review["name"])}">{photos}</div>' if photos else '')+f'{review_person(review)}<details class="review-expand" id="review-{rid}"><summary data-review-open="{rid}">{"Ler o trecho" if review.get("excerpt_only") else "Ler avaliação"}<span aria-hidden="true">+</span></summary><div class="review-full-body">{full}</div></details></li>')
    return '<section class="google-reviews section-wrap" id="avaliacoes" aria-labelledby="reviews-title"><div class="reviews-heading"><div><p class="eyebrow">QUEM VIAJA, CONTA</p><h2 id="reviews-title">A viagem passa.<br>O cuidado <em>fica.</em></h2></div><div class="reviews-intro"><p>Nas palavras de quem viveu.<br>Relatos de viagens, detalhes e bons encontros com a Retrato.</p><a href="'+h(data['profile_url'])+'" target="_blank" rel="noopener noreferrer" class="reviews-google-link">Avaliações no '+google_wordmark()+'</a></div></div><div class="reviews-carousel"><ul class="reviews-track" aria-label="Avaliações de clientes">'+''.join(cards)+'</ul></div><div class="reviews-bottom"><p>13 relatos selecionados · Avaliações publicadas no Google</p><div class="reviews-controls" hidden><button type="button" data-reviews-prev aria-label="Ver avaliações anteriores">←</button><button type="button" data-reviews-next aria-label="Ver próximas avaliações">→</button></div></div></section>'
def review_dialog():
    return '<dialog class="review-dialog" id="review-dialog" aria-label="Avaliação de cliente"><button type="button" class="dialog-close" data-review-close aria-label="Fechar avaliação">×</button><div class="review-dialog-content"></div></dialog>'
def chip_prices():
    regions=load('chip-plans.json')['regions'];tabs=[];panels=[]
    for i,region in enumerate(regions):
        rid=region['id'];tabs.append(f'<button type="button" role="tab" id="chip-tab-{rid}" aria-controls="chip-panel-{rid}" aria-selected="{str(i==0).lower()}" tabindex="{0 if i==0 else -1}">{h(region["label"])}</button>')
        plans=[]
        for j,plan in enumerate(region['plans']):
            message=f'Olá! Tenho interesse no Retrato Chip: {region["label"]}, {plan["gb"]} GB, 30 dias, R$ {plan["brl"]}. Gostaria de confirmar cobertura e compatibilidade do meu aparelho.'
            price=f'{plan["brl"]:,}'.replace(',','.')
            plans.append(f'<article class="chip-plan"><p class="eyebrow">{["PARA O ESSENCIAL","PARA EXPLORAR","PARA COMPARTILHAR"][j]}</p><h3>{plan["gb"]}<span>GB</span></h3><p class="chip-validity">Franquia total · 30 dias</p><p class="chip-price"><span>R$</span> {price}<small>,00</small></p><ul><li>eSIM digital</li><li>Sem limite diário de dados</li><li>Acompanhamento do consumo</li><li>Suporte Retrato</li></ul><a class="button button-dark" href="{CONTACT}?text={quote(message)}" data-direct-contact target="_blank" rel="noopener">Escolher {plan["gb"]} GB <span aria-hidden="true">→</span></a></article>')
        panels.append(f'<div class="chip-region-panel" role="tabpanel" id="chip-panel-{rid}" aria-labelledby="chip-tab-{rid}" tabindex="0"><p class="chip-region-label">Planos para {h(region["label"])}</p><div class="chip-plan-grid">'+''.join(plans)+'</div></div>')
    return '<section class="chip-pricing section-wrap" id="planos" aria-labelledby="chip-pricing-title"><div class="section-heading"><div><p class="eyebrow">ESCOLHA SUA CONEXÃO</p><h2 id="chip-pricing-title">O destino muda.<br>A conexão <em>acompanha.</em></h2></div><p>Escolha a região e sua franquia.<br>Todos os planos têm validade de 30 dias.</p></div><div class="chip-tabs" role="tablist" aria-label="Região do plano">'+''.join(tabs)+'</div>'+''.join(panels)+'<p class="chip-price-note">Valores em reais, consultados em 30/09/2026. Antes da contratação, confirme países cobertos, compatibilidade do aparelho, início da validade e disponibilidade do plano.</p></section>'
def legal_sections(slug):
    doc=load('legal-documents.json')[slug];body=[];toc=[];list_open=False
    for block in doc['blocks']:
        kind=block['kind'];text=block['text']
        if kind!='li' and list_open:body.append('</ul>');list_open=False
        if kind=='li' and not list_open:body.append('<ul>');list_open=True
        value=h(text).replace('contato@agenciaretrato.com','<a href="mailto:contato@agenciaretrato.com">contato@agenciaretrato.com</a>')
        if kind=='h2':
            number=re.match(r'^(\d+)\.',text).group(1);anchor='assunto-'+number
            toc.append(f'<a href="#{anchor}">{h(text)}</a>');body.append(f'<h2 id="{anchor}">{value}</h2>')
        elif text in {'Política de Privacidade;','Política de Cookies;','Termos e Condições de Uso e Contratação.'}:
            target={'Política de Privacidade;':'política-de-privacidade','Política de Cookies;':'política-de-cookies','Termos e Condições de Uso e Contratação.':'termos-e-condições'}[text]
            body.append(f'<{kind}><a href="/{quote(target)}/">{value}</a></{kind}>')
        else:body.append(f'<{kind}>{value}</{kind}>')
    if list_open:body.append('</ul>')
    nav='<nav class="legal-toc" aria-label="Assuntos deste documento">'+''.join(toc)+'</nav>'
    related='<div class="legal-related"><p class="eyebrow">DOCUMENTOS</p><a href="/pol%C3%ADtica-de-privacidade/">Privacidade</a><a href="/pol%C3%ADtica-de-cookies/">Cookies</a><a href="/termos-e-condi%C3%A7%C3%B5es/">Termos e condições</a></div>'
    return f'<section class="legal-content section-wrap"><article class="legal-document"><p class="legal-updated">Última atualização: <time datetime="{doc["updated"]}">{doc["updated_label"]}</time></p>'+''.join(body)+'</article><aside class="legal-sidebar"><details class="legal-index" open><summary>Neste documento <span aria-hidden="true">⌄</span></summary>'+nav+'</details>'+related+'</aside></section>'
