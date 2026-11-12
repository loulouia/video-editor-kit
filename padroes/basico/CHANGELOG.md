# Changelog — Padrão Básico

## v1.2 (2026-11-12)

Pedido da Amanda, a partir de um vídeo de referência e de testes nos vídeos do Adel (C5824) e da Mariana (IMG_4802). A v1.1 (Playfair, legenda pequena) foi testada e reprovada ("fonte muito pequena, estranho") e não chegou a ser publicada.

**Legenda**
- Fonte: Playfair Display Italic → **Instrument Serif Italic** (a fonte da referência; a Playfair foi comparada lado a lado). Letras juntas (−3%).
- Tamanho: texto normal 42 → **99 px**; destaque **~1,94×** (192 px). Medidos na referência.
- Blocos de **até 3 linhas**, no máximo 3 palavras por linha, **quase encostadas e encaixadas letra por letra** (o espaço é medido coluna por coluna pelo desenho real das letras — acentos, pingos, hastes, maiúsculas, números, perninhas —, com o mínimo medido na referência; nunca se sobrepõem).
- **Palavra por palavra**: cada palavra entra no tempo da fala, saindo do desfocado; as anteriores ficam; o bloco desfoca ao sair.
- **Destaques** de 1 ou 2 palavras (expressão: "não tem", "de volume"), pelo menos um a cada 4 s, alternando sozinho numa linha e junto.
- **Sincronia**: a palavra entra junto com a voz, nunca antes (o Whisper adiantava até 0,45 s; medido 0 de 286 palavras antes da voz no IMG_4802).
- **Glow** opcional (`projeto.json` → `"glow": true`).

**Área segura do Instagram e rosto**
- Legendas, cards, título e logo dentro da área segura de post orgânico: 13% em cima, 22% embaixo; texto entre 11% e 89% da largura (centralizado pelo desenho das letras); cards entre 4% e 89%; logo a 14% do topo e 12% da direita.
- Linha larga: o destaque diminui (até 1,4×) ou a linha quebra em duas.
- Sem espaço entre o queixo e a margem: o bloco vira menos linhas (mesmo tamanho de letra); só em último caso a letra encolhe.
- Card que não cabe vira tela cheia; capa/print/foto ficam no alto (13%–55%) sobre fundo preto, com a legenda embaixo.
- `rosto.py` passou a medir o rosto inteiro em selfie de perto (antes parava nos olhos); enquadramentos normais não mudam.

**Ritmo**
- **Pausas e respiros** com 0,2 s ou mais são cortados (antes, só silêncio absoluto > 0,5 s e sobravam 18–25 s sem voz em 1 min 50 s). Detector de fala pelo **tom** (`motor/voz.py`): o respiro, mesmo alto, não tem tom. No IMG_4802: respiros de 10 para 1; 20,9 s tirados; nenhuma palavra perdida (conferido retranscrevendo).
- **Aceleração**: nenhuma por padrão (1,0×); opcional 1,05–1,15× se o usuário pedir.

**Motor** (tudo configurável; só liga em padrões que pedem — o padrão `amanda` não muda): `voz.py`, `cortar_pausas.py`, `sincronizar.py` (novos); `legendas.py` (blocos e destaques); `gerar.py` (palavra por palavra, encaixe, área segura, menos linhas, tela cheia, glow); `rosto.py` (selfie de perto).

## v1.0 (2026-10-24)

Criação do padrão a partir de vídeo de referência (Mariana & Adel Bark).

- Legenda dinâmica: Playfair Display Italic, branca, word-by-word, posição inferior (~65%)
- Corte de silêncio > 0,5 s
- Zoom alternado nos jump cuts (1,08×)
- Detecção de rosto: legenda nunca sobre o rosto
- Aceleração sutil (1,0–1,1×)
- Sem logo, título, cards ou fundo mesclado por padrão (todos opcionais)
