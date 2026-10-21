# Regras de trabalho — editor de vídeo

Pipeline de edição de vídeos curtos (Reels/TikTok, 1080×1920) feito em código. Visão de uso: `LEIA-ME.md`. Comandos do pipeline: `motor/LEIA-ME.md`.

## Comandos do projeto e início de sessão

Comandos (skills em `.claude/skills/`): `/video-editor-configurar` (primeiro uso), `/video-editor-videos` (status no Drive), `/video-editor-editar` (editar ou reabrir), `/video-editor-entregar` (render + entrega), `/video-editor-novo-padrao`. Pedidos em linguagem normal seguem o mesmo fluxo do comando correspondente.

Ao abrir o projeto, o hook `SessionStart` (`.claude/settings.json` → `motor/inicio.py`) informa se o setup está completo e quais vídeos estão novos/em andamento no Drive. Na primeira resposta: setup incompleto → indicar `/video-editor-configurar` e não editar; completo → citar em uma frase os vídeos novos/em andamento.

## Nome da pasta: `video-editor.nosync`

O projeto é distribuído com a pasta já chamada **`video-editor.nosync`**: pastas terminadas em `.nosync` não são sincronizadas pelo iCloud, então os arquivos ficam sempre no Mac (com "Mesa e Documentos" no iCloud e pouco espaço, o macOS tira arquivos do disco — aconteceu com 471 arquivos deste projeto em 2026-10-20, e git dentro do iCloud pode corromper). A pessoa coloca a pasta onde quiser; o motor funciona em qualquer lugar. O `/video-editor-configurar` confere: se a pasta estiver sem `.nosync` **e** num lugar sincronizado pelo iCloud, explica em uma frase e pede OK pra renomear (baixando antes os arquivos que estiverem só no iCloud).

## Drive e Mac (cada pessoa usa o próprio Drive)

```
Meu Drive/Edição de vídeos/
  brutos/                       ← SÓ vídeos pra editar (só arquivos direto aqui são brutos)
  insercoes/<nome-do-bruto>/    ← imagens e b-roll daquele vídeo (nomes livres)
  editados/                     ← <nome-do-bruto>-<padrão>.mp4 (reedição: -v2, -v3; nunca sobrescreve)
  _padroes/<padrão>/referencias/  _marca/meus-editados/   ← vídeos de referência e editados da marca
  _backup/                      ← zip do projeto após cada entrega (5 mais recentes)
  _audio/musicas/               ← biblioteca: trilhas (mp3/wav), pra qualquer projeto/padrão
  _audio/efeitos/               ← biblioteca: efeitos sonoros (whoosh, pop, clique...)
  _transicoes/                  ← biblioteca: transições em vídeo pra overlay (com alfa ou fundo preto/verde)
```
- **Biblioteca (`_audio/`, `_transicoes/`):** compartilhada por todos os projetos e padrões; a pessoa abastece, com nomes que dizem o uso (`calma-piano.mp3`, `whoosh-card.wav`, `flash-branco.mov`). Só arquivos que ela tem direito de usar (livres de royalties ou comprados). Baixar só o que o vídeo usa pra `projetos/<slug>/cache/` (apagado na entrega). Cada padrão diz no PLAYBOOK se usa música/efeitos/transições e como; em cada vídeo, sugerir no plano (arquivo, momento, volume) e **só aplicar com aprovação**. **O motor ainda não mixa áudio nem aplica transições** (pendente): implementar de forma configurável no primeiro vídeo que pedir (música com volume baixo e abaixando sob a voz, entrada/saída suaves; efeitos em eventos como entrada de card/palavra-chave; transição como overlay nos cortes).
- Transporte: **rclone** (`motor/drive.py`; config em `config/ambiente.json`, remote `gdrive:`). O conector do Google Drive só serve pra consultar/listar — não transfere vídeo.
- **Nunca** renomear, mover ou apagar arquivos da pessoa no Drive. Única exceção: backups antigos que o próprio motor criou em `_backup/`.
- Vídeo ambíguo em `brutos/` (sem fala, muito curto, nome tipo "broll") → perguntar se é bruto ou inserção; nunca decidir sozinho.
- No Mac fica só o permanente e pequeno: motor, padrões, marcas, `registro.json` e as decisões de cada vídeo. Bruto e inserções são baixados em `projetos/<slug>/cache/` e `composicao/assets/img/` só durante a edição.
- **Entrega** (`motor/entregar.py`): render → envio → **conferência (tamanho + MD5)** → versão do motor/padrão guardada em `versao/` → limpeza **automática** dos temporários (sem perguntar; só depois de conferir) → backup. Aviso final tranquilizador: o que foi entregue, quanto espaço foi liberado, e que tudo pra reeditar está guardado.
- **Reedição** (`motor/reabrir.py`): perguntar "igual à versão entregue" (padrão) ou "com o padrão atualizado".
- **Padrão de cada vídeo:** sempre perguntar, a menos que `marca.json` tenha `"padrao_padrao"` definido.

## Estrutura: motor, padrões, marcas, projetos

| Pasta | O que é | Muda entre… |
|---|---|---|
| `motor/` | **Como editar.** Scripts genéricos (cortes, cor, recorte, rosto, camadas, gerador). Igual pra todos | nunca muda por estilo; melhorias valem pra todos os padrões |
| `padroes/<nome>/` | **O visual.** `PLAYBOOK.md` (regras e porquês), `padrao.json` (valores que o motor lê), `CHANGELOG.md`, `fontes/`, `analise/` (vídeos de referência ficam no Drive) | estilos |
| `marcas/<nome>/` | **O criador.** `marca.json`, logos claro/escuro, `glossario.md`, LUT do cenário (`cor/`) | pessoas/clientes |
| `projetos/<slug>/` | **Um vídeo (decisões).** `projeto.json` (padrão, marca, aceleração, grading, entregas), `edicao.json` (o que entra e quando), `cortes.json`, `transcricao/`, `storyboard/`, `versao/` | vídeos |

Regras:
- **Nunca** escrever valor visual fixo no motor: ele lê `padrao.json`. Recurso novo pedido por um padrão → implementar no motor de forma configurável, com o valor do padrão em `padrao.json`, e ligar/desligar em `"recursos"`.
- Ajuste visual pedido durante a edição de um vídeo vale **só pra esse vídeo** (`edicao.json`/`projeto.json`), mesmo com "vale pra tudo". O padrão só muda quando a pessoa disser explicitamente que é pro padrão / pra todos os vídeos; na dúvida, aplicar no vídeo e perguntar uma vez se leva pro padrão. Mudança aprovada pro padrão → `padroes/<nome>/PLAYBOOK.md` + `padrao.json` + entrada no `CHANGELOG.md` do padrão. Sobre grafia de termos → `marcas/<nome>/glossario.md`.
- Ao mexer no motor, regenerar um projeto já aprovado (ex.: `taste-washing-5`) e comparar com snapshots anteriores: o resultado de um padrão aprovado não pode mudar sem pedido.
- Padrões existentes: `amanda` (v1.0, oficial, com ajustes pendentes que a autora vai revisar; vai também pros clientes, que recebem a licença da Helvetica Now e a fonte em `padroes/amanda/fontes/`). `topo-livre` (em criação, para clientes: fonte TikTok Sans, sem fonte paga nem logo fixo).

## Distribuição para clientes

Pacote `video-editor.nosync` com: `motor/`, `.claude/` (comandos e hook), `CLAUDE.md`, `LEIA-ME.md`, `padroes/` (amanda + topo-livre, com fontes e licenças). **Não vai:** `marcas/amanda/` (logo, glossário, editados), `projetos/`, `config/`, `registro.json`, `.git/`. Marca do cliente: logo e glossário definidos por ele no `/video-editor-configurar`; a cor sugerida depende de **como a câmera grava**: imagem normal (com contraste) → a mesma da Amanda (`padroes/amanda/cor/meus-editados.cube`); **imagem lavada** (cinza, sem contraste: perfis log/flat, comum em câmeras Sony/cinema) → `padroes/amanda/cor/lavado.cube` (contraste, pele quente, cor rica; aprovada no vídeo do Adel Bark, 2026-10-21). A LUT da Amanda num vídeo lavado deixa ainda mais apagado. Sempre mostrar a comparação e deixar a pessoa escolher; a escolhida é copiada pra `marcas/<cliente>/cor/`. O vídeo de teste (`taste-washing-5`) é só da autora do motor.

## Primeiro uso / padrão novo

Se o padrão pedido não tem `PLAYBOOK.md`, ou a usuária pede um padrão novo: guiar pela seção "Criar um padrão novo" do `LEIA-ME.md` (caminho A: partir de vídeos editados da marca; caminho B: copiar referências). Não editar um bruto sem padrão definido, a menos que ela peça explicitamente.

## Criação e atualização de um padrão (análise de referências)

Papéis das entradas:
- `_marca/meus-editados/` (Drive): a base no caminho A. O padrão parte da identidade atual; as referências nunca a substituem.
- `_padroes/<nome>/referencias/` (Drive; baixar em pasta temporária, resolução original): fonte de elementos isolados. Nunca copiar uma referência inteira; levar em conta o que a usuária disse que gosta em cada uma.
- Par editado + bruto do mesmo vídeo (`<nome>` e `<nome>-bruto`): comparar os dois pra inferir as regras de corte reais. É a evidência mais confiável.

Caminho B ("referência como base"): uma referência principal vira a base. Pedir 2 a 3 vídeos do mesmo criador e só tratar como estilo o que se repete entre eles. Replicar o estilo de edição, mas não a identidade do criador (logo, paleta exata, assinaturas visuais, bordões). Checar a licença das fontes (padrão para clientes: só fontes livres, ex. Google Fonts). Marcar o que depende da gravação (enquadramento, headroom, luz, fundo). Tabela "Referência principal | Proposta".

Método por vídeo: `ffprobe` → transcrição com tempo por palavra → silêncios (`silencedetect`) e cortes de cena → quadros nos cortes e em amostragem regular → medidas: pausa entre frases, cortes/min, legenda (posição, tamanho, palavras por tela, cor, contorno, animação), zooms, inserções (frequência, formato, bordas), efeitos de fundo, gancho (0–3 s), música/sfx, duração. Pra medir lógica de destaques de cor, detectar a cor automaticamente quadro a quadro (como foi feito com o vermelho do Kaio) e cruzar com a transcrição.

Entregável: tabela comparativa com valores numéricos; a usuária decide a coluna Proposta; só depois escrever `PLAYBOOK.md` + `padrao.json`. Deixar explícito o que foi medido e o que foi estimado. Apagar os quadros extraídos ao terminar.

## Nada cobre o rosto (PLAYBOOK §0, vale pra todo padrão)

Nunca posicionar título, cards, legendas ou palavras-chave em posições fixas. Rodar `motor/rosto.py` depois do recorte; o `motor/gerar.py` usa esse mapa (com zoom e deslocamento do fundo mesclado) pra colocar cada elemento abaixo do queixo; se não couber, o card encolhe; o rosto nunca cede. Conferir nos snapshots antes do preview.

## Cor e iluminação (PLAYBOOK 1.1)

Em todo vídeo, **antes de montar o plano**, perguntar qual grading usar: (1) o da marca (`marcas/<nome>/cor/*.cube`, padrão), (2) o de outra referência indicada, ou (3) manter o original. Mostrar comparação lado a lado (bruto | com grading | referência). Grava a escolha em `projeto.json` → `"grading"`. Aplicado no A-roll (`motor/cortes.py`) antes do recorte; inserções mantêm as cores originais.

Gerar LUT: `motor/grading.py --bruto <bruto> --ref <video>:<t1,t2,...> ... --saida marcas/<nome>/cor/<nome>.cube --comparar <jpg>`.
- Tempos de referência **só da pessoa falando**: montar uma grade dos quadros e conferir antes (b-roll e cards contaminam).
- A medição usa só **pele do rosto + fundo da sala** (máscara do recorte); a roupa não entra.
- A LUT da marca `amanda` já existe (`marcas/amanda/cor/meus-editados.cube`, 2026-10-12): reaproveitar.

## Fluxo obrigatório de cada edição (nunca pular etapas)

1. **Plano antes de editar.** Transcrever e apresentar o plano: cortes com timecodes, aceleração, duração final, legendas, zooms, inserções (tabela PLAYBOOK 4.0), efeitos, regras do padrão aplicadas, grading. Esperar a aprovação.
2. **Storyboard antes de montar** (todo padrão, atual e futuro). Com o A-roll pronto (`motor/cortes.py`) e o `edicao.json` do plano, rodar `motor/storyboard.py projetos/<slug>` (~2 min, não precisa do recorte completo) e mandar `storyboard/storyboard.jpg` (`SendUserFile`). Um quadro por momento com a composição real, tempo, fala, tipo, origem da imagem e alertas de regra em vermelho. Só seguir pro recorte/camadas/preview depois da aprovação; correções são feitas por número do quadro.
3. **Preview antes de renderizar.** `npx hyperframes preview` em `projetos/<slug>/composicao` e abrir no navegador do app. Ajustar por lá; conferir pontos com snapshots.
4. **Entrega só com aprovação explícita:** `/video-editor-entregar` (`motor/entregar.py`). Conferir quadros do MP4 final.
5. **Registrar o aprendizado** no padrão (PLAYBOOK + padrao.json + CHANGELOG) ou na marca (glossário).

## Regras que valem em toda edição

- **Glossário da marca:** `motor/transcrever.py` passa os termos como contexto do Whisper. Aplicar a tabela de erros conhecidos pelo contexto ("cloud" só vira "Claude" quando o assunto é a IA). Termo novo ou duvidoso → perguntar e acrescentar.
- **Confirmação das inserções (PLAYBOOK 4.0):** tabela fala exata → entra/sai → duração → arquivo → tipo e posição, de todas as inserções. Gancho (~5 s) é pergunta separada: quantas inserções, tipo, posição, duração.
- **Recursos opcionais** (fundo mesclado, palavras-chave, efeito negativo, texto atrás): nunca aplicar sem pedido ou aprovação explícita, e só se o padrão os tiver em `"recursos"`.

## Lições técnicas

- **iCloud:** a Área de Trabalho sincroniza com o iCloud; ler o mesmo vídeo em dois processos dá "Operation timed out". Por isso os brutos vêm do Drive pra `projetos/<slug>/cache/` (cópia local de trabalho).
- **Cortes:** os tempos globais do Whisper derivam até ~1 s. Rodar `motor/refinar_cortes.py` (retranscreve janelas curtas) e **sempre** validar com `motor/energia.py` (bordas e interior no nível do ruído da sala; `--perfil de ate` mostra os vales).
- **Conferência:** depois do A-roll, retranscrever o arquivo inteiro e comparar com o roteiro. Janelas curtas (<5 s) fazem o Whisper inventar palavras. Nas legendas, usar o texto do roteiro.
- **Corte duvidoso:** sílabas emendadas → não adivinhar. Gerar 2–3 versões curtas do trecho (`SendUserFile`) e deixar a usuária escolher pelo ouvido.
- **Uma cópia só da pessoa:** recorte nunca como segunda `<video>` no HyperFrames (dessincroniza no preview → "fantasma"). `motor/compor_camadas.py` embute fundo mesclado + texto atrás + recorte num vídeo único.
- **Ordem de dependência:** mudou corte, aceleração ou grading → `cortes.py`, recorte, `rosto.py`, `compor_camadas.py`, `gerar.py`. Mudou fundo mesclado/texto atrás → `compor_camadas.py` + `gerar.py`. Mudou legenda, palavra-chave, card, título ou valor do padrão (exceto fundo mesclado/texto atrás) → só `gerar.py`.
- **MediaPipe 1.1** não tem `mp.solutions`: a detecção de rosto do `/shorts` (claude-shorts) está quebrada. O motor usa `rosto.py` (pele dentro da máscara do recorte).

## Pesquisa de imagens e notícias (opcional, PLAYBOOK §5)

Só quando a usuária pedir: 1) propor 4–8 queries curtas e **esperar aprovação**; 2) buscar e montar galeria/lista numerada; 3) baixar só o escolhido, dizendo a origem, e **enviar pra `insercoes/<nome-do-bruto>/` no Drive** (+ cópia em `composicao/assets/img/`); 4) se falhar, nunca travar o plano: dizer o que falhou e pedir o arquivo em `insercoes/<nome-do-bruto>/` no Drive ("aguardando arquivo").

## Organização e restrições

- Bruto novo no Drive → `motor/registro.py iniciar` cria `projetos/<slug>/` (slug: minúsculas, sem acentos/espaços) e registra em `registro.json`.
- `projetos/taste-washing-5` e `projetos/teste-topo-livre-1` são anteriores ao Drive; os brutos estão em `_padroes/<padrão>/teste/` no Drive (`bruto_drive` no `projeto.json`; `motor/preparar.py` baixa quando precisar). `taste-washing-5` é a regressão do padrão Amanda: a versão aprovada vigente, que evolui quando a autora aprova melhorias no padrão (o editado v1.0 está em `editados/` no Drive).
- Pouco espaço em disco: checar `df -h ~` antes de baixar; avisar abaixo de ~3 GB. Apagar intermediários quando não forem mais necessários.
- Git: usar `/opt/homebrew/bin/git` (o `/usr/bin/git` exige Xcode CLT). Este projeto é **privado**: tem repositório próprio e é ignorado pelo repositório público do portfólio (`../.gitignore`, com e sem `.nosync`). Nunca publicar sem pedido. Backup dos clientes = zip no Drive; GitHub privado é só pra autora do motor.
