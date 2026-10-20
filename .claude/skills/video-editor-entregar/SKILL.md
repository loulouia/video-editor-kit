---
name: video-editor-entregar
description: Entrega um vídeo aprovado no editor de vídeo (video-editor) — renderiza, envia pra pasta editados/ do Google Drive, confere, guarda a versão, limpa o Mac e faz backup. Use quando a pessoa aprovar o preview e pedir pra finalizar, renderizar ou entregar.
argument-hint: "[nome do vídeo]"
---

# Entregar um vídeo

Vídeo: $ARGUMENTS (se vazio, usar o que está em preview; se houver mais de um, perguntar).

1. Só entregar com **aprovação explícita** do preview nesta conversa.
2. Rodar `~/.video-skill/bin/python -I motor/entregar.py projetos/<slug>`. Ele:
   - renderiza (MP4 1080×1920);
   - envia pra `editados/<nome-do-bruto>-<padrão>.mp4` (se já existir: `-v2`, `-v3`… nunca sobrescreve);
   - **confere** tamanho + MD5 no Drive — se falhar, para e não apaga nada;
   - guarda as decisões e a versão do motor/padrão usada (pra reabrir igual);
   - apaga só os temporários do Mac (automático, sem perguntar);
   - faz o backup do projeto em `_backup/` (5 mais recentes).
3. Conferir 3–4 quadros do MP4 antes de anunciar (se algo estiver diferente do preview, avisar).
4. Repassar o aviso do script em linguagem simples, por exemplo:
   > ✅ **Entregue:** aula-03-topo-livre.mp4 está em `editados/` no seu Drive.
   > Liberei 240 MB no seu Mac (só arquivos temporários de edição). O vídeo e tudo o que é preciso pra reeditar estão guardados.
5. Se o backup falhar, dizer que o vídeo está entregue e seguro, e que o backup será tentado de novo na próxima entrega.
