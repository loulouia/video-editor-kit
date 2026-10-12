# Glossário de termos

Duas funções:
1. **Antes de transcrever:** a lista de termos certos é passada ao Whisper como contexto (`initial_prompt`), o que reduz os erros.
2. **Depois de transcrever:** cada erro conhecido é trocado pela grafia correta antes de virar legenda. Mesmo assim, toda legenda com nome próprio é conferida no plano.

Pra acrescentar um termo, é só falar: *"adiciona X no glossário"*.

## Termos certos (grafia usada nas legendas)

| Termo | Categoria |
|---|---|
| Amanda Lourenço | você |
| LOULOU Studios | sua marca |
| creator-founder | seus conceitos |
| ChatGPT | IA |
| Claude | IA |
| Anthropic | IA |
| OpenAI | IA |
| Dario Amodei, Daniela Amodei | pessoas |
| Sam Altman | pessoas |
| Lex Fridman | pessoas |
| Kendall Jenner | pessoas |
| Kardashian, Kardashian Curse | pessoas/termos |
| Fanatics, Fanatics Sportsbook | marcas |
| Super Bowl | eventos |
| Messy Middle | marketing |
| tráfego pago, público frio | marketing |
| Pierre Bourdieu, A Distinção, capital cultural | cultura |
| Breaking News, taste washing | termos |
| Greg Brockman | pessoas |
| Palantir | marcas |
| VSL, CAC, B2B, order bump | marketing |
| Creator Economy | marketing |

## Erros conhecidos do Whisper → correção

| Whisper escreveu | Correto | Visto em |
|---|---|---|
| chat IPT | ChatGPT | claude-chatgpt |
| cloud (quando é a IA) | Claude | claude-chatgpt |
| Modei | Amodei | claude-chatgpt |
| 100 ads | sem ads | claude-chatgpt |
| Massy Middle | Messy Middle | kendall-fanatics |
| Fanatic Sportsbook | Fanatics Sportsbook | kendall-fanatics |
| cac | CAC | kendall-fanatics |
| Creative Economy | Creator Economy | kendall-fanatics |
| o EV de lançamento | viver de lançamento | kendall-fanatics |
| coisa errada (depois de "order bump") | coisarada | kendall-fanatics |

**Atenção:** "cloud" só deve virar "Claude" quando o assunto for a IA; a correção é feita pelo contexto, não por substituição cega.

## Expressões da Amanda

Expressões e gírias que ela usa e que o Whisper tende a "corrigir" pra outra palavra. Manter como ela fala:

- coisarada
- viver de lançamento
