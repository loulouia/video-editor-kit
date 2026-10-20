# Editor de vídeo (Reels / TikTok)

Edição de vídeos curtos (1080×1920) feita pelo Claude: cortes de pausas, aceleração, cor, legendas, palavras-chave, inserções e render, sempre com plano, storyboard e preview aprovados por você. Os vídeos ficam no seu Google Drive; o Mac guarda só o que é pequeno.

## Comece aqui

1. Coloque a pasta **`video-editor.nosync`** onde preferir (Área de Trabalho, Documentos...) e abra no Claude Code. Não tire o `.nosync` do nome: é ele que impede o iCloud de tirar os arquivos do seu Mac quando o disco fica cheio.
2. Digite **`/video-editor-configurar`**. O Claude confere e instala as ferramentas, conecta o seu Google Drive (você autoriza no navegador) e, **com o seu OK**, cria as pastas no Drive.
3. Suba um vídeo gravado em `Edição de vídeos/brutos/` no seu Drive (pelo navegador, celular ou computador).
4. Digite **`/video-editor-videos`** pra ver o que é novo, e **`/video-editor-editar`** pra começar.

Toda vez que você abrir o projeto, o Claude já confere se há vídeos novos no Drive e te avisa na primeira resposta.

### Comandos

Digite `/video-editor` pra ver todos.

| Comando | O que faz |
|---|---|
| `/video-editor-configurar` | primeiro uso: ferramentas, Drive, pastas, marca |
| `/video-editor-videos` | mostra 🆕 novos, ⏳ em andamento e ✅ entregues |
| `/video-editor-editar` | edita um bruto (ou reabre um já entregue pra ajustar) até o preview |
| `/video-editor-entregar` | renderiza o aprovado, envia pro Drive, confere, limpa o Mac e faz backup |
| `/video-editor-novo-padrao` | cria um estilo de edição a partir de vídeos de referência |

Também dá pra pedir em linguagem normal (ex.: *"edita o vídeo novo"*).

## Seu Google Drive

```
Meu Drive/Edição de vídeos/
  brutos/                       ← você sobe aqui os vídeos pra editar
  insercoes/<nome-do-bruto>/    ← prints, fotos e b-rolls de cada vídeo
  editados/                     ← os vídeos prontos aparecem aqui
  _padroes/  _marca/            ← vídeos de referência e seus vídeos já editados
  _backup/                      ← cópias de segurança do projeto (automáticas)
```

- **Bruto** é só o que está **direto** em `brutos/`. Uma pasta por vídeo em `insercoes/`, com o **mesmo nome do bruto** (ex.: `brutos/aula-03.mov` → `insercoes/aula-03/`). Os nomes dos arquivos dentro dela são livres; se quiser, coloque o momento no começo (ex.: `0m12-print.png`).
- O vídeo pronto vai pra `editados/<nome-do-bruto>-<padrão>.mp4`. Se você pedir ajuste depois, a versão nova vira `-v2` e a anterior continua lá.
- O Claude **nunca renomeia, move ou apaga** arquivos seus no Drive.
- Suba os vídeos **originais**, direto do celular ou do computador. Passar pelo WhatsApp ou baixar de rede social comprime o vídeo antes.
- **Não apague o bruto** de um vídeo que talvez precise de ajuste: sem ele, não dá pra reabrir a edição.

## Como funciona cada edição

Nada é renderizado sem você aprovar.

1. **Você pede.** Diga qual bruto e qual padrão (o Claude sempre pergunta o padrão). Pra cada inserção você pode escolher o tipo; recursos opcionais só entram quando você pede (ex.: *"com palavras-chave"*).
   - **Cor e iluminação:** antes/depois pra escolher: a cor da sua marca, a de outra referência ou a original.
   - **Pesquisa de imagens (opcional):** *"busca imagens"*. O Claude propõe as buscas, você aprova, escolhe e só o escolhido é baixado (e guardado na pasta do vídeo no Drive).
2. **Plano (você aprova).** Cortes, aceleração, duração, legendas, inserções (fala exata, entrada/saída, duração, tipo) e o gancho.
3. **Storyboard (você aprova).** Um quadro por momento, já com a composição real, tempo, fala, origem de cada imagem e **alertas em vermelho** quando algo fere uma regra. Correção pelo número do quadro.
4. **Preview (você ajusta).** Timeline no navegador do app; cada ajuste aparece em segundos.
5. **Entrega.** Com a sua aprovação: o vídeo vai pra `editados/` no Drive, é conferido, e o Mac é limpo sozinho. Você recebe um aviso como:
   > ✅ **Entregue:** aula-03-topo-livre.mp4 está em `editados/` no seu Drive.
   > Liberei 240 MB no seu Mac (só arquivos temporários de edição). O vídeo e tudo o que é preciso pra reeditar estão guardados.
6. **Ajustes depois da entrega.** `/video-editor-editar` com o nome do vídeo: ele reabre igual à versão entregue (ou com o padrão atualizado, se você quiser).

## Como está organizado (no Mac)

| Pasta | O que é |
|---|---|
| `motor/` | **Como editar.** Os scripts que fazem o trabalho. Iguais pra qualquer estilo (não mexer) |
| `padroes/<nome>/` | **Um estilo de edição.** Regras (`PLAYBOOK.md`), valores (`padrao.json`), histórico (`CHANGELOG.md`), fontes |
| `marcas/<nome>/` | **Um criador ou cliente.** Logo (claro e escuro), glossário de termos, cor do cenário, paleta |
| `projetos/<nome-do-video>/` | **As decisões de cada vídeo** (< 1 MB): cortes, legendas, inserções, storyboard, versão entregue |
| `config/` | configuração desta instalação (conexão com o Drive) |
| `registro.json` | lista de vídeos e status |

Cada vídeo combina **um padrão + uma marca**. O mesmo vídeo pode ser editado em outro padrão sem mudar nada da marca.

### Padrões existentes

| Padrão | Status | Para |
|---|---|---|
| `amanda` | v1.0, oficial | uso próprio (Helvetica Now Display, LOULOU Studios) |
| `topo-livre` | em criação | clientes (TikTok Sans + Instrument Serif, livres) |

## Criar um padrão novo

Use **`/video-editor-novo-padrao`**.
- **Caminho A:** partir dos seus vídeos editados (em `_marca/meus-editados/` no Drive).
- **Caminho B:** copiar o estilo de **2 a 3 vídeos do mesmo criador** (em `_padroes/<novo>/referencias/` no Drive). O que se repete é o estilo; a identidade do criador (logo, paleta exata, bordões) não é copiada.

O Claude devolve uma **tabela comparativa**; você decide cada linha, e o padrão nasce. Recursos que o motor já faz e cada padrão liga/desliga: legendas, título do gancho, palavras-chave (com efeito negativo), texto atrás da pessoa, fundo mesclado, caixa no topo, cartões de frase, cards e notícias, zoom de jump cut, cor, "nada cobre o rosto". Padrões pra clientes usam só fontes livres.

## Ferramentas

| Ferramenta | Para quê |
|---|---|
| ffmpeg | cortar, juntar, converter, cor, camadas |
| mlx-whisper | transcrição com tempo por palavra (`~/.video-skill`) |
| HyperFrames | composição, recorte da pessoa, preview, render (telemetria desativada) |
| rclone | leva os vídeos do Drive pro Mac e devolve o editado (sem app, sem cache) |
| git | histórico do projeto (repositório privado) |

**Backup:** depois de cada entrega, um zip do projeto (sem vídeos) vai pra `_backup/` no seu Drive, com as 5 cópias mais recentes. Em um Mac novo, o `/video-editor-configurar` restaura a partir dele.
