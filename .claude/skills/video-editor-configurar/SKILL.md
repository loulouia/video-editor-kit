---
name: video-editor-configurar
description: Primeiro uso do editor de vídeo (video-editor) — instala e confere as ferramentas, instala o rclone, conecta o Google Drive, cria as pastas no Drive (com OK) e cadastra a marca. Use quando o setup estiver incompleto ou a pessoa pedir pra configurar/reconfigurar o editor de vídeo.
---

# Configurar o editor de vídeo

Siga em ordem. Fale em linguagem simples (a pessoa pode não ser técnica). Cada etapa já feita é só conferida e pulada. Regras gerais: `CLAUDE.md`.

## 0. Local e nome da pasta

### Pasta-mãe `ClaudeCode`
O projeto deve ficar dentro de `~/Desktop/ClaudeCode/`. Conferir:
- `~/Desktop/ClaudeCode/` já existe? → seguir.
- não existe? → criar `mkdir -p ~/Desktop/ClaudeCode` (sem perguntar — é só uma pasta organizadora).

Se o projeto foi clonado ou descompactado em outro lugar (ex.: `~/Desktop/video-editor.nosync`), mover pra dentro de `~/Desktop/ClaudeCode/` e avisar: "Movi a pasta pra ~/Desktop/ClaudeCode/video-editor.nosync pra ficar organizado."

### Nome `.nosync` (iCloud)
A pasta deve se chamar `video-editor.nosync` (já é distribuída assim). Conferir:
- nome atual da raiz do projeto termina em `.nosync`? → seguir;
- não termina **e** está num lugar sincronizado pelo iCloud (caminho dentro de `~/Desktop` ou `~/Documents` quando existir `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop`, ou dentro de `~/Library/Mobile Documents`) → explicar em uma frase ("o iCloud pode tirar arquivos do seu Mac quando o disco enche; com `.nosync` no nome a pasta fica sempre no Mac") e **pedir OK** pra renomear no mesmo lugar. Antes: checar espaço e baixar os arquivos que estejam só na nuvem (`find . -flags +dataless`); depois: conferir que nenhum ficou na nuvem. Avisar que a pessoa passa a abrir a pasta com o nome novo.
- não está num lugar sincronizado → não mexer.

### Abrir o projeto no Claude Code
Depois de garantir que a pasta está em `~/Desktop/ClaudeCode/video-editor.nosync`, o projeto precisa estar **aberto como pasta do Claude Code** pra que os comandos `/video-editor-*` funcionem. Conferir:
- o diretório de trabalho atual do Claude Code já é esta pasta? → seguir.
- não é? → trocar o diretório de trabalho pra `~/Desktop/ClaudeCode/video-editor.nosync` (usar a ferramenta de trocar diretório do Claude Code). Explicar: "Preciso abrir a pasta do editor como projeto ativo pra que os comandos funcionem."

## 1. Ferramentas no Mac

Conferir e, se faltar, instalar (avisar o tamanho antes de downloads grandes; checar espaço livre com `df -h ~` — se houver menos de ~5 GB, avisar antes de seguir):

| Ferramenta | Conferir | Instalar |
|---|---|---|
| Homebrew | `which brew` | pedir pra pessoa instalar (https://brew.sh) — exige a senha dela |
| ffmpeg | `ffmpeg -version` | `brew install ffmpeg` |
| Node (npx) | `npx --version` | `brew install node` |
| Ambiente Python | `~/.video-skill/bin/python -c "import mlx_whisper, cv2, matplotlib, fontTools"` | `python3 -m venv ~/.video-skill && ~/.video-skill/bin/pip install mlx-whisper opencv-python numpy matplotlib fonttools` |
| HyperFrames (render) | `npx -y hyperframes@latest doctor` | `npx -y hyperframes@latest browser ensure`; desativar telemetria: `npx -y hyperframes@latest telemetry disable` |

## 2. rclone (transporte dos vídeos entre o Drive e o Mac)

- Conferir: `rclone version` (ou `~/.local/bin/rclone version`).
- Se faltar: `brew install rclone`. Se o Homebrew falhar, baixar o binário oficial de https://downloads.rclone.org (versão em `version.txt`, arquivo `rclone-<versão>-osx-arm64.zip` ou `osx-amd64` em Mac Intel), **conferir o SHA256** com o `SHA256SUMS` do mesmo diretório e copiar só o executável pra `~/.local/bin/rclone`.
- Explicar em uma frase: "é a ferramenta que leva os vídeos do seu Drive pro Mac e devolve o editado; não fica rodando nem guarda cópias".

## 3. Conectar o Google Drive

1. Explicar em duas frases: primeiro a pessoa cria uma **chave própria** no Google (grátis, ~10 min, eu guio passo a passo), depois autoriza o acesso ao Drive **uma vez**. Eu nunca vejo a senha nem a chave. O acesso é ao Drive inteiro porque os vídeos que ela sobe pelo navegador/celular precisam ser lidos.
2. Seguir **`chave-google.md`** (nesta pasta), um passo por mensagem: projeto → Drive API → tela de autorização → chave → terminal com `chave-google.sh` (cria a conexão `gdrive` já com a chave e abre o Google pra autorizar).
3. Conferir: `rclone lsd gdrive:` lista as pastas do Meu Drive **sem** o NOTICE de `client_id`. (Se já houver uma conexão `gdrive` com a chave compartilhada, o mesmo script troca a chave.)
4. Gravar `config/ambiente.json`: `{"remote": "gdrive:", "raiz": "Edição de vídeos", "configurado": false, "biblioteca": {"pasta_id": "1C_tqHO2k-w02zYEYLw3pZ4pTt6tHSqN_", "destinos": {"efeitos sonoros": "_audio/efeitos", "musicas": "_audio/musicas", "transicoes": "_transicoes"}}}`

## 4. Pastas no Drive (só com OK)

Mostrar exatamente o que será criado e **esperar o OK**:

```
Meu Drive/Edição de vídeos/
  brutos/                       ← vídeos pra editar
  insercoes/<nome-do-bruto>/    ← imagens e b-roll de cada vídeo
  editados/                     ← vídeos prontos
  _padroes/<padrão>/referencias/
  _marca/meus-editados/
  _backup/                      ← cópias de segurança do projeto
  _audio/musicas/               ← biblioteca de músicas
  _audio/efeitos/               ← biblioteca de efeitos sonoros
  _transicoes/                  ← biblioteca de transições em vídeo (overlay)
```
Explicar em uma frase que `_audio/` e `_transicoes/` são uma biblioteca da pessoa, pra qualquer vídeo, e que só entra o que ela tem direito de usar.

`python motor/drive.py status` mostra o que já existe; `python motor/drive.py criar-estrutura` cria só o que falta (nunca apaga nem renomeia nada). Se a pasta já existir, usar a existente.

## 4.1. Biblioteca inicial (efeitos, músicas, transições)

Se `config/ambiente.json` tiver o campo `"biblioteca"` (com `pasta_id` e `destinos`), listar os arquivos disponíveis com `rclone lsjson -R --files-only "gdrive,root_folder_id=<pasta_id>:"` pra saber quantos são e o tamanho total, e oferecer a cópia informando os números:

> Tenho uma biblioteca inicial com **N** efeitos sonoros, **N** músicas e **N** transições (total ~X MB) pra você. Quer que eu copie pro seu Drive? São arquivos livres pra usar nos vídeos.

- Se sim: `python motor/drive.py copiar-biblioteca`. Mostrar quantos arquivos foram copiados em cada categoria.
- Se não: seguir sem copiar. A pessoa pode pedir depois (comando: `python motor/drive.py copiar-biblioteca`).
- Se `"biblioteca"` não existir no `ambiente.json`: pular silenciosamente.

Os arquivos vão pra `_audio/efeitos/`, `_audio/musicas/` e `_transicoes/` no Drive da pessoa — a mesma biblioteca que ela vai abastecer depois com os dela.

## 5. Marcas

Listar as pastas em `marcas/` e ler cada `marca.json`.

### Nenhuma marca existe
Cadastrar do zero: nome, logo (versão clara e escura, PNG transparente; opcional), fontes próprias (se houver e tiver licença), cores/paleta (opcional), termos pro glossário (opcional). Criar `marcas/<slug>/marca.json` (`"padrao_padrao": null`).

### Marcas já existem (pré-configuradas)
Apresentar de forma clara o que já tem e o que falta em cada uma:

> Encontrei **N** marcas pré-configuradas:
> 1. **adel-bark** — nome definido, cor definida, sem logo
> 2. **mariana** — nome e cor a definir
>
> Vamos completar uma por vez. Qual você quer configurar primeiro?

Para cada marca, verificar e completar:
- `nome` é null → perguntar: "Qual o nome completo da pessoa ou da marca?"
- `marca` é null → perguntar: "Como a marca se apresenta? (ex.: 'Nome — Nicho')"
- `logo` é null → perguntar: "Tem logo? Se tiver, manda a versão clara e escura (PNG sem fundo). Se não tiver, o vídeo sai sem logo — pode adicionar depois."
- `glossario` é null → perguntar: "Tem termos técnicos do nicho que o nome pode ser escrito errado? (ex.: nomes de procedimentos, marcas, nomes próprios). Se não tiver agora, pode adicionar depois."
- `lut` é null → avisar: "A cor do vídeo será decidida no primeiro vídeo que editar — vou mostrar uma comparação pra você escolher."

Completar cada campo no `marca.json`. Não apagar campos que já estão preenchidos.

### Cor do cenário
Decidida no primeiro vídeo de cada marca, com comparação lado a lado. Imagem normal (com contraste) → sugerir `padroes/amanda/cor/meus-editados.cube`; imagem lavada (cinza, sem contraste: perfis log/flat) → sugerir `padroes/amanda/cor/lavado.cube`. A escolhida é copiada pra `marcas/<slug>/cor/`. Outra cor: gerar com vídeos editados da pessoa (`motor/grading.py`).

### Mais de uma marca
Quando houver mais de uma marca, ao iniciar cada edição o Claude sempre pergunta **de qual marca é o vídeo**. Não existe marca "principal" — cada vídeo é de uma marca.

## 6. Vídeos de referência e editados que estejam no Mac

Se houver vídeos em `padroes/*/referencias/` ou `marcas/*/meus-editados/` no Mac: oferecer mover pro Drive (`_padroes/<padrão>/referencias/`, `_marca/meus-editados/`). Enviar com `motor/drive.py enviar` (confere tamanho + MD5) e só apagar a cópia local depois de **todos** conferidos. Dizer quanto espaço foi liberado.

## 7. Fechar

- Marcar `"configurado": true` em `config/ambiente.json`.
- Rodar `python motor/backup.py` (primeiro backup).
- Resumo curto: o que foi instalado, onde ficam as pastas no Drive e o próximo passo: "suba um vídeo em `brutos/` e digite `/video-editor-videos`".
