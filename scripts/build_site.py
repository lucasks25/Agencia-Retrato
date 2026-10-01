"""Build the complete static Retrato site from a shared shell and verified source index."""
import json, re, unicodedata, hashlib
from datetime import datetime
from html import escape as h
from pathlib import Path
from urllib.parse import unquote, urlsplit, quote
from content_sections import review_section, review_dialog, chip_prices, legal_sections
from journal_sections import article_reading

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
SOURCE=json.loads((ROOT/'sources/inventory.json').read_text())
JOURNAL={a['slug']:a for a in json.loads((ROOT/'sources/journal-articles.json').read_text())}
HOME=(ROOT/'templates/home.html').read_text()
HOME=re.sub(r'    <section class="google-reviews.*?</section>',review_section(),HOME,flags=re.S)
HOME=HOME.replace('  <dialog class="destination-dialog"','  '+review_dialog()+'\n  <dialog class="destination-dialog"',1)
HOME=HOME.replace('<script src="app.js" defer></script>','<script src="app.js" defer></script><script src="experience.js" defer></script>')
HOME=HOME.replace('<script src="app.js" defer></script>','<script src="brand.js" defer></script><script src="navigation.js" defer></script><script src="app.js" defer></script>')
HOME=HOME.replace('assets/hero.jpg','assets/landscape-maldives-4k.webp')
HOME=HOME.replace('class="hero-image"','class="hero-image" data-water-scene="maldives" width="3840" height="2160"')
HOME=HOME.replace('Refúgio à beira-mar ao entardecer, com coqueiros e espaços de descanso diante do oceano','Vista aérea de ilhas, villas e mar azul nas Maldivas')
HOME=re.sub(r'(<div class="destination-foot">.*?</span>)<a.*?</a>',r'\1',HOME,flags=re.S)
HOME=HOME.replace('<a class="button button-dark" href="https://www.agenciaretrato.com/whatsapp" target="_blank" rel="noopener">Vamos conversar <span>↗</span></a>','')
SHELL_HEADER=HOME[HOME.index('  <header'):HOME.index('  <main')]
SHELL_FOOTER=HOME[HOME.index('  <footer'):HOME.index('  <dialog')]
DIALOGS=HOME[HOME.index('  <dialog'):HOME.index('</body>')]
HEAD=HOME[HOME.index('<head>'):HOME.index('</head>')+7]
ROUTES=[]
BASE='https://www.agenciaretrato.com'
CONTACT='https://wa.me/551132880015'
INSTAGRAM='https://www.instagram.com/agencia.re.trato'
CHANNEL='https://www.whatsapp.com/channel/0029VanB51b0G0XdaJhCeF3S'
CATEGORIES={'hoteis-residencias':'Hotéis & Residências','design-hospitalidade':'Design & Hospitalidade','curadoria-retrato':'Curadoria Retrato','aviação':'Aviação'}
BRAND_INTRO='<div class="brand-intro" aria-hidden="true" hidden><div class="brand-intro-frame"><i></i><i></i><i></i><i></i><div class="brand-intro-mark"><span>agência</span><strong><b>(</b>re<b>)</b>trato</strong></div><p>UM NOVO OLHAR PARA VIAJAR</p></div></div>'
LANDSCAPES={'milagres.jpg':('landscape-milagres-4k.jpg','Coqueiros e praia em São Miguel dos Milagres, Alagoas'),'prea.jpg':('landscape-prea-4k.jpg','Vista do Casana Hotel e da Praia do Preá, Ceará'),'maldivas.jpg':('landscape-maldives-4k.webp','Ilhas e villas vistas do alto nas Maldivas'),'rome.jpg':('landscape-rome-4k.webp','Cúpulas e arquitetura de Roma ao entardecer'),'rio.jpeg':('landscape-rio-4k.webp','Vista aérea do litoral e das montanhas do Rio de Janeiro'),'retreat.jpg':('landscape-villa-4k.jpg','Terraço com piscina e vista para o mar em Kaş, Turquia'),'bungalow.webp':('casana-pool-4k.jpg','Piscina privativa de uma suíte do Casana Hotel, Ceará')}

def asset(name):return '/assets/'+name
def normalized(text):return ''.join(c for c in unicodedata.normalize('NFD',text.lower()) if unicodedata.category(c)!='Mn')
def local(url):
    parts=urlsplit(url)
    path=unquote(parts.path).rstrip('/')
    if parts.netloc in {'www.agenciaretrato.com','agenciaretrato.com'}:
        if path=='/whatsapp':return CONTACT
        if path=='/instagram':return INSTAGRAM
        if path=='/canal':return CHANNEL
        if path in route_paths:return quote(path,safe='/')+'/' if path else '/'
        return '/contato/'
    return url
def link_map(html):
    return re.sub(r'href="(https://(?:www\.)?agenciaretrato\.com[^\"]*)"',lambda m:'href="'+local(m.group(1))+'"'+(' data-local="true"' if local(m.group(1)).startswith('/') else ''),html)
def root_assets(html):
    versions={name:hashlib.sha256((DIST/name).read_bytes()).hexdigest()[:12] for name in ('styles.css','app.js','ocean.js','experience.js','navigation.js','brand.js')}
    return re.sub(r'(href|src)="(assets/[^\"]*|styles\.css|app\.js|ocean\.js|experience\.js|navigation\.js|brand\.js)"',lambda m:m.group(1)+'="/'+m.group(2)+('?v='+versions[m.group(2)] if m.group(2) in versions else '')+'"',html)
def clean_interface(html,quiet=False):
    for old,(new,alt) in LANDSCAPES.items():
        html=re.sub(r'<img\b[^>]*src="/?assets/'+re.escape(old)+r'"[^>]*>',lambda m:m.group(0) if 'data-preserve-photo' in m.group(0) else re.sub(r'alt="[^"]*"','alt="'+h(alt)+'"',m.group(0).replace(old,new)),html)
    html=re.sub(r'(<body[^>]*>)',r'\1'+BRAND_INTRO,html,count=1)
    html=re.sub(r'<span(?: [^>]*)?>↗</span>','',html)
    html=html.replace(' ↗','').replace('↗','')
    html=re.sub(r'<span class="(?:card-arrow|client-icon)"[^>]*></span>','',html)
    html=re.sub(r'  <a class="contact-float".*?</a>','',html,flags=re.S)
    html=html.replace('>Planeje com a Retrato</a>','>Contato</a>')
    html=html.replace('>Fale com a Retrato <small>Uma conversa para começar</small>','>Contato <small>Os canais da agência</small>')
    if quiet:html=re.sub(r'<a class="header-cta".*?</a>','',html)
    return '\n'.join(line.rstrip() for line in html.split('\n'))

def cta(label='Planeje sua viagem',choice=''):
    return f'<button type="button" class="button button-dark" data-plan-destination="{h(choice)}">{h(label)} <span aria-hidden="true">→</span></button>'
def heading(kicker,title,description=''):
    return f'<section class="page-heading section-wrap"><nav class="breadcrumbs" aria-label="Você está aqui"><a href="/">Início</a><span aria-hidden="true">/</span><span>{h(kicker)}</span></nav><p class="eyebrow">{h(kicker.upper())}</p><h1>{title}</h1>{"<p class=page-intro>"+description+"</p>" if description else ""}</section>'
def photo_heading(kicker,title,description,image,alt,caption='',actions='',extra=''):
    return f'<section class="photo-heading section-wrap {extra}"><img src="/assets/{image}" alt="{h(alt)}" width="3840" height="2160" fetchpriority="high"><div class="photo-heading-shade"></div><div class="photo-heading-copy"><nav class="breadcrumbs" aria-label="Você está aqui"><a href="/">Início</a><span aria-hidden="true">/</span><span>{h(kicker)}</span></nav><p class="eyebrow light">{h(kicker.upper())}</p><h1>{title}</h1><p class="page-intro">{description}</p>{actions}</div>{"<span class=photo-location>"+h(caption)+"</span>" if caption else ""}</section>'
def end_cta(title='A próxima viagem começa<br>com <em>você.</em>',description='Conte suas ideias. A Retrato ajuda a dar forma ao próximo capítulo.'):
    return f'<section class="page-cta section-wrap"><div><p class="eyebrow">DO DESEJO AO EMBARQUE</p><h2>{title}</h2><p>{description}</p></div>{cta("Vamos planejar")}</section>'
def feature_rows(items):
    return '<div class="feature-rows">'+''.join(f'<article><span>{i:02}</span><div><h3>{title}</h3><p>{description}</p></div></article>' for i,(title,description) in enumerate(items,1))+'</div>'
def faq(items):
    return '<section class="faq-section section-wrap"><div><p class="eyebrow">ANTES DE COMEÇAR</p><h2>Boas perguntas.<br><em>Escolhas mais claras.</em></h2></div><div>'+''.join(f'<details><summary>{q}<span aria-hidden="true">+</span></summary><p>{a}</p></details>' for q,a in items)+'</div></section>'
def create(path,title,content,description='',extra=''):
    if 'class="photo-heading' in content or extra=='destination-page':extra+=' photo-page'
    ROUTES.append(path)
    target=DIST/path.strip('/')/'index.html' if path else DIST/'index.html'
    target.parent.mkdir(parents=True,exist_ok=True)
    head=re.sub(r'<title>.*?</title>',f'<title>{h(title)} | Agência Retrato</title>',HEAD)
    head=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{h(description or title)}">',head)
    head=re.sub(r'<meta property="og:title" content="[^"]*">',f'<meta property="og:title" content="{h(title)} | Agência Retrato">',head)
    head=re.sub(r'<meta property="og:description" content="[^"]*">',f'<meta property="og:description" content="{h(description or title)}">',head)
    head=re.sub(r'  <link rel="preload"[^\n]*\n','',head)
    html='<!doctype html>\n<html lang="pt-BR">\n'+head+'\n<body class="inner-page '+extra+'"><a class="skip" href="#conteudo">Ir para o conteúdo</a>'+SHELL_HEADER+'<main id="conteudo">'+content+'</main>'+SHELL_FOOTER+DIALOGS+'</body></html>'
    html=clean_interface(root_assets(link_map(html)),quiet=path in {'política-de-privacidade','política-de-cookies','termos-e-condições','contato','retrato-chip','seguro-viagem','members','retratonews/seguro-viagem-retrato-universal-assistance'})
    html=html.replace('href="#inicio"','href="/"').replace('href="#destinos"','href="/roteiros/"').replace('href="#experiencia"','href="/agencia-boutique/"').replace('href="#sobre"','href="/sobre/"').replace('href="#journal"','href="/retrato-news/"')
    html=re.sub(r'(<a[^>]*data-local="true"[^>]*)(?: target="_blank")',r'\1',html)
    target.write_text(html)

# Every public original route is represented; integrations retain their real external destinations.
post_entries=[x for x in SOURCE if x.get('type')!='page']
route_paths={'','/sobre','/agencia-boutique','/roteiros','/retrato-chip','/members','/retrato-news','/seguro-viagem','/contato','/perguntas-frequentes','/política-de-privacidade','/política-de-cookies','/termos-e-condições'}
route_paths.update(unquote(urlsplit(p['source']).path).rstrip('/') for p in post_entries)
route_paths.update('/retrato-news/categories/'+c for c in CATEGORIES)

# Replace the landing page's header with real site navigation.
SHELL_FOOTER=SHELL_FOOTER.replace('https://www.agenciaretrato.com/retratonews/seguro-viagem-retrato-universal-assistance','/seguro-viagem/').replace('href="https://www.agenciaretrato.com/whatsapp" target="_blank" rel="noopener">Planeje com a Retrato ↗','href="/contato/">Contato')
SHELL_HEADER=SHELL_HEADER.replace('href="#destinos"','href="/roteiros/"').replace('href="#experiencia"','href="/agencia-boutique/"').replace('href="#sobre"','href="/sobre/"').replace('href="#journal"','href="/retrato-news/"')
SHELL_HEADER=SHELL_HEADER.replace('class="destinations-menu"','class="destinations-menu nav-menu"').replace('class="destinations-panel"','class="destinations-panel nav-panel"')
SHELL_HEADER=SHELL_HEADER.replace('Destinos <span aria-hidden="true">⌄</span>','Destinos')
SHELL_HEADER=SHELL_HEADER.replace('<div class="destination-menu-intro">','<div class="destination-menu-intro"><img src="/assets/landscape-lencois-4k.webp" width="3840" height="2160" alt="Dunas e lagoas nos Lençóis Maranhenses" loading="lazy"><div>')
SHELL_HEADER=SHELL_HEADER.replace('<div class="destination-menu-columns">','</div><div class="destination-menu-columns">')
SHELL_HEADER=SHELL_HEADER.replace('<a href="/retrato-news/">Journal</a>','<a href="/retrato-news/">Journal</a><div class="services-menu nav-menu"><button class="nav-disclosure" type="button" aria-expanded="false" aria-controls="services-panel">Sua viagem</button><div class="services-panel nav-panel" id="services-panel" hidden><p class="eyebrow">CADA DETALHE, BEM CONDUZIDO</p><p class="service-menu-heading">Antes, durante.<br>E no seu <em>retorno.</em></p><div class="service-menu-links"><a href="/retrato-chip/"><span>01</span><div>Retrato Chip <small>Conectividade para explorar o mundo</small></div></a><a href="/seguro-viagem/"><span>02</span><div>Seguro viagem <small>Cuidado que acompanha a sua jornada</small></div></a><a href="/members/"><span>03</span><div>Acesse sua viagem <small>Seu itinerário e documentos à mão</small></div></a><a href="/contato/"><span>04</span><div>Contato <small>Uma conversa no seu momento</small></div></a></div></div></div>',1)
SHELL_HEADER=SHELL_HEADER.replace('<a href="https://viagens.meuagente.com/br/trips/" target="_blank" rel="noopener">Acesse sua viagem ↗</a>','<a href="/retrato-chip/">Retrato Chip</a><a href="/seguro-viagem/">Seguro viagem</a><a href="/members/">Acesse sua viagem</a><a href="/contato/">Contato</a>')
home=HOME[:HOME.index('  <header')]+SHELL_HEADER+HOME[HOME.index('  <main'):]
home=home[:home.index('  <footer')]+SHELL_FOOTER+home[home.index('  <dialog'):]
home=clean_interface(root_assets(link_map(home)))
home=re.sub(r'(<a[^>]*data-local="true"[^>]*)(?: target="_blank")',r'\1',home)
(DIST/'index.html').write_text(home)
ROUTES.append('')

# About: identity and credibility, followed by a natural planning action.
about=photo_heading('A Retrato','Uma viagem.<br>Um <em>retrato seu.</em>','Uma agência boutique em São Paulo, dedicada a viagens de luxo sob medida e à gestão de viagens corporativas para executivos e pequenos grupos.','landscape-villa-4k.jpg','Terraço com piscina e vista para o mar em Kaş, Turquia','KAŞ, TURQUIA · UM HORIZONTE PARA DESACELERAR')
about+='<section class="split-editorial section-wrap"><div class="editorial-image"><img src="/assets/retreat.jpg" alt="Piscina com vista para lago e montanhas ao entardecer"></div><div><p class="eyebrow">ESCUTA. CRITÉRIO. CUIDADO.</p><h2>Antes do destino,<br><em>vem você.</em></h2><p>Uma viagem começa com a leitura do seu momento. Descanso, celebração, descoberta ou trabalho: a intenção orienta as escolhas.</p><p>A Retrato conecta hospedagem, transporte e experiências em um desenho atento ao tempo, ao conforto e à privacidade. O objetivo é que cada etapa converse com a próxima.</p></div></section>'
about+='<section class="values section-wrap"><p class="eyebrow">O QUE ORIENTA A CURADORIA</p>'+feature_rows([('Seu momento','Preferências e prioridades ajudam a definir a direção da viagem.'),('Escolhas coerentes','Ritmo, logística e hospedagem são pensados em conjunto.'),('Cuidado próximo','Uma condução personalizada para jornadas de lazer e de trabalho.')])+'</section>'
about+='<section class="credibility section-wrap"><span>São Paulo<br><small>NOSSA BASE</small></span><span>55.563.619/0001-04<br><small>CNPJ</small></span><span>96195702<br><small>IATA · TIDS</small></span></section>'+end_cta()
create('sobre','Sobre a Retrato',about,'Conheça a agência boutique de viagens sob medida com base em São Paulo.')

boutique=photo_heading('A experiência Retrato','O mundo é amplo.<br>A curadoria é <em>pessoal.</em>','Uma viagem sob medida começa quando suas prioridades se tornam o centro de cada decisão.','landscape-prea-4k.jpg','Casana Hotel e Praia do Preá, Ceará','PRAIA DO PREÁ, CEARÁ · HOSPITALIDADE BOUTIQUE')
boutique+='<section class="split-editorial section-wrap"><div><p class="eyebrow">COMO PENSAMOS SUA VIAGEM</p><h2>Os detalhes fazem<br><em>o todo.</em></h2><p>Voos, conexões, hotelaria e deslocamentos influenciam o tempo que você terá para aproveitar o destino. A curadoria boutique olha para essa relação.</p><p>Seu ritmo e o nível de serviço desejado orientam as alternativas. Em uma viagem de lazer ou na agenda de um pequeno grupo executivo, conforto e precisão precisam caminhar juntos.</p></div><div class="editorial-image"><img src="/assets/bungalow.webp" alt="Bangalô com piscina privativa no Casana Hotel"></div></section>'
boutique+='<section class="service-types section-wrap"><p class="eyebrow">DOIS CONTEXTOS. O MESMO CUIDADO.</p><div class="service-grid"><article><span>01 / LAZER</span><h3>Viajar no seu ritmo</h3><p>Preferências de hospedagem, dias livres e experiências que combinem com o momento da viagem.</p></article><article><span>02 / CORPORATIVO</span><h3>Tempo bem organizado</h3><p>Gestão para executivos e pequenos grupos, com atenção à logística, ao conforto e à discrição.</p></article></div></section>'
boutique+=faq([('Preciso chegar com um roteiro pronto?','Não. Comece com uma ideia, um período ou uma intenção. Esses pontos ajudam a orientar a conversa.'),('É possível incluir destinos brasileiros?','Sim. Explore as inspirações pelo Brasil e converse com a Retrato sobre a combinação mais adequada ao seu perfil.'),('Como são definidos preços e disponibilidade?','Datas, serviços e perfil dos viajantes orientam a consulta. As condições são apresentadas na proposta e precisam de confirmação.')])+end_cta()
create('agencia-boutique','A experiência boutique',boutique,'Curadoria de viagens com atenção ao seu ritmo, à hotelaria e à logística.')

dest_block=HOME[HOME.index('    <section class="destinations"'):HOME.index('    <section class="experience')]
dest_block=re.sub(r'<div class="section-heading">.*?</div>\s*<div class="destination-toolbar">','<div class="destination-toolbar">',dest_block,flags=re.S)
roteiros=photo_heading('Destinos & roteiros','O seu próximo<br><em>capítulo.</em>','Descubra lugares, hotéis e experiências da curadoria Retrato. Uma inspiração é o começo; o roteiro é desenhado para você.','landscape-lencois-4k.webp','Lagoas azuis entre as dunas dos Lençóis Maranhenses','LENÇÓIS MARANHENSES, BRASIL')+dest_block
roteiros+='<section class="trip-intents section-wrap"><p class="eyebrow">MAIS QUE UM LUGAR, UMA INTENÇÃO</p><h2>O que você quer<br><em>levar na memória?</em></h2><div class="intent-grid">'+''.join('<button class="intent-card" type="button" data-plan-vibe="'+vibe+'"><span>'+num+'</span><h3>'+label+'</h3><p>'+desc+'</p><span class="intent-arrow">↗</span></button>' for num,label,desc,vibe in [('01','Desacelerar','Mar, descanso e um hotel para chamar de refúgio.','Praia e descanso'),('02','Descobrir','Sabores, arte e novas maneiras de viver uma cidade.','Cultura e gastronomia'),('03','Reconectar','Natureza e tempo para estar presente.','Natureza e bem-estar'),('04','Realizar','Uma agenda de trabalho com logística bem conduzida.','Viagem corporativa')])+'</div></section>'
create('roteiros','Destinos e roteiros',roteiros,'Inspirações brasileiras e internacionais para desenhar uma viagem sob medida.')

chip=heading('Retrato Chip','Seu mundo.<br>Sem <em>distância.</em>','Mapas, mensagens e descobertas. Escolha a conexão para acompanhar sua viagem, desde a chegada.')
chip+='<section class="chip-section section-wrap"><div class="chip-visual"><div class="chip-orbit orbit-one"></div><div class="chip-orbit orbit-two"></div><div class="esim-card"><span>agência (re)trato</span><svg width="55" height="55" viewBox="0 0 55 55" fill="none" aria-hidden="true"><rect x="12" y="9" width="31" height="37" rx="6" stroke="currentColor" stroke-width="1.5"/><path d="M22 9v10h11V9M12 27h31M22 46V35h11v11" stroke="currentColor" stroke-width="1.5"/></svg><strong>O próximo lugar.<br>A mesma conexão.</strong><span>RETRATO CHIP · eSIM</span></div></div><div><p class="eyebrow">UM DETALHE A MENOS PARA RESOLVER</p><h2>Chegue com tempo<br>para <em>aproveitar.</em></h2><p>Um eSIM digital para usar a internet no exterior, sem trocar seu chip físico. Selecione a região da viagem e a franquia que combina com o seu uso.</p><div class="chip-benefits"><span>01 <strong>Escolha o plano</strong><small>Região, franquia e aparelho compatível.</small></span><span>02 <strong>Receba as orientações</strong><small>A instalação segue as instruções do seu eSIM.</small></span><span>03 <strong>Explore conectado</strong><small>Acompanhe o consumo com suporte da Retrato.</small></span></div><a class="text-link" href="#planos">Compare os planos <span aria-hidden="true">↓</span></a></div></section>'
chip+=chip_prices()
chip+=faq([('10, 20 ou 50 GB: como escolher?','Pense nos dias da viagem e no uso de mapas, mensagens, redes sociais e vídeo. A franquia é o total disponível no período de 30 dias; compare com o consumo habitual indicado no seu aparelho.'),('Meu celular aceita eSIM?','O aparelho precisa ser compatível com eSIM e estar desbloqueado. Confirme o modelo antes da contratação. A Retrato pode ajudar nessa verificação.'),('O plano Europa ou Mundo inclui qualquer país?','A cobertura depende do plano. Informe todos os países do roteiro ao escolher a conexão e confirme a lista coberta antes de contratar.'),('Quando começa a validade de 30 dias?','Confirme a regra de ativação do plano escolhido antes de instalar. As orientações do eSIM informam como e quando ativá-lo.'),('Como faço a contratação?','Selecione a região e a franquia. O botão do plano leva ao WhatsApp com sua escolha preenchida, para confirmar as condições com a Retrato.')])
create('retrato-chip','Retrato Chip — Planos de eSIM internacional',chip,'Planos de 10, 20 e 50 GB para Estados Unidos, Europa e Mundo. Valores em reais e validade de 30 dias.')

insurance_action='<div class="photo-heading-actions"><a class="button button-cream" data-direct-contact href="'+CONTACT+'?text='+quote('Olá! Gostaria de cotar o seguro viagem Retrato + Universal Assistance. Posso informar destino, datas e idade dos viajantes.')+'" target="_blank" rel="noopener">Cotar meu seguro <span aria-hidden="true">→</span></a><a class="photo-text-link" href="#protecao">Entenda a proteção <span aria-hidden="true">↓</span></a></div><p class="insurance-hero-help">Destino, datas e idade dos viajantes orientam a cotação.</p>'
insurance=photo_heading('Retrato + Universal Assistance','Explore o mundo.<br>Leve o <em>cuidado.</em>','Há uma tranquilidade em partir sabendo a quem recorrer. Escolha a proteção que combina com a sua jornada.','insurance-photo-4k.jpg','Viajante com mala em um aeroporto, em fotografia ilustrativa do seguro viagem',actions=insurance_action,extra='insurance-hero')
insurance+='<section class="insurance-introduction section-wrap" id="protecao"><p class="eyebrow">PARA VIAJAR COM MAIS TRANQUILIDADE</p><h2>O imprevisto muda.<br>O cuidado <em>continua.</em></h2><p>Destino, duração, idade dos viajantes e atividades ajudam a escolher a proteção. A Retrato orienta a cotação para que você conheça os serviços e os limites antes de contratar.</p></section>'
insurance+='<section class="insurance-details section-wrap"><div><p class="eyebrow">ANTES DE ESCOLHER</p><h2>Entenda o que<br>vai <em>com você.</em></h2><p>Compare os serviços previstos no produto e guarde os canais de assistência junto dos documentos da viagem.</p></div>'+feature_rows([('Assistência médica e hospitalar','Confira os valores de cobertura, abrangência territorial e condições do produto adequado ao seu destino.'),('Assistência durante a viagem','Os serviços para imprevistos e bagagem variam conforme o plano. Leia o bilhete e as condições para conhecer os limites e exclusões.'),('Recursos digitais','Consulte a disponibilidade de aplicativo e teleassistência no produto contratado e saiba como acionar os serviços.'),('O seu jeito de viajar','Uma viagem nacional, internacional ou frequente pode exigir modalidades diferentes. Informe atividades previstas e necessidades dos viajantes.')])+'</section>'
insurance+=faq([('Todos os planos têm as mesmas coberturas?','Não. Coberturas, serviços, limites e exclusões variam conforme o produto. Compare o bilhete e as condições antes de contratar.'),('Quando devo contratar?','Inclua o seguro no planejamento e consulte as condições antes do embarque. A cobertura depende das datas e regras do produto contratado.'),('O que preciso informar na cotação?','Destino, datas, idade dos viajantes e atividades previstas. Esses dados ajudam a orientar a consulta do seguro.'),('Como aciono a assistência?','Use os canais e orientações informados no bilhete e no material do seguro. Guarde esses documentos em um local fácil de acessar durante a viagem.')])
create('seguro-viagem','Seguro viagem Retrato + Universal Assistance',insurance,'Conheça o seguro viagem Retrato e Universal Assistance e solicite uma cotação para o seu destino.')

members=heading('Área do cliente','Sua viagem.<br>O próximo passo,<br><em>bem à mão.</em>','Já está planejando com a Retrato? Entre no ambiente oficial indicado pela agência.')
members+='<section class="client-access section-wrap"><div><span class="client-icon" aria-hidden="true">↗</span><h2>Acesse sua viagem</h2><p>Continue no portal usado pela Retrato para acompanhar sua viagem. O acesso acontece no ambiente oficial.</p><a class="button button-dark" href="https://viagens.meuagente.com/br/trips/" target="_blank" rel="noopener">Ir para minha viagem <span>↗</span></a></div><div><p class="eyebrow">PRECISA DE UMA MÃO?</p><h3>O atendimento<br>começa com proximidade.</h3><p>Para dúvidas sobre acesso ou sobre uma viagem em planejamento, use os canais oficiais da agência.</p><a class="text-link" href="'+CONTACT+'" target="_blank" rel="noopener" data-direct-contact>Falar com a Retrato <span>↗</span></a><a class="text-link" href="mailto:contato@agenciaretrato.com">Enviar um e-mail <span>↗</span></a></div></section>'

create('members','Área do cliente',members,'Acesse o portal oficial da sua viagem ou fale com o atendimento da Agência Retrato.')

contact=heading('Contato','A viagem começa<br>no seu <em>momento.</em>','Você traz a ideia. A Retrato ajuda a conectar destinos, experiências e o tempo para viver cada escolha.')
contact+='<section class="contact-options section-wrap"><article class="contact-primary"><p class="eyebrow">UM PRIMEIRO PASSO, SEM PRESSA</p><h2>O que faria esta<br>viagem ser <em>sua?</em></h2><p>Destino, ritmo, ocasião. Organize suas preferências em três etapas curtas e leve um resumo pronto para a conversa.</p><ol class="contact-steps"><li><span>01</span> Sua ideia de viagem</li><li><span>02</span> Datas e companhia</li><li><span>03</span> Um resumo para começar</li></ol>'+cta('Desenhar minha viagem')+'<p class="field-hint">Suas escolhas só chegam à agência quando você envia a mensagem.</p></article><article class="contact-direct"><p class="eyebrow">PREFERE COMEÇAR COM UMA CONVERSA?</p><h3>Estamos por aqui.</h3><a class="contact-channel" href="'+CONTACT+'" target="_blank" rel="noopener" data-direct-contact><span>WhatsApp<small>+55 (11) 3288-0015</small></span></a><a class="contact-channel" href="mailto:contato@agenciaretrato.com"><span>E-mail<small>contato@agenciaretrato.com</small></span></a><a class="contact-channel" href="'+INSTAGRAM+'" target="_blank" rel="noopener"><span>Instagram<small>@agencia.re.trato</small></span></a><div class="contact-existing"><p>Já está viajando com a Retrato?</p><a class="text-link" href="/members/">Acesse sua viagem</a></div><p class="field-hint">Agência Retrato Viagens e Experiências Ltda.<br>São Paulo, Brasil</p></article></section>'
contact+=faq([('Ainda não sei para onde viajar. Posso começar?','Sim. Parta de uma intenção: descansar, celebrar, descobrir ou viajar a trabalho. No planejamento, você pode selecionar “Quero sugestões”.'),('O resumo confirma uma reserva?','O resumo inicia a conversa. O atendimento consulta disponibilidade e apresenta uma proposta; a contratação depende das condições dos serviços escolhidos.'),('Quero conhecer destinos antes de conversar.','Explore a página de destinos e o Journal para encontrar lugares, hotéis e experiências que combinam com o seu momento.')])
create('contato','Contato',contact,'Organize suas preferências em três etapas ou fale pelos canais oficiais da Agência Retrato.')

faqcontent=heading('Perguntas frequentes','Antes de partir,<br><em>vamos esclarecer.</em>','Respostas para começar o planejamento com mais confiança.')
faqcontent+=faq([('O que uma agência boutique faz?','A curadoria parte do perfil do viajante. Destinos, hospedagens e logística são considerados em conjunto para compor uma viagem sob medida.'),('A Retrato atende viagens corporativas?','Sim. A agência apresenta gestão de viagens para executivos e pequenos grupos.'),('Os destinos apresentados são pacotes fechados?','Nesta experiência, os destinos são inspirações de curadoria. Datas, serviços e condições são definidos no atendimento.'),('Um pedido no site confirma uma reserva?','Não. O planejamento guiado monta um resumo para iniciar a conversa. Reservas dependem da proposta, das condições e das confirmações aplicáveis.'),('Onde consulto eSIM e seguro?','Use as páginas Retrato Chip e Seguro viagem para encontrar informações e os canais oficiais de contratação.'),('Onde acesso uma viagem já planejada?','A Área do cliente encaminha você ao portal oficial utilizado pela agência.')])
create('perguntas-frequentes','Perguntas frequentes',faqcontent)

legal=[('política-de-privacidade','Privacidade','Política de <em>Privacidade.</em>'),('política-de-cookies','Cookies','Política de <em>Cookies.</em>'),('termos-e-condições','Termos e condições','Termos e Condições<br>de Uso e <em>Contratação.</em>')]
for path,label,title in legal:
    create(path,label,heading(label,title)+legal_sections(path),extra='legal-page')

# Editorial archive: preserve discoverable entries with navigation inside this site.
def classify(entry):
    text=normalized(entry.get('title','')+' '+entry['source'])
    if any(k in text for k in ['aere','anac','voo','aeroporto','bagagem','latam','azul','gol-','gru','passageir','sdu','sala-vip','salavip','terminal','cathay','aviacao']):return 'aviação'
    if any(k in text for k in ['design','arquitet','convento','palacio','brutalist','hospitalidade','hoxton','aman','rosewood','sofitel','mandarin','conrad']):return 'design-hospitalidade'
    if any(k in text for k in ['hotel','resort','waldorf','nannai','casana','st-regis','santorini','shebara','parador','tivoli','lanesborough','50-melhores']):return 'hoteis-residencias'
    return 'curadoria-retrato'

posts=[]
for entry in post_entries:
    path=unquote(urlsplit(entry['source']).path)
    title=entry.get('title') or ('Latin America’s 50 Best Restaurants 2024' if path.endswith('/latinamericas50bestrestaurants2024') else unquote(path.rsplit('/',1)[-1]).replace('-',' ').capitalize())
    category=classify(entry)
    date=entry.get('published') or entry.get('lastmod','')
    image=entry.get('image','')
    # Resize using the same public Wix asset transformation used by the original site.
    if image:image=image+'/v1/fill/w_960,h_640,al_c,q_85/'+image.rsplit('/',1)[-1]
    posts.append({'path':quote(path,safe='/')+'/', 'title':title, 'category':category, 'category_label':CATEGORIES[category], 'date':date[:10], 'source':entry['source'], 'image':image, 'alt':entry.get('image_alt') or 'Imagem da curadoria Retrato: '+title})
posts.sort(key=lambda p:p['date'],reverse=True)
for post in posts:post['display_date']=datetime.strptime(post['date'],'%Y-%m-%d').strftime('%d.%m.%Y') if post['date'] else 'Acervo Retrato'

def article_card(post):
    return f'<a class="archive-card" href="{post["path"]}" data-category="{h(post["category"])}" data-search="{h(normalized(post["title"]+" "+post["category_label"]))}"><div class="archive-image"><img loading="lazy" src="{h(post["image"])}" alt="{h(post["alt"])}"><span aria-hidden="true">↗</span></div><p class="eyebrow">{h(post["category_label"].upper())}</p><h3>{h(post["title"])}</h3><span class="archive-date">{datetime.strptime(post["date"],"%Y-%m-%d").strftime("%d.%m.%Y") if post["date"] else "ACERVO RETRATO"}</span></a>'

def journal_page(category=''):
    content=photo_heading('Retrato Journal','Um olhar que<br>abre <em>possibilidades.</em>','Hotelaria, cultura e histórias para abrir o seu horizonte. Encontre uma leitura, descubra um lugar e imagine o próximo capítulo.','landscape-como-4k.webp','Lago de Como entre montanhas ao amanhecer, na Itália','LAGO DE COMO, ITÁLIA · HISTÓRIAS QUE ABREM HORIZONTES',actions='<a class="photo-text-link journal-explore" href="#leituras">Explore as histórias <span aria-hidden="true">↓</span></a>',extra='journal-hero')
    content+='<section class="archive section-wrap" data-initial-category="'+h(category)+'"><div class="archive-toolbar"><label class="archive-search"><span>Buscar no Journal</span><input id="journal-search" type="search" placeholder="Destino, hotel ou assunto" aria-label="Buscar por destino, hotel ou assunto"><span class="search-icon" aria-hidden="true">⌕</span></label><div class="archive-filters" role="group" aria-label="Categorias do Journal"><button type="button" data-journal-category="" aria-pressed="true">Tudo</button>'+''.join(f'<button type="button" data-journal-category="{h(key)}" aria-pressed="false">{h(value)}</button>' for key,value in CATEGORIES.items())+'</div></div><div class="archive-status"><p id="journal-count" role="status" aria-live="polite"></p><button id="journal-clear" type="button" hidden>Limpar busca e filtros ×</button></div><div class="archive-grid">'+''.join(article_card(p) for p in posts)+'</div><div class="archive-empty" id="journal-empty" hidden><h3>A próxima descoberta<br>pode começar de outro jeito.</h3><p>Tente outro destino ou assunto, ou limpe os filtros para explorar todo o acervo.</p></div><div class="archive-more"><button class="button button-dark" id="journal-more" type="button">Mais histórias <span>↓</span></button></div></section>'
    return content.replace('<section class="archive section-wrap"','<section id="leituras" class="archive section-wrap"',1)

create('retrato-news','Retrato Journal',journal_page(),'Explore o acervo completo da Retrato por tema, destino ou hotel.')
for key,value in CATEGORIES.items():create('retrato-news/categories/'+key,value+' — Journal',journal_page(key),'Conteúdos de '+value.lower()+' na curadoria Retrato.')

for post in posts:
    slug=unquote(post['path']).strip('/').rsplit('/',1)[-1]
    draft=JOURNAL[slug]
    reading,minutes=article_reading(draft)
    if slug=='seguro-viagem-retrato-universal-assistance':
        content=insurance[:insurance.index('<section class="insurance-introduction')]
    else:
        content=f'<section class="article-hero section-wrap"><nav class="breadcrumbs" aria-label="Você está aqui"><a href="/">Início</a><span aria-hidden="true">/</span><a href="/retrato-news/">Journal</a><span aria-hidden="true">/</span><a href="/retrato-news/categories/{quote(post["category"])}/">{h(post["category_label"])}</a></nav><p class="eyebrow">{h(post["category_label"].upper())}</p><h1>{h(post["title"])}</h1><p class="article-byline"><span>ACERVO · <time datetime="{post["date"]}">{post["display_date"]}</time></span><span>{minutes} MIN DE LEITURA</span><span>LEITURA REVISADA EM 01.10.2026</span></p><figure class="article-cover"><img src="{h(post["image"])}" alt="{h(post["alt"])}" fetchpriority="high"><figcaption>Imagem do acervo editorial da Retrato.</figcaption></figure></section>'
    reading_anchor=' id="protecao"' if slug=='seguro-viagem-retrato-universal-assistance' else ''
    content+='<section class="article-layout section-wrap"'+reading_anchor+'>'+reading+'</section>'
    related=[p for p in posts if p['category']==post['category'] and p['path']!=post['path']][:3]
    content+='<section class="related-articles section-wrap"><p class="eyebrow">CONTINUE DESCOBRINDO</p><h2>O próximo <em>olhar.</em></h2><div class="archive-grid">'+''.join(article_card(p) for p in related)+'</div></section>'
    create(unquote(post['path']).strip('/'),post['title'],content,draft['lead'],extra='article-page')

# Destination pages connect editorial inspiration to the planning experience.
destination_data=[
 {'slug':'milagres','name':'Milagres','choice':'Milagres, Alagoas','location':'ALAGOAS · BRASIL','image':'milagres.jpg','stay_image':'milagres.jpg','stay_alt':'Praia do Marceneiro na Costa dos Corais, Alagoas','article':'reveillon-2027-nannai-milagres-pacote-valores','headline':'O mar encontra<br>o seu <em>tempo.</em>','intro':'A Costa dos Corais como ponto de partida para uma viagem de praia, descanso e celebração.','editorial_title':'Dias leves.<br><em>Boas escolhas.</em>','editorial':'Na Praia do Marceneiro, a paisagem de Alagoas convida a desacelerar. A curadoria pode começar pelo que você quer viver: descansar à beira-mar ou celebrar uma ocasião especial.','stay':'NANNAI Milagres','stay_copy':'Um endereço presente na curadoria da Retrato. Para o fim de ano, o Journal reúne informações sobre a hospedagem e a celebração de Réveillon. Período, categoria e condições precisam ser consultados antes de definir a viagem.','highlights':[('Mar & natureza','A paisagem da Costa dos Corais como companhia para os seus dias.'),('Tempo a dois','Uma intenção de viagem que combina praia e presença.'),('Celebrações','Uma ocasião especial pode orientar o desenho da jornada.')]},
 {'slug':'praia-do-prea','name':'Praia do Preá','choice':'Praia do Preá, Ceará','location':'CEARÁ · BRASIL','image':'prea.jpg','stay_image':'bungalow.webp','stay_alt':'Bangalô e piscina privativa no Casana Hotel','article':'casana-hotel-praia-do-prea-slh','headline':'O vento muda.<br>Seu ritmo é <em>seu.</em>','intro':'Mar, natureza e hotelaria em pequena escala no litoral do Ceará.','editorial_title':'Um refúgio.<br><em>Outro ritmo.</em>','editorial':'O Preá aproxima a viagem do mar e do vento. Na curadoria da Retrato, o destino encontra uma proposta de hospedagem reservada, com espaço para combinar descanso e atividade.','stay':'Casana Hotel','stay_copy':'Sete bangalôs compõem este refúgio boutique. A experiência conecta praia, kitesurf, gastronomia e bem-estar. A escolha do período deve considerar o vento e o perfil de quem viaja.','highlights':[('Praia & vento','O cenário do litoral cearense participa da experiência.'),('Hospitalidade boutique','Uma hospedagem em pequena escala, com atenção à privacidade.'),('Bem-estar','Dias de descanso podem alternar com atividades no mar.')]},
 {'slug':'rio-de-janeiro','name':'Rio de Janeiro','choice':'Rio de Janeiro','location':'RIO DE JANEIRO · BRASIL','image':'rio.jpeg','stay_image':'rio.jpeg','stay_alt':'Gastronomia da curadoria Retrato no Rio de Janeiro','article':'melhores-restaurantes-bares-rio-de-janeiro-2026-teste-pt','headline':'Uma cidade.<br>Muitos <em>encontros.</em>','intro':'Descubra o Rio também à mesa, pela gastronomia e pelos lugares que fazem cada ocasião valer a viagem.','editorial_title':'A cidade tem<br><em>outros sabores.</em>','editorial':'Entre restaurantes e bares, a curadoria da Retrato propõe um olhar para o Rio a partir da gastronomia. A escolha de uma boa mesa pode se tornar um dos momentos centrais da viagem.','stay':'Uma curadoria à mesa','stay_copy':'O Journal reúne restaurantes e bares selecionados para considerar no planejamento. Perfil, ocasião e logística ajudam a organizar as escolhas sem transformar os dias em uma sequência apressada.','highlights':[('Gastronomia','Escolha as mesas que combinam com a ocasião.'),('Cultura urbana','Deixe espaço para descobrir a cidade entre os encontros.'),('Seu tempo','Organize as experiências com margem para aproveitar.')]},
 {'slug':'maldivas','name':'Maldivas','choice':'Maldivas','location':'OCEANO ÍNDICO','image':'maldivas.jpg','stay_image':'maldivas.jpg','stay_alt':'Villas sobre a água em uma ilha das Maldivas','article':'viagem-maldivas-guia-resorts-melhor-epoca','headline':'Todos os azuis.<br>Um horizonte <em>seu.</em>','intro':'Uma viagem em que a escolha da ilha muda a maneira de viver cada dia.','editorial_title':'O lugar certo<br>para <em>estar presente.</em>','editorial':'Nas Maldivas, a hospedagem é parte central da experiência. A ilha define paisagem, acesso ao mar e o percurso desde a chegada. A curadoria conecta essas escolhas ao que você procura na viagem.','stay':'Sua ilha, seu refúgio','stay_copy':'Villa na praia ou sobre a água, refeições e traslados precisam ser pensados juntos. O roteiro começa com o seu perfil e ganha forma conforme o período, a disponibilidade e o estilo do resort.','highlights':[('Uma ilha','Privacidade e paisagem como critérios de escolha.'),('Sua hospedagem','O tipo de villa influencia o jeito de viver o destino.'),('Logística conectada','O traslado faz parte da experiência desde a chegada.')]},
 {'slug':'roma','name':'Roma','choice':'Roma, Itália','location':'ITÁLIA','image':'rome.jpg','stay_image':'rome.jpg','stay_alt':'Anantara Palazzo Naiadi na Piazza della Repubblica, Roma','article':'anantara-palazzo-naiadi-rome-hotel','headline':'Histórias eternas.<br>Descobertas <em>suas.</em>','intro':'Arquitetura, hospitalidade e um novo olhar para viver Roma.','editorial_title':'O passado inspira.<br>Você vive <em>o presente.</em>','editorial':'Roma convida a combinar descobertas com tempo para permanecer. Uma localização bem escolhida ajuda a organizar os deslocamentos e a criar espaço para experiências que tenham relação com o seu perfil.','stay':'Anantara Palazzo Naiadi','stay_copy':'A Piazza della Repubblica é o cenário deste endereço apresentado pelo Journal da Retrato. Uma inspiração de hotelaria que conecta patrimônio e a experiência de estar no centro da cidade.','highlights':[('História & arquitetura','Um cenário para descobrir com calma.'),('Hospitalidade','O hotel como ponto de partida para viver a cidade.'),('Gastronomia','Encontros à mesa em sintonia com o seu roteiro.')]}
]
for d in destination_data:
    content=f'<section class="destination-hero"><img src="/assets/{d["image"]}" alt="{h(d["name"])} na curadoria da Retrato" fetchpriority="high"><div class="destination-hero-shade"></div><div class="destination-hero-copy"><a class="destination-back" href="/roteiros/">← Explore os destinos</a><p class="eyebrow light">{d["location"]}</p><h1>{d["headline"]}</h1><p>{d["intro"]}</p>{cta("Planeje sua viagem",d["choice"])}</div><a class="destination-scroll" href="#descubra">Descubra {h(d["name"])} <span>↓</span></a></section>'
    content+=f'<nav class="destination-subnav" aria-label="Explore esta viagem"><a href="#descubra">O destino</a><a href="#momentos">Experiências</a><a href="#curadoria">Curadoria</a></nav>'
    content+=f'<section id="descubra" class="destination-editorial section-wrap"><div><p class="eyebrow">{h(d["name"].upper())} · UM NOVO OLHAR</p><h2>{d["editorial_title"]}</h2></div><div><p class="destination-lead">{d["editorial"]}</p><p>Uma viagem sob medida encontra o equilíbrio entre o que você quer viver e as escolhas que tornam isso possível.</p></div></section>'
    content+='<section class="destination-highlights section-wrap" id="momentos"><p class="eyebrow">POSSIBILIDADES PARA SUA VIAGEM</p><div>'+''.join(f'<article><span>{i:02} /</span><h3>{title}</h3><p>{desc}</p></article>' for i,(title,desc) in enumerate(d['highlights'],1))+'</div></section>'
    content+=f'<section class="destination-stay section-wrap" id="curadoria"><div class="destination-stay-image"><img src="/assets/{d["stay_image"]}" alt="{h(d["stay_alt"])}" loading="lazy"></div><div><p class="eyebrow">UM ENDEREÇO. UMA INSPIRAÇÃO.</p><h2>{h(d["stay"])}</h2><p>{d["stay_copy"]}</p><a class="text-link" href="/retratonews/{quote(d["article"])}/">Explore a leitura do Journal <span>↗</span></a></div></section>'
    content+=faq([('Essa viagem tem um roteiro fechado?','O destino é uma inspiração. O roteiro é construído conforme suas preferências, período e perfil dos viajantes.'),('Como consulto os valores?','Comece o planejamento com seu destino e período. A Retrato consulta os serviços e apresenta as condições para a sua viagem.'),('Posso combinar este destino com outros lugares?','Leve essa ideia para o atendimento. A combinação precisa considerar deslocamentos e o tempo disponível.')])
    content+=f'<div class="destination-sticky" inert><div><span>{d["location"]}</span><strong>{h(d["name"])}</strong></div>{cta("Planeje esta viagem",d["choice"])}</div>'
    route_paths.add('/destinos/'+d['slug'])
    create('destinos/'+d['slug'],d['name']+' — Viagem sob medida',content,d['intro'],extra='destination-page')

dest_links={'/retratonews/'+d['article']+'/':'/destinos/'+d['slug']+'/' for d in destination_data}
for file in DIST.rglob('index.html'):
    html=file.read_text()
    def destination_link(match):
        attrs=match.group(1)
        href=re.search(r'href="([^"]*)"',attrs)
        key=unquote(href.group(1)) if href else ''
        if key in dest_links:attrs=attrs.replace(href.group(0),'href="'+dest_links[key]+'"')+' data-destination-page="true"'
        return '<a class="destination-card"'+attrs+'>'
    html=re.sub(r'<a class="destination-card"([^>]*)>',destination_link,html)
    file.write_text(html)
(DIST/'assets/posts.json').write_text(json.dumps(posts,ensure_ascii=False))
(ROOT/'sources/route-manifest.json').write_text(json.dumps(ROUTES,ensure_ascii=False,indent=2))
notfound=heading('Página não encontrada','O caminho mudou.<br>A descoberta <em>continua.</em>','Encontre sua próxima inspiração ou volte ao início da Retrato.')+'<section class="not-found section-wrap"><a class="button button-dark" href="/">Voltar ao início <span>↗</span></a><a class="text-link" href="/roteiros/">Explorar destinos <span>↗</span></a></section>'
create('404','Página não encontrada',notfound)
(DIST/'404.html').write_text((DIST/'404/index.html').read_text())
print(json.dumps({'pages':len(ROUTES),'articles':len(posts),'categories':len(CATEGORIES)},ensure_ascii=False))
