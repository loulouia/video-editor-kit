---
name: video-editor-verificar
description: Verifica se tem vídeo novo na pasta brutos do Drive e lista para o usuário escolher qual editar. Responde a "veja se tem vídeo novo", "subi vídeo novo", "carreguei video para edição", "tem material novo?", "quero editar um vídeo", e variações.
---

# Verificar material novo

1. Rodar `rclone lsf "gdrive:Edição de vídeos/brutos/" --format pst` para listar os brutos no Drive (nome, tamanho, data).
2. Ler `registro.json` e comparar: identificar quais brutos do Drive **já estão registrados** e quais são **novos**.
3. Mostrar para o usuário de forma clara:
   - **Novos** (ainda não registrados): nome e tamanho.
   - **Já registrados** (com a etapa atual): nome, etapa, padrão.
4. Atualizar `_driveCheck` em `registro.json` com `{"checked":"HH:MM","message":"...","newCount":N}`.
5. Avisos:
   - Nome que parece b-roll em `brutos/` (sem fala, muito curto, nome tipo "broll") → perguntar se é bruto ou inserção.
   - Vídeo registrado que sumiu de `brutos/` → avisar.
6. Se houver vídeos novos, perguntar: **"Qual você quer editar?"** e listar os novos com número para facilitar.
7. Quando o usuário escolher, seguir para `/video-editor-editar <nome>`.

Se o setup estiver incompleto, indicar `/video-editor-configurar`.

## Importante

- Usar **rclone direto** (não o conector do Google Drive — é mais rápido).
- Não perguntar confirmações desnecessárias; ir direto ao ponto.
- Se só tem 1 vídeo novo, já sugerir: "Quer editar esse?"
