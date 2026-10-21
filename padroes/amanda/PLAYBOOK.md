# Playbook de edição — Amanda Lourenço / LOULOU Studios

**Status:** **v1.0 — oficial (2026-10-12)**, validado no TASTE WASHING 5. Criado a partir de `marcas/amanda/meus-editados/` (claude-chatgpt, kendall-fanatics) + referências em `referencias/`. Valores lidos pelo motor: `padrao.json` (este arquivo explica as regras e o porquê). Histórico: `CHANGELOG.md`. Termos: `marcas/amanda/glossario.md`. Valores marcados com (E) foram estimados visualmente.

Tela: 1080×1920, 30 fps. Coordenadas em % da altura/largura da tela.

## 0. Regra de ouro: nada cobre o rosto

**Título do gancho, cards, notícias, legendas e palavras-chave NUNCA podem ficar em cima do rosto da Amanda**, em nenhum enquadramento (decisão da Amanda).

| Regra | Valor |
|---|---|
| Como | o rosto é mapeado ao longo do vídeo inteiro (`motor/rosto.py`: pele dentro da máscara do recorte, 4×/s). Cada elemento é posicionado pelo pior caso do rosto durante o tempo em que fica na tela, já contando o zoom dos jump cuts e o deslocamento do fundo mesclado |
| Onde vai | abaixo do queixo, com folga de 2% da altura. As posições padrão (legenda a 54%, título a 40% etc.) valem só quando o rosto está acima delas |
| Se não couber embaixo | o card encolhe (mínimo 16% da altura); se ainda assim não couber, o elemento vai pra cima do rosto, abaixo do logo |
| Limites da tela | entre 8% (abaixo do logo) e 86% (acima da interface do Reels/TikTok) |
| Exceções intencionais | o **texto atrás da pessoa** e a **imagem do fundo mesclado**, que ficam atrás dela por definição |
| Conferência | antes de mostrar o preview, tirar snapshots dos momentos com título, cards e palavras-chave e checar o rosto |

## 1. Identidade fixa (todo vídeo)

| Elemento | Regra |
|---|---|
| Fonte | Helvetica Now Display ExtraBold (`padroes/amanda/fontes/HelveticaNowDisplay-ExtraBold.ttf`) |
| Logo | "LOULOU STUDIOS" no canto superior direito, ~19% da largura, a ~5% do topo, o vídeo inteiro, acima de qualquer camada. Versão escura (70% de opacidade) sobre fundo claro; troca automaticamente pra versão clara quando o topo mesclado tem imagem escura naquele canto |
| Título de abertura | 3 linhas em maiúsculas + subtítulo menor entre parênteses, nos primeiros ~5 s, na altura da legenda |
| Enquadramento | plano aberto, sentada; jump cuts alternando plano aberto e mais fechado |

### 1.1 Cor e iluminação (color grading)

**Padrão:** o bruto recebe a mesma coloração e iluminação dos vídeos editados da marca (`marcas/<marca>/meus-editados/`): temperatura, tom de pele, cor da parede, contraste e brilho.

**Confirmação obrigatória em cada vídeo** (no plano, antes de editar), com uma comparação lado a lado (bruto | com o grading | referência):
1. **Estilo dos meus-editados** (padrão);
2. **Estilo de outra referência**: a Amanda diz qual vídeo, e o grading é extraído dele;
3. **Manter o original** do bruto.

| Regra | Valor |
|---|---|
| Como extrair | medir só os quadros da Amanda falando nos vídeos de referência (sem b-roll, cards ou telas cheias), comparando a cor em espaço Lab (luminosidade + dois eixos de cor), e gerar uma LUT de cor (`.cube`) que leva o bruto até esses valores |
| Onde aplicar | no A-roll, **antes do recorte** (pra Amanda recortada e o fundo ficarem com a mesma cor). Nunca nas imagens/vídeos inseridos, que mantêm as cores originais |
| Intensidade | ajustável de 0% a 100%; padrão 100%, reduzir se a pele ficar artificial |
| Limites | corrige cor, brilho e contraste. **Não muda a direção nem o tipo da luz** (uma sombra forte de um lado continua lá). Se a gravação for muito diferente da referência (outra luz, outro lugar), avisar no plano |
| Arquivo | a LUT fica na marca, em `marcas/<marca>/cor/` (ex.: `meus-editados.cube`) e é reaproveitada nos próximos vídeos |

## 2. Ritmo e cortes

| Regra | Valor |
|---|---|
| Pausas entre palavras | cortar tudo acima de ~0,3 s; deixar no máximo 3–6 pausas por vídeo, só as intencionais (antes de frase de impacto) |
| Aceleração do bruto | de **1,10× a 1,15×**, conforme a velocidade da fala no bruto (como a Amanda faz no CapCut). Escolha: medir as palavras/s do bruto já sem as pausas e usar o fator, dentro dessa faixa, que mais aproxima o resultado de ~3,7 palavras/s. Fala lenta → 1,15×; fala já rápida → 1,10×. O fator escolhido vai no plano, pra aprovação |
| Como acelerar | a voz mantém o tom (sem efeito de "voz fina"). A aceleração vale só pra gravação da Amanda; b-roll, cards e trechos de outros vídeos ficam na velocidade original |
| Ordem | 1) cortar as pausas, 2) acelerar, 3) cronometrar legendas, palavras-chave e inserções na linha do tempo já acelerada |
| Velocidade resultante | ~3,7 palavras/s (medida nos vídeos editados, já com a aceleração) |
| Margem do corte | não cortar no meio de sílaba; usar os tempos por palavra da transcrição |
| J-cut | a definir no primeiro teste |

## 3. Legendas

| Regra | Valor |
|---|---|
| Estilo | branca, MAIÚSCULAS, Helvetica Now Display ExtraBold |
| Tamanho | ~40 px (E) |
| Palavras por tela | 2 a 5 |
| Posição | centralizada, ~54% da altura; sobe pra ~44% quando há um card abaixo |
| Destaque | palavra única maior (~2×), branca (ex.: "KARDASHIAN") |
| Grafia | sempre pelo glossário da marca (`marcas/<marca>/glossario.md`) |

### 3.1 Palavras-chave em destaque (opcional — só quando a Amanda pedir)

**Não é padrão.** Só entra quando a Amanda pedir no pedido ou aprovar no plano. No plano, listar cada destaque com o tempo e o texto.

**Lógica** (medida nas referências do Kaio, `ref1-kaio` e `ref2-kaio`):

| Regra | Valor medido |
|---|---|
| Frequência | ~10 destaques por minuto (um a cada ~6 s); ~22% do tempo do vídeo tem destaque na tela |
| Duração | de 0,5 a 3,5 s; o normal é de 1 a 1,5 s. O destaque fica na tela enquanto o trecho é falado e sai logo depois |
| Tamanho do trecho | de 1 a 6 palavras; frases longas só quando são a conclusão do vídeo |
| Montagem | palavra por palavra, cada uma entrando no instante em que é falada ("POR" → "POR UM ÚNICO") |
| Legenda normal | some enquanto o destaque está na tela e volta depois |
| Hierarquia | dentro do trecho, a palavra principal (número, nome, conceito) fica bem maior que as palavras de ligação ("NOVEMBRO DE" pequeno, "2020" grande) |
| Posição | ver a tabela de aparência abaixo |

**O que vira destaque** (em ordem de prioridade):
1. Números e dados: "2020", "14 horas", "17 milhões", "4 mil versus 18".
2. A conclusão ou a virada da frase, quase sempre no fim dela: "não conseguem copiar", "pelo amor de Deus", "marca sem convicção não constrói cultura".
3. O conceito central do vídeo: "pertencimento", "fanatismo", "identidade".
4. Um detalhe concreto e surpreendente: "às duas da manhã", "cinzas de um parente".

**Aparência** (definida pela Amanda + medida em `referencias/palavras-chave-1`, `-2`, `-3`). **Nunca usar o vermelho com brilho do Kaio.**

| Elemento | Regra |
|---|---|
| Fonte | a mesma da legenda: Helvetica Now Display ExtraBold |
| Cor | branca, com uma sombra suave só pra garantir a leitura em fundo claro |
| Encaixe no vão | se a palavra grande começa com letras **baixas** (sem haste, acento, pingo ou maiúscula, ex.: "v", "a", "p") e a linha pequena de antes cabe sobre elas, a linha pequena **desce até o topo dessas letras**, encaixada no vão ("um" sobre o "v" de "vilão", colado no pingo do "i"; "na verdade é" sobre "acesso."). Se a palavra grande começa com letra alta, número ou maiúscula ("lá", "1979", "CAPITAL"), a linha pequena fica acima da letra mais alta |
| Âncora das palavras pequenas | ancoradas na **palavra grande**, nunca na largura do bloco. As de antes ficam encaixadas no canto superior esquerdo da primeira linha grande ("um / **vilão**", "Do it / **yourself**"). As de depois ficam alinhadas à direita da última linha grande; se forem **mais largas** que ela, começam no pé esquerdo da palavra grande e crescem pra direita, na ordem da leitura ("**vilão** / escondido na nossa rotina."). A largura do bloco é sempre a da palavra grande |
| Composição | um bloco tipográfico: **uma palavra principal enorme** e as palavras de ligação pequenas, encaixadas em volta dela (acima à esquerda, abaixo à direita, nos vãos das letras). Ex.: "doesn't make you / **weak.**", "everyone has / **days** / they'd rather forget." |
| Tamanho da palavra principal | de 50% a 72% da largura da tela; altura das letras de 6% a 11% da altura da tela (fonte de ~150 a ~280 px em 1080×1920) (E) |
| Tamanho das palavras de ligação | o mesmo da legenda normal (~40 px) (E); proporção de 1:3 a 1:5 em relação à palavra principal |
| Espaçamento | letras bem juntas (espaçamento negativo, ~−3% a −4%). Entre as linhas, a distância é medida pelo **contorno real das letras**, não pela caixa da fonte: folga de só ~4% do tamanho da palavra principal entre o pé das palavras pequenas e o topo das letras grandes (e vice-versa). Nunca usar a entrelinha padrão da fonte, que deixa um vão grande demais |
| Maiúsculas e minúsculas | os dois, conforme o caso (decisão da Amanda). Minúsculas ("weak.", "make money.") pra frases e falas; MAIÚSCULAS ("LIFE SAVINGS", "VIRAL") pra números, nomes e termos de impacto. O Claude sugere em cada destaque, no plano |
| Pontuação | o ponto final aparece quando fecha a frase ("weak.", "money.") |
| Entrada | cada palavra entra no instante em que é falada, já na posição final, saindo de desfocada e transparente pra nítida em ~0,2–0,3 s |
| Saída | o bloco inteiro desfoca e some quando o trecho termina |
| Posição | centralizado na horizontal, entre ~45% e ~70% da altura (peito), sem cobrir boca nem olhos. Quando o centro estiver ocupado, vai pro espaço vazio ao lado da cabeça |

#### Variação opcional: efeito negativo

Escolhida **por palavra-chave** (no pedido ou no plano), nunca aplicada por padrão.

| Regra | Valor |
|---|---|
| O que é | as letras não têm cor própria: **invertem as cores do vídeo atrás delas** (fundo claro → letra escura; roupa escura → letra clara). A mesma palavra muda de cor quando passa de um fundo pro outro |
| Como | mesma fonte, tamanho, composição e animação das palavras-chave normais; sem sombra (a sombra atrapalharia a inversão). No `edicao.json`: `"efeito": "negativo"` na palavra-chave |
| Cor resultante | é o oposto do que está atrás: sobre bege/creme a letra fica azulada; sobre cinza médio o contraste cai. Funciona melhor sobre áreas bem claras ou bem escuras |
| Conferir | no snapshot, se a palavra ficou legível; se cair sobre cinza médio, sugerir a versão branca normal |

### 3.2 Texto atrás da pessoa (opcional — só quando a Amanda pedir)

**Não é padrão.** Só entra quando a Amanda pedir no pedido ou aprovar no plano. Usa a mesma técnica de recorte do topo mesclado (4.5). Referência: `palavras-chave-3`, de 0:09 a 0:11 ("WE SPENT NINE MONTHS", "FULL REBRAND").

| Regra | Valor |
|---|---|
| O que é | um bloco de palavra-chave enorme no fundo, acima dos ombros, com a cabeça e o cabelo da Amanda **na frente** das letras |
| Camadas | vídeo original → texto → Amanda recortada → legendas e logo |
| Fonte e cor | as mesmas das palavras-chave (3.1): Helvetica Now Display ExtraBold, branca. A referência usa uma fonte condensada vermelha, que **não** será copiada |
| Tamanho | ~80% da largura **já descontando o zoom do trecho** (se houver zoom de jump cut ativo, o texto é reduzido na mesma proporção, pra nunca cortar nas bordas); 1 a 2 linhas grandes |
| Posição | faixa de ~11% a ~34% da altura; a cabeça cobre de ~30% a ~40% da altura das letras, mas as palavras continuam legíveis (E) |
| Entrada | sobe de baixo pra cima, saindo do desfocado pro nítido, palavra por palavra no tempo da fala |
| Quando usar (sugestão) | poucas vezes por vídeo (1 a 3), nos momentos mais fortes: gancho, tese central, virada |

**A testar no primeiro vídeo:**
- **Contraste:** texto branco sobre a parede clara da Amanda tende a sumir. Testar sombra suave ou um leve escurecimento só atrás do texto.
- **Espaço acima da cabeça:** no plano aberto, a cabeça começa a ~12% da altura, então sobra pouco espaço. Pode ser preciso descer o texto (mais atrás da cabeça) ou usar o recurso só nos planos mais abertos.
- **Logo LOULOU:** fica no canto superior direito (~6–9% da altura). O texto não pode passar por baixo dele.

## 4. Tipos de inserção

Cada imagem ou vídeo inserido usa **um** destes tipos. O tipo é escolhido por inserção, no pedido ou no plano. Se o pedido não disser o tipo, o Claude sugere um no plano e espera a aprovação.

### 4.0 Confirmação obrigatória das inserções (no plano)

Nenhuma inserção é montada sem a Amanda aprovar, no plano, uma tabela com **cada** inserção:

| Coluna | O que informar |
|---|---|
| Fala | o trecho exato da fala em que a inserção aparece (da primeira à última palavra) |
| Entra / sai | os tempos no vídeo final |
| Duração | quanto tempo fica na tela |
| Arquivo | qual imagem/vídeo (e, se for vídeo, qual trecho dele) |
| Tipo e posição | card na base, card no topo, notícia, tela cheia, horizontal com faixas pretas ou topo mesclado |

**Gancho (primeiros ~5 s):** decisão separada, sempre perguntada à Amanda. Quantas inserções (nenhuma, 1 ou mais), qual o tipo e a posição de cada uma (tela cheia, topo mesclado, card no topo ou card na base), e quanto tempo cada uma fica.

### 4.1 Card arredondado (padrão)

- Sobreposto ao vídeo, na primeira camada.
- ~86% da largura, bordas arredondadas (~26 px).
- **Posição: na base (padrão) ou no topo**, escolhida por inserção.
  - Base: começa a ~54% da altura; a legenda sobe pra ~49%.
  - Topo: começa a ~8% da altura (abaixo do logo); a legenda fica na posição normal. Conferir se o card não cobre o rosto no enquadramento do vídeo.
- Usar para: imagens, trechos de vídeo, anúncios.

### 4.2 Card de notícia / print

- Card branco (ou escuro, quando o print é escuro), bordas arredondadas, ~75% da largura, metade de baixo da tela.
- Usar para: manchetes, prints de site e posts.
- **Vale em qualquer vídeo**, inclusive nos trechos com topo mesclado.

### 4.3 Tela cheia

- O b-roll ocupa a tela inteira; a legenda continua na posição normal.
- Usar para: pessoas citadas, cenas de anúncio, momentos de impacto.

### 4.4 Horizontal com faixas pretas

- Vídeo 16:9 centralizado, com faixas pretas em cima e embaixo; legenda logo acima do vídeo.
- Usar para: material horizontal (anúncios, trechos de filme ou entrevista) que perderia conteúdo se fosse cortado pra vertical.

### Encerramento com vídeo (opcional)

O vídeo pode ou não terminar com um clipe. Quando terminar, o clipe usa **tela cheia** (4.3) ou **horizontal com faixas pretas** (4.4), escolhido por vídeo.

### 4.5 Topo mesclado (opcional — só quando a Amanda pedir)

**Não é padrão.** Só é aplicado quando a Amanda pedir no pedido ou aprovar no plano. O Claude pode sugerir, sempre marcado como sugestão.

- **Divisão da tela: imagem em 60% em cima, no máximo 40% embaixo** (decisão da Amanda; a imagem pode ocupar mais, nunca menos). Padrão: imagem sólida até 56% e degradê de 56% a 64% (meio do degradê em 60%), mesclando com o fundo real do vídeo.
- **O vídeo da Amanda desce** pra liberar o topo: o topo da cabeça vai pra ~46% da altura e a parte de baixo (pernas) sai do quadro. O deslocamento é **calculado em cada vídeo**, medindo o topo da cabeça na máscara do recorte, então funciona em qualquer enquadramento (plano aberto desce mais; plano fechado desce pouco ou nada; máximo de 30% da altura). Não há zoom, então não perde qualidade.
- **Corte seco** na entrada e na saída: o vídeo "pula" pra baixo no mesmo quadro em que a imagem aparece (decisão da Amanda).
- A Amanda fica **na frente** da imagem (cabeça e cabelo recortados).
- Nesses trechos, legendas descem pra ~71% da altura e palavras-chave pra ~64%, abaixo do rosto.
- Camadas, de baixo pra cima: vídeo da Amanda (deslocado) → imagem do topo com degradê → Amanda recortada → legendas, cards e logo. As três primeiras são embutidas num vídeo único (`compor_camadas.py`), pra existir uma cópia só da Amanda.
- Pode durar um trecho (uma imagem) ou um bloco (várias imagens trocando a cada 1–4 s, acompanhando o assunto).
- Referência: `padroes/amanda/referencias/ref1-kaio`, `ref2-kaio`.
- A decidir no primeiro teste: degradê direto na parede clara ou escurecendo levemente o topo.

## 5. Pesquisa de imagens e notícias (opcional — só quando a Amanda pedir)

Só acontece quando a Amanda pedir (ex.: *"busca imagens e notícias"*). Complementa as inserções que ela mesma coloca; não substitui. Acontece depois da transcrição e antes do plano.

### 5.1 Definição das queries (aprovação obrigatória antes de buscar)

O Claude propõe uma lista de queries e **só busca depois que a Amanda aprovar**. Regras:

| Regra | Valor |
|---|---|
| Quantidade | de 4 a 8 queries por vídeo; uma por momento que pede imagem, nunca uma por frase |
| Tamanho | de 2 a 5 palavras |
| Conteúdo | entidade concreta + contexto que a diferencia (pessoa, marca, lugar, evento, objeto). Ex.: "Anthropic pop-up café West Village", "Pierre Bourdieu 1998", "Greg Brockman taste tweet" |
| Evitar | conceitos abstratos ("bom gosto", "capital cultural"), frases do roteiro, termos genéricos ("tecnologia", "pessoas felizes"), queries que juntam dois assuntos |
| Idioma | o idioma em que o assunto aparece mais nas fontes (assunto americano → inglês; brasileiro → português) |
| Tipo | cada query é marcada como **imagem** ou **notícia**. Notícia só pra fato datado (lançamento, número, declaração, evento) |
| Ângulo | preferir o que é interessante e específico do roteiro (o objeto, o lugar, o momento citado) ao retrato genérico |

Formato da proposta: `momento (tempo) | trecho falado | query | tipo | por quê`.

### 5.2 Busca e escolha

- **Imagens:** o Claude busca, abre a fonte original quando possível e monta uma galeria numerada com 3 a 5 opções por query. Preferência: resolução ≥ 1080 px no lado menor, sem marca d'água, fontes mais seguras (Wikimedia, kit de imprensa, perfis oficiais) quando existirem.
- **Notícias:** lista com título, veículo, data e link (2 a 3 por query), priorizando veículos conhecidos e as mais recentes.
- A Amanda escolhe ("momento 2: foto 3; notícia B"). A escolha vale como autorização de download só dos itens escolhidos, e o Claude informa a origem de cada arquivo.
- **Print da manchete:** recusar os cookies não essenciais e capturar só a área do título. Se banner, paywall ou anúncio cobrir a manchete, propor recriar o card da notícia no estilo 4.2 (manchete, veículo e data, com a fonte citada).
- Os arquivos baixados vão pra `projetos/<slug>/insercoes/` com nome descritivo (ex.: `bourdieu-1998.jpg`, `noticia-newyorker-techbros.png`) e entram no plano como as outras inserções.

### 5.3 Quando não der certo

Se a busca, o download ou o print falhar por qualquer motivo (nenhum resultado bom, resolução baixa, site bloqueado, paywall, download recusado), o Claude **não trava o plano**:
1. Diz exatamente qual item falhou e por quê.
2. Pede pra Amanda colocar o arquivo em **`projetos/<slug>/insercoes/`**, sugerindo o nome do arquivo e o que procurar (a query e, se tiver, o link encontrado).
3. Segue com o resto do plano e marca o item como "aguardando arquivo".

## 6. Música, efeitos sonoros e transições

| Regra | Valor |
|---|---|
| De onde vêm | biblioteca da Amanda no Drive: `_audio/musicas/`, `_audio/efeitos/`, `_transicoes/` (transições em vídeo, como overlay). Compartilhada com todos os padrões |
| Quando entram | **só com aprovação no plano**: o Claude sugere arquivo, momento e volume; nada é aplicado sem o OK |
| Como (a definir no primeiro vídeo com áudio) | música baixa e abaixando sob a voz, entrada/saída suaves; efeitos em eventos (entrada de card, palavra-chave); transição sobreposta nos cortes. Valores (volume, duração) entram aqui e no `padrao.json` depois de aprovados |
| Status | motor ainda não mixa áudio nem aplica transições (pendente) |

## 7. Decisões pendentes

- [ ] Texto atrás da pessoa (3.2): contraste na parede clara, espaço acima da cabeça e convivência com o logo — testar no primeiro vídeo
- [ ] Tipo de degradê do topo mesclado (ver 4.5)
- [ ] Regras de J-cut
- [ ] Motor do preview: HyperFrames ou Remotion (tendência: HyperFrames)
- [ ] Música, efeitos e transições (§6): volumes, onde entram e quais tipos de transição
