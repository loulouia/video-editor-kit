---
name: video-editor-verificar
description: Verifica se tem vídeo novo na pasta brutos do Drive e lista para o usuário escolher qual editar. Responde a "veja se tem vídeo novo", "subi vídeo novo", "carreguei video para edição", "tem material novo?", "quero editar um vídeo", e variações.
---

# Verificar material novo

1. Rodar `~/.video-skill/bin/python -I motor/registro.py --json` (com `~/.local/bin` no PATH, se o rclone estiver lá). É a mesma conferência do `/video-editor-videos` e do início de sessão — não listar o Drive por conta própria. Ela já devolve, por bruto: nome, tamanho, etapa (`novo`, `plano`, `storyboard`, `montagem`, `preview`, `entregue`), padrão, se o nome parece b-roll (`suspeito_broll`) e os vídeos registrados que sumiram do Drive (`sumidos_do_drive`); reconhece vídeo renomeado pelo ID do Drive.
2. Mostrar para o usuário de forma clara:
   - **Novos** (`etapa: novo`): nome e tamanho.
   - **Em andamento / entregues**: nome, etapa, padrão.
3. Avisos:
   - `suspeito_broll` → perguntar se é bruto ou inserção (nunca decidir sozinho).
   - `sumidos_do_drive` → avisar que o vídeo não está mais em `brutos/` (sem ele, não dá pra reabrir a edição).
4. Se houver vídeos novos, perguntar: **"Qual você quer editar?"** e listar os novos com número para facilitar.
5. Quando o usuário escolher, seguir para `/video-editor-editar <nome>`.

Se o setup estiver incompleto (o comando falha por falta de configuração), indicar `/video-editor-configurar`.

## Importante

- Usar o `motor/registro.py` (rclone por baixo), não o conector do Google Drive — é mais rápido e é a mesma lógica dos outros comandos.
- Não perguntar confirmações desnecessárias; ir direto ao ponto.
- Se só tem 1 vídeo novo, já sugerir: "Quer editar esse?"
