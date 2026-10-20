---
name: video-editor-configurar
description: Primeiro uso do editor de vídeo (video-editor) — instala e confere as ferramentas, instala o rclone, conecta o Google Drive, cria as pastas no Drive (com OK) e cadastra a marca. Use quando o setup estiver incompleto ou a pessoa pedir pra configurar/reconfigurar o editor de vídeo.
---

# Configurar o editor de vídeo

Siga em ordem. Fale em linguagem simples (a pessoa pode não ser técnica). Cada etapa já feita é só conferida e pulada. Regras gerais: `CLAUDE.md`.

## 0. Nome da pasta (iCloud)

A pasta deve se chamar `video-editor.nosync` (já é distribuída assim). Conferir:
- nome atual da raiz do projeto termina em `.nosync`? → seguir;
- não termina **e** está num lugar sincronizado pelo iCloud (caminho dentro de `~/Desktop` ou `~/Documents` quando existir `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop`, ou dentro de `~/Library/Mobile Documents`) → explicar em uma frase ("o iCloud pode tirar arquivos do seu Mac quando o disco enche; com `.nosync` no nome a pasta fica sempre no Mac") e **pedir OK** pra renomear no mesmo lugar. Antes: checar espaço e baixar os arquivos que estejam só na nuvem (`find . -flags +dataless`); depois: conferir que nenhum ficou na nuvem. Avisar que a pessoa passa a abrir a pasta com o nome novo.
- não está num lugar sincronizado → não mexer.

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

1. Explicar: vai abrir uma página do Google no navegador; a pessoa entra na conta e clica em **Permitir**. Eu nunca vejo a senha. O acesso é ao Drive inteiro porque os vídeos que ela sobe pelo navegador/celular precisam ser lidos.
2. Rodar em segundo plano (espera a autorização): `rclone config create gdrive drive scope=drive`
3. Conferir: `rclone lsd gdrive:` lista as pastas do Meu Drive.
4. Gravar `config/ambiente.json`: `{"remote": "gdrive:", "raiz": "Edição de vídeos", "configurado": false}`

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
```

`python motor/drive.py status` mostra o que já existe; `python motor/drive.py criar-estrutura` cria só o que falta (nunca apaga nem renomeia nada). Se a pasta já existir, usar a existente.

## 5. Marca

Se não houver marca em `marcas/`, cadastrar com a pessoa: nome, logo (versão clara e escura, PNG transparente), fontes próprias (se houver e se tiver licença), cores/paleta (opcional), termos e nomes próprios pro glossário. Criar `marcas/<slug>/marca.json` seguindo `marcas/amanda/marca.json` (`"padrao_padrao": null` — o padrão de cada vídeo é sempre perguntado enquanto isso estiver vazio). A cor do cenário (LUT) é gerada depois, com vídeos editados da pessoa (`motor/grading.py`).

## 6. Vídeos de referência e editados que estejam no Mac

Se houver vídeos em `padroes/*/referencias/` ou `marcas/*/meus-editados/` no Mac: oferecer mover pro Drive (`_padroes/<padrão>/referencias/`, `_marca/meus-editados/`). Enviar com `motor/drive.py enviar` (confere tamanho + MD5) e só apagar a cópia local depois de **todos** conferidos. Dizer quanto espaço foi liberado.

## 7. Fechar

- Marcar `"configurado": true` em `config/ambiente.json`.
- Rodar `python motor/backup.py` (primeiro backup).
- Resumo curto: o que foi instalado, onde ficam as pastas no Drive e o próximo passo: "suba um vídeo em `brutos/` e digite `/video-editor-videos`".
