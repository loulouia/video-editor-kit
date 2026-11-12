# Playbook de edição — Padrão Básico

**Status:** v1.2 (2026-11-12): legenda em Instrument Serif Italic no estilo da referência da Amanda (blocos de até 3 linhas quase encostadas, palavra por palavra saindo do desfocado, destaques de 1–2 palavras), sem aceleração por padrão, glow opcional. v1.0 (2026-10-24). Criado a partir de vídeo de referência (Mariana & Adel Bark — conteúdo hospitalar/cirúrgico). Valores lidos pelo motor: `padrao.json`. Histórico: `CHANGELOG.md`.

Tela: 1080×1920, 30 fps. Coordenadas em % da altura/largura da tela.

## 0. Regra de ouro: nada cobre o rosto

Legendas, título e qualquer elemento de texto **nunca ficam em cima do rosto** da pessoa que fala.

| Regra | Valor |
|---|---|
| Como | rosto mapeado ao longo do vídeo (`motor/rosto.py`, a partir do **recorte completo** da pessoa; o modo rápido só serve pro storyboard e erra em selfie de perto). Mede o rosto inteiro até o queixo, também em selfie de perto, sem se confundir com a mão encostada no rosto. Cada elemento fica abaixo do queixo, com folga de 2% da altura |
| Posição padrão da legenda | ~65% da altura — só vale quando o rosto está acima dessa linha |
| Se não couber embaixo | a legenda é dividida em menos linhas (§0.1); o card vira tela cheia. O rosto nunca é coberto |
| Limites da tela | a área segura do Instagram (§0.1): entre 13% e 78% da altura; texto entre 11% e 89% da largura; cards entre 4% e 89% |

## 0.1 Área segura do Instagram (margens)

Legendas, título, cards e logo **nunca** passam da área segura de um post do Instagram (Reels orgânico), pra não ficarem escondidos atrás do nome do perfil, da legenda do post ou dos botões. Decisão da Amanda (2026-11-12).

| Margem | Valor (1080×1920) | O que cobre |
|---|---|---|
| Em cima | **13%** (~250 px) | nome do perfil, "Seguir" |
| Embaixo | **22%** (~420 px) | legenda do post, áudio |
| Esquerda | **4%** (~43 px) | borda |
| Direita | **11%** (~120 px) | botões de curtir, comentar, compartilhar |

| Regra | Valor |
|---|---|
| Legendas | o bloco fica dentro da área. **Texto com a mesma margem dos dois lados (11%)**, centralizado pelo desenho real das letras (o itálico pende pra direita), pra não ficar colado na borda esquerda. Linha larga demais: **primeiro o destaque daquela linha diminui** (até 1,4×); se não bastar, **a linha quebra em duas** |
| Sem espaço entre o queixo e a margem de baixo | o rosto não cede e a margem também não: o bloco é **dividido em menos linhas** (2, depois 1), cada pedaço no tempo da sua fala, com o mesmo tamanho de letra (decisão da Amanda). Só se nem 1 linha couber, a letra encolhe (até 70%) e o motor avisa |
| Cards (imagem/vídeo em quadro) | dentro da área; se não couber entre o rosto e a margem de baixo, **vira tela cheia** automaticamente. Mídia vertical (9:16) ocupa a tela inteira; as outras (capa de livro, print, foto) ficam **no alto da área segura, inteiras, sobre fundo preto**, e a legenda vai **embaixo**, nunca por cima do texto da imagem |
| Mídia em tela cheia | **permitida** (é fundo); só o texto por cima respeita a área |
| Logo (se a marca usar) | canto superior direito, a 14% do topo e 12% da direita (fora do nome do perfil e da faixa dos botões) |
| Gravação | selfie muito de perto deixa pouco espaço abaixo do queixo (no IMG_4802 o queixo chega a ~60% da altura): os blocos ficam mais curtos. Orientação pra quem grava: câmera um pouco mais longe, rosto na metade de cima da tela |
| Fonte das medidas | a Meta não publica margens oficiais pra post orgânico; valores de guias de criadores. Pra **anúncio**, o guia da Meta pede 14% / 35% / 6% (mais rígido) |

## 1. Identidade visual

| Elemento | Regra |
|---|---|
| Fonte das legendas | **Instrument Serif Italic** (`fontes/InstrumentSerif-Italic.ttf`), livre (SIL OFL, `fontes/OFL-InstrumentSerif.txt`) |
| Fonte de apoio | Instrument Serif Regular (`fontes/InstrumentSerif-Regular.ttf`), pra cards e títulos quando necessário |
| Cor do texto | Branco (#FFFFFF) |
| Glow (opcional) | brilho branco leve em volta das letras da legenda. **Desligado por padrão**; o Claude oferece no início da edição e grava a escolha em `projeto.json` → `"glow": true`. Fica junto com a sombra suave (a sombra garante a leitura em fundo claro) |
| Logo | **Opcional** — não tem logo fixo por padrão. Se a marca do cliente tiver logo, canto superior direito dentro da área segura (14% do topo, 12% da direita), ~13% da largura |
| Título de abertura | **Opcional** — se usado, serif italic, centralizado a ~35% da altura, com sombra suave |

### 1.1 Cor e iluminação

Sem grading por padrão. O vídeo mantém as cores originais da gravação, a menos que a marca do cliente tenha LUT definida (`marcas/<marca>/cor/*.cube`).

Se o cliente tiver LUT:
1. Aplicar no A-roll, **antes do recorte**
2. Inserções mantêm cores originais
3. Mostrar comparação lado a lado antes de aplicar

## 2. Ritmo e cortes

| Regra | Valor |
|---|---|
| Corte de pausas e respiros | **todo trecho sem voz com 0,2 s ou mais** (silêncio, respiro, ruído) é cortado, ficando ~0,16 s entre as falas (pedido da Amanda, 2026-11-12). O detector (`motor/voz.py`) decide pelo **tom** (vibração das cordas vocais), não pelo volume: com o celular perto da boca, o respiro é tão alto quanto a fala. Fala = som com tom + 0,06 s antes e 0,10 s depois pras consoantes sem tom ("s", "f", "ch") |
| Pausas intencionais | só quando pedidas/aprovadas: o trecho vai em `projeto.json` → `cortes_config.manter` |
| Conferência | depois do corte, o vídeo cortado é transcrito de novo e comparado palavra por palavra com o original: nenhuma palavra pode sumir |
| Aceleração | **Nenhuma por padrão (1,0×).** Opcional: o Claude oferece no início da edição; se o usuário quiser, de **1,05× a 1,15×**, mirando ~3,5 palavras/s. No modo direto ao resultado, não acelera |
| Como cortar | `motor/cortar_pausas.py` (detector de fala pelo tom), **não** pelos tempos da transcrição (o Whisper erra até ~1 s). A folga das consoantes protege o começo e o fim das palavras |
| Ordem | 1) transcrever o bruto, 2) cortar pausas e respiros (`cortar_pausas.py`), 3) acelerar (só se o usuário pediu), 4) gerar o A-roll (`cortes.py`), 5) **conferir** retranscrevendo, 6) transcrever o A-roll e **sincronizar** (`sincronizar.py`), 7) legendas e inserções na timeline final |

### 2.1 Zoom (jump cut)

Alternância sutil entre o enquadramento original e um zoom suave pra dar ritmo aos cortes.

| Regra | Valor |
|---|---|
| Escala do zoom | 1,08× (8% de aproximação) |
| Origem | centro horizontal, 38% da altura (na região do peito/rosto) |
| Quando aplicar | nos jump cuts — a cada corte (pausa ou respiro), alternar entre enquadramento original e zoom |
| Duração | instantâneo no corte (sem transição animada) |

## 3. Legendas

Referência visual: vídeo de referência enviado pela Amanda em 2026-11-12 (blocos de texto serifado em itálico, empilhados, com uma linha grande no meio). Medidas abaixo tiradas dele, convertidas pra 1080×1920. Diferença intencional: a referência alterna com uma fonte sem serifa nas frases comuns; aqui **tudo é na serifada**.

| Regra | Valor |
|---|---|
| Fonte | **Instrument Serif Italic** (a mesma da referência), letras juntas (espaçamento −3%) |
| Cor | branca (#FFFFFF), sombra suave `0 2px 10px rgba(0,0,0,.45)`; glow opcional (§1) |
| Tamanho do texto normal | **99 px** (altura do "x" ≈ 51 px, medida na referência) |
| Posição | centro do bloco a ~65% da altura, na altura do peito; texto entre 11% e 89% da largura, centralizado pelo desenho das letras; nunca sobre o rosto (§0) nem fora da área segura (§0.1) |
| Bloco | **até 3 linhas, no máximo 3 palavras por linha**. Formato típico da referência: linha pequena / **linha grande** / linha pequena ("marca grande / **não tem** / um segredo.") |
| Espaço entre as linhas | **quase encostadas, encaixadas letra por letra**: cada linha desce até o desenho das letras quase tocar o da linha de cima (folga ~6 px), coluna por coluna. As palavras pequenas encaixam no vão das letras baixas da palavra grande; só um acento, o pingo do i ou a haste do t no caminho seguram a linha naquele ponto. Mínimo: da base de uma linha até o topo do "x" da seguinte, 0,65 × a altura do "x" do texto normal (as perninhas de "g", "p" quase tocam a linha de baixo). Medido pelo contorno real das letras, não pela caixa da fonte. **Nunca se sobrepõem:** números e letras altas (1, d, l, t) da linha de baixo ficam sempre abaixo das perninhas da linha de cima |
| Espaço entre palavras | 0,2 × o tamanho de cada palavra (entre palavras grandes, o espaço é grande também) |
| Aparecimento | **palavra por palavra**: cada palavra aparece no instante em que é falada, **saindo do desfocado** (0,25 s), e as anteriores **continuam na tela** até completar o bloco; aí o bloco desfoca e some (0,18 s) e entra o próximo. As palavras já nascem na posição final |
| Sincronia | a palavra aparece **junto com a voz, nunca antes**: `motor/sincronizar.py` usa o mesmo detector de fala (pelo tom). Palavra perto de um início de voz começa exatamente nele; na fala corrida, atrasa pelo erro médio medido no vídeo; e a palavra **nunca** entra num trecho sem voz (silêncio/respiro) |
| Linha larga demais | primeiro o destaque daquela linha diminui (até 1,4×); se não bastar, a linha quebra em duas; só uma palavra sozinha larga demais encolhe (§0.1) |
| Quebras | fim de frase troca o bloco; vírgula fecha a linha; palavra de ligação (de, que, a, o...) nunca fica no fim da linha nem do bloco |
| Fim extra | o bloco permanece 0,3 s depois da última palavra |
| Grafia | pelo glossário da marca (`marcas/<marca>/glossario.md`) |

### 3.0 Palavras de destaque (dentro da legenda)

| Regra | Valor |
|---|---|
| O que é | **1 ou 2 palavras** em tamanho **~1,94× maior** (192 px; altura do "x" ≈ 99 px, medida na referência), mesma fonte e cor. Duas palavras quando formam expressão: "**não tem**", "**de volume**", "**das mamas**", "**sem nada**" |
| Frequência | **pelo menos um a cada 4 s** (o motor avisa se passar disso); de preferência não mais que um a cada ~2,5 s |
| Qual palavra | a que carrega o sentido: números, nomes, o conceito do trecho, a conclusão da frase. Nunca palavra vazia ("isso", "muito", "vamos") nem de ligação |
| Sozinho numa linha | **alterna**: um destaque ocupa uma linha só dele (a linha grande do bloco), o seguinte divide a linha com outras palavras, e assim por diante. Quando ficar sozinho deixaria um pedaço solto, ele divide a linha dessa vez e o próximo fica sozinho. Destaque de 2 palavras nunca é separado |
| Como é feito | `motor/legendas.py` propõe blocos e destaques automaticamente; o Claude **revisa no plano** (troca destaques fracos por palavras de mais sentido e ajusta quebras estranhas) antes de gravar. No `edicao.json`, cada legenda leva `{"linhas", "destaques", "sozinha"}` |

### 3.1 Palavras-chave em destaque (opcional)

Só quando o cliente pedir. Palavra ou trecho curto em tamanho maior, centralizado, com entrada em fade+subida e saída em fade.

## 4. Inserções (b-roll e imagens)

Se o cliente colocar imagens em `insercoes/<nome-do-bruto>/`, elas entram no momento da fala a que se referem:

| Regra | Valor |
|---|---|
| Como entra | **card** abaixo do rosto, dentro da área segura (§0.1), com a legenda logo acima |
| Não cabe como card | vira **tela cheia** automaticamente: mídia vertical (9:16) ocupa a tela inteira; capa, print ou foto ficam **no alto da área segura (13%–55% da altura), inteiras, sobre fundo preto**, com a legenda **embaixo**, nunca por cima do texto da imagem |
| Duração | o trecho da fala (2–4 s, em geral) |
| Transição | corte seco (sem efeito) |
| Legenda durante inserção | continua aparecendo, palavra por palavra |

## 5. Cards e telas de texto (opcional)

Desligados por padrão. Se o cliente pedir:

| Regra | Valor |
|---|---|
| Estilo | fundo semi-transparente com bordas arredondadas (raio 16 px) |
| Posição | ~47% da altura |
| Largura | 82% da tela, sempre dentro da área segura lateral (§0.1) |
| Sombra | `0 12px 40px rgba(0,0,0,.25)` |
| Fonte | Instrument Serif Regular |

## 6. Áudio

| Regra | Valor |
|---|---|
| Música de fundo | **Opcional** — só com aprovação. Volume baixo (~15–20% do volume da voz), fade in/out suaves |
| Efeitos sonoros | **Opcional** — whoosh sutil nos cortes de cena, pop nos destaques. Só com aprovação |
| Normalização / tratamento da voz | **pendente** — decisão da Amanda (CLAUDE.md, "Tratamento de áudio"). Até lá o áudio sai original |
| Status | o motor ainda não mixa música nem efeitos (CLAUDE.md, biblioteca `_audio/`) |

## 7. Resumo: o que o padrão básico faz por padrão

| Recurso | Estado |
|---|---|
| Legendas palavra por palavra (Instrument Serif Italic, até 3 linhas × 3 palavras, linhas quase encostadas) | **Ligado** |
| Palavras de destaque na legenda (1–2 palavras, 1 a cada 4 s, alternando sozinha) | **Ligado** |
| Aceleração | Opcional (padrão: sem aceleração) |
| Glow na legenda | Opcional |
| Corte de pausas e respiros ≥ 0,2 s (detector pelo tom) + conferência por retranscrição | **Ligado** |
| Sincronia: palavra entra junto com a voz | **Ligado** |
| Área segura do Instagram (13% / 22% / 11% texto) | **Ligado** |
| Card que não cabe vira tela cheia | **Ligado** |
| Zoom alternado nos jump cuts | **Ligado** |
| Detecção de rosto (legenda nunca sobre o rosto; menos linhas quando falta espaço) | **Ligado** |
| Título de abertura | Opcional |
| Logo | Opcional |
| Palavras-chave em destaque | Opcional |
| Cards de texto | Opcional |
| Fundo mesclado | Desligado |
| Texto atrás da pessoa | Desligado |
| Efeito negativo | Desligado |
| Música de fundo | Opcional |
| Efeitos sonoros | Opcional |
