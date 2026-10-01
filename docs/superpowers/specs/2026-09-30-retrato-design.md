# Agência Retrato — experiência completa

Site privado em português brasileiro, com composição editorial inspirada na FTLO e identidade da Retrato: fotografia em destaque, serifas, tons areia, espaços generosos e navegação clara. Conteúdo fundamentado em páginas oficiais e material fornecido pelo usuário; sem números, depoimentos, tarifas, prazos de atendimento ou garantias inventados.

## Conteúdo e navegação

Todas as rotas institucionais originais são locais, com Sobre, Boutique, Roteiros, Chip, Seguro, Área do cliente, Contato, Perguntas frequentes, documentos, quatro categorias de Journal e cinco destinos. Os 119 artigos possuem leitura editorial própria e ampliada, com cinco assuntos em média, índice navegável, tempo de leitura, fontes e avisos de contexto para eventos e ofertas antigos. Não são cópias integrais das publicações. Nenhum botão ou link leva ao site antigo agenciaretrato.com. WhatsApp, Instagram, Google e o portal externo de clientes são integrações independentes e oficiais. Destinos e Sua viagem usam o mesmo controlador de navegação com descrições, abertura por mouse, teclado ou toque e fechamento com Escape. Destinos combina fotografia dos Lençóis Maranhenses, agrupamento Brasil/mundo e links locais; Sua viagem organiza Chip, Seguro, Área do cliente e Contato. As opções do formulário compartilhado foram corrigidas: sete escolhas de destino e cinco perfis de companhia.

## Escolhas e contato

O planejamento organiza intenção, destino, período, companhia e observações em três etapas. O usuário revisa o resumo e escolhe enviar pelo WhatsApp, sem envio automático ou gravação de preferências. A página Contato apresenta uma ação principal e canais de contato claros. Botões de contato repetidos, banners genéricos em páginas de serviço e o contato flutuante foram removidos. Documentos legais não têm CTA de venda. O rodapé usa links simples, sem setas diagonais; navegação e ações contextuais permanecem.

## Dados verificados

13 avaliações do Google foram fornecidas por capturas do usuário. O texto é preservado em sources/google-reviews.json, inclusive indicação de trecho para a captura incompleta de Flavia. Os cards usam fotos de perfil e de viagens disponíveis nos próprios PNGs através de recortes CSS; iniciais para os perfis sem foto. Os cards são compactos: quatro por faixa no desktop, três em telas médias e um em destaque no celular, com quatro linhas de prévia, fotos menores e leitura completa no diálogo. Há carrossel manual, foco, fechamento e restauração. Não há nota média ou contagem global inventada: “13 relatos selecionados” descreve apenas a seleção.

Retrato Chip contém 9 planos oficiais em reais, consultados em 30/09/2026: Estados Unidos R$109/179/249, Europa R$149/229/399, Mundo R$449/749/1099, para 10/20/50 GB e validade de 30 dias. Abas permitem comparar a região e o WhatsApp leva a escolha preenchida. Compatibilidade, países cobertos e ativação precisam de confirmação antes da compra.

Seguro usa uma fotografia real de viajante no aeroporto, de Gustavo Fring/Pexels, em 3840 × 2160 pixels no hero. Texto vivo sobre gradiente mantém a leitura; a foto se adapta ao celular. A imagem original de baixa resolução foi retirada da página. A geração de imagem não entregou 4K e não foi ampliada artificialmente nem usada. A cotação tem uma ação direta e as informações explicam como comparar perfil, serviços e condições sem prometer cobertura universal.

Privacidade, Termos e Cookies reproduzem integralmente os textos institucionais, atualizados pela agência em 23/07/2026. São 17, 27 e 13 assuntos, respectivamente, com índice navegável, legibilidade e impressão. Sources/legal-documents.json preserva os blocos de texto e as listas originais.

## Movimento e verificação

A home agora usa uma fotografia aérea das Maldivas em 3840 × 2160, com movimento sutil do mar e máscara própria que preserva a ilha e as villas. O controlador também mantém a configuração da foto anterior com costa e pedras. WebGL tem alternativa Canvas 2D, pausa, preferência de movimento reduzido, suspensão fora da tela e em página oculta. Oito testes offline verificam o controlador, máscaras das duas cenas, pausa, visibilidade, preferência de movimento e deslocamento suave. Três testes verificam os menus; quatro testes Python conferem os textos completos e índices dos 119 artigos, estrutura das 143 páginas e opções do formulário. Scripts e estilos usam hashes de conteúdo para invalidar cache.

Auditoria estática verifica rotas, recursos, textos alternativos e ausência de links ao domínio antigo. Acesso de navegador ao site hospedado foi negado por preferência salva do usuário; não contornar. Aparência, interações e shaders ainda precisam de inspeção visual autorizada em navegador. Testes offline não substituem essa inspeção.

## Fotografias e abertura da marca — atualização de 01/10/2026

Journal usa Lago de Como ao amanhecer no hero. Sobre, Boutique, Roteiros, Seguro e cinco destinos usam fotografias nativas recortadas para 3840 × 2160, sem aumento artificial. Onze arquivos e suas fontes estão registrados em sources/photography-4k.json. Fotos editoriais originais do acervo e capturas reais de avaliações permanecem na resolução disponível; não são anunciadas como 4K. Uma abertura de aproximadamente 1,3 segundo anima o nome Retrato dentro de uma moldura fotográfica; não bloqueia ações, desaparece ao tocar ou usar o teclado, não reaparece ao voltar pelo histórico e respeita movimento reduzido.

A revisão independente identificou dois problemas importantes: um fragmento sem destino na leitura de seguro e a alternância por toque em dispositivos com mouse. Ambos foram corrigidos com regressões reproduzidas antes da correção. A auditoria agora confere todos os fragmentos locais e IDs de controles; 143 páginas passaram sem problemas. Os onze testes Node e quatro testes Python passaram, assim como a validação de sintaxe de todos os scripts e git diff --check. A aparência em navegador permanece sem inspeção devido à preferência de acesso registrada.

A pedido do usuário, a seção final da home (E se a próxima viagem fosse a sua melhor história?) voltou a usar a fotografia anterior de coqueiros e mar, assets/milagres.jpg, na resolução original de 1280 × 960. O atributo data-preserve-photo mantém essa escolha nas próximas compilações; as outras fotografias não são alteradas.

As páginas de Sua viagem agora mantêm a mesma ação principal e alinhamento do cabeçalho da home. A remoção dessa ação foi restringida aos documentos legais. Teste de regressão confere o botão nas cinco rotas de serviço; alinhamento vertical e não quebra da ação são explícitos no CSS.

Por correção explícita do usuário, os cinco cards de destinos voltaram às fotografias anteriores, sem substituição automática de seleção. O rodapé do hero não exibe botão de movimento nem o link O próximo capítulo começa aqui; o mar continua animado e respeita movimento reduzido sem depender da presença de controle visual.

O hero de Sobre nós usa uma fotografia 4K de fachadas comerciais ao entardecer, sem pessoas, solicitada pelo usuário. A imagem de Dima/Unsplash é ilustrativa e não representa a sede da agência. A troca está restrita a esse hero.

A abertura foi estendida para aproximadamente 2,7 segundos, com avião vetorial dourado discreto passando atrás da marca. Movimento e escala se adaptam ao celular. Toque, teclado, retorno pelo histórico e preferência de movimento reduzido continuam interrompendo ou dispensando a abertura.

O menu Sua viagem agora usa painel fotográfico lateral e conteúdo ao lado, com a mesma linguagem visual e controlador animado de Destinos. A foto mostra uma viajante com mala no aeroporto, relacionando a imagem aos serviços antes, durante e depois do embarque.

O avião da abertura foi refinado: fuselagem com acabamento metálico suave, asas enflechadas, dois motores, cabine e janelas. O voo percorre uma curva ascendente leve, muda discretamente o ângulo e a escala e deixa um rastro difuso, sempre atrás da marca. A duração e a interrupção acessível permanecem.

Por ajuste do usuário, o avião agora faz uma volta elíptica completa em torno da marca, com orientação automática pela tangente e rastro suave. O percurso tem escala própria no celular, alternativa CSS para navegadores sem motion path e mantém dispensa por movimento reduzido, toque ou teclado.

A linha inferior do cabeçalho foi removida quando ele está transparente sobre fotos; o cabeçalho opaco após rolagem mantém sua separação.

O voo agora calcula uma volta completa em torno da marca e continua pela mesma tangente em uma curva de saída para além do canto superior direito da tela. O fim do percurso usa as dimensões reais da janela; não desaparece antecipadamente. A abertura dura aproximadamente 3,45 segundos. Avião metálico refinado, detalhes dourados nas asas e entradas dos motores, com rastro leve crescente na saída.
