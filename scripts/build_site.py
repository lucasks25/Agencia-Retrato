"""Build the complete static Retrato site from a shared shell and verified source index."""
import json, re, unicodedata, hashlib
from datetime import datetime
from html import escape as h
from pathlib import Path
from urllib.parse import unquote, urlsplit, quote

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
SOURCE=json.loads((ROOT/'sources/inventory.json').read_text())
HOME=(ROOT/'templates/home.html').read_text()
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
    versions={name:hashlib.sha256((DIST/name).read_bytes()).hexdigest()[:12] for name in ('styles.css','app.js','ocean.js')}
    return re.sub(r'(href|src)="(assets/[^\"]*|styles\.css|app\.js|ocean\.js)"',lambda m:m.group(1)+'="/'+m.group(2)+('?v='+versions[m.group(2)] if m.group(2) in versions else '')+'"',html)
def cta(label='Planeje sua viagem',choice=''):
    return f'<button type="button" class="button button-dark" data-plan-destination="{h(choice)}">{h(label)} <span>↗</span></button>'
def heading(kicker,title,description=''):
    return f'<section class="page-heading section-wrap"><nav class="breadcrumbs" aria-label="Você está aqui"><a href="/">Início</a><span aria-hidden="true">/</span><span>{h(kicker)}</span></nav><p class="eyebrow">{h(kicker.upper())}</p><h1>{title}</h1>{"<p class=page-intro>"+description+"</p>" if description else ""}</section>'
def end_cta(title='A próxima viagem começa<br>com <em>você.</em>',description='Conte suas ideias. A Retrato ajuda a dar forma ao próximo capítulo.'):
    return f'<section class="page-cta section-wrap"><div><p class="eyebrow">DO DESEJO AO EMBARQUE</p><h2>{title}</h2><p>{description}</p></div>{cta("Vamos planejar")}</section>'
def feature_rows(items):
    return '<div class="feature-rows">'+''.join(f'<article><span>{i:02}</span><div><h3>{title}</h3><p>{description}</p></div></article>' for i,(title,description) in enumerate(items,1))+'</div>'
def faq(items):
    return '<section class="faq-section section-wrap"><div><p class="eyebrow">ANTES DE COMEÇAR</p><h2>Boas perguntas.<br><em>Escolhas mais claras.</em></h2></div><div>'+''.join(f'<details><summary>{q}<span aria-hidden="true">+</span></summary><p>{a}</p></details>' for q,a in items)+'</div></section>'
def create(path,title,content,description='',extra=''):
    ROUTES.append(path)
    target=DIST/path.strip('/')/'index.html' if path else DIST/'index.html'
    target.parent.mkdir(parents=True,exist_ok=True)
    head=re.sub(r'<title>.*?</title>',f'<title>{h(title)} | Agência Retrato</title>',HEAD)
    head=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{h(description or title)}">',head)
    head=re.sub(r'<meta property="og:title" content="[^"]*">',f'<meta property="og:title" content="{h(title)} | Agência Retrato">',head)
    head=re.sub(r'<meta property="og:description" content="[^"]*">',f'<meta property="og:description" content="{h(description or title)}">',head)
    head=re.sub(r'  <link rel="preload"[^\n]*\n','',head)
    html='<!doctype html>\n<html lang="pt-BR">\n'+head+'\n<body class="inner-page '+extra+'"><a class="skip" href="#conteudo">Ir para o conteúdo</a>'+SHELL_HEADER+'<main id="conteudo">'+content+'</main>'+SHELL_FOOTER+DIALOGS+'</body></html>'
    html=root_assets(link_map(html))
    html=html.replace('href="#inicio"','href="/"').replace('href="#destinos"','href="/roteiros/"').replace('href="#experiencia"','href="/agencia-boutique/"').replace('href="#sobre"','href="/sobre/"').replace('href="#journal"','href="/retrato-news/"')
    html=re.sub(r'(<a[^>]*data-local="true"[^>]*)(?: target="_blank")',r'\1',html)
    target.write_text(html)

# Every public original route is represented; integrations retain their real external destinations.
post_entries=[x for x in SOURCE if x.get('type')!='page']
route_paths={'','/sobre','/agencia-boutique','/roteiros','/retrato-chip','/members','/retrato-news','/seguro-viagem','/contato','/perguntas-frequentes','/política-de-privacidade','/política-de-cookies','/termos-e-condições'}
route_paths.update(unquote(urlsplit(p['source']).path).rstrip('/') for p in post_entries)
route_paths.update('/retrato-news/categories/'+c for c in CATEGORIES)

# Replace the landing page's header with real site navigation.
SHELL_HEADER=SHELL_HEADER.replace('href="#destinos"','href="/roteiros/"').replace('href="#experiencia"','href="/agencia-boutique/"').replace('href="#sobre"','href="/sobre/"').replace('href="#journal"','href="/retrato-news/"')
SHELL_HEADER=SHELL_HEADER.replace('<a href="/retrato-news/">Journal</a>','<a href="/retrato-news/">Journal</a><details class="services-menu"><summary>Sua viagem <span>⌄</span></summary><div><a href="/retrato-chip/">Retrato Chip <small>Conectividade no exterior</small></a><a href="/seguro-viagem/">Seguro viagem <small>Proteção para sua jornada</small></a><a href="/members/">Acesse sua viagem <small>Área do cliente</small></a><a href="/contato/">Fale com a Retrato <small>Uma conversa para começar</small></a></div></details>',1)
SHELL_HEADER=SHELL_HEADER.replace('<a href="https://viagens.meuagente.com/br/trips/" target="_blank" rel="noopener">Acesse sua viagem ↗</a>','<a href="/retrato-chip/">Retrato Chip</a><a href="/seguro-viagem/">Seguro viagem</a><a href="/members/">Acesse sua viagem</a><a href="/contato/">Contato</a>')
home=HOME[:HOME.index('  <header')]+SHELL_HEADER+HOME[HOME.index('  <main'):]
home=root_assets(link_map(home))
home=re.sub(r'(<a[^>]*data-local="true"[^>]*)(?: target="_blank")',r'\1',home)
(DIST/'index.html').write_text(home)
ROUTES.append('')

# About: identity and credibility, followed by a natural planning action.
about=heading('A Retrato','Uma viagem.<br>Um <em>retrato seu.</em>','Uma agência boutique em São Paulo, dedicada a viagens de luxo sob medida e à gestão de viagens corporativas para executivos e pequenos grupos.')
about+='<section class="split-editorial section-wrap"><div class="editorial-image"><img src="/assets/retreat.jpg" alt="Piscina com vista para lago e montanhas ao entardecer"></div><div><p class="eyebrow">ESCUTA. CRITÉRIO. CUIDADO.</p><h2>Antes do destino,<br><em>vem você.</em></h2><p>Uma viagem começa com a leitura do seu momento. Descanso, celebração, descoberta ou trabalho: a intenção orienta as escolhas.</p><p>A Retrato conecta hospedagem, transporte e experiências em um desenho atento ao tempo, ao conforto e à privacidade. O objetivo é que cada etapa converse com a próxima.</p>'+cta('Conte sua ideia')+'</div></section>'
about+='<section class="values section-wrap"><p class="eyebrow">O QUE ORIENTA A CURADORIA</p>'+feature_rows([('Seu momento','Preferências e prioridades ajudam a definir a direção da viagem.'),('Escolhas coerentes','Ritmo, logística e hospedagem são pensados em conjunto.'),('Cuidado próximo','Uma condução personalizada para jornadas de lazer e de trabalho.')])+'</section>'
about+='<section class="credibility section-wrap"><span>São Paulo<br><small>NOSSA BASE</small></span><span>55.563.619/0001-04<br><small>CNPJ</small></span><span>96195702<br><small>IATA · TIDS</small></span></section>'+end_cta()
create('sobre','Sobre a Retrato',about,'Conheça a agência boutique de viagens sob medida com base em São Paulo.')

boutique=heading('A experiência Retrato','O mundo é amplo.<br>A curadoria é <em>pessoal.</em>','Uma viagem sob medida começa quando suas prioridades se tornam o centro de cada decisão.')
boutique+='<section class="split-editorial section-wrap"><div><p class="eyebrow">COMO PENSAMOS SUA VIAGEM</p><h2>Os detalhes fazem<br><em>o todo.</em></h2><p>Voos, conexões, hotelaria e deslocamentos influenciam o tempo que você terá para aproveitar o destino. A curadoria boutique olha para essa relação.</p><p>Seu ritmo e o nível de serviço desejado orientam as alternativas. Em uma viagem de lazer ou na agenda de um pequeno grupo executivo, conforto e precisão precisam caminhar juntos.</p>'+cta('Desenhe sua viagem')+'</div><div class="editorial-image"><img src="/assets/bungalow.webp" alt="Bangalô com piscina privativa no Casana Hotel"></div></section>'
boutique+='<section class="service-types section-wrap"><p class="eyebrow">DOIS CONTEXTOS. O MESMO CUIDADO.</p><div class="service-grid"><article><span>01 / LAZER</span><h3>Viajar no seu ritmo</h3><p>Preferências de hospedagem, dias livres e experiências que combinem com o momento da viagem.</p>'+cta('Planejar uma viagem de lazer')+'</article><article><span>02 / CORPORATIVO</span><h3>Tempo bem organizado</h3><p>Gestão para executivos e pequenos grupos, com atenção à logística, ao conforto e à discrição.</p>'+cta('Conversar sobre uma viagem corporativa')+'</article></div></section>'
boutique+=faq([('Preciso chegar com um roteiro pronto?','Não. Comece com uma ideia, um período ou uma intenção. Esses pontos ajudam a orientar a conversa.'),('É possível incluir destinos brasileiros?','Sim. Explore as inspirações pelo Brasil e converse com a Retrato sobre a combinação mais adequada ao seu perfil.'),('Como são definidos preços e disponibilidade?','Datas, serviços e perfil dos viajantes orientam a consulta. As condições são apresentadas na proposta e precisam de confirmação.')])+end_cta()
create('agencia-boutique','A experiência boutique',boutique,'Curadoria de viagens com atenção ao seu ritmo, à hotelaria e à logística.')

dest_block=HOME[HOME.index('    <section class="destinations"'):HOME.index('    <section class="experience')]
dest_block=re.sub(r'<div class="section-heading">.*?</div>\s*<div class="destination-toolbar">','<div class="destination-toolbar">',dest_block,flags=re.S)
roteiros=heading('Destinos & roteiros','O seu próximo<br><em>capítulo.</em>','Descubra lugares, hotéis e experiências da curadoria Retrato. Uma inspiração é o começo; o roteiro é desenhado para você.')+dest_block
roteiros+='<section class="trip-intents section-wrap"><p class="eyebrow">MAIS QUE UM LUGAR, UMA INTENÇÃO</p><h2>O que você quer<br><em>levar na memória?</em></h2><div class="intent-grid">'+''.join('<button class="intent-card" type="button" data-plan-vibe="'+vibe+'"><span>'+num+'</span><h3>'+label+'</h3><p>'+desc+'</p><span class="intent-arrow">↗</span></button>' for num,label,desc,vibe in [('01','Desacelerar','Mar, descanso e um hotel para chamar de refúgio.','Praia e descanso'),('02','Descobrir','Sabores, arte e novas maneiras de viver uma cidade.','Cultura e gastronomia'),('03','Reconectar','Natureza e tempo para estar presente.','Natureza e bem-estar'),('04','Realizar','Uma agenda de trabalho com logística bem conduzida.','Viagem corporativa')])+'</div></section>'+end_cta()
create('roteiros','Destinos e roteiros',roteiros,'Inspirações brasileiras e internacionais para desenhar uma viagem sob medida.')

chip=heading('Retrato Chip','O mundo mais perto.<br>Você mais <em>conectado.</em>','Conectividade internacional como parte do planejamento da sua viagem.')
chip+='<section class="chip-section section-wrap"><div class="chip-visual"><div class="chip-orbit orbit-one"></div><div class="chip-orbit orbit-two"></div><div class="esim-card"><span>agência (re)trato</span><svg width="55" height="55" viewBox="0 0 55 55" fill="none" aria-hidden="true"><rect x="12" y="9" width="31" height="37" rx="6" stroke="currentColor" stroke-width="1.5"/><path d="M22 9v10h11V9M12 27h31M22 46V35h11v11" stroke="currentColor" stroke-width="1.5"/></svg><strong>Seu mundo.<br>Sem distância.</strong><span>RETRATO CHIP · eSIM</span></div></div><div><p class="eyebrow">CONECTIVIDADE NO EXTERIOR</p><h2>Antes de embarcar,<br><em>conecte as escolhas.</em></h2><p>O Retrato Chip é a solução de eSIM internacional da agência. O destino e o aparelho precisam ser compatíveis com o plano escolhido.</p><p>Consulte cobertura, franquia, validade e condições antes da contratação. A instalação deve seguir as instruções fornecidas para o seu eSIM.</p><button class="button button-dark" type="button" data-plan-service="Retrato Chip / eSIM">Consultar planos com a Retrato <span>↗</span></button></div></section>'
chip+=faq([('Como escolho o plano?','Comece pelo destino, duração da viagem e seu uso de dados. Confira a cobertura e as condições exibidas no ambiente oficial.'),('Meu celular aceita eSIM?','A compatibilidade depende do modelo e das condições do aparelho. Confirme essa informação antes da contratação.'),('Onde consulto os planos e faço a contratação?','Use o botão de consulta para conversar com a Retrato sobre os planos disponíveis e as condições de contratação.')])+end_cta('Cada detalhe faz parte<br><em>da viagem.</em>','Além da conexão, vamos pensar no destino, na hospedagem e no seu ritmo.')
create('retrato-chip','Retrato Chip — eSIM internacional',chip,'Conectividade internacional com o Retrato Chip. Consulte compatibilidade, destinos e planos oficiais.')

insurance=heading('Seguro viagem','Cuidado que acompanha<br>cada <em>embarque.</em>','Retrato + Universal Assistance: proteção e assistência como parte da viagem.')
insurance+='<section class="insurance-overview section-wrap"><div><p class="eyebrow">UMA ESCOLHA QUE MERECE ATENÇÃO</p><h2>Proteção pensada<br>para <em>o seu perfil.</em></h2><p>Destino, duração e atividades previstas ajudam a escolher o seguro. Os limites e benefícios são definidos pelo produto contratado.</p><button class="button button-dark" type="button" data-plan-service="Seguro viagem">Solicitar uma cotação <span>↗</span></button></div>'+feature_rows([('Assistência médica','Atendimento médico e hospitalar, conforme as condições e os limites do plano.'),('Recursos digitais','Aplicativo e teleassistência para facilitar o acionamento dos serviços.'),('Diferentes modalidades','Opções para viagens nacionais, internacionais e viajantes frequentes.')])+'</section>'
insurance+=faq([('Todos os planos têm as mesmas coberturas?','Não. Consulte o bilhete e as condições do produto para conhecer limites, exclusões e serviços.'),('O que considerar antes da escolha?','Destino, duração, perfil dos viajantes e atividades previstas. Compare a proteção necessária para a sua viagem.'),('Como faço a cotação?','Converse com a Retrato pelo botão desta página. O atendimento orienta a consulta e apresenta as condições antes da contratação.')])+end_cta()
create('seguro-viagem','Seguro viagem',insurance,'Seguro viagem Retrato e Universal Assistance: conheça os pontos importantes antes de escolher sua proteção.')

members=heading('Área do cliente','Sua viagem.<br>O próximo passo,<br><em>bem à mão.</em>','Já está planejando com a Retrato? Entre no ambiente oficial indicado pela agência.')
members+='<section class="client-access section-wrap"><div><span class="client-icon" aria-hidden="true">↗</span><h2>Acesse sua viagem</h2><p>Continue no portal usado pela Retrato para acompanhar sua viagem. O acesso acontece no ambiente oficial.</p><a class="button button-dark" href="https://viagens.meuagente.com/br/trips/" target="_blank" rel="noopener">Ir para minha viagem <span>↗</span></a></div><div><p class="eyebrow">PRECISA DE UMA MÃO?</p><h3>O atendimento<br>começa com proximidade.</h3><p>Para dúvidas sobre acesso ou sobre uma viagem em planejamento, use os canais oficiais da agência.</p><a class="text-link" href="'+CONTACT+'" target="_blank" rel="noopener" data-direct-contact>Falar com a Retrato <span>↗</span></a><a class="text-link" href="mailto:contato@agenciaretrato.com">Enviar um e-mail <span>↗</span></a></div></section>'
members+=end_cta('Pensando em uma<br><em>nova viagem?</em>','Se você ainda não começou, conte o que imagina para o próximo embarque.')
create('members','Área do cliente',members,'Acesse o portal oficial da sua viagem ou fale com o atendimento da Agência Retrato.')

contact=heading('Contato','A melhor viagem<br>começa com <em>escuta.</em>','Uma ideia, um destino, um desejo. Vamos dar forma ao que você quer viver.')
contact+='<section class="contact-options section-wrap"><article><p class="eyebrow">PARA COMEÇAR A PLANEJAR</p><h2>Conte sua ideia.</h2><p>Organize suas primeiras preferências e leve um resumo para a conversa com a Retrato.</p>'+cta('Comece seu planejamento')+'</article><article><p class="eyebrow">PARA UMA CONVERSA DIRETA</p><h3>Vamos nos conectar</h3><a class="contact-channel" href="'+CONTACT+'" target="_blank" rel="noopener" data-direct-contact>WhatsApp <span>↗</span></a><a class="contact-channel" href="mailto:contato@agenciaretrato.com">contato@agenciaretrato.com <span>↗</span></a><a class="contact-channel" href="'+BASE+'/instagram" target="_blank" rel="noopener">Instagram <span>↗</span></a><p class="field-hint">Agência Retrato Viagens e Experiências Ltda.<br>São Paulo, Brasil</p></article></section>'
contact+=faq([('Ainda não sei para onde viajar. Posso conversar?','Sim. Uma intenção já ajuda: descanso, cultura, natureza ou trabalho. O planejamento guiado organiza esse primeiro ponto de partida.'),('Já tenho uma viagem com a Retrato. Onde acesso?','Na Área do cliente, você encontra o encaminhamento para o portal oficial da sua viagem.'),('Onde encontro as inspirações da agência?','No Journal, explore artigos de hotelaria, curadoria, design e aviação. Na página de roteiros, descubra as primeiras inspirações.')])
create('contato','Contato',contact,'Planeje uma viagem sob medida ou fale diretamente com a Agência Retrato.')

faqcontent=heading('Perguntas frequentes','Antes de partir,<br><em>vamos esclarecer.</em>','Respostas para começar o planejamento com mais confiança.')
faqcontent+=faq([('O que uma agência boutique faz?','A curadoria parte do perfil do viajante. Destinos, hospedagens e logística são considerados em conjunto para compor uma viagem sob medida.'),('A Retrato atende viagens corporativas?','Sim. A agência apresenta gestão de viagens para executivos e pequenos grupos.'),('Os destinos apresentados são pacotes fechados?','Nesta experiência, os destinos são inspirações de curadoria. Datas, serviços e condições são definidos no atendimento.'),('Um pedido no site confirma uma reserva?','Não. O planejamento guiado monta um resumo para iniciar a conversa. Reservas dependem da proposta, das condições e das confirmações aplicáveis.'),('Onde consulto eSIM e seguro?','Use as páginas Retrato Chip e Seguro viagem para encontrar informações e os canais oficiais de contratação.'),('Onde acesso uma viagem já planejada?','A Área do cliente encaminha você ao portal oficial utilizado pela agência.')])+end_cta()
create('perguntas-frequentes','Perguntas frequentes',faqcontent)

legal=[('política-de-privacidade','Privacidade','Suas informações,<br>com <em>clareza.</em>','O planejamento guiado desta página funciona no seu navegador. As preferências não são enviadas à agência automaticamente. O contato começa quando você escolhe enviar sua mensagem pelos canais oficiais.','Para informações sobre o tratamento de dados no atendimento e na prestação dos serviços, entre em contato com a Retrato pelo e-mail indicado abaixo.'),('política-de-cookies','Cookies','Uma navegação<br><em>transparente.</em>','O planejamento não usa cookies para guardar as suas escolhas. Links para o WhatsApp, o portal e outros serviços conduzem a ambientes com práticas próprias.','Para conhecer as práticas dos canais e serviços utilizados no atendimento, fale com a Retrato pelo e-mail indicado abaixo.'),('termos-e-condições','Termos e condições','Escolhas claras.<br><em>Viagens bem alinhadas.</em>','As inspirações do site não constituem confirmação de reserva ou garantia de disponibilidade. Uma viagem depende de consulta, proposta e das condições dos fornecedores.','Antes da contratação, solicite os termos ao atendimento e revise as condições apresentadas na proposta da agência.')]
for path,label,title,p1,p2 in legal:
    content=heading(label,title)+f'<section class="legal-content section-wrap"><div><h2>Sobre esta navegação</h2><p>{p1}</p><h2>Atendimento e contratação</h2><p>{p2}</p><a class="button button-dark" href="mailto:contato@agenciaretrato.com">Fale com a Retrato <span>↗</span></a><p class="legal-contact">Dúvidas? <a href="mailto:contato@agenciaretrato.com">contato@agenciaretrato.com</a></p></div><aside><p class="eyebrow">DOCUMENTOS</p><a href="/pol%C3%ADtica-de-privacidade/">Privacidade ↗</a><a href="/pol%C3%ADtica-de-cookies/">Cookies ↗</a><a href="/termos-e-condi%C3%A7%C3%B5es/">Termos e condições ↗</a><a href="/contato/">Contato ↗</a></aside></section>'
    create(path,label,content)

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
    title=entry.get('title') or unquote(path.rsplit('/',1)[-1]).replace('-',' ').capitalize()
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
    content=heading('Retrato Journal','Um olhar que<br>abre <em>possibilidades.</em>','Hotelaria, cultura, hospitalidade e informações para a viagem. Explore o acervo da Retrato por tema ou pelo destino que desperta sua curiosidade.')
    content+='<section class="archive section-wrap" data-initial-category="'+h(category)+'"><div class="archive-toolbar"><label class="archive-search"><span>Buscar no Journal</span><input id="journal-search" type="search" placeholder="Destino, hotel ou assunto" aria-label="Buscar por destino, hotel ou assunto"><span class="search-icon" aria-hidden="true">⌕</span></label><div class="archive-filters" role="group" aria-label="Categorias do Journal"><button type="button" data-journal-category="" aria-pressed="true">Tudo</button>'+''.join(f'<button type="button" data-journal-category="{h(key)}" aria-pressed="false">{h(value)}</button>' for key,value in CATEGORIES.items())+'</div></div><div class="archive-status"><p id="journal-count" role="status" aria-live="polite"></p><button id="journal-clear" type="button" hidden>Limpar busca e filtros ×</button></div><div class="archive-grid">'+''.join(article_card(p) for p in posts)+'</div><div class="archive-empty" id="journal-empty" hidden><h3>A próxima descoberta<br>pode começar de outro jeito.</h3><p>Tente outro destino ou assunto, ou limpe os filtros para explorar todo o acervo.</p></div><div class="archive-more"><button class="button button-dark" id="journal-more" type="button">Mais histórias <span>↓</span></button></div></section>'+end_cta('A inspiração vira viagem<br>quando faz sentido <em>para você.</em>')
    return content

create('retrato-news','Retrato Journal',journal_page(),'Explore o acervo completo da Retrato por tema, destino ou hotel.')
for key,value in CATEGORIES.items():create('retrato-news/categories/'+key,value+' — Journal',journal_page(key),'Conteúdos de '+value.lower()+' na curadoria Retrato.')

editorial_summaries={
 'casana-hotel-praia-do-prea-slh':'Na Praia do Preá, o Casana propõe uma hospedagem em pequena escala. Os sete bangalôs, a proximidade do mar e a relação com o kitesurf formam uma inspiração para quem procura privacidade e contato com o destino.',
 'reveillon-2027-nannai-milagres-pacote-valores':'A Costa dos Corais é o cenário desta proposta de fim de ano no NANNAI Milagres. A publicação reúne o período da hospedagem, as opções de acomodação e as condições que precisam ser reconfirmadas antes da reserva.',
 'viagem-maldivas-guia-resorts-melhor-epoca':'Nas Maldivas, o resort influencia toda a jornada. A escolha da ilha conecta hospedagem, tipo de villa, refeições e traslado. A curadoria começa por entender o que você deseja viver e quanto tempo quer dedicar a cada etapa.',
 'anantara-palazzo-naiadi-rome-hotel':'Diante da Piazza della Repubblica, o Palazzo Naiadi oferece uma inspiração de hospitalidade no centro de Roma. O artigo da Retrato percorre o encontro entre patrimônio, hospedagem e experiências na cidade.',
 'melhores-restaurantes-bares-rio-de-janeiro-2026-teste-pt':'Uma viagem pelo Rio também pode ser construída à mesa. A seleção da Retrato conecta gastronomia e coquetelaria à descoberta da cidade, reunindo endereços para considerar conforme a ocasião e o seu perfil.',
 'retrato-chip-esim-internacional':'Conexão no exterior começa com escolhas feitas antes do embarque. O conteúdo da Retrato apresenta o eSIM e os pontos que merecem confirmação: cobertura, compatibilidade do aparelho, franquia e condições de uso.',
 'seguro-viagem-retrato-universal-assistance':'A proteção faz parte do desenho da viagem. A Retrato apresenta sua solução com a Universal Assistance e explica como perfil, destino e atividades ajudam a escolher entre diferentes produtos e níveis de assistência.'
}
topic_intro={
 'hoteis-residencias':'A hospedagem muda a maneira de viver um lugar. Localização, privacidade e o estilo de serviço ajudam a escolher um hotel que converse com o seu ritmo.',
 'design-hospitalidade':'Arquitetura, ambiente e hospitalidade contam uma parte da história de um destino. A leitura desses detalhes ajuda a escolher onde permanecer e como viver o lugar.',
 'curadoria-retrato':'Uma boa inspiração ganha sentido quando encontra o seu momento. Antes de transformar uma descoberta em roteiro, vale pensar em interesses, ritmo e no tempo disponível.',
 'aviação':'Uma viagem fluida começa também na logística. Rotas, conexões e condições de cada serviço precisam ser verificadas de acordo com a data e com o bilhete escolhido.'
}
checkpoints={
 'hoteis-residencias':[('Localização','Pense na relação entre o hotel, o destino e os deslocamentos que deseja fazer.'),('Seu ritmo','Considere se a proposta combina com descanso, celebração ou descoberta.'),('Condições','Confirme datas, categorias e o que está incluído na consulta à agência.')],
 'design-hospitalidade':[('O lugar','Observe como arquitetura e ambiente se conectam ao destino.'),('A experiência','Considere o que você procura na hospedagem e no tempo passado ali.'),('A escolha','Alinhe estilo, localização e disponibilidade antes de definir a viagem.')],
 'curadoria-retrato':[('Sua intenção','Escolha as experiências que têm relação com o seu momento.'),('Tempo de viagem','Equilibre deslocamentos, visitas e espaço para descobertas.'),('O próximo passo','Leve a inspiração para a conversa e construa um roteiro personalizado.')],
 'aviação':[('Data e rota','Verifique a informação válida para o seu itinerário.'),('Regras do serviço','Condições dependem do bilhete, do fornecedor e do momento da contratação.'),('Planejamento','Antecipar essas escolhas ajuda a reduzir atrito nos deslocamentos.')]
}
for index,post in enumerate(posts):
    slug=unquote(post['path']).strip('/').rsplit('/',1)[-1]
    summary=editorial_summaries.get(slug,topic_intro[post['category']])
    content=f'<section class="article-hero section-wrap"><nav class="breadcrumbs" aria-label="Você está aqui"><a href="/">Início</a><span>/</span><a href="/retrato-news/">Journal</a><span>/</span><a href="/retrato-news/categories/{quote(post["category"])}/">{h(post["category_label"])}</a></nav><p class="eyebrow">{h(post["category_label"].upper())}</p><h1>{h(post["title"])}</h1><p class="article-byline">CURADORIA RETRATO · <time datetime="{post["date"]}">{post["display_date"]}</time></p><div class="article-cover"><img src="{h(post["image"])}" alt="{h(post["alt"])}" fetchpriority="high"></div></section>'
    content+=f'<section class="article-layout section-wrap"><article class="article-body"><p class="article-lead">{summary}</p><h2>Da leitura à sua viagem</h2><p>Uma referência é um ponto de partida. O desenho da viagem considera suas preferências, o período escolhido e as condições disponíveis no momento do planejamento.</p>'+feature_rows(checkpoints[post['category']])+f'<div class="original-reading"><p class="eyebrow">UM NOVO OLHAR</p><h3>Sua próxima descoberta</h3><p>Explore outras inspirações de hotelaria, destinos e experiências para dar forma à sua viagem.</p><a class="text-link" href="/retrato-news/">Continue explorando o Journal <span>↗</span></a></div></article><aside class="article-planning"><p class="eyebrow">DO JOURNAL AO EMBARQUE</p><h3>Essa inspiração<br>combina com você?</h3><p>Converse sobre como incluir essa descoberta no seu próximo roteiro.</p>{cta("Planeje com a Retrato")}<a href="/roteiros/" class="text-link">Explore outros destinos <span>↗</span></a></aside></section>'
    related=[p for p in posts if p['category']==post['category'] and p['path']!=post['path']][:3]
    content+='<section class="related-articles section-wrap"><p class="eyebrow">CONTINUE DESCOBRINDO</p><h2>O próximo <em>olhar.</em></h2><div class="archive-grid">'+''.join(article_card(p) for p in related)+'</div></section>'
    create(unquote(post['path']).strip('/'),post['title'],content,summary,extra='article-page')

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
    content+=f'<nav class="destination-subnav" aria-label="Explore esta viagem"><a href="#descubra">O destino</a><a href="#momentos">Experiências</a><a href="#curadoria">Curadoria</a><button type="button" data-plan-destination="{h(d["choice"])}">Desenhe sua viagem ↗</button></nav>'
    content+=f'<section id="descubra" class="destination-editorial section-wrap"><div><p class="eyebrow">{h(d["name"].upper())} · UM NOVO OLHAR</p><h2>{d["editorial_title"]}</h2></div><div><p class="destination-lead">{d["editorial"]}</p><p>Uma viagem sob medida encontra o equilíbrio entre o que você quer viver e as escolhas que tornam isso possível.</p></div></section>'
    content+='<section class="destination-highlights section-wrap" id="momentos"><p class="eyebrow">POSSIBILIDADES PARA SUA VIAGEM</p><div>'+''.join(f'<article><span>{i:02} /</span><h3>{title}</h3><p>{desc}</p></article>' for i,(title,desc) in enumerate(d['highlights'],1))+'</div></section>'
    content+=f'<section class="destination-stay section-wrap" id="curadoria"><div class="destination-stay-image"><img src="/assets/{d["stay_image"]}" alt="{h(d["stay_alt"])}" loading="lazy"></div><div><p class="eyebrow">UM ENDEREÇO. UMA INSPIRAÇÃO.</p><h2>{h(d["stay"])}</h2><p>{d["stay_copy"]}</p><a class="text-link" href="/retratonews/{quote(d["article"])}/">Explore a leitura do Journal <span>↗</span></a>{cta("Converse sobre esta viagem",d["choice"])}</div></section>'
    content+=faq([('Essa viagem tem um roteiro fechado?','O destino é uma inspiração. O roteiro é construído conforme suas preferências, período e perfil dos viajantes.'),('Como consulto os valores?','Comece o planejamento com seu destino e período. A Retrato consulta os serviços e apresenta as condições para a sua viagem.'),('Posso combinar este destino com outros lugares?','Leve essa ideia para o atendimento. A combinação precisa considerar deslocamentos e o tempo disponível.')])
    content+=end_cta('A viagem é sobre<br>o que faz sentido <em>para você.</em>')
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
