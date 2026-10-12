# Análise inicial — 2026-10-12

Caminho A (partir do estilo atual). Referências do Kaio usadas **só pelo efeito "topo mesclado"** (imagem/vídeo no topo, mesclada ao fundo, com a pessoa na frente).

## Vídeos analisados

| Vídeo | Formato | Duração |
|---|---|---|
| meus-editados/claude-chatgpt | 1080×1920, 30 fps | 1:56 |
| meus-editados/kendall-fanatics | 1080×1920, 30 fps | 2:23 |
| referencias/ref1-kaio | 720×1280, 24 fps | 2:53 |
| referencias/ref2-kaio | 720×1280, 24 fps | 2:16 |

## Medidas (M = medido, E = estimado visualmente)

| Aspecto | Amanda hoje | Kaio (ref1 / ref2) |
|---|---|---|
| Velocidade da fala (M) | 3,7 palavras/s | 3,5 palavras/s |
| Pausas entre palavras (M) | mediana 0 s; só 3–6 pausas > 0,3 s por vídeo | mediana 0 s; 4 pausas > 0,3 s por vídeo |
| Cortes por minuto (M) | 23 (claude-chatgpt) / 12 (kendall) | 13 / 7,5 |
| Enquadramento (E) | plano aberto, sentada de pernas cruzadas com notebook; cabeça entre 12% e 30% da altura; jump cuts alternando aberto/mais fechado | plano médio na mesa; cabeça entre 25% e 40% |
| Fundo (E) | parede clara cinza-esverdeada | ref1: sala quente; ref2: estúdio escuro |
| Legenda (E) | Helvetica Now Display ExtraBold, branca, MAIÚSCULAS, 2–5 palavras, centralizada a ~54% da altura (sobe pra ~44% quando há card) | sans regular pequena, branca, MAIÚSCULAS, 2–4 palavras, a ~67% da altura |
| Destaque de palavra (E) | palavra única maior, branca (ex.: "KARDASHIAN") | palavras-chave grandes em vermelho com brilho (glow), montadas palavra por palavra, posição variável |
| Título de abertura (E) | 3 linhas + subtítulo menor entre parênteses, nos primeiros ~5 s | não usa |
| Logo (E) | "LOULOU STUDIOS" cinza, canto superior direito (~7% do topo), o vídeo todo | não usa |
| Inserções (E) | cards com borda arredondada (~88% da largura, entre 47% e 80% da altura); cards de notícia (brancos ou escuros); diagramas | quase não usa |
| Cortes pra b-roll em tela cheia (E) | sim, frequentes (anúncios, pessoas citadas) | ocasionais (comida, foto antiga) |
| Encerramento (E) | clipe horizontal com faixas pretas e legenda acima | sem CTA visual |
| **Topo mesclado (E)** | não usa | imagem/vídeo de 0% a ~37% da altura, degradê de ~34% a ~45% até o fundo original; cabeça/cabelo **na frente** da imagem; troca de imagem a cada 1–4 s acompanhando o assunto |

## Palavras-chave do Kaio (M)

Detecção automática do texto de destaque (4 quadros/s, abaixo de 42% da altura), cruzada com a transcrição.

| | ref1-kaio | ref2-kaio |
|---|---|---|
| Destaques | 31 (10,7/min) | 23 (10,1/min) |
| Tempo do vídeo com destaque | 23% | 22% |
| Duração | 0,5–3,5 s (normal 1–1,5 s) | 0,5–3,25 s |
| Altura | 50–73% | 51–75% |

Exemplos: "não conseguem copiar", "Novembro de 2020", "14 horas", "por um único hambúrguer", "pelo amor de Deus", "às duas da manhã", "4 mil versus 18", "pertencimento", "marca sem convicção não constrói cultura" (ref1); "não consegue copiar", "17 milhões e 800 mil pessoas", "do planeta", "cinzas de um parente", "identidade" (ref2).

## Observações técnicas

- O efeito exige 3 camadas: vídeo original → imagem do topo com máscara em degradê → a Amanda recortada por cima (HyperFrames `remove-background`). As legendas e o logo ficam acima de tudo.
- O enquadramento atual da Amanda funciona: a cabeça fica dentro da faixa da imagem, e o cabelo escuro contrasta bem com a parede clara (bom pro recorte).
- O degradê do Kaio termina em fundo escuro, o que disfarça a emenda. Na parede clara a emenda fica mais visível; isso precisa ser testado.
- A transcrição troca nomes próprios ("chat IPT" → ChatGPT, "cloud" → Claude, "Inenalte" → In-N-Out). O playbook precisa de um glossário de termos.
