# Playbook de edição — padrão "topo-livre"

**Status:** v0.1 — regras definidas pela Amanda (2026-10-12), a partir de `referencias/ref-topo-livre1.mp4` (análise em `analise/analise.md`). Ainda não testado num bruto. Padrão para **clientes**: nada da identidade da Amanda (sem LOULOU Studios, sem Helvetica). Valores lidos pelo motor: `padrao.json`. Histórico: `CHANGELOG.md`.

**Ideia do padrão:** a criadora fala em plano médio, e o **topo da tela é o lugar das inserções**: uma caixa fixa que nunca fica vazia, trocando de imagem a cada ~3 s, ilustrando literalmente o que ela fala. Embaixo, legenda pequena e discreta.

## 0. Regras herdadas do motor

- **Nada cobre o rosto** (inclusive a caixa do topo — ver §2, enquadramento).
- Cor e iluminação confirmadas em todo vídeo; plano → preview → render com aprovação; confirmação de todas as inserções (tabela) e do gancho.

## 1. Fontes

| Uso | Fonte | Licença |
|---|---|---|
| Legendas, título de abertura | **TikTok Sans** (`fontes/TikTokSans-Variable.ttf`, peso 300–900, largura 75–150) | SIL OFL 1.1 — uso comercial livre |
| Cartões de frase (dentro da caixa) | **Instrument Serif** (`fontes/InstrumentSerif-Regular.ttf` + itálico), em tamanho **maior** que na primeira prévia, pra ler bem no celular (escolha da Amanda) | SIL OFL 1.1 |

## 2. Inserção no topo (a marca do padrão)

| Regra | Valor |
|---|---|
| Caixa | **16:9 fixa**, ~66% da largura, centralizada, de ~17% a ~37,5% da altura |
| Cantos | **retos** (sem arredondamento), sem borda, sem sombra (decisão da Amanda) |
| Troca | corte seco; uma inserção a cada ~3 s (de 1 a 15 s cada; diagramas e explicações longas podem ficar mais) |
| Topo nunca vazio | depois do título de abertura, sempre há algo na caixa |
| Conteúdo | (1) fotos/cenas que ilustram literalmente a fala; (2) **cartões de frase** gerados automaticamente (§3); (3) diagramas e prints do cliente |
| Imagem dentro da caixa | preenche a caixa inteira (corte "cover"); prints e diagramas que não podem ser cortados vão inteiros, com fundo do próprio cartão |
| **Enquadramento** (decisão da Amanda: opção B) | o motor **não** desloca o vídeo. A criadora grava com espaço acima da cabeça: **topo da cabeça a ~38–40% da altura** (logo abaixo da caixa). Se o bruto vier com a cabeça mais alta, o plano **avisa** (com a medida) e pergunta: regravar, ou aceitar uma caixa menor que caiba acima da cabeça (se houver espaço). A caixa nunca cobre o rosto |

## 3. Cartões de frase (pontuais)

**Regra principal (decisão da Amanda):** o conteúdo da caixa do topo é **imagem** — buscada no **Google / Pinterest** ou **enviada pelo usuário**. Cartão é **exceção**, usado só em dois casos:
1. uma **frase muito importante** (a tese, a virada do vídeo) que merece ficar escrita;
2. um **esquema visual** que explica melhor que uma foto (etapas, comparação, diagrama).

Não há limite de quantidade: o critério é o conteúdo. No plano, cada cartão vem justificado ("frase muito importante" ou "esquema visual").

| Regra | Valor |
|---|---|
| Fonte | Instrument Serif (§1) |
| Layout | modelos **pedra** (frase centralizada), **carvão** (palavra em itálico em destaque) e **papel** (título + traço + itens/etapas) |
| Cores | §6 (paleta da marca do cliente; tons neutros se não houver) |

**Imagens de Google/Pinterest:** em vídeo de cliente, o direito de uso da imagem é responsabilidade de quem publica. No plano, o Claude indica a origem de cada imagem; quando houver alternativa equivalente em banco livre (Unsplash), ela é oferecida junto.

## 4. Legenda

| Regra | Valor |
|---|---|
| Fonte | TikTok Sans, peso médio (~500) |
| Estilo | branca, frase em minúsculas (sentence case), sem destaque de palavra |
| Tamanho | ~2% da altura (~38 px em 1080×1920), mantido |
| Posição | centralizada, ~80% da altura (sempre abaixo do rosto) |
| **Largura máxima** | **~55% da largura da tela** (de ~22,5% a ~77,5%), centralizada — nunca uma linha comprida de ponta a ponta (correção da Amanda) |
| Quantidade | **no máximo 2 linhas**, até **~31 caracteres por linha** (~60 por legenda); as duas linhas com comprimento parecido. Frase maior que isso vira duas legendas |
| Quebras | uma legenda nunca termina em palavra de ligação (pra, de, que, e, o, a...), e dentro da legenda a palavra de ligação fica presa à seguinte (nunca sozinha no fim da linha). Sobra curta junta na legenda anterior. Divisão automática: `motor/legendas.py` |

## 5. Gancho e primeiros segundos

Medido em `referencias/ref-topo-livre1.mp4` (0,0–1,9 s). A pergunta do gancho do motor (PLAYBOOK 4.0 do padrão Amanda: quantas inserções, tipo, duração) vale aqui, com esta composição como padrão.

| Elemento | Regra |
|---|---|
| Duração | o título fica **~2 s** (enquanto a criadora fala a frase de abertura); depois, corte seco pra primeira inserção da caixa do topo |
| Fala | a frase de abertura nomeia o tema ("welcome to sales maxxing 101"); a legenda normal aparece junto, a ~80% |
| **Colagem** | **3 imagens** lado a lado, **~29% da largura cada**, margens de ~3–4%, de **12% a 28%** da altura; cantos retos; resumem o vídeo (vêm das inserções do próprio vídeo) |
| **Título** | TikTok Sans **peso ~600** (não ultra-negrito), **MAIÚSCULAS**, branco, **sem sombra**. Letras com **~4,7% da altura da tela**, topo das letras a **~26,3%** — **sobrepõe a base da colagem**. Até ~92% da largura. **Tamanho fixo em todos os vídeos do topo-livre.** **Até 18 caracteres por linha** (contando espaços; a referência tem 17): se o título passar disso, **quebra em nova linha abaixo**, no mesmo tamanho — nunca diminui a letra |
| **Subtítulo** | TikTok Sans **fino** (peso ~300), minúsculas, branco, **sem sombra**, **colado no título** (~0,9% da altura abaixo da última linha do título), **~78% da largura**, **até 45 caracteres** (a referência tem 43); pode ter **uma palavra em MAIÚSCULAS** pra ênfase ("to sell ANYTHING to anyone…") |
| Proibido | sombra, brilho ou contorno no título e no subtítulo (reprovado pela Amanda: "sombra feia/brega") |
| Rosto | tudo termina acima de ~35%; com o enquadramento do padrão, a cabeça começa em ~38–40% (regra §0) |
| No plano | o Claude propõe título (curto, com número ou termo forte), subtítulo (a promessa) e as 3 imagens da colagem; a criadora aprova |

## 6. Paleta de cores (cartões de frase)

| Regra | Valor |
|---|---|
| Fonte da paleta | **a paleta da marca do cliente** (`marcas/<cliente>/marca.json` → `"paleta"`) |
| Sem paleta na marca | **tons neutros suaves** (fallback): pedra `#DCD5CA`, papel `#F4F1EB`, areia `#E7E0D4`, taupe `#A89B88`, carvão `#2A2724`. Texto escuro `#2A2724` sobre fundos claros; claro `#F2EDE4` sobre carvão |
| Proibido | cores saturadas e "gritantes" (os laranjas e azuis fortes da primeira prévia foram reprovados: "fortes e bregas") |
| Textura | grão de papel sutil, quase imperceptível |

## 7. Recursos do motor

| Recurso | No topo-livre |
|---|---|
| Palavras-chave em destaque, efeito negativo | disponíveis **sob pedido** (confirmado) (ficam na altura do peito; não conflitam com a caixa) |
| Fundo mesclado, texto atrás da pessoa | **desligados** (disputam o topo com a caixa); o motor recusa e explica |
| Zoom de jump cut | desligado (a referência é um take só, enquadramento fixo) |
| Logo | da marca do cliente, pequeno, **só se o cliente pedir** |
| Ritmo | regra do motor: cortar pausas + acelerar 1,10–1,15× (a referência fala a 3,54 palavras/s, sem pausas > 0,5 s) |
| Música, efeitos sonoros, transições | da biblioteca do Drive (`_audio/musicas/`, `_audio/efeitos/`, `_transicoes/`), **só com aprovação no plano**; regras a definir (o motor ainda não usa) |
