# Editor de vídeo (Reels / TikTok)

Edição de vídeos curtos (1080×1920) feita pelo Claude em código: cortes de pausas, aceleração, cor, legendas, palavras-chave, inserções, fundo mesclado e render, sempre com plano e preview aprovados por você.

## Como está organizado

| Pasta | O que é |
|---|---|
| `motor/` | **Como editar.** Os scripts que fazem o trabalho. São os mesmos pra qualquer estilo (não mexer) |
| `padroes/<nome>/` | **Um estilo de edição.** Regras (`PLAYBOOK.md`), valores (`padrao.json`), histórico (`CHANGELOG.md`), fontes e vídeos de referência |
| `marcas/<nome>/` | **Um criador ou cliente.** Logo (claro e escuro), glossário de termos, cor do cenário (LUT) e vídeos já editados |
| `projetos/<nome-do-video>/` | **Um vídeo.** Plano, decisões, inserções e a composição. Criada pelo Claude quando você coloca o bruto |
| `entrada/brutos/` | Onde você coloca os vídeos gravados, sem edição |
| `saida/` | Vídeos prontos |
| `tools/` | Ferramentas instaladas (não mexer) |

Cada vídeo combina **um padrão + uma marca**. Ex.: o TASTE WASHING 5 é *padrão amanda + marca amanda*. O mesmo vídeo pode ser editado em outro padrão sem mudar nada da marca.

### Padrões existentes

| Padrão | Status | Para |
|---|---|---|
| `amanda` | v1.0, oficial | uso próprio (Helvetica Now Display, LOULOU Studios) |
| `topo-livre` | em criação | clientes (fonte TikTok Sans, livre) |

## Criar um padrão novo

1. **Escolha o caminho.**
   - **A. Partir de vídeos editados** de uma marca: eles ficam em `marcas/<nome>/meus-editados/`. Referências em `padroes/<novo>/referencias/` entram só como elementos pontuais.
   - **B. Copiar o estilo de referências:** coloque **2 a 3 vídeos do mesmo criador** em `padroes/<novo>/referencias/`. O que se repete entre eles é o estilo; a identidade do criador (logo, paleta exata, bordões) não é copiada.
2. **Coloque os arquivos.** MP4 ou MOV, nomes sem espaços e sem acentos. Salve as referências pelo próprio app ou grave a tela, evitando a interface do app por cima.
3. **Avise o Claude:** o caminho, a referência principal (no B) e o que você gosta em cada referência (ritmo, legendas, transições...).
4. O Claude analisa e devolve uma **tabela comparativa** com uma coluna "Proposta". Você decide cada linha, e o padrão nasce (`PLAYBOOK.md` + `padrao.json`).
5. **Teste com um bruto.** Ver o mesmo vídeo em dois padrões, lado a lado, é a melhor forma de comparar.

Recursos que o motor já sabe fazer e que cada padrão liga, desliga ou ajusta: legendas, título do gancho, palavras-chave (com efeito negativo opcional), texto atrás da pessoa, fundo mesclado, cards e notícias, zoom de jump cut, grading de cor, "nada cobre o rosto". Se uma referência tiver algo novo, o recurso é construído no motor e fica disponível pra todos os padrões.

**Fontes:** padrão pra clientes usa só fontes livres (ex.: Google Fonts). Fontes pagas exigem licença pra uso em serviço.

## Como funciona cada edição

Nada é renderizado sem você aprovar.

1. **Você pede.** Coloque o bruto em `entrada/brutos/` e diga o padrão e a marca. O Claude cria `projetos/<nome-do-video>/insercoes/`: coloque lá as imagens e vídeos desse vídeo (opcional: o momento no nome, ex.: `0m12-noticia-openai.png`). Pra cada inserção você pode escolher o tipo: card (na base ou no topo), notícia, tela cheia, horizontal com faixas pretas ou fundo mesclado. Recursos opcionais só entram quando você pede (ex.: *"com palavras-chave; no gancho, texto atrás de mim"*).
   - **Cor e iluminação:** o Claude mostra um antes/depois e pergunta qual coloração usar: a da marca (padrão), a de outra referência ou a original.
   - **Pesquisa de imagens e notícias (opcional):** peça *"busca imagens e notícias"*. O Claude propõe as buscas, você aprova, escolhe nas opções e só o escolhido é baixado.
2. **Plano (você aprova).** Cortes com o tempo de cada um, aceleração, duração final, legendas, palavras-chave, tabela de inserções (fala exata, entrada/saída, duração, tipo) e a pergunta do gancho.
3. **Storyboard (você aprova).** Antes de montar, uma folha com um quadro por momento do vídeo, já com a composição real: gancho, imagens, cartões, legendas e palavras-chave nas posições do padrão, com tempo, fala, origem de cada imagem e **alertas em vermelho** quando algo fere uma regra. Você corrige pelo número do quadro (ex.: *"quadro 4: troca a imagem"*). Vale pra todos os padrões.
4. **Preview (você ajusta).** Timeline no navegador do app; cada ajuste aparece em segundos. Ex.: *"aos 0:07 a legenda cobre a boca"*.
5. **Render.** Só com a sua aprovação: MP4 1080×1920 em `saida/`.
6. **Aprendizado.** Toda correção vira regra no padrão (ou no glossário da marca), registrada no `CHANGELOG.md`.

## Ferramentas instaladas

| Ferramenta | Para quê | Onde |
|---|---|---|
| ffmpeg 9 | cortar, juntar, converter, cor (LUT), camadas | Homebrew |
| mlx-whisper (large-v3-turbo) | transcrição com tempo por palavra (rápido no M4) | `~/.video-skill` |
| opencv, matplotlib | medidas, mapa do rosto, texto atrás | `~/.video-skill` |
| HyperFrames + skills | composição, recorte da pessoa (remove-background), preview, render | `npx hyperframes`, `~/.claude/skills` |
| Remotion skills, claude-shorts | instalados, não usados neste fluxo | `~/.claude/skills` |
| git | controle de versão (repositório privado) | Homebrew |

Telemetria do HyperFrames desativada.
