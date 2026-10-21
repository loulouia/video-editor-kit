# Histórico do padrão topo-livre

## 2026-10-21 — biblioteca de áudio e transições

- Nova seção/linha: música, efeitos sonoros e transições vêm da biblioteca do Drive (`_audio/musicas/`, `_audio/efeitos/`, `_transicoes/`) e só entram com aprovação no plano. Regras de volume e uso a definir no primeiro vídeo com áudio. Motivo: pedido da Amanda.

## 2026-10-12 — v0.1

- Padrão criado pelo caminho B a partir de `referencias/ref-topo-livre1.mp4`. Para clientes: TikTok Sans, sem identidade da Amanda.
- Decisões da Amanda: o **topo é o lugar das inserções** (caixa 16:9 fixa, nunca vazia); **cantos retos**; **cartões de frase automáticos** com fonte serifada e layout com design; legenda em TikTok Sans no tamanho da referência; enquadramento **opção B** (a criadora grava com espaço acima da cabeça; o motor só avisa, não desloca); logo pequeno só sob pedido.
- Recursos (confirmado pela Amanda): palavras-chave/efeito negativo sob pedido; fundo mesclado e texto atrás desligados (conflitam com a caixa do topo).

## 2026-10-12 — v0.2

- **Gancho (§5) detalhado** com as medidas da referência: colagem de 3 imagens (27% da largura cada, 12–28% da altura), título em maiúsculas a 91% da largura encostando na colagem, subtítulo fino com uma palavra em MAIÚSCULAS, ~2 s. Motivo: pergunta da Amanda.
- **Cartões:** fonte **Instrument Serif**, maior. **Paleta (§6):** a da marca do cliente; sem paleta, tons neutros suaves. Motivo: a primeira prévia foi reprovada ("cores muito fortes e bregas").

## 2026-10-12 — v0.3

- **Legenda (§4):** largura máxima ~55% da tela, no máximo 2 linhas de ~31 caracteres, linhas equilibradas. Motivo: correção da Amanda (a prévia tinha texto demais na mesma linha). Medido na referência (leituras limpas: 49–55% da largura, linha mais longa com 31 caracteres).
- Quebras de legenda: nunca terminar legenda nem linha em palavra de ligação; sobras curtas juntam na anterior. O motor ganhou `legendas.py` (divisão automática pelo limite do padrão) e o gerador avisa quando uma legenda passa do limite.

## 2026-10-12 — v0.4

- **Gancho (§5) refeito pela referência:** título peso ~600 sem sombra, letras com 4,7% da altura sobrepondo a base da colagem, até ~18 caracteres; subtítulo fino colado embaixo (78% da largura); colagem de 3 × 29%. Motivo: correção da Amanda (sombra feia; subtítulo distante e pequeno; título fora do padrão).
- **Cartões (§3) passam a ser pontuais:** só pra frase muito importante ou esquema visual. O resto da caixa do topo são imagens de Google/Pinterest ou do usuário. Motivo: decisão da Amanda.

## 2026-10-12 — v0.5

- **Título do gancho:** tamanho fixo; até 18 caracteres por linha — passou disso, quebra em nova linha abaixo (não diminui, não reescreve). **Subtítulo:** até 45 caracteres. Motivo: definição da Amanda, só pro topo-livre.
- Correção: removido o limite "1–2 cartões por vídeo", que o Claude tinha inventado. Vale só o critério da Amanda (frase muito importante ou esquema visual; o resto é imagem).
