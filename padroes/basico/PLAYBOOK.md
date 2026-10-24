# Playbook de edição — Padrão Básico

**Status:** v1.0 (2026-10-24). Criado a partir de vídeo de referência (Mariana & Adel Bark — conteúdo hospitalar/cirúrgico). Valores lidos pelo motor: `padrao.json`. Histórico: `CHANGELOG.md`.

Tela: 1080×1920, 30 fps. Coordenadas em % da altura/largura da tela.

## 0. Regra de ouro: nada cobre o rosto

Legendas, título e qualquer elemento de texto **nunca ficam em cima do rosto** da pessoa que fala.

| Regra | Valor |
|---|---|
| Como | rosto mapeado ao longo do vídeo (`motor/rosto.py`). Cada elemento é posicionado abaixo do queixo, com folga de 2% da altura |
| Posição padrão da legenda | ~65% da altura — só vale quando o rosto está acima dessa linha |
| Se não couber embaixo | o elemento sobe pra acima do rosto |
| Limites da tela | entre 8% (topo) e 88% (acima da interface do Reels/TikTok) |

## 1. Identidade visual

| Elemento | Regra |
|---|---|
| Fonte das legendas | Playfair Display Italic (`fontes/PlayfairDisplay-Italic-Variable.ttf`), peso 500, livre (SIL OFL) |
| Fonte de apoio | Playfair Display Regular (`fontes/PlayfairDisplay-Variable.ttf`), pra cards e títulos quando necessário |
| Cor do texto | Branco (#FFFFFF) |
| Logo | **Opcional** — não tem logo fixo por padrão. Se a marca do cliente tiver logo, posicionar no canto superior direito (~4% do topo, ~5% da direita), ~13% da largura |
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
| Corte de silêncio | todo silêncio **acima de 0,5 s** é cortado. Manter silêncios ≤ 0,5 s — são pausas naturais da fala |
| Pausas intencionais | preservar 2–4 pausas por vídeo antes de frases de impacto (mesmo acima de 0,5 s), sob aprovação |
| Aceleração | **1,0× a 1,1×** (sutil). Só acelerar se a fala for lenta (< 3,0 palavras/s). Alvo: ~3,5 palavras/s |
| Margem do corte | nunca cortar no meio de sílaba; usar tempos por palavra da transcrição, com folga de 0,05 s |
| Ordem dos cortes | 1) transcrever, 2) cortar silêncios > 0,5 s, 3) acelerar (se aplicável), 4) cronometrar legendas e inserções na timeline final |

### 2.1 Zoom (jump cut)

Alternância sutil entre o enquadramento original e um zoom suave pra dar ritmo aos cortes.

| Regra | Valor |
|---|---|
| Escala do zoom | 1,08× (8% de aproximação) |
| Origem | centro horizontal, 38% da altura (na região do peito/rosto) |
| Quando aplicar | nos jump cuts — a cada corte de silêncio, alternar entre enquadramento original e zoom |
| Duração | instantâneo no corte (sem transição animada) |

## 3. Legendas

| Regra | Valor |
|---|---|
| Estilo | **Italic**, minúsculas (como fala natural), Playfair Display Italic |
| Cor | branca (#FFFFFF) |
| Tamanho | ~42 px |
| Sombra | `0 2px 10px rgba(0,0,0,.45)` — visível o suficiente pra ler sobre qualquer fundo |
| Posição | centralizada, ~65% da altura do frame (parte inferior, mas acima da safe zone do Reels) |
| Palavras por tela | 1 a 6, agrupadas por sentido (preposições coladas à próxima palavra) |
| Linhas | até 2 linhas, equilibradas |
| Largura máx | 85% da tela |
| Fim extra | legenda permanece 0,3 s após a última palavra do grupo |
| Grafia | pelo glossário da marca (`marcas/<marca>/glossario.md`) |

### 3.1 Palavras-chave em destaque (opcional)

Só quando o cliente pedir. Palavra ou trecho curto em tamanho maior, centralizado, com entrada em fade+subida e saída em fade.

## 4. Inserções (b-roll e imagens)

Se o cliente colocar imagens em `insercoes/<nome-do-bruto>/`:

| Regra | Valor |
|---|---|
| Enquadramento | imagem inteira dentro do frame 9:16, com letterbox se necessário |
| Duração | 2–4 s por inserção, no momento correspondente da fala |
| Transição | corte seco (sem efeito) |
| Legenda durante inserção | continua aparecendo normalmente |

## 5. Cards e telas de texto (opcional)

Desligados por padrão. Se o cliente pedir:

| Regra | Valor |
|---|---|
| Estilo | fundo semi-transparente com bordas arredondadas (raio 16 px) |
| Posição | ~47% da altura |
| Largura | 82% da tela |
| Sombra | `0 12px 40px rgba(0,0,0,.25)` |
| Fonte | Playfair Display Regular |

## 6. Áudio

| Regra | Valor |
|---|---|
| Música de fundo | **Opcional** — só com aprovação. Volume baixo (~15–20% do volume da voz), fade in/out suaves |
| Efeitos sonoros | **Opcional** — whoosh sutil nos cortes de cena, pop nos destaques. Só com aprovação |
| Normalização | normalizar o áudio da voz pra -14 LUFS (padrão pra Reels/TikTok) |

## 7. Resumo: o que o padrão básico faz por padrão

| Recurso | Estado |
|---|---|
| Legendas dinâmicas (italic, word-by-word) | **Ligado** |
| Corte de silêncio > 0,5 s | **Ligado** |
| Zoom alternado nos jump cuts | **Ligado** |
| Detecção de rosto (legenda nunca sobre o rosto) | **Ligado** |
| Título de abertura | Opcional |
| Logo | Opcional |
| Palavras-chave em destaque | Opcional |
| Cards de texto | Opcional |
| Fundo mesclado | Desligado |
| Texto atrás da pessoa | Desligado |
| Efeito negativo | Desligado |
| Música de fundo | Opcional |
| Efeitos sonoros | Opcional |
