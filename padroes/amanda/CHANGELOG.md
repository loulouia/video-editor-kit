# Histórico do playbook

## 2026-10-12 — v1.5

- Palavras-chave (3.1): **encaixe no vão**. A linha pequena de antes desce até o topo das letras baixas iniciais da palavra grande quando cabe ali ("um" colado no pingo do "i" de "vilão"). Motivo: correção da Amanda; o "um" estava acima da letra mais alta, longe da palavra.

## 2026-10-12 — v1.4

- Fundo mesclado (4.5): proporção passa a ser **60% imagem / no máximo 40% embaixo** (sólida até 56%, degradê 56–64%, cabeça a ~46%). Motivo: pedido da Amanda.
- taste-washing-5: efeito negativo aplicado em "pessoal." e "CAPITAL CULTURAL".

## 2026-10-12 — v1.3

- Palavras-chave (3.1): nova variação opcional **efeito negativo** (letras invertem as cores do vídeo atrás delas), escolhida por palavra-chave. Motivo: pedido da Amanda.

## 2026-10-12 — v1.2

- Nova regra **§0 Nada cobre o rosto**: título, cards, legendas e palavras-chave são posicionados pelo mapa do rosto (abaixo do queixo; se não couber, o card encolhe ou o elemento vai acima do rosto). Motivo: no preview, título e notícia do gancho ficaram em cima do rosto no trecho em que a Amanda está mais perto da câmera.
- taste-washing-5: grading dos meus-editados aplicado a 100%.

## 2026-10-12 — v1.1

- Nova seção **1.1 Cor e iluminação**: por padrão, o bruto recebe o grading dos `meus-editados` (LUT gerada a partir dos quadros da Amanda falando), aplicado antes do recorte. Em todo vídeo há uma confirmação com antes/depois: estilo dos meus-editados, de outra referência ou original. Motivo: pedido da Amanda.

## 2026-10-12 — v1.0

- **Fundo mesclado (4.5):** a imagem ocupa ≥ 50% da tela, o vídeo da Amanda desce (cabeça a ~40%, pernas saem do quadro), o deslocamento é medido automaticamente em cada vídeo, corte seco, legendas e palavras-chave descem nesses trechos. Motivo: pedido da Amanda; precisa funcionar em outros enquadramentos.
- Camadas com a pessoa na frente passam a ser embutidas num vídeo único (sem "fantasma" no preview).
- Texto atrás (3.2): largura calculada já descontando o zoom do trecho.
- Palavras-chave (3.1): âncora das palavras pequenas na palavra grande; linha de depois mais larga cresce pra direita.
- taste-washing-5: gancho com 1 notícia na base (opção C), escolhida pela Amanda.

## 2026-10-12 — v0.9

- Palavras-chave (3.1): a distância entre as linhas passa a ser medida pelo contorno real das letras, com folga de ~4% do tamanho da palavra principal. Motivo: no 1º preview o vão entre as palavras pequenas e a grande ficou maior que nas referências `palavras-chave-1/2/3`.

## 2026-10-12 — v0.8

- Nova seção **4.0 Confirmação obrigatória das inserções**: o plano traz uma tabela com fala exata, entrada/saída, duração na tela, arquivo e tipo/posição de cada inserção. O **gancho** (primeiros ~5 s) é uma decisão separada: quantas inserções, tipo, posição e duração. Motivo: pedido da Amanda depois do primeiro preview.
- Card (4.1): passa a ter duas posições, **base** (padrão) ou **topo**.
- Início falso do "mostrou que" mantido no taste-washing-5: a Amanda escolheu, ouvindo 3 versões, manter a fala original.

## 2026-10-12 — v0.7

- Nova seção **5. Pesquisa de imagens e notícias**, opcional. Tem uma etapa obrigatória de definição de queries (4 a 8, de 2 a 5 palavras, específicas), aprovada antes de qualquer busca. Galeria pra escolha, download só do escolhido, print de manchete com alternativa de card recriado. Se algo falhar, a Amanda coloca o arquivo em `projetos/<slug>/insercoes/`. Motivo: pedido da Amanda.
- Logo (§1): troca automática pra versão clara sobre imagem escura no topo mesclado (aprendido no teste do taste-washing-5).

## 2026-10-12 — v0.6

- Ritmo (2): **aceleração do bruto de 1,10× a 1,15×**, escolhida pela velocidade da fala, com meta de ~3,7 palavras/s (o ritmo medido nos editados, que já estavam acelerados). A voz mantém o tom; inserções ficam na velocidade original. Motivo: é o que a Amanda faz no CapCut.

## 2026-10-12 — v0.5

- Palavras-chave (3.1): a palavra principal pode ser em minúsculas ou MAIÚSCULAS, conforme o caso. Motivo: decisão da Amanda.
- Novo recurso **3.2 Texto atrás da pessoa**, **opcional**. Medido em `palavras-chave-3` (0:09–0:11), com a fonte e a cor da Amanda no lugar da fonte condensada vermelha da referência. Motivo: pedido da Amanda. Pendências de teste: contraste na parede clara, espaço acima da cabeça, logo.

## 2026-10-12 — v0.4

- **Aparência das palavras-chave (3.1) definida.** Fonte e cor vieram da Amanda (Helvetica Now Display ExtraBold, branca). Composição, tamanho, espaçamento, entrada/saída e posição foram medidos nas referências `palavras-chave-1`, `-2` e `-3`. A frequência e os critérios de escolha continuam os do Kaio. Pendente: minúsculas ou maiúsculas na palavra principal.

## 2026-10-12 — v0.3

- Nova seção **3.1 Palavras-chave em destaque**, **opcional**. A lógica foi medida nas referências do Kaio: frequência, duração, montagem palavra por palavra, legenda normal some, hierarquia de tamanho e critérios de escolha. Motivo: a Amanda quer a lógica do Kaio, mas não a aparência dele. Fonte, cor, efeito, disposição e tamanho ficam "a definir" até chegar o novo conjunto de referências. O vermelho com brilho não será usado.

## 2026-10-12 — v0.2

- "Encerramento horizontal" deixou de ser padrão. Virou dois itens: o tipo de inserção **horizontal com faixas pretas** (4.4), que pode ser usado em qualquer momento, e o **encerramento com vídeo**, que é opcional e usa tela cheia ou horizontal. Motivo: correção da Amanda — o vídeo nem sempre termina com um clipe.
- Glossário: as 3 dúvidas foram respondidas (Creator Economy, "viver de lançamento", "coisarada"). Criada a seção "Expressões da Amanda".

## 2026-10-12 — v0.1 (rascunho)

- Playbook criado a partir de `meus-editados/` (claude-chatgpt, kendall-fanatics). Análise em `projetos/analise-inicial/analise.md`.
- Ritmo, legendas, logo, título e inserções (card, notícia, tela cheia, encerramento) descritos a partir do padrão atual.
- **Topo mesclado** (das referências do Kaio) adicionado como tipo de inserção **opcional**, aplicado só quando a Amanda pedir. Motivo: decisão da Amanda — é uma escolha por inserção, não o padrão do estilo. Cards de print/notícia continuam valendo nos trechos com topo mesclado.
- Glossário criado com os erros reais da transcrição dos dois vídeos.
